from flask import Flask, request, jsonify
import csv, os
import google.generativeai as genai

# -------------------------
# FLASK APP
# -------------------------
app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DB_FILE = "applications.csv"

# -------------------------
# GEMINI CONFIG
# -------------------------
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_ai_question(role):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    prompt = f"Ask one interview question for the job role: {role}"
    response = model.generate_content(prompt)
    return response.text

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return "Velvoro Job AI is Live"

@app.route("/question")
def question():
    role = request.args.get("role", "Python Developer")
    q = generate_ai_question(role)
    return jsonify({"question": q})

# -------------------------
# RUN LOCAL ONLY
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
