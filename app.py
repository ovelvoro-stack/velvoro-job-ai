from flask import Flask, request, redirect, session, render_template_string
import csv, os, random

# ======================
# SAFE GEMINI IMPORT
# ======================
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DB_FILE = "applications.csv"

# ======================
# GEMINI CONFIG
# ======================
"""
⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇⬇
ఇక్కడ నీ Gemini API Key పెట్టాలి
"""
if GEMINI_AVAILABLE:
    genai.configure(api_key="AIzaSyB-Xil35VylfYAPZQvFzCjgzcwouWudkRU")

# ======================
# DATA
# ======================
COACHINGS = {
    "IT": ["Python Developer", "Java Developer", "Full Stack", "Data Analyst"],
    "NON-IT": ["HR", "Marketing", "Sales", "Accounts"],
    "GENERAL": ["Office Admin", "Clerk", "Assistant"]
}

# ======================
# AI FUNCTIONS (SAFE)
# ======================
def generate_question(coaching, role):
    if not GEMINI_AVAILABLE:
        return f"Explain your knowledge in {role}"
    model = genai.GenerativeModel("gemini-pro")
    return model.generate_content(
        f"Ask an interview question for {role} ({coaching})"
    ).text

def evaluate_answer(question, answer):
    if not GEMINI_AVAILABLE:
        return "SCORE: 50 | RESULT: PENDING"
    model = genai.GenerativeModel("gemini-pro")
    return model.generate_content(
        f"Question: {question}\nAnswer: {answer}\nEvaluate pass or fail"
    ).text

# ======================
# ROUTES
# ======================
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        session["form"] = request.form.to_dict()
        return redirect("/question")

    return render_template_string(FORM_HTML, coachings=COACHINGS)

@app.route("/question", methods=["GET", "POST"])
def question():
    f = session.get("form")
    if not f:
        return redirect("/")

    if request.method == "POST":
        q = f["question"]
        ans = request.form["answer"]
        result = evaluate_answer(q, ans)

        write_header = not os.path.exists(DB_FILE)
        with open(DB_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["Name","Email","Role","Result"])
            writer.writerow([f["name"], f["email"], f["job_role"], result])

        return "<h2>Application Submitted Successfully</h2>"

    q = generate_question(f["coaching"], f["job_role"])
    f["question"] = q
    session["form"] = f
    return render_template_string(QUESTION_HTML, question=q)

@app.route("/admin")
def admin():
    rows = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            rows = list(csv.reader(f))
    return render_template_string(ADMIN_HTML, rows=rows)

# ======================
# HTML
# ======================
FORM_HTML = """
<h2>Velvoro Software Solution – Job Application</h2>
<form method="post">
<input name="name" placeholder="Full Name" required><br>
<input name="email" placeholder="Email" required><br>

<select name="coaching" required>
<option value="">Select Coaching</option>
{% for c in coachings %}<option>{{c}}</option>{% endfor %}
</select><br>

<select name="job_role" required>
{% for v in coachings.values() %}
{% for r in v %}<option>{{r}}</option>{% endfor %}
{% endfor %}
</select><br>

<button>Continue</button>
</form>
"""

QUESTION_HTML = """
<h3>AI Question</h3>
<p>{{question}}</p>
<form method="post">
<textarea name="answer" required></textarea><br>
<button>Submit</button>
</form>
"""

ADMIN_HTML = """
<h2>Admin Dashboard</h2>
<table border="1">
{% for r in rows %}
<tr>{% for c in r %}<td>{{c}}</td>{% endfor %}</tr>
{% endfor %}
</table>
"""

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    app.run()
