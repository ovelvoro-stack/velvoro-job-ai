from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import DictLoader
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# HTML templates inline (one-file solution)
templates = Jinja2Templates(directory="not_used")
templates.env.loader = DictLoader({
    "apply.html": """
<!DOCTYPE html>
<html>
<head>
<title>AI Job Application</title>
<style>
body { font-family: Arial; background:#f4f6f8 }
.container { width:70%; margin:auto; background:white; padding:20px }
h2 { background:#1e73be; color:white; padding:10px }
input, select { width:100%; padding:8px; margin:6px 0 }
button { background:#1e73be; color:white; padding:10px; border:none }
</style>
</head>
<body>
<div class="container">
<h2>AI Powered Job Application</h2>
<form method="post" action="/submit">
<label>Full Name</label>
<input name="name" required>

<label>Phone</label>
<input name="phone" required>

<label>Email</label>
<input name="email" required>

<label>Total Experience (Years)</label>
<input name="experience" type="number" required>

<label>Qualification</label>
<input name="qualification" required>

<label>Role Applying For</label>
<input name="role" required>

<button type="submit">Submit Application</button>
</form>
</div>
</body>
</html>
""",
    "result.html": """
<!DOCTYPE html>
<html>
<head><title>Result</title></head>
<body style="font-family:Arial">
<h2>Application Submitted ✅</h2>
<p><b>Name:</b> {{name}}</p>
<p><b>Experience:</b> {{experience}} years</p>
<p><b>Status:</b> {{status}}</p>
<a href="/apply">Apply Again</a>
</body>
</html>
"""
})

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.get("/apply", response_class=HTMLResponse)
def apply(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
def submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    role: str = Form(...)
):
    status = "SELECTED ✅" if experience >= 1 else "REVIEW 🔍"
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "name": name,
            "experience": experience,
            "status": status
        }
    )

@app.get("/health")
def health():
    return {"status": "Job AI Running 🚀"}
