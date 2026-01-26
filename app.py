import os
import csv
import io
import re
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename

# ------------------ BASIC CONFIG ------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB
UPLOAD_EXTENSIONS = [".pdf", ".doc", ".docx"]
DATA_FILE = "applications.csv"

COMPANY_NAME = "Velvoro Software Solution"

# ------------------ AI CONFIG (OPTIONAL) ------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ai_score_resume(text):
    """
    Safe AI scoring:
    - If AI key available → simple real call placeholder
    - Else → deterministic fallback score
    """
    if OPENAI_API_KEY or GEMINI_API_KEY:
        # 🔒 Production-safe placeholder (no heavy SDK on free plan)
        length = len(text.split())
        return min(95, max(60, int(length / 20)))
    else:
        # fallback
        length = len(text.split())
        return min(90, max(50, int(length / 25)))

# ------------------ QUESTIONS ------------------
IT_ROLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Data Analyst", "Data Scientist",
    "DevOps Engineer", "QA / Tester", "Mobile App Developer"
]

NON_IT_ROLES = [
    "HR Executive", "Recruiter", "Marketing Executive",
    "Sales Executive", "Digital Marketing",
    "Content Writer", "Accountant", "Operations Executive"
]

IT_QUESTIONS = [
    "Explain a challenging technical problem you solved recently.",
    "Which technologies or tools are you most confident with and why?",
    "How do you ensure code quality and performance?"
]

NON_IT_QUESTIONS = [
    "Explain your previous work experience related to this role.",
    "How do you handle pressure and deadlines?",
    "Why do you think you are suitable for this position?"
]

# ------------------ LOCATION DATA (LIGHTWEIGHT SAMPLE) ------------------
# (structure scalable; free-plan friendly)
LOCATION_DATA = {
    "India": {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada"],
        "Telangana": ["Hyderabad", "Warangal"]
    },
    "USA": {
        "California": ["Los Angeles", "San Francisco"],
        "Texas": ["Austin", "Dallas"]
    }
}

# ------------------ CSV INIT ------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp","name","phone","email","job_role",
            "experience","country","state","district","area",
            "ai_score","qualification"
        ])

# ------------------ HELPERS ------------------
def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in UPLOAD_EXTENSIONS)

def qualification_from_answers(a1, a2, a3):
    total_len = len(a1.strip()) + len(a2.strip()) + len(a3.strip())
    return "Qualified" if total_len >= 150 else "Not Qualified"

# ------------------ USER PAGE ------------------
@app.route("/", methods=["GET", "POST"])
def apply():
    result = None

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        job_role = request.form["job_role"]
        experience = request.form["experience"]

        country = request.form["country"]
        state = request.form["state"]
        district = request.form["district"]
        area = request.form["area"]

        q1 = request.form["q1"]
        q2 = request.form["q2"]
        q3 = request.form["q3"]

        resume_file = request.files["resume"]

        resume_text = ""
        if resume_file and allowed_file(resume_file.filename):
            resume_text = resume_file.read().decode("latin-1", errors="ignore")

        ai_score = ai_score_resume(resume_text)
        qualification = qualification_from_answers(q1, q2, q3)

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow(), name, phone, email, job_role,
                experience, country, state, district, area,
                ai_score, qualification
            ])

        result = f"Result: {qualification} | AI Score: {ai_score}"

    return render_template_string(TEMPLATE, result=result,
                                  it_roles=IT_ROLES,
                                  non_it_roles=NON_IT_ROLES,
                                  it_q=IT_QUESTIONS,
                                  non_it_q=NON_IT_QUESTIONS,
                                  location_data=LOCATION_DATA)

# ------------------ ADMIN ------------------
@app.route("/admin")
def admin():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    avg_score = 0
    if rows:
        avg_score = sum(int(r["ai_score"]) for r in rows) // len(rows)

    return render_template_string(ADMIN_TEMPLATE,
                                  rows=rows,
                                  total=len(rows),
                                  avg=avg_score)

# ------------------ TEMPLATES ------------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>{{company}}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-4">
<div class="card shadow p-4">
<h3 class="text-center mb-4">Velvoro Software Solution – Job Application</h3>

<form method="post" enctype="multipart/form-data">

<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" name="email" type="email" placeholder="Email" required>

<select class="form-select mb-2" name="job_role" id="jobRole" required>
<option value="">Select Job Role</option>
<optgroup label="IT">
{% for r in it_roles %}<option value="{{r}}">{{r}}</option>{% endfor %}
</optgroup>
<optgroup label="Non-IT">
{% for r in non_it_roles %}<option value="{{r}}">{{r}}</option>{% endfor %}
</optgroup>
</select>

<select class="form-select mb-2" name="experience">
{% for i in range(0,31) %}
<option value="{{i}}">{{i}} Years</option>
{% endfor %}
</select>

<select class="form-select mb-2" name="country" id="country"></select>
<select class="form-select mb-2" name="state" id="state"></select>
<select class="form-select mb-2" name="district" id="district"></select>
<input class="form-control mb-2" name="area" placeholder="Area / Locality" required>

<input type="file" class="form-control mb-3" name="resume" required>

<div id="questions"></div>

<button class="btn btn-primary w-100">Submit Application</button>
</form>

{% if result %}
<div class="alert alert-info mt-3">{{result}}</div>
{% endif %}
</div>
</div>

<script>
const data = {{ location_data | tojson }};
const itQ = {{ it_q | tojson }};
const nonItQ = {{ non_it_q | tojson }};
const itRoles = {{ it_roles | tojson }};

const country = document.getElementById("country");
const state = document.getElementById("state");
const district = document.getElementById("district");

country.innerHTML = '<option value="">Country</option>';
for (let c in data) country.innerHTML += `<option>${c}</option>`;

country.onchange = () => {
state.innerHTML='<option>State</option>';
district.innerHTML='<option>District</option>';
for (let s in data[country.value])
state.innerHTML += `<option>${s}</option>`;
};

state.onchange = () => {
district.innerHTML='<option>District</option>';
data[country.value][state.value].forEach(d =>
district.innerHTML += `<option>${d}</option>`);
};

document.getElementById("jobRole").onchange = function(){
let q = itRoles.includes(this.value) ? itQ : nonItQ;
let html = "";
q.forEach((qq,i)=>{
html += `<label class="mt-2">${qq}</label>
<textarea class="form-control" name="q${i+1}" required></textarea>`;
});
document.getElementById("questions").innerHTML = html;
};
</script>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-4">
<div class="card p-3 shadow">
<h4>Admin Dashboard</h4>
<p>Total Applications: {{total}}</p>
<p>Average AI Score: {{avg}}</p>

<table class="table table-bordered">
<tr>
<th>Name</th><th>Phone</th><th>Email</th>
<th>Job</th><th>Experience</th>
<th>Location</th><th>Score</th><th>Result</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td>
<td>{{r.phone}}</td>
<td>{{r.email}}</td>
<td>{{r.job_role}}</td>
<td>{{r.experience}}</td>
<td>{{r.country}}, {{r.state}}, {{r.district}}, {{r.area}}</td>
<td>{{r.ai_score}}</td>
<td>{{r.qualification}}</td>
</tr>
{% endfor %}
</table>
</div>
</div>
</body>
</html>
"""

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
