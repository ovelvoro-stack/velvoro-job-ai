from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
import os
from datetime import datetime

app = FastAPI()

FILE = "data.xlsx"

def save_excel(data):
    if os.path.exists(FILE):
        df = pd.read_excel(FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_excel(FILE, index=False)

def ai_evaluate(category, q1, q2, q3):
    text = (q1 + q2 + q3).lower()
    score = len(text.split())

    if category == "IT":
        tech_words = ["python","java","api","database","sql","ai","ml","backend","frontend"]
        score += sum(10 for w in tech_words if w in text)
    else:
        hr_words = ["manage","team","communication","process","client","recruit"]
        score += sum(10 for w in hr_words if w in text)

    result = "QUALIFIED" if score >= 60 else "FAILED"
    return score, result

@app.get("/apply", response_class=HTMLResponse)
def apply_page():
    return """<!DOCTYPE html>
<html>
<head>
<title>Velvoro Job Application</title>
<style>
body{font-family:Arial;background:#f4f6f8}
.container{width:800px;margin:auto;background:#fff;padding:20px}
h2{background:#0b5ed7;color:#fff;padding:10px}
input,select,textarea{width:100%;padding:8px;margin:5px 0}
button{background:#0b5ed7;color:white;padding:10px;border:none}
</style>
<script>
function toggleQ(){
 let c=document.getElementById("category").value;
 document.getElementById("it").style.display = c=="IT"?"block":"none";
 document.getElementById("nonit").style.display = c=="NON-IT"?"block":"none";
}
</script>
</head>
<body>
<div class="container">
<h2>AI Powered Job Application – Velvoro Software Solution</h2>
<form method="post" action="/submit">
<input name="name" placeholder="Full Name" required>
<input name="phone" placeholder="Phone Number" required>
<input name="email" placeholder="Email ID" required>

<select name="experience">
<option>0</option><option>1</option><option>2</option><option>3</option>
<option>4</option><option>5</option><option>6</option><option>7</option>
<option>8</option><option>9</option><option>10</option>
</select>

<select name="qualification" required>
<option>B.Tech</option><option>M.Tech</option><option>MCA</option>
<option>MBA</option><option>BSc</option><option>MSc</option>
<option>Diploma</option><option>ITI</option><option>PhD</option>
</select>

<select name="category" id="category" onchange="toggleQ()">
<option value="IT">IT</option>
<option value="NON-IT">NON-IT</option>
</select>

<input name="role" placeholder="Job Role Applied">

<div id="it">
<textarea name="q1" placeholder="Explain your technical skills"></textarea>
<textarea name="q2" placeholder="Describe technical problem solved"></textarea>
<textarea name="q3" placeholder="Why should we hire you (technical)"></textarea>
</div>

<div id="nonit" style="display:none">
<textarea name="q1" placeholder="Explain role responsibility"></textarea>
<textarea name="q2" placeholder="Describe real work experience"></textarea>
<textarea name="q3" placeholder="Why should we hire you"></textarea>
</div>

<button type="submit">Submit Application</button>
</form>
</div>
</body>
</html>"""

@app.post("/submit", response_class=HTMLResponse)
def submit(
    name:str=Form(...), phone:str=Form(...), email:str=Form(...),
    experience:str=Form(...), qualification:str=Form(...),
    category:str=Form(...), role:str=Form(...),
    q1:str=Form(""), q2:str=Form(""), q3:str=Form("")
):
    score, result = ai_evaluate(category,q1,q2,q3)

    save_excel({
        "Name":name,"Phone":phone,"Email":email,
        "Category":category,"Role":role,
        "Experience":experience,
        "Score":score,"Result":result,
        "Time":datetime.now()
    })

    return f"""
    <h2>Application Result</h2>
    <p>Score: {score}</p>
    <p>Status: <b>{result}</b></p>
    """
