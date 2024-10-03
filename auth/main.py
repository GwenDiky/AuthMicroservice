import uvicorn
from fastapi import FastAPI
from auth.domain.entities.user import User
from fastapi.encoders import jsonable_encoder

app = FastAPI()


@app.post("/users/{user_id}")
async def create_user(user: User):
    return jsonable_encoder(user)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8081)
