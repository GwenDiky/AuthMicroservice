import uvicorn
from fastapi import FastAPI
from auth.api.routers.user_routers import user_router
from auth.database.repo import UserRepository
import asyncio
from auth.core.settings import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(user_router, prefix="/api/user", tags=['authentication'])


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8083)
