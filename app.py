from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Velvoro Job AI is running 🚀"}
