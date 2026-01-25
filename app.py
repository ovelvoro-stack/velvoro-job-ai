from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# =========================
# ROOT – MAIN PAGE
# =========================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "apply.html",   # or home.html / index.html
        {"request": request}
    )


# =========================
# APPLY PAGE (explicit)
# =========================
@app.get("/apply", response_class=HTMLResponse)
async def apply(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {"request": request}
    )


# =========================
# API TEST (already working)
# =========================
@app.get("/health")
async def health():
    return {"status": "ok", "message": "Job AI running 🚀"}
