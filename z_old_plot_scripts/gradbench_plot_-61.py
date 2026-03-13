import re
import matplotlib.pyplot as plt
import numpy as np

# === НАСТРОЙКИ ===
filename1 = "gradbench_results/llsq_adept_launch.txt"
filename2 = "gradbench_results/llsq_xad_launch.txt"
STEP = 0.03  # Ширина столбца

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
    common_tests = sorted(list(set(data_tool2.keys()) & set(data_tool1.keys())))
    if not common_tests:
        print("There are no common tests")
        return

    jacobian_tests = [t for t in common_tests if 'jacobian' in t]
    tests_to_plot = jacobian_tests if jacobian_tests else common_tests

    differences = []
    for t in tests_to_plot:
        diff = data_tool2[t] - data_tool1[t]
        differences.append(diff)

    # === ГЕНЕРАЦИЯ КОРЗИН (СИММЕТРИЧНО ОТ НУЛЯ) ===
    # 1. Левая часть: от 0 до -6.1 (с небольшим запасом)
    bins_neg = np.arange(0, -6.1, -STEP)

    # 2. Правая часть: от 0 до 1.1 (с небольшим запасом)
    bins_pos = np.arange(0, 1.1, STEP)

    # Объединяем
    bins = np.unique(np.concatenate([bins_neg, bins_pos]))
    # ===============================================

    plt.figure(figsize=(14, 8))

    n, output_bins, patches = plt.hist(differences, bins=bins, edgecolor='black', alpha=0.8)

    # Раскраска
    for patch, bin_left, bin_right in zip(patches, output_bins[:-1], output_bins[1:]):
        bin_center = (bin_left + bin_right) / 2
        if bin_center < 0:
            patch.set_facecolor('#2ca02c') # Зеленый
        else:
            patch.set_facecolor('#d62728') # Красный

    plt.axvline(0, color='black', linewidth=2)

    # === НАСТРОЙКА ОСЕЙ И ПОДПИСЕЙ ===
    plt.xlabel('Time difference (s)', fontsize=12)
    plt.ylabel('Frequency - number of tests', fontsize=12)
    plt.title(f'Distribution of time differences (Adept-vs-XAD for LLSQ task)\nRange [-6, 1], Step={STEP}', fontsize=14)

    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # 1. Устанавливаем границы отображения от -6 до 1
    plt.xlim(-6, 1)

    # 2. Делаем подписи внизу (xticks) с шагом 0.5 сек для читаемости
    # np.arange(-6, 1.1, 0.5) создаст метки -6.0, -5.5, ... 0.5, 1.0
    ticks = np.arange(-6, 1.1, 0.5)
    plt.xticks(ticks)

    plt.grid(axis='x', linestyle=':', alpha=0.5)

    plt.tight_layout()
    plt.show()

# ЗАПУСК
print(f"Reading XAD from {filename2}...")
data_tool2 = parse_file(filename2)
print(f"Reading Adept from {filename1}...")
data_tool1 = parse_file(filename1)
print(f"Tests found: XAD={len(data_tool2)}, Adept={len(data_tool1)}")
plot_comparison(data_tool2, data_tool1)
