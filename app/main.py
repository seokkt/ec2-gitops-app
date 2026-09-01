import os
import time

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI(
    title="EC2 GitOps Demo API",
    version="1.0.0",
)


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = time.time()

    response = await call_next(request)

    elapsed_time = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        endpoint=request.url.path,
    ).observe(elapsed_time)

    return response


@app.get("/")
def root():
    return {
        "service": "ec2-gitops-demo",
        "status": "running",
        "version": os.getenv("APP_VERSION", "local"),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/api/hello")
def hello():
    return {
        "message": "hello from EC2 GitOps project"
    }


@app.get("/healthz")
def health():
    return {
        "status": "ok"
    }


@app.get("/readyz")
def ready():
    return {
        "ready": True
    }


@app.get("/version")
def version():
    return {
        "version": os.getenv("APP_VERSION", "local")
    }


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )