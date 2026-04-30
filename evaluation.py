import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

from workload import generate_workload

API_URL = "http://127.0.0.1:8000/route"

CHEAP_COST = 0.001
EXPENSIVE_COST = 0.01


def run_test(repeat_ratio, size=4):
    queries = generate_workload(size=size, repeat_ratio=repeat_ratio)

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

        if model_used == "cache":
            hits += 1

            if q not in seen_queries:
                false_positives += 1
        else:
            if "8b" in model_used:
                total_cost += CHEAP_COST
            else:
                total_cost += EXPENSIVE_COST

        seen_queries.add(q)

    hit_rate = hits / len(queries)
    avg_latency = total_time / len(queries)

    return hit_rate, avg_latency, total_cost, false_positives


def run_without_cache(repeat_ratio, size=4):
    queries = generate_workload(size=size, repeat_ratio=repeat_ratio)

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


def run_evaluation(size=4):
    ratios = [0.0,0.25, 0.5,0.75]

    rows = []

    for r in ratios:
        hit, latency_cache, cost_cache, fp = run_test(r, size=size)
        latency_no_cache, cost_no_cache = run_without_cache(r, size=size)

        rows.append({
            "Repetition Rate": r,
            "Hit Rate": hit,
            "Latency With Cache": latency_cache,
            "Latency Without Cache": latency_no_cache,
            "Cost With Cache": cost_cache,
            "Cost Without Cache": cost_no_cache,
            "False Positives": fp,
        })

    return pd.DataFrame(rows)


def create_graphs(results_df):
    figures = {}

    fig1, ax1 = plt.subplots()
    ax1.plot(results_df["Repetition Rate"], results_df["Hit Rate"], marker="o")
    ax1.set_xlabel("Repetition Rate")
    ax1.set_ylabel("Hit Rate")
    ax1.set_title("Hit Rate vs Repetition")
    ax1.grid(True)
    figures["Hit Rate vs Repetition"] = fig1

    fig2, ax2 = plt.subplots()
    ax2.plot(results_df["Repetition Rate"], results_df["Latency With Cache"], marker="o", label="With Cache")
    ax2.plot(results_df["Repetition Rate"], results_df["Latency Without Cache"], marker="o", label="Without Cache")
    ax2.set_xlabel("Repetition Rate")
    ax2.set_ylabel("Average Latency")
    ax2.set_title("Latency vs Repetition")
    ax2.legend()
    ax2.grid(True)
    figures["Latency vs Repetition"] = fig2

    fig3, ax3 = plt.subplots()
    ax3.plot(results_df["Repetition Rate"], results_df["Cost With Cache"], marker="o", label="With Cache")
    ax3.plot(results_df["Repetition Rate"], results_df["Cost Without Cache"], marker="o", label="Without Cache")
    ax3.set_xlabel("Repetition Rate")
    ax3.set_ylabel("Cost")
    ax3.set_title("Cost vs Repetition")
    ax3.legend()
    ax3.grid(True)
    figures["Cost vs Repetition"] = fig3

    fig4, ax4 = plt.subplots()
    ax4.plot(results_df["Repetition Rate"], results_df["False Positives"], marker="o")
    ax4.set_xlabel("Repetition Rate")
    ax4.set_ylabel("False Positives")
    ax4.set_title("False Positives vs Repetition")
    ax4.grid(True)
    figures["False Positives vs Repetition"] = fig4

    return figures


if __name__ == "__main__":
    results = run_evaluation(size=4)
    print(results)

    graphs = create_graphs(results)

    for title, fig in graphs.items():
        fig.show()
