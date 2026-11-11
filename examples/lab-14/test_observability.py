from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.observability import install_metrics


def test_counts_success_and_failure_without_counting_scrapes():
    app = FastAPI()
    install_metrics(app)

    @app.get("/ok")
    def ok():
        return {"ok": True}

    @app.get("/unavailable")
    def unavailable():
        raise HTTPException(503, "Simulated")

    @app.get("/crash")
    def crash():
        raise RuntimeError("Simulated crash")

    client = TestClient(app, raise_server_exceptions=False)
    assert client.get("/ok").status_code == 200
    assert client.get("/unavailable").status_code == 503
    assert client.get("/crash").status_code == 500
    text = client.get("/metrics").text
    for code in ("200", "503", "500"):
        assert f'incidentflow_http_responses_total{{method="GET",status="{code}"}} 1.0' in text
    assert client.get("/metrics").text == text
