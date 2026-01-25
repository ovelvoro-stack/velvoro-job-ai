from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import google.generativeai as genai

# ================= CONFIG =================
genai.configure(api_key="PASTE_YOUR_GEMINI_API_KEY")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

EXCEL_FILE = "data.xlsx"

# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

# ================= APPLY =================
@app.post("/submit")
def submit(
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
    q3: str = Form(...),
    resume: UploadFile = File(...)
):
    # ===== AI EVALUATION =====
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    Job Role: {job_role}
    Q1 Answer: {q1}
    Q2 Answer: {q2}
    Q3 Answer: {q3}

    Evaluate and give score out of 100.
    Say Qualified or Not Qualified.
    """

    response = model.generate_content(prompt)
    ai_result = response.text

    # ===== SAVE TO EXCEL =====
    data = {
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Experience": experience,
        "Qualification": qualification,
        "Job Role": job_role,
        "Country": country,
        "State": state,
        "District": district,
        "Area": area,
        "AI Result": ai_result
    }

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([data])])
    else:
        df = pd.DataFrame([data])

    df.to_excel(EXCEL_FILE, index=False)

    return {
        "status": "Application Submitted",
        "ai_result": ai_result
    }

# ================= ADMIN =================
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        data = df.to_dict(orient="records")
    else:
        data = []

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "data": data
    })
