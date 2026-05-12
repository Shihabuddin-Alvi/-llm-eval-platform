from core.models import EvalJob
from core.graders import exact_match, contains_match, regex_match, llm_judge

GRADERS = {
    "exact_match": exact_match,
    "contains_match": contains_match,
    "regex_match": regex_match,
    "llm_judge": llm_judge,
}

def run_eval(job: EvalJob) -> dict:
    grader_fn = GRADERS.get(job.grader_name)
    if grader_fn is None:
        return {"score": 0.0, "passed": False, "grader": job.grader_name, "reasoning": "Grader not found"}
    return grader_fn(job.prediction, job.reference)
