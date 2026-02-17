# Flask UI Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/sandyworkstation/Downloads/beInformed
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

#### Option A: Using PostgreSQL.app (Recommended for Mac)
1. Download and install [Postgres.app](https://postgresapp.com/)
2. Start PostgreSQL
3. Create database:
```bash
createdb beInformed
```

#### Option B: Using Homebrew
```bash
brew install postgresql
brew services start postgresql
createdb beInformed
```

#### Option C: Using Docker
```bash
docker run --name beinformed-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=beInformed -p 5432:5432 -d postgres
```

### 3. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and update the `DATABASE_URL`:
```
DATABASE_URL=postgresql://localhost/beInformed
# Or with username/password:
# DATABASE_URL=postgresql://username:password@localhost/beInformed
```

### 4. Initialize Database

The database tables will be created automatically when you first run the app.

### 5. Run the Flask Application

```bash
python app.py
```

The application will be available at: **http://localhost:5001**

## Features

### Tab 1: Daily Trade Calls 📈
- Click "Generate New Calls" to get AI-powered trade recommendations
- View market indicators:
  - **Gold/Nifty Ratio**: Indicates whether it's a good time to invest in stocks
  - **VIX**: Fear index showing market volatility
  - **Put-Call Ratio**: Market sentiment indicator
  - **FII/DII Net**: Foreign and domestic institutional investor positions
- Each trade call shows:
  - Entry price, target price, and stop loss
  - Potential gain percentage
  - Conviction score (0-100)
  - Detailed reasoning

### Tab 2: Performance Tracking 📊
- View all trade calls for the day
- Track performance with:
  - Total calls made
  - Winning vs losing trades
  - Average gain/loss percentage
  - Total P&L
- Close trades by clicking "Close Trade" and entering exit price
- Filter by date using the date picker

### Tab 3: Conviction Analysis 🔍
- Enter a stock symbol (e.g., ITC, HCLTECH)
- Click "Analyze" to get:
  - Transcript summary from earnings calls
  - Key insights extracted
  - Conviction factors (revenue growth, margins, order book)
  - Overall conviction score
  - Sentiment analysis

## Using Mock Data

Currently, the application uses **mock data** for:
- Stock prices
- Market indicators
- Transcript analysis

This allows you to test the UI and database functionality without needing real-time data APIs.

## Next Steps: Integrating Real Data

Once you find a free stock price API, you can update:

1. **`mock_data.py`** - Replace mock functions with real API calls
2. **`market_data.py`** (create this) - Add functions to fetch:
   - Gold prices from NSE or commodity APIs
   - Nifty 50 data
   - VIX from NSE
   - FII/DII data from NSE website

Example structure for `market_data.py`:
```python
import requests

def get_nifty_data():
    # Call NSE API or scrape NSE website
    pass

def get_gold_price():
    # Call commodity API
    pass
```

## Troubleshooting

### Database Connection Error
If you see `could not connect to server`, ensure PostgreSQL is running:
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (if using Homebrew)
brew services start postgresql
```

### Port Already in Use
If port 5000 is busy, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Database Schema

The application creates 4 tables:
- **trade_calls**: Stores trade recommendations
- **trade_performance**: Tracks actual trade results
- **market_indicators**: Daily market ratios
- **conviction_insights**: Stock analysis data

To view the database:
```bash
psql beInformed
\dt  # List tables
SELECT * FROM trade_calls;  # View trade calls
```

## Development Notes

- The UI uses **dark mode** with glassmorphism effects
- All API endpoints return JSON
- Frontend uses vanilla JavaScript (no frameworks)
- Database operations use SQLAlchemy ORM
- Mock data is deterministic for testing consistency
