import logging

from dotenv import load_dotenv
from fastapi.security import HTTPBearer

load_dotenv()
http_bearer = HTTPBearer()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
