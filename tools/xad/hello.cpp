#include "gradbench/evals/hello.hpp"
#include "gradbench/main.hpp"

// Connecting XAD
#include <XAD/XAD.hpp>

class Double : public Function<hello::Input, hello::DoubleOutput> {
public:
  Double(hello::Input& input) : Function(input) {}

  void compute(hello::DoubleOutput& output) {
    // Defining types
    // xad::adj<double> is a mode adjoint for double type
    typedef xad::adj<double> mode;
    typedef mode::tape_type tape_type;
    typedef mode::active_type AD;

    // Tape initialization
    tape_type tape;

    // x - an active input variable
    AD x = _input;

    // tape input
    tape.registerInput(x);

    tape.newRecording();

    // computation of the function
    AD y = hello::square(x);

    // tape output
    tape.registerOutput(y);

    // set f'(y) = 1
    // В документации используется глобальная функция derivative(y) = 1.0;
    xad::derivative(y) = 1.0;

    // computing of the derivatives using backward mode
    tape.computeAdjoints();

    // derivative by x
    output = xad::derivative(x);
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"square", function_main<hello::Square>},
                       {"double", function_main<Double>}});
}
