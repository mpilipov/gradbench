import re
import matplotlib.pyplot as plt
import numpy as np

# === НАСТРОЙКИ ===
filename1 = "gradbench_results/ode_adept_launch.txt"
filename2 = "gradbench_results/ode_xad_launch.txt"

def parse_time_to_seconds(time_str):
    if ':' in time_str:
        parts = time_str.split(':')
        minutes = float(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return float(time_str)

def parse_file(filename):
    data_dict = {}
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
            test_index = match.group(1).strip()
            test_body = match.group(2).strip()
            test_name = f"{test_index} {test_body}"
            time_str = match.group(3).strip()
            try:
                seconds = parse_time_to_seconds(time_str)
                data_dict[test_name] = seconds
            except ValueError:
                continue
    return data_dict

def plot_comparison(data_tool2, data_tool1):
    # 1. Находим общие тесты
    common_tests = sorted(list(set(data_tool2.keys()) & set(data_tool1.keys())))
    if not common_tests:
        print("There are no common tests")
        return

    # 2. Фильтрация (только Jacobian)
    jacobian_tests = [t for t in common_tests if 'jacobian' in t]
    tests_to_plot = jacobian_tests if jacobian_tests else common_tests

    differences = []
    for t in tests_to_plot:
        differences.append(data_tool2[t] - data_tool1[t])

    # === СОЗДАНИЕ НЕРАВНОМЕРНЫХ КОРЗИН (NON-UNIFORM BINS) ===
    min_val = np.floor(min(differences))
    max_val = np.ceil(max(differences))

    # Зона детального просмотра
    detail_min = -1.0
    detail_max = 1.0

    # 1. Левый хвост (шаг 1.0)
    if min_val < detail_min:
        bins_left = np.arange(min_val, detail_min, 1.0)
    else:
        bins_left = np.array([])

    # 2. Правый хвост (шаг 1.0)
    if max_val > detail_max:
        bins_right = np.arange(detail_max + 1.0, max_val + 2.0, 1.0)
    else:
        bins_right = np.array([])

    # 3. Центральная часть (шаг 0.03)
    # Именно этот вариант использовался для вашего графика
    bins_center = np.arange(detail_min, detail_max + 0.0001, 0.03)

    # Склеиваем всё вместе
    bins = np.unique(np.concatenate([bins_left, bins_center, bins_right]))
    # ========================================================

    plt.figure(figsize=(14, 8))

    n, output_bins, patches = plt.hist(differences, bins=bins, edgecolor='black', alpha=0.8)

    # Раскраска
    for patch, bin_left, bin_right in zip(patches, output_bins[:-1], output_bins[1:]):
        bin_center = (bin_left + bin_right) / 2
        if bin_center < 0:
            patch.set_facecolor('#2ca02c') # Зеленый
        else:
            patch.set_facecolor('#d62728') # Красный

    # Ось Y
    plt.axvline(0, color='black', linewidth=2, linestyle='-')

    plt.xlabel('Time difference (s)', fontsize=12)
    plt.ylabel('Frequency - number of tests', fontsize=12)
    # Тот самый заголовок с картинки
    plt.title('Distribution of time differences of the performances (Adept vs XAD for ODE task), on range [-15,1]', fontsize=14)

    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Тики по оси X (основные целые числа)
    major_ticks = np.arange(min_val, max_val + 1, 1.0)
    plt.xticks(major_ticks)

    plt.tight_layout()
    plt.show()

# ЗАПУСК
print(f"Reading XAD from {filename2}...")
data_tool2 = parse_file(filename2)

print(f"Reading Adept from {filename1}...")
data_tool1 = parse_file(filename1)

plot_comparison(data_tool2, data_tool1)
