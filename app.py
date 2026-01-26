import csv, os
from flask import Flask, request, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = "velvoro_saas_secret"

os.makedirs("data", exist_ok=True)

COMPANIES = "data/companies.csv"
JOBS = "data/jobs.csv"
APPS = "data/applications.csv"

# ---------------- INIT FILES ----------------
def init_file(path, header):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header)

init_file(COMPANIES, ["company_id","company_name","email","password"])
init_file(JOBS, ["job_id","company_id","job_title","job_type","paid"])
init_file(APPS, ["name","email","company","job","score"])

# ---------------- HELPERS ----------------
def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ---------------- COMPANY LOGIN ----------------
@app.route("/company/login", methods=["GET","POST"])
def company_login():
    if request.method == "POST":
        for c in read_csv(COMPANIES):
            if c["email"] == request.form["email"] and c["password"] == request.form["password"]:
                session["company"] = c
                return redirect("/company/dashboard")
    return """
    <h3>Company Login</h3>
    <form method="post">
    <input name="email"><br>
    <input name="password" type="password"><br>
    <button>Login</button>
    </form>
    """

# ---------------- COMPANY DASHBOARD ----------------
@app.route("/company/dashboard", methods=["GET","POST"])
def company_dash():
    if "company" not in session:
        return redirect("/company/login")

    company = session["company"]

    if request.method == "POST":
        with open(JOBS,"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow([
                "J"+str(len(read_csv(JOBS))+1),
                company["company_id"],
                request.form["title"],
                request.form["type"],
                request.form["paid"]
            ])

    jobs = [j for j in read_csv(JOBS) if j["company_id"] == company["company_id"]]

    return render_template_string("""
    <h2>{{company.company_name}}</h2>

    <form method="post">
    Job Title: <input name="title"><br>
    Type:
    <select name="type">
        <option>IT</option>
        <option>Non-IT</option>
    </select><br>
    Paid:
    <select name="paid">
        <option>YES</option>
        <option>NO</option>
    </select><br>
    <button>Add Job</button>
    </form>

    <hr>
    <h3>Your Jobs</h3>
    {% for j in jobs %}
        <p>{{j.job_title}} | {{j.job_type}} | Paid: {{j.paid}}</p>
    {% endfor %}
    """, company=company, jobs=jobs)

# ---------------- PUBLIC JOB LIST ----------------
@app.route("/", methods=["GET","POST"])
def public_jobs():
    jobs = read_csv(JOBS)
    companies = {c["company_id"]:c["company_name"] for c in read_csv(COMPANIES)}

    if request.method == "POST":
        score = 50  # simple base score
        with open(APPS,"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow([
                request.form["name"],
                request.form["email"],
                companies[request.form["company"]],
                request.form["job"],
                score
            ])
        return "<h2>Application Submitted</h2>"

    return render_template_string("""
    <h2>Velvoro Multi-Company Jobs</h2>
    <form method="post">
    Name: <input name="name"><br>
    Email: <input name="email"><br>

    Company:
    <select name="company">
        {% for c in companies %}
            <option value="{{c}}">{{companies[c]}}</option>
        {% endfor %}
    </select><br>

    Job:
    <select name="job">
        {% for j in jobs %}
            <option>{{j.job_title}} ({{companies[j.company_id]}})</option>
        {% endfor %}
    </select><br>

    <button>Apply</button>
    </form>
    """, jobs=jobs, companies=companies)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
