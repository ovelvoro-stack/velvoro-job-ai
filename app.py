from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
import shutil

app = FastAPI(title="Velvoro Job AI")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
DATA_DIR = "data"
EXCEL_FILE = f"{DATA_DIR}/applications.xlsx"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ---------------- APPLY FORM ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

# ---------------- APPLY SUBMIT ----------------
@app.post("/apply")
async def submit_application(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    resume: UploadFile = File(...)
):
    resume_path = f"{UPLOAD_DIR}/{resume.filename}"
    with open(resume_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    row = {
        "Name": name,
        "Email": email,
        "Role": role,
        "Q1": q1,
        "Q2": q2,
        "Resume": resume.filename
    }

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_excel(EXCEL_FILE, index=False)

    return RedirectResponse("/apply", status_code=302)

# ---------------- ADMIN DASHBOARD ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        records = df.to_dict(orient="records")
    else:
        records = []

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "records": records}
    )
