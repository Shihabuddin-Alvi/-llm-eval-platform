from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api.routes import graders
from api.routes import jobs

app = FastAPI(
    title="LLM Eval Platform",
    description="REST API for evaluating LLM outputs.",
    version="0.1.0"
)

app.include_router(graders.router)
app.include_router(jobs.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}
