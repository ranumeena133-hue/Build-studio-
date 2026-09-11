"""
HindiAI Coder - chat app for the locally trained Hindi coding model.
Run: python app/server.py  (serves on 0.0.0.0:8000)
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "model"))

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402

app = Flask(__name__, static_folder=os.path.join(HERE, "static"))

MODEL = None
TOK = None
MODEL_NAME = None


def init_model():
    global MODEL, TOK, MODEL_NAME
    ckpt_dir = os.path.join(os.path.dirname(HERE), "checkpoints")
    for name in ("best.pt", "final.pt"):
        p = os.path.join(ckpt_dir, name)
        if os.path.exists(p) and os.path.getsize(p) > 100000:
            from generate import load_model
            print(f"[app] loading {name}...", flush=True)
            MODEL, TOK = load_model(name)
            MODEL_NAME = name
            print("[app] model ready", flush=True)
            return
    print("[app] NO MODEL YET - waiting for training", flush=True)


@app.route("/")
def index():
    return send_from_directory(os.path.join(HERE, "static"), "index.html")


def model_available():
    ckpt_dir = os.path.join(os.path.dirname(HERE), "checkpoints")
    return any(os.path.exists(os.path.join(ckpt_dir, n)) and os.path.getsize(os.path.join(ckpt_dir, n)) > 100000
               for n in ("best.pt", "final.pt"))


@app.route("/api/status")
def status():
    ready = MODEL is not None or model_available()
    return jsonify({"ready": ready, "model": MODEL_NAME})


@app.route("/api/ask", methods=["POST"])
def ask():
    if MODEL is None:
        if not model_available():
            return jsonify({"error": "Model abhi ready nahi hai. Training chalu hai."}), 503
        init_model()  # lazy load on first use after training
    if MODEL is None:
        return jsonify({"error": "Model load nahi ho paaya"}), 500
    q = (request.json or {}).get("q", "").strip()
    if not q:
        return jsonify({"error": "Sawal khali hai"}), 400
    from generate import generate_code
    code = generate_code(MODEL, TOK, q, max_new=320, greedy=True)
    return jsonify({"code": code})


@app.route("/api/run", methods=["POST"])
def run():
    code = (request.json or {}).get("code", "")
    if not code.strip():
        return jsonify({"ok": False, "stderr": "Code khali hai"}), 400
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "gen.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            r = subprocess.run([sys.executable, "-I", p], capture_output=True,
                               text=True, timeout=5, cwd=td)
            return jsonify({"ok": r.returncode == 0,
                            "stdout": r.stdout[-4000:], "stderr": r.stderr[-2000:]})
        except subprocess.TimeoutExpired:
            return jsonify({"ok": False, "stdout": "",
                            "stderr": "Time out (5s se zyada liya)"})
        except Exception as e:
            return jsonify({"ok": False, "stdout": "", "stderr": str(e)})


if __name__ == "__main__":
    init_model()
    app.run(host="0.0.0.0", port=8000, threaded=True)
