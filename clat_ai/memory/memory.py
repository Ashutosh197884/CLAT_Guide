import json
import os

class MemoryManager:
    def __init__(self, file_path="memory/student_state.json"):
        self.file_path = file_path
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                try:
                    return json.load(f)
                except:
                    pass
        return {
            "current_topic": "Contract Law",
            "weak_areas": [],
            "strong_areas": [],
            "history": [],
            "accuracy": {},
            "attempts": {},
            "last_result": None
        }

    def save_state(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def update_performance(self, topic, is_correct):
        # Update last result for planner
        self.state["last_result"] = "correct" if is_correct else "incorrect"
        
        # Update attempts
        self.state["attempts"][topic] = self.state["attempts"].get(topic, 0) + 1
        
        # Data-driven accuracy update
        acc = self.state["accuracy"].get(topic, 0.5)
        if is_correct:
            acc += 0.1
        else:
            acc -= 0.1
        self.state["accuracy"][topic] = max(0.0, min(1.0, acc))

        # Evolution logic
        acc_val = self.state["accuracy"][topic]
        if acc_val > 0.8:
            if topic in self.state["weak_areas"]: self.state["weak_areas"].remove(topic)
            if topic not in self.state["strong_areas"]: self.state["strong_areas"].append(topic)
        elif acc_val < 0.4:
            if topic in self.state["strong_areas"]: self.state["strong_areas"].remove(topic)
            if topic not in self.state["weak_areas"]: self.state["weak_areas"].append(topic)

        self.save_state()

    def add_history(self, entry):
        self.state["history"].append(entry)
        if len(self.state["history"]) > 50: # Cap history
            self.state["history"] = self.state["history"][-50:]
        self.save_state()

    def get_state(self):
        return self.state

    def get_dashboard_data(self):
        return {
            "weak_areas": self.state["weak_areas"],
            "strong_areas": self.state["strong_areas"],
            "accuracy": self.state["accuracy"],
            "current_topic": self.state["current_topic"]
        }

    def set_current_topic(self, topic):
        self.state["current_topic"] = topic
        self.save_state()
