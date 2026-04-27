# Aceestver2.0.1.py
# Flask web app for aceest-gym: copy this file to aceest-gym/app.py (matches pytest + Docker).

import os
import sqlite3

from flask import Flask, jsonify, render_template, request

PROGRAMS = {
    "Fat Loss (FL)": {
        "name": "Fat Loss (FL)",
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
        "name": "Muscle Gain (MG)",
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
        "name": "Beginner (BG)",
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

app = Flask(__name__)


def _db_path():
    return os.environ.get("DB_PATH", "aceest.db")


def get_connection():
    return sqlite3.connect(_db_path())


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            name TEXT PRIMARY KEY,
            age INTEGER,
            weight REAL,
            program TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def _client_calories(weight, program):
    if weight is None or program not in PROGRAMS:
        return None
    try:
        w = float(weight)
    except (TypeError, ValueError):
        return None
    if w <= 0:
        return None
    return int(w * PROGRAMS[program]["calorie_factor"])


@app.route("/")
def home():
    return render_template("index.html", programs=list(PROGRAMS.keys()))


@app.route("/api/programs", methods=["GET"])
def list_programs():
    out = []
    for key in PROGRAMS:
        p = PROGRAMS[key]
        out.append(
            {
                "name": p["name"],
                "workout": p["workout"],
                "diet": p["diet"],
                "calorie_factor": p["calorie_factor"],
            }
        )
    return jsonify(out)


@app.route("/api/programs/<path:prog_name>", methods=["GET"])
def get_program(prog_name):
    if prog_name not in PROGRAMS:
        return jsonify({"error": "not found"}), 404
    p = PROGRAMS[prog_name]
    return jsonify(
        {
            "name": p["name"],
            "workout": p["workout"],
            "diet": p["diet"],
            "calorie_factor": p["calorie_factor"],
        }
    )


@app.route("/api/calculate-calories", methods=["POST"])
def calculate_calories():
    data = request.get_json(silent=True) or {}
    if "weight" not in data or "program" not in data:
        return jsonify({"error": "missing fields"}), 400
    program = data["program"]
    if program not in PROGRAMS:
        return jsonify({"error": "invalid program"}), 400
    try:
        weight = float(data["weight"])
    except (TypeError, ValueError):
        return jsonify({"error": "invalid weight"}), 400
    if weight <= 0:
        return jsonify({"error": "invalid weight"}), 400
    calories = int(weight * PROGRAMS[program]["calorie_factor"])
    return jsonify(
        {
            "calories": calories,
            "program": program,
            "weight": weight,
        }
    )


@app.route("/api/clients", methods=["GET"])
def list_clients():
    conn = get_connection()
    cur = conn.execute(
        "SELECT name, age, weight, program FROM clients ORDER BY name"
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for name, age, weight, program in rows:
        result.append(
            {
                "name": name,
                "age": age,
                "weight": weight,
                "program": program,
                "calories": _client_calories(weight, program),
            }
        )
    return jsonify(result)


@app.route("/api/clients", methods=["POST"])
def create_client():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if name is None or not str(name).strip():
        return jsonify({"error": "name required"}), 400
    program = data.get("program")
    if program not in PROGRAMS:
        return jsonify({"error": "invalid program"}), 400

    age = data.get("age")
    if age is not None:
        try:
            age = int(age)
        except (TypeError, ValueError):
            age = None

    weight = data.get("weight")
    if weight is not None:
        try:
            weight = float(weight)
        except (TypeError, ValueError):
            weight = None

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO clients (name, age, weight, program) VALUES (?, ?, ?, ?)",
            (str(name).strip(), age, weight, program),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "client already exists"}), 409
    finally:
        conn.close()

    return jsonify({"name": str(name).strip()}), 201


@app.route("/api/clients/<path:client_name>", methods=["GET"])
def get_client(client_name):
    conn = get_connection()
    cur = conn.execute(
        "SELECT name, age, weight, program FROM clients WHERE name = ?",
        (client_name,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    name, age, weight, program = row
    return jsonify(
        {
            "name": name,
            "age": age,
            "weight": weight,
            "program": program,
            "calories": _client_calories(weight, program),
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
