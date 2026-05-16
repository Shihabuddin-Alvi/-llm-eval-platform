"""
Criterion — Advanced Live API Test Suite
Runs against https://criterion-api-c7mf.onrender.com
Usage: python criterion_tests_v2.py
"""

import httpx
import asyncio
import time
import json

BASE_URL = "https://criterion-api-c7mf.onrender.com"
TIMEOUT = 60

passed = 0
failed = 0
results = []

def log(test_name, success, detail=""):
    global passed, failed
    status = "PASS" if success else "FAIL"
    if success:
        passed += 1
    else:
        failed += 1
    results.append((test_name, status, detail))
    mark = "✓" if success else "✗"
    print(f"  [{status}] {mark} {test_name}")
    if detail:
        print(f"         {detail}")

def run_job(payload, timeout=TIMEOUT):
    r = httpx.post(f"{BASE_URL}/jobs", json=payload, timeout=timeout)
    return r

print("\n" + "="*60)
print("  CRITERION — Advanced Live API Test Suite v2")
print(f"  Target: {BASE_URL}")
print("="*60 + "\n")

# ── HEALTH ────────────────────────────────────────────────────
print("[ Health ]")
try:
    r = httpx.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    log("API is live", r.status_code == 200, r.json())
except Exception as e:
    log("API is live", False, str(e))

# ── GRADER EDGE CASES ─────────────────────────────────────────
print("\n[ Grader Edge Cases ]")

# Unicode
try:
    r = run_job({"input": "Q", "prediction": "café", "reference": "café",
                 "grader_name": "exact_match", "model_name": "edge-test"})
    score = r.json().get("score")
    log("exact_match handles unicode characters (café)", score == 1.0, f"score={score}")
except Exception as e:
    log("exact_match handles unicode characters (café)", False, str(e))

# Unicode mismatch
try:
    r = run_job({"input": "Q", "prediction": "cafe", "reference": "café",
                 "grader_name": "exact_match", "model_name": "edge-test"})
    score = r.json().get("score")
    log("exact_match distinguishes café vs cafe", score == 0.0, f"score={score}")
except Exception as e:
    log("exact_match distinguishes café vs cafe", False, str(e))

# Very long prediction
try:
    long_text = "Paris " * 2000  # ~12,000 characters
    r = run_job({"input": "Q", "prediction": long_text, "reference": "Paris",
                 "grader_name": "contains_match", "model_name": "edge-test"})
    score = r.json().get("score")
    log("contains_match handles 12,000 char prediction", score == 1.0, f"score={score}")
except Exception as e:
    log("contains_match handles 12,000 char prediction", False, str(e))

# Invalid regex pattern
try:
    r = run_job({"input": "Q", "prediction": "hello", "reference": "[invalid(regex",
                 "grader_name": "regex_match", "model_name": "edge-test"})
    status = r.status_code
    log("regex_match with invalid pattern returns clean error not 500",
        status in [400, 422, 200], f"status={status} body={r.text[:100]}")
except Exception as e:
    log("regex_match with invalid pattern returns clean error not 500", False, str(e))

# Newlines in prediction
try:
    r = run_job({"input": "Q", "prediction": "The answer\nis Paris\n",
                 "reference": "Paris", "grader_name": "contains_match",
                 "model_name": "edge-test"})
    score = r.json().get("score")
    log("contains_match handles newlines in prediction", score == 1.0, f"score={score}")
except Exception as e:
    log("contains_match handles newlines in prediction", False, str(e))

# Both empty
try:
    r = run_job({"input": "", "prediction": "", "reference": "",
                 "grader_name": "exact_match", "model_name": "edge-test"})
    score = r.json().get("score")
    log("exact_match with both empty strings returns 1.0", score == 1.0, f"score={score}")
except Exception as e:
    log("exact_match with both empty strings returns 1.0", False, str(e))

