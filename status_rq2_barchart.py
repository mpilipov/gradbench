import matplotlib.pyplot as plt
import numpy as np


tasks = ['det', 'gmm', 'llsq', 'ode']

# Метрика А: Строки кода (LOC) - результаты утилиты cloc
loc_xad = [45, 60, 35, 80]     # Подставьте реальные цифры для XAD
loc_adept = [50, 75, 40, 95]   # Подставьте реальные цифры для Adept

# Метрика B: Вызовы API - результаты скрипта count_api.py
api_xad = [4, 10, 4, 4]         # Подставьте реальные цифры для XAD
api_adept = [10, 24, 10, 10]      # Подставьте реальные цифры для Adept
# ==========================================


x = np.arange(len(tasks))  # Расположение задач по оси X
width = 0.35  # Ширина столбцов

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# --- График 1: Строки кода (LOC) ---
rects1_loc = ax1.bar(x - width/2, loc_xad, width, label='XAD', color='#4CAF50', edgecolor='black')
rects2_loc = ax1.bar(x + width/2, loc_adept, width, label='Adept', color='#FFC107', edgecolor='black')

ax1.set_ylabel('Lines of Code (LOC)', fontsize=12)
ax1.set_title('Metric A: code size comparison', fontsize=14)
ax1.set_xticks(x)
ax1.set_xticklabels(tasks, fontsize=12)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# Добавляем цифры над столбцами
ax1.bar_label(rects1_loc, padding=3)
ax1.bar_label(rects2_loc, padding=3)

# --- График 2: Вызовы API ---
rects1_api = ax2.bar(x - width/2, api_xad, width, label='XAD', color='#2196F3', edgecolor='black')
rects2_api = ax2.bar(x + width/2, api_adept, width, label='Adept', color='#FF5722', edgecolor='black')

ax2.set_ylabel('Number of API calls', fontsize=12)
ax2.set_title('Metric B: library API calls comparison', fontsize=14)
ax2.set_xticks(x)
ax2.set_xticklabels(tasks, fontsize=12)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# Добавляем цифры над столбцами
ax2.bar_label(rects1_api, padding=3)
ax2.bar_label(rects2_api, padding=3)

# Отрисовка
plt.tight_layout()
plt.show()
