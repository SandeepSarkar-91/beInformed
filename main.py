import os
from dotenv import load_dotenv
from context_parser import ContextParser
from broker_manager import HDFCSkyBroker, SafetyManager
from email_manager import EmailManager
from analyzer import TradingAnalyzer
from fastapi import FastAPI, BackgroundTasks
import uvicorn

load_dotenv()

app = FastAPI(title="Indian Trading Agent")

# Global state (simulated for now)
broker = HDFCSkyBroker(
    api_key=os.getenv("HDFC_API_KEY"),
    api_secret=os.getenv("HDFC_API_SECRET")
)
safety = SafetyManager(total_capital=10000.0, max_daily_loss=500.0)
parser = ContextParser()
analyzer = TradingAnalyzer(parser)
email_mgr = EmailManager(
    smtp_server=os.getenv("EMAIL_SMTP_SERVER"),
    smtp_port=int(os.getenv("EMAIL_SMTP_PORT", 587)),
    sender_email=os.getenv("EMAIL_SENDER"),
    sender_password=os.getenv("EMAIL_PASSWORD"),
    receiver_email=os.getenv("EMAIL_RECEIVER")
)

pending_trades = []

@app.get("/")
def home():
    return {"status": "Trading Agent Active"}

@app.post("/propose_trades")
def propose_trades(nifty_change: float = 0.0):
    """
    1. Determine market state
    2. Suggest assets from watchlist
    3. Filter by 200 DMA
    4. Validate with Screener qualitative data
    5. Propose trade and send email
    """
    state = analyzer.get_market_state(nifty_change)
    suggestion = analyzer.suggest_trades(state)
    
    if not suggestion['assets']:
        return {"message": "No trades suggested for current market state."}

    valid_proposals = []
    for asset in suggestion['assets']:
        # Mock price and DMA for demo
        current_price = 1450.0 
        dma_200 = 1500.0
        
        # 1. DMA Check
        dma_safe, dma_msg = analyzer.is_price_below_200dma(asset, current_price, dma_200)
        if not dma_safe:
            print(f"Skipping {asset}: {dma_msg}")
            continue
            
        # 2. Qualitative Check (Screener)
        qual_safe, qual_msg = analyzer.confirm_with_qualitative_data(asset)
        if not qual_safe:
            print(f"Skipping {asset}: {qual_msg}")
            continue
            
        proposal = {
            "symbol": asset,
            "quantity": 5,
            "side": "BUY",
            "order_type": "MARKET",
            "reason": f"{suggestion['reasoning']} | {qual_msg}"
        }
        valid_proposals.append(proposal)
        break # Just propose one for now

    if not valid_proposals:
        return {"message": "No assets passed both technical (DMA) and qualitative (Screener) checks today."}

    proposal = valid_proposals[0]
    global pending_trades
    pending_trades = [proposal]
    
    # Send Email
    base_url = os.getenv("NGROK_URL", "http://localhost:8000")
    email_mgr.send_approval_email(
        proposal,
        approve_url=f"{base_url}/approve",
        reject_url=f"{base_url}/reject"
    )
    
    return {
        "message": f"Market state identified as {state}. Trades proposed and email sent.",
        "proposal": proposal
    }

@app.get("/approve")
def approve_trade(background_tasks: BackgroundTasks):
    global pending_trades
    if not pending_trades:
        return {"status": "error", "message": "No pending trades"}
    
    for trade in pending_trades:
        # Safety check
        is_safe, msg = safety.check_trade_safety(trade['quantity'] * 2500) # Mock price
        if is_safe:
            background_tasks.add_task(
                broker.place_order, 
                trade['symbol'], 
                trade['quantity'], 
                trade['side'], 
                trade['order_type']
            )
        else:
            print(f"Safety Block: {msg}")
            
    pending_trades = []
    return {"status": "Trade approved and execution started"}

@app.get("/reject")
def reject_trade():
    global pending_trades
    pending_trades = []
    return {"status": "Trades rejected"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
