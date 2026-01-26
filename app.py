from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DATA_FILE = "data/applications.csv"

# Ensure data folder & file exist
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "name","phone","email","experience","qualification",
        "job_role","country","state","district","area",
        "ai_score","result"
    ])
    df.to_csv(DATA_FILE, index=False)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "phone": request.form["phone"],
            "email": request.form["email"],
            "experience": request.form["experience"],
            "qualification": request.form["qualification"],
            "job_role": request.form["job_role"],
            "country": request.form["country"],
            "state": request.form["state"],
            "district": request.form["district"],
            "area": request.form["area"],
            "ai_score": "Pending",
            "result": "Pending"
        }

        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        return "✅ Application Submitted Successfully"

    return render_template("apply.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Login"

    return render_template("admin_login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    df = pd.read_csv(DATA_FILE)
    return render_template("dashboard.html", tables=df.to_dict(orient="records"))


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
