from flask import Flask, request, render_template_string, redirect, url_for
import csv, os, uuid, smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

# ======================
# CONFIG
# ======================
UPLOAD_FOLDER = "uploads"
DATA_FILE = "applications.csv"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

CURRENT_PLAN = os.getenv("SAAS_PLAN", "FREE")  # FREE / PRO / ENTERPRISE

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

COMPANY_NAME = "Velvoro Software Solution"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ======================
# QUESTIONS
# ======================
IT_QUESTIONS = [
    "Explain your backend architecture experience.",
    "How do you design scalable APIs?",
    "How do you handle production issues?"
]

NON_IT_QUESTIONS = [
    "Explain your previous work experience.",
    "How do you handle pressure at work?",
    "How do you manage team coordination?"
]

# ======================
# HELPERS
# ======================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def ai_score_resume(text):
    if not OPENAI_API_KEY:
        return 60  # safe fallback
    # Real OpenAI call can be added here later
    return 80

def send_confirmation_email(name, email, job):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return
    try:
        msg = MIMEText(
            f"""
Hello {name},

Thank you for applying to {COMPANY_NAME}.

Job Role: {job}

Our team will review your profile.

Regards,
{COMPANY_NAME} Hiring Team
"""
        )
        msg["Subject"] = "Application Received – Velvoro"
        msg["From"] = SMTP_EMAIL
        msg["To"] = email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception:
        pass  # safe fallback

# ======================
# ROUTES
# ======================
@app.route("/", methods=["GET", "POST"])
def apply():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        job = request.form["job"]
        country = request.form["country"]
        state = request.form["state"]
        district = request.form["district"]
        area = request.form["area"]

        q1 = request.form.get("q1", "")
        q2 = request.form.get("q2", "")
        q3 = request.form.get("q3", "")

        resume_text = ""
        file = request.files["resume"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            resume_text = filename

        score = ai_score_resume(resume_text)
        qualified = "Qualified" if score >= 70 else "Not Qualified"

        exists = os.path.isfile(DATA_FILE)
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow([
                    "Name","Phone","Email","Job","Country","State","District","Area",
                    "Score","Result","Company"
                ])
            writer.writerow([
                name, phone, email, job, country, state, district, area,
                score, qualified, COMPANY_NAME
            ])

        send_confirmation_email(name, email, job)
        result = qualified

    return render_template_string(TEMPLATE, result=result)

@app.route("/admin")
def admin():
    rows = []
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    avg_score = (
        sum(int(r["Score"]) for r in rows) // len(rows)
        if rows else 0
    )
    return render_template_string(ADMIN_TEMPLATE, rows=rows, avg=avg_score)

# ======================
# TEMPLATES
# ======================
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function loadQuestions() {
    let job = document.getElementById("job").value;
    let it = {{ it|tojson }};
    let nonit = {{ nonit|tojson }};
    let qs = job.includes("Developer") ? it : nonit;
    for (let i=0;i<3;i++){
        document.getElementById("ql"+(i+1)).innerText = qs[i];
    }
}
</script>
</head>
<body class="bg-light">
<div class="container mt-5">
<h3>Velvoro Job AI</h3>
<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<select name="job" id="job" class="form-control mb-2" onchange="loadQuestions()">
<option>Backend Developer</option>
<option>HR Executive</option>
</select>

<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">

<label id="ql1"></label>
<textarea name="q1" class="form-control mb-2"></textarea>
<label id="ql2"></label>
<textarea name="q2" class="form-control mb-2"></textarea>
<label id="ql3"></label>
<textarea name="q3" class="form-control mb-2"></textarea>

<input type="file" name="resume" class="form-control mb-2" required>
<button class="btn btn-primary">Submit</button>
</form>

{% if result %}
<div class="alert alert-info mt-3">Result: {{ result }}</div>
{% endif %}
</div>
<script>loadQuestions();</script>
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
<body>
<div class="container mt-5">
<h3>Admin Dashboard</h3>
<p>Avg AI Score: {{ avg }}</p>
<table class="table table-bordered">
<tr>
<th>Name</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r.Name}}</td><td>{{r.Email}}</td><td>{{r.Job}}</td>
<td>{{r.Score}}</td><td>{{r.Result}}</td>
</tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""

# ======================
if __name__ == "__main__":
    app.run(debug=True)
