import argparse
import json
from src.evaluator import evaluate

def main():
    parser = argparse.ArgumentParser(description="Mini Answer Evaluator CLI")
    parser.add_argument("--question", type=str, help="Question text")
    parser.add_argument("--answer", type=str, help="Student answer text")
    args = parser.parse_args()

    if not args.question:
        args.question = input("Enter the question:\n")
    if not args.answer:
        args.answer = input("Enter the student's answer:\n")

    result = evaluate(args.question, args.answer)
    print("\n--- Retrieved Rubric ---")
    print(result.get("rubric_file", "fallback.json"))
    print("\n--- Evaluation Result ---")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
