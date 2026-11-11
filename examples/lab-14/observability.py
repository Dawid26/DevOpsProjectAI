"""Metryki odpowiedzi HTTP; jeden proces Uvicorn na kontener."""
from fastapi import Response
from prometheus_client import CollectorRegistry, Counter, generate_latest, CONTENT_TYPE_LATEST


def install_metrics(app):
    registry = CollectorRegistry()
    requests = Counter("incidentflow_http_responses_total", "Completed HTTP responses", ["method", "status"], registry=registry)

    @app.middleware("http")
    async def count_response(request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        code = "500"
        try:
            response = await call_next(request)
            code = str(response.status_code)
            return response
        finally:
            # Metoda i status mają ograniczony zbiór wartości. Nie etykietujemy ID ani tytułów.
            method = request.method if request.method in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"} else "OTHER"
            requests.labels(method, code).inc()

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(registry), headers={"Content-Type": CONTENT_TYPE_LATEST})
