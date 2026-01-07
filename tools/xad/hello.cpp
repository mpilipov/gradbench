#include "gradbench/evals/hello.hpp"
#include "gradbench/main.hpp"

// Connecting XAD
#include <XAD/XAD.hpp>
using namespace xad;
using namespace hello;
// template <typename T>
// T square_x(T x) {
//   return x * 2.0;
// }

// calculates the function value
class HelloFunctionXAD
    : public Function<hello::Input,
                      hello::DoubleOutput> {  // DoubleOutput is hello.hpp type
public:                                       // constructor init
  HelloFunctionXAD(hello::Input& input) : Function(input) {}

  void compute(hello::DoubleOutput& output) {
    // Defining types
    // xad::adj<double> is a mode adjoint for double type
    typedef xad::adj<double>  mode;
    typedef mode::tape_type   tape_type;
    typedef mode::active_type AD;

    // Tape initialization
    tape_type tape;

    // x - an active input variable
    AD x = _input;  //(_input - is saved input at the constructor of class
                    // Function (main.hpp))

    // tape input
    tape.registerInput(x);
    tape.newRecording();
    AD y = hello::square(
        x);  // set the comupted function itself (part of hello.hpp)
    // we don't call computeAdjoints() function here
    // output is a value of function y=x^2 (hello::square(x))
    output = y.value();
  }
};
// calculates derivative of the function
class HelloDerivativeXAD : public Function<hello::Input, hello::DoubleOutput> {
public:  // constructor init
  HelloDerivativeXAD(hello::Input& input) : Function(input) {}

  void compute(hello::DoubleOutput& output) {
    // Defining types
    // xad::adj<double> is a mode adjoint for double type
    typedef xad::adj<double>  mode;
    typedef mode::tape_type   tape_type;
    typedef mode::active_type AD;

    // Tape initialization
    tape_type tape;

    // x - an active input variable
    AD x = _input;  //(_input - is saved input at the constructor of class
                    // Function (main.hpp))

    // tape input
    tape.registerInput(x);

    tape.newRecording();
    // set the comupted function itself (also hello::square)
    AD y = hello::square(x);
    tape.registerOutput(y);
    derivative(y) = 1.0;
    // call computeAdjoints() to calculate the derivative
    tape.computeAdjoints();

    // output is a derivative of function y=x^2
    output = xad::derivative(x);
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"square", function_main<HelloFunctionXAD>},
                       {"double", function_main<HelloDerivativeXAD>}});
}
