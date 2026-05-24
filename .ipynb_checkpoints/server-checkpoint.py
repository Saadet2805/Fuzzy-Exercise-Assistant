"""
Flask server: serves the frontend and runs FCM via POST /api/recommend
"""

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from fcm_engine import _USE_FCMPY, run_fcm

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "fcmpy": _USE_FCMPY})


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}

    try:
        bmi = int(data.get("bmi", 5))
        fitness = int(data.get("fitness", 5))
        muscle = int(data.get("muscle", 5))
        weight_loss = int(data.get("weightloss", data.get("weight_loss", 5)))
    except (TypeError, ValueError):
        return jsonify({"error": "All inputs must be numbers between 1 and 10."}), 400

    for name, val in [
        ("bmi", bmi),
        ("fitness", fitness),
        ("muscle", muscle),
        ("weight_loss", weight_loss),
    ]:
        if not 1 <= val <= 10:
            return jsonify({"error": f"{name} must be between 1 and 10."}), 400

    try:
        result = run_fcm(bmi, fitness, muscle, weight_loss)
    except Exception as exc:
        return jsonify({"error": f"FCM calculation failed: {exc}"}), 500

    return jsonify(
        {
            "inputs": {
                "bmi": bmi,
                "fitness": fitness,
                "muscle": muscle,
                "weightloss": weight_loss,
            },
            "inputs_fuzzy": result["inputs_fuzzy"],
            "iterations": result["iterations"],
            "engine": result["engine"],
            "recommendations": result["recommendations"],
        }
    )


@app.route("/<path:filename>")
def static_files(filename):
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    path = ROOT / filename
    if path.is_file():
        return send_from_directory(ROOT, filename)
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    engine = "fcmpy" if _USE_FCMPY else "built-in (install fcmpy for exact library match)"
    print("Fuzzy Exercise Assistant")
    print(f"FCM engine: {engine}")
    print("Open: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
