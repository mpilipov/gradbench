import json
from statistics import mean

filename = "run/gmm/adept.jsonl"

total_times = []
evaluations = 0

with open(filename, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)

        # Новый формат: ищем объекты с ключом "response"
        if "response" in data:
            resp = data["response"]

            # Некоторые строки только подтверждают команду, без timings
            if "timings" in resp:
                # Суммируем nanoseconds из всех стадий выполнения
                total_ns = sum(t["nanoseconds"] for t in resp["timings"])
                total_times.append(total_ns / 1e9)  # в секунды
                evaluations += 1

print(f"The number of recordings: {evaluations}")
if total_times:
    print(f"Average time (s): {mean(total_times):.6f}")
    print(f"Maximum (s): {max(total_times):.6f}")
    print(f"Minimum (s): {min(total_times):.6f}")
else:
    print("error")
