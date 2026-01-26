from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- APPLY ----------------
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        return redirect(url_for("result"))
    return render_template("apply.html")

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    return render_template("admin.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------------- RESULT ----------------
@app.route("/result")
def result():
    return render_template("result.html")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
