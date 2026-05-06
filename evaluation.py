import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

from workload import generate_workload
from cache import set_similarity_threshold

API_URL = "http://127.0.0.1:8000/route"

CHEAP_COST = 0.001
EXPENSIVE_COST = 0.01


def run_test(repeat_ratio, size=4, threshold=0.55):
    set_similarity_threshold(threshold)
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

    hit_rate = hits / len(queries) if len(queries) > 0 else 0
    avg_latency = total_time / len(queries) if len(queries) > 0 else 0

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

    avg_latency = total_time / len(queries) if len(queries) > 0 else 0

    return avg_latency, total_cost


def run_evaluation(size=4):
    # Repetition Analysis
    ratios = [0.0, 0.25, 0.5, 0.75]
    rows = []

    for r in ratios:
        hit, latency_cache, cost_cache, fp = run_test(r, size=size, threshold=0.55)
        latency_no_cache, cost_no_cache = run_without_cache(r, size=size)

        rows.append({
            "Repetition Rate": r,
            "Hit Rate": hit,
            "Latency With Cache": latency_cache,
            "Latency Without Cache": latency_no_cache,
            "Cost With Cache": cost_cache,
            "Cost Without Cache": cost_no_cache,
            "Cost Savings": cost_no_cache - cost_cache,
            "False Positives": fp,
        })

    return pd.DataFrame(rows)


def create_graphs(repetition_df):
    figures = {}

    # 1. Cache Hit Rate at threshold 0.55 vs Repetition Rate
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(repetition_df["Repetition Rate"], repetition_df["Hit Rate"], marker="o", linewidth=2.5, color="#9333ea", markersize=8)
    ax1.set_xlabel("Repetition Rate", fontsize=11)
    ax1.set_ylabel("Hit Rate", fontsize=11)
    ax1.set_title("Cache Hit Rate @ Threshold 0.55", fontsize=13, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    figures["1. Hit Rate at 0.55"] = fig1

    # 2. Cost Savings vs Repetition Rate
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(repetition_df["Repetition Rate"], repetition_df["Cost Savings"], marker="o", linewidth=2.5, color="#16a34a", markersize=8)
    ax2.set_xlabel("Repetition Rate", fontsize=11)
    ax2.set_ylabel("Cost Savings ($)", fontsize=11)
    ax2.set_title("Cost Savings vs Repetition Rate", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3)
    figures["2. Cost Savings vs Repetition"] = fig2

    # 3. False Positives at threshold 0.55 vs Repetition Rate
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    ax3.plot(repetition_df["Repetition Rate"], repetition_df["False Positives"], marker="o", linewidth=2.5, color="#dc2626", markersize=8)
    ax3.set_xlabel("Repetition Rate", fontsize=11)
    ax3.set_ylabel("False Positives", fontsize=11)
    ax3.set_title("False Positives @ Threshold 0.55", fontsize=13, fontweight="bold")
    ax3.grid(True, alpha=0.3)
    figures["3. False Positives at 0.55"] = fig3

    # 4. Average Latency (with cache) vs Repetition Rate
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    ax4.plot(repetition_df["Repetition Rate"], repetition_df["Latency With Cache"], marker="o", linewidth=2.5, color="#0f766e", markersize=8)
    ax4.set_xlabel("Repetition Rate", fontsize=11)
    ax4.set_ylabel("Average Latency (s)", fontsize=11)
    ax4.set_title("Average Latency vs Repetition Rate (With Cache)", fontsize=13, fontweight="bold")
    ax4.grid(True, alpha=0.3)
    figures["4. Latency vs Repetition"] = fig4

    return figures


if __name__ == "__main__":
    repetition_df = run_evaluation(size=4)
    print("Repetition Results:")
    print(repetition_df)
    graphs = create_graphs(repetition_df)
    for title, fig in graphs.items():
        fig.show()

