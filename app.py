from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "velvoro-secret-key"

DATA_FILE = "velvoro_candidates.xlsx"

# ---------- Helpers ----------
def init_excel():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Name","Phone","Email","Experience","Qualification",
            "Job Role","Country","State","District","Area",
            "AI Score","Result","Applied At"
        ])
        df.to_excel(DATA_FILE, index=False)

def save_candidate(data):
    init_excel()
    df = pd.read_excel(DATA_FILE)
    df.loc[len(df)] = data
    df.to_excel(DATA_FILE, index=False)

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/apply", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        data = [
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["experience"],
            request.form["qualification"],
            request.form["job_role"],
            request.form["country"],
            request.form["state"],
            request.form["district"],
            request.form["area"],
            "Pending",
            "Pending",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ]
        save_candidate(data)
        return redirect(url_for("apply_success"))
    return render_template("apply.html")

@app.route("/apply-success")
def apply_success():
    return "<h2>Application Submitted Successfully</h2>"

@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect(url_for("dashboard"))
    return render_template("admin_login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    init_excel()
    df = pd.read_excel(DATA_FILE)
    return render_template("admin_dashboard.html", rows=df.values)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
