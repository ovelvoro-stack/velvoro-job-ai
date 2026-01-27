# ===============================
# Velvoro Job AI – Single File SaaS App
# ===============================

from flask import Flask, request, render_template_string, redirect, url_for
import csv, os, datetime, smtplib
from email.mime.text import MIMEText
from statistics import mean

app = Flask(__name__)

DATA_FILE = "applications.csv"
PLAN = os.getenv("SAAS_PLAN", "FREE")  # FREE / PRO / ENTERPRISE

# -------------------------------
# COUNTRY / STATE / DISTRICT DATA
# -------------------------------
COUNTRIES = ["India", "USA", "Canada", "UK", "Australia"]

STATES = {
    "India": ["Telangana", "Andhra Pradesh", "Karnataka"],
    "USA": ["California", "Texas", "New York"]
}

DISTRICTS = {
    "Telangana": ["Hyderabad", "Warangal"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada"],
    "Karnataka": ["Bengaluru", "Mysuru"],
    "California": ["Los Angeles County", "San Diego County"],
    "Texas": ["Harris County", "Dallas County"]
}

# -------------------------------
# JOB QUESTIONS
# -------------------------------
IT_QUESTIONS = [
    "Explain your backend development experience.",
    "How do you design scalable systems?",
    "Explain a challenging bug you solved."
]

NON_IT_QUESTIONS = [
    "Explain your previous work experience.",
    "How do you handle pressure and deadlines?",
    "Why are you suitable for this role?"
]

# -------------------------------
# CSV INIT
# -------------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","job","experience",
            "country","state","district","area",
            "ai_score","qualification"
        ])

# -------------------------------
# EMAIL FUNCTION (SAFE)
# -------------------------------
def send_email(to_email, name, job):
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    if not user or not pwd:
        return  # safe fallback

    msg = MIMEText(f"""
Hi {name},

Thank you for applying for the {job} role at Velvoro Software Solution.
Our team will review your profile shortly.

Regards,
Velvoro HR Team
""")
    msg["Subject"] = "Application Received – Velvoro"
    msg["From"] = user
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
    except:
        pass

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        job = request.form["job"]
        exp = request.form["experience"]
        country = request.form["country"]
        state = request.form["state"]
        district = request.form.get("district","")
        area = request.form["area"]

        # Dummy AI score (replace with real AI)
        ai_score = len(name) + len(job)
        qualification = "Qualified" if ai_score > 10 else "Not Qualified"

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name,phone,email,job,exp,
                country,state,district,area,
                ai_score,qualification
            ])

        send_email(email, name, job)

        return f"<h2>{qualification}</h2><a href='/'>Back</a>"

    return render_template_string("""
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function loadStates(){
 let c=document.getElementById("country").value;
 let s=document.getElementById("state");
 s.innerHTML="";
 {% for c,sts in STATES.items() %}
 if(c=="{{c}}"){
  {% for st in sts %}
   s.innerHTML += "<option>{{st}}</option>";
  {% endfor %}
 }
 {% endfor %}
}
function loadDistrict(){
 let s=document.getElementById("state").value;
 let d=document.getElementById("district");
 d.innerHTML="";
 {% for st,ds in DISTRICTS.items() %}
 if(s=="{{st}}"){
  {% for di in ds %}
   d.innerHTML += "<option>{{di}}</option>";
  {% endfor %}
 }
 {% endfor %}
}
</script>
</head>
<body class="container mt-5">
<h2>Velvoro Job AI</h2>
<form method="post">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>
<select class="form-control mb-2" name="job">
<option>Backend Developer</option>
<option>HR Executive</option>
</select>
<select class="form-control mb-2" name="experience">
{% for i in range(0,31) %}<option>{{i}}</option>{% endfor %}
</select>
<select class="form-control mb-2" id="country" name="country" onchange="loadStates()">
{% for c in COUNTRIES %}<option>{{c}}</option>{% endfor %}
</select>
<select class="form-control mb-2" id="state" name="state" onchange="loadDistrict()"></select>
<select class="form-control mb-2" id="district" name="district"></select>
<input class="form-control mb-2" name="area" placeholder="Area">
<button class="btn btn-primary">Submit</button>
</form>
</body>
</html>
""", COUNTRIES=COUNTRIES, STATES=STATES, DISTRICTS=DISTRICTS)

@app.route("/admin")
def admin():
    rows=[]
    with open(DATA_FILE, encoding="utf-8") as f:
        r=csv.DictReader(f)
        rows=list(r)
    avg = mean([int(x["ai_score"]) for x in rows]) if rows else 0
    return render_template_string("""
<h2>Admin Dashboard</h2>
<p>Total: {{rows|length}}</p>
<p>Avg AI Score: {{avg}}</p>
<table border=1>
<tr><th>Name</th><th>Job</th><th>Score</th><th>Result</th></tr>
{% for r in rows %}
<tr><td>{{r.name}}</td><td>{{r.job}}</td><td>{{r.ai_score}}</td><td>{{r.qualification}}</td></tr>
{% endfor %}
</table>
""", rows=rows, avg=avg)

if __name__ == "__main__":
    app.run(debug=True)
