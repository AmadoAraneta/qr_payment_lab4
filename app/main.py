from __future__ import annotations

import base64
import io
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import qrcode
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Lab 4 Simulated QR Payment", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# In-memory storage deliberately keeps this demo easy to run and reset.
transactions: dict[str, dict] = {}
payments_by_token: dict[str, dict] = {}

DEMO_APPROVE = "DEMO-APPROVE"
DEMO_DECLINE = "DEMO-DECLINE"


class PaymentRequest(BaseModel):
    transaction_id: str = Field(min_length=1)
    method: Literal["QR"] = "QR"
    amount: float = Field(gt=0)
    currency: Literal["DEMO"] = "DEMO"
    payment_token: str | None = None


class ConfirmationRequest(BaseModel):
    confirmation: Literal["DEMO-APPROVE", "DEMO-DECLINE"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_payment_token() -> str:
    return f"PAY-SIM-{secrets.token_hex(6).upper()}"


def new_payment_id() -> str:
    return f"PAYMENT-SIM-{secrets.token_hex(6).upper()}"


def simulation_reference(token: str) -> str:
    # Stable, readable reference for the payment result.
    suffix = token.removeprefix("PAY-SIM-")
    return f"SIM-QR-{suffix}"


def qr_bytes(url: str) -> bytes:
    code = qrcode.QRCode(version=None, box_size=10, border=4)
    code.add_data(url)
    code.make(fit=True)
    image = code.make_image(fill_color="black", back_color="white")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def payment_result(payment: dict, status: str) -> dict:
    return {
        "payment_id": payment["payment_id"],
        "transaction_id": payment["transaction_id"],
        "method": "QR",
        "status": status,
        "amount": payment["amount"],
        "currency": "DEMO",
        "simulation_reference": payment["simulation_reference"],
    }


@app.get("/", response_class=HTMLResponse)
def counter_page() -> HTMLResponse:
    return HTMLResponse((BASE_DIR / "static" / "counter.html").read_text())


@app.get("/phone/{payment_token}", response_class=HTMLResponse)
def phone_page(payment_token: str) -> HTMLResponse:
    payment = payments_by_token.get(payment_token)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment token not found")
    html = (BASE_DIR / "static" / "phone.html").read_text()
    return HTMLResponse(html.replace("__PAYMENT_TOKEN__", payment_token))


@app.get("/receipt/{payment_token}", response_class=HTMLResponse)
def receipt_page(payment_token: str) -> HTMLResponse:
    payment = payments_by_token.get(payment_token)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment token not found")
    if payment["status"] != "SUCCESS":
        raise HTTPException(status_code=409, detail="Receipt is available only after a successful demo payment")
    html = (BASE_DIR / "static" / "receipt.html").read_text()
    replacements = {
        "__TRANSACTION_ID__": payment["transaction_id"],
        "__PAYMENT_ID__": payment["payment_id"],
        "__AMOUNT__": f'{payment["amount"]:.2f}',
        "__CURRENCY__": payment["currency"],
        "__REFERENCE__": payment["simulation_reference"],
        "__CONFIRMED_AT__": payment["confirmed_at"],
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return HTMLResponse(html)


@app.post("/api/payments")
def create_payment(payload: PaymentRequest, request: Request) -> dict:
    transaction = transactions.get(payload.transaction_id)
    if transaction and transaction["amount"] != payload.amount:
        raise HTTPException(status_code=409, detail="Transaction amount mismatch")
    if transaction and transaction["status"] not in {"PENDING_PAYMENT"}:
        raise HTTPException(status_code=409, detail="Transaction is no longer payable")

    token = payload.payment_token or new_payment_token()
    existing = payments_by_token.get(token)
    if existing:
        if existing["transaction_id"] != payload.transaction_id:
            raise HTTPException(status_code=409, detail="Payment token already belongs to another transaction")
        return {**existing["request_response"], "reused": True}

    transactions[payload.transaction_id] = {
        "transaction_id": payload.transaction_id,
        "amount": payload.amount,
        "currency": payload.currency,
        "status": "PENDING_PAYMENT",
        "updated_at": now_iso(),
    }
    payment = {
        "payment_id": new_payment_id(),
        "transaction_id": payload.transaction_id,
        "method": "QR",
        "status": "PENDING",
        "amount": payload.amount,
        "currency": payload.currency,
        "payment_token": token,
        "simulation_reference": simulation_reference(token),
        "created_at": now_iso(),
    }
    phone_url = str(request.base_url).rstrip("/") + f"/phone/{token}"
    payment["phone_url"] = phone_url
    response = {
        "transaction_id": payload.transaction_id,
        "method": "QR",
        "amount": payload.amount,
        "currency": payload.currency,
        "payment_token": token,
        "payment_id": payment["payment_id"],
        "status": "PENDING_PAYMENT",
        "phone_url": phone_url,
        "qr_image_url": f"/api/payments/{token}/qr",
        "simulation_only": True,
    }
    payment["request_response"] = response
    payments_by_token[token] = payment
    return response


@app.get("/api/payments/{payment_token}/qr")
def payment_qr(payment_token: str) -> Response:
    payment = payments_by_token.get(payment_token)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment token not found")
    return Response(content=qr_bytes(payment["phone_url"]), media_type="image/png")


@app.get("/api/payments/{payment_token}")
def payment_status(payment_token: str) -> dict:
    payment = payments_by_token.get(payment_token)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment token not found")
    tx = transactions[payment["transaction_id"]]
    return {**payment_result(payment, payment["status"]), "transaction_status": tx["status"]}


@app.post("/api/payments/{payment_token}/confirm")
def confirm_payment(payment_token: str, payload: ConfirmationRequest) -> dict:
    payment = payments_by_token.get(payment_token)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment token not found")
    if payment["status"] != "PENDING":
        # A repeated confirmation must not create another payment.
        return Response(status_code=409, content='{"status":"DUPLICATE","detail":"Payment token already confirmed"}', media_type="application/json")

    success = payload.confirmation == DEMO_APPROVE
    payment["status"] = "SUCCESS" if success else "FAILED"
    if success:
        payment["confirmed_at"] = now_iso()
    tx = transactions[payment["transaction_id"]]
    tx["status"] = "PAYMENT_SUCCESS" if success else "PAYMENT_FAILED"
    tx["updated_at"] = now_iso()
    return payment_result(payment, payment["status"])


@app.get("/api/transactions/{transaction_id}")
def transaction_status(transaction_id: str) -> dict:
    transaction = transactions.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/api/reset")
def reset_demo() -> dict:
    transactions.clear()
    payments_by_token.clear()
    return {"reset": True}
