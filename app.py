from fastapi import FastAPI, Request, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

EXCEL_FILE = "data.xlsx"

if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "Name","Phone","Email","Experience","Qualification",
        "Category","Role","Coaching",
        "Country","State","District","Area",
        "AI Score","Result"
    ])
    df.to_excel(EXCEL_FILE, index=False)

@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
def submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    category: str = Form(...),
    role: str = Form(...),
    coaching: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    skills: str = Form(...),
    problem: str = Form(...)
):
    score = experience * 5
    score += len(skills) // 20
    score += len(problem) // 20

    result = "QUALIFIED" if score >= 60 else "NOT QUALIFIED"

    df = pd.read_excel(EXCEL_FILE)
    df.loc[len(df)] = [
        name, phone, email, experience, qualification,
        category, role, coaching,
        country, state, district, area,
        score, result
    ]
    df.to_excel(EXCEL_FILE, index=False)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "score": score,
        "result": result
    })

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    df = pd.read_excel(EXCEL_FILE)
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "rows": df.to_dict(orient="records")
    })
