# The builder image, used to build the virtual environment
FROM python:3.11-bookworm as builder

RUN apt-get update && apt-get install -y git

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

ENV HOST=0.0.0.0
ENV LISTEN_PORT 8080
EXPOSE 8080

WORKDIR /app

#COPY pyproject.toml ./app/pyproject.toml
#COPY poetry.lock ./app/poetry.lock
COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-bookworm as runtime

RUN <<EOF
apt-get update
apt-get -y install sqlite3
apt-get -y install poppler-utils
EOF

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./app ./app
COPY ./.streamlit ./.streamlit

CMD ["streamlit", "run", "app/app.py", "--server.port", "8080"]
