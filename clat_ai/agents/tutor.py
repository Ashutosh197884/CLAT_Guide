class TutorAgent:
    def __init__(self, ollama):
        self.ollama = ollama

    def teach(self, topic, context="", difficulty="Moderate"):
        prompt = f"""Mode: TEACH
Topic: {topic}
Difficulty: {difficulty}
Context from Study Material: {context}

Task:
1. Explain the topic based on the specified difficulty.
2. Use real-life CLAT-relevant examples.
3. End with 2 quick concept-check questions.
"""
        return self.ollama.generate(prompt)
