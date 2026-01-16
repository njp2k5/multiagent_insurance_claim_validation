def calculate_validation_score(texts: list[str]) -> float:
    score = 0.0
    keywords = ["policy", "insurance", "aadhaar", "claim", "government"]

    for t in texts:
        for k in keywords:
            if k in t.lower():
                score += 0.1

    return min(score, 1.0)
