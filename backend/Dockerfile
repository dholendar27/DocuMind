FROM python:3.11-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

EXPOSE 4321

CMD ["gunicorn", "-w","3", "0.0.0.0:4321", "main:app"]