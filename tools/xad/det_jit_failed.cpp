#include "gradbench/evals/det.hpp"
#include "gradbench/main.hpp"
#include <XAD/XAD.hpp>

// for JIT management
// #include <XAD/JITCompilerTLS.cpp>
// #include <XAD/JITGraphInterpreter.cpp>

#include <vector>

// Gradient class: computes the gradient of the matrix determinant
// with respect to all elements of A, using XAD adjoint-mode AD.
//
// det::primal calls det_of_minor recursively. The index vectors r and c
// used during the recursion are plain size_t (not AD), so their mutation
// and restoration are invisible to the tape -- only arithmetic on AD
// values is recorded.
class DetXAD : public Function<det::Input, det::GradientOutput> {
  // 1. Define XAD types for JIT mode
  using AD = xad::AReal<double, 1>;

  // 2. State variables that persist across runs
  xad::JITCompiler<double, 1> jit;
  AD                          result_det;
  std::vector<AD>             A_ad;
  double                      out_val;

public:
  DetXAD(det::Input& input) : Function(input), A_ad(input.A.size()) {
    // ell:       matrix dimension (ell x ell)
    // n_elements: total number of matrix entries (ell * ell)
    size_t ell        = _input.ell;
    size_t n_elements = _input.A.size();

    // 3.  and register each with the tape
    for (size_t i = 0; i < n_elements; ++i) {
      A_ad[i] = _input.A[i];
      jit.registerInput(A_ad[i]);
    }

    // forward propagation - XAD writes every operation in det::primal
    det::primal<AD>(ell, A_ad.data(), &result_det);

    // registering of scalar output
    jit.registerOutput(result_det);

    // jit-compilation - reversing recursion to one linear function
    jit.compile();
  }
  void compute(det::GradientOutput& output) {

    size_t n_elements = _input.A.size();
    // update input values by new gradbench data
    for (size_t i = 0; i < n_elements; ++i) {
      A_ad[i] = _input.A[i];
    }

    // Cleaning derivatives from the previous run
    jit.clearDerivatives();

    // fast pass by already compilated code
    jit.forward(&out_val);

    // setting the seed
    jit.setDerivative(result_det.getSlot(), 1.0);

    // back propagation
    jit.computeAdjoints();

    // 8. Collect d(det) / d(A[i]) for every matrix element
    output.resize(n_elements);
    for (size_t i = 0; i < n_elements; ++i) {
      output[i] = jit.getDerivative(A_ad[i].getSlot());
    }
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"primal", function_main<det::Primal>},
                       {"gradient", function_main<DetXAD>}});
}
