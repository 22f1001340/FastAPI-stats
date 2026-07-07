from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

EMAIL = "22f1001340@ds.study.iitm.ac.in"

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-g0eqsv.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{duration:.6f}"

        return response


app.add_middleware(TimingMiddleware)


@app.get("/stats")
async def stats(values: str):
    nums = [int(x.strip()) for x in values.split(",") if x.strip()]

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }