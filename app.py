from flask import Flask, request, redirect, render_template_string
import random
import os
import requests
import time

app = Flask(__name__)

# 🔐 In-memory OTP store (SAFE for MVP)
otp_store = {}

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
  Email:<br>
  <input type="email" name="email" required><br><br>
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

def send_email(email, otp):
    requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Velvoro Job AI <onboarding@resend.dev>",
            "to": [email],
            "subject": "Velvoro Job AI – OTP",
            "html": f"<h3>Your OTP is <b>{otp}</b></h3><p>Valid for 5 minutes</p>"
        },
        timeout=10
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form["email"]
        otp = str(random.randint(100000, 999999))

        # store otp with timestamp
        otp_store[email] = {
            "otp": otp,
            "time": time.time()
        }

        send_email(email, otp)
        return redirect("/verify")

    return render_template_string(HTML_FORM)

@app.route("/verify", methods=["GET", "POST"])
def verify():
    msg = ""
    if request.method == "POST":
        email = request.form["email"]
        user_otp = request.form["otp"]

        record = otp_store.get(email)

        if not record:
            msg = "OTP not found"
        elif time.time() - record["time"] > 300:
            msg = "OTP expired"
        elif record["otp"] == user_otp:
            otp_store.pop(email, None)
            return render_template_string(HTML_SUCCESS)
        else:
            msg = "Invalid OTP"

    return render_template_string(HTML_VERIFY, msg=msg)

if __name__ == "__main__":
    app.run()
