from flask import session, redirect, url_for
from config import ADMIN_USERNAME, ADMIN_PASSWORD

def admin_login_check(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD
