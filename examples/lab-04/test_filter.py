def test_filter_incidents_by_severity(client):
    for severity in ("critical", "low"):
        response = client.post("/incidents", json={"title": "Test filtra", "severity": severity})
        assert response.status_code == 201
    result = client.get("/incidents?severity=critical")
    assert result.status_code == 200
    assert len(result.json()) == 1
    assert result.json()[0]["severity"] == "critical"
    assert client.get("/incidents?severity=urgent").status_code == 422
    assert len(client.get("/incidents").json()) == 2
