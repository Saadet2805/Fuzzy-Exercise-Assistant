"""
Flask server: serves the frontend and runs FCM via POST /api/recommend
"""

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from fcm_engine import _USE_FCMPY, run_fcm
from results_logger import RESULTS_CSV, append_result, sanitize_name

ROOT = Path(__file__).resolve().parent
ENGINE_VERSION = "2.3"  # bump when FCM logic changes — check /api/health
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


@app.after_request
def no_cache(response):
    if response.content_type and "text/html" in response.content_type:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    if response.content_type and "javascript" in response.content_type:
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "fcmpy": _USE_FCMPY,
        "engine_version": ENGINE_VERSION,
    })


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}

    name = sanitize_name(str(data.get("name", "")))

    try:
        bmi = float(data.get("bmi", 0))
        fitness = int(data.get("fitness", 5))
        muscle = int(data.get("muscle", 5))
        weight_loss = int(data.get("weightloss", data.get("weight_loss", 5)))
    except (TypeError, ValueError):
        return jsonify({"error": "Please check your numbers and try again."}), 400

    if not 10 <= bmi <= 60:
        return jsonify({
            "error": (
                f"BMI {bmi} is out of range. Enter your calculated BMI (usually 10–60, e.g. 18.3)."
            )
        }), 400

    slider_checks = [
        ("Fitness level", fitness),
        ("Muscle gain goal", muscle),
        ("Weight loss goal", weight_loss),
    ]
    for label, val in slider_checks:
        if not 1 <= val <= 10:
            return jsonify({"error": f"{label} must be between 1 and 10 on the slider."}), 400

    user_name = name
    print(
        f"[FCM] name={user_name} bmi={bmi} fitness={fitness} "
        f"muscle={muscle} weight_loss={weight_loss}"
    )

    try:
        result = run_fcm(bmi, fitness, muscle, weight_loss)
        saved = append_result(
            user_name, bmi, fitness, muscle, weight_loss, result["recommendations"]
        )
    except Exception as exc:
        return jsonify({"error": f"FCM calculation failed: {exc}"}), 500

    return jsonify(
        {
            "engine_version": ENGINE_VERSION,
            "name": saved["name"],
            "best_match": saved["best_match"],
            "total_saved": saved["total_saved"],
            "inputs": {
                "bmi": round(bmi, 1),
                "fitness": fitness,
                "muscle": muscle,
                "weightloss": weight_loss,
            },
            "bmi_value": result.get("bmi_value", round(bmi, 1)),
            "inputs_fuzzy": result["inputs_fuzzy"],
            "iterations": result["iterations"],
            "engine": result["engine"],
            "recommendations": result["recommendations"],
            "logged": True,
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
    print(f"FCM engine: {engine} (version {ENGINE_VERSION})")
    print("Open: http://127.0.0.1:5000")
    print(f"Evaluation log: {RESULTS_CSV}")
    print("Press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
