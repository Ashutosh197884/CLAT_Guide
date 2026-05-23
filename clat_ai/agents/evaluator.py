class EvaluatorAgent:
    def __init__(self, ollama, memory):
        self.ollama = ollama
        self.memory = memory

    def evaluate(self, topic, user_answer, correct_answer=""):
        prompt = f"""Mode: EVALUATE
Topic: {topic}
User's Answer: {user_answer}
Correct Reference: {correct_answer}

Task:
1. Check if the user's answer is correct or logical.
2. Explain the reasoning behind the correct answer.
3. Identify exactly where the user made a mistake.
4. If the user is wrong, flag this topic as a "Weak Area".
"""
        response = self.ollama.generate(prompt)
        
        # Simple heuristic to detect if incorrect (can be improved)
        if "incorrect" in response.lower() or "wrong" in response.lower() or "mistake" in response.lower():
            self.memory.add_weak_area(topic)
            
        return response
