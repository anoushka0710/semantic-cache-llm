import time
from difflib import SequenceMatcher

import matplotlib.pyplot as plt
import pandas as pd
import requests

from cache import semantic_similarity
from router import route_query
from utils import estimate_cost
from workload import generate_workload


API_URL = "http://127.0.0.1:8000/route"
CHEAP_CACHE_LATENCY = 0.01
CHEAP_MODEL_LATENCY = 0.35
EXPENSIVE_MODEL_LATENCY = 0.85
THRESHOLDS = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def _run_with_cache(repeat_ratio, size=4):
    queries = generate_workload(size=size, repeat_ratio=repeat_ratio)

    hits = 0
    total_time = 0.0
    total_cost = 0.0
    false_positives = 0
    seen_queries = set()

    for query in queries:
        start = time.time()

        response = requests.post(API_URL, json={"query": query})
        data = response.json()

        latency = time.time() - start
        total_time += latency

        model_used = data["model"]

        if model_used == "cache":
            hits += 1
            if query not in seen_queries:
                false_positives += 1
        else:
            total_cost += estimate_cost(model_used)

        seen_queries.add(query)

    hit_rate = hits / len(queries)
    avg_latency = total_time / len(queries)
    return hit_rate, avg_latency, total_cost, false_positives


def _run_without_cache(repeat_ratio, size=4):
    queries = generate_workload(size=size, repeat_ratio=repeat_ratio)

    total_time = 0.0
    total_cost = 0.0

    for query in queries:
        start = time.time()

        response = requests.post(API_URL + "?nocache=true", json={"query": query})
        data = response.json()

        latency = time.time() - start
        total_time += latency

        total_cost += estimate_cost(data["model"])

    avg_latency = total_time / len(queries)
    return avg_latency, total_cost


def run_repetition_evaluation(size=4):
    ratios = [0.0, 0.25, 0.5, 0.75]
    rows = []

    for ratio in ratios:
        hit_rate, latency_with_cache, cost_with_cache, false_positives = _run_with_cache(
            ratio, size=size
        )
        latency_without_cache, cost_without_cache = _run_without_cache(ratio, size=size)

        rows.append(
            {
                "Repetition Rate": ratio,
                "Hit Rate": hit_rate,
                "Latency With Cache": latency_with_cache,
                "Latency Without Cache": latency_without_cache,
                "Average Latency": latency_with_cache,
                "Cost With Cache": cost_with_cache,
                "Cost Without Cache": cost_without_cache,
                "Cost Savings": cost_without_cache - cost_with_cache,
                "False Positives": false_positives,
            }
        )

    return pd.DataFrame(rows)


def _extract_topic(question: str) -> str:
    topic = question.lower().strip()
    topic = topic.replace("what's", "what is")
    topic = topic.replace("whats", "what is")
    topic = topic.replace("tell me about", "")
    topic = topic.replace("define", "")
    topic = topic.replace("explain", "")
    topic = topic.replace("what is meant by", "")
    topic = topic.replace("what does", "")
    topic = topic.replace("mean", "")
    topic = topic.replace("?") if False else topic
    topic = " ".join(topic.split())
    return topic.strip(" ?!.,:;")


def _build_threshold_workload():
    topics = [
        "LLM",
        "DSA",
        "machine learning",
        "deep learning",
        "semantic caching",
        "vector database",
        "transformers",
        "attention mechanism",
        "prompt engineering",
        "RAG",
    ]

    workload = []
    for topic in topics:
        label = topic.lower()
        workload.extend(
            [
                {"query": f"What is {topic}?", "label": label},
                {"query": f"What does {topic} mean?", "label": label},
                {"query": f"What is meant by {topic}?", "label": label},
                {"query": f"Define {topic}", "label": label},
                {"query": f"Tell me about {topic}", "label": label},
            ]
        )

    return workload


def _simulate_threshold_run(queries, threshold):
    cache_entries = []
    hits = 0
    false_positives = 0
    total_cost = 0.0
    total_latency = 0.0
    baseline_cost = 0.0

    for item in queries:
        query = item["query"]
        label = item["label"]

        decision = route_query(query)
        baseline_cost += estimate_cost(decision["model"])

        best_match = None
        best_score = 0.0

        for entry in cache_entries:
            score = semantic_similarity(query, entry["query"])
            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score >= threshold:
            hits += 1
            total_latency += CHEAP_CACHE_LATENCY
            if best_match["label"] != label:
                false_positives += 1
        else:
            cache_entries.append({"query": query, "label": label})
            total_cost += estimate_cost(decision["model"])
            total_latency += CHEAP_MODEL_LATENCY if decision["type"] == "cheap" else EXPENSIVE_MODEL_LATENCY

    total_queries = len(queries)
    return {
        "Similarity Threshold": threshold,
        "Cache Hit Rate": hits / total_queries,
        "False Positive Rate": false_positives / total_queries,
        "Average Latency": total_latency / total_queries,
        "Cost Savings": baseline_cost - total_cost,
    }


def run_threshold_evaluation():
    queries = _build_threshold_workload()
    rows = [_simulate_threshold_run(queries, threshold) for threshold in THRESHOLDS]
    return pd.DataFrame(rows)


def _style_axis(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)


def create_graphs(repetition_df, threshold_df):
    figures = []

    fig1, ax1 = plt.subplots(figsize=(8, 4), dpi=120)
    ax1.plot(
        threshold_df["Similarity Threshold"],
        threshold_df["Cache Hit Rate"],
        marker="o",
        linewidth=2.5,
        color="#2563eb",
    )
    _style_axis(
        ax1,
        "Similarity Threshold",
        "Cache Hit Rate",
        "Cache Hit Rate vs Similarity Threshold",
    )
    figures.append(("Cache Hit Rate vs Similarity Threshold", fig1))

    fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=120)
    ax2.plot(
        repetition_df["Repetition Rate"],
        repetition_df["Cost Savings"],
        marker="o",
        linewidth=2.5,
        color="#16a34a",
    )
    _style_axis(
        ax2,
        "Repetition Rate",
        "Cost Savings",
        "Cost Savings vs Repetition Rate",
    )
    figures.append(("Cost Savings vs Repetition Rate", fig2))

    fig3, ax3 = plt.subplots(figsize=(8, 4), dpi=120)
    ax3.plot(
        threshold_df["Similarity Threshold"],
        threshold_df["False Positive Rate"],
        marker="o",
        linewidth=2.5,
        color="#dc2626",
    )
    _style_axis(
        ax3,
        "Similarity Threshold",
        "False Positive Rate",
        "False Positive Rate vs Threshold",
    )
    figures.append(("False Positive Rate vs Threshold", fig3))

    fig4, ax4 = plt.subplots(figsize=(8, 4), dpi=120)
    ax4.plot(
        repetition_df["Repetition Rate"],
        repetition_df["Average Latency"],
        marker="o",
        linewidth=2.5,
        color="#7c3aed",
    )
    _style_axis(
        ax4,
        "Repetition Rate",
        "Average Latency (seconds)",
        "Average Latency vs Repetition Rate",
    )
    figures.append(("Average Latency vs Repetition Rate", fig4))

    return figures


def run_evaluation(size=4):
    repetition_df = run_repetition_evaluation(size=size)
    threshold_df = run_threshold_evaluation()
    return repetition_df, threshold_df


if __name__ == "__main__":
    repetition_results, threshold_results = run_evaluation(size=4)
    print(repetition_results)
    print(threshold_results)

    for title, fig in create_graphs(repetition_results, threshold_results):
        fig.show()
