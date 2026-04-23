def compute_confidence(query: str) -> float:
    q = query.lower()
    score = 0.5

    if any(k in q for k in ["what is", "define", "who is"]):
        score += 0.3

    if any(k in q for k in ["explain", "why", "compare", "analyze"]):
        score -= 0.3

    if len(q.split()) > 20:
        score -= 0.2

    return max(0, min(1, score))


def route_query(query: str):
    conf = compute_confidence(query)

    if conf >= 0.6:
        return {
            "type": "cheap",
            "model": "llama-3.1-8b-instant",   # ✅ ADD THIS
            "reason": f"High confidence ({conf:.2f}) → cheap model"
        }
    else:
        return {
            "type": "expensive",
           "model" : "llama-3.3-70b-versatile",  # ✅ ADD THIS
            "reason": f"Low confidence ({conf:.2f}) → powerful model"
        }