from flask import Flask, render_template, request, redirect, session
import random, smtplib, os
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Email config
EMAIL = os.environ.get("EMAIL_SENDER")
PASSWORD = os.environ.get("EMAIL_PASSWORD")

DATA = []  # simple in-memory storage


def send_otp(email, otp):
    msg = f"Subject: Velvoro Job AI - OTP\n\nYour OTP is: {otp}"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, email, msg)
    server.quit()


def ai_score(role):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"Give pass or fail for job role: {role}"
    res = model.generate_content(prompt)
    return res.text.strip()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        otp = random.randint(100000, 999999)
        session["otp"] = str(otp)
        session["user"] = request.form.to_dict()

        send_otp(session["user"]["email"], otp)
        return redirect("/verify")

    return render_template("index.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        if request.form["otp"] == session.get("otp"):
            user = session["user"]
            result = ai_score(user["job_role"])
            user["ai_result"] = result
            DATA.append(user)
            return "✅ Application submitted & evaluated successfully"
        else:
            return "❌ Invalid OTP"

    return render_template("verify_otp.html")


@app.route("/admin")
def admin():
    return render_template("admin.html", data=DATA)


if __name__ == "__main__":
    app.run(debug=True)
