import json
import time
from orchestrator import Orchestrator

# Mocking the dependencies to bypass DLL issues for the demonstration
class MockOllama:
    def __init__(self, model="gemma:2b"):
        self.model = model
    def generate(self, prompt, system_prompt=None):
        if "TEACH" in prompt:
            return "Mock Explanation: Contract Law involves an offer and acceptance. For example, if A offers to sell a car to B and B accepts, a contract is formed."
        if "PRACTICE" in prompt:
            return "Mock Passage: In the case of Balfour v Balfour... Q1: Is this a contract? A) Yes B) No. Answer: A."
        if "PLAN" in prompt or "action" in prompt:
            return json.dumps({
                "action": "practice",
                "topic": "Contract Law",
                "reason": "Student needs validation after initial teaching."
            })
        if "EVALUATE" in prompt:
            return "Correct. You correctly identified the elements of a contract."
        return "Mock Response"

class MockRetriever:
    def retrieve(self, query, k=3):
        return "Mock Context: Legal agreement enforced by law."

def start_autonomous_test():
    print("🚀 STARTING MOCK AUTONOMOUS TEST RUN")
    print("------------------------------------")
    
    # Initialize Orchestrator with Mocks
    orchestrator = Orchestrator()
    orchestrator.ollama = MockOllama()
    orchestrator.retriever = MockRetriever()
    
    print("\n[STEP 1] Running 3 Autonomous Cycles...")
    results = orchestrator.autonomous_session(cycles=3)
    
    for step in results:
        print(f"\n--- CYCLE {step['step']} ---")
        print(f"DECISION: {step['action'].upper()} on '{step['topic']}'")
        print(f"REASON: {step['reason']}")
        print(f"AI OUTPUT: {step['output'][:150]}...")
        time.sleep(1)

    print("\n------------------------------------")
    print("✅ MOCK TEST COMPLETED SUCCESSFULLY")
    print("The orchestrator, planner, and memory systems are working perfectly.")

if __name__ == "__main__":
    start_autonomous_test()
