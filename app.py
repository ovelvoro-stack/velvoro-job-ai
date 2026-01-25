from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os, random, smtplib
from email.mime.text import MIMEText
import google.generativeai as genai

# ---------------- CONFIG ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = "data"
UPLOAD_DIR = "uploads"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

USERS = f"{DATA_DIR}/users.xlsx"
JOBS = f"{DATA_DIR}/jobs.xlsx"
APPS = f"{DATA_DIR}/applications.xlsx"

# ---------------- APP ----------------
app = FastAPI(title="Velvoro Job AI – Final")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OTP_STORE = {}

# ---------------- UTIL ----------------
def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()

def save_excel(file, row):
    if os.path.exists(file):
        df = pd.read_excel(file)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_excel(file, index=False)

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ---------------- LOGIN OTP ----------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/send-otp")
def send_otp(email: str = Form(...)):
    otp = random.randint(100000, 999999)
    OTP_STORE[email] = otp
    send_email(email, "Velvoro OTP Login", f"Your OTP is {otp}")
    return {"msg": "OTP sent"}

@app.post("/verify-otp")
def verify_otp(email: str = Form(...), otp: int = Form(...)):
    if OTP_STORE.get(email) == otp:
        save_excel(USERS, {"Email": email})
        return RedirectResponse("/apply", status_code=302)
    return {"error": "Invalid OTP"}

# ---------------- APPLY JOB ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_page(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/apply")
async def apply_job(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    experience: int = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    resume: UploadFile = File(...)
):
    path = f"{UPLOAD_DIR}/{resume.filename}"
    with open(path, "wb") as f:
        f.write(await resume.read())

    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
    Evaluate candidate for {role}
    Experience: {experience}
    Q1: {q1}
    Q2: {q2}
    Give score out of 100 and short verdict.
    """
    ai = model.generate_content(prompt).text

    save_excel(APPS, {
        "Name": name,
        "Email": email,
        "Role": role,
        "Experience": experience,
        "AI_Ranking": ai,
        "Resume": resume.filename
    })

    send_email(email, "Application Submitted", "Your profile is under AI evaluation.")
    return RedirectResponse("/", status_code=302)

# ---------------- ADMIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    data = []
    if os.path.exists(APPS):
        data = pd.read_excel(APPS).to_dict(orient="records")
    return templates.TemplateResponse("admin.html", {"request": request, "data": data})

# ---------------- COMPANY JOB POST ----------------
@app.get("/company", response_class=HTMLResponse)
def company_page(request: Request):
    return templates.TemplateResponse("company.html", {"request": request})

@app.post("/post-job")
def post_job(title: str = Form(...), paid: str = Form("FREE")):
    save_excel(JOBS, {"Job": title, "Plan": paid})
    return RedirectResponse("/company", status_code=302)
