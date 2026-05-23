import json
import os
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.ollama_client import OllamaClient

client = OllamaClient(model="gemma:2b")

def generate_entries(topic, n=5):
    print(f"Generating {n} entries for {topic}...")
    prompt = f"""
Generate {n} CLAT preparation dataset entries in JSON array format.

Topic: {topic}

Each entry must include:
- topic
- subtopic
- content
- example
- question
- answer
- explanation
- difficulty (easy/medium/hard)
- type (concept/logic/gk/pyq)

Return ONLY valid JSON array. Do not add any conversational text.
"""
    response = client.generate(prompt)
    
    try:
        # Basic cleanup of markdown JSON blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)
    except Exception as e:
        print(f"Error parsing JSON for {topic}: {e}")
        return []

def save_dataset(topic, filename):
    data = generate_entries(topic)
    if not data:
        return
        
    path = f"rag/data/{filename}"
    existing_data = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                existing_data = json.load(f)
            except:
                pass
    
    existing_data.extend(data)
    
    with open(path, "w") as f:
        json.dump(existing_data, f, indent=2)
    print(f"Saved {len(data)} entries to {path}")

if __name__ == "__main__":
    topics = [
        ("Contract Law", "legal_contract.json"),
        ("Fundamental Rights", "legal_constitution.json"),
        ("Logical Reasoning", "logical.json"),
        ("Current Affairs India 2026", "gk.json"),
        ("Reading Comprehension", "english.json"),
        ("Quantitative Aptitude", "quant.json")
    ]
    
    for topic, filename in topics:
        save_dataset(topic, filename)
