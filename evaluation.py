import time
import requests
import matplotlib.pyplot as plt
from workload import generate_workload

API_URL = "http://127.0.0.1:8000/route"

CHEAP_COST = 0.001
EXPENSIVE_COST = 0.01


def run_test(repeat_ratio):
    queries = generate_workload(repeat_ratio=repeat_ratio)

    hits = 0
    total_time = 0
    total_cost = 0
    false_positives = 0

    seen_queries = set()

    for q in queries:
        start = time.time()

        response = requests.post(API_URL, json={"query": q})
        data = response.json()

        latency = time.time() - start
        total_time += latency

        model_used = data["model"]

        # Cache hit
        if model_used == "cache":
            hits += 1

            # False positive detection
            if q not in seen_queries:
                false_positives += 1

        else:
            # Cost tracking
            if "8b" in model_used:
                total_cost += CHEAP_COST
            else:
                total_cost += EXPENSIVE_COST

        seen_queries.add(q)

    hit_rate = hits / len(queries)
    avg_latency = total_time / len(queries)

    return hit_rate, avg_latency, total_cost, false_positives


def run_without_cache(repeat_ratio):
    queries = generate_workload(repeat_ratio=repeat_ratio)

    total_time = 0
    total_cost = 0

    for q in queries:
        start = time.time()

        response = requests.post(API_URL + "?nocache=true", json={"query": q})
        data = response.json()

        latency = time.time() - start
        total_time += latency

        model_used = data["model"]

        if "8b" in model_used:
            total_cost += CHEAP_COST
        else:
            total_cost += EXPENSIVE_COST

    avg_latency = total_time / len(queries)

    return avg_latency, total_cost


def run_all_tests():
    ratios = [0.0, 0.25, 0.5, 0.75]

    hit_rates = []
    latencies = []
    costs = []
    false_pos = []
    cost_no_cache = []

    for r in ratios:
        print(f"\nRepetition: {r*100}%")

        hit, latency, cost, fp = run_test(r)
        lat_nc, cost_nc = run_without_cache(r)

        hit_rates.append(hit)
        latencies.append(latency)
        costs.append(cost)
        false_pos.append(fp)
        cost_no_cache.append(cost_nc)

        print(f"Hit Rate: {hit}")
        print(f"Latency (cache): {latency}")
        print(f"Latency (no cache): {lat_nc}")
        print(f"Cost (cache): ${cost}")
        print(f"Cost (no cache): ${cost_nc}")
        print(f"False Positives: {fp}")

    # 📈 Hit Rate vs Repetition
    plt.figure()
    plt.plot(ratios, hit_rates)
    plt.xlabel("Repetition Rate")
    plt.ylabel("Hit Rate")
    plt.title("Hit Rate vs Repetition")
    plt.show()

    # 📈 Latency vs Repetition
    plt.figure()
    plt.plot(ratios, latencies, label="With Cache")
    plt.xlabel("Repetition Rate")
    plt.ylabel("Latency")
    plt.title("Latency vs Repetition")
    plt.legend()
    plt.show()

    # 📈 Cost vs Repetition
    plt.figure()
    plt.plot(ratios, costs, label="With Cache")
    plt.plot(ratios, cost_no_cache, label="Without Cache")
    plt.xlabel("Repetition Rate")
    plt.ylabel("Cost")
    plt.title("Cost vs Repetition")
    plt.legend()
    plt.show()

    # 📈 False Positives
    plt.figure()
    plt.plot(ratios, false_pos)
    plt.xlabel("Repetition Rate")
    plt.ylabel("False Positives")
    plt.title("False Positives vs Repetition")
    plt.show()


def threshold_experiment():
    thresholds = [0.85, 0.90, 0.95]
    hit_rates = []

    for t in thresholds:
        print(f"\nTesting threshold: {t}")

        # IMPORTANT: backend must use this threshold manually
        hit, _, _, _ = run_test(0.5)  # fixed repetition
        hit_rates.append(hit)

    plt.figure()
    plt.plot(thresholds, hit_rates)
    plt.xlabel("Threshold")
    plt.ylabel("Hit Rate")
    plt.title("Hit Rate vs Threshold")
    plt.show()


if __name__ == "__main__":
    run_all_tests()
    threshold_experiment()