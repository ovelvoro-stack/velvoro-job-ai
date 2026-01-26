import os, csv, datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# ---------- BASIC CONFIG ----------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "velvoro-secret")

DATA_DIR = "data"
APP_FILE = f"{DATA_DIR}/applications.csv"
PAY_FILE = f"{DATA_DIR}/payments.csv"

os.makedirs(DATA_DIR, exist_ok=True)

# ---------- INIT CSV ----------
def init_csv(path, headers):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

init_csv(APP_FILE, [
    "date","name","phone","email","category","experience","company","score"
])

init_csv(PAY_FILE, [
    "date","company","amount"
])

# ---------- SAFE AI SCORING ----------
def resume_score_dummy(text):
    # SAFE fallback – always works
    return min(95, max(60, len(text) % 100))

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        data = [
            datetime.date.today().isoformat(),
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["category"],
            request.form["experience"],
            request.form["company"],
            resume_score_dummy(request.form["name"])
        ]
        with open(APP_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(data)

        return redirect(url_for("success"))
    return render_template("apply.html")

@app.route("/success")
def success():
    return render_template("success.html")

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["password"] == os.environ.get("ADMIN_PASSWORD","admin123"):
            session["admin"] = True
            return redirect(url_for("dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    rows = []
    with open(APP_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return render_template("admin_dashboard.html", rows=rows)

# ---------- REVENUE ----------
@app.route("/admin/revenue")
def revenue():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    revenue = {}
    with open(PAY_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            revenue[r["date"]] = revenue.get(r["date"],0) + int(r["amount"])

    return render_template(
        "admin_revenue.html",
        dates=list(revenue.keys()),
        amounts=list(revenue.values())
    )

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
