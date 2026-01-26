from flask import Flask, request, redirect, session, render_template_string
import csv, os, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "velvoro_final_secret"

DATA = "data"
os.makedirs(DATA, exist_ok=True)

APP_CSV = f"{DATA}/applications.csv"
PAY_CSV = f"{DATA}/payments.csv"
SUB_CSV = f"{DATA}/subscriptions.csv"

# ---------------- INIT CSV ----------------
def init():
    if not os.path.exists(APP_CSV):
        with open(APP_CSV,"w",newline="") as f:
            csv.writer(f).writerow(
                ["name","email","category","job","exp","qual","resume","quiz","date"]
            )
    if not os.path.exists(PAY_CSV):
        with open(PAY_CSV,"w",newline="") as f:
            csv.writer(f).writerow(["date","amount"])
    if not os.path.exists(SUB_CSV):
        with open(SUB_CSV,"w",newline="") as f:
            csv.writer(f).writerow(["company","plan","start"])
init()

# ---------------- EMAIL CONFIG ----------------
SMTP_EMAIL = "yourmail@gmail.com"
SMTP_PASS  = "your-app-password"

def send_mail(to,name):
    msg = MIMEMultipart()
    msg["From"] = "Velvoro HR <"+SMTP_EMAIL+">"
    msg["To"] = to
    msg["Subject"] = "Velvoro – Application Received"

    body = f"""
    Dear {name},

    Thank you for applying at Velvoro Software Solution.

    Our recruitment team is reviewing your profile.
    If shortlisted, you will be contacted shortly.

    Regards,
    Velvoro HR Team
    www.velvoro.com
    """
    msg.attach(MIMEText(body,"plain"))

    s = smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(SMTP_EMAIL,SMTP_PASS)
    s.send_message(msg)
    s.quit()

# ---------------- JOB DATA ----------------
IT_JOBS = ["Python Developer","Java Developer","Data Analyst"]
NON_IT_JOBS = ["HR Recruiter","Sales Executive"]
QUALS = ["Any Degree","B.Tech","MBA","Inter"]

# ---------------- APPLY ----------------
@app.route("/",methods=["GET","POST"])
def apply():
    if request.method=="POST":
        f=request.form
        quiz = "PASS" if f["quiz"]=="correct" else "FAIL"

        with open(APP_CSV,"a",newline="") as c:
            csv.writer(c).writerow([
                f["name"],f["email"],f["category"],f["job"],
                f["exp"],f["qual"],f["resume"],quiz,
                datetime.date.today()
            ])

        try:
            send_mail(f["email"],f["name"])
        except:
            pass

        return redirect("/success")

    return render_template_string("""
    <h2>Velvoro Job Application</h2>
    <form method="post">
    Name:<input name="name" required><br>
    Email:<input name="email" required><br>

    Category:
    <select id="cat" name="category" onchange="loadJobs()">
      <option>IT</option><option>Non-IT</option>
    </select><br>

    Job:
    <select id="jobs" name="job"></select><br>

    Experience:
    <select name="exp">{% for i in range(0,31) %}<option>{{i}}</option>{% endfor %}</select><br>

    Qualification:
    <select name="qual">{% for q in quals %}<option>{{q}}</option>{% endfor %}</select><br>

    Resume Name:<input name="resume" required><br>

    Quiz: Python is?<br>
    <input type="radio" name="quiz" value="correct">Programming Language
    <input type="radio" name="quiz" value="wrong">Database<br>

    <button>Apply</button>
    </form>

    <script>
    const IT={{it|safe}},NON={{non|safe}};
    function loadJobs(){
      let j=document.getElementById("jobs");
      j.innerHTML="";
      (cat.value=="IT"?IT:NON).forEach(x=>{
        let o=document.createElement("option");
        o.text=x;j.add(o);
      });
    }loadJobs();
    </script>
    """,it=IT_JOBS,non=NON_IT_JOBS,quals=QUALS)

@app.route("/success")
def success():
    return "<h3>Application Submitted Successfully</h3>"

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method=="POST":
        if request.form["u"]=="admin" and request.form["p"]=="admin123":
            session["admin"]=True
            return redirect("/dashboard")
    return "<form method=post><input name=u><input type=password name=p><button>Login</button></form>"

# ---------------- DASHBOARD + CHART ----------------
@app.route("/dashboard")
def dash():
    if not session.get("admin"): return redirect("/admin")

    days={}
    revenue=0
    with open(APP_CSV) as f:
        for r in csv.DictReader(f):
            days[r["date"]] = days.get(r["date"],0)+1

    with open(PAY_CSV) as p:
        for r in csv.DictReader(p):
            revenue += int(r["amount"])

    return render_template_string("""
    <h2>Admin Dashboard</h2>
    Revenue: ₹{{rev}}<br><br>

    <canvas id="c" width="400" height="200"></canvas>
    <script>
    let d={{days|safe}};
    let ctx=document.getElementById("c").getContext("2d");
    let x=20;
    Object.keys(d).forEach(k=>{
      ctx.fillRect(x,180-d[k]*20,20,d[k]*20);
      ctx.fillText(k,x,195);
      x+=40;
    });
    </script>

    <h3>Company Subscriptions</h3>
    <form method="post" action="/subscribe">
    Company:<input name="c">
    <select name="p"><option>FREE</option><option>PRO</option></select>
    <button>Add</button>
    </form>
    """,days=days,rev=revenue)

# ---------------- SUBSCRIPTION ----------------
@app.route("/subscribe",methods=["POST"])
def sub():
    with open(SUB_CSV,"a",newline="") as s:
        csv.writer(s).writerow([
            request.form["c"],request.form["p"],datetime.date.today()
        ])
    if request.form["p"]=="PRO":
        with open(PAY_CSV,"a",newline="") as p:
            csv.writer(p).writerow([datetime.date.today(),5000])
    return redirect("/dashboard")

@app.route("/logout")
def lo():
    session.clear()
    return redirect("/admin")

# ---------------- RUN ----------------
app.run(host="0.0.0.0",port=10000)
