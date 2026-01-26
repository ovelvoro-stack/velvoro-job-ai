from flask import Flask, request, redirect, session, url_for, render_template_string
import csv, os, random, smtplib, razorpay
from email.mime.text import MIMEText
import google.generativeai as genai

# ---------------- APP ----------------
app = Flask(__name__)
app.secret_key = "velvoro_secret_key"
DB_FILE = "applications.csv"

# ---------------- ENV ----------------
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

razorpay_client = razorpay.Client(
    auth=(os.environ.get("RAZORPAY_KEY_ID"),
          os.environ.get("RAZORPAY_KEY_SECRET"))
)

# ---------------- UTIL ----------------
def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def generate_ai_question(role):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    res = model.generate_content(f"Ask one interview question for {role}")
    return res.text

# ---------------- OTP LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        otp = random.randint(100000, 999999)
        session["otp"] = otp
        session["email"] = email
        send_email(email, "Velvoro OTP", f"Your OTP is {otp}")
        return redirect("/verify")

    return render_template_string("""
    <h2>Login</h2>
    <form method="post">
      <input name="email" required>
      <button>Send OTP</button>
    </form>
    """)

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        if int(request.form["otp"]) == session.get("otp"):
            session["user"] = session["email"]
            return redirect("/")
    return render_template_string("""
    <h3>Verify OTP</h3>
    <form method="post">
      <input name="otp">
      <button>Verify</button>
    </form>
    """)

# ---------------- JOB FORM ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        role = request.form["role"]
        question = generate_ai_question(role)

        with open(DB_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                random.randint(1000,9999),
                request.form["name"],
                session["user"],
                role,
                "PENDING",
                "NO"
            ])

        return f"<h3>AI Question</h3><p>{question}</p><a href='/pay'>Pay & Post Job</a>"

    return render_template_string("""
    <h2>Post Job</h2>
    <form method="post">
      <input name="name" placeholder="Name" required><br>
      <input name="role" placeholder="Job Role" required><br>
      <button>Submit</button>
    </form>
    """)

# ---------------- PAYMENT ----------------
@app.route("/pay")
def pay():
    order = razorpay_client.order.create({
        "amount": 29900,
        "currency": "INR",
        "payment_capture": 1
    })
    return render_template_string("""
    <h2>Pay ₹299</h2>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
    Razorpay({
      key: "{{key}}",
      amount: 29900,
      order_id: "{{order}}"
    }).open();
    </script>
    """, key=os.environ.get("RAZORPAY_KEY_ID"), order=order["id"])

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if session.get("user") != ADMIN_EMAIL:
        return "Unauthorized"

    q = request.args.get("q", "").lower()
    rows = []

    with open(DB_FILE) as f:
        reader = csv.reader(f)
        for r in reader:
            if q in ",".join(r).lower():
                rows.append(r)

    return render_template_string("""
    <h2>Admin Dashboard</h2>
    <form>
      <input name="q" placeholder="search">
    </form>
    {% for r in rows %}
      <p>{{r}}</p>
      <a href="/approve/{{r[0]}}">Approve</a> |
      <a href="/reject/{{r[0]}}">Reject</a>
    {% endfor %}
    """, rows=rows)

@app.route("/approve/<id>")
def approve(id):
    update_status(id, "APPROVED")
    return redirect("/admin")

@app.route("/reject/<id>")
def reject(id):
    update_status(id, "REJECTED")
    return redirect("/admin")

def update_status(id, status):
    rows = []
    with open(DB_FILE) as f:
        reader = csv.reader(f)
        for r in reader:
            if r and r[0] == id:
                r[4] = status
            rows.append(r)

    with open(DB_FILE, "w", newline="") as f:
        csv.writer(f).writerows(rows)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
