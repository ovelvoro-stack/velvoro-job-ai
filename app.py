from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# ---------------- CONFIG ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Velvoro Job AI")

UPLOAD_DIR = "uploads"
EXCEL_FILE = "applications.xlsx"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- AI LOGIC ----------------
def ai_evaluate(role, answers):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are an HR evaluator.
Job Role: {role}

Candidate Answers:
{answers}

Decide strictly:
Return only one word: QUALIFIED or NOT QUALIFIED
"""
        res = model.generate_content(prompt)
        text = res.text.upper()
        return "QUALIFIED" if "QUALIFIED" in text else "NOT QUALIFIED"
    except:
        return "NOT QUALIFIED"

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Velvoro Software Solution</h2>
    <h3>AI Powered Job Application</h3>
    <a href="/apply">Apply for Job</a><br><br>
    <a href="/docs">API Docs</a>
    """

# ---------------- APPLY FORM ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form():
    jobs_it = [
        "Python Developer","Java Developer","Full Stack Developer",
        "Frontend Developer","Backend Developer","DevOps Engineer",
        "Data Analyst","Data Scientist","AI/ML Engineer","QA Tester"
    ]
    jobs_non_it = ["HR Executive","HR Manager","Recruiter","Marketing","Sales"]

    job_options = "".join([f"<option>{j}</option>" for j in jobs_it + jobs_non_it])
    exp_options = "".join([f"<option>{i}</option>" for i in range(0,31)])

    return f"""
    <h2>AI Powered Job Application – Velvoro</h2>
    <form action="/submit" method="post" enctype="multipart/form-data">

    Full Name:<br><input name="name" required><br><br>
    Phone:<br><input name="phone" required><br><br>
    Email:<br><input name="email" required><br><br>

    Experience (Years):<br>
    <select name="experience">{exp_options}</select><br><br>

    Qualification:<br>
    <select name="qualification">
      <option>B.Tech</option>
      <option>MCA</option>
      <option>MBA</option>
      <option>B.Sc</option>
      <option>Diploma</option>
    </select><br><br>

    Job Role:<br>
    <select name="role">{job_options}</select><br><br>

    Country:<br><input name="country" value="India"><br><br>
    State:<br><input name="state"><br><br>
    District:<br><input name="district"><br><br>
    Area:<br><input name="area"><br><br>

    Resume:<br>
    <input type="file" name="resume" required><br><br>

    Q1: Explain your core skills:<br>
    <textarea name="q1" required></textarea><br><br>

    Q2: Describe a real-time problem you solved:<br>
    <textarea name="q2" required></textarea><br><br>

    Q3: Why should we hire you?:<br>
    <textarea name="q3" required></textarea><br><br>

    <button type="submit">Submit Application</button>
    </form>
    """

# ---------------- SUBMIT ----------------
@app.post("/submit", response_class=HTMLResponse)
async def submit(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: str = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...),
    resume: UploadFile = File(...)
):
    resume_path = f"{UPLOAD_DIR}/{datetime.now().timestamp()}_{resume.filename}"
    with open(resume_path, "wb") as f:
        f.write(await resume.read())

    answers = f"Q1:{q1}\nQ2:{q2}\nQ3:{q3}"
    result = ai_evaluate(role, answers)

    row = {
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Experience": experience,
        "Qualification": qualification,
        "Role": role,
        "Country": country,
        "State": state,
        "District": district,
        "Area": area,
        "AI Result": result,
        "Resume": resume_path
    }

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([row])])
    else:
        df = pd.DataFrame([row])

    df.to_excel(EXCEL_FILE, index=False)

    return f"""
    <h2>Application Submitted</h2>
    <b>Status:</b> {result}<br><br>
    <a href="/apply">Apply Another</a>
    """
