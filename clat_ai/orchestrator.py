from utils.ollama_client import OllamaClient, MASTER_PROMPT
from agents.tutor import TutorAgent
from agents.generator import QuestionGenerator
from agents.evaluator import EvaluatorAgent
from agents.planner import PlannerAgent
from rag.retriever import Retriever
from memory.memory import MemoryManager
import json

class Orchestrator:
    def __init__(self, model="gemma:2b"):
        self.ollama = OllamaClient(model=model)
        self.memory = MemoryManager()
        self.retriever = Retriever()
        
        self.tutor = TutorAgent(self.ollama)
        self.generator = QuestionGenerator(self.ollama)
        self.evaluator = EvaluatorAgent(self.ollama, self.memory)
        self.planner = PlannerAgent(self.ollama, self.memory)

    def build_prompt(self, mode, topic, retrieved):
        context = f"""
CONCEPTS FROM DATASET:
{json.dumps(retrieved['concepts'], indent=2)}

RELEVANT PYQs:
{json.dumps(retrieved['questions'], indent=2)}
"""
        return f"""{MASTER_PROMPT}

MODE: {mode.upper()}
TOPIC: {topic}

CONTEXT:
{context}

RULES:
- Strictly follow the context provided.
- If topic is missing in context, use your internal knowledge but mention it's a general explanation.
- Step-by-step reasoning is mandatory.
"""

    def route(self, mode, topic, user_answer=None):
        retrieved = self.retriever.smart_retrieve(topic)
        system_prompt = self.build_prompt(mode, topic, retrieved)

        if mode == "teach" or mode == "revise":
            response = self.tutor.teach(topic, context=system_prompt)
        elif mode == "practice":
            response = self.generator.practice(topic, context=system_prompt)
        elif mode == "evaluate":
            response = self.evaluator.evaluate(topic, user_answer)
            is_correct = "correct" in response.lower() and "incorrect" not in response.lower()
            self.memory.update_performance(topic, is_correct)
        else:
            response = "Invalid mode."

        self.memory.add_history({"mode": mode, "topic": topic, "response": response})
        return response

    def _classify_intent(self, message):
        prompt = f"""Analyze the user message and return ONLY a JSON object with 'mode' and 'topic'.
Modes: teach, practice, revise, evaluate.
Default mode: teach.
Default topic: Contract Law (if none found).

Message: "{message}"

JSON:"""
        response = self.ollama.generate(prompt)
        try:
            # Clean response if LLM adds markdown or chatter
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(response[start:end])
            return {"mode": "teach", "topic": "Contract Law"}
        except:
            return {"mode": "teach", "topic": "Contract Law"}

    def handle_message(self, message):
        # 1. Classify
        classification = self._classify_intent(message)
        mode = classification.get("mode", "teach")
        topic = classification.get("topic", "Contract Law")

        # 2. Route
        return self.route(mode, topic)

    def autonomous_session(self, cycles=5):
        session_results = []
        for i in range(cycles):
            decision = self.planner.decide_next_action()
            action = decision["action"]
            topic = decision["topic"]
            
            if action == "move_to_next_topic":
                self.memory.set_current_topic(topic)
                action = "teach"

            response = self.route(action, topic)
            session_results.append({
                "step": i + 1,
                "action": action,
                "topic": topic,
                "reason": decision.get("reason", ""),
                "output": response
            })
        return session_results
