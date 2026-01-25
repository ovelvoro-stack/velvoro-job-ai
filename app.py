from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
import google.generativeai as genai

# ---------------- CONFIG ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

UPLOAD_DIR = "uploads"
EXCEL_FILE = "applications.xlsx"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- APP ----------------
app = FastAPI(title="Velvoro Job AI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ---------------- APPLY JOB ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_page(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/apply")
async def apply_job(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    resume: UploadFile = File(...)
):
    resume_path = os.path.join(UPLOAD_DIR, resume.filename)
    with open(resume_path, "wb") as f:
        f.write(await resume.read())

    data = {
        "Name": name,
        "Email": email,
        "Role": role,
        "Experience": experience,
        "Qualification": qualification,
        "Q1": q1,
        "Q2": q2,
        "Resume": resume.filename
    }

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(EXCEL_FILE, index=False)

    return RedirectResponse("/", status_code=302)

# ---------------- ADMIN DASHBOARD ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        records = df.to_dict(orient="records")
    else:
        records = []

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "records": records}
    )
