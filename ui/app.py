import streamlit as st
import httpx

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Criterion", layout="wide")
st.sidebar.title("Criterion")
page = st.sidebar.radio("Navigate", ["Submit Eval", "History", "Leaderboard"])

if page == "Submit Eval":
    st.title("Submit Eval")
    input_text = st.text_input("Input")
    prediction = st.text_input("Prediction")
    reference = st.text_input("Reference")
    grader = st.selectbox("Grader", ["exact_match", "contains_match", "regex_match", "llm_judge"])
    model_name = st.text_input("Model name (optional)")

    if st.button("Run Eval"):
        payload = {
            "input": input_text,
            "prediction": prediction,
            "reference": reference,
            "grader_name": grader,
            "model_name": model_name or None
        }
        res = httpx.post(f"{API_URL}/jobs", json=payload)
        data = res.json()
        if data["passed"]:
            st.success(f"PASSED — Score: {data['score']}")
        else:
            st.error(f"FAILED — Score: {data['score']}")
        if data.get("reasoning"):
            st.info(f"Reasoning: {data['reasoning']}")

elif page == "History":
    st.title("Eval History")
    res = httpx.get(f"{API_URL}/history")
    st.dataframe(res.json())

elif page == "Leaderboard":
    st.title("Model Leaderboard")
    res = httpx.get(f"{API_URL}/jobs/leaderboard")
    st.dataframe(res.json())
