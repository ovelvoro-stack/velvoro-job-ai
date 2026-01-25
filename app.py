from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd, os, time
from passlib.hash import bcrypt
import google.generativeai as genai

# ================= CONFIG =================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI(title="Velvoro Job AI Platform")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

USERS = "users.xlsx"
JOBS = "jobs.xlsx"
APPS = "applications.xlsx"

# ================= INIT FILES =================
def init(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_excel(file, index=False)

init(USERS, ["username","password","role"])
init(JOBS, ["company","role","location","paid"])
init(APPS, ["name","email","role","score","status","resume"])

# ================= AI =================
def ai_score(role, answers):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
Evaluate candidate for {role}.
Answers:
{answers}

Give score out of 100.
"""
        r = model.generate_content(prompt).text
        score = int("".join(filter(str.isdigit, r))[:2] or 50)
        return score
    except:
        return 50

# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Velvoro Software Solution</h1>
    <a href="/login">Login</a> |
    <a href="/apply">Apply Job</a>
    """

# ================= LOGIN =================
@app.get("/login", response_class=HTMLResponse)
def login():
    return """
    <form method="post">
    Username:<input name="u">
    Password:<input type="password" name="p">
    <button>Login</button>
    </form>
    """

@app.post("/login")
def login_post(u:str=Form(...), p:str=Form(...)):
    df = pd.read_excel(USERS)
    user = df[df.username==u]
    if not user.empty and bcrypt.verify(p, user.password.values[0]):
        return {"status":"success","role":user.role.values[0]}
    return {"status":"failed"}

# ================= COMPANY =================
@app.get("/company", response_class=HTMLResponse)
def company():
    return """
    <h2>Post Job</h2>
    <form action="/post-job" method="post">
    Company:<input name="company">
    Role:<input name="role">
    Location:<input name="location">
    <button>Post</button>
    </form>
    """

@app.post("/post-job")
def post_job(company:str=Form(...), role:str=Form(...), location:str=Form(...)):
    df = pd.read_excel(JOBS)
    df.loc[len(df)] = [company, role, location, "FREE"]
    df.to_excel(JOBS, index=False)
    return {"message":"Job posted (free tier)"}

# ================= APPLY =================
@app.get("/apply", response_class=HTMLResponse)
def apply():
    jobs = pd.read_excel(JOBS).role.tolist()
    options = "".join(f"<option>{j}</option>" for j in jobs)
    return f"""
    <form action="/submit" method="post" enctype="multipart/form-data">
    Name:<input name="name"><br>
    Email:<input name="email"><br>
    Job:<select name="role">{options}</select><br>
    Q1:<textarea name="q1"></textarea><br>
    Q2:<textarea name="q2"></textarea><br>
    Resume:<input type="file" name="resume"><br>
    <button>Apply</button>
    </form>
    """

@app.post("/submit")
async def submit(
 name:str=Form(...), email:str=Form(...), role:str=Form(...),
 q1:str=Form(...), q2:str=Form(...),
 resume:UploadFile=File(...)
):
    path = f"{UPLOAD_DIR}/{time.time()}_{resume.filename}"
    with open(path,"wb") as f:
        f.write(await resume.read())

    score = ai_score(role, q1+q2)
    status = "QUALIFIED" if score>=70 else "NOT QUALIFIED"

    df = pd.read_excel(APPS)
    df.loc[len(df)] = [name,email,role,score,status,path]
    df.to_excel(APPS, index=False)

    return {"score":score,"status":status}

# ================= ADMIN =================
@app.get("/admin")
def admin():
    df = pd.read_excel(APPS).sort_values("score", ascending=False)
    return df.to_dict(orient="records")

# ================= NOTIFICATION =================
@app.get("/notify")
def notify():
    return {"email":"ready","sms":"placeholder"}

# ================= ANDROID APIs =================
@app.get("/api/jobs")
def api_jobs():
    return pd.read_excel(JOBS).to_dict(orient="records")

@app.get("/api/applications")
def api_apps():
    return pd.read_excel(APPS).to_dict(orient="records")

# ================= PAYMENT =================
@app.get("/payment")
def payment():
    return {"message":"Paid job posting coming soon"}
