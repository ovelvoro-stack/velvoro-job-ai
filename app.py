from flask import Flask, request, redirect, session, render_template_string
import csv, os, random
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

# --------------------
# FLASK APP
# --------------------
app = Flask(__name__)
app.secret_key = "velvoro_secret_key"
DB_FILE = "applications.csv"

# --------------------
# ENV VARIABLES
# --------------------
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --------------------
# UTIL FUNCTIONS
# --------------------
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def send_whatsapp(to_number, message):
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=f"whatsapp:{to_number}",
        body=message
    )

def save_application(data):
    file_exists = os.path.isfile(DB_FILE)
    with open(DB_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def read_applications():
    if not os.path.isfile(DB_FILE):
        return []
    with open(DB_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# --------------------
# ROUTES
# --------------------
@app.route("/")
def home():
    return render_template_string("""
    <h2>Velvoro Job AI</h2>
    <form method="post" action="/apply">
      Name:<input name="name"><br>
      Phone (+91..):<input name="phone"><br>
      Email:<input name="email"><br>
      Job Role:<input name="job"><br>
      <button>Apply</button>
    </form>
    <hr>
    <a href="/admin">Admin Login</a>
    """)

# --------------------
# APPLY + OTP
# --------------------
@app.route("/apply", methods=["POST"])
def apply():
    otp = random.randint(100000, 999999)

    session["otp"] = str(otp)
    session["form"] = dict(request.form)

    send_email(
        request.form["email"],
        "Your OTP - Velvoro",
        f"Your OTP is {otp}"
    )

    send_whatsapp(
        request.form["phone"],
        f"Velvoro OTP: {otp}"
    )

    return redirect("/verify")

# --------------------
# VERIFY OTP
# --------------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            data = session.get("form")
            data["status"] = "Pending"
            save_application(data)
            return "✅ Application submitted successfully"
        return "❌ Wrong OTP"

    return render_template_string("""
    <h3>Enter OTP</h3>
    <form method="post">
      <input name="otp">
      <button>Verify</button>
    </form>
    """)

# --------------------
# ADMIN LOGIN (BASIC)
# --------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/dashboard")
        return "Wrong password"

    return render_template_string("""
    <h3>Admin Login</h3>
    <form method="post">
      Password:<input type="password" name="password">
      <button>Login</button>
    </form>
    """)

# --------------------
# ADMIN DASHBOARD
# --------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    rows = read_applications()
    html = "<h2>Applications</h2><table border=1>"
    if rows:
        html += "<tr>" + "".join(f"<th>{k}</th>" for k in rows[0].keys()) + "</tr>"
        for r in rows:
            html += "<tr>" + "".join(f"<td>{v}</td>" for v in r.values()) + "</tr>"
    html += "</table>"
    return html

# --------------------
# RUN
# --------------------
if __name__ == "__main__":
    app.run()
