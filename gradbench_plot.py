import re
import matplotlib.pyplot as plt
import numpy as np
log_data = ""
filename1="gradbench_results/gmm_adept_launch.txt"
filename2="gradbench_results/gmm_xad_launch.txt"

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
    # 2. type (def or eval)
    # 3. test name
    # 4. time (can be a number or mm:ss.ms)
    regex_pattern = r'\[\s*\d+\]\s+eval\s+(.+?)\s+((?:\d+:)?\d+\.\d+)'
                    # убрать эту часть regexp
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
            test_name = " ".join(match.group(1).split())
            time_str = match.group(2).strip()
            try:
                seconds = parse_time_to_seconds(time_str)
                data_dict[test_name] = seconds
            except ValueError:
                continue
    return data_dict

def plot_comparison(xad_data, adept_data):
    # 1. Find common tests for both libraries implementations for the task
    common_tests = sorted(list(set(xad_data.keys()) & set(adept_data.keys())))
    print(common_tests)
    if not common_tests:
        print("There are no common tests")
        return

    # Filtration (only Jacobian) ???
    jacobian_tests = [t for t in common_tests if 'jacobian' in t]
    tests_to_plot = jacobian_tests if jacobian_tests else common_tests

    # 2. Split data on two parts
    left_side = []  # (name, abs_diff) - XAD is faster than Adept
    right_side = [] # (name, abs_diff) - Adept is faster than XAD

    for t in tests_to_plot:
        t_xad = xad_data[t]
        t_adept = adept_data[t]
        diff = t_xad - t_adept

        clean_name = t.replace('gmm::jacobian', '').replace('gmm::objective', 'Obj').strip()
        #print(t)
        if diff < 0:
            # XAD is faster Adept
            left_side.append((clean_name, abs(diff)))
        else:
            # XAD is slower than Adept
            right_side.append((clean_name, abs(diff)))

    # 3. Sorting
    # left side - to sort in ascending
    left_side.sort(key=lambda x: x[1])

    # right side - to sort in descending
    right_side.sort(key=lambda x: x[1], reverse=True)

    # 4. Подготовка координат для графика
    # Левая сторона (отрицательные X): индексы -N, ..., -1
    x_left = np.arange(-len(left_side), 0)
    y_left = [item[1] for item in left_side]
    labels_left = [item[0] for item in left_side]
    #print(labels_left)

    # Правая сторона (положительные X): индексы 0, ..., N-1
    # Добавляем небольшой сдвиг (0.5), чтобы был зазор посередине
    x_right = np.arange(0, len(right_side))
    y_right = [item[1] for item in right_side]
    labels_right = [item[0] for item in right_side]

    # 5. Plot the graph
    plt.figure(figsize=(16, 9))


    bars_left = plt.bar(x_left + 0.5, y_left, width=0.8, color='#2ca02c', edgecolor='black', alpha=0.8, label='XAD Быстрее')

    bars_right = plt.bar(x_right + 0.5, y_right, width=0.8, color='#d62728', edgecolor='black', alpha=0.8, label='Adept Быстрее')

    # Axis Y
    plt.axvline(0, color='black', linewidth=2, linestyle='-')

    # Vertical label
    plt.ylabel('Time difference (seconds)', fontsize=12)

    # Labels for bars on X axis
    all_x = np.concatenate([x_left + 0.5, x_right + 0.5])
    all_labels = labels_left + labels_right
    plt.xticks(all_x, all_labels, rotation=45, ha='right', fontsize=9)

    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Bar values labels
    def annotate_bars(bars):
        for bar in bars:
            height = bar.get_height()+0.1
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}',
                     ha='center', va='bottom', fontsize=8, rotation=90)

    annotate_bars(bars_left)
    annotate_bars(bars_right)
    plt.tight_layout()
    plt.show()

print(f"Reading XAD from {filename2}...")
data_xad = parse_file(filename2)

print(f"Reading Adept from {filename1}...")
data_adept = parse_file(filename1)

print(f"Tests found: XAD={len(data_xad)}, Adept={len(data_adept)}")
plot_comparison(data_xad, data_adept)