# Special characters
try:
    r = run_job({"input": "Q", "prediction": "score: 95%", "reference": r"\d+%",
                 "grader_name": "regex_match", "model_name": "edge-test"})
    score = r.json().get("score")
    log("regex_match handles percentage pattern", score == 1.0, f"score={score}")
except Exception as e:
    log("regex_match handles percentage pattern", False, str(e))

# ── DATA INTEGRITY ────────────────────────────────────────────
print("\n[ Data Integrity ]")

try:
    payload = {
        "input": "integrity-test-input",
        "prediction": "integrity-test-prediction",
        "reference": "integrity-test-prediction",
        "grader_name": "exact_match",
        "model_name": "integrity-model"
    }
    r = run_job(payload)
    data = r.json()
    job_id = data.get("id") or data.get("job_id")

    if job_id:
        r2 = httpx.get(f"{BASE_URL}/jobs/{job_id}", timeout=TIMEOUT)
        stored = r2.json()
        match = (
            stored.get("prediction") == payload["prediction"] and
            stored.get("reference") == payload["reference"] and
            stored.get("model_name") == payload["model_name"]
        )
        log("stored job matches submitted payload exactly", match,
            f"id={job_id} prediction={stored.get('prediction')[:20]}")
    else:
        log("stored job matches submitted payload exactly", False,
            f"no job_id in response: {data}")
except Exception as e:
    log("stored job matches submitted payload exactly", False, str(e))

# ── LEADERBOARD MATH ──────────────────────────────────────────
print("\n[ Leaderboard Math ]")

try:
    model = "math-verify-model"
    # 3 passes, 1 fail = 75% pass rate, avg_score = 0.75
    for pred, ref in [("Paris", "Paris"), ("Paris", "Paris"), ("Paris", "Paris"), ("London", "Paris")]:
        run_job({"input": "Q", "prediction": pred, "reference": ref,
                 "grader_name": "exact_match", "model_name": model})

    r = httpx.get(f"{BASE_URL}/jobs/leaderboard", timeout=TIMEOUT)
    board = r.json()
    model_row = next((m for m in board if m["model_name"] == model), None)

    if model_row:
        pass_rate = model_row.get("pass_rate")
        avg_score = model_row.get("avg_score")
        log("leaderboard pass_rate is exactly 75.0 for 3/4 passing",
            pass_rate == 75.0, f"pass_rate={pass_rate}")
        log("leaderboard avg_score is exactly 0.75 for 3/4 passing",
            avg_score == 0.75, f"avg_score={avg_score}")
    else:
        log("leaderboard pass_rate is exactly 75.0", False, f"model not found in board")
        log("leaderboard avg_score is exactly 0.75", False, "model not found in board")
except Exception as e:
    log("leaderboard math tests", False, str(e))

# ── CLUSTERING BOUNDARY ───────────────────────────────────────
print("\n[ Clustering Boundary Cases ]")

# Single text
try:
    r = httpx.post(f"{BASE_URL}/jobs/failures/cluster",
                   json=["only one text here"], timeout=TIMEOUT)
    log("cluster endpoint handles single text without crashing",
        r.status_code == 200, f"status={r.status_code} body={r.text[:80]}")
except Exception as e:
    log("cluster endpoint handles single text without crashing", False, str(e))

# Request more clusters than texts
try:
    r = httpx.post(f"{BASE_URL}/jobs/failures/cluster?n_clusters=10",
                   json=["text one", "text two"], timeout=TIMEOUT)
    log("cluster endpoint caps n_clusters to len(texts) gracefully",
        r.status_code == 200, f"status={r.status_code}")
except Exception as e:
    log("cluster endpoint caps n_clusters to len(texts) gracefully", False, str(e))

# ── MALFORMED INPUT ───────────────────────────────────────────
print("\n[ Malformed Input Handling ]")

# Missing required field
try:
    r = httpx.post(f"{BASE_URL}/jobs",
                   json={"prediction": "Paris", "reference": "Paris"},
                   timeout=TIMEOUT)
    log("missing required field returns 422 not 500",
        r.status_code == 422, f"status={r.status_code}")
