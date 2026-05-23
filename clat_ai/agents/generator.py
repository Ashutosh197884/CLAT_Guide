class QuestionGenerator:
    def __init__(self, ollama):
        self.ollama = ollama

    def practice(self, topic, context="", difficulty="Moderate"):
        prompt = f"""Mode: PRACTICE
Topic: {topic}
Difficulty: {difficulty}
Context: {context}

Task:
1. Create a CLAT-style passage (150-200 words) based on the topic or context at the specified difficulty.
2. Generate 4 multiple-choice questions (MCQs) based on the passage.
3. Provide the Correct Answer and a detailed explanation for each.
"""
        return self.ollama.generate(prompt)
