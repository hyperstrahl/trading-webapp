import os
import json
import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import urllib.request
import urllib.error

app = Flask(__name__)
CORS(app)

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '').strip()

def claude_call(prompt, max_tokens=400):
    url = "https://api.anthropic.com/v1/messages"
    data = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())
            return result["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"Anthropic HTTP {e.code}: {body}")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if not ANTHROPIC_KEY:
        return jsonify({"success": False, "error": "ANTHROPIC_KEY nicht gesetzt!"}), 500
    body = request.json
    prompt = body.get('prompt', '')
    try:
        result = claude_call(prompt, 400)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        print(f"FEHLER analyze: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/orchestrate', methods=['POST'])
def orchestrate():
    if not ANTHROPIC_KEY:
        return jsonify({"success": False, "error": "ANTHROPIC_KEY nicht gesetzt!"}), 500
    body = request.json
    prompt = body.get('prompt', '')
    try:
        result = claude_call(prompt, 380)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        print(f"FEHLER orchestrate: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok", "key_set": bool(ANTHROPIC_KEY)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
