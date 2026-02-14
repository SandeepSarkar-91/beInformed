# Indian Trading Agent

A powerful, safety-first trading agent designed for Indian markets. It integrates technical filters, qualitative analysis from Screener.in, and manual email approval to manage a balanced portfolio based on market states.

## 🚀 Core Trading Logic

The agent follows a strict multi-layer filter before proposing any trade:

1.  **Market State Filter:** Analyzes Nifty 50 movement to categorize the market into **UP, DOWN, or FLAT**.
2.  **Watchlist Filter:** Maps the market state to your specific philosophy-based watchlist (Gold vs. Dividends vs. Monopoly/Growth).
3.  **Technical Filter (200 DMA):** Only proposes trades if the current price is **below the 200-day Moving Average** (protects against buying at the peak).
4.  **Qualitative Filter (Screener.in):** Scrapes **Screener.in** for the latest announcements/con-call summaries to veto trades if negative news (e.g., losses, defaults) is found.
5.  **Manual Approval:** Sends a trade proposal to your email. No trade is placed without a physical click on "Approve".

---

## 🛠️ Components

- [main.py] The FastAPI-based orchestrator. It handles the proposal flow and the approval webhook.
- [analyzer.py]: The "Brain" of the agent. Enforces market states, 200 DMA rules, and symbol restrictions.
- [transcripts.py]: The "Researcher". Scrapes Screener.in company pages for announcements and AI con-call summaries.
- [broker_manager.py]: Handles API communication. Currently supports a skeletal **HDFC Sky** integration (Free API).
- [safety_manager.py]: (Part of broker_manager) Enforces the ₹10,000 capital limit and ₹500 daily loss protection.

---

## ⚙️ Configuration & Customization

### 1. Trading Philosophy (`context.md`)
Update [context.md] to change your:
- **Watchlist symbols**
- **Trade rules** (e.g., risk appetite per trade)
- **Market View logic**

### 2. API Choice
We recommend **HDFC Sky** because its Trading APIs are **Free**. 
- To use **Zerodha (~₹2000/mo)**, update the `Broker` class in `broker_manager.py` to use `kiteconnect`.

### 3. Environment Setup (`.env`)
Create a `.env` file based on `.env.example`:
```bash
HDFC_API_KEY=...
EMAIL_SMTP_SERVER=...
NGROK_URL=... # Required for email approval links to work back to your local machine
```

---

## 📋 How to Run

1.  **Install dependencies:**
    ```bash
    python3 -m pip install fastapi uvicorn requests beautifulsoup4 python-dotenv
    ```
2.  **Start the server:**
    ```bash
    python3 main.py
    ```
3.  **Trigger a scan:**
    Post to `http://localhost:8000/propose_trades?nifty_change=-0.01` (e.g., `-0.01` for 1% down) to generate a proposal based on your philosophy.

---

## 🛡️ Safety & Risk
- **Total Capital:** ₹10,000
- **Daily SL:** ₹500
- **Verification:** Always verify the proposal in your email before clicking Approve.