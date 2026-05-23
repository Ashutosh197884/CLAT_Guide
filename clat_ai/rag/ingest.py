import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class DataIngestor:
    def __init__(self, data_dir="rag/data", index_path="rag/faiss_index"):
        self.data_dir = data_dir
        self.index_path = index_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def ingest(self):
        documents = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.data_dir, filename), 'r') as f:
                    data = json.load(f)
                    for item in data:
                        text = f"Topic: {item['topic']}\nContent: {item['content']}"
                        documents.append(text)

        if not documents:
            print("No documents found to ingest.")
            return

        embeddings = self.model.encode(documents)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float32'))

        faiss.write_index(index, self.index_path + ".index")
        with open(self.index_path + "_docs.json", 'w') as f:
            json.dump(documents, f)
        
        print(f"Ingested {len(documents)} documents.")

if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.ingest()
