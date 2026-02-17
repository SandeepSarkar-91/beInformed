// Trading Dashboard JavaScript

// Utility Functions
const showLoading = () => {
    document.getElementById('loadingOverlay').classList.add('active');
};

const hideLoading = () => {
    document.getElementById('loadingOverlay').classList.remove('active');
};

const formatCurrency = (value) => {
    return `₹${parseFloat(value).toFixed(2)}`;
};

const formatPercent = (value) => {
    const num = parseFloat(value);
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toFixed(2)}%`;
};

// Tab Switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;

        // Update active states
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(tabId).classList.add('active');

        // Load data for the tab
        if (tabId === 'tab1') {
            loadTodaysCalls();
            loadMarketIndicators();
        } else if (tabId === 'tab2') {
            loadPerformanceSummary();
        }
    });
});

// ============= TAB 1: DAILY TRADE CALLS =============

const loadMarketIndicators = async () => {
    try {
        const response = await fetch('/api/market_indicators');
        const data = await response.json();

        if (data.success) {
            const ind = data.indicators;

            // Update indicator values
            document.getElementById('goldNiftyRatio').textContent = ind.gold_nifty_ratio.toFixed(4);
            document.getElementById('vixValue').textContent = ind.vix.toFixed(2);
            document.getElementById('pcrValue').textContent = ind.put_call_ratio.toFixed(2);
            document.getElementById('marketSentiment').textContent = ind.market_sentiment;

            // Add trend indicators
            const goldNiftyTrend = ind.gold_nifty_ratio < 2.5 ? '📈 Bullish for Equities' :
                ind.gold_nifty_ratio > 3.0 ? '📉 Risk-Off Mode' : '➡️ Neutral';
            document.getElementById('goldNiftyTrend').textContent = goldNiftyTrend;

            const vixTrend = ind.vix < 15 ? '😌 Low Fear' :
                ind.vix > 20 ? '😰 High Fear' : '😐 Moderate Fear';
            document.getElementById('vixTrend').textContent = vixTrend;

            const pcrTrend = ind.put_call_ratio > 1.2 ? '🐻 Bearish' :
                ind.put_call_ratio < 0.8 ? '🐂 Bullish' : '➡️ Neutral';
            document.getElementById('pcrTrend').textContent = pcrTrend;

            const sentimentIcon = ind.market_sentiment === 'BULLISH' ? '🚀' :
                ind.market_sentiment === 'BEARISH' ? '⚠️' : '➡️';
            document.getElementById('sentimentIcon').textContent = sentimentIcon;
        }
    } catch (error) {
        console.error('Error loading market indicators:', error);
    }
};

const loadTodaysCalls = async () => {
    try {
        const response = await fetch('/api/todays_calls');
        const data = await response.json();

        if (data.success && data.calls.length > 0) {
            displayTradeCalls(data.calls);
        }
    } catch (error) {
        console.error('Error loading trade calls:', error);
    }
};

const displayTradeCalls = (calls) => {
    const container = document.getElementById('tradeCallsContainer');

    if (calls.length === 0) {
        container.innerHTML = '<p class="empty-state">No trade calls for today</p>';
        return;
    }

    container.innerHTML = calls.map(call => `
        <div class="trade-card">
            <div class="trade-card-header">
                <div class="trade-symbol">${call.symbol}</div>
                <div class="conviction-badge">${call.conviction_score}/100</div>
            </div>
            
            <div class="trade-prices">
                <div class="price-item">
                    <div class="price-label">Entry</div>
                    <div class="price-value">${formatCurrency(call.entry_price)}</div>
                </div>
                <div class="price-item">
                    <div class="price-label">Target</div>
                    <div class="price-value">${formatCurrency(call.target_price)}</div>
                </div>
                <div class="price-item">
                    <div class="price-label">Stop Loss</div>
                    <div class="price-value">${formatCurrency(call.stop_loss)}</div>
                </div>
            </div>
            
            <div class="potential-gain">
                <div class="price-label">Potential Gain</div>
                <div class="potential-gain-value">${formatPercent(call.potential_gain)}</div>
            </div>
            
            <div class="trade-reasoning">
                <strong>Reasoning:</strong><br>
                ${call.reasoning}
            </div>
        </div>
    `).join('');
};

document.getElementById('generateCallsBtn').addEventListener('click', async () => {
    showLoading();

    try {
        const response = await fetch('/api/generate_calls', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nifty_change: 0.0 })
        });

        const data = await response.json();

        if (data.success) {
            displayTradeCalls(data.trade_calls);

            // Update market indicators
            if (data.market_indicators) {
                const ind = data.market_indicators;
                document.getElementById('goldNiftyRatio').textContent = ind.gold_nifty_ratio.toFixed(4);
                document.getElementById('vixValue').textContent = ind.vix.toFixed(2);
                document.getElementById('pcrValue').textContent = ind.put_call_ratio.toFixed(2);
                document.getElementById('marketSentiment').textContent = ind.market_sentiment || 'NEUTRAL';
            }
        } else {
            alert('Error generating calls: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate trade calls');
    } finally {
        hideLoading();
    }
});

// ============= TAB 2: PERFORMANCE TRACKING =============

const loadPerformanceSummary = async (date = null) => {
    showLoading();

    try {
        const url = date ? `/api/performance_summary?date=${date}` : '/api/performance_summary';
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            // Update summary cards
            document.getElementById('totalCalls').textContent = data.summary.total_calls;
            document.getElementById('closedTrades').textContent = data.summary.closed_trades;
            document.getElementById('winningTrades').textContent = data.summary.winning_trades;
            document.getElementById('losingTrades').textContent = data.summary.losing_trades;
            document.getElementById('avgGainLoss').textContent = formatPercent(data.summary.avg_gain_loss_percent);
            document.getElementById('totalPnl').textContent = formatCurrency(data.summary.total_pnl);

            // Color code P&L
            const pnlElement = document.getElementById('totalPnl');
            if (data.summary.total_pnl > 0) {
                pnlElement.classList.add('gain-positive');
                pnlElement.classList.remove('gain-negative');
            } else if (data.summary.total_pnl < 0) {
                pnlElement.classList.add('gain-negative');
                pnlElement.classList.remove('gain-positive');
            }

            // Update trades table
            displayTradesTable(data.trades);
        }
    } catch (error) {
        console.error('Error loading performance:', error);
    } finally {
        hideLoading();
    }
};

const displayTradesTable = (trades) => {
    const tbody = document.getElementById('tradesTableBody');

    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No trades for selected date</td></tr>';
        return;
    }

    tbody.innerHTML = trades.map(trade => {
        const statusClass = trade.status === 'OPEN' ? 'status-open' : 'status-closed';
        const gainClass = trade.gain_loss_percent >= 0 ? 'gain-positive' : 'gain-negative';

        return `
            <tr>
                <td><strong>${trade.symbol}</strong></td>
                <td>${trade.call_time}</td>
                <td>${formatCurrency(trade.entry_price)}</td>
                <td>${formatCurrency(trade.target_price)}</td>
                <td><span class="status-badge ${statusClass}">${trade.status}</span></td>
                <td class="${gainClass}">${formatPercent(trade.gain_loss_percent)}</td>
                <td class="${gainClass}">${formatCurrency(trade.gain_loss_amount)}</td>
                <td>
                    ${trade.status === 'OPEN' ?
                `<button class="btn btn-success btn-sm" onclick="closeTrade(${trade.id})">Close Trade</button>` :
                '-'
            }
                </td>
            </tr>
        `;
    }).join('');
};

const closeTrade = async (tradeId) => {
    const exitPrice = prompt('Enter exit price:');
    if (!exitPrice) return;

    showLoading();

    try {
        const response = await fetch(`/api/close_trade/${tradeId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ exit_price: parseFloat(exitPrice) })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Trade closed! Gain/Loss: ${formatPercent(data.gain_loss_percent)}`);
            loadPerformanceSummary();
        } else {
            alert('Error closing trade: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to close trade');
    } finally {
        hideLoading();
    }
};

// Date picker for performance
document.getElementById('performanceDate').addEventListener('change', (e) => {
    loadPerformanceSummary(e.target.value);
});

// Set today's date as default
document.getElementById('performanceDate').valueAsDate = new Date();

// ============= TAB 3: CONVICTION ANALYSIS =============

document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const symbol = document.getElementById('symbolInput').value.trim().toUpperCase();

    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/analyze_conviction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol })
        });

        const data = await response.json();

        if (data.success) {
            displayConvictionAnalysis(data.symbol, data.analysis);
        } else {
            alert('Error analyzing stock: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze stock');
    } finally {
        hideLoading();
    }
});

// Allow Enter key to trigger analysis
document.getElementById('symbolInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('analyzeBtn').click();
    }
});

const displayConvictionAnalysis = (symbol, analysis) => {
    const container = document.getElementById('analysisContainer');

    const scoreColor = analysis.overall_score > 70 ? 'var(--success)' :
        analysis.overall_score > 50 ? 'var(--warning)' : 'var(--danger)';

    const sentimentEmoji = analysis.sentiment === 'POSITIVE' ? '😊' :
        analysis.sentiment === 'NEGATIVE' ? '😟' : '😐';

    container.innerHTML = `
        <div class="analysis-result">
            <div class="analysis-header">
                <div class="analysis-symbol">${symbol}</div>
                <div class="conviction-score">
                    <div class="score-circle" style="background: ${scoreColor}">
                        ${analysis.overall_score}
                    </div>
                    <div class="score-label">Conviction Score</div>
                </div>
            </div>
            
            <div class="transcript-summary">
                <h3>📄 Transcript Summary</h3>
                <p>${analysis.transcript_summary}</p>
            </div>
            
            <div class="key-insights">
                <h3>💡 Key Insights</h3>
                <ul class="insights-list">
                    ${analysis.key_insights.map(insight => `<li>${insight}</li>`).join('')}
                </ul>
            </div>
            
            <div class="conviction-factors">
                <div class="factor-item">
                    <div class="factor-label">Revenue Growth</div>
                    <div class="factor-value gain-positive">${analysis.revenue_growth}%</div>
                </div>
                <div class="factor-item">
                    <div class="factor-label">Margin Trend</div>
                    <div class="factor-value">${analysis.margin_trend}</div>
                </div>
                <div class="factor-item">
                    <div class="factor-label">Order Book</div>
                    <div class="factor-value">${analysis.order_book_strength}</div>
                </div>
                <div class="factor-item">
                    <div class="factor-label">Sentiment</div>
                    <div class="factor-value">${sentimentEmoji} ${analysis.sentiment}</div>
                </div>
            </div>
        </div>
    `;
};

// ============= PRICE VERIFICATION =============

let allPrices = [];
let currentPage = 1;
const itemsPerPage = 10;

const displayPricesPage = (page) => {
    const tbody = document.getElementById('priceVerificationBody');
    const startIdx = (page - 1) * itemsPerPage;
    const endIdx = startIdx + itemsPerPage;
    const pageData = allPrices.slice(startIdx, endIdx);

    tbody.innerHTML = pageData.map(item => {
        const statusClass = item.status === 'success' ? 'gain-positive' : 'gain-negative';
        const priceDisplay = item.price !== null ? formatCurrency(item.price) : 'N/A';
        const statusDisplay = item.status === 'success' ? '✅ Success' : `❌ ${item.error || 'Failed'}`;

        return `
            <tr>
                <td><strong>${item.symbol}</strong></td>
                <td><code>${item.yf_symbol}</code></td>
                <td>${priceDisplay}</td>
                <td class="${statusClass}">${statusDisplay}</td>
            </tr>
        `;
    }).join('');

    // Update pagination
    const totalPages = Math.ceil(allPrices.length / itemsPerPage);
    document.getElementById('pageInfo').textContent = `Page ${page} of ${totalPages}`;
    document.getElementById('prevPage').disabled = page === 1;
    document.getElementById('nextPage').disabled = page === totalPages;
};

document.getElementById('verifyPricesBtn').addEventListener('click', async () => {
    showLoading();

    try {
        const response = await fetch('/api/verify_prices');
        const data = await response.json();

        if (data.success) {
            allPrices = data.prices;
            currentPage = 1;
            displayPricesPage(currentPage);
            document.getElementById('priceVerificationContainer').style.display = 'block';
        } else {
            alert('Error fetching prices: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to fetch prices');
    } finally {
        hideLoading();
    }
});

document.getElementById('prevPage').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        displayPricesPage(currentPage);
    }
});

document.getElementById('nextPage').addEventListener('click', () => {
    const totalPages = Math.ceil(allPrices.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayPricesPage(currentPage);
    }
});

// ============= 7-DAY TRENDS =============

const renderTrendChart = (containerId, data, type = 'default') => {
    const container = document.getElementById(containerId);
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="empty-state">No data available</p>';
        return;
    }

    // Find min and max values for scaling
    const values = data.map(d => d.value);
    const maxValue = Math.max(...values.map(Math.abs));
    const minValue = Math.min(...values);

    container.innerHTML = data.map(item => {
        const value = item.value;
        const absValue = Math.abs(value);
        const heightPercent = (absValue / maxValue) * 100;
        const date = new Date(item.date);
        const dateLabel = `${date.getMonth() + 1}/${date.getDate()}`;

        // Determine bar class based on type and value
        let barClass = '';
        if (type === 'flow') {
            barClass = value >= 0 ? 'positive' : 'negative';
        }

        return `
            <div class="chart-bar ${barClass}" style="height: ${heightPercent}%;" title="${dateLabel}: ${value}">
                <div class="chart-bar-value">${value}</div>
                <div class="chart-bar-label">${dateLabel}</div>
            </div>
        `;
    }).join('');
};

document.getElementById('loadTrendsBtn').addEventListener('click', async () => {
    showLoading();

    try {
        const response = await fetch('/api/7day_trends');
        const data = await response.json();

        if (data.success) {
            const trends = data.trends;

            // Render each chart
            renderTrendChart('vixChart', trends.vix_trend, 'default');

            // Show the trends container
            document.getElementById('trendsContainer').style.display = 'grid';
        } else {
            alert('Error loading trends: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load trends');
    } finally {
        hideLoading();
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTodaysCalls();
    loadMarketIndicators();
});
