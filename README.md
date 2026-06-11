# Mini Answer Evaluator

A lightweight Python tool that evaluates a student's answer against a rubric using the Google Gemini API.

## Features
- Keyword‑based rubric retrieval (each rubric stored in its own JSON file).
- Calls Gemini (any model) with a controlled prompt and parses the JSON response.
- Command‑line interface for quick testing.
- Minimal static web UI served by Flask (dark glass‑morphism design).

## Quick Start
```bash
# Clone / copy the repo
cd mini_answer_evaluator
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Set your Gemini API key
copy .env.example .env
# Edit .env and add GEMINI_API_KEY=YOUR_KEY

# Run the CLI
python -m src.cli --question "What is Newton's second law?" --answer "F = ma"

# or start the web UI
python server.py
# Open http://localhost:5000 in your browser
```

## Project Structure
```
mini_answer_evaluator/
│   README.md
│   requirements.txt
│   .env.example
│
├─ rubrics/
│   ├─ fallback.json
│   ├─ physics.json
│   ├─ mathematics.json
│   └─ english.json
│
├─ src/
│   ├─ __init__.py
│   ├─ evaluator.py
│   ├─ cli.py
│   └─ web/
│       ├─ index.html
│       ├─ style.css
│       └─ app.js
│
└─ server.py
```

## Prompt Sent to Gemini
```
You are an evaluation assistant. Given the **question**, the **student answer**, and a **rubric**, output a JSON object with the following keys:
- marks_awarded (integer)
- max_marks (integer, from the rubric)
- feedback (short, constructive feedback)
- justification (explain why the marks were given)

Respond **only** with valid JSON.
```

## Improvements
- Add embeddings for smarter rubric retrieval.
- Support multiple LLM providers.
- Extend UI with richer visualizations of rubric criteria.
