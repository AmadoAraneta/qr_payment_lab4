# Lab 4 Workstream F — VS Code Setup Guide

This guide explains how to run and test the **Simulated QR Payment** project using Visual Studio Code.

The project is a local demo only. It uses the `DEMO` currency and does not connect to a real payment provider.

---

## 1. What you need

Install these before starting:

1. **Visual Studio Code**
2. **Python 3.10 or newer**
3. A phone connected to the **same Wi-Fi network** as the computer running the project
4. A phone QR scanner or the phone camera app

In VS Code, it is also helpful to install the official **Python** extension by Microsoft:

1. Open VS Code.
2. Select the Extensions icon on the left side.
3. Search for `Python`.
4. Install **Python — Microsoft**.

---

## 2. Extract the project ZIP file

1. Download `qr_payment_lab4.zip`.
2. Extract it to a convenient location, such as:

   - Windows: `Documents\qr_payment_lab4`
   - macOS/Linux: `Documents/qr_payment_lab4`

3. Open VS Code.
4. Select **File > Open Folder**.
5. Select the extracted `qr_payment_lab4` folder.
6. Confirm that the VS Code Explorer shows these files:

```text
qr_payment_lab4/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── static/
│       ├── counter.html
│       ├── phone.html
│       └── receipt.html
├── tests/
│   └── test_api.py
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
└── VS_CODE_SETUP_GUIDE.md
```

Important: Open the **qr_payment_lab4 folder itself**, not only the ZIP file and not only the `app` folder.

---

## 3. Open the VS Code terminal

In VS Code, select:

```text
Terminal > New Terminal
```

A terminal panel will appear at the bottom of VS Code.

Check that the terminal is inside the project folder. You should see a path ending in something similar to:

```text
.../qr_payment_lab4
```

If not, change to the project folder with `cd`. Example:

### Windows PowerShell

```powershell
cd "$HOME\Documents\qr_payment_lab4"
```

### macOS/Linux

```bash
cd ~/Documents/qr_payment_lab4
```

You can confirm the location with:

```bash
python --version
```

or:

```bash
python3 --version
```

---

## 4. Create a Python virtual environment

A virtual environment keeps this project’s packages separate from other Python projects.

### Windows PowerShell

```powershell
py -m venv .venv
```

If `py` is unavailable, use:

```powershell
python -m venv .venv
```

### macOS/Linux

```bash
python3 -m venv .venv
```

After this command, a `.venv` folder should appear in the VS Code Explorer. It is normal for `.venv` to be hidden by `.gitignore` in some setups.

---

## 5. Activate the virtual environment

Run the command for your operating system and terminal.

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, open PowerShell as your normal user and run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

### macOS/Linux

```bash
source .venv/bin/activate
```

When activation works, the terminal usually shows `(.venv)` at the beginning of the prompt, for example:

```text
(.venv) C:\Users\YourName\Documents\qr_payment_lab4>
```

or:

```text
(.venv) user@computer:~/Documents/qr_payment_lab4$
```

---

## 6. Select the correct Python interpreter in VS Code

1. Press `Ctrl+Shift+P` on Windows/Linux or `Cmd+Shift+P` on macOS.
2. Search for **Python: Select Interpreter**.
3. Select the interpreter inside the project’s `.venv` folder.

The correct interpreter normally looks like:

- Windows: `.venv\Scripts\python.exe`
- macOS/Linux: `.venv/bin/python`

This step prevents VS Code from using a different Python installation that does not have the project packages.

---

## 7. Install the project packages

Make sure the virtual environment is activated, then run:

```bash
pip install -r requirements.txt
```

The important packages are:

- **FastAPI** — creates the payment API
- **Uvicorn** — runs the web server
- **qrcode** — generates the QR PNG image
- **pytest** — runs the automated tests

If your computer uses `pip3` instead of `pip`, run:

```bash
pip3 install -r requirements.txt
```

---

## 8. Run the automated tests

Before using the browser pages, verify the implementation with:

```bash
pytest -q
```

You should see output similar to:

```text
7 passed
```

The tests verify:

