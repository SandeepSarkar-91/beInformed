from models import TradeCall, TradePerformance, MarketIndicators, ConvictionInsights, AnnualReportAnalysis, get_session
from datetime import datetime, timedelta
from sqlalchemy import func, desc

class DatabaseManager:
    """Helper class for database operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    # Trade Call operations
    def create_trade_call(self, symbol, recommendation, entry_price, target_price, 
                         stop_loss=None, reasoning="", market_state="FLAT", 
                         conviction_score=50, potential_gain_percent=0):
        """Create a new trade call"""
        try:
            # Convert to native Python types to avoid numpy/SQLAlchemy issues
            entry_price = float(entry_price) if entry_price is not None else None
            target_price = float(target_price) if target_price is not None else None
            stop_loss = float(stop_loss) if stop_loss is not None else None
            potential_gain_percent = float(potential_gain_percent) if potential_gain_percent is not None else 0
            conviction_score = int(conviction_score) if conviction_score is not None else 50

            trade_call = TradeCall(
                symbol=symbol,
                recommendation=recommendation,
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning=reasoning,
                market_state=market_state,
                conviction_score=conviction_score,
                potential_gain_percent=potential_gain_percent
            )
            self.session.add(trade_call)
            self.session.commit()
            return trade_call
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_todays_trade_calls(self):
        """Get all trade calls for today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.session.query(TradeCall).filter(
            TradeCall.call_date >= today_start
        ).all()
    
    def get_trade_calls_by_date(self, date):
        """Get trade calls for a specific date"""
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        return self.session.query(TradeCall).filter(
            TradeCall.call_date >= date_start,
            TradeCall.call_date < date_end
        ).all()
    
    # Trade Performance operations
    def record_trade_performance(self, trade_call_id, actual_entry_price, 
                                actual_exit_price=None, status='OPEN', notes=""):
        """Record or update trade performance"""
        performance = self.session.query(TradePerformance).filter_by(
            trade_call_id=trade_call_id
        ).first()
        
        if performance:
            # Update existing
            performance.actual_entry_price = actual_entry_price
            if actual_exit_price:
                performance.actual_exit_price = actual_exit_price
                performance.exit_time = datetime.now()
                performance.status = status
                # Calculate gain/loss
                performance.gain_loss_percent = (
                    (actual_exit_price - actual_entry_price) / actual_entry_price * 100
                )
                performance.gain_loss_amount = actual_exit_price - actual_entry_price
            performance.notes = notes
        else:
            # Create new
            performance = TradePerformance(
                trade_call_id=trade_call_id,
                actual_entry_price=actual_entry_price,
                actual_exit_price=actual_exit_price,
                status=status,
                notes=notes
            )
            if actual_exit_price:
                performance.exit_time = datetime.now()
                performance.gain_loss_percent = (
                    (actual_exit_price - actual_entry_price) / actual_entry_price * 100
                )
                performance.gain_loss_amount = actual_exit_price - actual_entry_price
            self.session.add(performance)
        
        self.session.commit()
        return performance
    
    def close_trade(self, trade_call_id, exit_price):
        """Close a trade and calculate performance"""
        return self.record_trade_performance(
            trade_call_id, 
            actual_entry_price=None,  # Will use existing
            actual_exit_price=exit_price,
            status='CLOSED'
        )

    def get_active_trades(self):
        """Get all trades that are not CLOSED or CANCELLED across all dates"""
        from sqlalchemy import or_
        from models import TradePerformance
        
        # Returns TradeCalls that:
        # 1. Have no performance record (default OPEN)
        # 2. Have a performance record with status 'OPEN'
        return self.session.query(TradeCall).outerjoin(
            TradePerformance, TradeCall.id == TradePerformance.trade_call_id
        ).filter(
            or_(
                TradePerformance.id == None,
                TradePerformance.status == 'OPEN'
            )
        ).all()
    
    def get_performance_summary(self, date=None):
        """Get performance summary for a date (default: today)"""
        if date is None:
            date = datetime.now()
        
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        trades = self.session.query(TradeCall).filter(
            TradeCall.call_date >= date_start,
            TradeCall.call_date < date_end
        ).all()
        
        total_calls = len(trades)
        closed_trades = [t for t in trades if t.performance and t.performance.status == 'CLOSED']
        winning_trades = [t for t in closed_trades if t.performance.gain_loss_percent > 0]
        losing_trades = [t for t in closed_trades if t.performance.gain_loss_percent < 0]
        
        avg_gain_loss = 0
        total_pnl = 0
        if closed_trades:
            avg_gain_loss = sum(t.performance.gain_loss_percent for t in closed_trades) / len(closed_trades)
            total_pnl = sum(t.performance.gain_loss_amount for t in closed_trades)
        
        return {
            'total_calls': total_calls,
            'closed_trades': len(closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_gain_loss_percent': avg_gain_loss,
            'total_pnl': total_pnl,
            'trades': trades
        }
    
    # Market Indicators operations
    def save_market_indicators(self, gold_price, nifty_value, gold_nifty_ratio=None, 
                              vix=None, put_call_ratio=None, fii_net=None, 
                              dii_net=None, nifty_change_percent=0):
        """Save market indicators for today"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Convert numpy types to Python native types to avoid PostgreSQL errors
        gold_price = float(gold_price) if gold_price is not None else None
        nifty_value = float(nifty_value) if nifty_value is not None else None
        gold_nifty_ratio = float(gold_nifty_ratio) if gold_nifty_ratio is not None else None
        vix = float(vix) if vix is not None else None
        put_call_ratio = float(put_call_ratio) if put_call_ratio is not None else None
        fii_net = float(fii_net) if fii_net is not None else None
        dii_net = float(dii_net) if dii_net is not None else None
        nifty_change_percent = float(nifty_change_percent) if nifty_change_percent is not None else 0
        
        # Check if already exists
        indicator = self.session.query(MarketIndicators).filter_by(date=today).first()
        
        # Calculate ratio if not provided
        if gold_nifty_ratio is None:
            gold_nifty_ratio = gold_price / nifty_value if nifty_value else 0
        
        # Determine sentiment
        sentiment = "NEUTRAL"
        if gold_nifty_ratio < 2.5:
            sentiment = "BULLISH"  # Good time for equities
        elif gold_nifty_ratio > 3.0:
            sentiment = "BEARISH"  # Risk-off, prefer gold
        
        if indicator:
            # Update existing
            indicator.gold_price = gold_price
            indicator.nifty_value = nifty_value
            indicator.gold_nifty_ratio = gold_nifty_ratio
            indicator.vix = vix
            indicator.put_call_ratio = put_call_ratio
            indicator.nifty_change_percent = nifty_change_percent
            indicator.market_sentiment = sentiment
        else:
            # Create new
            indicator = MarketIndicators(
                date=today,
                gold_price=gold_price,
                nifty_value=nifty_value,
                gold_nifty_ratio=gold_nifty_ratio,
                vix=vix,
                put_call_ratio=put_call_ratio,
                nifty_change_percent=nifty_change_percent,
                market_sentiment=sentiment
            )
            self.session.add(indicator)
        
        try:
            self.session.commit()
            return indicator
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_todays_market_indicators(self):
        """Get market indicators for today"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.session.query(MarketIndicators).filter_by(date=today).first()
    
    # Conviction Insights operations
    def save_conviction_insights(self, symbol, **analysis_data):
        """Save conviction analysis for a symbol"""
        # Extract fields needed for individual columns (backward compat)
        quarter = analysis_data.get('quarter')
        transcript_summary = analysis_data.get('transcript_summary')
        key_insights = analysis_data.get('key_insights')
        conviction_factors = analysis_data.get('conviction_factors')
        overall_score = analysis_data.get('overall_score', 0)
        sentiment = analysis_data.get('sentiment', 'NEUTRAL')
        revenue_growth = analysis_data.get('revenue_growth_val', analysis_data.get('revenue_growth', 0))
        # if revenue_growth is the dict from the new engine, try to get the float
        if isinstance(revenue_growth, dict):
            revenue_growth = revenue_growth.get('yoy_growth', 0)
            
        margin_trend = analysis_data.get('margin_trend', 'STABLE')
        order_book_strength = analysis_data.get('order_book_strength', 'MODERATE')

        insight = ConvictionInsights(
            symbol=symbol,
            quarter=quarter,
            transcript_summary=transcript_summary,
            key_insights=key_insights,
            conviction_factors=conviction_factors,
            overall_score=overall_score,
            sentiment=sentiment,
            revenue_growth=revenue_growth,
            margin_trend=margin_trend,
            order_book_strength=order_book_strength,
            full_analysis=analysis_data # Store everything
        )
        self.session.add(insight)
        self.session.commit()
        return insight
    
    def get_latest_conviction(self, symbol):
        """Get latest conviction analysis for a symbol"""
        from sqlalchemy import desc
        return self.session.query(ConvictionInsights).filter_by(
            symbol=symbol
        ).order_by(desc(ConvictionInsights.analysis_date)).first()

    def get_quarterly_conviction(self, symbol, quarter):
        """Check if analysis for symbol and quarter already exists"""
        return self.session.query(ConvictionInsights).filter_by(
            symbol=symbol, 
            quarter=quarter
        ).first()
    
    def get_all_convictions(self, limit=10):
        """Get recent conviction analyses"""
        from sqlalchemy import desc
        return self.session.query(ConvictionInsights).order_by(
            desc(ConvictionInsights.analysis_date)
        ).limit(limit).all()

    # Annual Report operations
    def save_annual_report_analysis(self, symbol, fiscal_year, analysis_data, overall_score, verdict):
        """Save annual report analysis"""
        analysis = AnnualReportAnalysis(
            symbol=symbol,
            fiscal_year=fiscal_year,
            analysis_data=analysis_data,
            overall_score=overall_score,
            verdict=verdict
        )
        self.session.add(analysis)
        self.session.commit()
        return analysis

    def get_latest_annual_report_analysis(self, symbol):
        """Get latest annual report analysis for a symbol"""
        return self.session.query(AnnualReportAnalysis).filter_by(
            symbol=symbol
        ).order_by(desc(AnnualReportAnalysis.analysis_date)).first()

    def get_annual_report_by_fy(self, symbol, fiscal_year):
        """Get analysis for specific symbol and FY"""
        return self.session.query(AnnualReportAnalysis).filter_by(
            symbol=symbol,
            fiscal_year=fiscal_year
        ).first()

    def get_transcript_history(self, limit=10):
        """Get recent transcript analyses"""
        return self.session.query(ConvictionInsights).order_by(
            desc(ConvictionInsights.analysis_date)
        ).limit(limit).all()

    def get_annual_report_history(self, limit=10):
        """Get recent annual report analyses"""
        return self.session.query(AnnualReportAnalysis).order_by(
            desc(AnnualReportAnalysis.analysis_date)
        ).limit(limit).all()

    def close(self):
        """Close the session"""
        self.session.close()
