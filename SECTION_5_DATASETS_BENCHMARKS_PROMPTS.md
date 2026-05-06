# Section 5: Dataset, Benchmarks, and Prompt Design

## 5.1 Dataset and Benchmark

**Type & Size**: Question-Answering (QA) benchmark with 50 unique queries covering AI/ML concepts (neural networks, NLP, embeddings, caching systems). Workloads are generated with controlled repetition ratios (0%, 25%, 50%, 75%) to simulate realistic usage patterns and measure cache performance across different saturation levels.

## 5.2 Data Preprocessing

**Embeddings & Similarity**: GPTCache's string-based embedding function (`to_embeddings`) vectorizes queries with exact-match evaluation and 0.90 similarity threshold. Responses are stored persistently using GPTCache's map-based manager in `gptcache_data/` directory for cache state recovery.

## 5.3 Prompt Engineering

**Approach**: Direct user queries without explicit system prompts. Confidence-based routing uses linguistic features: keywords (+0.3 for "what is", "define"), complexity indicators (-0.3 for "explain", "compare"), and length penalty (-0.2 for >20 tokens). Queries with confidence ≥ 0.6 route to Llama 3.1 8B (cheap), others to Llama 3.3 70B (expensive).

**Example**: "What is semantic caching?" → High confidence → Llama 3.1 8B model

## 5.4 Evaluation Metrics

**Hit Rate**: Defined as the ratio of cached responses retrieved to total queries executed. This metric directly measures cache effectiveness and benefits from higher repetition ratios, indicating potential cost savings.

**Latency Comparison**: Average response time is measured with and without caching enabled. The differential latency (`latency_no_cache - latency_with_cache`) demonstrates the speed improvement from semantic caching, particularly when hits occur.

**Cost Analysis**: Total cost is computed by multiplying model invocations by their respective costs ($0.001 for Llama 3.1 8B, $0.01 for Llama 3.3 70B). Cost reduction is calculated as a percentage improvement when cache is enabled versus disabled across identical workloads.

**False Positive Rate**: Tracks queries where the cache returned a hit despite the query not appearing in prior request history. This metric captures cases where semantic similarity matching retrieves responses for genuinely novel but semantically similar queries, indicating both potential benefits and risks of approximate caching.

**Metrics Justification**: These metrics directly align with the project's dual optimization objectives: hit rate and false positives measure cache quality, while latency and cost metrics quantify real-world benefits. Together, they provide comprehensive evaluation of both functional correctness (minimizing false positives) and practical utility (maximizing cost and latency improvements).

---
*Evaluation conducted against Groq API (Llama models) with repetition-controlled workloads to ensure reproducibility and systematic performance analysis across cache saturation conditions.*
- **Hit Rate**: Ratio of cached responses to total queries; measures cache effectiveness
- **Latency**: Average response time with and without caching; quantifies speed improvement
- **Cost**: Model invocation cost ($0.001 for 8B, $0.01 for 70B); measures financial benefit
- **False Positive Rate**: Cache hits for novel but semantically similar queries; ensures accuracy

These metrics evaluate both cache quality (hit rate, false positives) and practical benefit (latency, cost reduction) across controlled repetition patterns (0-75%).