import re
import matplotlib.pyplot as plt
import numpy as np

log_data = ""
filename1="gradbench_results/ode_adept_launch.txt"
filename2="gradbench_results/ode_xad_launch.txt"

def parse_time_to_seconds(time_str):
    if ':' in time_str:
        # format mm:ss.ms
        parts = time_str.split(':')
        minutes = float(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        # seconds
        return float(time_str)

def parse_file(filename):
    data_dict = {}
    # 1. index [N]
    # 2. test name
    # 3. time (can be a number or mm:ss.ms)
    regex_pattern = r'(\[\s*\d+\])\s+eval\s+(.+?)\s+((?:\d+:)?\d+\.\d+)'

    try:
        with open(filename, 'r', encoding='utf-16') as f:
            content = f.read()
    except (UnicodeError, FileNotFoundError):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: the file {filename} is not found")
            return {}

    for line in content.split('\n'):
        match = re.search(regex_pattern, line)
        if match:
            # taking index of group 1 and name from group 2
            test_index = match.group(1).strip()
            test_body = match.group(2).strip()

            # concatenating the index and the body
            test_name = f"{test_index} {test_body}"

            time_str = match.group(3).strip() # time is on the 3rd group
            try:
                seconds = parse_time_to_seconds(time_str)
                data_dict[test_name] = seconds
            except ValueError:
                continue
    return data_dict

def plot_comparison(data_tool2, data_tool1):
    # 1. Find common tests for both libraries implementations for the task
    common_tests = sorted(list(set(data_tool2.keys()) & set(data_tool1.keys())))
    if not common_tests:
        print("There are no common tests")
        return

    # 2. Filtration (only Jacobian) ???
    jacobian_tests = [t for t in common_tests if 'jacobian' in t]
    tests_to_plot = jacobian_tests if jacobian_tests else common_tests
    # tests_to_plot = common_tests # both jacobian and objective
    differences = []
    for t in tests_to_plot:
        t_xad = data_tool2[t]
        t_adept = data_tool1[t]
        diff = t_xad - t_adept
        differences.append(diff)


    # creating non-uniform bins (by data borders)
    min_val = np.floor(min(differences))
    max_val = np.ceil(max(differences))

    # area of more detailed view
    detail_min = -1
    detail_max = 1

    # distribution of data by bins:
    # the values < -1
    if min_val < detail_min:
        bins_left = np.arange(min_val, detail_min, 1.0)
    else:
        bins_left = np.array([])

    # the values > 1
    if max_val > detail_max:
        bins_right = np.arange(detail_max + 1.0, max_val + 2.0, 1.0)
    else:
        bins_right = np.array([])

    # central bins  [-1, 1] are with higher detalization
    bins_center_neg = np.arange(detail_min, 0, 0.03)

    # 2. От 0 до detail_max
    bins_center_pos = np.arange(0, detail_max + 0.0001, 0.03)
    #print(len(bins_center_neg+bins_center_pos))
    # concatenating everything in one data array
    bins = np.unique(np.concatenate([bins_left, bins_center_neg, bins_center_pos, bins_right]))

    plt.figure(figsize=(14, 8))

    n, output_bins, patches = plt.hist(differences, bins=bins, edgecolor='black', alpha=0.8)

    for patch, bin_left, bin_right in zip(patches, output_bins[:-1], output_bins[1:]):
        bin_center = (bin_left + bin_right) / 2
        if bin_center < 0:
            patch.set_facecolor('#2ca02c') # Зеленый (XAD быстрее)
        else:
            patch.set_facecolor('#d62728') # Красный (Adept быстрее)

    # (left part - XAD is faster, right part - Adept is faster)
    plt.xlabel('Time difference (s)\n', fontsize=12)
    plt.ylabel('Frequency - number of tests', fontsize=12)
    plt.title('Distribution of time differences of the performances (Adept-vs-XAD for ODE task), on range [-0.5, 0.5] there are 36 bins with step=0.014', fontsize=14)

    plt.grid(axis='y', linestyle='--', alpha=0.5)

    major_ticks = np.arange(min_val, max_val + 1, 1.0)
    plt.xticks(major_ticks)
    plt.xlim(-0.5, 0.5)
    plt.tight_layout()
    plt.show()


print(f"Reading XAD from {filename2}...")
data_tool2 = parse_file(filename2)

print(f"Reading Adept from {filename1}...")
data_tool1 = parse_file(filename1)

print(f"Tests found: XAD={len(data_tool2)}, Adept={len(data_tool1)}")
plot_comparison(data_tool2, data_tool1)
