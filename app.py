from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Velvoro Job AI")

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>🚀 Velvoro Job AI</h1>
    <ul>
        <li><a href="/apply">Apply Job</a></li>
        <li><a href="/admin">Admin Dashboard</a></li>
    </ul>
    """

# ---------------- APPLY FORM ----------------
@app.get("/apply", response_class=HTMLResponse)
def apply_form():
    return """
    <h2>Job Apply</h2>
    <form method="post" action="/apply">
        Name: <input type="text" name="name"><br><br>
        Email: <input type="email" name="email"><br><br>
        Role:
        <select name="role">
            <option>IT</option>
            <option>Non-IT</option>
            <option>Pharma</option>
        </select><br><br>
        <button type="submit">Apply</button>
    </form>
    """

@app.post("/apply", response_class=HTMLResponse)
def apply_submit(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...)
):
    return f"""
    <h3>✅ Application Submitted</h3>
    <p>Name: {name}</p>
    <p>Email: {email}</p>
    <p>Role: {role}</p>
    <a href="/">Go Home</a>
    """

# ---------------- ADMIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin():
    return """
    <h2>Admin Dashboard</h2>
    <p>Coming Soon 🚧</p>
    <ul>
        <li>Total Applications</li>
        <li>AI Ranking</li>
        <li>Payments</li>
    </ul>
    """
