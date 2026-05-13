from fastapi import APIRouter
from core.models import EvalJob
from core.runner import run_eval, get_db_connection

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("")
def submit_job(job: EvalJob):
    result = run_eval(job)
    return result

@router.get("")
def list_jobs():
    return []
@router.get("/leaderboard")
def get_leaderboard():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            model_name,
            COUNT(*) as total_runs,
            ROUND(AVG(score), 3) as avg_score,
            ROUND(SUM(passed) * 100.0 / COUNT(*), 1) as pass_rate
        FROM jobs
        WHERE model_name IS NOT NULL AND model_name != ''
        GROUP BY model_name
        ORDER BY avg_score DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]