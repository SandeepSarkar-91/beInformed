# Trading Context & Rules

## Goal
Gain maximum profits on a daily basis (Intraday) or Swing trading (up to 3 months).

## Capital
Total Investment: ₹10,000

## Allowed Watchlist (Philosophy Integrated)

- **Market State: FLAT (Gold & Dividends)**
    - **Gold/Silver:** SBI Gold ETF, Zerodha Gold, Kotak Silver ET
    - **Dividend/Quality:** ITC, HCL Tech, CAMS, Cipla, Balkrishna Ind, Fine Organics
- **Market State: DOWN (Index & Monopoly/Growth)**
    - **Index Funds:** MO Nasdaq Q50, MO NASDAQ 100, Mirae NYSEFANG
    - **Monopoly/Great Business:** CDSL, BSE Limited, MCX India, Hindustan Aeron (HAL), Bharat Elec (BEL), Jio Financial, KFin Tech, Info Edge, Divis Labs, Waaree Energies, Waaree Renewabl, Hind Copper, Anant Raj
    - **High Risk/Other:** Vodafone Idea, Billionbrains G, MO Defence
- **Market State: UP (Gold Only)**
    - **Gold:** SBI Gold ETF, Zerodha Gold, Kotak Silver ET

## How to Determine Market State

The agent uses **Nifty 50 daily percentage change** as the primary indicator:

- **Market DOWN**: Nifty 50 change < -0.5% (e.g., -0.8%, -1.2%)
- **Market UP**: Nifty 50 change > +0.5% (e.g., +0.7%, +1.5%)
- **Market FLAT**: Nifty 50 change between -0.5% and +0.5%

**Additional Confirmation (Recommended):**
- **For FLAT detection**: Check if Nifty 50 has been trading in a narrow range (±2%) for the last 5-7 trading days.
- **For trend confirmation**: Use 20 DMA vs 50 DMA crossover:
  - If 20 DMA > 50 DMA → Uptrend bias
  - If 20 DMA < 50 DMA → Downtrend bias

**Note:** The current implementation uses a simple daily % change. You can enhance it by fetching historical data and calculating moving averages for more robust state detection.

## Strategy & Instructions
- **Only trade in the symbols listed above.**
- **200 DMA Rule:** Only place trades if the current market price (CMP) is **less than** its 200-day Daily Moving Average (DMA). This applies to all symbols except Gold/Silver ETFs.
- Daily check: Determine if market is UP, DOWN, or FLAT using the logic above.
- Map the state to the corresponding sub-list in the "Allowed Watchlist".

## Safety Constraints
- Max loss per trade: 2% of capital per trade
- Max daily loss: ₹500
- Multi-day trend required for swing trades.
