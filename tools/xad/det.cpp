#include "gradbench/evals/det.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>
#include <vector>

// Gradient class: computes the gradient of the matrix determinant
// with respect to all elements of A, using XAD adjoint-mode AD.
//
// det::primal calls det_of_minor recursively. The index vectors r and c
// used during the recursion are plain size_t (not AD), so their mutation
// and restoration are invisible to the tape -- only arithmetic on AD
// values is recorded.
class DetXAD : public Function<det::Input, det::GradientOutput> {
public:
  DetXAD(det::Input& input) : Function(input) {}

  void compute(det::GradientOutput& output) {
    // 1. Define XAD types for reverse (adjoint) mode
    using mode      = xad::adj<double>;
    using AD        = mode::active_type;
    using tape_type = mode::tape_type;

    // 2. Initialise the tape
    tape_type tape;

    // ell:       matrix dimension (ell x ell)
    // n_elements: total number of matrix entries (ell * ell)
    size_t ell        = _input.ell;
    size_t n_elements = _input.A.size();

    // 3. Initialise active input variables -- one per matrix element --
    //    and register each with the tape
    std::vector<AD> A_ad(n_elements);
    for (size_t i = 0; i < n_elements; ++i) {
      A_ad[i] = _input.A[i];
      tape.registerInput(A_ad[i]);
    }

    // 4. Start recording operations onto the tape
    tape.newRecording();

    // 5. Evaluate the determinant with active types.
    //    det::primal<AD> calls det_of_minor<AD> recursively; XAD records
    //    all multiplications and additions performed during the expansion.
    AD result_det;
    det::primal<AD>(ell, A_ad.data(), &result_det);

    // 6. Register the scalar output and seed its adjoint
    tape.registerOutput(result_det);
    xad::derivative(result_det) = 1.0;  // d(det)/d(det) = 1

    // 7. Run the reverse pass to propagate adjoints back to the inputs
    tape.computeAdjoints();

    // 8. Collect d(det) / d(A[i]) for every matrix element
    output.resize(n_elements);
    for (size_t i = 0; i < n_elements; ++i) {
      output[i] = xad::derivative(A_ad[i]);
    }
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"primal", function_main<det::Primal>},
                       {"gradient", function_main<DetXAD>}});
}
