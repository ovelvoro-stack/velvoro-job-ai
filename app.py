from flask import Flask, request, redirect, url_for
import csv, os, random, smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

DATA_FILE = "candidates.csv"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# =========================
# SAFE EMAIL FUNCTION
# =========================
def send_email_safe(to_email, subject, body):
    try:
        sender = os.environ.get("EMAIL_SENDER")
        password = os.environ.get("EMAIL_PASSWORD")

        if not sender or not password:
            print("Email skipped: ENV not set")
            return False

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email sent")
        return True

    except Exception as e:
        print("Email failed:", e)
        return False


# =========================
# SAFE WHATSAPP (Twilio optional)
# =========================
def send_whatsapp_safe(phone, message):
    try:
        from twilio.rest import Client  # optional

        sid = os.environ.get("TWILIO_ACCOUNT_SID")
        token = os.environ.get("TWILIO_AUTH_TOKEN")
        frm = os.environ.get("TWILIO_WHATSAPP_FROM")

        if not sid or not token or not frm:
            print("WhatsApp skipped: ENV missing")
            return False

        client = Client(sid, token)
        client.messages.create(
            from_=frm,
            to=f"whatsapp:{phone}",
            body=message
        )
        print("WhatsApp sent")
        return True

    except Exception as e:
        print("WhatsApp failed:", e)
        return False


# =========================
# SAVE TO CSV
# =========================
def save_candidate(row):
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Name", "Phone", "Email", "Role",
                "OTP", "Status"
            ])
        writer.writerow(row)


# =========================
# HOME – JOB APPLY FORM
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        role = request.form["role"]

        otp = random.randint(100000, 999999)

        save_candidate([name, phone, email, role, otp, "Pending"])

        send_email_safe(email, "Your OTP", f"Your OTP is {otp}")
        send_whatsapp_safe(phone, f"Your OTP is {otp}")

        return "Application Submitted Successfully ✅"

    return """
    <h2>Velvoro Job AI</h2>
    <form method="post">
      Name:<br><input name="name"><br>
      Phone:<br><input name="phone"><br>
      Email:<br><input name="email"><br>
      Job Role:<br><input name="role"><br><br>
      <button type="submit">Apply</button>
    </form>
    <hr>
    <a href="/admin">Admin Login</a>
    """


# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            return redirect("/dashboard")
        return "Wrong Password"

    return """
    <h3>Admin Login</h3>
    <form method="post">
      Password: <input type="password" name="password">
      <button>Login</button>
    </form>
    """


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

    html = "<h2>Admin Dashboard</h2><table border=1>"
    for r in rows:
        html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    html += "</table>"

    return html


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
