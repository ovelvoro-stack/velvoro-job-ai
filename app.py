from flask import Flask, request, render_template_string, redirect, session
import csv, os, random, smtplib
from email.message import EmailMessage
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "velvoro_secret"

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_FILE = "applications.csv"

# =======================
# 🔑 CONFIG PLACEHOLDERS
# =======================

"""
⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇
ఇక్కడ నీ Gemini API Key పెట్టాలి
"""
genai.configure(api_key="AIzaSyB-Xil35VylfYAPZQvFzCjgzcwouWudkRU")

"""
⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇
ఇక్కడ Email OTP పంపడానికి Gmail credentials
"""
SMTP_EMAIL = "ovelvoro@gmail.com"
SMTP_PASSWORD = "qiduijujhrmcyfnh"

# =======================
# DATA
# =======================

COACHINGS = {
    "IT": [
        "Python Developer","Java Developer","Full Stack",
        "Data Analyst","AI Engineer"
    ],
    "NON-IT": [
        "HR Recruiter","Digital Marketing","Accounts",
        "Customer Support","Sales Executive"
    ],
    "GENERAL": [
        "Office Admin","Clerk","Assistant","Coordinator"
    ]
}

# =======================
# AI FUNCTIONS
# =======================

def generate_question(coaching, role):
    prompt = f"Ask an interview question for {role} ({coaching})"
    model = genai.GenerativeModel("gemini-pro")
    return model.generate_content(prompt).text

def evaluate_answer(question, answer):
    prompt = f"""
    Question: {question}
    Answer: {answer}
    Evaluate and give score out of 100 and PASS or FAIL
    """
    model = genai.GenerativeModel("gemini-pro")
    result = model.generate_content(prompt).text
    return result

# =======================
# EMAIL OTP
# =======================

def send_otp(email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your Velvoro OTP is {otp}")
    msg["Subject"] = "Velvoro OTP Verification"
    msg["From"] = SMTP_EMAIL
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

# =======================
# ROUTES
# =======================

@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        otp = random.randint(100000, 999999)
        session["otp"] = otp
        session["form"] = request.form.to_dict()
        send_otp(request.form["email"], otp)
        return redirect("/verify")

    return render_template_string(FORM_HTML, coachings=COACHINGS)

@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method == "POST":
        if str(session["otp"]) != request.form["otp"]:
            return "Invalid OTP"

        f = session["form"]
        question = generate_question(f["coaching"], f["job_role"])
        result = evaluate_answer(question, f["answer"])

        with open(DB_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([f["name"], f["email"], f["job_role"], result])

        return "<h2>Application Submitted Successfully</h2>"

    return VERIFY_HTML

@app.route("/admin")
def admin():
    rows = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            rows = list(csv.reader(f))
    return render_template_string(ADMIN_HTML, rows=rows)

# =======================
# HTML
# =======================

FORM_HTML = """
<!doctype html>
<html>
<head>
<title>Velvoro Job Apply</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card p-4 shadow">

<h3 class="text-center">Velvoro Software Solution – Job Application</h3>

<form method="post" enctype="multipart/form-data">

<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>

<select class="form-control mb-2" name="coaching" required>
<option value="">Select Coaching</option>
{% for c in coachings %}
<option>{{c}}</option>
{% endfor %}
</select>

<select class="form-control mb-2" name="job_role" required>
{% for v in coachings.values() %}
{% for j in v %}
<option>{{j}}</option>
{% endfor %}
{% endfor %}
</select>

<textarea class="form-control mb-2" name="answer" placeholder="Your Answer" required></textarea>

<button class="btn btn-primary w-100">Send OTP</button>

</form>
</div>
</div>
</body>
</html>
"""

VERIFY_HTML = """
<form method="post">
<h3>Enter OTP</h3>
<input name="otp">
<button>Verify</button>
</form>
"""

ADMIN_HTML = """
<h2>Admin Dashboard</h2>
<table border=1>
{% for r in rows %}
<tr>{% for c in r %}<td>{{c}}</td>{% endfor %}</tr>
{% endfor %}
</table>
"""

if __name__ == "__main__":
    app.run(debug=True)
