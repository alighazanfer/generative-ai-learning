from langchain.evaluation import load_evaluator
from main import get_agent_response

def run_eval():
    evaluator = load_evaluator("labeled_criteria", criteria="correctness")

    test_cases = [
        {"input": "What is 2 + 2?", "expected": "4"},
        {"input": "What is the capital of France?", "expected": "Paris"},
        {"input": "What is the current time?", "expected": "(depends, skip strict match)"},
    ]

    for case in test_cases:
        prediction = get_agent_response(case["input"])
        reference = case["expected"]

        if reference.startswith("("):
            print(f"Q: {case['input']}\nA: {prediction}\nEVAL: skipped\n")
        else:
            result = evaluator.evaluate_strings(
                input=case["input"],
                prediction=prediction,
                reference=reference
            )
            print(f"Q: {case['input']}\nA: {prediction}\nEVAL: {result}\n")

run_eval()
