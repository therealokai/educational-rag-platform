from fastapi import APIRouter
from app.api.v1.endpoints import ingest, questions

api_router = APIRouter()
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(questions.router, prefix="/generate/questions", tags=["questions"])
