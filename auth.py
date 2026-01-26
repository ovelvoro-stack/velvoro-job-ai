from flask import session, redirect, url_for
import csv, os

ADMIN_FILE = "data/admins.csv"

def check_login(username, password):
    with open(ADMIN_FILE, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if row[0] == username and row[1] == password:
                return True
    return False

def login_required():
    if not session.get("admin"):
        return redirect(url_for("login"))
