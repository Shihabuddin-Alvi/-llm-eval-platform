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
def contains_match(prediction: str, reference: str) -> dict:
    prediction_clean = prediction.strip().lower()
    reference_clean = reference.strip().lower()
    passed = reference_clean in prediction_clean

    return {
        "grader": "contains_match",
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "prediction": prediction,
        "reference": reference,
    }


import re

def regex_match(prediction: str, pattern: str) -> dict:
    passed = bool(re.search(pattern, prediction, re.IGNORECASE))

    return {
        "grader": "regex_match",
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "prediction": prediction,
        "reference": pattern,
    }
