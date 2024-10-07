import uvicorn
from fastapi import FastAPI
from infrastracture.api.user_routers import user_router

app = FastAPI()
app.include_router(user_router, prefix="/api/user", tags=['authentication'])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8083)
