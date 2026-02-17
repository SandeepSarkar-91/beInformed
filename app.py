from flask import Flask, render_template, request, jsonify
from database import DatabaseManager
from mock_data import MockDataGenerator
from market_data import MarketDataManager
from analyzer import TradingAnalyzer
from context_parser import ContextParser
from transcripts import ScreenerScraper
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize components
parser = ContextParser()
analyzer = TradingAnalyzer(parser)
scraper = ScreenerScraper()
mock_data = MockDataGenerator()
market_data = MarketDataManager()


@app.route('/')
def index():
    """Main dashboard with tabs"""
    return render_template('index.html')


# ============= TAB 1: DAILY TRADE CALLS =============

@app.route('/api/generate_calls', methods=['POST'])
def generate_calls():
    """Generate trade calls based on market state"""
    try:
        # Get market state from request or use mock
        nifty_change = request.json.get('nifty_change', 0.0) if request.json else 0.0
        
        # Determine market state
        market_state = analyzer.get_market_state(nifty_change)
        
        # Get suggested assets
        suggestion = analyzer.suggest_trades(market_state)
        
        # Generate market indicators (Live)
        indicators_data = market_data.get_market_indicators()
        
        # Save market indicators to database
        db = DatabaseManager()
        db.save_market_indicators(**indicators_data)
        
        # Generate 3-5 trade calls
        trade_calls = []
        failed_symbols = []
        assets = suggestion['assets'][:5]  # Limit to 5
        
        for symbol in assets:
            try:
                entry_price = market_data.get_stock_price(symbol)
                target_price = market_data.get_target_price(symbol, market_state)
                stop_loss = market_data.get_stop_loss(symbol)
                
                conviction_score = 50 + (hash(symbol) % 40)  # Deterministic but varied
                potential_gain = ((target_price - entry_price) / entry_price) * 100
                
                reasoning = mock_data.generate_trade_reasoning(symbol, market_state, conviction_score)
                
                # Save to database
                trade_call = db.create_trade_call(
                    symbol=symbol,
                    recommendation="BUY",
                    entry_price=entry_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    reasoning=reasoning,
                    market_state=market_state,
                    conviction_score=conviction_score,
                    potential_gain_percent=round(potential_gain, 2)
                )
                
                trade_calls.append({
                    'id': trade_call.id,
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'potential_gain': round(potential_gain, 2),
                    'conviction_score': conviction_score,
                    'reasoning': reasoning,
                    'market_state': market_state
                })
            except Exception as e:
                # Log the error and skip this symbol
                print(f"Skipping {symbol} due to error: {str(e)}")
                failed_symbols.append({'symbol': symbol, 'error': str(e)})
                continue
        
        db.close()
        
        response_data = {
            'success': True,
            'market_state': market_state,
            'trade_calls': trade_calls,
            'market_indicators': indicators_data
        }
        
        # Add warning about failed symbols if any
        if failed_symbols:
            response_data['warnings'] = {
                'failed_symbols': failed_symbols,
                'message': f"Skipped {len(failed_symbols)} symbol(s) due to data fetch errors"
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/market_indicators', methods=['GET'])
def get_market_indicators():
    """Get today's market indicators"""
    try:
        db = DatabaseManager()
        indicators = db.get_todays_market_indicators()
        db.close()
        
        if indicators:
            return jsonify({
                'success': True,
                'indicators': {
                    'gold_price': indicators.gold_price,
                    'nifty_value': indicators.nifty_value,
                    'gold_nifty_ratio': indicators.gold_nifty_ratio,
                    'vix': indicators.vix,
                    'put_call_ratio': indicators.put_call_ratio,
                    'nifty_change_percent': indicators.nifty_change_percent,
                    'market_sentiment': indicators.market_sentiment
                }
            })
        else:
            # Generate and save live data
            indicators_data = market_data.get_market_indicators()
            
            db = DatabaseManager()
            db.save_market_indicators(**indicators_data)
            db.close()
            return jsonify({'success': True, 'indicators': indicators_data})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/7day_trends', methods=['GET'])
def get_7day_trends():
    """Get 7-day historical trends for VIX, FII, and DII"""
    try:
        trends = market_data.get_7day_trends()
        return jsonify({'success': True, 'trends': trends})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/todays_calls', methods=['GET'])
def get_todays_calls():
    """Get today's trade calls"""
    try:
        db = DatabaseManager()
        calls = db.get_todays_trade_calls()
        db.close()
        
        calls_data = [{
            'id': call.id,
            'symbol': call.symbol,
            'entry_price': call.entry_price,
            'target_price': call.target_price,
            'stop_loss': call.stop_loss,
            'potential_gain': call.potential_gain_percent,
            'conviction_score': call.conviction_score,
            'reasoning': call.reasoning,
            'market_state': call.market_state,
            'call_time': call.call_date.strftime('%H:%M')
        } for call in calls]
        
        return jsonify({'success': True, 'calls': calls_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/verify_prices', methods=['GET'])
def verify_prices():
    """Fetch all watchlist stock prices for verification"""
    try:
        # Get all unique symbols from analyzer watchlists
        all_symbols = set()
        for state in ["FLAT", "DOWN", "UP"]:
            suggestion = analyzer.suggest_trades(state)
            all_symbols.update(suggestion['assets'])
        
        # Fetch prices for all symbols
        price_data = []
        for symbol in sorted(all_symbols):
            try:
                price = market_data.get_stock_price(symbol)
                yf_symbol = market_data.SYMBOL_MAP.get(symbol, f"{symbol}.NS")
                price_data.append({
                    'symbol': symbol,
                    'yf_symbol': yf_symbol,
                    'price': price,
                    'status': 'success'
                })
            except Exception as e:
                price_data.append({
                    'symbol': symbol,
                    'yf_symbol': market_data.SYMBOL_MAP.get(symbol, f"{symbol}.NS"),
                    'price': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({'success': True, 'prices': price_data})
        

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============= TAB 2: TRADE PERFORMANCE =============

@app.route('/api/record_trade', methods=['POST'])
def record_trade():
    """Record a trade performance"""
    try:
        data = request.json
        trade_call_id = data.get('trade_call_id')
        actual_entry_price = data.get('actual_entry_price')
        
        db = DatabaseManager()
        performance = db.record_trade_performance(
            trade_call_id=trade_call_id,
            actual_entry_price=actual_entry_price,
            status='OPEN'
        )
        db.close()
        
        return jsonify({'success': True, 'performance_id': performance.id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/close_trade/<int:trade_call_id>', methods=['PUT'])
def close_trade(trade_call_id):
    """Close a trade and record exit price"""
    try:
        data = request.json
        exit_price = data.get('exit_price')
        
        db = DatabaseManager()
        
        # Get the trade call to get entry price
        trade_call = db.session.query(TradeCall).get(trade_call_id)
        
        performance = db.record_trade_performance(
            trade_call_id=trade_call_id,
            actual_entry_price=trade_call.entry_price,
            actual_exit_price=exit_price,
            status='CLOSED'
        )
        db.close()
        
        return jsonify({
            'success': True,
            'gain_loss_percent': performance.gain_loss_percent,
            'gain_loss_amount': performance.gain_loss_amount
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/performance_summary', methods=['GET'])
def get_performance_summary():
    """Get performance summary for a date"""
    try:
        date_str = request.args.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.now()
        
        db = DatabaseManager()
        summary = db.get_performance_summary(date)
        db.close()
        
        # Format trades data
        trades_data = []
        for trade in summary['trades']:
            trade_data = {
                'id': trade.id,
                'symbol': trade.symbol,
                'entry_price': trade.entry_price,
                'target_price': trade.target_price,
                'call_time': trade.call_date.strftime('%H:%M'),
                'status': 'OPEN',
                'gain_loss_percent': 0,
                'gain_loss_amount': 0
            }
            
            if trade.performance:
                trade_data['status'] = trade.performance.status
                trade_data['actual_entry_price'] = trade.performance.actual_entry_price
                trade_data['actual_exit_price'] = trade.performance.actual_exit_price
                trade_data['gain_loss_percent'] = trade.performance.gain_loss_percent or 0
                trade_data['gain_loss_amount'] = trade.performance.gain_loss_amount or 0
            
            trades_data.append(trade_data)
        
        return jsonify({
            'success': True,
            'summary': {
                'total_calls': summary['total_calls'],
                'closed_trades': summary['closed_trades'],
                'winning_trades': summary['winning_trades'],
                'losing_trades': summary['losing_trades'],
                'avg_gain_loss_percent': round(summary['avg_gain_loss_percent'], 2),
                'total_pnl': round(summary['total_pnl'], 2)
            },
            'trades': trades_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============= TAB 3: CONVICTION ANALYSIS =============

@app.route('/api/analyze_conviction', methods=['POST'])
def analyze_conviction():
    """Analyze a stock for conviction insights"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        
        # Generate mock conviction data
        conviction_data = mock_data.generate_conviction_insights(symbol)
        
        # Save to database
        db = DatabaseManager()
        insight = db.save_conviction_insights(
            symbol=symbol,
            **conviction_data
        )
        db.close()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': conviction_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conviction/<symbol>', methods=['GET'])
def get_conviction(symbol):
    """Get latest conviction analysis for a symbol"""
    try:
        db = DatabaseManager()
        insight = db.get_latest_conviction(symbol.upper())
        db.close()
        
        if insight:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'analysis': {
                    'transcript_summary': insight.transcript_summary,
                    'key_insights': insight.key_insights,
                    'conviction_factors': insight.conviction_factors,
                    'overall_score': insight.overall_score,
                    'sentiment': insight.sentiment,
                    'revenue_growth': insight.revenue_growth,
                    'margin_trend': insight.margin_trend,
                    'order_book_strength': insight.order_book_strength,
                    'analysis_date': insight.analysis_date.strftime('%Y-%m-%d %H:%M')
                }
            })
        else:
            return jsonify({'success': False, 'error': 'No analysis found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize database
    from models import init_db
    print("Initializing database...")
    init_db()
    print("Database initialized!")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
