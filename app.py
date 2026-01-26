from flask import Flask, request, redirect
import csv, os, random, threading, smtplib
from email.message import EmailMessage

# -------- Gemini --------
import google.generativeai as genai
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# -------- Twilio --------
from twilio.rest import Client

# -------- App --------
app = Flask(__name__)
DATA_FILE = "data.csv"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# -------- Utils --------
def save_row(row):
    exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["Name","Phone","Email","Role","OTP","AI_SCORE","STATUS"])
        w.writerow(row)

# -------- Background Email --------
def send_email_bg(to_email, otp):
    try:
        msg = EmailMessage()
        msg.set_content(f"Your OTP is {otp}")
        msg["Subject"] = "Velvoro Job AI – OTP"
        msg["From"] = os.environ["EMAIL_SENDER"]
        msg["To"] = to_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
        server.login(os.environ["EMAIL_SENDER"], os.environ["EMAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

# -------- Background WhatsApp --------
def send_whatsapp_bg(phone, otp):
    try:
        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"]
        )
        client.messages.create(
            from_=os.environ["TWILIO_WHATSAPP_FROM"],
            to=f"whatsapp:+91{phone}",
            body=f"Your Velvoro Job AI OTP is {otp}"
        )
    except Exception as e:
        print("WhatsApp error:", e)

# -------- Gemini AI Score --------
def ai_score(role):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        r = model.generate_content(
            f"Give a numeric suitability score out of 100 for job role: {role}"
        )
        return r.text.strip()
    except:
        return "50"

# -------- Home --------
@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        role = request.form["role"]

        otp = random.randint(100000,999999)
        score = ai_score(role)

        save_row([name,phone,email,role,otp,score,"PENDING"])

        threading.Thread(target=send_email_bg, args=(email,otp)).start()
        threading.Thread(target=send_whatsapp_bg, args=(phone,otp)).start()

        return f"""
        <h3>Application Submitted ✅</h3>
        <p>AI Score: <b>{score}</b></p>
        <p>OTP sent via Email & WhatsApp</p>
        <a href="/">Back</a>
        """

    return """
    <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">

    <div class="container mt-5">
    <h2>Velvoro Job AI</h2>
    <form method="post">
      <input class="form-control mb-2" name="name" placeholder="Name" required>
      <input class="form-control mb-2" name="phone" placeholder="Phone" required>
      <input class="form-control mb-2" name="email" placeholder="Email" required>
      <input class="form-control mb-2" name="role" placeholder="Job Role" required>
      <button class="btn btn-primary">Apply</button>
    </form>
    <hr>
    <a href="/admin">Admin Login</a>
    </div>
    """

# -------- Admin --------
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            return redirect("/dashboard")
        return "Wrong password"

    return """
    <h3>Admin Login</h3>
    <form method="post">
    <input type="password" name="password">
    <button>Login</button>
    </form>
    """

# -------- Dashboard --------
@app.route("/dashboard")
def dashboard():
    rows=[]
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,encoding="utf-8") as f:
            rows=list(csv.reader(f))

    html="<h2>Dashboard</h2><table border=1>"
    for r in rows:
        html+="<tr>"+"".join(f"<td>{c}</td>" for c in r)+"</tr>"
    html+="</table>"
    return html

# -------- Run --------
if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
