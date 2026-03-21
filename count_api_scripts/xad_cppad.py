import os
import re

# paths to code directories for each library
DIR_CPPAD = r"C:\Users\Michael\Downloads\gradbench\tools\cppad"
DIR_XAD = r"C:\Users\Michael\Downloads\gradbench\tools\xad"

# How to count API calls
API_SIGNATURES = {
    "cppad": [
        r"CppAD::\w+",                          # matches CppAD::AD, CppAD::Independent, CppAD::ADFun
        r"(?<!CppAD::)\bADdouble\b",            # matches the ADdouble typedef (if not prefixed by CppAD::)
        r"\.(?:Jacobian|Forward|Reverse)\s*\(", # matches specific CppAD driver methods like f.Jacobian()
    ],
    "xad": [
        r"xad::\w+",                # xad::adj, xad::derivative, other classes/functions
        r"\.registerInput\s*\(",    # registration of independent variables
        r"\.newRecording\s*\(",     # start of tape recording
        r"\.registerOutput\s*\(",   # output registration
        r"\.computeAdjoints?\s*\(", # running of gradient calculation (back propagation)
        r"\.getDerivative\s*\(",    # getting the gradient
    ]
}

def remove_cpp_comments(text):
    # removes 1-string and multi-string comments
    pattern = r"//.*?$|/\*.*?\*/"
    return re.sub(pattern, "", text, flags=re.DOTALL | re.MULTILINE)

def count_api_calls(filepath, library_name):
    # counts API calls in a particular file
    if not os.path.exists(filepath):
        return -1 # the file wasn't found

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read() # the file was found

    # clean the code out of comments
    clean_code = remove_cpp_comments(code)

    total_calls = 0
    signatures = API_SIGNATURES.get(library_name, [])

    for sig in signatures:
        # summing up al the API calls in clean_code using patterns
        matches = re.findall(sig, clean_code)
        total_calls += len(matches)

    return total_calls

def analyze_directory(directory, library_name):
    # checks all the .cpp/.hpp files in the directory
    results = {}
    if not os.path.exists(directory):
        print(f"The directory was not found: {directory}")
        return results

    for filename in os.listdir(directory):
        if filename.endswith(".cpp") or filename.endswith(".hpp"):
            filepath = os.path.join(directory, filename)
            calls = count_api_calls(filepath, library_name)

            # saving the results with removed extension (det.cpp -> det)
            task_name = filename.split('.')[0]
            results[task_name] = calls

    return results

def main():
    print("API calls in the library:")

    adept_results = analyze_directory(DIR_CPPAD, "cppad")
    xad_results = analyze_directory(DIR_XAD, "xad")

    # looks for the common tasks which were solved by both libraries (there are implementations)
    common_tasks = sorted(list(set(adept_results.keys()) & set(xad_results.keys())))

    if not common_tasks:
        print("There are no any common tasks for comparisons")
        return

    # printing the table
    print(f"{'Task':<15} | {'XAD API Calls':<15} | {'Cppad API Calls':<15}")
    print("-" * 50)

    for task in common_tasks:
        calls_xad = xad_results[task]
        calls_adept = adept_results[task]
        print(f"{task:<15} | {calls_xad:<15} | {calls_adept:<15}")

if __name__ == "__main__":
    main()