1. A payment starts in `PENDING_PAYMENT`.
2. A QR code is generated as a PNG image.
3. `DEMO-APPROVE` returns `SUCCESS`.
4. `DEMO-DECLINE` returns `FAILED`.
5. A repeated confirmation returns HTTP `409` and `DUPLICATE`.
6. Reusing the same payment token does not create a second payment.
7. A successful payment opens a Payment Sent receipt with the timestamp, amount, payment ID, transaction ID, and simulation reference.

If the tests fail with `No module named ...`, activate `.venv` and run `pip install -r requirements.txt` again.

---

## 9. Start the Checkout Counter server

For a test on the same Wi-Fi network, start the server on all network interfaces:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Keep this terminal running. Do not close it while testing.

You should see a message similar to:

```text
Uvicorn running on http://0.0.0.0:8000
```

The server is now running the Checkout Counter page and the mock payment API.

---

## 10. Open the Checkout Counter page

On the computer running VS Code, open a browser and visit:

```text
http://127.0.0.1:8000/
```

You should see:

- **Checkout Counter** heading
- Transaction ID field
- Amount field
- Payment token field
- Simulation-only warning
- **Generate QR payment** button

The default fields already use the Lab 4 values:

```text
Transaction ID: TX-20260928-000045
Amount: 6.80
Payment token: PAY-SIM-000123
Currency: DEMO
```

---

## 11. Find the computer’s local IP address

The phone must open the server using the computer’s local network address, not `localhost`.

### Windows

Open another VS Code terminal and run:

```powershell
ipconfig
```

Find the active Wi-Fi adapter and copy the **IPv4 Address**, usually similar to:

```text
192.168.1.25
```

### macOS

Run:

```bash
ipconfig getifaddr en0
```

If that returns nothing and you are using another network adapter, check the address in **System Settings > Network**.

### Linux

Run:

```bash
hostname -I
```

Use the address that starts with something like `192.168.x.x` or `10.x.x.x`.

Before scanning, test the address on the computer itself by opening:

```text
http://YOUR_LOCAL_IP:8000/
```

For example:

```text
http://192.168.1.25:8000/
```

---

## 12. Generate the QR code

1. On the Checkout Counter page, verify the default values.
2. Click **Generate QR payment**.
3. The application creates a payment in `PENDING_PAYMENT`.
4. A QR code appears.
5. The page displays the demo amount and says it is waiting for phone confirmation.

The QR code contains a URL similar to:

```text
http://192.168.1.25:8000/phone/PAY-SIM-000123
```

If it contains `127.0.0.1` or `localhost`, do not scan it from the phone. Open the Checkout Counter page using the computer’s local IP address first, then generate the QR code again.

---

## 13. Test a successful payment

1. Connect the phone to the same Wi-Fi network as the computer.
2. Scan the QR code with the phone camera or QR scanner.
3. Open the detected URL.
4. The mock phone page should show:

   - Transaction ID
   - Amount in `DEMO`
   - Payment method `QR`
   - Simulation-only warning
   - **Pay Demo** button
   - **Decline Demo** button

5. Confirm that the page does **not** ask for a card number, PIN, password, bank details, or wallet credentials.
6. Press **Pay Demo**.
7. Return to the Checkout Counter page.
8. Within a few seconds, the status should show:

```text
Payment SUCCESS · transaction PAYMENT_SUCCESS
```

9. On the phone, the approval message becomes prominent:

```text
PAYMENT APPROVED — opening receipt…
```

10. The phone automatically opens a separate **Payment Sent** receipt page. It shows:

   - **PAYMENT SENT**
   - Date and time
   - Amount: `6.80 DEMO`
   - Payment method: `QR`
   - Transaction ID
   - Payment ID
   - Simulation reference number

11. On the Checkout Counter, click **View Payment Receipt** if you want to open the same receipt again.

The API response should contain values similar to:

```json
{
  "payment_id": "PAYMENT-SIM-...",
  "transaction_id": "TX-20260928-000045",
  "method": "QR",
  "status": "SUCCESS",
  "amount": 6.8,
  "currency": "DEMO",
  "simulation_reference": "SIM-QR-000123"
}
```

---

## 14. Test a declined payment

The in-memory demo keeps state until it is reset or the server is restarted.

1. In a new terminal, reset the current demo:

```bash
curl -X POST http://127.0.0.1:8000/api/reset
```

