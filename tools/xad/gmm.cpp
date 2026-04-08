#include "gradbench/evals/gmm.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>
#include <cmath>
#include <vector>

using namespace gmm;
using namespace xad;
using namespace std;
class GmmXAD : public Function<Input, JacOutput> {
public:
  GmmXAD(Input& input) : Function(input) {}

  void compute(JacOutput& output) {
    // types initialization
    typedef xad::adj<double>  mode;       // mode: adj or fwd
    typedef mode::tape_type   tape_type;  // creating the tape
    typedef mode::active_type AD;  // an alias for "mode::active_type" type

    tape_type tape;  // tape initialization

    // active variables initialization
    std::vector<AD> alpha_ad(
        _input.k);  // weights of clusters (equals number of clusters=K)
    std::vector<AD> mu_ad(_input.d *
                          _input.k);  // centers of clusters (equals K*number of
                                      // coordinates of each cluster=K*D)
    std::vector<AD> q_ad(
        _input.k *
        _input.d);  // diagonal elements of covariation matrices (equals K*D)
                    // responsible for the span of the cluster along the axes
    // size l: k * (d * (d - 1) / 2)
    std::vector<AD> l_ad(
        _input.l
            .size());  // non-diagonal elements of covariation matrices (equals
                       // K*D) responsible for the tilt of the cluster

    // copying data from input to the active variables
    for (size_t i = 0; i < alpha_ad.size(); ++i)
      alpha_ad[i] = _input.alpha[i];
    for (size_t i = 0; i < mu_ad.size(); ++i)
      mu_ad[i] = _input.mu[i];
    for (size_t i = 0; i < q_ad.size(); ++i)
      q_ad[i] = _input.q[i];
    for (size_t i = 0; i < l_ad.size(); ++i)
      l_ad[i] = _input.l[i];

    // variables for which derivatives are taken
    for (auto& v : alpha_ad)  // for every v in the vector alpha_ad
      tape.registerInput(v);  // registering input on the tape
    for (auto& v : mu_ad)
      tape.registerInput(v);
    for (auto& v : q_ad)
      tape.registerInput(v);
    for (auto& v : l_ad)
      tape.registerInput(v);

    // start of the recording
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
