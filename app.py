from flask import Flask, request, redirect, session, render_template_string
import csv, os, random, smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DB_FILE = "applications.csv"

# =========================
# EMAIL CONFIG (Render ENV)
# =========================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")      # your gmail
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # gmail app password

# =========================
# UTILS
# =========================
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def save_to_csv(row):
    file_exists = os.path.exists(DB_FILE)
    with open(DB_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Email", "Phone"])
        writer.writerow(row)

# =========================
# HOME – JOB FORM
# =========================
@app.route("/")
def home():
    return render_template_string("""
    <h2>Velvoro Job Application</h2>
    <form method="post" action="/send-otp">
        Name:<br><input name="name" required><br><br>
        Email:<br><input name="email" required><br><br>
        Phone:<br><input name="phone" required><br><br>
        <button type="submit">Send OTP</button>
    </form>
    """)

# =========================
# SEND OTP
# =========================
@app.route("/send-otp", methods=["POST"])
def send_otp():
    session["name"] = request.form["name"]
    session["email"] = request.form["email"]
    session["phone"] = request.form["phone"]

    otp = str(random.randint(100000, 999999))
    session["otp"] = otp

    send_email(
        session["email"],
        "Velvoro OTP Verification",
        f"Your OTP is: {otp}"
    )

    return render_template_string("""
    <h3>OTP sent to your email</h3>
    <form method="post" action="/verify-otp">
        Enter OTP:<br>
        <input name="otp" required><br><br>
        <button type="submit">Verify</button>
    </form>
    """)

# =========================
# VERIFY OTP
# =========================
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    if request.form["otp"] == session.get("otp"):
        save_to_csv([
            session["name"],
            session["email"],
            session["phone"]
        ])
        return "✅ Application Submitted Successfully"
    else:
        return "❌ Invalid OTP"

# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            rows = f.read().replace("\n", "<br>")
    return f"""
    <h2>Admin Dashboard</h2>
    <div>{rows}</div>
    """

# =========================
# RENDER PORT BINDING
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
