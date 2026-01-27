from flask import Flask, request, render_template_string, redirect, url_for
import csv, os, uuid
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CSV_FILE = "applications.csv"

# =========================
# JOB ROLES & QUESTIONS
# =========================
IT_ROLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Data Analyst", "Data Scientist",
    "DevOps Engineer", "QA / Tester", "Mobile App Developer"
]

NON_IT_ROLES = [
    "HR Executive", "Recruiter", "Marketing Executive",
    "Sales Executive", "Digital Marketing",
    "Content Writer", "Accountant", "Operations Executive"
]

IT_QUESTIONS = [
    "Explain a project you have built using your primary tech stack.",
    "How do you debug a production issue?",
    "How do you ensure code quality and scalability?"
]

NON_IT_QUESTIONS = [
    "Explain your experience relevant to this role.",
    "How do you handle targets or deadlines?",
    "How do you communicate with teams or clients?"
]

# =========================
# LOCATION DATA
# =========================
COUNTRIES = ["India", "USA"]  # ISO expandable

STATES = {
    "India": [
        "Andhra Pradesh","Telangana","Karnataka","Tamil Nadu",
        "Maharashtra","Kerala","Delhi","Gujarat","Rajasthan"
    ],
    "USA": [
        "California","Texas","New York","Florida","Illinois"
    ]
}

DISTRICTS = {
    "Telangana": ["Hyderabad","Rangareddy","Medchal","Nalgonda"],
    "Andhra Pradesh": ["Visakhapatnam","Vijayawada","Guntur"],
    "Karnataka": ["Bengaluru Urban","Mysuru","Mangaluru"],
    "California": ["Los Angeles County","San Diego County"],
    "Texas": ["Harris County","Dallas County"]
}

# =========================
# CSV INIT
# =========================
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name","Phone","Email","Job Role","Experience",
            "Country","State","District","Area",
            "AI Score","Result","Date"
        ])

# =========================
# AI SCORING (SAFE FALLBACK)
# =========================
def ai_score(resume_text):
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = f"Score this resume out of 100:\n{resume_text}"
        response = model.generate_content(prompt)
        score = int("".join(filter(str.isdigit, response.text))[:2])
        return score
    except:
        return min(90, max(50, len(resume_text)//30))

# =========================
# HOME / APPLY
# =========================
@app.route("/", methods=["GET","POST"])
def apply():
    result = None
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        role = request.form["job_role"]
        exp = request.form["experience"]
        country = request.form["country"]
        state = request.form.get("state","")
        district = request.form.get("district","")
        area = request.form["area"]

        file = request.files["resume"]
        path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4())+"_"+file.filename)
        file.save(path)

        with open(path, "r", errors="ignore") as f:
            resume_text = f.read()

        score = ai_score(resume_text)
        result = "Qualified" if score >= 60 else "Not Qualified"

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name,phone,email,role,exp,
                country,state,district,area,
                score,result,datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES, non_it_roles=NON_IT_ROLES,
        it_q=IT_QUESTIONS, non_it_q=NON_IT_QUESTIONS,
        countries=COUNTRIES, states=STATES, districts=DISTRICTS,
        result=result
    )

# =========================
# ADMIN
# =========================
@app.route("/admin")
def admin():
    with open(CSV_FILE, encoding="utf-8") as f:
        data = list(csv.reader(f))[1:]
    return render_template_string(ADMIN, data=data)

# =========================
# HTML TEMPLATE
# =========================
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function loadQuestions(){
 let role=document.getElementById("job_role").value;
 document.getElementById("it_q").style.display={{'IT' if False else 'none'}};
 document.getElementById("nonit_q").style.display='none';
 if ({{ it_roles|tojson }}.includes(role)){
   document.getElementById("it_q").style.display='block';
 }
 if ({{ non_it_roles|tojson }}.includes(role)){
   document.getElementById("nonit_q").style.display='block';
 }
}
function loadStates(){
 let c=document.getElementById("country").value;
 let s=document.getElementById("state");
 s.innerHTML="";
 ({{ states|tojson }}[c]||[]).forEach(x=>s.innerHTML+=`<option>${x}</option>`);
 loadDistricts();
}
function loadDistricts(){
 let s=document.getElementById("state").value;
 let d=document.getElementById("district");
 d.innerHTML="";
 ({{ districts|tojson }}[s]||[]).forEach(x=>d.innerHTML+=`<option>${x}</option>`);
}
</script>
</head>
<body class="bg-light">
<div class="container mt-4">
<h2 class="text-center mb-3">Velvoro Job AI</h2>
<form method="post" enctype="multipart/form-data" class="card p-4">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>

<select class="form-select mb-2" id="job_role" name="job_role" onchange="loadQuestions()" required>
<option value="">Select Job Role</option>
{% for r in it_roles %}<option>{{r}}</option>{% endfor %}
{% for r in non_it_roles %}<option>{{r}}</option>{% endfor %}
</select>

<div id="it_q" style="display:none">
{% for q in it_q %}<label>{{q}}</label><textarea class="form-control mb-2"></textarea>{% endfor %}
</div>

<div id="nonit_q" style="display:none">
{% for q in non_it_q %}<label>{{q}}</label><textarea class="form-control mb-2"></textarea>{% endfor %}
</div>

<select class="form-select mb-2" name="experience">
{% for i in range(0,31) %}<option>{{i}}</option>{% endfor %}
</select>

<select class="form-select mb-2" id="country" name="country" onchange="loadStates()" required>
<option value="">Country</option>
{% for c in countries %}<option>{{c}}</option>{% endfor %}
</select>

<select class="form-select mb-2" id="state" name="state" onchange="loadDistricts()"></select>
<select class="form-select mb-2" id="district" name="district"></select>

<input class="form-control mb-2" name="area" placeholder="Area / Locality">
<input class="form-control mb-3" type="file" name="resume" required>

<button class="btn btn-primary w-100">Submit Application</button>
</form>

{% if result %}
<div class="alert alert-info mt-3">Result: <b>{{result}}</b></div>
{% endif %}
</div>
</body>
</html>
"""

ADMIN = """
<!doctype html>
<html><head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="container mt-4">
<h3>Admin Dashboard</h3>
<table class="table table-bordered">
<tr><th>Name</th><th>Phone</th><th>Email</th><th>Job</th><th>Exp</th><th>Score</th><th>Result</th></tr>
{% for r in data %}
<tr>{% for c in r[:7] %}<td>{{c}}</td>{% endfor %}</tr>
{% endfor %}
</table>
</body></html>
"""

if __name__ == "__main__":
    app.run(debug=True)
