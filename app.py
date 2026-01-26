from flask import Flask, render_template, request, redirect, session
import random, os
import resend
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

# Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

DATA = []


def send_otp_email(to_email, otp):
    resend.Emails.send({
        "from": "Velvoro Job AI <onboarding@resend.dev>",
        "to": to_email,
        "subject": "Velvoro Job AI – OTP",
        "html": f"<h2>Your OTP is <b>{otp}</b></h2>"
    })


def ai_score(role):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    res = model.generate_content(
        f"Evaluate candidate for job role {role}. Reply PASS or FAIL"
    )
    return res.text.strip()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        otp = random.randint(100000, 999999)
        session["otp"] = str(otp)
        session["user"] = request.form.to_dict()

        send_otp_email(session["user"]["email"], otp)
        return redirect("/otp")

    return render_template("index.html")


@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            user = session["user"]
            result = ai_score(user["job_role"])
            user["ai_result"] = result
            DATA.append(user)
            return "✅ OTP Verified. Application Submitted."
        else:
            return "❌ Invalid OTP"

    return render_template("otp.html")


@app.route("/admin")
def admin():
    return render_template("admin.html", data=DATA)


if __name__ == "__main__":
    app.run()
