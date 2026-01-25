from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from jinja2 import DictLoader
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="not_used")
templates.env.loader = DictLoader({

"apply.html": """
<!DOCTYPE html>
<html>
<head>
<title>AI Powered Job Application</title>
<style>
body { font-family: Arial; background:#f2f4f7 }
.container { width:75%; margin:auto; background:#fff; padding:20px }
h2 { background:#1f5ea8; color:white; padding:12px }
label { font-weight:bold }
input, select { width:100%; padding:8px; margin:6px 0 }
.section { margin-top:20px }
button { background:#1f5ea8; color:white; padding:12px; border:none; font-size:16px }
</style>
</head>
<body>

<div class="container">
<h2>AI Powered Job Application</h2>

<form method="post" action="/submit">

<div class="section">
<label>Full Name</label>
<input name="name" required>

<label>Phone Number</label>
<input name="phone" required>

<label>Email ID</label>
<input name="email" required>
</div>

<div class="section">
<h3>Professional Details</h3>

<label>Total Experience (Years)</label>
<input name="experience" type="number" value="0">

<label>Qualification</label>
<select name="qualification">
<option>Degree</option>
<option>Diploma</option>
<option>Intermediate</option>
<option>SSC</option>
</select>

<label>Job Role</label>
<select name="role">
<option>Software Developer</option>
<option>Tester</option>
<option>HR</option>
<option>Data Analyst</option>
</select>
</div>

<div class="section">
<h3>Location Details</h3>

<label>Country</label>
<input name="country" value="India">

<label>State</label>
<input name="state" value="Andhra Pradesh">

<label>District</label>
<input name="district">
</div>

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
<body style="font-family:Arial; background:#f2f4f7">
<div style="width:60%; margin:auto; background:white; padding:20px">
<h2>Application Result</h2>
<p><b>Name:</b> {{name}}</p>
<p><b>Experience:</b> {{experience}} years</p>
<p><b>Role:</b> {{role}}</p>
<p><b>Status:</b> {{status}}</p>
<a href="/apply">Apply Again</a>
</div>
</body>
</html>
"""
})

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
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
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...)
):
    status = "SELECTED ✅" if experience >= 1 else "UNDER REVIEW 🔍"
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "name": name,
            "experience": experience,
            "role": role,
            "status": status
        }
    )

@app.get("/health")
def health():
    return {"status": "AI Job Application Running 🚀"}
