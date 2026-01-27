from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ingest_service import IngestService
from app.schemas.ingest import IngestResponse
import shutil
import os

router = APIRouter()
ingest_service = IngestService()

@router.post("/", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        toc = ingest_service.process_pdf_simple(temp_file)
        return IngestResponse(message="PDF ingested successfully", table_of_contents=toc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
