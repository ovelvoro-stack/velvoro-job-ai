from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Velvoro Job AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "RUNNING",
        "service": "Velvoro Job AI",
        "message": "Job Application & AI Screening Backend Live"
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/apply")
def apply_job(data: dict):
    return {
        "result": "Application received",
        "next": "AI Screening Pending"
    }
