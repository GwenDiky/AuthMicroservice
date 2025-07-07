FROM python:3.11.10-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt install -y netcat

RUN pip install poetry==1.8.2
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root


COPY docker-aws-entrypoint.sh ./

COPY docker-entrypoint.sh ./

COPY . .

RUN chmod +x ./docker-aws-entrypoint.sh ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
