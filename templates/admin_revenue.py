import csv
from collections import defaultdict

PAYMENT_FILE = "data/payments.csv"

def daily_revenue_data():
    revenue = defaultdict(int)

    with open(PAYMENT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            revenue[row["date"]] += int(row["amount"])

    # sort by date
    dates = sorted(revenue.keys())
    amounts = [revenue[d] for d in dates]

    return {
        "dates": dates,
        "amounts": amounts,
        "total": sum(amounts)
    }
