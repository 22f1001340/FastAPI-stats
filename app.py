from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid
from collections import deque

EMAIL = "22f1001340@ds.study.iitm.ac.in"

app = FastAPI()

# Startup time
START_TIME = time.time()

# Prometheus counter
REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

# Keep last 1000 logs
LOGS = deque(maxlen=1000)


@app.middleware("http")
async def metrics_and_logs(request: Request, call_next):
    REQUEST_COUNTER.inc()

    request_id = str(uuid.uuid4())
    ts = time.time()

    response = await call_next(request)

    LOGS.append({
        "level": "INFO",
        "ts": ts,
        "path": request.url.path,
        "request_id": request_id
    })

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/work")
def work(n: int):
    # simulate work
    for _ in range(max(n, 0)):
        pass

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def logs_tail(limit: int = 10):
    if limit < 0:
        limit = 0
    return JSONResponse(list(LOGS)[-limit:])