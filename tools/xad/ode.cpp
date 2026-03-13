#include "gradbench/evals/ode.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>
#include <vector>

// Gradient class: computes the gradient of the last element of the ODE
// primal output with respect to all inputs x, using XAD adjoint-mode AD.
class Gradient : public Function<ode::Input, ode::GradientOutput> {
public:
  Gradient(ode::Input& input) : Function(input) {}

  void compute(ode::GradientOutput& output) {
    size_t n = _input.x.size();
    output.resize(n);

    // 1. Define XAD types for reverse (adjoint) mode
    using mode      = xad::adj<double>;
    using AD        = mode::active_type;
    using tape_type = mode::tape_type;

    // 2. Initialise the tape
    tape_type tape;

    // 3. Initialise active input variables and register them with the tape
    std::vector<AD> x_ad(n);
    for (size_t i = 0; i < n; ++i) {
      x_ad[i] = _input.x[i];
      tape.registerInput(x_ad[i]);
    }

    // 4. Start recording operations onto the tape
    tape.newRecording();

    // 5. Run the Runge-Kutta primal with active types.
    //    Because ode::primal is templated, XAD automatically records all
    //    arithmetic operations performed inside the Runge-Kutta solver.
    std::vector<AD> y_out(n);
    ode::primal(n, x_ad.data(), _input.s, y_out.data());

    // 6. Register the output of interest and seed the adjoint.
    //    The GradBench ODE benchmark differentiates the last element of the
    //    output vector, matching the convention used by all other tools
    //    (e.g. adept/ode.cpp).
    AD& result_node = y_out.back();
    tape.registerOutput(result_node);
    xad::derivative(result_node) = 1.0;  // d(output)/d(output) = 1

    // 7. Run the reverse pass to propagate adjoints back to the inputs
    tape.computeAdjoints();

    // 8. Collect the gradients d(y_out.back()) / d(x[i]) for each input
    for (size_t i = 0; i < n; ++i) {
      output[i] = xad::derivative(x_ad[i]);
    }
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"primal", function_main<ode::Primal>},
                       {"gradient", function_main<Gradient>}});
}
