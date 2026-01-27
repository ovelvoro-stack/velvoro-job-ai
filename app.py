import os, csv, smtplib
from flask import Flask, request, render_template_string
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DATA_FILE = "applications.csv"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- JOB ROLES ----------------
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

IT_QUESTIONS = [
    "Explain a technical challenge you solved recently.",
    "Which tools / technologies are you strongest in?",
    "How do you ensure code quality and scalability?"
]

NON_IT_QUESTIONS = [
    "Describe your previous work experience.",
    "How do you handle pressure and deadlines?",
    "Why should we hire you for this role?"
]

# ---------------- CSV INIT ----------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE,"w",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow([
            "name","phone","email","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3","ai_score","result"
        ])

# ---------------- AI SCORE ----------------
def score_resume(text):
    return min(100, 50 + len(text) % 50)

# ---------------- EMAIL ----------------
def send_email(to_email,name,role):
    user=os.getenv("SMTP_USER"); pwd=os.getenv("SMTP_PASS")
    if not user or not pwd: return
    msg=MIMEText(f"""
Dear {name},

Thank you for applying for the {role} role at Velvoro Software Solution.

Our team will review your application shortly.

Regards,
Velvoro Hiring Team
""")
    msg["Subject"]="Application Received – Velvoro"
    msg["From"]=user; msg["To"]=to_email
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(user,pwd); s.send_message(msg)

# ---------------- ROUTES ----------------
@app.route("/",methods=["GET","POST"])
def index():
    result=None
    if request.method=="POST":
        f=request.form
        resume=request.files.get("resume")
        resume_text=""
        if resume:
            path=os.path.join(UPLOAD_FOLDER,secure_filename(resume.filename))
            resume.save(path); resume_text=resume.filename

        ai=score_resume(resume_text+f["q1"]+f["q2"]+f["q3"])
        result="Qualified" if ai>=60 else "Not Qualified"

        with open(DATA_FILE,"a",newline="",encoding="utf-8") as fcsv:
            csv.writer(fcsv).writerow([
                f["name"],f["phone"],f["email"],f["job_role"],f["experience"],
                f["country"],f["state"],f["district"],f["area"],
                f["q1"],f["q2"],f["q3"],ai,result
            ])
        send_email(f["email"],f["name"],f["job_role"])

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES,non_it_roles=NON_IT_ROLES,
        it_q=IT_QUESTIONS,non_it_q=NON_IT_QUESTIONS,
        result=result)

@app.route("/admin")
def admin():
    rows=[]
    with open(DATA_FILE,encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    total=len(rows)
    avg=sum(int(r["ai_score"]) for r in rows)/total if total else 0
    q=sum(1 for r in rows if r["result"]=="Qualified")
    return render_template_string(ADMIN,rows=rows,total=total,avg=avg,q=q)

# ---------------- TEMPLATES ----------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const IT={{it_q|tojson}},NONIT={{non_it_q|tojson}};
function loadQ(){
 let r=document.getElementById("job_role").value;
 let qs=IT_ROLES.includes(r)?IT:NONIT;
 for(let i=0;i<3;i++){
  document.getElementById("ql"+(i+1)).innerText=qs[i];
 }
}
const IT_ROLES={{it_roles|tojson}};
</script>
</head>
<body class="bg-light">
<div class="container py-4">
<div class="card shadow p-4">
<h4 class="mb-3">Apply for Job</h4>
<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<input list="roles" id="job_role" name="job_role" class="form-control mb-2" oninput="loadQ()" placeholder="Select Job Role">
<datalist id="roles">
{% for r in it_roles+non_it_roles %}<option value="{{r}}">{% endfor %}
</datalist>

<select name="experience" class="form-control mb-2">
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">

<label id="ql1"></label><textarea name="q1" class="form-control mb-2"></textarea>
<label id="ql2"></label><textarea name="q2" class="form-control mb-2"></textarea>
<label id="ql3"></label><textarea name="q3" class="form-control mb-2"></textarea>

<input type="file" name="resume" class="form-control mb-3" required>
<button class="btn btn-primary w-100">Submit</button>
</form>
{% if result %}<div class="alert alert-info mt-3">Result: {{result}}</div>{% endif %}
</div>
</div>
</body>
</html>
"""

ADMIN = """
<!doctype html>
<html>
<head>
<title>Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="container py-4">
<h3>Admin Dashboard</h3>
<p>Total: {{total}} | Avg Score: {{avg|round(1)}} | Qualified: {{q}}</p>
<canvas id="chart"></canvas>
<table class="table table-bordered mt-4">
<tr><th>Name</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th></tr>
{% for r in rows %}
<tr><td>{{r.name}}</td><td>{{r.email}}</td><td>{{r.job_role}}</td><td>{{r.ai_score}}</td><td>{{r.result}}</td></tr>
{% endfor %}
</table>
<script>
new Chart(document.getElementById("chart"),{
 type:"bar",
 data:{labels:["Qualified","Not Qualified"],
 datasets:[{data:[{{q}},{{total-q}}]}]}
});
</script>
</body>
</html>
"""

if __name__=="__main__":
    app.run()
