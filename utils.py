def estimate_cost(model: str) -> float:
    # Fake but consistent for project
    if "8b" in model:
        return 0.001
    else:
        return 0.01