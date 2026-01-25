from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

app = FastAPI(title="Velvoro Job AI")

templates = Jinja2Templates(directory="templates")

DATA_FILE = "applications.xlsx"

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ---------------- APPLY FORM ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/apply")
def apply_submit(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    q1: str = Form(""),
    q2: str = Form(""),
    resume: UploadFile = File(None)
):
    data = {
        "Name": name,
        "Email": email,
        "Role": role,
        "Q1": q1,
        "Q2": q2,
        "Resume": resume.filename if resume else ""
    }

    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(DATA_FILE, index=False)

    return RedirectResponse("/apply", status_code=303)

# ---------------- ADMIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
        records = df.to_dict(orient="records")
    else:
        records = []

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "records": records}
    )
