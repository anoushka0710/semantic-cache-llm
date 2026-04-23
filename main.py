from fastapi import FastAPI
import time

from router import route_query
from llm import call_llm
from utils import estimate_cost

app = FastAPI()


@app.post("/route")
def route(data: dict):
    query = data.get("query", "")

    if not query:
        return {"error": "Query is required"}

    start = time.time()

    # 1. Decide model
    decision = route_query(query)
    model = decision["model"]
    reason = decision["reason"]

    # 2. Call LLM
    response = call_llm(query, model)

    # 3. Metrics
    latency = round(time.time() - start, 3)
    cost = estimate_cost(model)

    # logging
    print(f"[ROUTE] model={model} | latency={latency}s | query={query}")


    return {
        "query": query,
        "response": response,
        "model": model,
        "reason": reason,
        "latency": latency,
        "cost": cost
    }