import os
import csv
import uuid
from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "velvoro-secret"

UPLOAD_FOLDER = "uploads"
DATA_FILE = "applications.csv"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# Static Data (Lightweight)
# -----------------------------
COUNTRIES = [
    "India", "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "France", "Singapore", "UAE"
]

STATES = {
    "India": ["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"],
    "United States": ["California", "Texas", "New York"]
}

DISTRICTS = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur"],
    "Telangana": ["Hyderabad", "Warangal"],
    "California": ["Los Angeles", "San Francisco"],
    "Texas": ["Dallas", "Austin"]
}

IT_ROLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Data Analyst", "DevOps Engineer"
]

NON_IT_ROLES = [
    "HR Executive", "Recruiter", "Sales Executive",
    "Marketing Executive", "Operations Executive"
]

IT_QUESTIONS = [
    "Explain a challenging technical problem you solved.",
    "How do you debug a production issue?",
    "Describe a project you are proud of."
]

NON_IT_QUESTIONS = [
    "Explain your previous work experience related to this role.",
    "How do you handle pressure and deadlines?",
    "Why do you think you are suitable for this position?"
]

# -----------------------------
# CSV Init
# -----------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Phone", "Email", "JobRole", "Experience",
            "Country", "State", "District", "Area",
            "AIScore", "Qualification"
        ])

# -----------------------------
# AI Scoring (Safe Fallback)
# -----------------------------
def ai_score(text):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return min(100, max(40, len(text) // 5))
    # real AI can be plugged later
    return 75

def qualification(answer_text):
    return "Qualified" if len(answer_text) > 120 else "Not Qualified"

# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def apply():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        role = request.form["job_role"]
        exp = request.form["experience"]
        country = request.form["country"]
        state = request.form.get("state", "")
        district = request.form.get("district", "")
        area = request.form["area"]
        answers = " ".join([
            request.form.get("q1", ""),
            request.form.get("q2", ""),
            request.form.get("q3", "")
        ])

        resume = request.files["resume"]
        filename = secure_filename(resume.filename)
        resume.save(os.path.join(UPLOAD_FOLDER, filename))

        score = ai_score(answers)
        qual = qualification(answers)
        result = qual

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name, phone, email, role, exp,
                country, state, district, area,
                score, qual
            ])

    return render_template_string(TEMPLATE,
        countries=COUNTRIES,
        states=STATES,
        districts=DISTRICTS,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        it_q=IT_QUESTIONS,
        non_it_q=NON_IT_QUESTIONS,
        result=result
    )

@app.route("/admin")
def admin():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            rows.append(r)
    return render_template_string(ADMIN, rows=rows)

# -----------------------------
# Templates (Bootstrap 5)
# -----------------------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job Application</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card shadow p-4">
<h3 class="text-center mb-4">Velvoro Software Solution – Job Application</h3>

{% if result %}
<div class="alert alert-info text-center">
Application Submitted – {{ result }}
</div>
{% endif %}

<form method="post" enctype="multipart/form-data">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>

<select class="form-select mb-2" name="job_role" id="job_role" required>
<option value="">Select Job Role</option>
<optgroup label="IT">
{% for r in it_roles %}<option>{{r}}</option>{% endfor %}
</optgroup>
<optgroup label="Non-IT">
{% for r in non_it_roles %}<option>{{r}}</option>{% endfor %}
</optgroup>
</select>

<select class="form-select mb-2" name="experience">
{% for i in range(0,31) %}
<option>{{i}}</option>
{% endfor %}
</select>

<select class="form-select mb-2" name="country" id="country">
{% for c in countries %}<option>{{c}}</option>{% endfor %}
</select>

<select class="form-select mb-2" name="state" id="state"></select>
<select class="form-select mb-2" name="district" id="district"></select>
<input class="form-control mb-2" name="area" placeholder="Area / Locality">

<input class="form-control mb-3" type="file" name="resume" required>

<div id="questions"></div>

<button class="btn btn-primary w-100">Submit Application</button>
</form>
</div>
</div>

<script>
const states = {{ states|tojson }};
const districts = {{ districts|tojson }};
const itQ = {{ it_q|tojson }};
const nonItQ = {{ non_it_q|tojson }};

document.getElementById("country").onchange = function(){
 let s = document.getElementById("state");
 s.innerHTML="";
 (states[this.value]||[]).forEach(v=>s.innerHTML+=`<option>${v}</option>`);
 s.dispatchEvent(new Event("change"));
};

document.getElementById("state").onchange = function(){
 let d = document.getElementById("district");
 d.innerHTML="";
 (districts[this.value]||[]).forEach(v=>d.innerHTML+=`<option>${v}</option>`);
};

document.getElementById("job_role").onchange = function(){
 let q = document.getElementById("questions");
 q.innerHTML="";
 let list = itQ.concat(nonItQ).includes(this.value) ? itQ : nonItQ;
 list.forEach((t,i)=>q.innerHTML+=`
 <label class="mt-2">${t}</label>
 <textarea class="form-control" name="q${i+1}" required></textarea>
 `);
};
</script>
</body>
</html>
"""

ADMIN = """
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-4">
<h3>Admin Dashboard</h3>
<table class="table table-bordered">
<tr>
<th>Name</th><th>Phone</th><th>Email</th><th>Role</th>
<th>Exp</th><th>Location</th><th>AI</th><th>Status</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td>
<td>{{r[4]}}</td>
<td>{{r[5]}}, {{r[6]}}, {{r[7]}}, {{r[8]}}</td>
<td>{{r[9]}}</td><td>{{r[10]}}</td>
</tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
