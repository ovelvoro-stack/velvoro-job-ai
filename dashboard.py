import csv

def company_stats(company_id):
    total = shortlisted = rejected = 0

    with open("data/applications.csv", newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            if r[0] == company_id:
                total += 1
                if int(r[6]) >= 60:
                    shortlisted += 1
                else:
                    rejected += 1

    return {
        "total": total,
        "shortlisted": shortlisted,
        "rejected": rejected
    }
