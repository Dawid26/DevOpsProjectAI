def test_liveness(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_create_list_and_update(client):
    response = client.post(
        "/incidents", json={"title": "Database is slow", "severity": "high"}
    )
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 1
    assert created["status"] == "open"

    response = client.get("/incidents")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.patch("/incidents/1", json={"status": "investigating"})
    assert response.status_code == 200
    assert response.json()["status"] == "investigating"

    response = client.get("/incidents/1")
    assert response.json()["status"] == "investigating"


def test_invalid_severity_returns_422(client):
    response = client.post(
        "/incidents", json={"title": "Invalid severity", "severity": "urgent"}
    )
    assert response.status_code == 422


def test_missing_incident_returns_404(client):
    response = client.get("/incidents/999")
    assert response.status_code == 404
