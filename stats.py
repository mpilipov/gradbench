import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

xad_gmm_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\xad_det_averaged.txt"
cppad_gmm_log = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\cppad_det_averaged.txt"

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
    pattern = r'eval\s+\w+::(?:jacobian|gradient)\s+([\w_]+)\s*,\s*(\d+(?:\.\d+)?)\s*(ms|s)\s+evaluate.*?(✓|✗)'
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

xad_data = parse_log(xad_gmm_log)
cppad_data = parse_log(cppad_gmm_log)
# taking only tests which are successful for both tools
common_tests = sorted(list(set(xad_data.keys()) & set(cppad_data.keys())))

times_xad = [xad_data[t] for t in common_tests]
times_cppad = [cppad_data[t] for t in common_tests]

# statistical testing
stat, p_value = stats.wilcoxon(times_xad, times_cppad)
print(f"Number of common tests for both tools: {len(common_tests)}")
print(f"Wilcoxon statistic: {stat}")
print(f"P-value: {p_value:.5f}")

median_xad = np.median(times_xad)
median_cppad = np.median(times_cppad)
iqr_xad = stats.iqr(times_xad)
iqr_cppad = stats.iqr(times_cppad)
print(f"Median XAD time:   {median_xad:.4f} s (IQR: {iqr_xad:.4f} s)")
print(f"Median cppad time: {median_cppad:.4f} s (IQR: {iqr_cppad:.4f} s)")
if p_value < 0.05:
    print("Conclusion: The performance difference is statistically significant (p < 0.05)")
else:
    print("Conclusion: The performance difference is not statistically significant.")

# visualization box plot
plt.figure(figsize=(9, 6))
plt.boxplot([times_xad, times_cppad], tick_labels=['XAD', 'cppad'], patch_artist=True,
            boxprops=dict(facecolor='#E0F7FA', color='#006064'),
            medianprops=dict(color='red', linewidth=2))
plt.ylabel('Execution time (seconds)', fontsize=12)
# setting the logarythmic scale
plt.yscale('log')
plt.title('Performance distribution (DET gradient task)', fontsize=14)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
