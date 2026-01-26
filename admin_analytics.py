import csv
from collections import Counter, defaultdict

DATA_FILE = "data/applications.csv"

def load_applications():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r in reader:
            # company, name, role, exp, resume, score
            rows.append({
                "company": r[0],
                "role": r[2],
                "score": int(r[5])
            })
    return rows

def analytics_summary():
    data = load_applications()

    total = len(data)

    company_count = Counter(d["company"] for d in data)
    role_count = Counter(d["role"] for d in data)

    pass_count = sum(1 for d in data if d["score"] >= 60)
    fail_count = total - pass_count

    return {
        "total": total,
        "company_labels": list(company_count.keys()),
        "company_values": list(company_count.values()),

        "role_labels": list(role_count.keys()),
        "role_values": list(role_count.values()),

        "pass": pass_count,
        "fail": fail_count
    }
