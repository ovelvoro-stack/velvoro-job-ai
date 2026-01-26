from flask import Flask, request, render_template_string
import csv
import os
from datetime import datetime

app = Flask(__name__)

CSV_FILE = "applications.csv"

# -------------------------------
# Country → State → District data
# -------------------------------
LOCATION_DATA = {
    "India": {
        "Telangana": ["Hyderabad", "Rangareddy", "Medchal"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur"],
        "Karnataka": ["Bengaluru Urban", "Mysuru", "Mangaluru"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"]
    },
    "USA": {
        "California": ["Los Angeles County", "San Diego County", "San Jose"],
        "Texas": ["Harris County", "Dallas County", "Austin"],
        "New York": ["New York City", "Buffalo", "Albany"]
    },
    "UK": {
        "England": ["London", "Manchester", "Birmingham"],
        "Scotland": ["Edinburgh", "Glasgow"]
    }
}

# -------------------------------
# Create CSV if not exists
# -------------------------------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp", "Name", "Phone", "Email",
            "Job Role", "Country", "State", "District", "Area"
        ])

# -------------------------------
# Main Route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def apply():
    message = None

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        job = request.form.get("job")
        country = request.form.get("country")
        state = request.form.get("state")
        district = request.form.get("district")
        area = request.form.get("area")

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(), name, phone, email,
                job, country, state, district, area
            ])

        message = "Application submitted successfully!"

    return render_template_string(TEMPLATE,
        location_data=LOCATION_DATA,
        message=message
    )

# -------------------------------
# HTML + JS Template
# -------------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Velvoro Software Solution – Job Application</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background:#f4f6f9; }
        .card { border-radius:12px; }
    </style>
</head>
<body>

<div class="container mt-5">
    <div class="card shadow p-4">
        <h3 class="text-center mb-4">Velvoro Software Solution – Job Application</h3>

        {% if message %}
        <div class="alert alert-success text-center">{{ message }}</div>
        {% endif %}

        <form method="POST">
            <div class="mb-3">
                <input class="form-control" name="name" placeholder="Full Name" required>
            </div>

            <div class="mb-3">
                <input class="form-control" name="phone" placeholder="Phone Number" required>
            </div>

            <div class="mb-3">
                <input type="email" class="form-control" name="email" placeholder="Email" required>
            </div>

            <div class="mb-3">
                <select class="form-select" name="job" required>
                    <option value="">Select Job Role</option>
                    <option>Software Engineer</option>
                    <option>Backend Developer</option>
                    <option>Frontend Developer</option>
                    <option>Full Stack Developer</option>
                    <option>HR Executive</option>
                    <option>Recruiter</option>
                    <option>Sales Executive</option>
                </select>
            </div>

            <!-- Country -->
            <div class="mb-3">
                <select class="form-select" id="country" name="country" required onchange="loadStates()">
                    <option value="">Select Country</option>
                    {% for c in location_data.keys() %}
                        <option value="{{c}}">{{c}}</option>
                    {% endfor %}
                </select>
            </div>

            <!-- State -->
            <div class="mb-3">
                <select class="form-select" id="state" name="state" required onchange="loadDistricts()">
                    <option value="">Select State</option>
                </select>
            </div>

            <!-- District -->
            <div class="mb-3">
                <select class="form-select" id="district" name="district" required>
                    <option value="">Select District</option>
                </select>
            </div>

            <!-- Area -->
            <div class="mb-3">
                <input class="form-control" name="area" placeholder="Area / Locality" required>
            </div>

            <button class="btn btn-primary w-100">Submit Application</button>
        </form>
    </div>
</div>

<script>
const locationData = {{ location_data | tojson }};

function loadStates() {
    let country = document.getElementById("country").value;
    let stateSelect = document.getElementById("state");
    let districtSelect = document.getElementById("district");

    stateSelect.innerHTML = '<option value="">Select State</option>';
    districtSelect.innerHTML = '<option value="">Select District</option>';

    if (country && locationData[country]) {
        Object.keys(locationData[country]).forEach(state => {
            let opt = document.createElement("option");
            opt.value = state;
            opt.textContent = state;
            stateSelect.appendChild(opt);
        });
    }
}

function loadDistricts() {
    let country = document.getElementById("country").value;
    let state = document.getElementById("state").value;
    let districtSelect = document.getElementById("district");

    districtSelect.innerHTML = '<option value="">Select District</option>';

    if (country && state && locationData[country][state]) {
        locationData[country][state].forEach(d => {
            let opt = document.createElement("option");
            opt.value = d;
            opt.textContent = d;
            districtSelect.appendChild(opt);
        });
    }
}
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
