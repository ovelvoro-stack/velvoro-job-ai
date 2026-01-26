import pandas as pd
import os
from config import EXCEL_DB

COLUMNS = [
    "Name","Phone","Email","Experience","Qualification",
    "Job Role","Country","State","District","Area",
    "AI Score","Result","Resume"
]

def init_db():
    if not os.path.exists(EXCEL_DB):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(EXCEL_DB, index=False)

def save_candidate(data):
    df = pd.read_excel(EXCEL_DB)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(EXCEL_DB, index=False)

def get_all_candidates():
    return pd.read_excel(EXCEL_DB).to_dict(orient="records")
