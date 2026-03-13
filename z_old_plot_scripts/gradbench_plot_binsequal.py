import re
import matplotlib.pyplot as plt
import numpy as np

log_data = ""
filename1="gradbench_results/gmm_adept_launch.txt"
filename2="gradbench_results/gmm_xad_launch.txt"
BIN_WIDTH = 0.03

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

# Берём только jacobian
    jacobian_tests = [t for t in common_tests if 'jacobian' in t]
    tests_to_plot = jacobian_tests if jacobian_tests else common_tests

    differences = []
    for t in tests_to_plot:
        diff = data_tool2[t] - data_tool1[t]  # xad - adept
        differences.append(diff)
        print(diff)

    differences = np.array(differences)

# Разделяем по знаку
    adept_faster = differences[differences > 0]   # справа
    adept_slower = differences[differences < 0]   # слева

# Общие границы, чтобы гистограмма была симметричной
    max_abs = max(abs(differences.min()), abs(differences.max()))
    bins = np.linspace(-max_abs, max_abs, 150)

    plt.figure(figsize=(10, 6))

    plt.hist(adept_slower, bins=bins, alpha=0.7, label="adept slower than xad")

    plt.hist(adept_faster, bins=bins, alpha=0.7, label="adept faster than xad")

# Вертикальная линия в нуле
    plt.axvline(0, linestyle='--')

    plt.xlabel("Time difference (xad − adept), seconds")
    plt.ylabel("Frequency")
    plt.title("Frequency histogram of time differences (jacobian)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(-0.5, 0.5)
    plt.tight_layout()
    plt.show()

print(f"Reading XAD from {filename2}...")
data_tool2 = parse_file(filename2)

print(f"Reading Adept from {filename1}...")
data_tool1 = parse_file(filename1)

print(f"Tests found: XAD={len(data_tool2)}, Adept={len(data_tool1)}")
plot_comparison(data_tool2, data_tool1)
