import random

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


def generate_workload(size=4, repeat_ratio=0.0):
    unique_count = max(1, int(size * (1 - repeat_ratio)))
    duplicate_count = size - unique_count

    queries = []

    for i in range(unique_count):
        q = random.choice(BASE_QUERIES)
        queries.append(f"{q} (variation {i})")

    for i in range(duplicate_count):
        queries.append(random.choice(queries))

    return queries



def generate_all_workloads(size=4):
    return {
        "W1_0%": generate_workload(size, 0.0),
        "W2_25%": generate_workload(size, 0.25),
        "W3_50%": generate_workload(size, 0.5),
        "W4_75%": generate_workload(size, 0.75),
    }


if __name__ == "__main__":
    workloads = generate_all_workloads(size=4)

    for name, data in workloads.items():
        print(f"\n{name} SAMPLE:")
        print(data)
