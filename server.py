from flask import Flask, request, jsonify, send_from_directory
import os
import json
from src.evaluator import evaluate, load_rubrics

app = Flask(__name__, static_folder=os.path.join('src', 'web'))

# Route for static files (index.html, css, js)
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/style.css')
def styles():
    return send_from_directory(app.static_folder, 'style.css')

@app.route('/app.js')
def scripts():
    return send_from_directory(app.static_folder, 'app.js')


# Endpoint to retrieve a specific rubric file (optional, UI may request)
@app.route('/rubric/<filename>', methods=['GET'])
def get_rubric(filename):
    rubrics_path = os.path.join('rubrics', filename)
    full_path = os.path.abspath(rubrics_path)
    if not os.path.isfile(full_path):
        return jsonify({"error": "Rubric not found"}), 404
    with open(full_path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

# Evaluation endpoint
@app.route('/evaluate', methods=['POST'])
def evaluate_endpoint():
    data = request.get_json()
    if not data or 'question' not in data or 'answer' not in data:
        return jsonify({"error": "Missing 'question' or 'answer' in request"}), 400
    result = evaluate(data['question'], data['answer'])
    return jsonify(result)

if __name__ == '__main__':
    # Default to port 5000; can be overridden with PORT env var
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
