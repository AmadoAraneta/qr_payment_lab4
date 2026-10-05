from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TX = "TX-20260928-000045"
TOKEN = "PAY-SIM-000123"


def setup_function():
    client.post("/api/reset")


def create():
    return client.post("/api/payments", json={
        "transaction_id": TX, "method": "QR", "amount": 6.80,
        "currency": "DEMO", "payment_token": TOKEN,
    })


def test_create_payment_is_pending_and_qr_is_png():
    response = create()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDING_PAYMENT"
    assert body["payment_token"] == TOKEN
    assert body["simulation_only"] is True
    qr = client.get(f"/api/payments/{TOKEN}/qr")
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/png"
    assert qr.content.startswith(b"\x89PNG")


def test_demo_approve_updates_payment_and_transaction():
    create()
    response = client.post(f"/api/payments/{TOKEN}/confirm", json={"confirmation": "DEMO-APPROVE"})
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert client.get(f"/api/transactions/{TX}").json()["status"] == "PAYMENT_SUCCESS"


def test_success_receipt_shows_payment_sent_details():
    create()
    client.post(f"/api/payments/{TOKEN}/confirm", json={"confirmation": "DEMO-APPROVE"})
    receipt = client.get(f"/receipt/{TOKEN}")
    assert receipt.status_code == 200
    assert "PAYMENT SENT" in receipt.text
    assert "6.80 DEMO" in receipt.text
    assert "SIM-QR-000123" in receipt.text
    assert "TX-20260928-000045" in receipt.text
    assert "PAYMENT-SIM-" in receipt.text


def test_receipt_is_not_available_before_success():
    create()
    assert client.get(f"/receipt/{TOKEN}").status_code == 409


def test_demo_decline_updates_failure_state():
    create()
    response = client.post(f"/api/payments/{TOKEN}/confirm", json={"confirmation": "DEMO-DECLINE"})
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"
    assert client.get(f"/api/transactions/{TX}").json()["status"] == "PAYMENT_FAILED"


def test_repeated_confirmation_returns_409_duplicate():
    create()
    assert client.post(f"/api/payments/{TOKEN}/confirm", json={"confirmation": "DEMO-APPROVE"}).status_code == 200
    duplicate = client.post(f"/api/payments/{TOKEN}/confirm", json={"confirmation": "DEMO-APPROVE"})
    assert duplicate.status_code == 409
    assert duplicate.json()["status"] == "DUPLICATE"


def test_payment_creation_is_idempotent_for_same_token():
    first = create().json()
    second = create()
    assert second.status_code == 200
    assert second.json()["payment_id"] == first["payment_id"]
    assert second.json()["reused"] is True
