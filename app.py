from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Velvoro Job AI")

# TEMP STORAGE (In-Memory)
applications = []

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
        Name: <input type="text" name="name" required><br><br>
        Email: <input type="email" name="email" required><br><br>
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
    applications.append({
        "name": name,
        "email": email,
        "role": role
    })

    return """
    <h3>✅ Application Submitted Successfully</h3>
    <a href="/">Go Home</a>
    """

# ---------------- ADMIN ----------------
@app.get("/admin", response_class=HTMLResponse)
def admin():
    html = "<h2>📋 Admin Dashboard</h2>"

    if not applications:
        html += "<p>No applications yet</p>"
    else:
        html += "<table border='1' cellpadding='8'>"
        html += "<tr><th>Name</th><th>Email</th><th>Role</th></tr>"

        for app_data in applications:
            html += f"""
            <tr>
                <td>{app_data['name']}</td>
                <td>{app_data['email']}</td>
                <td>{app_data['role']}</td>
            </tr>
            """

        html += "</table>"

    html += "<br><a href='/'>Home</a>"
    return html
