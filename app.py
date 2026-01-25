from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# -------------------------
# SAFETY CHECK (Railway fix)
# -------------------------
if not os.path.isdir("templates"):
    raise RuntimeError("templates folder not found")

if not os.path.isdir("static"):
    os.makedirs("static")

# -------------------------
# STATIC & TEMPLATES
# -------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# -------------------------
# ROOT
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {"request": request}
    )


# -------------------------
# APPLY PAGE
# -------------------------
@app.get("/apply", response_class=HTMLResponse)
async def apply(request: Request):
    return templates.TemplateResponse(
        "apply.html",
        {"request": request}
    )


# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "Job AI is running 🚀"
