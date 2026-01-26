from flask import Flask, request, redirect, url_for, session, render_template_string
import csv, os, uuid

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

UPLOAD_FOLDER = "uploads"
DATA_FOLDER = "data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

APP_FILE = f"{DATA_FOLDER}/applications.csv"
QUIZ_FILE = f"{DATA_FOLDER}/company_quiz.csv"

# ---------- INIT CSV FILES ----------
if not os.path.exists(APP_FILE):
    with open(APP_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID","Name","Phone","Email","Category",
            "Experience","Company","Score","Resume"
        ])

if not os.path.exists(QUIZ_FILE):
    with open(QUIZ_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company","Question","Answer"])
        writer.writerow(["Velvoro","What is Python?","language"])
        writer.writerow(["Velvoro","HTML is used for?","web"])
        writer.writerow(["Velvoro","SQL is for?","database"])

# ---------- HOME / APPLY ----------
@app.route("/", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        uid = str(uuid.uuid4())[:8]

        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        category = request.form["category"]
        exp = request.form["experience"]
        company = request.form["company"]

        resume = request.files["resume"]
        resume_name = uid + "_" + resume.filename
        resume.save(os.path.join(UPLOAD_FOLDER, resume_name))

        session["app"] = {
            "id": uid, "name": name, "phone": phone,
            "email": email, "category": category,
            "exp": exp, "company": company,
            "resume": resume_name
        }
        return redirect("/quiz")

    return render_template_string(APPLY_HTML)

# ---------- QUIZ ----------
@app.route("/quiz", methods=["GET","POST"])
def quiz():
    app_data = session.get("app")
    if not app_data:
        return redirect("/")

    questions = []
    with open(QUIZ_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["Company"] == app_data["company"]:
                questions.append(r)

    if request.method == "POST":
        score = 0
        for i,q in enumerate(questions):
            if request.form.get(f"q{i}") == q["Answer"]:
                score += 1

        with open(APP_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                app_data["id"], app_data["name"],
                app_data["phone"], app_data["email"],
                app_data["category"], app_data["exp"],
                app_data["company"], score,
                app_data["resume"]
            ])
        session.clear()
        return render_template_string(SUCCESS_HTML, score=score)

    return render_template_string(QUIZ_HTML, questions=questions)

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True

    if not session.get("admin"):
        return render_template_string(ADMIN_LOGIN)

    rows = []
    with open(APP_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    return render_template_string(ADMIN_DASH, rows=rows)

# ---------- HTML TEMPLATES ----------

APPLY_HTML = """
<h2>Velvoro Job Application</h2>
<form method="post" enctype="multipart/form-data">
<input name="name" placeholder="Full Name" required><br>
<input name="phone" placeholder="Phone" required><br>
<input name="email" placeholder="Email" required><br>

<select name="category">
<option>IT</option>
<option>Non-IT</option>
</select><br>

<select name="experience">
{% for i in range(31) %}
<option>{{i}} Years</option>
{% endfor %}
</select><br>

<input name="company" value="Velvoro"><br>
<input type="file" name="resume" required><br>

<button>Apply Job</button>
</form>
"""

QUIZ_HTML = """
<h3>Quiz</h3>
<form method="post">
{% for q in questions %}
<p>{{q.Question}}</p>
<input name="q{{loop.index0}}"><br>
{% endfor %}
<button>Submit</button>
</form>
"""

SUCCESS_HTML = """
<h2>Application Submitted ✅</h2>
<p>Your Quiz Score: {{score}}</p>
"""

ADMIN_LOGIN = """
<h3>Admin Login</h3>
<form method="post">
<input type="password" name="password">
<button>Login</button>
</form>
"""

ADMIN_DASH = """
<h2>Admin Dashboard</h2>
<table border="1">
{% for r in rows %}
<tr>
{% for c in r %}
<td>{{c}}</td>
{% endfor %}
</tr>
{% endfor %}
</table>
"""

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
