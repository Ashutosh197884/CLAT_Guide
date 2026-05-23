from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from orchestrator import Orchestrator
import uvicorn

app = FastAPI(title="CLAT Ultimate AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class ChatRequest(BaseModel):
    mode: str
    topic: str
    answer: Optional[str] = None

class MessageRequest(BaseModel):
    message: str

class AutoRequest(BaseModel):
    cycles: int = 5

@app.get("/")
def health_check():
    return {"status": "CLAT AI Engine is ACTIVE", "version": "3.0.0 (Production)"}

@app.get("/dashboard")
def get_dashboard():
    try:
        return orchestrator.memory.get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = orchestrator.route(
            mode=request.mode.lower(),
            topic=request.topic,
            user_answer=request.answer
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/message")
async def chat_message(request: MessageRequest):
    try:
        response = orchestrator.handle_message(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auto")
async def auto_session(request: AutoRequest):
    try:
        results = orchestrator.autonomous_session(cycles=request.cycles)
        return {"session_output": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
