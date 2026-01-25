from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from jinja2 import DictLoader
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="x")
templates.env.loader = DictLoader({

"apply.html": """
<!DOCTYPE html>
<html>
<head>
<title>AI Powered Job Application</title>
<style>
body { font-family: Arial; background:#f2f4f7 }
.container { width:80%; margin:auto; background:#fff; padding:20px }
h2 { background:#1f5ea8; color:white; padding:12px }
label { font-weight:bold }
input, select, textarea {
 width:100%; padding:8px; margin:6px 0
}
.section { margin-top:20px }
button {
 background:#1f5ea8; color:white;
 padding:12px 20px; border:none; font-size:16px
}
</style>
</head>

<body>
<div class="container">
<h2>AI Powered Job Application</h2>

<form method="post" action="/submit" enctype="multipart/form-data">

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
<select name="experience">
{% for i in range(0,21) %}
<option>{{i}}</option>
{% endfor %}
</select>

<label>Qualification</label>
<select name="qualification">
<option>Degree</option>
<option>Diploma</option>
<option>Intermediate</option>
<option>SSC</option>
</select>

<label>Job Role</label>
<select name="role">
<optgroup label="IT ROLES">
<option>Python Developer</option>
<option>Java Developer</option>
<option>Full Stack Developer</option>
<option>Frontend Developer</option>
<option>Backend Developer</option>
<option>DevOps Engineer</option>
<option>Cloud Engineer</option>
<option>Data Analyst</option>
<option>Data Scientist</option>
<option>AI / ML Engineer</option>
<option>QA / Tester</option>
<option>Automation Engineer</option>
<option>Cyber Security Analyst</option>
<option>System Administrator</option>
</optgroup>

<optgroup label="NON-IT ROLES">
<option>HR Executive</option>
<option>HR Manager</option>
<option>Recruiter</option>
</optgroup>
</select>
</div>

<div class="section">
<h3>Location Details</h3>

<label>Country</label>
<select name="country">
<option>India</option>
<option>United States</option>
<option>United Kingdom</option>
<option>Canada</option>
<option>Australia</option>
<option>UAE</option>
</select>

<label>State</label>
<select name="state">
<option>Andhra Pradesh</option>
<option>Telangana</option>
<option>Karnataka</option>
<option>Tamil Nadu</option>
<option>Maharashtra</option>
</select>

<label>District</label>
<select name="district">
<option>Hyderabad</option>
<option>Bengaluru</option>
<option>Chennai</option>
<option>Mumbai</option>
<option>Pune</option>
<option>Visakhapatnam</option>
<option>Vijayawada</option>
</select>

<label>Area</label>
<input name="area">
</div>

<div class="section">
<h3>Resume</h3>
<input type="file" name="resume">
</div>

<div class="section">
<h3>AI Professional Screening</h3>

<label>1. Explain your core skills related to the selected role</label>
<textarea name="q1" required></textarea>

<label>2. Describe a real-time problem you solved in your work</label>
<textarea name="q2" required></textarea>

<label>3. Why should Velvoro Software Solution hire you?</label>
<textarea name="q3" required></textarea>
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
<body style="font-family:Arial;background:#f2f4f7">
<div style="width:60%;margin:auto;background:white;padding:20px">
<h2>Application Submitted Successfully ✅</h2>
<p><b>Name:</b> {{name}}</p>
<p><b>Role:</b> {{role}}</p>
<p><b>Experience:</b> {{experience}} years</p>
<p><b>Status:</b> UNDER AI REVIEW 🔍</p>
</div>
</body>
</html>
"""
})

@app.get("/", response_class=HTMLResponse)
@app.get("/apply", response_class=HTMLResponse)
def apply(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: int = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...),
    resume: UploadFile = File(None)
):
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "name": name,
            "role": role,
            "experience": experience
        }
    )
