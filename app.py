from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Velvoro Job AI is running 🚀"}

@app.get("/health")
def health():
    return {"ok": True}

# Railway needs this
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
