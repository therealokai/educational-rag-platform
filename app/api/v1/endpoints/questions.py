from fastapi import APIRouter, HTTPException
from app.services.questions_service import QuestionService
from app.schemas.questions import QuestionRequest, QuestionResponse

router = APIRouter()
question_service = QuestionService()

@router.post("/", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    try:
        result = await question_service.generate_questions(request.query)
        return QuestionResponse(
            questions=result["questions"],
            evaluation=result["evaluation"],
            iterations=result["iterations"],
            passed=result["passed"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
