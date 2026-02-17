import random
from datetime import datetime, timedelta

class MockDataGenerator:
    """Generate realistic mock data for testing"""
    
    # Mock stock prices (realistic ranges for Indian stocks)
    STOCK_PRICES = {
        "ITC": 450.50,
        "HCLTECH": 1820.30,
        "CAMS": 4250.00,
        "CIPLA": 1450.75,
        "BALKRISIND": 2890.20,
        "CDSL": 1650.40,
        "BSE": 3200.50,
        "MCX": 2450.30,
        "HAL": 4100.80,
        "BEL": 285.60,
        "JIOFIN": 320.40,
        "KFINTECH": 1180.50,
        "NAUKRI": 7250.30,
        "DIVISLAB": 5680.20,
        "WAAREEENER": 2850.40,
        "SETFGLD": 6800.00,
        "ZGOLD": 68.50,
        "SILVERBEES": 82.30
    }
    
    @staticmethod
    def get_stock_price(symbol):
        """Get mock current price for a symbol"""
        base_price = MockDataGenerator.STOCK_PRICES.get(symbol, 1000.0)
        # Add some random variation (±2%)
        variation = random.uniform(-0.02, 0.02)
        return round(base_price * (1 + variation), 2)
    
    @staticmethod
    def get_target_price(entry_price, market_state):
        """Calculate target price based on market state"""
        if market_state == "UP":
            gain = random.uniform(0.02, 0.05)  # 2-5% gain
        elif market_state == "DOWN":
            gain = random.uniform(0.03, 0.08)  # 3-8% gain (buying dip)
        else:  # FLAT
            gain = random.uniform(0.015, 0.04)  # 1.5-4% gain
        
        return round(entry_price * (1 + gain), 2)
    
    @staticmethod
    def get_stop_loss(entry_price):
        """Calculate stop loss (2% below entry)"""
        return round(entry_price * 0.98, 2)
    
    @staticmethod
    def get_market_indicators():
        """Generate mock market indicators"""
        # Realistic values for Indian market
        gold_price = random.uniform(6500, 7200)  # Gold per 10g in INR
        nifty_value = random.uniform(23000, 24500)  # Nifty 50 range
        gold_nifty_ratio = gold_price / nifty_value
        
        return {
            'gold_price': round(gold_price, 2),
            'nifty_value': round(nifty_value, 2),
            'gold_nifty_ratio': round(gold_nifty_ratio, 4),
            'vix': round(random.uniform(12, 22), 2),  # VIX range
            'put_call_ratio': round(random.uniform(0.7, 1.3), 2),  # PCR
            'fii_net': round(random.uniform(-2000, 3000), 2),  # FII in crores
            'dii_net': round(random.uniform(-1000, 2500), 2),  # DII in crores
            'nifty_change_percent': round(random.uniform(-1.5, 1.5), 2)
        }
    
    @staticmethod
    def generate_trade_reasoning(symbol, market_state, conviction_score):
        """Generate realistic trade reasoning"""
        reasons = []
        
        if market_state == "DOWN":
            reasons.append(f"Market is down, buying quality stock {symbol} at discount")
            reasons.append("Price below 200 DMA - technical buy signal")
        elif market_state == "UP":
            reasons.append("Market rallying, taking position in defensive gold")
        else:  # FLAT
            reasons.append(f"Market consolidating, {symbol} showing relative strength")
            reasons.append("Dividend yield attractive in flat market")
        
        if conviction_score > 70:
            reasons.append("Strong fundamentals with revenue growth")
            reasons.append("Management guidance positive")
        elif conviction_score > 50:
            reasons.append("Stable business with consistent performance")
        
        return " | ".join(reasons)
    
    @staticmethod
    def generate_conviction_insights(symbol):
        """Generate mock conviction analysis"""
        revenue_growth = round(random.uniform(8, 25), 1)
        margin_trends = ["EXPANDING", "STABLE", "CONTRACTING"]
        order_book_strengths = ["STRONG", "MODERATE", "WEAK"]
        
        key_insights = [
            f"Revenue grew {revenue_growth}% YoY in latest quarter",
            "Operating margins improved by 150 bps",
            "Order book stands at ₹12,500 Cr (2.5x annual revenue)",
            "Management confident about maintaining growth trajectory",
            "Capacity expansion on track for Q3 FY26"
        ]
        
        conviction_factors = {
            "revenue_growth": revenue_growth,
            "margin_expansion": random.choice([True, False]),
            "order_book_strength": random.choice(order_book_strengths),
            "management_quality": random.randint(6, 10),
            "competitive_moat": random.randint(5, 9)
        }
        
        overall_score = random.randint(60, 95)
        
        sentiment = "POSITIVE" if overall_score > 70 else "NEUTRAL"
        
        transcript_summary = f"""
        {symbol} reported strong quarterly results with {revenue_growth}% revenue growth.
        Management highlighted robust order book and improving operational efficiency.
        Key focus areas include capacity expansion and market share gains.
        Guidance for next quarter remains optimistic with expected margin improvement.
        """
        
        return {
            'transcript_summary': transcript_summary.strip(),
            'key_insights': key_insights,
            'conviction_factors': conviction_factors,
            'overall_score': overall_score,
            'sentiment': sentiment,
            'revenue_growth': revenue_growth,
            'margin_trend': random.choice(margin_trends),
            'order_book_strength': random.choice(order_book_strengths)
        }
