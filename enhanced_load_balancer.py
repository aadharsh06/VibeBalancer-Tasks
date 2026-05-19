from contextlib import asynccontextmanager
from typing import Optional
import asyncio
import time

from fastapi import FastAPI
from fastapi import Response
import httpx
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import make_asgi_app
import psutil


BACKENDS = [
    {"id": "server1", "url": "http://127.0.0.1:8001/work"},
    {"id": "server2", "url": "http://127.0.0.1:8003/work"},
]

visited = 0
server_health = {backend["id"]: True for backend in BACKENDS}
active_by_backend = {backend["id"]: 0 for backend in BACKENDS}

request_counter = Counter(
    "total_requests",
    "Total number of requests sent to the load balancer",
)
total_errors_counter = Counter("total_errors", "Total number of errors returned")
active_connections = Gauge("active_connections", "Total number of active connections")
cpu_usage = Gauge("cpu_usage_percent", "Current cpu usage percent")
memory_usage_percent = Gauge("memory_usage_percent", "Current memory usage percent")

backend_requests = Counter(
    "backend_requests",
    "Requests forwarded to each backend server",
    ["backend"],
)
backend_errors = Counter(
    "backend_errors",
    "Failed forwarding attempts for each backend server",
    ["backend"],
)
backend_active_connections = Gauge(
    "backend_active_connections",
    "Active load balancer connections for each backend server",
    ["backend"],
)
backend_health = Gauge(
    "backend_health",
    "Backend health status, where 1 means healthy and 0 means unhealthy",
    ["backend"],
)
algorithm_requests = Counter(
    "algorithm_requests",
    "Requests handled by each load balancing algorithm",
    ["algorithm"],
)
request_duration = Histogram(
    "load_balancer_request_duration_seconds",
    "Time spent forwarding a load balancer request",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 15),
)


def healthy_backends():
    return [backend for backend in BACKENDS if server_health[backend["id"]]]


async def single_check(client, backend):
    try:
        response = await client.get(backend["url"], timeout=3.0)
        response.raise_for_status()
        server_health[backend["id"]] = True
        backend_health.labels(backend=backend["id"]).set(1)
    except Exception:
        server_health[backend["id"]] = False
        backend_health.labels(backend=backend["id"]).set(0)


async def check_health():
    async with httpx.AsyncClient() as client:
        while True:
            cpu_usage.set(psutil.cpu_percent(interval=None))
            memory_usage_percent.set(psutil.virtual_memory().percent)

            await asyncio.gather(*(single_check(client, backend) for backend in BACKENDS))
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for backend in BACKENDS:
        backend_health.labels(backend=backend["id"]).set(1)
        backend_active_connections.labels(backend=backend["id"]).set(0)

    health_task = asyncio.create_task(check_health())
    yield
    health_task.cancel()


lb = FastAPI(lifespan=lifespan)
lb.mount("/metrics", make_asgi_app())
client = httpx.AsyncClient()


def choose_backend(algorithm):
    global visited

    candidates = healthy_backends()
    if not candidates:
        return None

    if algorithm == "least_connections":
        return min(candidates, key=lambda backend: active_by_backend[backend["id"]])

    selected = candidates[visited % len(candidates)]
    visited = (visited + 1) % len(candidates)
    return selected


async def forward_to_backend(backend, delay):
    backend_id = backend["id"]
    target_url = f"{backend['url']}?delay={delay}"

    backend_requests.labels(backend=backend_id).inc()
    active_by_backend[backend_id] += 1
    active_connections.inc()
    backend_active_connections.labels(backend=backend_id).inc()

    try:
        response = await client.get(target_url, timeout=10.0)
        return Response(content=response.content, status_code=response.status_code)
    except Exception:
        backend_errors.labels(backend=backend_id).inc()
        total_errors_counter.inc()
        raise
    finally:
        active_by_backend[backend_id] -= 1
        active_connections.dec()
        backend_active_connections.labels(backend=backend_id).dec()


@lb.get("/work")
async def work(delay: Optional[int] = None, type: Optional[str] = None):
    request_counter.inc()

    algorithm = type or "round_robin"
    if algorithm not in {"round_robin", "least_connections"}:
        algorithm = "round_robin"
    algorithm_requests.labels(algorithm=algorithm).inc()

    if delay is None:
        delay = 0

    start_time = time.perf_counter()
    try:
        first_backend = choose_backend(algorithm)
        if first_backend is None:
            total_errors_counter.inc()
            return Response(content="503 Service Unavailable", status_code=503)

        try:
            return await forward_to_backend(first_backend, delay)
        except Exception:
            fallback_backend = next(
                (
                    backend
                    for backend in healthy_backends()
                    if backend["id"] != first_backend["id"]
                ),
                None,
            )
            if fallback_backend is None:
                return Response(content="503 Service Unavailable", status_code=503)

            try:
                return await forward_to_backend(fallback_backend, delay)
            except Exception:
                return Response(content="503 Service Unavailable", status_code=503)
    finally:
        request_duration.observe(time.perf_counter() - start_time)
