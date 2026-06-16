import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

xad_ode_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\ode_xad_averaged.txt"
adept_ode_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\ode_adept_averaged.txt"
adolc_ode_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\ode_adolc_averaged.txt"
codipack_ode_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\ode_codipack_averaged.txt"
cppad_ode_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\ode_cppad_averaged.txt"
enzyme_ode_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\ode_enzyme_averaged.txt"

log_files = {
    'XAD': xad_ode_log,
    'Adept': adept_ode_log,
    'ADOL-C': adolc_ode_log,
    'CoDiPack': codipack_ode_log,
    'CppAD': cppad_ode_log,
    'Enzyme': enzyme_ode_log
}

def parse_log(filepath):
    results = {}
    # reading the file
    if not os.path.exists(filepath):
        print(f"Error: the file was not found -> {filepath}")
        return results
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            log_text = f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-16') as f:
            log_text = f.read()

    # 1. Taking test parameters in 4th column
    # 2. Taking type of the test (only if it is jacobian/gradient)
    # 3. Taking time in 7th column (before word 'evaluate')
    # 4. Taking abovementioned data only if there is ✓ in the end of string
    pattern = r'eval\s+\w+::(?:jacobian|gradient)\s+([\w_=,]+)\s*,\s*(\d+(?:\.\d+)?)\s*(ms|s)\s+evaluate.*?(✓|✗)'
    #pattern = r'eval\s+\w+::(?:jacobian|gradient)\s+([\w_]+)\s*,\s*(\d+(?:\.\d+)?)\s*(ms|s)\s+evaluate.*?(✓|✗)'
    for line in log_text.strip().split('\n'):
        match = re.search(pattern, line)
        if match:
            params = match.group(1) # test parameters
            time_val = float(match.group(2)) # average run time
            unit = match.group(3) # units (seconds or milliseconds)
            status = match.group(4)

            # taking successful tests
            if status == '✓':
                # making all the times in seconds
                if unit == 'ms':
                    time_val /= 1000.0
                results[params] = time_val
    return results

# logs parsing
all_data = {}
for lib_name, filepath in log_files.items():
    all_data[lib_name] = parse_log(filepath)

# finding successful tests
successful_sets = [set(data.keys()) for data in all_data.values() if data]
if not successful_sets:
    print("Error: No data for analysis, check filepaths.")
    exit()
# taking only tests which are successful for both tools
common_tests = sorted(list(set.intersection(*successful_sets)))
print(f"Number of common successful tests: {len(common_tests)}\n")

if len(common_tests) == 0:
    print("Error: No common tests")
    exit()

# creating lists of timings for each library based on common_tests
libraries = list(log_files.keys())
times_per_lib = {
    lib: [all_data[lib][t] for t in common_tests] for lib in libraries
}

# statistical testing
# Friedman criteria
arrays_for_test = [times_per_lib[lib] for lib in libraries]
stat, p_value = stats.friedmanchisquare(*arrays_for_test)

for lib in libraries:
    times = times_per_lib[lib]
    median = np.median(times)
    iqr = stats.iqr(times)
    print(f"Median {lib:8}: {median:.4f} s (IQR: {iqr:.4f} s)")

print(f"Friedman statistics: {stat:.4f}")
print(f"P-value: {p_value:.5f}")

if p_value < 0.05:
    print("Conclusion: The performance difference is statistically significant (p < 0.05)")
else:
    print("Conclusion: The performance difference is not statistically significant.")

# visualization box plot
plt.figure(figsize=(11, 6))
box_data = [times_per_lib[lib] for lib in libraries]
bp = plt.boxplot(
    box_data,
    tick_labels=libraries,
    patch_artist=True,
    medianprops=dict(color='red', linewidth=2),
)
plt.ylabel('Execution time (seconds)', fontsize=12)
plt.yscale('log')  # logarithmic scale
plt.title(
    'Performance distribution comparison across 6 AD libraries (ODE task)',
    fontsize=14,
    fontweight='bold',
)
plt.grid(True, axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
