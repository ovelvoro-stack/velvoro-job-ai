from flask import Flask, request, render_template_string, redirect, url_for
import csv, os, datetime, smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CSV_FILE = 'applications.csv'

# ---------------- QUESTIONS ----------------
IT_QUESTIONS = [
    "Explain your experience with programming languages you know.",
    "Describe a challenging technical problem you solved recently.",
    "How do you keep yourself updated with new technologies?"
]

NON_IT_QUESTIONS = [
    "Explain your previous work experience related to this role.",
    "How do you handle pressure and deadlines?",
    "Why do you think you are suitable for this position?"
]

IT_ROLES = [
    "Software Engineer","Backend Developer","Frontend Developer",
    "Full Stack Developer","Data Analyst","Data Scientist",
    "DevOps Engineer","QA / Tester","Mobile App Developer"
]

NON_IT_ROLES = [
    "HR Executive","Recruiter","Marketing Executive","Sales Executive",
    "Digital Marketing","Content Writer","Accountant","Operations Executive"
]

# ---------------- EMAIL ----------------
def send_confirmation_email(name, email, job):
    try:
        msg = EmailMessage()
        msg['Subject'] = "Application Received – Velvoro Software Solution"
        msg['From'] = os.environ.get("SMTP_USER")
        msg['To'] = email

        msg.set_content(f"""
Dear {name},

Congratulations! 🎉

We have successfully received your application for the role of
{job} at Velvoro Software Solution.

Our team will review your profile and get back to you shortly.

Best Regards,
Velvoro Software Solution
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(
                os.environ.get("SMTP_USER"),
                os.environ.get("SMTP_PASS")
            )
            server.send_message(msg)
    except Exception as e:
        print("Email error:", e)

# ---------------- AI SCORE (SAFE) ----------------
def ai_score(resume_text):
    # Render free plan safe fallback
    if not resume_text:
        return 0
    length = len(resume_text)
    return min(100, max(30, length // 10))

# ---------------- QUALIFICATION ----------------
def qualification(ans1, ans2, ans3):
    score = len(ans1) + len(ans2) + len(ans3)
    return "Qualified" if score > 200 else "Not Qualified"

# ---------------- ROUTES ----------------
@app.route('/', methods=['GET','POST'])
def apply():
    result = None
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        job = request.form['job']
        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']

        file = request.files['resume']
        resume_text = ""
        if file:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            resume_text = file.filename

        score = ai_score(resume_text)
        qualify = qualification(q1, q2, q3)

        write_header = not os.path.exists(CSV_FILE)
        with open(CSV_FILE,'a',newline='',encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["Name","Phone","Email","Job","Score","Result"])
            writer.writerow([name,phone,email,job,score,qualify])

        send_confirmation_email(name,email,job)
        result = qualify

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        it_q=IT_QUESTIONS,
        non_it_q=NON_IT_QUESTIONS,
        result=result
    )

@app.route('/admin')
def admin():
    data = []
    total = 0
    avg = 0
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE,encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                data.append(r)
        total = len(data)
        if total:
            avg = sum(int(r['Score']) for r in data)//total
    return render_template_string(ADMIN_TEMPLATE,data=data,total=total,avg=avg)

# ---------------- TEMPLATES ----------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job Application</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function loadQuestions(){
    let job=document.getElementById("job").value;
    let it={{ it_roles|tojson }};
    let qIT={{ it_q|tojson }};
    let qN={{ non_it_q|tojson }};
    let qs = it.includes(job) ? qIT : qN;
    for(let i=0;i<3;i++){
        document.getElementById("ql"+i).innerText=qs[i];
    }
}
</script>
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card shadow p-4">
<h3 class="text-center mb-3">Velvoro Software Solution – Job Application</h3>
<form method="post" enctype="multipart/form-data">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" name="email" type="email" placeholder="Email" required>

<select id="job" name="job" class="form-select mb-3" onchange="loadQuestions()" required>
<option value="">Select Job Role</option>
<optgroup label="IT">
{% for r in it_roles %}<option>{{r}}</option>{% endfor %}
</optgroup>
<optgroup label="Non-IT">
{% for r in non_it_roles %}<option>{{r}}</option>{% endfor %}
</optgroup>
</select>

<input class="form-control mb-3" type="file" name="resume" accept=".pdf,.doc,.docx" required>

<label id="ql0"></label>
<textarea class="form-control mb-2" name="q1" required></textarea>

<label id="ql1"></label>
<textarea class="form-control mb-2" name="q2" required></textarea>

<label id="ql2"></label>
<textarea class="form-control mb-3" name="q3" required></textarea>

<button class="btn btn-primary w-100">Submit Application</button>
</form>

{% if result %}
<div class="alert alert-info mt-3 text-center">
Result: <b>{{result}}</b>
</div>
{% endif %}
</div>
</div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
<h3>Admin Dashboard</h3>
<p>Total Applications: {{total}}</p>
<p>Average Resume Score: {{avg}}</p>
<table class="table table-bordered">
<tr><th>Name</th><th>Phone</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th></tr>
{% for r in data %}
<tr>
<td>{{r.Name}}</td>
<td>{{r.Phone}}</td>
<td>{{r.Email}}</td>
<td>{{r.Job}}</td>
<td>{{r.Score}}</td>
<td>{{r.Result}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == '__main__':
    app.run()
