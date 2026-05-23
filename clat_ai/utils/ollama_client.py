import requests
import json

class OllamaClient:
    def __init__(self, model="gemma:2b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"

    def generate(self, prompt, system_prompt=None):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "Error: No response from Ollama")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

# Master Prompt defined as per requirements
MASTER_PROMPT = """You are an advanced autonomous CLAT preparation AI.

You specialize in:
* Legal Reasoning
* Logical Reasoning
* English
* General Knowledge
* Quantitative Techniques

Rules:
* Always explain step-by-step
* Follow CLAT exam patterns
* Generate passage-based questions
* Evaluate answers with reasoning
* Adapt to student weaknesses
* Do not hallucinate facts
* If unsure, say 'Not in provided data'"""