On Windows PowerShell, this also works:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/reset
```

2. Refresh the Checkout Counter page.
3. Generate the QR code again.
4. Scan it with the phone.
5. Press **Decline Demo**.
6. The Checkout Counter should show:

```text
Payment FAILED · transaction PAYMENT_FAILED
```

The expected confirmation value for this scenario is:

```text
DEMO-DECLINE
```

---

## 15. Test duplicate confirmation

A payment token can only be confirmed once.

After pressing **Pay Demo** or **Decline Demo** once, press the same button again or send another confirmation request.

The second confirmation should return:

```text
HTTP 409 Conflict
```

with a response similar to:

```json
{
  "status": "DUPLICATE",
  "detail": "Payment token already confirmed"
}
```

This prevents a repeated phone action from creating another payment.

---

## 16. View the API documentation

FastAPI automatically provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

For a phone or another computer, replace `127.0.0.1` with the host computer’s local IP:

```text
http://YOUR_LOCAL_IP:8000/docs
```

Useful endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /api/payments` | Create a QR payment in `PENDING_PAYMENT` |
| `GET /api/payments/{payment_token}/qr` | Return the QR code PNG |
| `GET /api/payments/{payment_token}` | View payment status |
| `POST /api/payments/{payment_token}/confirm` | Approve or decline the demo payment |
| `GET /receipt/{payment_token}` | Display the Payment Sent receipt after success |
| `GET /api/transactions/{transaction_id}` | View transaction status |
| `POST /api/reset` | Clear the in-memory demo data |

---

## 17. Stop the server

Go back to the VS Code terminal running Uvicorn and press:

```text
Ctrl+C
```

The application stores data only in memory, so stopping the server clears the demo payments and transactions.

---

## 18. How to explain the files to your group

### `app/main.py`

Contains the FastAPI server, payment models, in-memory transaction storage, QR generation function, API endpoints, and state transitions.

### `app/static/counter.html`

The Checkout Counter page. It creates the QR payment and polls the API until the phone confirms or declines it.

### `app/static/phone.html`

The mock phone page. It displays payment information and provides the **Pay Demo** and **Decline Demo** actions.

### `tests/test_api.py`

Automated tests for the QR payment scenarios from the group’s `payment_cases.json` file.

### `requirements.txt`

The Python packages required to run the project.

### `README.md`

Short technical documentation and API contract for integration.

---

## 19. Suggested integration sequence for the group

During integration, the Checkout Counter group can call the QR API like this:

1. Send the transaction ID, method `QR`, amount `6.80`, currency `DEMO`, and an optional payment token to `POST /api/payments`.
2. Confirm the response status is `PENDING_PAYMENT`.
3. Display the returned QR image URL on the Checkout laptop.
4. Wait for the phone confirmation.
5. Poll `GET /api/payments/{payment_token}` until the payment is no longer `PENDING`.
6. If the payment status is `SUCCESS`, the transaction state is `PAYMENT_SUCCESS`.
7. If the payment status is `FAILED`, the transaction state is `PAYMENT_FAILED`.
8. The Checkout Counter group may continue its own receipt/completion step and change the final transaction state to `COMPLETED` after successful payment.

No real-money transaction is performed.

---

## 20. Common problems and fixes

### Problem: `uvicorn` is not recognized

Activate the virtual environment, then run:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Problem: `ModuleNotFoundError: No module named 'fastapi'`

Run:

```bash
pip install -r requirements.txt
```

Make sure `.venv` is activated first.

### Problem: The phone cannot open the QR URL

Check all of these:

1. The server was started with `--host 0.0.0.0`.
2. The phone and computer use the same Wi-Fi network.
3. The QR was generated after opening the Counter page through the computer’s LAN IP.
4. The computer firewall allows incoming connections on port `8000`.
5. The Wi-Fi network does not use client isolation or a guest network that blocks device-to-device connections.

### Problem: Port 8000 is already in use

Use another port:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Then open:

```text
http://127.0.0.1:8001/
```

The QR code will use the port from the page URL.

### Problem: The status does not update

Refresh the page and check that the phone confirmation completed. You can also inspect the current status at:

```text
http://127.0.0.1:8000/api/payments/PAY-SIM-000123
```

### Problem: A previous test says the payment is already confirmed

Reset the demo:

```bash
curl -X POST http://127.0.0.1:8000/api/reset
```

Or stop and restart Uvicorn.
