import random

# Base pool of tech-related queries
BASE_QUERIES = [
    "What is a large language model?",
    "Explain machine learning",
    "What is deep learning?",
    "What is artificial intelligence?",
    "Explain neural networks",
    "What is overfitting in ML?",
    "What is supervised learning?",
    "What is unsupervised learning?",
    "What is reinforcement learning?",
    "What is natural language processing?",
    "Explain transformers in AI",
    "What is GPT?",
    "What is ChatGPT?",
    "What is tokenization in NLP?",
    "What is an embedding?",
    "Explain cosine similarity",
    "What is a vector database?",
    "What is LangChain?",
    "What is prompt engineering?",
    "What is fine-tuning?",
    "What is RAG (retrieval augmented generation)?",
    "What is a chatbot?",
    "What is a neural network layer?",
    "What is backpropagation?",
    "What is gradient descent?",
    "What is a dataset?",
    "What is training vs testing data?",
    "What is model inference?",
    "What is a parameter in ML?",
    "What is a hyperparameter?",
    "What is accuracy in ML?",
    "What is precision and recall?",
    "What is F1 score?",
    "What is bias in ML?",
    "What is variance in ML?",
    "Explain bias-variance tradeoff",
    "What is an API?",
    "What is FastAPI?",
    "What is Streamlit?",
    "What is caching in AI systems?",
    "What is GPTCache?",
    "What is semantic search?",
    "What is cosine distance?",
    "What is latency?",
    "What is throughput?",
    "What is cloud computing?",
    "What is edge computing?",
    "What is a GPU?",
    "What is parallel processing?",
    "What is Python used for?"
]


def generate_workload(size=200, repeat_ratio=0.0):
    """
    Generates workload of tech queries with given repetition ratio
    """

    # Step 1: create base unique queries (expand from base pool)
    queries = []
    for i in range(size):
        q = random.choice(BASE_QUERIES)
        queries.append(f"{q} (variation {i})")  # ensures uniqueness

    # Step 2: introduce repetition
    num_duplicates = int(size * repeat_ratio)

    for i in range(num_duplicates):
        queries[i] = random.choice(queries[:50])  # duplicate from first 50

    return queries


# Optional: generate all 4 datasets at once
def generate_all_workloads():
    return {
        "W1_0%": generate_workload(200, 0.0),
        "W2_25%": generate_workload(200, 0.25),
        "W3_50%": generate_workload(200, 0.5),
        "W4_75%": generate_workload(200, 0.75),
    }


# Test run
if __name__ == "__main__":
    workloads = generate_all_workloads()

    for name, data in workloads.items():
        print(f"\n{name} SAMPLE:")
        print(data[:10])