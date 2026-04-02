from flask import Flask, jsonify, request, render_template
import sqlite3
import os

app = Flask(__name__)

# --- program data (same structure as the desktop versions) ---
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": (
            "Mon: Back Squat 5x5 + Core\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: Deadlift + Box Jumps\n"
            "Fri: Zone 2 Cardio 30min"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2000 kcal"
        ),
        "calorie_factor": 22,
    },
    "Muscle Gain (MG)": {
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "Breakfast: Eggs + Peanut Butter Oats\n"
            "Lunch: Chicken Biryani\n"
            "Dinner: Mutton Curry + Rice\n"
            "Target: ~3200 kcal"
        ),
        "calorie_factor": 35,
    },
    "Beginner (BG)": {
        "workout": (
            "Full Body Circuit:\n"
            "- Air Squats\n"
            "- Ring Rows\n"
            "- Push-ups\n"
            "Focus: Technique & Consistency"
        ),
        "diet": (
            "Balanced Tamil Meals\n"
            "Idli / Dosa / Rice + Dal\n"
            "Protein Target: 120g/day"
        ),
        "calorie_factor": 26,
    },
}


def get_db():
    db_path = os.environ.get("DB_PATH", "aceest.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    UNIQUE NOT NULL,
            age   INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER
        )
    """)
    conn.commit()
    conn.close()


# ---- routes ----

@app.route("/")
def index():
    return render_template("index.html", programs=list(PROGRAMS.keys()))


@app.route("/api/programs", methods=["GET"])
def list_programs():
    result = []
    for name, data in PROGRAMS.items():
        result.append({
            "name": name,
            "calorie_factor": data["calorie_factor"],
        })
    return jsonify(result)


@app.route("/api/programs/<path:program_name>", methods=["GET"])
def get_program(program_name):
    if program_name not in PROGRAMS:
        return jsonify({"error": "Program not found"}), 404
    data = PROGRAMS[program_name]
    return jsonify({
        "name": program_name,
        "workout": data["workout"],
        "diet": data["diet"],
        "calorie_factor": data["calorie_factor"],
    })


@app.route("/api/calculate-calories", methods=["POST"])
def calculate_calories():
    body = request.get_json(silent=True) or {}
    weight = body.get("weight")
    program = body.get("program")

    if weight is None or program is None:
        return jsonify({"error": "weight and program are required"}), 400

    if program not in PROGRAMS:
        return jsonify({"error": "Unknown program"}), 400

    try:
        weight = float(weight)
    except (TypeError, ValueError):
        return jsonify({"error": "weight must be a number"}), 400

    if weight <= 0:
        return jsonify({"error": "weight must be positive"}), 400

    calories = int(weight * PROGRAMS[program]["calorie_factor"])
    return jsonify({"calories": calories, "program": program, "weight": weight})


@app.route("/api/clients", methods=["GET"])
def list_clients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM clients").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/clients", methods=["POST"])
def create_client():
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    program = body.get("program", "")
    age = body.get("age")
    weight = body.get("weight")

    if not name:
        return jsonify({"error": "name is required"}), 400

    if not program or program not in PROGRAMS:
        return jsonify({"error": "valid program is required"}), 400

    calories = None
    if weight:
        try:
            calories = int(float(weight) * PROGRAMS[program]["calorie_factor"])
        except (TypeError, ValueError):
            pass

    conn = get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO clients (name, age, weight, program, calories) VALUES (?,?,?,?,?)",
            (name, age, weight, program, calories),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 409
    conn.close()

    return jsonify({"message": "Client saved", "name": name}), 201


@app.route("/api/clients/<client_name>", methods=["GET"])
def get_client(client_name):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM clients WHERE name = ?", (client_name,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Client not found"}), 404

    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
