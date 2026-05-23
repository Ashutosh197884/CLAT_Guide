import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from database.connection import get_db
from database.models import UploadedDocument, User
from auth.utils import get_current_user
from rag.service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG Document Processing"])

# Directories for uploads
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 4

class QueryResponseItem(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    # Clean filename and generate local storage path
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (".", "_", "-"))
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{safe_filename}")

    try:
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file: {str(e)}"
        )

    try:
        # Insert into database to get an ID
        db_doc = UploadedDocument(
            filename=file.filename,
            file_path=file_path,
            file_type="pdf",
            user_id=current_user.id
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        # Ingest into vector DB
        chunk_count = rag_service.ingest_pdf(
            file_path=file_path,
            document_id=str(db_doc.id),
            user_id=current_user.id
        )

        # Update chunk count
        db_doc.chunk_count = chunk_count
        db.commit()

        return {
            "message": "File successfully uploaded and ingested.",
            "document_id": db_doc.id,
            "filename": db_doc.filename,
            "chunks_ingested": chunk_count
        }

    except Exception as e:
        # Clean up file if DB commit fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}"
        )

@router.post("/query", response_model=List[QueryResponseItem])
def query_documents(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        results = rag_service.retrieve_context(
            query=request.query,
            user_id=current_user.id,
            top_k=request.top_k
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )

@router.get("/documents")
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    docs = db.query(UploadedDocument).filter(UploadedDocument.user_id == current_user.id).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "chunk_count": doc.chunk_count,
            "uploaded_at": doc.uploaded_at
        } for doc in docs
    ]
