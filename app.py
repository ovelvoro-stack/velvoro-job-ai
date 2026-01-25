from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from datetime import datetime

app = FastAPI()

EXCEL_FILE = "applications.xlsx"

# ----------------------------
# INIT EXCEL
# ----------------------------
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "Name", "Email", "Phone",
        "JobRole", "Experience",
        "Score", "CreatedAt"
    ])
    df.to_excel(EXCEL_FILE, index=False)


# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def root():
    return {"status": "Velvoro Job AI running 🚀"}


# ----------------------------
# REQUEST MODEL
# ----------------------------
class JobRequest(BaseModel):
    name: str
    email: str
    phone: str
    job_role: str
    experience: int


# ----------------------------
# JOB API
# ----------------------------
@app.post("/job")
def submit_job(data: JobRequest):

    score = evaluate_score(data.experience)

    new_row = {
        "Name": data.name,
        "Email": data.email,
        "Phone": data.phone,
        "JobRole": data.job_role,
        "Experience": data.experience,
        "Score": score,
        "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    return {
        "message": "Job application saved",
        "score": score
    }


# ----------------------------
# AI EVALUATION (simple logic)
# ----------------------------
def evaluate_score(experience: int):
    if experience >= 5:
        return 90
    elif experience >= 3:
        return 75
    elif experience >= 1:
        return 60
    else:
        return 40


# ----------------------------
# EVALUATE API
# ----------------------------
@app.get("/evaluate/{experience}")
def evaluate(experience: int):
    return {"score": evaluate_score(experience)}
