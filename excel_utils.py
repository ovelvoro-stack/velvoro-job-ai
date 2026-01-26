import pandas as pd
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

CANDIDATES_FILE = f"{DATA_DIR}/candidates.xlsx"
APPLICATIONS_FILE = f"{DATA_DIR}/applications.xlsx"

def save_candidate(data):
    if os.path.exists(CANDIDATES_FILE):
        df = pd.read_excel(CANDIDATES_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(CANDIDATES_FILE, index=False)

def save_application(data):
    if os.path.exists(APPLICATIONS_FILE):
        df = pd.read_excel(APPLICATIONS_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(APPLICATIONS_FILE, index=False)
