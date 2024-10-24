import uvicorn
from auth.api.routers import app
from auth.core.config import settings

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8083)
