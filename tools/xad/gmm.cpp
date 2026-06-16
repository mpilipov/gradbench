#include "gradbench/evals/gmm.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>
#include <cmath>
#include <vector>

using namespace gmm;
using namespace xad;
using namespace std;
class GmmXAD : public Function<Input, JacOutput> {
  // types initialization
  // typedef xad::adj<double>  mode;       // mode: adj or fwd
  using AD        = xad::AReal<double>;
  using tape_type = xad::Tape<double>;  // an alias for "mode::active_type" type

  // tape and active variables
  tape_type       tape;
  std::vector<AD> alpha_ad;
  std::vector<AD> mu_ad;
  std::vector<AD> q_ad;
  std::vector<AD> l_ad;

public:
  GmmXAD(Input& input)
      : Function(input),
        // allocating memory
        alpha_ad(input.k),  // weights of clusters (equals number of clusters=K)
        mu_ad(input.d * input.k),  // centers of clusters (equals K*number of
                                   // coordinates of each cluster=K*D)
        q_ad(
            input.k *
            input.d),  // diagonal elements of covariation matrices (equals K*D)
                       // responsible for the span of the cluster along the axes
        l_ad(input.l.size())  // non-diagonal elements of covariation matrices
                              // (equals K*D) responsible for the tilt of the
                              // cluster
  {}

  void compute(JacOutput& output) {

    // copying data from input to the active variables
    for (size_t i = 0; i < alpha_ad.size(); ++i)
      alpha_ad[i] = _input.alpha[i];
    for (size_t i = 0; i < mu_ad.size(); ++i)
      mu_ad[i] = _input.mu[i];
    for (size_t i = 0; i < q_ad.size(); ++i)
      q_ad[i] = _input.q[i];
    for (size_t i = 0; i < l_ad.size(); ++i)
      l_ad[i] = _input.l[i];

    // registering variables for taking derivatives
    for (auto& v : alpha_ad)
      tape.registerInput(v);
    for (auto& v : mu_ad)
      tape.registerInput(v);
    for (auto& v : q_ad)
      tape.registerInput(v);
    for (auto& v : l_ad)
      tape.registerInput(v);

    // cleaning the tape for a new Gradbench run (includes clearDerivatives()
    // functional)
    tape.newRecording();

    AD error;  // target function we want to minimize

    // gmm::objective receives data pointers (cpp/../gmm.hpp)
    // forward pass of the model
    gmm::objective(_input.d, _input.k, _input.n, alpha_ad.data(), mu_ad.data(),
                   q_ad.data(), l_ad.data(), _input.x.data(), _input.wishart,
                   &error);
    // the computation result will be recorded into error

    // Registering output on the tape and setting seed f'(...)=1
    tape.registerOutput(error);
    xad::derivative(error) = 1.0;

    // adjoint mode computation - calculating derivatives by every of 4
    // parameters (alpha, mu, q, l) using chain rule
    tape.computeAdjoints();

    // preparation of the output variables
    output.d = _input.d;
    output.k = _input.k;
    output.n = _input.n;
    output.alpha.resize(
        _input.k);  // should be the same as sizes of input parameters
    output.mu.resize(_input.d * _input.k);
    output.q.resize(_input.k * _input.d);
    output.l.resize(l_ad.size());

    // reading results from derivative() results to the output variables
    for (size_t i = 0; i < output.alpha.size(); ++i)
      output.alpha[i] = xad::derivative(alpha_ad[i]);
    for (size_t i = 0; i < output.mu.size(); ++i)
      output.mu[i] = xad::derivative(mu_ad[i]);
    for (size_t i = 0; i < output.q.size(); ++i)
      output.q[i] = xad::derivative(q_ad[i]);
    for (size_t i = 0; i < output.l.size(); ++i)
      output.l[i] = xad::derivative(l_ad[i]);
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
