from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os, shutil
from database import SessionLocal
from models import Application
from auth import verify_admin

app = FastAPI(title="Velvoro AI Powered Job Application")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/apply")
def submit_apply(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    job_category: str = Form(...),
    job_role: str = Form(...),
    answer: str = Form(...),
    resume: UploadFile = File(...)
):
    # Simple AI validation
    if len(answer.strip()) < 10:
        return {"status": "FAIL", "message": "You are not eligible"}

    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    db = SessionLocal()
    app_data = Application(
        name=name,
        phone=phone,
        email=email,
        country=country,
        state=state,
        district=district,
        area=area,
        experience=experience,
        qualification=qualification,
        job_category=job_category,
        job_role=job_role,
        resume=file_path,
        result="PASS"
    )
    db.add(app_data)
    db.commit()
    db.close()

    return {"status": "SUCCESS", "message": "Application Submitted"}

@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin")
def admin_auth(username: str = Form(...), password: str = Form(...)):
    if verify_admin(username, password):
        return RedirectResponse("/dashboard", status_code=302)
    return {"error": "Invalid credentials"}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    apps = db.query(Application).all()
    db.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "apps": apps})
