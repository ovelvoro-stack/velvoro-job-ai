from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)

CSV_FILE = "applications.csv"


def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name", "Phone", "Email", "Experience",
                "Qualification", "Job Role",
                "Country", "State", "District", "Area",
                "AI Score", "Result", "Applied At"
            ])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        init_csv()

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
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data)

        return "✅ Application Submitted Successfully"

    return render_template("apply.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/dashboard")
def dashboard():
    init_csv()
    rows = []

    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    return render_template("dashboard.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
