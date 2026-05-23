import json

class PlannerAgent:
    def __init__(self, ollama, memory):
        self.ollama = ollama
        self.memory = memory

    def decide_next_action(self):
        state = self.memory.get_state()
        
        # Data-driven planning logic
        weak = state.get("weak_areas", [])
        strong = state.get("strong_areas", [])
        current_topic = state.get("current_topic", "Contract Law")
        last_result = state.get("last_result")

        # 1. Handle errors/failures
        if last_result == "incorrect":
            return {
                "action": "revise",
                "topic": current_topic,
                "reason": "Student struggled with last practice session. Re-teaching concepts."
            }

        # 2. Progress check
        acc = state["accuracy"].get(current_topic, 0.5)
        if acc > 0.8:
            # Move to next topic if strong
            new_topic = self._get_next_topic(current_topic)
            return {
                "action": "move_to_next_topic",
                "topic": new_topic,
                "reason": f"Mastered {current_topic} (Acc: {acc:.2f}). Moving to {new_topic}."
            }

        # 3. Default practice loop
        if state["attempts"].get(current_topic, 0) == 1: # Taught once
            return {
                "action": "practice",
                "topic": current_topic,
                "reason": "Concept explained. Starting practice session."
            }

        # 4. Weak area rotation
        if len(weak) > 0 and len(strong) > 2:
            return {
                "action": "revise",
                "topic": weak[0],
                "reason": "Rotating back to a weak area for reinforcement."
            }

        return {
            "action": "practice",
            "topic": current_topic,
            "reason": "Continuing practice to build confidence."
        }

    def _get_next_topic(self, current):
        topics = ["Contract Law", "Torts", "Constitutional Law", "Criminal Law", "Logical Reasoning", "English", "GK"]
        try:
            idx = topics.index(current)
            return topics[(idx + 1) % len(topics)]
        except:
            return "Contract Law"
