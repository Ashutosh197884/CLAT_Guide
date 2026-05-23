import os
import uuid
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from config import settings

class RAGService:
    def __init__(self):
        # Initialize ChromaDB persistent client
        os.makedirs(settings.CHROMA_PATH, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection(
            name="lexai_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Lazy loading embedding model to optimize startup time
        self._embedding_model = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            print("Loading sentence-transformers embedding model...")
            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return self._embedding_model

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from a PDF file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")
            
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into smaller chunks with overlap."""
        chunks = []
        words = text.split()
        
        # Simple character-based step chunker
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - chunk_overlap
            
        # Clean empty chunks
        return [c.strip() for c in chunks if c.strip()]

    def ingest_pdf(self, file_path: str, document_id: str, user_id: int) -> int:
        """Extract, chunk, embed, and store PDF in ChromaDB."""
        text = self.extract_text_from_pdf(file_path)
        chunks = self.chunk_text(text)
        
        if not chunks:
            return 0
            
        # Generate embeddings in bulk
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "user_id": user_id, "chunk_index": i} for i in range(len(chunks))]
        
        # Add to ChromaDB collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        return len(chunks)

    def retrieve_context(self, query: str, user_id: int, top_k: int = 4) -> List[Dict[str, Any]]:
        """Query ChromaDB for relevant context chunks."""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Filter by user_id to isolate user data (plus allow general system docs if user_id is 0)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"user_id": user_id}
        )
        
        retrieved_docs = []
        if results and results["documents"]:
            for i in range(len(results["documents"][0])):
                retrieved_docs.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
        return retrieved_docs

rag_service = RAGService()
