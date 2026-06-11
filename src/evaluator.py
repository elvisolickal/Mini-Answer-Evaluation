import os
import json
from typing import Dict, List
from pathlib import Path

from groq import Groq
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Configure Groq client
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set in environment variables.")

client = Groq(api_key=API_KEY)

# Default model; override by setting GROQ_MODEL in .env
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Path to rubric directory (two levels up from this file)
RUBRIC_DIR = Path(__file__).resolve().parent.parent / "rubrics"


def load_rubrics() -> List[Dict]:
    """Load all rubric JSON files from the rubrics/ directory.

    Each entry gets a '_filename' key injected so callers can
    identify which file a rubric came from.
    """
    rubrics = []
    for file in RUBRIC_DIR.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["_filename"] = file.name
            rubrics.append(data)
    return rubrics


def retrieve_rubric(question: str) -> Dict:
    """Select the most relevant rubric using keyword overlap.

    For every non-fallback rubric we count how many of its 'keywords'
    appear in the (lower-cased) question string. The rubric with the
    highest count is returned. Ties are broken by order of discovery.
    Falls back to 'fallback.json' when no keywords match.
    """
    question_lc = question.lower()
    rubrics = load_rubrics()

    best_score = -1
    best_rubric = None
    fallback = None

    for rub in rubrics:
        if rub.get("_filename") == "fallback.json":
            fallback = rub
            continue
        keywords: List[str] = rub.get("keywords", [])
        score = sum(kw.lower() in question_lc for kw in keywords)
        if score > best_score:
            best_score = score
            best_rubric = rub

    if best_score <= 0 or best_rubric is None:
        return fallback if fallback else {"max_marks": 5, "criteria": []}
    return best_rubric


def build_prompt(question: str, answer: str, rubric: Dict) -> str:
    """Construct the prompt sent to the LLM.

    We strip the internal '_filename' key before serialising the
    rubric so the model never sees that implementation detail.
    """
    rubric_text = json.dumps(
        {k: v for k, v in rubric.items() if k != "_filename"}, indent=2
    )
    prompt = (
        "You are an evaluation assistant. Given the QUESTION, the STUDENT ANSWER, "
        "and a RUBRIC, output a JSON object with these keys:\n"
        "  - marks_awarded  (integer)\n"
        "  - max_marks      (integer – use the rubric's max_marks value)\n"
        "  - feedback       (short, constructive, one to two sentences)\n"
        "  - justification  (explain the marks awarded with reference to rubric criteria)\n\n"
        "Respond ONLY with valid JSON. Do NOT wrap it in markdown code fences.\n\n"
        f"QUESTION:\n{question}\n\n"
        f"STUDENT ANSWER:\n{answer}\n\n"
        f"RUBRIC:\n{rubric_text}\n"
    )
    return prompt


def call_llm(prompt: str) -> Dict:
    """Send the prompt to Groq and return the parsed JSON response.

    The model is instructed to respond with pure JSON. We also strip
    markdown fences defensively in case they appear anyway.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict answer evaluation assistant. "
                    "Always respond with valid JSON only, no extra text."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    text = response.choices[0].message.content.strip()

    # Strip optional markdown fences  ```json … ``` defensively
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        ).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM response is not valid JSON.\nError: {e}\nResponse: {text}"
        )


def evaluate(question: str, answer: str) -> Dict:
    """Orchestrate rubric retrieval, prompt building, LLM call, and result assembly.

    The returned dict always contains:
      marks_awarded, max_marks, feedback, justification, rubric_file
    """
    rubric = retrieve_rubric(question)
    prompt = build_prompt(question, answer, rubric)
    result = call_llm(prompt)

    # Guarantee required keys are present
    result.setdefault("max_marks", rubric.get("max_marks", 5))
    result["rubric_file"] = rubric.get("_filename", "fallback.json")
    return result
