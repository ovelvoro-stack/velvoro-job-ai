from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
import os
from datetime import datetime

app = FastAPI(title="Velvoro Job AI")

EXCEL_FILE = "applications.xlsx"

# ---------------------------
# INIT EXCEL FILE
# ---------------------------
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "Name",
        "Phone",
        "Email",
        "Experience",
        "Qualification",
        "JobRole",
        "Skills",
        "AI_Score",
        "CreatedAt"
    ])
    df.to_excel(EXCEL_FILE, index=False)

# ---------------------------
# HEALTH CHECK (IMPORTANT)
# ---------------------------
@app.get("/")
def health():
    return {"status": "Velvoro Job AI is running 🚀"}

# ---------------------------
# 1️⃣ JOB APPLY API
# ---------------------------
@app.post("/job/apply")
async def apply_job(request: Request):
    data = await request.json()

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    experience = data.get("experience")
    qualification = data.get("qualification")
    jobrole = data.get("jobrole")
    skills = data.get("skills")

    # Simple AI scoring logic
    score = 0
    if experience:
        score += int(experience) * 10
    if skills:
        score += len(skills.split(",")) * 5

    new_row = {
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Experience": experience,
        "Qualification": qualification,
        "JobRole": jobrole,
        "Skills": skills,
        "AI_Score": score,
        "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    return {
        "message": "Application submitted successfully",
        "ai_score": score
    }

# ---------------------------
# 2️⃣ AI EVALUATION API
# ---------------------------
@app.post("/evaluate")
async def evaluate(data: dict):
    experience = data.get("experience", 0)
    skills = data.get("skills", "")

    score = int(experience) * 10 + len(skills.split(",")) * 5

    return {
        "ai_score": score,
        "status": "evaluated"
    }

# ---------------------------
# 3️⃣ ADMIN – VIEW ALL DATA
# ---------------------------
@app.get("/admin/applications")
def get_all_applications():
    df = pd.read_excel(EXCEL_FILE)
    return JSONResponse(content=df.to_dict(orient="records"))
