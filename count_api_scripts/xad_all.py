import os
import re

# A block of path to the code directories
DIR_XAD = r"C:\Users\Michael\Downloads\gradbench\tools\xad"
DIR_ADEPT = r"C:\Users\Michael\Downloads\gradbench\tools\adept"
DIR_ADOLC = r"C:\Users\Michael\Downloads\gradbench\tools\adol-c"
DIR_CODIPACK = r"C:\Users\Michael\Downloads\gradbench\tools\codipack"
DIR_CPPAD = r"C:\Users\Michael\Downloads\gradbench\tools\cppad"
DIR_ENZYME = r"C:\Users\Michael\Downloads\gradbench\tools\enzyme"

# Linking libraries to their directories
LIB_DIRECTORIES = {
    "XAD": DIR_XAD,
    "Adept": DIR_ADEPT,
    "ADOL-C": DIR_ADOLC,
    "CoDiPack": DIR_CODIPACK,
    "CppAD": DIR_CPPAD,
    "Enzyme": DIR_ENZYME,
}

# Rules of counting API calls for all the 6 libraries
API_SIGNATURES = {
    "Adept": [
        r"adept::\w+",  # any calls from the adept namespace
        r"(?<!adept::)\badouble\b",  # using type adouble without the adept namespace
        r"\.new_recording\s*\(", # the new recording on tape
        r"\.set_gradient\s*\(",  # set the start gradient
        r"\.reverse\s*\(",  # launch of reverse pass
        r"\.get_gradient\s*\(",
    ],
    "XAD": [
        r"xad::\w+",  # xad::adj, xad::derivative и др.
        r"\.registerInput\s*\(",  # registering of the input values
        r"\.newRecording\s*\(",  # the new recording on tape
        r"\.registerOutput\s*\(",  # registering of the output values
        r"\.computeAdjoints?\s*\(",  # launch of the reverse pass
        r"\.getDerivative\s*\(",  # get a derivative result
    ],
    "ADOL-C": [
        r"\badouble\b",  # using of adouble active type
        r"\btrace_on\s*\(",  # enabling tape recording
        r"\btrace_off\s*\(",  # disabling tape recording
        r"\bgradient\s*\(",  #gradient calculation (reverse mode)
        r"<<=",  # operator for registering input variables ADOL-C
        r">>=",  #the operator for registering output variables ADOL-C
    ],
    "CoDiPack": [
        r"\bCoDiReverseRunner\b",  # the base class/type CoDiPack
        r"\bcodi[A-Z]\w*\s*\(",  # codiStartRecording(), codiEval(), codiGetGradient() etc.
        r"codi::\w+",  # using the codi namespace
    ],
    "CppAD": [
        r"CppAD::\w+",  # CppAD::AD, CppAD::Independent, CppAD::ADFun
        r"(?<!CppAD::)\bADdouble\b",  # using the ADdouble alias
        r"\.(?:Jacobian|Forward|Reverse)\s*\(",  # methods drivers (for example f.Jacobian()
    ],
    "Enzyme": [
        r"\b__?enzyme_\w+\b",  # the signatures like __enzyme_autodiff, enzyme_const
    ],
}


def remove_cpp_comments(text):
    # removes one-line comments, multi-line comments
    pattern = r"//.*?$|/\*.*?\*/"
    return re.sub(pattern, "", text, flags=re.DOTALL | re.MULTILINE)


def count_api_calls(filepath, library_name):
    # Counts API calls in a particular file
    if not os.path.exists(filepath):
        return -1  # file not found

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # removes comments
    clean_code = remove_cpp_comments(code)

    total_calls = 0
    signatures = API_SIGNATURES.get(library_name, [])

    for sig in signatures:
        matches = re.findall(sig, clean_code)
        total_calls += len(matches) # sums up all the comments


    return total_calls


def analyze_directory(directory, library_name):
    # scans a directory for .cpp/.hpp files, counts API calls
    results = {}
    if not os.path.exists(directory):
        return results

    for filename in os.listdir(directory):
        if filename.endswith(".cpp") or filename.endswith(".hpp"):
            filepath = os.path.join(directory, filename)
            calls = count_api_calls(filepath, library_name)

            # Saves the name of the task without file extension (gmm.cpp -> gmm)
            task_name = filename.split(".")[0]
            # Ignore common configuration/binding files, if there are any (for example, main)
            if task_name in ["main", "common", "gradbench"]:
                continue

            results[task_name] = calls

    return results


def main():
    print("Scanning directories and counting API calls...\n")

    # gathering results for each library
    all_library_results = {}
    for lib_name, dir_path in LIB_DIRECTORIES.items():
        all_library_results[lib_name] = analyze_directory(dir_path, lib_name)

    # finding all the unique tasks, which are implemented in at least one library    all_tasks = set()
    for lib_res in all_library_results.values():
        all_tasks.update(lib_res.keys())

    sorted_tasks = sorted(list(all_tasks))

    if not sorted_tasks:
        print(
            "Tasks for analysis are not found. Check filepaths to the directories."
        )
        return

    # printing summary tabke
    header_format = (
        "{:<15} | {:<11} | {:<11} | {:<11} | {:<11} | {:<11} | {:<11}"
    )
    row_format = "{:<15} | {:<11} | {:<11} | {:<11} | {:<11} | {:<11} | {:<11}"

    print(
        header_format.format(
            "Task", "XAD", "Adept", "ADOL-C", "CoDiPack", "CppAD", "Enzyme"
        )
    )
    print("-" * 93)

    for task in sorted_tasks:
        row_values = [task]
        for lib_name in [
            "XAD",
            "Adept",
            "ADOL-C",
            "CoDiPack",
            "CppAD",
            "Enzyme",
        ]:
            calls = all_library_results[lib_name].get(task, -1)
            # Writing N/A if there is no implementation of the task for this library
            val_to_print = str(calls) if calls != -1 else "N/A"
            row_values.append(val_to_print)

        print(row_format.format(*row_values))


if __name__ == "__main__":
    main()
