from flask import Flask, request, redirect, session
import os, random, csv

app = Flask(__name__)
app.secret_key = "velvoro-secret"

# -------- OPTIONAL SERVICES --------
try:
    from twilio.rest import Client
    twilio_enabled = True
except:
    twilio_enabled = False

# -------- HELPERS --------
def generate_otp():
    return str(random.randint(100000, 999999))

def send_whatsapp(phone, otp):
    if not twilio_enabled:
        return
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=f"whatsapp:{phone}",
            body=f"Velvoro Job AI OTP: {otp}"
        )
    except:
        pass

# -------- ROUTES --------
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

        send_whatsapp(phone, otp)

        return redirect("/verify")

    return """
    <h2>Velvoro Job AI</h2>
    <form method="post">
      Name:<br><input name="name" required><br>
      Phone (+91...):<br><input name="phone" required><br>
      Email:<br><input name="email" required><br>
      Job Role:<br><input name="role" required><br><br>
      <button type="submit">Apply</button>
    </form>
    """

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        entered = request.form["otp"]
        if entered == session.get("otp"):
            name, phone, email, role = session["user"]
            with open("data.csv", "a", newline="") as f:
                csv.writer(f).writerow([name, phone, email, role])

            return """
            <h2>✅ OTP Verified Successfully</h2>
            <p>Application Submitted</p>
            <a href="/">Back</a>
            """
        else:
            return "<h3>❌ Invalid OTP</h3><a href='/verify'>Try Again</a>"

    return """
    <h2>Enter OTP</h2>
    <form method="post">
      <input name="otp" placeholder="Enter OTP" required>
      <button type="submit">Verify</button>
    </form>
    """

@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists("data.csv"):
        with open("data.csv") as f:
            for r in csv.reader(f):
                rows += "<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>"

    return f"""
    <h2>Admin Dashboard</h2>
    <table border="1">
    <tr><th>Name</th><th>Phone</th><th>Email</th><th>Role</th></tr>
    {rows}
    </table>
    """

# -------- RUN --------
if __name__ == "__main__":
    app.run()
