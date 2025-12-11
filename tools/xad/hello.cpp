#include "gradbench/evals/hello.hpp"
#include "gradbench/main.hpp"

// Подключаем XAD
#include <XAD/XAD.hpp>

class Double : public Function<hello::Input, hello::DoubleOutput> {
public:
  Double(hello::Input& input) : Function(input) {}

  void compute(hello::DoubleOutput& output) {
    // 1. Определяем типы (как в документации)
    // xad::adj<double> - это режим adjoint для типа double
    typedef xad::adj<double>  mode;
    typedef mode::tape_type   tape_type;
    typedef mode::active_type AD;

    // 2. Инициализируем ленту (Tape)
    tape_type tape;

    // 3. Создаем активную входную переменную
    AD x = _input;

    // 4. Регистрируем вход на ленте
    tape.registerInput(x);

    // 5. Начинаем запись
    tape.newRecording();

    // 6. Вычисляем функцию
    AD y = hello::square(x);

    // 7. Регистрируем выход
    tape.registerOutput(y);

    // 8. Устанавливаем seed производной для выхода (dL/dy = 1.0)
    // В документации используется глобальная функция derivative(y) = 1.0;
    xad::derivative(y) = 1.0;

    // 9. Вычисляем производные (обратный проход)
    tape.computeAdjoints();

    // 10. Получаем результат (производную по x)
    output = xad::derivative(x);
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"square", function_main<hello::Square>},
                       {"double", function_main<Double>}});
}
