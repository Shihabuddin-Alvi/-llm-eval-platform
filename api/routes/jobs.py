from fastapi import APIRouter
from core.models import EvalJob
from core.runner import run_eval

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("")
def submit_job(job: EvalJob):
    result = run_eval(job)
    return result

@router.get("")
def list_jobs():
    return []
