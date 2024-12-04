from fastapi import FastAPI
from fastapi_pagination import Page, add_pagination, paginate
from auth.api.handlers.user import user_router

app = FastAPI()
app.include_router(user_router, prefix="/api/user", tags=["authentication"])
add_pagination(app)