from fastapi import FastAPI

from app.routes import dt , resume

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}

app.include_router(dt.router, prefix="/api", tags=["API"])
app.include_router(resume.router, prefix="/api", tags=["API"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)