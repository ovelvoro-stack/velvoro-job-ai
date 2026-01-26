from flask import Flask, request, redirect, session, render_template_string
import os, csv, random, time, smtplib
from email.mime.text import MIMEText

# ===================== AI (GEMINI) =====================
import google.generativeai as genai
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def ai_score(text):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        r = model.generate_content(f"Give score out of 10 for this resume:\n{text}")
        return r.text
    except:
        return "AI unavailable"

# ===================== TWILIO =====================
from twilio.rest import Client
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

twilio = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(phone, msg):
    if twilio:
        twilio.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{phone}",
            body=msg
        )

# ===================== EMAIL =====================
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def send_email(to, subject, body):
    if not EMAIL_SENDER:
        return
    msg = MIMEText(body)
    msg["From"] = EMAIL_SENDER
    msg["To"] = to
    msg["Subject"] = subject

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(EMAIL_SENDER, EMAIL_PASSWORD)
    s.send_message(msg)
    s.quit()

# ===================== APP =====================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "velvoro_secret")

DB = "applications.csv"
UPLOAD = "resumes"
os.makedirs(UPLOAD, exist_ok=True)

FIELDS = ["name","phone","email","job","resume","ai","status"]

def save_row(row):
    exists = os.path.exists(DB)
    with open(DB,"a",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        w.writerow(row)

def read_all():
    if not os.path.exists(DB): return []
    with open(DB,encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_all(rows):
    with open(DB,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

# ===================== APPLY =====================
@app.route("/", methods=["GET","POST"])
def apply():
    if request.method=="POST":
        otp = str(random.randint(100000,999999))
        session["otp"] = otp
        session["time"] = time.time()

        resume = request.files["resume"]
        path = os.path.join(UPLOAD, resume.filename)
        resume.save(path)

        ai = ai_score(resume.filename)

        session["data"] = {
            "name": request.form["name"],
            "phone": request.form["phone"],
            "email": request.form["email"],
            "job": request.form["job"],
            "resume": resume.filename,
            "ai": ai,
            "status": "Pending"
        }

        send_whatsapp(request.form["phone"], f"Velvoro OTP: {otp}")
        send_email(request.form["email"], "OTP", f"Your OTP: {otp}")

        return redirect("/verify")

    return render_template_string("""
    <h2>Velvoro Job AI</h2>
    <form method=post enctype=multipart/form-data>
    Name<input name=name><br>
    Phone<input name=phone><br>
    Email<input name=email><br>
    Job<input name=job><br>
    Resume<input type=file name=resume><br>
    <button>Send OTP</button>
    </form>
    <a href=/admin>Admin</a>
    """)

# ===================== VERIFY =====================
@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method=="POST":
        if request.form["otp"] == session.get("otp"):
            save_row(session["data"])
            session.clear()
            return "Applied Successfully ✅"
        return "Wrong OTP ❌"

    return "<form method=post>OTP<input name=otp><button>Verify</button></form>"

# ===================== ADMIN =====================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST":
        if request.form["pass"] == os.environ.get("ADMIN_PASSWORD","admin"):
            session["admin"]=True
            return redirect("/dashboard")
    return "<form method=post>Password<input name=pass><button>Login</button></form>"

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"): return redirect("/admin")
    rows = read_all()
    return render_template_string("""
    <h2>Admin Dashboard</h2>
    <table border=1>
    <tr><th>Name</th><th>Job</th><th>AI</th><th>Status</th><th>Action</th></tr>
    {% for r in rows %}
    <tr>
    <td>{{r.name}}</td>
    <td>{{r.job}}</td>
    <td>{{r.ai}}</td>
    <td>{{r.status}}</td>
    <td>
    <a href=/update/{{loop.index0}}/Approved>Approve</a>
    <a href=/update/{{loop.index0}}/Rejected>Reject</a>
    </td>
    </tr>
    {% endfor %}
    </table>
    """, rows=rows)

@app.route("/update/<int:i>/<s>")
def update(i,s):
    rows = read_all()
    rows[i]["status"] = s
    write_all(rows)
    return redirect("/dashboard")

# ===================== RUN =====================
if __name__ == "__main__":
    app.run()
