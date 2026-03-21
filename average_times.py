import re
import os
from collections import defaultdict

# 1. Paths to the gradbench results
file1 = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\det_enzyme_run1.txt"
file2 = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\det_enzyme_run2.txt"
file3 = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\det_enzyme_run3.txt"

# 2. Name of the final result data
output_file = r"C:\Users\Michael\Downloads\gradbench\gradbench_results2\enzyme_det_averaged.txt"

def parse_time(val_str, unit):
    # converting time to ms
    if ':' in val_str:
        m, s = val_str.split(':')
        return int(m) * 60 + float(s)
    val = float(val_str)
    if unit == 'ms':
        return val / 1000.0
    return val

def extract_times(filepath, data_dict):
    if not os.path.exists(filepath):
        print(f"Error: this file was not found -> {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        log_text = f.read()

    # pattern takes the total time of the test (3, 4 groups) and number of computations (5 group)
    pattern = r'\[(\d+)\]\s+eval\s+(?:\w+::)?gradient\s+([\w_]+)\s+([\d:.]+)\s*(ms|s)?\s+~.*?(?:×\s*(\d+)\s*)?(✓|✗)'

    for line in log_text.strip().split('\n'):
        match = re.search(pattern, line)
        if match:
            test_id = match.group(1)      # test number ([4])
            param = match.group(2)        # test parameters ( 5_run0)
            total_time_val = match.group(3) # Total time of the test (1.357)
            unit = match.group(4)         # s or ms for Total time of the test
            runs_str = match.group(5)
            runs_count = int(runs_str) if runs_str else 1  # number of computaions (63876)
            status = match.group(6)       # check if the test result = ✓

            if status == '✓' and runs_count > 0:
                total_t_sec = parse_time(total_time_val, unit)
                # Dividing the total time by number of computations
                time_per_run = total_t_sec / runs_count

                data_dict[param]['times'].append(time_per_run)
                data_dict[param]['id'] = test_id

# A dictionary: key - test parameters, value - a dictionary with ID and list of times per run
times_data = defaultdict(lambda: {'id': '', 'times': []})

# gathering data from all 3 runs
extract_times(file1, times_data)
extract_times(file2, times_data)
extract_times(file3, times_data)

# writing the averaged result
with open(output_file, 'w', encoding='utf-8') as f:
    tests_written = 0
    # sorting the tests by its number
    sorted_tests = sorted(times_data.items(), key=lambda x: int(x[1]['id']) if x[1]['id'] else 0)

    for param, info in sorted_tests:
        times = info['times']
        test_id = info['id']

        # writing only successfull tests
        if len(times) > 0:
            avg_time = sum(times) / len(times)
            # creating a string to be red by stats.py
            f.write(f"[{test_id}] eval det::gradient {param} , {avg_time:.9f} s evaluate ✓\n")
            tests_written += 1

print(f"The process is completed. Were averaged {tests_written} tests (only gradient).")
print(f"The result is saved in {output_file}")
