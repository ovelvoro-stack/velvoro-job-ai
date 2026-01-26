from flask import Blueprint, render_template, session, redirect
import csv

admin = Blueprint("admin", __name__)

@admin.route("/admin")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")

    rows = []
    with open("data/applications.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for r in reader:
            rows.append(r)

    return render_template("admin_dashboard.html", headers=headers, rows=rows)
