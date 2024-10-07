import time
from typing import Dict
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

#
# async def token_response(token: str):
#     return {
#         "access_token": token
#     }
#
#
# async def signJWT(user_id: str) -> Dict[str, str]:
#     payload = {
#         "user_id": user_id,
#         "expires": time.time() + 900
#     }
#     token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return await token_response(token)


# async def decodeJWT(token: str) -> dict:
#     try:
#         decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         return decoded_token if decoded_token["expires"] >= time.time() else None # check if expiration time is valid
#     except Exception as e:
#         return {"error": e}


# async def refresh_token(payload: ...): # check payload
#     return jwt.encode(
#         payload = {
#             ...
#         }
#     )


