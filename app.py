from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
@app.head("/")  # Add HEAD method support for health checks
def read_root():
    return {"message": "Hello World", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
