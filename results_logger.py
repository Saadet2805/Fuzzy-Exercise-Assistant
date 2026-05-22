"""Append FCM runs to results.csv for user-testing (name + scores only)."""

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS_CSV = ROOT / "results.csv"

CSV_HEADER = [
    "timestamp",
    "name",
    "bmi",
    "fitness",
    "muscle_gain",
    "weight_loss",
    "light_cardio",
    "strength",
    "hiit",
    "beginner",
    "best_match",
]

OLD_HEADER = [h for h in CSV_HEADER if h != "name"]

KEY_TO_LABEL = {
    "Rec_Light_Cardio": "Light Cardio",
    "Rec_Strength": "Strength",
    "Rec_HIIT": "HIIT",
    "Rec_Beginner": "Beginner",
}


def sanitize_name(raw: str) -> str:
    name = (raw or "").strip()[:40]
    name = "".join(c for c in name if c.isalnum() or c in " -'")
    return name.strip() or "Anonymous"


def _migrate_csv_if_needed() -> None:
    if not RESULTS_CSV.exists() or RESULTS_CSV.stat().st_size == 0:
        return

    with RESULTS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return

    if "name" in header:
        return

    backup = RESULTS_CSV.with_name("results_backup.csv")
    rows_old = []
    with RESULTS_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows_old.append(row)

    if backup.exists():
        backup.unlink()
    RESULTS_CSV.rename(backup)

    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        for old in rows_old:
            writer.writerow(
                {
                    "timestamp": old.get("timestamp", ""),
                    "name": "",
                    "bmi": old.get("bmi", ""),
                    "fitness": old.get("fitness", ""),
                    "muscle_gain": old.get("muscle_gain", ""),
                    "weight_loss": old.get("weight_loss", ""),
                    "light_cardio": old.get("light_cardio", ""),
                    "strength": old.get("strength", ""),
                    "hiit": old.get("hiit", ""),
                    "beginner": old.get("beginner", ""),
                    "best_match": old.get("best_match", ""),
                }
            )


def count_results() -> int:
    _migrate_csv_if_needed()
    if not RESULTS_CSV.exists():
        return 0
    with RESULTS_CSV.open("r", encoding="utf-8", newline="") as f:
        return max(0, sum(1 for _ in f) - 1)


def append_result(
    name: str,
    bmi: float,
    fitness: int,
    muscle_gain: int,
    weight_loss: int,
    recommendations: list[dict],
) -> dict:
    _migrate_csv_if_needed()

    scores = {r["key"]: float(r["score"]) for r in recommendations}
    best_key = max(scores, key=scores.get)
    best_match = KEY_TO_LABEL.get(best_key, best_key)
    display_name = sanitize_name(name)

    row = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "name": display_name,
        "bmi": round(float(bmi), 1),
        "fitness": fitness,
        "muscle_gain": muscle_gain,
        "weight_loss": weight_loss,
        "light_cardio": round(scores.get("Rec_Light_Cardio", 0), 6),
        "strength": round(scores.get("Rec_Strength", 0), 6),
        "hiit": round(scores.get("Rec_HIIT", 0), 6),
        "beginner": round(scores.get("Rec_Beginner", 0), 6),
        "best_match": best_match,
    }

    file_empty = not RESULTS_CSV.exists() or RESULTS_CSV.stat().st_size == 0
    needs_header = file_empty
    if not file_empty:
        with RESULTS_CSV.open("r", encoding="utf-8", newline="") as f:
            first_line = f.readline()
        if "name" not in first_line:
            _migrate_csv_if_needed()
            file_empty = not RESULTS_CSV.exists() or RESULTS_CSV.stat().st_size == 0
            needs_header = file_empty

    with RESULTS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)

    return {
        "best_match": best_match,
        "name": display_name,
        "total_saved": count_results(),
    }
