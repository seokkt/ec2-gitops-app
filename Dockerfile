FROM python:3.13-slim AS base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


FROM base AS test

COPY app ./app
COPY tests ./tests
COPY pytest.ini .

CMD ["python", "-m", "pytest", "-v"]


FROM base AS runtime

ARG APP_VERSION=unknown
ENV APP_VERSION=${APP_VERSION}

COPY app ./app

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
