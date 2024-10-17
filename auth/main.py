import uvicorn
from fastapi import FastAPI

from auth.services.handlers.user import user_router
from auth.services.email import get_dir

app = FastAPI()
app.include_router(user_router, prefix="/api/user", tags=['authentication'])


if __name__ == "__main__":
    get_dir()
    uvicorn.run("main:app", reload=True, port=8083)
