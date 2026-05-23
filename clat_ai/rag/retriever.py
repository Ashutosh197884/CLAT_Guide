import json
import os
import random

class Retriever:
    def __init__(self, data_dir="rag/data"):
        self.data_dir = data_dir

    def _load_all_data(self):
        all_data = []
        if not os.path.exists(self.data_dir):
            return []
            
        for file in os.listdir(self.data_dir):
            if file.endswith(".json"):
                with open(os.path.join(self.data_dir, file), 'r') as f:
                    try:
                        all_data.extend(json.load(f))
                    except:
                        continue
        return all_data

    def smart_retrieve(self, query):
        data = self._load_all_data()
        
        # Simple relevance filtering
        relevant = [d for d in data if query.lower() in str(d).lower()]
        
        if not relevant:
            # Fallback: if no specific match, pick random from general topic if possible
            relevant = data[:10] 

        concepts = [d for d in relevant if d.get("type") == "concept"]
        questions = [d for d in relevant if d.get("type") in ["pyq", "logic", "practice"]]

        # Sample for context
        retrieved_concepts = random.sample(concepts, min(2, len(concepts)))
        retrieved_questions = random.sample(questions, min(2, len(questions)))

        return {
            "concepts": retrieved_concepts,
            "questions": retrieved_questions
        }

    # Keep old method for backward compatibility if needed
    def retrieve(self, query, k=3):
        res = self.smart_retrieve(query)
        context = "CONCEPTS:\n" + json.dumps(res['concepts'], indent=2)
        context += "\n\nQUESTIONS:\n" + json.dumps(res['questions'], indent=2)
        return context
