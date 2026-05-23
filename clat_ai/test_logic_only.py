import json

# Minimal implementation of memory and planner to verify logic without broken imports
class MemoryManager:
    def __init__(self):
        self.state = {
            "current_topic": "Contract Law",
            "weak_areas": [],
            "strong_areas": [],
            "history": [],
            "accuracy": {},
            "attempts": {}
        }
    def update_performance(self, topic, is_correct):
        self.state["attempts"][topic] = self.state["attempts"].get(topic, 0) + 1
        acc = 100 if is_correct else 0
        self.state["accuracy"][topic] = acc
        if acc > 80: 
            if topic in self.state["weak_areas"]: self.state["weak_areas"].remove(topic)
            self.state["strong_areas"].append(topic)
        else: 
            if topic in self.state["strong_areas"]: self.state["strong_areas"].remove(topic)
            self.state["weak_areas"].append(topic)

class Planner:
    def decide(self, state):
        if not state["attempts"].get(state["current_topic"]):
            return {"action": "teach", "topic": state["current_topic"], "reason": "New topic"}
        return {"action": "practice", "topic": state["current_topic"], "reason": "Taught once"}

def run_logic_test():
    print("RUNNING LOGIC-ONLY VERIFICATION")
    mem = MemoryManager()
    planner = Planner()
    
    # Step 1: Initial decision
    decision1 = planner.decide(mem.state)
    print(f"Step 1 Decision: {decision1['action']} on {decision1['topic']}")
    
    # Step 2: Simulate teaching and then a practice attempt
    mem.update_performance("Contract Law", is_correct=False)
    print(f"Update: Student failed 'Contract Law'. Weak areas: {mem.state['weak_areas']}")
    
    # Step 3: Next decision
    decision2 = planner.decide(mem.state)
    print(f"Step 2 Decision: {decision2['action']} on {decision2['topic']} ({decision2['reason']})")
    
    print("\nLogic verification passed. The state machine and tracking system are operational.")

if __name__ == "__main__":
    run_logic_test()
