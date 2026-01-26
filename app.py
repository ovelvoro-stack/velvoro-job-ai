from flask import Flask, request, redirect, session, render_template_string
import os, csv, random

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_FILE = "applications.csv"

# ---------- DATA ----------
JOB_ROLES = [
    # IT
    "Python Developer","Java Developer","Full Stack Developer","Frontend Developer",
    "Backend Developer","Data Analyst","Data Scientist","AI/ML Engineer",
    "DevOps Engineer","Cloud Engineer","Cyber Security Analyst",
    # NON-IT
    "HR Executive","HR Recruiter","Digital Marketing","SEO Executive",
    "Content Writer","Sales Executive","Business Development",
    "Customer Support","Telecaller","Accounts Executive","Office Admin"
]

QUALIFICATIONS = [
    "10th","Inter","Diploma","ITI","Graduate","B.Tech","M.Tech",
    "MBA","MCA","B.Sc","M.Sc","PhD"
]

# ---------- AI SCORING (Gemini fallback ready) ----------
def ai_evaluate(job, answer):
    keywords = {
        "Python Developer": ["list","dict","loop","function"],
        "HR Recruiter": ["recruitment","interview","screening"],
        "Digital Marketing": ["seo","ads","marketing"]
    }
    score = 0
    for k in keywords.get(job, []):
        if k.lower() in answer.lower():
            score += 25
    return score, ("PASS" if score >= 50 else "FAIL")

# ---------- ROUTES ----------
@app.route("/", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        resume = request.files["resume"]
        resume_path = os.path.join(UPLOAD_FOLDER, resume.filename)
        resume.save(resume_path)

        score, result = ai_evaluate(
            request.form["job_role"],
            request.form["answer"]
        )

        row = [
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["experience"],
            request.form["qualification"],
            request.form["job_role"],
            request.form["country"],
            request.form["state"],
            request.form["district"],
            request.form["area"],
            score,
            result,
            resume.filename
        ]

        new_file = not os.path.exists(DB_FILE)
        with open(DB_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow([
                    "Name","Phone","Email","Experience","Qualification","Job Role",
                    "Country","State","District","Area","AI Score","Result","Resume"
                ])
            writer.writerow(row)

        return f"<h2>Application Submitted – {result}</h2>"

    return render_template_string(TEMPLATE, jobs=JOB_ROLES, quals=QUALIFICATIONS)

# ---------- UI TEMPLATE ----------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Software Solution – Job Apply</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card shadow p-4">
<h2 class="text-center mb-4">Velvoro Software Solution – Job Application</h2>

<form method="post" enctype="multipart/form-data">

<div class="row">
<div class="col-md-6 mb-3">
<label>Full Name</label>
<input class="form-control" name="name" required>
</div>
<div class="col-md-6 mb-3">
<label>Mobile</label>
<input class="form-control" name="phone" required>
</div>
</div>

<div class="row">
<div class="col-md-6 mb-3">
<label>Email</label>
<input class="form-control" name="email" required>
</div>
<div class="col-md-6 mb-3">
<label>Experience (Years)</label>
<input type="number" class="form-control" name="experience" required>
</div>
</div>

<div class="row">
<div class="col-md-6 mb-3">
<label>Qualification</label>
<select class="form-control" name="qualification">
{% for q in quals %}
<option>{{q}}</option>
{% endfor %}
</select>
</div>

<div class="col-md-6 mb-3">
<label>Job Role</label>
<select class="form-control" name="job_role">
{% for j in jobs %}
<option>{{j}}</option>
{% endfor %}
</select>
</div>
</div>

<div class="row">
<div class="col-md-3 mb-3"><input class="form-control" name="country" placeholder="Country" required></div>
<div class="col-md-3 mb-3"><input class="form-control" name="state" placeholder="State" required></div>
<div class="col-md-3 mb-3"><input class="form-control" name="district" placeholder="District" required></div>
<div class="col-md-3 mb-3"><input class="form-control" name="area" placeholder="Area" required></div>
</div>

<div class="mb-3">
<label>AI Question: Explain your core skill</label>
<textarea class="form-control" name="answer" required></textarea>
</div>

<div class="mb-3">
<label>Upload Resume (PDF/DOC)</label>
<input type="file" class="form-control" name="resume" required>
</div>

<button class="btn btn-primary w-100">Submit Application</button>

</form>
</div>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
