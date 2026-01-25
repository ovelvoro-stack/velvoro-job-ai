from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Application, Admin
from auth import hash_password, verify_password

app = FastAPI(title="Velvoro Job AI")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ---------------- APPLY ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/apply")
def submit_apply(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    db: Session = Depends(get_db)
):
    app_data = Application(
        name=name, email=email, role=role, q1=q1, q2=q2
    )
    db.add(app_data)
    db.commit()
    return RedirectResponse("/apply", status_code=302)

# ---------------- ADMIN LOGIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin")
def admin_auth(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin and verify_password(password, admin.password):
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/admin", status_code=302)

# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    apps = db.query(Application).all()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "applications": apps}
    )
