from fastapi import APIRouter, HTTPException
from app.services.questions_service import QuestionService
from app.schemas.questions import QuestionRequest, QuestionResponse

router = APIRouter()
question_service = QuestionService()


@router.post("/", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    if not request.query or len(request.query) > 250:
        raise HTTPException(status_code=400, detail="Query too long; please enter a shorter query (max 250 characters).")

    try:
        result = await question_service.generate_questions(request.query, request.num_questions)
        return QuestionResponse(
            questions=result.get("questions", []),
            evaluation=result.get("evaluation", ""),
            iterations=result.get("iterations", 0),
            passed=result.get("passed", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
