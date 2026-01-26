from flask import Blueprint, render_template, request, redirect, session

auth = Blueprint("auth", __name__)

ADMIN_USER = "admin"
ADMIN_PASS = "velvoro123"

@auth.route("/admin/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
    return render_template("admin_login.html")

@auth.route("/admin/logout")
def logout():
    session.clear()
    return redirect("/")
