from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

DATABASE = []   # simple in-memory (now)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})


@app.post("/apply")
async def submit_apply(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    answer: str = Form(...),
    resume: UploadFile = File(...)
):
    result = "PASS" if len(answer) > 10 else "FAIL"

    DATABASE.append({
        "name": name,
        "phone": phone,
        "email": email,
        "experience": experience,
        "qualification": qualification,
        "role": role,
        "result": result
    })

    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.post("/admin")
def admin_auth(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin123":
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/admin", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "data": DATABASE}
    )
