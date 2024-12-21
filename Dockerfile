FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000

# Install Poetry
#RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
#    cd /usr/local/bin && \
#    ln -s /opt/poetry/bin/poetry && \
#    poetry config virtualenvs.create false

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && poetry config virtualenvs.create false;

WORKDIR /app

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./alembic.ini ./pyproject.toml ./poetry.lock* /app/
COPY ./migrations /app/migrations
COPY ./api /app/api

RUN poetry install --no-root --no-dev

COPY ./app .

