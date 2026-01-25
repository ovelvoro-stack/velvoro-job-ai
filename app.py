from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn, os
import pandas as pd
import google.generativeai as genai

# ---------------- CONFIG ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Velvoro Job AI")

UPLOAD_DIR = "uploads"
EXCEL_FILE = "applications.xlsx"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- AI LOGIC ----------------
def ai_evaluate(role, answers):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
    Evaluate candidate for role: {role}
    Answers: {answers}
    Decide QUALIFIED or NOT QUALIFIED.
    """
    res = model.generate_content(prompt)
    text = res.text.lower()
    return "QUALIFIED" if "qualified" in text else "NOT QUALIFIED"

# ---------------- HOME / APPLY ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_page():
    return """
<!DOCTYPE html>
<html>
<head>
<title>AI Powered Job Application - Velvoro</title>
<style>
body{font-family:Arial;background:#f5f5f5}
.container{width:700px;margin:auto;background:#fff;padding:20px}
h2{background:#0a3d62;color:#fff;padding:10px}
input,select,textarea{width:100%;padding:8px;margin:6px 0}
button{padding:10px;background:#0a3d62;color:#fff;border:none}
</style>
</head>
<body>
<div class="container">
<h2>AI Powered Job Application – Velvoro Software Solution</h2>

<form action="/submit" method="post" enctype="multipart/form-data">
<input name="name" placeholder="Full Name" required>
<input name="phone" placeholder="Phone Number" required>
<input name="email" placeholder="Email" required>

<select name="experience">
""" + "".join([f"<option>{i}</option>" for i in range(0,31)]) + """
</select>

<select name="qualification">
<option>B.Tech</option><option>MCA</option><option>BCA</option>
<option>M.Tech</option><option>Degree</option><option>Diploma</option>
</select>

<select name="role">
<option>Python Developer</option>
<option>Java Developer</option>
<option>HR</option>
<option>Marketing</option>
<option>Non IT</option>
</select>

<select name="country">
<option>India</option><option>USA</option><option>UK</option>
<option>Canada</option><option>Australia</option>
</select>

<input name="state" placeholder="State">
<input name="district" placeholder="District">
<input name="area" placeholder="Area / Locality">

<h3>AI Screening Questions</h3>
<textarea name="answers" placeholder="Answer the questions here..." required></textarea>

<label>Upload Resume</label>
<input type="file" name="resume" required>

<button type="submit">Submit Application</button>
</form>
</div>
</body>
</html>
"""

# ---------------- SUBMIT ----------------
@app.post("/submit")
async def submit(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    experience: str = Form(...),
    qualification: str = Form(...),
    role: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    area: str = Form(...),
    answers: str = Form(...),
    resume: UploadFile = File(...)
):
    resume_path = f"{UPLOAD_DIR}/{resume.filename}"
    with open(resume_path, "wb") as f:
        f.write(await resume.read())

    result = ai_evaluate(role, answers)

    row = {
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Experience": experience,
        "Qualification": qualification,
        "Role": role,
        "Country": country,
        "State": state,
        "District": district,
        "Area": area,
        "AI Result": result,
        "Resume": resume.filename
    }

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = df.append(row, ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_excel(EXCEL_FILE, index=False)

    return JSONResponse({
        "status": "submitted",
        "result": result
    })

# ---------------- ADMIN ----------------
@app.get("/admin")
def admin():
    if not os.path.exists(EXCEL_FILE):
        return {"message": "No applications yet"}
    df = pd.read_excel(EXCEL_FILE)
    return df.to_dict(orient="records")

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
