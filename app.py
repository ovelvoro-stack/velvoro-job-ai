from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import os, time
import google.generativeai as genai

# ================= CONFIG =================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI(title="Velvoro Job AI Platform")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

APP_FILE = "applications.xlsx"
JOB_FILE = "jobs.xlsx"

# ================= MASTER DATA =================
IT_JOBS = [
 "Python Developer","Java Developer","Full Stack Developer",
 "Frontend Developer","Backend Developer","DevOps Engineer",
 "Cloud Engineer","AI / ML Engineer","Data Scientist",
 "Data Analyst","QA Tester","Automation Engineer",
 "Cyber Security Analyst","System Administrator"
]

NON_IT_JOBS = [
 "HR Executive","HR Manager","Recruiter",
 "Marketing Executive","Sales Executive",
 "Business Development Executive",
 "Operations Manager","Accountant","Office Admin"
]

PHARMA_JOBS = [
 "Pharmacist","Clinical Research Associate",
 "Medical Coding Executive","Drug Safety Associate",
 "Pharma Sales Executive","Quality Control Analyst",
 "Quality Assurance Analyst","Production Chemist",
 "Regulatory Affairs Executive"
]

QUALIFICATIONS = [
 "B.Tech","M.Tech","B.Sc","M.Sc","MCA","MBA",
 "B.Pharmacy","M.Pharmacy","Diploma","Intermediate"
]

# ================= AI LOGIC =================
def ai_evaluate(role, answers):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are a strict job evaluator.

Job Role: {role}

Candidate Answers:
{answers}

Rules:
- If answers are relevant → QUALIFIED
- If weak or irrelevant → NOT QUALIFIED
Return only one word.
"""
        res = model.generate_content(prompt)
        return "QUALIFIED" if "QUALIFIED" in res.text.upper() else "NOT QUALIFIED"
    except:
        return "NOT QUALIFIED"

# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Velvoro Software Solution</h1>
    <h3>AI Powered Job Platform</h3>
    <ul>
      <li><a href="/apply">Job Apply</a></li>
      <li><a href="/company">Company Post Job</a></li>
      <li><a href="/admin">Admin Dashboard</a></li>
      <li><a href="/docs">API Docs (Android)</a></li>
    </ul>
    """

# ================= APPLY PAGE =================
@app.get("/apply", response_class=HTMLResponse)
def apply():
    jobs = IT_JOBS + NON_IT_JOBS + PHARMA_JOBS
    job_options = "".join(f"<option>{j}</option>" for j in jobs)
    exp_options = "".join(f"<option>{i}</option>" for i in range(31))
    qual_options = "".join(f"<option>{q}</option>" for q in QUALIFICATIONS)

    return f"""
    <h2>Job Application – Velvoro</h2>
    <form action="/submit" method="post" enctype="multipart/form-data">
    Name:<input name="name" required><br><br>
    Phone:<input name="phone" required><br><br>
    Email:<input name="email" required><br><br>

    Experience:
    <select name="experience">{exp_options}</select><br><br>

    Qualification:
    <select name="qualification">{qual_options}</select><br><br>

    Job Role:
    <select name="role">{job_options}</select><br><br>

    Country:<input name="country"><br><br>
    State:<input name="state"><br><br>
    District:<input name="district"><br><br>
    Area:<input name="area"><br><br>

    Resume:<input type="file" name="resume" required><br><br>

    Q1:<textarea name="q1"></textarea><br>
    Q2:<textarea name="q2"></textarea><br>
    Q3:<textarea name="q3"></textarea><br><br>

    <button>Submit</button>
    </form>
    """

# ================= SUBMIT =================
@app.post("/submit", response_class=HTMLResponse)
async def submit(
 name:str=Form(...), phone:str=Form(...), email:str=Form(...),
 experience:str=Form(...), qualification:str=Form(...), role:str=Form(...),
 country:str=Form(...), state:str=Form(...), district:str=Form(...),
 area:str=Form(...), q1:str=Form(...), q2:str=Form(...), q3:str=Form(...),
 resume:UploadFile=File(...)
):
    path = f"{UPLOAD_DIR}/{int(time.time())}_{resume.filename}"
    with open(path,"wb") as f:
        f.write(await resume.read())

    answers = f"{q1}\n{q2}\n{q3}"
    result = ai_evaluate(role, answers)

    data = {
      "Name":name,"Phone":phone,"Email":email,
      "Experience":experience,"Qualification":qualification,
      "Role":role,"Country":country,"State":state,
      "District":district,"Area":area,
      "AI Result":result,"Resume":path
    }

    df = pd.DataFrame([data])
    if os.path.exists(APP_FILE):
        old = pd.read_excel(APP_FILE)
        df = pd.concat([old, df])

    df.to_excel(APP_FILE, index=False)

    return f"<h2>Submitted</h2>Status: {result}<br><a href='/'>Home</a>"

# ================= COMPANY JOB POST =================
@app.get("/company", response_class=HTMLResponse)
def company():
    return """
    <h2>Company Job Posting</h2>
    <form action="/post-job" method="post">
    Company Name:<input name="company"><br>
    Job Role:<input name="role"><br>
    Job Type:<input name="type"><br>
    Location:<input name="location"><br>
    <button>Post Job</button>
    </form>
    """

@app.post("/post-job")
def post_job(company:str=Form(...), role:str=Form(...),
             type:str=Form(...), location:str=Form(...)):
    job = {"Company":company,"Role":role,"Type":type,"Location":location}
    df = pd.DataFrame([job])
    if os.path.exists(JOB_FILE):
        df = pd.concat([pd.read_excel(JOB_FILE), df])
    df.to_excel(JOB_FILE, index=False)
    return {"status":"Job Posted"}

# ================= ADMIN DASHBOARD =================
@app.get("/admin", response_class=HTMLResponse)
def admin():
    apps = pd.read_excel(APP_FILE).to_html() if os.path.exists(APP_FILE) else "No data"
    jobs = pd.read_excel(JOB_FILE).to_html() if os.path.exists(JOB_FILE) else "No jobs"
    return f"<h2>Admin</h2><h3>Applications</h3>{apps}<h3>Jobs</h3>{jobs}"

# ================= ANDROID APIs =================
@app.get("/api/jobs")
def api_jobs():
    if os.path.exists(JOB_FILE):
        return pd.read_excel(JOB_FILE).to_dict(orient="records")
    return []

@app.get("/api/applications")
def api_apps():
    if os.path.exists(APP_FILE):
        return pd.read_excel(APP_FILE).to_dict(orient="records")
    return []

# ================= PAYMENT PLACEHOLDER =================
@app.get("/payment-info")
def payment():
    return {"message":"Payments will be enabled later"}
