# original/test_app.py
from original.app import app

def test_index():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200

def test_chat():
    client = app.test_client()
    res = client.post("/chat", json={"message": "テスト"})
    assert res.status_code == 200
    assert "response" in res.json