import uvicorn
from fastapi import FastAPI

from auth.api.handlers.mail import mail_router
from auth.api.handlers.user import user_router

app = FastAPI()
app.include_router(user_router, prefix="/api/user", tags=['authentication'])
app.include_router(mail_router, prefix="/messages", tags=['messages'])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8083)
