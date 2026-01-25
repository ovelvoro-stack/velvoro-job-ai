from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
from datetime import datetime

app = FastAPI(title="Velvoro Job Portal")

# folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

EXCEL_FILE = "data/applications.xlsx"

# static & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# ---------------- APPLY PAGE ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_page(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})


# ---------------- SUBMIT FORM ----------------
@app.post("/submit")
async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    experience: str = Form(...),
    qualification: str = Form(...),
    job_role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    resume: UploadFile = File(...)
):
    resume_path = f"uploads/{datetime.now().timestamp()}_{resume.filename}"
    with open(resume_path, "wb") as f:
        f.write(await resume.read())

    data = {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Experience": experience,
        "Qualification": qualification,
        "Job Role": job_role,
        "Country": country,
        "State": state,
        "District": district,
        "Area": area,
        "Resume": resume_path,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    df = pd.DataFrame([data])
    if os.path.exists(EXCEL_FILE):
        old = pd.read_excel(EXCEL_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_excel(EXCEL_FILE, index=False)

    return RedirectResponse("/apply", status_code=303)


# ---------------- ADMIN ----------------
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
