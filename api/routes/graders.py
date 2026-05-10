from fastapi import APIRouter
from pydantic import BaseModel
from core.graders import exact_match

router = APIRouter()

class GradeRequest(BaseModel):
    prediction: str
    reference: str

@router.post("/grade/exact-match")
def grade_exact_match(request: GradeRequest):
    return exact_match(request.prediction, request.reference)
