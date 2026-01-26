import os
import pandas as pd
from flask import Flask, request, redirect, url_for, send_from_directory

from werkzeug.utils import secure_filename

# ===============================
# BASIC CONFIG
# ===============================
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DB_FILE = "velvoro_jobs.xlsx"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================
# EXCEL DATABASE INIT
# ===============================
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=[
        "Company",
        "Name", "Phone", "Email",
        "Category", "JobRole",
        "Country", "State", "District", "Area",
        "Resume",
        "AI_Score",
        "Status",
        "Plan"
    ])
    df.to_excel(DB_FILE, index=False)

# ===============================
# AI SCORING (SAFE STUB)
# ===============================
def ai_score_stub(resume_name, job_role):
    # Gemini API later plug here
    # This keeps app stable now
    return 75

# ===============================
# HOME – JOB APPLY
# ===============================
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        resume = request.files["resume"]
        filename = secure_filename(resume.filename)
        resume.save(os.path.join(UPLOAD_FOLDER, filename))

        df = pd.read_excel(DB_FILE)

        score = ai_score_stub(filename, request.form["jobrole"])

        row = {
            "Company": "Velvoro",
            "Name": request.form["name"],
            "Phone": request.form["phone"],
            "Email": request.form["email"],
            "Category": request.form["category"],
            "JobRole": request.form["jobrole"],
            "Country": request.form["country"],
            "State": request.form["state"],
            "District": request.form["district"],
            "Area": request.form["area"],
            "Resume": filename,
            "AI_Score": score,
            "Status": "New",
            "Plan": "Free"
        }

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_excel(DB_FILE, index=False)

        return "<h2>✅ Application Submitted Successfully</h2>"

    return """
    <h2>Velvoro Job AI</h2>
    <form method='POST' enctype='multipart/form-data'>
    <input name='name' placeholder='Name' required><br>
    <input name='phone' placeholder='Phone' required><br>
    <input name='email' placeholder='Email' required><br>
    <select name='category'><option>IT</option><option>Non-IT</option></select><br>
    <input name='jobrole' placeholder='Job Role' required><br>
    <input name='country' placeholder='Country'><br>
    <input name='state' placeholder='State'><br>
    <input name='district' placeholder='District'><br>
    <input name='area' placeholder='Area'><br>
    <input type='file' name='resume' required><br><br>
    <button>Apply</button>
    </form>
    <br><a href='/admin'>Admin Login</a>
    """

# ===============================
# ADMIN LOGIN (SIMPLE, SAFE)
# ===============================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            return redirect("/dashboard")
        return "Invalid password"

    return """
    <h3>Admin Login</h3>
    <form method='POST'>
    <input type='password' name='password'>
    <button>Login</button>
    </form>
    """

# ===============================
# ADMIN DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():
    df = pd.read_excel(DB_FILE)
    html = "<h2>Admin Dashboard</h2><table border=1>"
    html += "".join(f"<th>{c}</th>" for c in df.columns)
    for i, r in df.iterrows():
        html += "<tr>"
        for c in df.columns:
            html += f"<td>{r[c]}</td>"
        html += f"<td><a href='/resume/{r['Resume']}'>Resume</a></td>"
        html += "</tr>"
    html += "</table>"
    return html

# ===============================
# RESUME DOWNLOAD
# ===============================
@app.route("/resume/<filename>")
def resume(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
