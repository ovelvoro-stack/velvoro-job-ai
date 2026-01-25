from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Velvoro Job AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

# ---------------- APPLY FORM ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {"request": request}
    )

@app.post("/apply")
async def apply_submit(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    resume: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    with open(file_path, "wb") as f:
        f.write(await resume.read())

    return RedirectResponse(url="/", status_code=302)

# ---------------- ADMIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "files": files}
    )
