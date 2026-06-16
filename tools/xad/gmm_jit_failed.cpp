#include "gradbench/evals/gmm.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>
#include <cmath>
#include <vector>

using namespace gmm;
using namespace xad;
using namespace std;
class GmmXAD : public Function<Input, JacOutput> {
  // 1. Используем тип AReal для JIT (1 - это идентификатор ленты)
  using AD = xad::AReal<double, 1>;

  // 2. Внутренние состояния, которые живут между запусками
  xad::JITCompiler<double, 1> jit;
  std::vector<AD>             alpha_ad;
  std::vector<AD>             mu_ad;
  std::vector<AD>             q_ad;
  std::vector<AD>             l_ad;
  AD                          error;
  double                      out_val;

public:
  // КОНСТРУКТОР: Выполняется 1 раз при старте.
  // Здесь мы записываем весь граф GMM и компилируем его.
  GmmXAD(Input& input)
      : Function(input), alpha_ad(input.k), mu_ad(input.d * input.k),
        q_ad(input.k * input.d), l_ad(input.l.size()) {

    // Копируем стартовые значения и сразу регистрируем входы для JIT
    for (size_t i = 0; i < alpha_ad.size(); ++i) {
      alpha_ad[i] = _input.alpha[i];
      jit.registerInput(alpha_ad[i]);
    }
    for (size_t i = 0; i < mu_ad.size(); ++i) {
      mu_ad[i] = _input.mu[i];
      jit.registerInput(mu_ad[i]);
    }
    for (size_t i = 0; i < q_ad.size(); ++i) {
      q_ad[i] = _input.q[i];
      jit.registerInput(q_ad[i]);
    }
    for (size_t i = 0; i < l_ad.size(); ++i) {
      l_ad[i] = _input.l[i];
      jit.registerInput(l_ad[i]);
    }

    // Прямой проход - ЗАПИСЬ ГРАФА
    // XAD "проглотит" все циклы внутри objective и выстроит их в цепочку
    gmm::objective(_input.d, _input.k, _input.n, alpha_ad.data(), mu_ad.data(),
                   q_ad.data(), l_ad.data(), _input.x.data(), _input.wishart,
                   &error);

    // Регистрируем скалярный выход (ошибку)
    jit.registerOutput(error);

    // КОМПИЛЯЦИЯ графа в машинный код
    jit.compile();
  }

  // COMPUTE: Вызывается тысячи раз. Граф больше не строится!
  void compute(JacOutput& output) {

    // 1. Обновляем входные значения новыми данными из GradBench.
    for (size_t i = 0; i < alpha_ad.size(); ++i)
      alpha_ad[i] = _input.alpha[i];
    for (size_t i = 0; i < mu_ad.size(); ++i)
      mu_ad[i] = _input.mu[i];
    for (size_t i = 0; i < q_ad.size(); ++i)
      q_ad[i] = _input.q[i];
    for (size_t i = 0; i < l_ad.size(); ++i)
      l_ad[i] = _input.l[i];

    // 2. Очищаем производные от предыдущего прогона
    jit.clearDerivatives();

    // 3. Сверхбыстрый прямой проход по скомпилированной формуле
    jit.forward(&out_val);

    // 4. Задаем seed = 1.0 для начала обратного прохода
    jit.setDerivative(error.getSlot(), 1.0);

    // 5. Обратный проход (Backprop)
    jit.computeAdjoints();

    // 6. Подготавливаем размеры структур вывода
    output.d = _input.d;
    output.k = _input.k;
    output.n = _input.n;
    output.alpha.resize(_input.k);
    output.mu.resize(_input.d * _input.k);
    output.q.resize(_input.k * _input.d);
    output.l.resize(l_ad.size());

    // 7. Собираем результаты из слотов памяти JIT
    for (size_t i = 0; i < output.alpha.size(); ++i)
      output.alpha[i] = jit.getDerivative(alpha_ad[i].getSlot());
    for (size_t i = 0; i < output.mu.size(); ++i)
      output.mu[i] = jit.getDerivative(mu_ad[i].getSlot());
    for (size_t i = 0; i < output.q.size(); ++i)
      output.q[i] = jit.getDerivative(q_ad[i].getSlot());
    for (size_t i = 0; i < output.l.size(); ++i)
      output.l[i] = jit.getDerivative(l_ad[i].getSlot());
  }
};

int main(int argc, char* argv[]) {
  return generic_main(
      argc, argv,
      {{"objective",
        function_main<gmm::Objective>},  // calculation of the error function

       {"jacobian",
        function_main<GmmXAD>}});  // calculates jacobian - matrix of first
                                   // derivatives for every parameter alpha, mu,
                                   // q, l (full gradient of the gmm model)
}
