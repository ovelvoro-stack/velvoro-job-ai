from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd, os, time, random, smtplib
from email.message import EmailMessage
import google.generativeai as genai

# ================= CONFIG =================
app = FastAPI(title="Velvoro Job AI Platform")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

USERS = "users.xlsx"
JOBS = "jobs.xlsx"
APPS = "applications.xlsx"
OTP_FILE = "otp.xlsx"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ================= INIT FILES =================
def init(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_excel(file, index=False)

init(USERS, ["email","role"])
init(JOBS, ["company","role","location","status"])
init(APPS, ["name","email","role","score","result","resume"])
init(OTP_FILE, ["email","otp","time"])

# ================= EMAIL =================
def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    server = smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT")))
    server.starttls()
    server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    server.send_message(msg)
    server.quit()

# ================= OTP =================
@app.post("/send-otp")
def send_otp(email:str=Form(...)):
    otp = random.randint(100000, 999999)
    df = pd.read_excel(OTP_FILE)
    df.loc[len(df)] = [email, otp, time.time()]
    df.to_excel(OTP_FILE, index=False)

    send_email(
        email,
        "Velvoro Login OTP",
        f"Your OTP is {otp}. Valid for 5 minutes."
    )
    return {"message":"OTP sent"}

@app.post("/verify-otp")
def verify_otp(email:str=Form(...), otp:int=Form(...)):
    df = pd.read_excel(OTP_FILE)
    row = df[(df.email==email) & (df.otp==otp)]

    if row.empty:
        return {"status":"failed"}

    if time.time() - row.time.values[0] > 300:
        return {"status":"expired"}

    return {"status":"success"}

# ================= AI =================
def ai_score(role, answers):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        r = model.generate_content(
            f"Evaluate answers for {role} and give score out of 100:\n{answers}"
        ).text
        return int("".join(filter(str.isdigit, r))[:2] or 60)
    except:
        return 60

# ================= APPLY =================
@app.get("/apply", response_class=HTMLResponse)
def apply():
    jobs = pd.read_excel(JOBS).role.tolist()
    options = "".join(f"<option>{j}</option>" for j in jobs)

    return f"""
    <form action="/submit" method="post" enctype="multipart/form-data">
    Name:<input name="name"><br>
    Email:<input name="email"><br>
    Role:<select name="role">{options}</select><br>
    Q1:<textarea name="q1"></textarea><br>
    Q2:<textarea name="q2"></textarea><br>
    Resume:<input type="file" name="resume"><br>
    <button>Apply</button>
    </form>
    """

@app.post("/submit")
async def submit(
    name:str=Form(...),
    email:str=Form(...),
    role:str=Form(...),
    q1:str=Form(...),
    q2:str=Form(...),
    resume:UploadFile=File(...)
):
    path = f"{UPLOAD_DIR}/{time.time()}_{resume.filename}"
    with open(path,"wb") as f:
        f.write(await resume.read())

    score = ai_score(role, q1+q2)
    result = "QUALIFIED" if score>=70 else "NOT QUALIFIED"

    df = pd.read_excel(APPS)
    df.loc[len(df)] = [name,email,role,score,result,path]
    df.to_excel(APPS, index=False)

    send_email(
        email,
        "Velvoro Job Application Result",
        f"Your Score: {score}\nStatus: {result}"
    )

    return {"score":score,"result":result}

# ================= ADMIN =================
@app.get("/admin")
def admin_dashboard():
    df = pd.read_excel(APPS).sort_values("score", ascending=False)
    return df.to_dict(orient="records")

# ================= COMPANY =================
@app.post("/post-job")
def post_job(
    company:str=Form(...),
    role:str=Form(...),
    location:str=Form(...)
):
    df = pd.read_excel(JOBS)
    df.loc[len(df)] = [company, role, location, "FREE"]
    df.to_excel(JOBS, index=False)
    return {"message":"Job posted successfully"}
