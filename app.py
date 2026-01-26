from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, shutil

app = FastAPI(title="Velvoro Job AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse("/apply")

# ---------------- APPLY FORM ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/apply")
async def submit_application(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    answer1: str = Form(...),
    answer2: str = Form(...),
    resume: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # SIMPLE AI LOGIC (PASS / FAIL)
    result = "PASS" if len(answer1) > 10 and len(answer2) > 10 else "FAIL"

    return {
        "status": "submitted",
        "result": result,
        "name": name,
        "role": role
    }

# ---------------- ADMIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
