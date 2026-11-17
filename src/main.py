from fastapi import FastAPI

app = FastAPI(title="Customer API")

@app.get("/health")
def health():
    return {"status": "ok"}