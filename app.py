from flask import Flask, request, redirect
import csv, os, random

app = Flask(__name__)
DATA_FILE = "data.csv"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# --------------------------
# Utility
# --------------------------
def save_row(row):
    exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["Name", "Phone", "Email", "Role", "OTP", "Status"])
        w.writerow(row)

# --------------------------
# Home – Job Apply
# --------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        role = request.form.get("role")

        otp = random.randint(100000, 999999)
        save_row([name, phone, email, role, otp, "PENDING"])

        return f"""
        <h3>Application Submitted ✅</h3>
        <p>Your OTP (demo): <b>{otp}</b></p>
        <a href="/">Back</a>
        """

    return """
    <h2>Velvoro Job AI</h2>
    <form method="post">
      Name:<br><input name="name" required><br><br>
      Phone:<br><input name="phone" required><br><br>
      Email:<br><input name="email" required><br><br>
      Job Role:<br><input name="role" required><br><br>
      <button type="submit">Apply</button>
    </form>
    <hr>
    <a href="/admin">Admin Login</a>
    """

# --------------------------
# Admin Login
# --------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            return redirect("/dashboard")
        return "Wrong password"

    return """
    <h3>Admin Login</h3>
    <form method="post">
      Password:
      <input type="password" name="password">
      <button>Login</button>
    </form>
    """

# --------------------------
# Dashboard
# --------------------------
@app.route("/dashboard")
def dashboard():
    rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            rows = list(csv.reader(f))

    html = "<h2>Admin Dashboard</h2><table border=1>"
    for r in rows:
        html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    html += "</table><br><a href='/'>Home</a>"
    return html

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
