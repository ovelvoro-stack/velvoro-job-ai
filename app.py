from flask import Flask, request, redirect, session, url_for, render_template_string
import csv, os, random, smtplib
from email.mime.text import MIMEText

# ===============================
# FLASK APP
# ===============================
app = Flask(__name__)
app.secret_key = "velvoro_secret_key"
DB_FILE = "applications.csv"

# ===============================
# EMAIL CONFIG (⚠️ ఇక్కడ నువ్వు పెట్టాలి)
# ===============================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_SENDER = "ovelvoro@gmail.com"      # 🔴 ఇక్కడ నీ email
EMAIL_PASSWORD = "qiduijujhrmcyfnh"       # 🔴 Gmail App Password

# ===============================
# UTILS
# ===============================
def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "name", "email", "mobile",
                "qualification", "experience",
                "job_role", "status"
            ])

init_db()

# ===============================
# OTP LOGIN
# ===============================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        otp = str(random.randint(100000, 999999))

        session["otp"] = otp
        session["email"] = email

        send_email(
            email,
            "Velvoro Login OTP",
            f"Your OTP is: {otp}"
        )

        return redirect("/verify")

    return render_template_string("""
    <h2>OTP Login</h2>
    <form method="post">
        Email: <input name="email" required>
        <button>Send OTP</button>
    </form>
    """)

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            session["logged_in"] = True
            return redirect("/apply")
        return "Invalid OTP"

    return render_template_string("""
    <h2>Verify OTP</h2>
    <form method="post">
        OTP: <input name="otp" required>
        <button>Verify</button>
    </form>
    """)

# ===============================
# JOB APPLY FORM
# ===============================
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if not session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":
        data = [
            request.form["name"],
            session["email"],
            request.form["mobile"],
            request.form["qualification"],
            request.form["experience"],
            request.form["job_role"],
            "Pending"
        ]

        with open(DB_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(data)

        send_email(
            session["email"],
            "Application Submitted",
            "Your application is successfully submitted."
        )

        return "Application Submitted Successfully"

    return render_template_string("""
    <h2>Job Application</h2>
    <form method="post">
        Name: <input name="name" required><br>
        Mobile: <input name="mobile" required><br>
        Qualification:
        <select name="qualification">
            <option>10th</option><option>Inter</option>
            <option>Degree</option><option>BTech</option>
            <option>MTech</option><option>PhD</option>
        </select><br>
        Experience (Years): <input name="experience"><br>
        Job Role:
        <select name="job_role">
            <option>Python Developer</option>
            <option>Java Developer</option>
            <option>Frontend Developer</option>
            <option>Data Analyst</option>
        </select><br><br>
        <button>Submit</button>
    </form>
    """)

# ===============================
# ADMIN DASHBOARD (SEARCH + FILTER)
# ===============================
@app.route("/admin")
def admin():
    if request.args.get("key") != "admin123":
        return "Unauthorized"

    q = request.args.get("q", "").lower()
    role = request.args.get("role", "")

    rows = []
    with open(DB_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if q and q not in r["name"].lower() and q not in r["email"].lower():
                continue
            if role and r["job_role"] != role:
                continue
            rows.append(r)

    html = """
    <h2>Admin Dashboard</h2>
    <form>
        Search: <input name="q">
        Role:
        <select name="role">
            <option value="">All</option>
            <option>Python Developer</option>
            <option>Java Developer</option>
            <option>Frontend Developer</option>
            <option>Data Analyst</option>
        </select>
        <button>Filter</button>
    </form>
    <table border=1>
        <tr>
            <th>Name</th><th>Email</th><th>Mobile</th>
            <th>Qualification</th><th>Exp</th>
            <th>Role</th><th>Status</th>
        </tr>
    """

    for r in rows:
        html += f"""
        <tr>
            <td>{r['name']}</td>
            <td>{r['email']}</td>
            <td>{r['mobile']}</td>
            <td>{r['qualification']}</td>
            <td>{r['experience']}</td>
            <td>{r['job_role']}</td>
            <td>{r['status']}</td>
        </tr>
        """

    html += "</table>"
    return html

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
