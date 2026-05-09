from fastapi import FastAPI

app = FastAPI(
    title="LLM Eval Platform",
    description="REST API for evaluating LLM outputs.",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

