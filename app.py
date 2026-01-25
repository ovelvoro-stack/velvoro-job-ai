# =========================
# Velvoro Job AI - A to Z
# =========================

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import pandas as pd
import os, shutil
import google.generativeai as genai

# -------------------------
# CONFIG
# -------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

UPLOAD_DIR = "uploads"
EXCEL_FILE = "applications.xlsx"
ADMIN_USER = "admin"
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Velvoro Job AI")

# -------------------------
# DATA
# -------------------------
EXPERIENCE = [f"{i} Years" for i in range(0, 31)]

QUALIFICATIONS = [
    "B.Tech", "MCA", "B.Pharmacy", "M.Pharmacy",
    "Diploma", "MBA", "B.Sc", "M.Sc", "Other"
]

JOB_ROLES = {
    "Python Developer": [
        "Explain list vs tuple",
        "What is virtualenv?",
        "Explain OOP"
    ],
    "Java Developer": [
        "What is JVM?",
        "Explain Spring Boot",
        "Difference between JDK & JRE"
    ],
    "HR": [
        "What is recruitment lifecycle?",
        "How do you handle conflict?",
        "What is employee engagement?"
    ],
    "Marketing": [
        "Explain digital marketing",
        "What is SEO?",
        "How do you generate leads?"
    ],
    "Pharmacy": [
        "What is bioavailability?",
        "Explain GMP",
        "Difference between B.Pharm & D.Pharm"
    ]
}

# -------------------------
# AI EVALUATION
# -------------------------
def ai_evaluate(role, answers):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
    Role: {role}
    Answers: {answers}

    Decide candidate is QUALIFIED or NOT QUALIFIED.
    Reply only one word.
    """
    res = model.generate_content(prompt)
    return res.text.strip()

# -------------------------
# APPLY PAGE
# -------------------------
@app.get("/apply", response_class=HTMLResponse)
def apply_page():
    return f"""
    <h2>AI Powered Job Application – Velvoro Software Solution</h2>
    <form method="post" enctype="multipart/form-data">
    
    Name: <input name="name"><br><br>
    Phone: <input name="phone"><br><br>
    Email: <input name="email"><br><br>

    Experience:
    <select name="experience">
        {''.join([f"<option>{e}</option>" for e in EXPERIENCE])}
    </select><br><br>

    Qualification:
    <select name="qualification">
        {''.join([f"<option>{q}</option>" for q in QUALIFICATIONS])}
    </select><br><br>

    Job Role:
    <select name="job_role">
        {''.join([f"<option>{r}</option>" for r in JOB_ROLES.keys()])}
    </select><br><br>

    Country: <input name="country"><br><br>
    State: <input name="state"><br><br>
    District: <input name="district"><br><br>
    Area: <input name="area"><br><br>

    Resume: <input type="file" name="resume"><br><br>

    Q1: <textarea name="q1"></textarea><br>
    Q2: <textarea name="q2"></textarea><br>
    Q3: <textarea name="q3"></textarea><br><br>

    <button type="submit">Apply</button>
    </form>
    """

# -------------------------
# APPLY SUBMIT
# -------------------------
@app.post("/apply")
def apply_submit(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: str = Form(...),
    qualification: str = Form(...),
    job_role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...),
    resume: UploadFile = File(...)
):
    resume_path = f"{UPLOAD_DIR}/{resume.filename}"
    with open(resume_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    answers = f"{q1} | {q2} | {q3}"
    result = ai_evaluate(job_role, answers)

    data = {
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Experience": experience,
        "Qualification": qualification,
        "Job Role": job_role,
        "Country": country,
        "State": state,
        "District": district,
        "Area": area,
        "AI Result": result,
        "Resume": resume.filename
    }

    df = pd.DataFrame([data])
    if os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, index=False, mode="a", header=False)
    else:
        df.to_excel(EXCEL_FILE, index=False)

    return {
        "status": "Application Submitted",
        "AI_Result": result
    }

# -------------------------
# ADMIN LOGIN
# -------------------------
@app.get("/admin", response_class=HTMLResponse)
def admin_login():
    return """
    <h2>Admin Login</h2>
    <form method="post">
    Username: <input name="username"><br>
    Password: <input name="password"><br>
    <button>Login</button>
    </form>
    """

@app.post("/admin")
def admin_auth(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return RedirectResponse("/admin/dashboard", status_code=302)
    return {"error": "Invalid Login"}

# -------------------------
# ADMIN DASHBOARD
# -------------------------
@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard():
    if not os.path.exists(EXCEL_FILE):
        return "No Applications Yet"

    df = pd.read_excel(EXCEL_FILE)
    return df.to_html()

# -------------------------
# ROOT
# -------------------------
@app.get("/")
def root():
    return {"message": "Velvoro Job AI Running"}
