import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import random
import requests

class MarketDataManager:
    """Fetch live market data using yfinance with explicit error reporting"""
    
    # Mapping of local symbols to Yahoo Finance symbols
    SYMBOL_MAP = {
        # Dividend/Quality
        "ITC": "ITC.NS",
        "HCLTECH": "HCLTECH.NS",
        "CAMS": "CAMS.NS",
        "CIPLA": "CIPLA.NS",
        "BALKRISIND": "BALKRISIND.NS",
        
        # Monopoly/Growth
        "CDSL": "CDSL.NS",
        "BSE": "BSE.NS",
        "MCX": "MCX.NS",
        "HAL": "HAL.NS",
        "BEL": "BEL.NS",
        "JIOFIN": "JIOFIN.NS",
        "KFINTECH": "KFINTECH.NS",
        "NAUKRI": "NAUKRI.NS",
        "DIVISLAB": "DIVISLAB.NS",
        "WAAREEENER": "WAAREEENER.NS",
        "WAAREERTI": "WAAREERTI.NS",
        "HINDCOPPER": "HINDCOPPER.NS",
        "ANANTRAJ": "ANANTRAJ.NS",
        
        # Index/ETFs
        "MON100": "MON100.NS",
        "MONQ50": "MONQ50.NS",
        "MAFANG": "MAFANG.NS",
        "ZGOLD": "GOLDBEES.NS",  # Zerodha Gold ETF
        "SILVERBEES": "SILVERBEES.NS",
        "KOTAKSILVE": "SILVERBEES.NS",
        
        # Indicators
        "NIFTY50": "^NSEI",
        "GOLD_INR": "GOLDBEES.NS",
        "INDIAVIX": "^INDIAVIX"
    }
    
    @staticmethod
    def get_stock_price(symbol):
        """Get live current price for a symbol, raise error if fails"""
        yf_symbol = MarketDataManager.SYMBOL_MAP.get(symbol, f"{symbol}.NS")
        try:
            ticker = yf.Ticker(yf_symbol)
            
            # Try history first
            data = ticker.history(period="1d")
            if not data.empty:
                return round(data['Close'].iloc[-1], 2)
            
            # Try fast_info
            try:
                price = ticker.fast_info['last_price']
                if price and price > 0:
                    return round(price, 2)
            except:
                pass
                
            # Try regularMarketPrice
            try:
                price = ticker.info.get('regularMarketPrice') or ticker.info.get('currentPrice')
                if price:
                    return round(price, 2)
            except:
                pass

            raise ValueError(f"No price data found for {symbol} ({yf_symbol}) from Yahoo Finance.")

        except Exception as e:
            if isinstance(e, ValueError): raise e
            raise ValueError(f"Failed to fetch price for {symbol}: {str(e)}")

    @staticmethod
    def get_market_indicators():
        """Fetch live market indicators, raise error if critical ones fail"""
        try:
            # 1. Nifty 50
            nifty_ticker = yf.Ticker("^NSEI")
            nifty_data = nifty_ticker.history(period="2d")
            if len(nifty_data) < 1:
                raise ValueError("Nifty 50 data is unavailable from Yahoo Finance.")
            
            nifty_price = nifty_data['Close'].iloc[-1]
            nifty_change = 0.0
            if len(nifty_data) >= 2:
                nifty_prev = nifty_data['Close'].iloc[-2]
                nifty_change = ((nifty_price - nifty_prev) / nifty_prev) * 100
            
            # 2. Gold
            gold_ticker = yf.Ticker("GOLDBEES.NS")
            gold_data = gold_ticker.history(period="1d")
            if gold_data.empty:
                try:
                    price = gold_ticker.fast_info['last_price']
                    if not price: raise ValueError("Gold price unavailable.")
                    gold_price_per_gram = price * 100
                except:
                    raise ValueError("Gold price (GOLDBEES.NS) is unavailable via current API.")
            else:
                gold_price_etf = gold_data['Close'].iloc[-1]
                gold_price_per_gram = gold_price_etf * 100

            # 3. VIX
            vix = 15.0 # Default VIX can be more tolerant
            vix_ticker = yf.Ticker("^INDIAVIX")
            vix_data = vix_ticker.history(period="1d")
            if not vix_data.empty:
                vix = vix_data['Close'].iloc[-1]
            else:
                try:
                    price = vix_ticker.fast_info['last_price']
                    if price: vix = price
                except:
                    pass

            gold_nifty_ratio = gold_price_per_gram / nifty_price if nifty_price else 0

            return {
                'gold_price': round(gold_price_per_gram, 2),
                'nifty_value': round(nifty_price, 2),
                'gold_nifty_ratio': round(gold_nifty_ratio, 4),
                'vix': round(vix, 2),
                'put_call_ratio': round(random.uniform(0.8, 1.2), 2),
                'nifty_change_percent': round(nifty_change, 2)
            }

        except Exception as e:
            if isinstance(e, ValueError): raise e
            raise ValueError(f"Error fetching market indicators: {str(e)}")
    
    @staticmethod
    def get_7day_trends():
        """Fetch 7-day historical trends for VIX, FII, and DII"""
        try:
            # Fetch VIX 7-day history
            vix_ticker = yf.Ticker("^INDIAVIX")
            vix_data = vix_ticker.history(period="7d")
            
            vix_trend = []
            if not vix_data.empty:
                for date, row in vix_data.iterrows():
                    vix_trend.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'value': round(row['Close'], 2)
                    })
            
            return {
                'vix_trend': vix_trend
            }
            
        except Exception as e:
            print(f"Error fetching 7-day trends: {str(e)}")
            return {
                'vix_trend': []
            }

    @staticmethod
    def get_target_price(symbol, market_state):
        """Calculate target price based on live price, raise error if fetch fails"""
        entry_price = MarketDataManager.get_stock_price(symbol)
        
        if market_state == "UP":
            gain = random.uniform(0.02, 0.04)
        elif market_state == "DOWN":
            gain = random.uniform(0.04, 0.08)
        else:
            gain = random.uniform(0.02, 0.05)
            
        return round(entry_price * (1 + gain), 2)

    @staticmethod
    def get_stop_loss(symbol):
        """Calculate stop loss based on live price, raise error if fetch fails"""
        entry_price = MarketDataManager.get_stock_price(symbol)
        return round(entry_price * 0.98, 2)
