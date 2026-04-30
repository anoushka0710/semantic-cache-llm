from fastapi import FastAPI
import time

from router import route_query
from llm import call_llm
from utils import estimate_cost
from cache import get_cached_response, init_cache, save_cached_response

app = FastAPI()
init_cache()


@app.post("/route")
def route(data: dict, nocache: bool = False):
    query = data.get("query", "")

    if not query:
        return {"error": "Query is required"}

    start = time.time()
    use_cache = not nocache and not data.get("nocache", False)

    if use_cache:
        cached_response = get_cached_response(query)
        if cached_response:
            latency = round(time.time() - start, 3)
            print(f"[CACHE HIT] latency={latency}s | query={query}")
            return {
                "query": query,
                "response": cached_response,
                "model": "cache",
                "reason": "Cache hit -> reused stored response",
                "latency": latency,
                "cost": 0,
                "cache_hit": True,
                "cache_status": "HIT"
            }

    # 1. Decide model
    decision = route_query(query)
    model = decision["model"]
    reason = decision["reason"]

    # 2. Call LLM
    response = call_llm(query, model)
    if use_cache:
        save_cached_response(query, response)

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
        "cost": cost,
        "cache_hit": False,
        "cache_status": "MISS" if use_cache else "DISABLED"
    }
