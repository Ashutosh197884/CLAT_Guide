# CLAT Preparation AI System

A production-ready autonomous CLAT tutor built with FastAPI, Ollama, and FAISS.

## 🚀 Features
* **Modular Agents**: Specialized agents for teaching, practicing, evaluating, and planning.
* **Local LLM**: Uses Ollama (Gemma or Mistral) for privacy and zero API costs.
* **RAG System**: FAISS-based vector database for retrieving legal concepts.
* **Persistent Memory**: Tracks student weak areas to personalize study plans.

## 🛠 Setup Instructions

### 1. Install Dependencies
Ensure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

### 2. Start Ollama
Install Ollama from [ollama.ai](https://ollama.ai/) and pull the model:
```bash
ollama pull gemma:2b  # or mistral
```
Make sure the Ollama server is running (usually at `http://localhost:11434`).

### 3. Ingest Data (RAG)
Run the ingestion script to create the vector index:
```bash
python rag/ingest.py
```

### 4. Run the FastAPI Server
```bash
python app.py
```
The server will start at `http://localhost:8000`.

## 📡 API Endpoints

### Health Check
`GET /`

### Chat / Tutor Interaction
`POST /chat`
**Body:**
```json
{
    "mode": "teach",
    "topic": "Contract Law"
}
```
**Modes:** `teach`, `practice`, `evaluate`, `plan`.

---
Developed by Antigravity Senior AI Systems Engineer.
