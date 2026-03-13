#include "gradbench/evals/llsq.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>
#include <vector>

// Gradient class: computes the gradient of the least-squares objective
// with respect to all polynomial coefficients x, using XAD adjoint-mode AD.
//
// Note: llsq.hpp defines two versions of primal():
//   - generic template primal<T>()  -- used here with T=AD (no OpenMP,
//   tape-safe)
//   - explicit specialisation for double -- uses OpenMP, only called by
//   llsq::Primal
// XAD will automatically select the generic template, avoiding any tape/thread
// conflict.
class LlsqXAD : public Function<llsq::Input, llsq::GradientOutput> {
public:
  LlsqXAD(llsq::Input& input) : Function(input) {}

  void compute(llsq::GradientOutput& output) {
    // 1. Define XAD types for reverse (adjoint) mode
    using mode      = xad::adj<double>;
    using AD        = mode::active_type;
    using tape_type = mode::tape_type;

    // 2. Initialise the tape
    tape_type tape;

    // n: number of sample points in the least-squares fit
    // m: number of polynomial coefficients (size of x)
    size_t n = _input.n;
    size_t m = _input.x.size();

    // 3. Initialise active input variables and register them with the tape.
    //    Each x[i] is a polynomial coefficient to differentiate with respect
    //    to.
    std::vector<AD> x_ad(m);
    for (size_t i = 0; i < m; ++i) {
      x_ad[i] = _input.x[i];
      tape.registerInput(x_ad[i]);
    }

    // 4. Start recording operations onto the tape
    tape.newRecording();

    // 5. Evaluate the primal (least-squares objective) with active types.
    //    The generic template primal<AD>() records all arithmetic on the tape.
    //    The sign function s() inside primal uses comparisons that return bool,
    //    so XAD treats it as a piecewise constant -- mathematically correct
    //    since the sign function has zero derivative almost everywhere.
    AD result_error;
    llsq::primal<AD>(n, m, x_ad.data(), &result_error);

    // 6. Register the scalar output and seed its adjoint
    tape.registerOutput(result_error);
    xad::derivative(result_error) = 1.0;  // d(objective)/d(objective) = 1

    // 7. Run the reverse pass to propagate adjoints back to the inputs
    tape.computeAdjoints();

    // 8. Collect d(objective) / d(x[i]) for each coefficient
    output.resize(m);
    for (size_t i = 0; i < m; ++i) {
      output[i] = xad::derivative(x_ad[i]);
    }
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"primal", function_main<llsq::Primal>},
                       {"gradient", function_main<LlsqXAD>}});
}
