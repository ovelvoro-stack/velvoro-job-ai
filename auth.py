from flask import session, redirect, url_for
import csv

def company_login(email, password):
    with open("data/companies.csv", newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            if r[1] == email and r[2] == password:
                return r
    return None

def login_required(role):
    if session.get("role") != role:
        return redirect(url_for("login"))
