from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

EXCEL_FILE = "data.xlsx"

# ---------- HOME ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

# ---------- APPLY FORM ----------
@app.post("/apply")
def apply(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...)
):
    # ----- AI SCORING (simple & safe) -----
    score = random.randint(40, 95)
    status = "QUALIFIED" if score >= 60 else "NOT QUALIFIED"

    data = {
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
        "Q1": q1,
        "Q2": q2,
        "Q3": q3,
        "Score": score,
        "Result": status
    }

    # ----- SAVE TO EXCEL -----
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([data])])
    else:
        df = pd.DataFrame([data])

    df.to_excel(EXCEL_FILE, index=False)

    return {
        "message": "Application Submitted",
        "score": score,
        "result": status
    }

# ---------- HEALTH CHECK ----------
@app.get("/health")
def health():
    return {"status": "OK"}
