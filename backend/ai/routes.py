from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from database.models import User
from auth.utils import get_current_user
from rag.service import rag_service
from ai.nemotron import nemotron_client

router = APIRouter(prefix="/ai", tags=["AI Doubt Solver & Tutor"])

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    response: str
    sources: List[str]

@router.post("/chat", response_model=ChatResponse)
def chat_doubt_solver(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        context_text = ""
        sources = []
        
        if request.use_rag:
            # Retrieve relevant chunks from vector DB
            retrieved_chunks = rag_service.retrieve_context(
                query=request.message,
                user_id=current_user.id,
                top_k=3
            )
            
            if retrieved_chunks:
                # Combine documents text
                context_chunks = []
                for chunk in retrieved_chunks:
                    context_chunks.append(chunk["text"])
                    # Track unique sources (document IDs)
                    doc_id = chunk["metadata"].get("document_id")
                    if doc_id and doc_id not in sources:
                        sources.append(str(doc_id))
                
                context_text = "\n---\n".join(context_chunks)

        # Generate response using NVIDIA Nemotron
        ai_response = nemotron_client.generate_response(
            prompt=request.message,
            context=context_text
        )

        return ChatResponse(
            response=ai_response,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Doubt Solver error: {str(e)}"
        )
