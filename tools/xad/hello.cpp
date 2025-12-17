#include "gradbench/evals/hello.hpp"
#include "gradbench/main.hpp"

// Connecting XAD
#include <XAD/XAD.hpp>
using namespace xad;
using namespace hello;
template <typename T>
T double_x(T x) {
  return x * 2.0;
}
class HelloSquareXAD : public Function<hello::Input, hello::DoubleOutput> {
public:
  HelloSquareXAD(hello::Input& input) : Function(input) {}

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
    AD y =
        hello::square(x);  // the comupted function itself (also hello:square)

    // output is function y=x^2 value
    output = y.value();
  }
};

class HelloDoubleXAD : public Function<hello::Input, hello::DoubleOutput> {
public:
  HelloDoubleXAD(hello::Input& input) : Function(input) {}

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

    AD y = double_x(x);  // the comupted function itself (also hello:square)

    // output is function y=2*x value
    output = y.value();
  }
};

int main(int argc, char* argv[]) {
  return generic_main(argc, argv,
                      {{"square", function_main<HelloSquareXAD>},
                       {"double", function_main<HelloDoubleXAD>}});
}
