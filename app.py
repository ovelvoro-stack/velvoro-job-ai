from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Velvoro Job AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

applications = []  # temp memory (next step DB)

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

# ---------------- APPLY ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {"request": request}
    )

@app.post("/apply")
async def submit_apply(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    resume: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    with open(file_path, "wb") as f:
        f.write(await resume.read())

    score = 80 if experience >= 2 else 40
    result = "PASS" if score >= 50 else "FAIL"

    applications.append({
        "name": name,
        "phone": phone,
        "email": email,
        "experience": experience,
        "qualification": qualification,
        "role": role,
        "score": score,
        "result": result
    })

    return RedirectResponse("/apply", status_code=303)

# ---------------- ADMIN LOGIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse(
        "admin.html",
        {"request": request}
    )

# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "apps": applications
        }
    )
