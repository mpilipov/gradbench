import re
import matplotlib.pyplot as plt

# log_data = """
#  [0] start gmm (xad)
#  [1] def   gmm                                 21.646 s ✓
#  [2] eval  gmm::objective  2_5_1000            1.491 s ~         0ms prepare,         0ms evaluate × 7552 ✓
#  [4] eval  gmm::jacobian   2_5_1000            1.178 s ~         0ms prepare,         0ms evaluate × 183 ✓
#  [6] eval  gmm::objective  2_10_1000           1.217 s ~         0ms prepare,         0ms evaluate × 3536 ✓
#  [8] eval  gmm::jacobian   2_10_1000           1.116 s ~         0ms prepare,        10ms evaluate × 94 ✓
# [84] eval  gmm::jacobian   64_25_1000        7:12.325   ~         0ms prepare,  6:40.404   evaluate ✓
# [96] eval  gmm::jacobian   64_50_1000         10.831 s ✗
# """
log_data = ""
filename="gradbench_results/gmm_adept_launch.txt"
try:
    with open(filename, 'r', encoding='utf-16') as f:
        log_data = f.read()
except UnicodeError:
    print("can't read as utf-16, try to read as UTF-8...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            log_data = f.read()
    except UnicodeDecodeError:
        print("Encoding error")
        exit()
except FileNotFoundError:
    print(f"File {filename} is not found")
    exit()



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

def parse_log(data):
    test_names = []
    execution_times = []

    # reg expression
    # 1. index [N]
    # 2. type (def or eval)
    # 3. test name
    # 4. time (can be a number or mm:ss.ms)
    regex_pattern = r'\[\s*\d+\]\s+(?:def|eval)\s+(.+?)\s+((?:\d+:)?\d+\.\d+)'

    lines = data.strip().split('\n')

    for line in lines:
        match = re.search(regex_pattern, line)
        if match:
            name_raw = match.group(1).strip()
            time_raw = match.group(2).strip()

            # remove extra spaces
            name_clean = " ".join(name_raw.split())

            try:
                seconds = parse_time_to_seconds(time_raw)

                test_names.append(name_clean)
                execution_times.append(seconds)
            except ValueError:
                continue

    return test_names, execution_times

def plot_chart(names, times):
    if not names:
        print("No data found")
        return

    plt.figure(figsize=(14, 8))

    # create bar chart
    bars = plt.bar(names, times, color='skyblue', edgecolor='navy')

    plt.ylabel('Execution time (s)', fontsize=12)
    plt.title('Tests performance', fontsize=16)

    # rotating axis X labels
    plt.xticks(rotation=45, ha='right', fontsize=8)

    # Add axis Y grid
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # test labels above the columns
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom', fontsize=8, rotation=90)

    # make indents
    plt.tight_layout()
    plt.show()

names, times = parse_log(log_data)
plot_chart(names, times)
