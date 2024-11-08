import uvicorn
from auth.api.routers import app

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8083)
