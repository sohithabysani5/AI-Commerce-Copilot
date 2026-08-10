# AI Commerce Copilot 🛒🎙️

AI Commerce Copilot is an intelligent shopping assistant for products, orders, and customer service. It now features **Multilingual Voice-to-Voice** capabilities, supporting English, Telugu, and Hindi over both web (Streamlit) and telephony (Twilio).

## Features

*   **Multilingual Support**: English, Telugu, and Hindi via text, web voice, and phone.
*   **Web Interface (Streamlit)**: Text chat, dashboard, and a direct Voice AI recording tab.
*   **Telephony (Twilio)**: Call a phone number and talk directly to the agent.
*   **Commerce Logic**: Search products, place orders, track shipments, and cancel orders via a robust state machine.

## Prerequisites

1.  Python 3.9+
2.  Twilio Account (for telephony)
3.  Google API Key (for Gemini and Google Cloud STT/TTS if used)
4.  ngrok (for local webhook testing)

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Copy `.env.example` to `.env` and fill in your keys:
    ```bash
    cp .env.example .env
    ```
    *Make sure to set `GEMINI_API_KEY` and Twilio credentials.*

## Running the Web App

Start the Streamlit application:
```bash
streamlit run app.py
```
This will open the dashboard where you can interact via text or the **Voice AI** tab.

## Running the Telephony Webhook Server

To receive phone calls, you need to run the FastAPI webhook server:

1.  Start the FastAPI server:
    ```bash
    python webhook_server.py
    ```
2.  Expose the port using ngrok (default port 8000):
    ```bash
    ngrok http 8000
    ```
3.  Copy the ngrok forwarding URL (e.g., `https://abcdef.ngrok-free.app`) and update the `WEBHOOK_BASE_URL` in `.env`.
4.  Configure your Twilio Phone Number's incoming webhook to: `https://abcdef.ngrok-free.app/voice/incoming` (HTTP POST).
5.  Call the phone number to test!

## Testing

Run the test suite using `unittest`:
```bash
python -m unittest discover tests
```
