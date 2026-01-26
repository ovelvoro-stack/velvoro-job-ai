from flask import Flask, request, jsonify, redirect, url_for
import csv, os
import google.generativeai as genai

# ==============================
# FLASK APP CONFIG
# ==============================
app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DB_FILE = "applications.csv"

# ==============================
# GEMINI CONFIG (DO NOT HARD CODE)
# ==============================
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_ai_question(role):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"Ask one interview question for the job role: {role}"
    response = model.generate_content(prompt)
    return response.text

def ai_pass_fail(answer):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"""
    Evaluate this interview answer.
    Answer only PASS or FAIL.

    Answer:
    {answer}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ==============================
# HOME
# ==============================
@app.route("/")
def home():
    return """
    <h2>Velvoro Job AI is Live</h2>
    <a href='/apply'>Apply Job</a><br><br>
    <a href='/admin'>Admin Dashboard</a>
    """

# ==============================
# JOB APPLY FORM
# ==============================
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]
        answer = request.form["answer"]

        result = ai_pass_fail(answer)

        file_exists = os.path.isfile(DB_FILE)
        with open(DB_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Name", "Email", "Role", "Answer", "Result"])
            writer.writerow([name, email, role, answer, result])

        return f"<h3>Result: {result}</h3><a href='/'>Back</a>"

    question = generate_ai_question("Python Developer")

    return f"""
    <h2>Velvoro Job Application</h2>
    <form method="post">
        Name:<br><input name="name"><br><br>
        Email:<br><input name="email"><br><br>
        Job Role:<br>
        <select name="role">
            <option>Python Developer</option>
            <option>Java Developer</option>
            <option>Data Analyst</option>
            <option>Web Developer</option>
        </select><br><br>

        <b>AI Question:</b><br>{question}<br><br>
        Answer:<br>
        <textarea name="answer" rows="5" cols="40"></textarea><br><br>

        <button type="submit">Submit</button>
    </form>
    """

# ==============================
# ADMIN DASHBOARD
# ==============================
@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for r in reader:
                rows += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"

    return f"""
    <h2>Admin Dashboard</h2>
    <table border="1" cellpadding="5">
        {rows}
    </table>
    <br><a href="/">Home</a>
    """

# ==============================
# AI QUESTION API (TEST)
# ==============================
@app.route("/question")
def question():
    role = request.args.get("role", "Python Developer")
    q = generate_ai_question(role)
    return jsonify({"question": q})
