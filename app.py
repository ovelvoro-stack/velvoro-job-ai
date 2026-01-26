import os
import random
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# In-memory OTP store (no session, no secret key)
OTP_STORE = {}

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

HTML_FORM = """
<!doctype html>
<html>
<head>
  <title>Velvoro Job AI</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
  <h2>Velvoro Job AI</h2>
  <form method="POST">
    <input class="form-control mb-2" name="email" placeholder="Enter Email" required>
    <button class="btn btn-primary">Send OTP</button>
  </form>
  {% if msg %}
    <div class="alert alert-info mt-3">{{ msg }}</div>
  {% endif %}
</div>
</body>
</html>
"""

HTML_VERIFY = """
<!doctype html>
<html>
<head>
  <title>Verify OTP</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
  <h3>Enter OTP</h3>
  <form method="POST">
    <input type="hidden" name="email" value="{{ email }}">
    <input class="form-control mb-2" name="otp" placeholder="Enter OTP" required>
    <button class="btn btn-success">Verify</button>
  </form>
  {% if msg %}
    <div class="alert alert-danger mt-3">{{ msg }}</div>
  {% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form["email"]

        otp = random.randint(100000, 999999)
        OTP_STORE[email] = otp

        # Send email via Resend
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Velvoro Job AI <onboarding@resend.dev>",
                "to": [email],
                "subject": "Velvoro Job AI – OTP",
                "html": f"<h2>Your OTP is {otp}</h2>"
            }
        )

        if res.status_code != 200:
            return render_template_string(HTML_FORM, msg="Email failed")

        return render_template_string(HTML_VERIFY, email=email)

    return render_template_string(HTML_FORM)

@app.route("/verify", methods=["POST"])
def verify():
    email = request.form["email"]
    user_otp = request.form["otp"]

    if email in OTP_STORE and str(OTP_STORE[email]) == user_otp:
        OTP_STORE.pop(email)
        return "<h2>✅ OTP Verified Successfully</h2>"

    return render_template_string(
        HTML_VERIFY,
        email=email,
        msg="Invalid OTP"
    )

if __name__ == "__main__":
    app.run()
