from flask import Flask, request, render_template_string, redirect, url_for
import csv, os

app = Flask(__name__)

DATA_FILE = "applications.csv"

# ------------------ JOB ROLES ------------------
IT_ROLES = [
    "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Software Engineer"
]

NON_IT_ROLES = [
    "HR Executive", "Recruiter",
    "Sales Executive", "Marketing Executive"
]

# ------------------ QUESTIONS ------------------
IT_QUESTIONS = [
    "Explain your previous technical experience relevant to this role.",
    "Which programming languages and frameworks are you strongest in?",
    "How do you debug and fix production issues?"
]

NON_IT_QUESTIONS = [
    "Explain your previous work experience related to this role.",
    "How do you handle pressure and deadlines?",
    "Why do you think you are suitable for this position?"
]

# ------------------ CSV INIT ------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name","Phone","Email","Role","Experience",
            "Country","State","District","Area",
            "Q1","Q2","Q3","Qualification"
        ])

# ------------------ MAIN FORM ------------------
@app.route("/", methods=["GET","POST"])
def apply():
    qualification = None

    if request.method == "POST":
        form = request.form
        answers = [form.get("q1",""), form.get("q2",""), form.get("q3","")]

        # Simple qualification logic
        qualification = "Qualified" if sum(len(a) for a in answers) >= 150 else "Not Qualified"

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                form["name"], form["phone"], form["email"], form["role"],
                form["experience"], form["country"], form["state"],
                form["district"], form["area"],
                answers[0], answers[1], answers[2], qualification
            ])

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        it_questions=IT_QUESTIONS,
        non_it_questions=NON_IT_QUESTIONS,
        qualification=qualification
    )

# ------------------ ADMIN ------------------
@app.route("/admin")
def admin():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    return render_template_string(ADMIN_TEMPLATE, rows=rows)

# ------------------ TEMPLATES ------------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card p-4 shadow">
<h3 class="text-center mb-4">Velvoro Job AI</h3>

<form method="post">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>

<select class="form-control mb-2" name="role" id="role" required onchange="loadQuestions()">
<option value="">Select Job Role</option>
{% for r in it_roles %}
<option value="{{r}}">{{r}}</option>
{% endfor %}
{% for r in non_it_roles %}
<option value="{{r}}">{{r}}</option>
{% endfor %}
</select>

<select class="form-control mb-2" name="experience">
{% for i in range(0,31) %}
<option value="{{i}}">{{i}} Years</option>
{% endfor %}
</select>

<input class="form-control mb-2" name="country" placeholder="Country" required>
<input class="form-control mb-2" name="state" placeholder="State" required>
<input class="form-control mb-2" name="district" placeholder="District" required>
<input class="form-control mb-2" name="area" placeholder="Area / Locality" required>

<div id="questions"></div>

<button class="btn btn-primary w-100 mt-3">Submit Application</button>
</form>

{% if qualification %}
<div class="alert alert-info mt-3 text-center">
Result: <b>{{qualification}}</b>
</div>
{% endif %}
</div>
</div>

<script>
const itRoles = {{ it_roles|tojson }};
const itQs = {{ it_questions|tojson }};
const nonItQs = {{ non_it_questions|tojson }};

function loadQuestions(){
    let role = document.getElementById("role").value;
    let qDiv = document.getElementById("questions");
    qDiv.innerHTML = "";

    let qs = itRoles.includes(role) ? itQs : nonItQs;

    qs.forEach((q,i)=>{
        qDiv.innerHTML += `
        <label class="mt-3"><b>${q}</b></label>
        <textarea class="form-control" name="q${i+1}" required></textarea>
        `;
    });
}
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
<body class="container mt-5">
<h3>Admin Dashboard</h3>
<table class="table table-bordered">
<tr>
<th>Name</th><th>Phone</th><th>Email</th><th>Role</th>
<th>Exp</th><th>Location</th><th>Result</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td>
<td>{{r[4]}}</td><td>{{r[5]}}, {{r[6]}}, {{r[7]}}</td><td>{{r[11]}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
