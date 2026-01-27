import os, csv, smtplib
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DATA_FILE = "applications.csv"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# JOB ROLES (EXPANDED)
# -------------------------
IT_ROLES = [
    "Backend Developer","Frontend Developer","Full Stack Developer",
    "Software Engineer","DevOps Engineer","Data Analyst",
    "Data Scientist","QA / Tester","Mobile App Developer","Cloud Engineer"
]

NON_IT_ROLES = [
    "HR Executive","Recruiter","Sales Executive","Marketing Executive",
    "Digital Marketing","Content Writer","Customer Support",
    "Operations Executive","Accountant"
]

# -------------------------
# QUESTIONS (UNCHANGED LOGIC)
# -------------------------
IT_QUESTIONS = [
    "Explain your backend / system architecture experience.",
    "Which programming languages and frameworks are you strongest in?",
    "How do you ensure performance and scalability?"
]

NON_IT_QUESTIONS = [
    "Describe your previous work experience.",
    "How do you handle targets or deadlines?",
    "Why should we hire you for this role?"
]

# -------------------------
# CSV INIT
# -------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3","ai_score","result"
        ])

# -------------------------
# AI SCORE (SAFE)
# -------------------------
def score_resume(text):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return 50
    return min(100, 60 + len(text) % 40)

# -------------------------
# EMAIL (SAFE)
# -------------------------
def send_email(to_email, name, role):
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    if not user or not pwd:
        return
    msg = MIMEText(
        f"""Dear {name},

Thank you for applying for the {role} position at Velvoro Software Solution.

Our team will review your profile and contact you shortly.

Regards,
Velvoro HR Team"""
    )
    msg["Subject"] = "Application Received – Velvoro"
    msg["From"] = user
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, pwd)
        server.send_message(msg)

# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET","POST"])
def index():
    result = None
    if request.method == "POST":
        data = {k: request.form.get(k,"") for k in [
            "name","phone","email","job_role","experience",
            "country","state","district","area","q1","q2","q3"
        ]}
        resume = request.files.get("resume")
        resume_text = ""
        if resume and resume.filename:
            filename = secure_filename(resume.filename)
            resume.save(os.path.join(UPLOAD_FOLDER, filename))
            resume_text = filename

        ai_score = score_resume(resume_text + data["q1"] + data["q2"] + data["q3"])
        result = "Qualified" if ai_score >= 60 else "Not Qualified"

        with open(DATA_FILE,"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow([
                data["name"],data["phone"],data["email"],data["job_role"],
                data["experience"],data["country"],data["state"],
                data["district"],data["area"],
                data["q1"],data["q2"],data["q3"],ai_score,result
            ])

        send_email(data["email"], data["name"], data["job_role"])

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        it_q=IT_QUESTIONS,
        non_it_q=NON_IT_QUESTIONS,
        result=result
    )

@app.route("/admin")
def admin():
    rows=[]
    scores=[]
    qualified=0
    with open(DATA_FILE,encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
            scores.append(int(r["ai_score"]))
            if r["result"]=="Qualified": qualified+=1
    avg = sum(scores)//len(scores) if scores else 0
    return render_template_string(ADMIN_TEMPLATE,
        rows=rows,
        total=len(rows),
        avg=avg,
        qualified=qualified,
        notq=len(rows)-qualified
    )

# -------------------------
# USER TEMPLATE
# -------------------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function loadQuestions(){
 let role=document.getElementById("job_role").value;
 let it={{it_q|tojson}}, nonit={{non_it_q|tojson}};
 let qs={{it_roles|tojson}}.includes(role)?it:nonit;
 for(let i=0;i<3;i++){
   document.getElementById("ql"+(i+1)).innerText=qs[i];
 }
}
</script>
</head>
<body class="bg-light">
<div class="container py-4">
<h3 class="mb-3">Apply for Job</h3>

<form method="post" enctype="multipart/form-data" class="card p-4 shadow-sm">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>

<input list="jobRoles" id="job_role" name="job_role" class="form-control mb-2"
 placeholder="Search Job Role" onchange="loadQuestions()" required>
<datalist id="jobRoles">
{% for r in it_roles+non_it_roles %}<option value="{{r}}">{% endfor %}
</datalist>

<select name="experience" class="form-control mb-2">
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

<input class="form-control mb-2" name="country" placeholder="Country">
<input class="form-control mb-2" name="state" placeholder="State">
<input class="form-control mb-2" name="district" placeholder="District">
<input class="form-control mb-2" name="area" placeholder="Area">

<label id="ql1"></label><textarea name="q1" class="form-control mb-2"></textarea>
<label id="ql2"></label><textarea name="q2" class="form-control mb-2"></textarea>
<label id="ql3"></label><textarea name="q3" class="form-control mb-2"></textarea>

<input type="file" name="resume" class="form-control mb-3">

<button class="btn btn-primary w-100">Submit Application</button>
</form>

{% if result %}
<div class="alert alert-info mt-3">Result: {{result}}</div>
{% endif %}
</div>
</body>
</html>
"""

# -------------------------
# ADMIN TEMPLATE
# -------------------------
ADMIN_TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="container py-4">
<h3>Admin Dashboard</h3>

<div class="row mb-4">
<div class="col">Total: {{total}}</div>
<div class="col">Avg Score: {{avg}}</div>
</div>

<canvas id="chart"></canvas>

<table class="table table-bordered mt-4">
<tr><th>Name</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th></tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td><td>{{r.email}}</td>
<td>{{r.job_role}}</td><td>{{r.ai_score}}</td><td>{{r.result}}</td>
</tr>
{% endfor %}
</table>

<script>
new Chart(document.getElementById("chart"),{
 type:"pie",
 data:{labels:["Qualified","Not Qualified"],
 datasets:[{data:[{{qualified}},{{notq}}]}]}
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run()
