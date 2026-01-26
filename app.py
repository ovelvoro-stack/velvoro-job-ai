from flask import Flask, request, render_template_string, session, redirect
import random
import os
import requests

app = Flask(__name__)

# ✅ VERY IMPORTANT (Render compatible)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

HTML_FORM = """
<h2>Velvoro Job AI – Email OTP</h2>
<form method="post">
  Email:<br>
  <input type="email" name="email" required><br><br>
  <button type="submit">Send OTP</button>
</form>
"""

HTML_VERIFY = """
<h2>Verify OTP</h2>
<form method="post">
  OTP:<br>
  <input type="text" name="otp" required><br><br>
  <button type="submit">Verify</button>
</form>
<p style="color:red;">{{msg}}</p>
"""

HTML_SUCCESS = """
<h2>✅ OTP Verified Successfully</h2>
<p>Welcome to Velvoro Job AI</p>
"""

def send_email_otp(email, otp):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Velvoro Job AI <onboarding@resend.dev>",
            "to": [email],
            "subject": "Velvoro Job AI – OTP",
            "html": f"<h3>Your OTP is <b>{otp}</b></h3><p>Valid for 5 minutes</p>",
        },
        timeout=10
    )
    print("Email status:", response.status_code)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form["email"]
        otp = str(random.randint(100000, 999999))

        session["otp"] = otp
        session["email"] = email

        send_email_otp(email, otp)
        return redirect("/verify")

    return render_template_string(HTML_FORM)

@app.route("/verify", methods=["GET", "POST"])
def verify():
    msg = ""
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            return render_template_string(HTML_SUCCESS)
        else:
            msg = "❌ Invalid OTP"
    return render_template_string(HTML_VERIFY, msg=msg)

if __name__ == "__main__":
    app.run()
