# Lab 4 — Workstream F: Simulated QR Payment

A local, reproducible FastAPI implementation for the embedded-systems integration demo. It uses only in-memory state and the `DEMO` currency; it never connects to a real payment provider or asks for real credentials.

## Run it

```bash
cd qr_payment_lab4
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://<checkout-laptop-ip>:8000/` on the Checkout laptop. To complete the same-network test, scan the QR code with a phone connected to the same Wi-Fi/LAN, then choose **Pay Demo** or **Decline Demo**.

Use the laptop's LAN IP in the URL, not `localhost`, because the phone cannot resolve the laptop's loopback address. For example, find it with `hostname -I`.

## Provided Lab 4 values

The default counter values match `payment_cases.json`:

- Transaction: `TX-20260928-000045`
- Amount: `6.80 DEMO`
- Token: `PAY-SIM-000123`
- Approve: `DEMO-APPROVE`
- Decline: `DEMO-DECLINE`

The token field is optional when using the API; if omitted, the server creates a unique `PAY-SIM-...` token. Keeping the provided token makes integration output deterministic.

## API contract

- `POST /api/payments` creates a QR payment in `PENDING_PAYMENT`, returns a phone URL and QR image URL.
- `GET /api/payments/{payment_token}/qr` returns a PNG QR code.
- `GET /api/payments/{payment_token}` returns payment and transaction status.
- `POST /api/payments/{payment_token}/confirm` accepts exactly `{"confirmation":"DEMO-APPROVE"}` or `{"confirmation":"DEMO-DECLINE"}`.
- After `DEMO-APPROVE`, the phone page redirects to `/receipt/{payment_token}`, a prominent **PAYMENT SENT** page showing date/time, amount, QR method, transaction ID, payment ID, and simulation reference.
- Reconfirming a token returns HTTP `409` with status `DUPLICATE`.
- `GET /api/transactions/{transaction_id}` exposes the transaction state.
- `POST /api/reset` clears the in-memory demo state between integration runs.

Success transitions to `PAYMENT_SUCCESS`; decline transitions to `PAYMENT_FAILED`. The normal sequence can be completed by the Checkout Counter group later with `COMPLETED` after its own receipt/completion step.

## Automated verification

```bash
cd qr_payment_lab4
. .venv/bin/activate
pytest -q
```

The tests cover QR PNG generation, pending state, approval, decline, duplicate confirmation, and same-token idempotency.
