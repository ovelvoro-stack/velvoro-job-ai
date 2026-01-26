from flask import Flask, request, redirect, session
import os, random, csv

app = Flask(__name__)
app.secret_key = "velvoro-final-secret"

# ---------- TWILIO ----------
from twilio.rest import Client

def send_whatsapp_otp(phone, otp):
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )
    client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_FROM"),
        to=f"whatsapp:{phone}",
        body=f"🔐 Velvoro Job AI OTP: {otp}"
    )

# ---------- OTP ----------
def generate_otp():
    return str(random.randint(100000, 999999))

# ---------- APPLY ----------
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name  = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        role  = request.form["role"]

        otp = generate_otp()

        session["otp"] = otp
        session["user"] = [name, phone, email, role]

        send_whatsapp_otp(phone, otp)

        # 🔥 THIS IS IMPORTANT
        return redirect("/verify-otp")

    return """
    <h2>Velvoro Job AI</h2>
    <form method="post">
      Name:<br><input name="name" required><br><br>
      Phone (+91XXXXXXXXXX):<br><input name="phone" required><br><br>
      Email:<br><input name="email" required><br><br>
      Job Role:<br><input name="role" required><br><br>
      <button type="submit">Apply</button>
    </form>
    """

# ---------- OTP PAGE ----------
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered = request.form["otp"]

        if entered == session.get("otp"):
            name, phone, email, role = session["user"]

            with open("applications.csv", "a", newline="") as f:
                csv.writer(f).writerow([name, phone, email, role])

            return """
            <h2>✅ OTP Verified</h2>
            <p>Your application is submitted successfully.</p>
            """

        return "<h3>❌ Invalid OTP</h3><a href='/verify-otp'>Try Again</a>"

    return """
    <h2>Enter OTP</h2>
    <p>OTP already sent to your WhatsApp</p>
    <form method="post">
      <input name="otp" placeholder="Enter OTP" required>
      <button type="submit">Verify</button>
    </form>
    """

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists("applications.csv"):
        with open("applications.csv") as f:
            for r in csv.reader(f):
                rows += "<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>"

    return f"""
    <h2>Admin Dashboard</h2>
    <table border="1">
      <tr><th>Name</th><th>Phone</th><th>Email</th><th>Role</th></tr>
      {rows}
    </table>
    """

# ---------- RUN ----------
if __name__ == "__main__":
    app.run()
