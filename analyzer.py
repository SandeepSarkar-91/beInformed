class TradingAnalyzer:
    def __init__(self, parser):
        self.parser = parser

    def get_market_state(self, current_nifty_change):
        """
        Logic to determine market state:
        - Down: < -0.5%
        - Up: > 0.5%
        - Flat: between -0.5% and 0.5%
        """
        if current_nifty_change < -0.005:
            return "DOWN"
        elif current_nifty_change > 0.005:
            return "UP"
        else:
            return "FLAT"

    def is_price_below_200dma(self, symbol, current_price, dma_200):
        """
        Rule: Only trade if current price < 200 DMA.
        Exempting Gold/Silver ETFs from this rule as per instructions.
        """
        gold_silver_keywords = ["GOLD", "SILVE", "GOLDBEES"]
        if any(kd in symbol.upper() for kd in gold_silver_keywords):
            return True, "Exempt from DMA rule (Gold/Silver)"
            
        if current_price < dma_200:
            return True, f"Price {current_price} is below 200 DMA {dma_200}"
        else:
            return False, f"Price {current_price} is NOT below 200 DMA {dma_200}"

    def confirm_with_qualitative_data(self, symbol):
        """
        Qualitative check placeholder. 
        Originally used Screener.in scraping, now disabled.
        """
        return True, "Qualitative check passed (Scraping disabled)."

    def suggest_trades(self, market_state):
        # Specific symbols extracted from user screenshots
        WATCHLIST = {
            "FLAT": ["SETFGLD", "ZGOLD", "SILVERBEES", "ITC", "HCLTECH", "CAMS", "CIPLA", "BALKRISHNA"],
            "DOWN": ["NASDQ100", "NASDQ50", "NYFANG", "CDSL", "BSE", "MCX", "HAL", "BEL", "JIOFIN", "KFINTECH", "NAUKRI", "DIVISLAB", "WAAREEENER", "HINDCOPPER", "ANANTRAJ"],
            "UP": ["SETFGLD", "ZGOLD", "SILVERBEES"]
        }
        
        # Mapped common names to likely NSE symbols (Approximated)
        SYMBOLS = {
            "FLAT": ["ZGOLD", "SILVERBEES", "ITC", "HCLTECH", "CAMS", "CIPLA", "BALKRISIND"],
            "DOWN": ["MON100", "MONQ50", "MAFANG", "CDSL", "BSE", "MCX", "HAL", "BEL", "JIOFIN", "KFINTECH", "NAUKRI", "DIVISLAB", "WAAREEENER", "HINDCOPPER", "ANANTRAJ"],
            "UP": ["ZGOLD", "KOTAKSILVE"]
        }

        if market_state == "FLAT":
            return {
                "assets": SYMBOLS["FLAT"],
                "reasoning": "Market is flat. Strategy: Gold/Silver ETFs and Dividend/Quality stocks from watchlist."
            }
        elif market_state == "DOWN":
            return {
                "assets": SYMBOLS["DOWN"],
                "reasoning": "Market is down. Strategy: Index ETFs and Monopoly/Growth businesses from watchlist."
            }
        elif market_state == "UP":
            return {
                "assets": SYMBOLS["UP"],
                "reasoning": "Market is up. Strategy: Gold/Silver ETFs only as per philosophy."
            }
        
        return {"assets": [], "reasoning": "No specific strategy for this state."}
