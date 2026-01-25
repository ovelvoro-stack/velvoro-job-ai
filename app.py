from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

EXCEL_FILE = "applications.xlsx"

# -------------------------------
# INIT EXCEL FILE
# -------------------------------
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "Name", "Phone", "Email",
        "Experience", "Qualification",
        "JobRole",
        "Country", "State", "District", "Area",
        "Q1", "Q2", "Q3",
        "Score", "Result",
        "AppliedAt"
    ])
    df.to_excel(EXCEL_FILE, index=False)


# -------------------------------
# HOME
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {
            "request": request,
            "company": "Velvoro Software Solution",
            "job_roles": JOB_ROLES,
            "countries": list(LOCATIONS.keys())
        }
    )


# -------------------------------
# APPLY PAGE
# -------------------------------
@app.get("/apply", response_class=HTMLResponse)
def apply_page(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {
            "request": request,
            "company": "Velvoro Software Solution",
            "job_roles": JOB_ROLES,
            "countries": list(LOCATIONS.keys())
        }
    )


# -------------------------------
# APPLY SUBMIT
# -------------------------------
@app.post("/apply", response_class=HTMLResponse)
def apply_submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    job_role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...)
):
    # ---------------- AI EVALUATION ----------------
    score = evaluate_answers(q1, q2, q3)
    result = "PASS" if score >= 60 else "FAIL"

    # ---------------- SAVE TO EXCEL ----------------
    df = pd.read_excel(EXCEL_FILE)
    df.loc[len(df)] = [
        name, phone, email,
        experience, qualification,
        job_role,
        country, state, district, area,
        q1, q2, q3,
        score, result,
        datetime.now()
    ]
    df.to_excel(EXCEL_FILE, index=False)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "name": name,
            "score": score,
            "result": result
        }
    )


# -------------------------------
# SIMPLE REAL AI (LOGIC BASED)
# -------------------------------
def evaluate_answers(a1, a2, a3):
    score = 0
    for ans in [a1, a2, a3]:
        if len(ans.strip()) > 30:
            score += 35
        elif len(ans.strip()) > 15:
            score += 25
        else:
            score += 10
    return min(score, 100)


# -------------------------------
# JOB ROLES (IT + NON-IT)
# -------------------------------
JOB_ROLES = {
    "IT": [
        "Python Developer",
        "Java Developer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Data Analyst",
        "Data Scientist",
        "DevOps Engineer",
        "AI Engineer",
        "QA Engineer"
    ],
    "NON_IT": [
        "HR Executive",
        "HR Manager",
        "Sales Executive",
        "Marketing Executive",
        "Marketing Manager",
        "Team Leader",
        "Business Development Executive",
        "Customer Support"
    ]
}


# -------------------------------
# LOCATION DATA (COUNTRY → STATE → DISTRICT)
# -------------------------------
LOCATIONS = {
    "India": {
        "Telangana": ["Hyderabad", "Warangal"],
        "Andhra Pradesh": ["Nellore", "Vijayawada"],
        "Karnataka": ["Bangalore", "Mysore"]
    },
    "USA": {
        "California": ["Los Angeles", "San Francisco"],
        "Texas": ["Dallas", "Austin"]
    },
    "UAE": {
        "Dubai": ["Deira", "Marina"],
        "Abu Dhabi": ["Yas Island"]
    }
}


# -------------------------------
# API FOR DROPDOWNS (AJAX)
# -------------------------------
@app.get("/api/states/{country}")
def get_states(country: str):
    return list(LOCATIONS.get(country, {}).keys())


@app.get("/api/districts/{country}/{state}")
def get_districts(country: str, state: str):
    return LOCATIONS.get(country, {}).get(state, [])


# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/health")
def health():
    return {"status": "Velvoro JobAI Running"}
