from fastapi import FastAPI
from auth.api.handlers.user import user_router

app = FastAPI()
app.include_router(user_router, prefix="/api/user", tags=['authentication'])