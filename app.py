import os
import sqlite3
import random
import requests
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

DB = "database.db"

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        role TEXT,
        otp INTEGER,
        verified INTEGER,
        ai_score TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- HTML ----------------
HOME_HTML = """
<h2>Velvoro Job AI</h2>
<form method="POST">
<input name="name" placeholder="Name" required><br><br>
<input name="email" placeholder="Email" required><br><br>
<input name="role" placeholder="Job Role" required><br><br>
<button>Apply</button>
</form>
<p style="color:green">{{msg}}</p>
<a href="/admin">Admin Login</a>
"""

OTP_HTML = """
<h3>Enter OTP</h3>
<form method="POST">
<input type="hidden" name="email" value="{{email}}">
<input name="otp" placeholder="OTP" required>
<button>Verify</button>
</form>
<p style="color:red">{{msg}}</p>
"""

ADMIN_LOGIN = """
<h3>Admin Login</h3>
<form method="POST">
<input type="password" name="password" placeholder="Password">
<button>Login</button>
</form>
<p>{{msg}}</p>
"""

ADMIN_DASH = """
<h2>Admin Dashboard</h2>
<table border="1" cellpadding="5">
<tr>
<th>Name</th><th>Email</th><th>Role</th><th>AI Score</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td>
</tr>
{% endfor %}
</table>
"""

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]

        otp = random.randint(100000,999999)

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO applications VALUES (NULL,?,?,?,?,?)",
                  (name,email,role,otp,0,"Pending"))
        conn.commit()
        conn.close()

        # Send OTP Email
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from":"Velvoro Job AI <onboarding@resend.dev>",
                "to":[email],
                "subject":"Your OTP",
                "html":f"<h2>Your OTP is {otp}</h2>"
            }
        )

        return render_template_string(OTP_HTML,email=email)

    return render_template_string(HOME_HTML,msg="")

@app.route("/verify", methods=["POST"])
def verify():
    email = request.form["email"]
    otp = request.form["otp"]

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT otp,role FROM applications WHERE email=?", (email,))
    row = c.fetchone()

    if row and str(row[0]) == otp:
        role = row[1]

        # Gemini AI scoring
        score = gemini_score(role)

        c.execute("UPDATE applications SET verified=1, ai_score=? WHERE email=?",
                  (score,email))
        conn.commit()
        conn.close()

        return "<h2>✅ Application Submitted Successfully</h2>"

    return render_template_string(OTP_HTML,email=email,msg="Invalid OTP")

def gemini_score(role):
    try:
        res = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents":[{
                    "parts":[{"text":f"Give a short hiring score for job role {role}"}]
                }]
            }
        )
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "AI Error"

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] != ADMIN_PASSWORD:
            return render_template_string(ADMIN_LOGIN,msg="Wrong password")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT name,email,role,ai_score FROM applications WHERE verified=1")
        rows = c.fetchall()
        conn.close()

        return render_template_string(ADMIN_DASH,rows=rows)

    return render_template_string(ADMIN_LOGIN,msg="")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
