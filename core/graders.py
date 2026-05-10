def exact_match(prediction: str, reference: str) -> dict:
    prediction_clean = prediction.strip().lower()
    reference_clean = reference.strip().lower()
    passed = prediction_clean == reference_clean

    return {
        "grader": "exact_match",
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "prediction": prediction,
        "reference": reference,
    }
