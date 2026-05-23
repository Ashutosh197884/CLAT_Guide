import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from config import settings
from database.connection import engine, Base
from auth.routes import router as auth_router
from rag.routes import router as rag_router
from ai.routes import router as ai_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("lexai.main")

# Auto-create DB tables (simplified migration for dev/proto)
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize database tables: {e}")

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="Ecosystem for CLAT preparation built with FastAPI, ChromaDB RAG, and NVIDIA Nemotron 120B.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(ai_router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Serve index.html dynamically
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")
    if not os.path.exists(filepath):
        return HTMLResponse("<h1>LexAI is online! Web Interface template is missing.</h1>")
        
    with open(filepath, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