except Exception as e:
    log("missing required field returns 422 not 500", False, str(e))

# Empty JSON body
try:
    r = httpx.post(f"{BASE_URL}/jobs", json={}, timeout=TIMEOUT)
    log("empty JSON body returns 422 not 500",
        r.status_code == 422, f"status={r.status_code}")
except Exception as e:
    log("empty JSON body returns 422 not 500", False, str(e))

# Wrong type for score field
try:
    r = httpx.post(f"{BASE_URL}/jobs",
                   json={"input": 123, "prediction": "Paris",
                         "reference": "Paris", "grader_name": "exact_match"},
                   timeout=TIMEOUT)
    log("integer input field is accepted or returns 422 cleanly",
        r.status_code in [200, 422], f"status={r.status_code}")
except Exception as e:
    log("integer input field is accepted or returns 422 cleanly", False, str(e))

# Non-existent grader name
try:
    r = run_job({"input": "Q", "prediction": "Paris", "reference": "Paris",
                 "grader_name": "fake_grader", "model_name": "test"})
    data = r.json()
    handled = r.status_code in [200, 400, 422] and "Grader not found" in str(data.get("reasoning", ""))
    log("unknown grader name handled gracefully with clear message",
        handled, f"status={r.status_code} reasoning={data.get('reasoning')}")
except Exception as e:
    log("unknown grader name handled gracefully with clear message", False, str(e))

# ── CONCURRENCY ───────────────────────────────────────────────
print("\n[ Concurrency ]")

async def fire_concurrent_jobs(n=10):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        tasks = [
            client.post(f"{BASE_URL}/jobs", json={
                "input": f"concurrent-Q-{i}",
                "prediction": "Paris",
                "reference": "Paris",
                "grader_name": "exact_match",
                "model_name": "concurrency-test"
            })
            for i in range(n)
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

try:
    start = time.time()
    responses = asyncio.run(fire_concurrent_jobs(10))
    elapsed = round(time.time() - start, 2)

    successful = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
    log(f"10 concurrent POST /jobs all return 200",
        len(successful) == 10, f"{len(successful)}/10 succeeded in {elapsed}s")

    scores = [r.json().get("score") for r in successful if not isinstance(r, Exception)]
    all_correct = all(s == 1.0 for s in scores)
    log("concurrent jobs all return correct scores with no corruption",
        all_correct, f"scores: {set(scores)}")
except Exception as e:
    log("10 concurrent POST /jobs all return 200", False, str(e))
    log("concurrent jobs return correct scores with no corruption", False, str(e))

# ── BATCH PERFORMANCE ─────────────────────────────────────────
print("\n[ Batch Performance ]")

try:
    batch_50 = [
        {"input": f"Q{i}", "prediction": "Paris", "reference": "Paris",
         "grader_name": "exact_match", "model_name": "perf-test"}
        for i in range(50)
    ]
    start = time.time()
    r = httpx.post(f"{BASE_URL}/jobs/batch", json=batch_50, timeout=120)
    elapsed = round(time.time() - start, 2)
    data = r.json()
    log("POST /jobs/batch handles 50 jobs",
        len(data) == 50, f"returned {len(data)} results in {elapsed}s")
    log("50 batch jobs complete in under 30 seconds",
        elapsed < 30, f"elapsed={elapsed}s")
except Exception as e:
    log("batch performance tests", False, str(e))

# ── SUMMARY ───────────────────────────────────────────────────
total = passed + failed
print("\n" + "="*60)
print(f"  RESULTS: {passed}/{total} passed  |  {failed} failed")
print(f"  Pass rate: {round(passed/total*100, 1)}%")
print("="*60)

print("\n  Full breakdown:")
for name, status, detail in results:
    mark = "✓" if status == "PASS" else "✗"
    print(f"  {mark} [{status}] {name}")
