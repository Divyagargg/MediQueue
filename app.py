from flask import Flask, render_template, request, jsonify
from heapq import heappush, heappop
from collections import deque
from datetime import datetime
import itertools

app = Flask(__name__)

# ---------------- DSA: Queue + Priority Queue ----------------
normal_queue = deque()
emergency_queue = []
counter = itertools.count()

patients = []
next_id = 1001

def priority_value(priority):
    return {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}.get(priority, 4)

def add_patient_to_ds(patient):
    if patient["priority"] == "Normal":
        normal_queue.append(patient["id"])
    else:
        heappush(emergency_queue, (priority_value(patient["priority"]), next(counter), patient["id"]))

def find_patient(pid):
    return next((p for p in patients if p["id"] == pid), None)

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/patients")
def get_patients():
    return jsonify(patients)

@app.post("/api/patients")
def add_patient():
    global next_id
    data = request.get_json(force=True)

    name = data.get("name", "").strip()
    age = data.get("age")
    gender = data.get("gender", "Other")
    department = data.get("department", "General")
    priority = data.get("priority", "Normal")
    symptoms = data.get("symptoms", "").strip()

    if not name or not age or not symptoms:
        return jsonify({"error": "Name, age and symptoms are required."}), 400

    patient = {
        "id": next_id,
        "name": name,
        "age": int(age),
        "gender": gender,
        "department": department,
        "priority": priority,
        "symptoms": symptoms,
        "status": "Waiting",
        "arrival": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    next_id += 1
    patients.append(patient)
    add_patient_to_ds(patient)
    return jsonify(patient), 201

@app.post("/api/next")
def call_next():
    waiting_ids = set()
    patient_map = {p["id"]: p for p in patients if p["status"] == "Waiting"}

    # Priority Queue gets emergency/priority cases first
    while emergency_queue:
        _, _, pid = heappop(emergency_queue)
        if pid in patient_map:
            patient_map[pid]["status"] = "In Consultation"
            return jsonify(patient_map[pid])

    # FIFO Queue for normal patients
    while normal_queue:
        pid = normal_queue.popleft()
        if pid in patient_map:
            patient_map[pid]["status"] = "In Consultation"
            return jsonify(patient_map[pid])

    return jsonify({"error": "No patients are waiting."}), 404

@app.post("/api/discharge/<int:pid>")
def discharge(pid):
    patient = find_patient(pid)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404
    patient["status"] = "Discharged"
    return jsonify(patient)

@app.delete("/api/patients/<int:pid>")
def delete_patient(pid):
    global patients
    patient = find_patient(pid)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404
    patients = [p for p in patients if p["id"] != pid]
    return jsonify({"message": "Patient removed."})

@app.get("/api/search")
def search():
    q = request.args.get("q", "").lower().strip()
    result = [
        p for p in patients
        if q in str(p["id"]).lower()
        or q in p["name"].lower()
        or q in p["department"].lower()
        or q in p["symptoms"].lower()
    ]
    return jsonify(result)

@app.get("/api/stats")
def stats():
    return jsonify({
        "total": len(patients),
        "waiting": sum(p["status"] == "Waiting" for p in patients),
        "consultation": sum(p["status"] == "In Consultation" for p in patients),
        "discharged": sum(p["status"] == "Discharged" for p in patients),
        "emergency": sum(p["priority"] in ["Critical", "High"] and p["status"] == "Waiting" for p in patients)
    })

if __name__ == "__main__":
    app.run(debug=True)
