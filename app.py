import os
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import urllib.request

app = Flask(__name__)
CORS(app)

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '')

def claude_call(prompt, max_tokens=400):
    url = "https://api.anthropic.com/v1/messages"
    data = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read().decode())
        return result["content"][0]["text"]

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    body = request.json
    prompt = body.get('prompt', '')
    try:
        result = claude_call(prompt, 400)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/orchestrate', methods=['POST'])
def orchestrate():
    body = request.json
    prompt = body.get('prompt', '')
    try:
        result = claude_call(prompt, 380)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok", "key_set": bool(ANTHROPIC_KEY)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
