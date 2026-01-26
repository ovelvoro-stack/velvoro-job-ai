from flask import Flask, request, render_template_string, redirect, url_for, session
import random, csv, os, datetime

# ---------------- BASIC SETUP ----------------
app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DATA_FILE = "applications.csv"
USERS_FILE = "users.csv"

# ---------------- INIT FILES ----------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        csv.writer(f).writerow([
            "name","phone","email","experience","qualification",
            "job_role","country","state","district","area",
            "ai_score","result","date"
        ])

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["email","otp","role","plan"])

# ---------------- MOCK AI QUESTIONS ----------------
AI_QUESTIONS = {
    "Python Developer": {
        "q": "What is a list in Python?",
        "ans": "collection"
    },
    "HR Executive": {
        "q": "What is recruitment?",
        "ans": "hiring"
    },
    "Marketing Executive": {
        "q": "What is digital marketing?",
        "ans": "online"
    }
}

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "<h2>Velvoro Job AI Live</h2><a href='/apply'>Apply Job</a> | <a href='/admin'>Admin</a>"

# ---------------- APPLY FORM ----------------
@app.route("/apply", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        experience = request.form["experience"]
        qualification = request.form["qualification"]
        job_role = request.form["job_role"]
        country = request.form["country"]
        state = request.form["state"]
        district = request.form["district"]
        area = request.form["area"]

        # AI evaluation
        user_answer = request.form["answer"].lower()
        correct = AI_QUESTIONS[job_role]["ans"]
        ai_score = 80 if correct in user_answer else 30
        result = "PASS" if ai_score >= 50 else "FAIL"

        with open(DATA_FILE,"a",newline="") as f:
            csv.writer(f).writerow([
                name,phone,email,experience,qualification,
                job_role,country,state,district,area,
                ai_score,result,str(datetime.date.today())
            ])

        return f"<h3>Application Submitted</h3><p>AI Score: {ai_score} ({result})</p><a href='/'>Home</a>"

    return render_template_string("""
    <h2>Velvoro Software Solution - Job Apply</h2>
    <form method="post">
    Name:<input name="name"><br>
    Phone:<input name="phone"><br>
    Email:<input name="email"><br>

    Experience:
    <select name="experience">
      {% for i in range(0,31) %}<option>{{i}}</option>{% endfor %}
    </select><br>

    Qualification:
    <select name="qualification">
      <option>PhD</option><option>M.Tech</option>
      <option>MCA</option><option>B.Tech</option>
      <option>B.Sc</option><option>Diploma</option>
      <option>SSC</option>
    </select><br>

    Job Role:
    <select name="job_role" onchange="this.form.submit()">
      {% for r in roles %}<option>{{r}}</option>{% endfor %}
    </select><br>

    Country:<input name="country" value="India"><br>
    State:<input name="state"><br>
    District:<input name="district"><br>
    Area:<input name="area"><br>

    <p><b>AI Question:</b> {{question}}</p>
    Answer:<input name="answer"><br><br>

    <button type="submit">Submit Application</button>
    </form>
    """,
    roles=AI_QUESTIONS.keys(),
    question=AI_QUESTIONS[list(AI_QUESTIONS.keys())[0]]["q"]
    )

# ---------------- OTP LOGIN (ADMIN) ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        otp = random.randint(100000,999999)
        session["otp"] = str(otp)
        session["email"] = email

        with open(USERS_FILE,"a",newline="") as f:
            csv.writer(f).writerow([email,otp,"admin","FREE"])

        print("OTP (Demo):", otp)
        return redirect("/verify")

    return "<form method='post'>Admin Email:<input name='email'><button>Send OTP</button></form>"

@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            session["admin"] = True
            return redirect("/admin")
        return "Invalid OTP"

    return "<form method='post'>OTP:<input name='otp'><button>Verify</button></form>"

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    rows=[]
    with open(DATA_FILE) as f:
        rows=list(csv.DictReader(f))

    html="<h2>Admin Dashboard</h2><table border=1>"
    for r in rows:
        html+="<tr>"+"".join(f"<td>{v}</td>" for v in r.values())+"</tr>"
    html+="</table><br><a href='/'>Home</a>"
    return html

# ---------------- RAZORPAY PLACEHOLDER ----------------
@app.route("/subscribe")
def subscribe():
    return """
    <h3>Subscription (Demo)</h3>
    <p>FREE → 5 Jobs</p>
    <p>PRO → ₹499 (Unlimited)</p>
    <p>(Razorpay keys add later)</p>
    """

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
