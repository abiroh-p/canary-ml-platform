def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_predict_valid(client):
    resp = client.post("/predict", json={"features": [1.0, 2.0, 3.0, 4.0, 5.0]})
    assert resp.status_code == 200
    body = resp.json()
    assert "prediction" in body
    assert body["model_version_label"] == "stable"


def test_predict_empty_features_rejected(client):
    resp = client.post("/predict", json={"features": []})
    assert resp.status_code == 422