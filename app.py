from flask import Flask, request, redirect
import os, random, csv

# ---------- OPTIONAL AI (SAFE) ----------
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    ai_enabled = True
except:
    ai_enabled = False

# ---------- OPTIONAL TWILIO (SAFE) ----------
try:
    from twilio.rest import Client
    twilio_enabled = True
except:
    twilio_enabled = False

app = Flask(__name__)

# ---------- HELPERS ----------
def generate_otp():
    return str(random.randint(100000, 999999))

def ai_score(role):
    if not ai_enabled:
        return "N/A"
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        r = model.generate_content(f"Rate candidate for role {role} from 1 to 10")
        return r.text.strip()
    except:
        return "AI Error"

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

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name  = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        role  = request.form["role"]

        otp   = generate_otp()
        score = ai_score(role)

        # Save CSV
        with open("data.csv", "a", newline="") as f:
            csv.writer(f).writerow([name, phone, email, role, otp, score])

        # WhatsApp OTP
        send_whatsapp(phone, otp)

        return f"""
        <h2>Application Submitted ✅</h2>
        <p><b>AI Score:</b> {score}</p>
        <p>OTP generated (WhatsApp)</p>
        <a href="/">Back</a>
        """

    return """
    <h2>Velvoro Job AI</h2>
    <form method="post">
      Name:<br><input name="name"><br>
      Phone (with country code):<br><input name="phone"><br>
      Email:<br><input name="email"><br>
      Job Role:<br><input name="role"><br><br>
      <button type="submit">Apply</button>
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
    <tr><th>Name</th><th>Phone</th><th>Email</th><th>Role</th><th>OTP</th><th>Score</th></tr>
    {rows}
    </table>
    """

# ---------- ENTRY ----------
if __name__ == "__main__":
    app.run()
