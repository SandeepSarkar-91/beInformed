// Trading Dashboard JavaScript
console.log('JS: Dashboard script loading...');

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
        console.error('JS_ERROR (MarketIndicators):', error);
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
        console.error('JS_ERROR (TodaysCalls):', error);
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
        console.error('JS_ERROR (GenerateCalls):', error);
        alert('Failed to generate calls');
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
        console.error('JS_ERROR (PerformanceSummary):', error);
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
        console.error('JS_ERROR (CloseTrade):', error);
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

document.getElementById('uploadBtn').addEventListener('click', () => {
    document.getElementById('transcriptFile').click();
});

document.getElementById('transcriptFile').addEventListener('change', (e) => {
    const fileName = e.target.files[0] ? e.target.files[0].name : '';
    if (fileName) {
        document.getElementById('uploadBtn').textContent = `📄 ${fileName}`;
    }
});

document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const symbol = document.getElementById('symbolInput').value.trim().toUpperCase();
    const fileInput = document.getElementById('transcriptFile');
    const file = fileInput.files[0];

    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }

    if (!file) {
        alert('Please upload a PDF transcript first');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('symbol', symbol);
        formData.append('file', file);

        const response = await fetch('/api/analyze_transcript', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayConvictionAnalysis(data.symbol, data.analysis);
        } else {
            alert('Error analyzing transcript: ' + data.error);
        }
    } catch (error) {
        console.error('JS_ERROR (AnalyzeTranscript):', error);
        alert('Failed to analyze transcript');
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

const renderBulletList = (items, emptyMsg = 'No data available') => {
    if (!items || items.length === 0) return `<p class="rr-empty">${emptyMsg}</p>`;
    return `<ul class="rr-list">${items.map(i => `<li>${i}</li>`).join('')}</ul>`;
};

const renderScoreBadge = (score, max = 10) => {
    const pct = (score / max) * 100;
    const color = pct >= 70 ? 'var(--success)' : pct >= 50 ? 'var(--warning)' : 'var(--danger)';
    return `<span class="rr-score-badge" style="background: ${color}">${score}/${max}</span>`;
};

const renderSection = (icon, title, contentHtml, open = false) => {
    return `
        <details class="rr-section" ${open ? 'open' : ''}>
            <summary class="rr-section-header">${icon} ${title}</summary>
            <div class="rr-section-body">${contentHtml}</div>
        </details>
    `;
};

const displayConvictionAnalysis = (symbol, a) => {
    const container = document.getElementById('analysisContainer');

    // Conviction verdict styling
    const verdict = a.conclusion?.verdict || 'NEUTRAL';
    const verdictColor = verdict === 'HIGH_CONVICTION' ? 'var(--success)' :
        verdict === 'AVOID' ? 'var(--danger)' : 'var(--warning)';
    const verdictLabel = verdict === 'HIGH_CONVICTION' ? '🟢 High Conviction' :
        verdict === 'AVOID' ? '🔴 Avoid' : '🟡 Neutral';

    const stScore = a.conviction_scores?.short_term?.score || 5;
    const ltScore = a.conviction_scores?.long_term?.score || 5;

    let html = `<div class="research-report">`;

    // ── Header ──
    html += `
        <div class="rr-hero">
            <div class="rr-hero-left">
                <h2 class="rr-symbol">${symbol}</h2>
                <span class="rr-quarter">${a.quarter || 'Latest'}</span>
                <span class="rr-verdict" style="background: ${verdictColor}">${verdictLabel}</span>
            </div>
            <div class="rr-hero-scores">
                <div class="rr-score-card">
                    <div class="rr-score-value" style="color: ${stScore >= 7 ? 'var(--success)' : stScore >= 5 ? 'var(--warning)' : 'var(--danger)'}">${stScore}</div>
                    <div class="rr-score-label">Short-Term</div>
                </div>
                <div class="rr-score-card">
                    <div class="rr-score-value" style="color: ${ltScore >= 7 ? 'var(--success)' : ltScore >= 5 ? 'var(--warning)' : 'var(--danger)'}">${ltScore}</div>
                    <div class="rr-score-label">Long-Term</div>
                </div>
            </div>
        </div>
    `;

    // ── Conclusion ──
    html += `<div class="rr-conclusion"><p>${a.conclusion?.summary || ''}</p></div>`;

    // 1. Executive Summary
    const execHtml = `
        <div class="rr-meta-row">
            <span class="rr-tag">Tone: <strong>${a.executive_summary?.tone || 'N/A'}</strong></span>
        </div>
        <h4>Key Takeaways</h4>
        ${renderBulletList(a.executive_summary?.takeaways)}
        ${a.executive_summary?.surprises?.length ? `<h4>Surprises</h4>${renderBulletList(a.executive_summary.surprises)}` : ''}
    `;
    html += renderSection('1️⃣', 'Executive Summary', execHtml, true);

    // 2. Revenue & Growth
    const revHtml = `
        <div class="rr-metrics-grid">
            <div class="rr-metric"><span class="rr-metric-label">YoY Growth</span><span class="rr-metric-value">${a.revenue_growth?.yoy_growth != null ? a.revenue_growth.yoy_growth + '%' : 'N/A'}</span></div>
            <div class="rr-metric"><span class="rr-metric-label">QoQ Growth</span><span class="rr-metric-value">${a.revenue_growth?.qoq_growth != null ? a.revenue_growth.qoq_growth + '%' : 'N/A'}</span></div>
            <div class="rr-metric"><span class="rr-metric-label">Sustainability</span><span class="rr-metric-value">${a.revenue_growth?.sustainability || 'N/A'}</span></div>
        </div>
        ${a.revenue_growth?.segment_performance?.length ? `<h4>Segment Performance</h4>${renderBulletList(a.revenue_growth.segment_performance)}` : ''}
        ${a.revenue_growth?.geographic_performance?.length ? `<h4>Geographic Performance</h4>${renderBulletList(a.revenue_growth.geographic_performance)}` : ''}
        ${a.revenue_growth?.volume_vs_pricing?.length ? `<h4>Volume vs Pricing</h4>${renderBulletList(a.revenue_growth.volume_vs_pricing)}` : ''}
    `;
    html += renderSection('2️⃣', 'Revenue & Growth Analysis', revHtml, true);

    // 3. Profitability & Margins
    const profHtml = `
        <div class="rr-metrics-grid">
            <div class="rr-metric"><span class="rr-metric-label">Gross Margin</span><span class="rr-metric-value">${a.profitability?.gross_margin != null ? a.profitability.gross_margin + '%' : 'N/A'}</span></div>
            <div class="rr-metric"><span class="rr-metric-label">EBITDA Margin</span><span class="rr-metric-value">${a.profitability?.ebitda_margin != null ? a.profitability.ebitda_margin + '%' : 'N/A'}</span></div>
            <div class="rr-metric"><span class="rr-metric-label">Net Margin</span><span class="rr-metric-value">${a.profitability?.net_margin != null ? a.profitability.net_margin + '%' : 'N/A'}</span></div>
            <div class="rr-metric"><span class="rr-metric-label">Trend</span><span class="rr-metric-value rr-tag-${a.profitability?.trend?.toLowerCase()}">${a.profitability?.trend || 'N/A'}</span></div>
        </div>
        ${a.profitability?.drivers?.length ? `<h4>Margin Drivers</h4>${renderBulletList(a.profitability.drivers)}` : ''}
    `;
    html += renderSection('3️⃣', 'Profitability & Margins', profHtml);

    // 4. Cash Flow & Capital Allocation
    const cfHtml = `
        ${a.cash_flow?.capex_commentary?.length ? `<h4>Capex Commentary</h4>${renderBulletList(a.cash_flow.capex_commentary)}` : ''}
        ${a.cash_flow?.debt_commentary?.length ? `<h4>Debt & Leverage</h4>${renderBulletList(a.cash_flow.debt_commentary)}` : ''}
        ${a.cash_flow?.shareholder_returns?.length ? `<h4>Shareholder Returns</h4>${renderBulletList(a.cash_flow.shareholder_returns)}` : ''}
        ${a.cash_flow?.mna_activity?.length ? `<h4>M&A Activity</h4>${renderBulletList(a.cash_flow.mna_activity)}` : ''}
    `;
    html += renderSection('4️⃣', 'Cash Flow & Capital Allocation', cfHtml);

    // 5. Balance Sheet
    const bsHtml = `
        ${a.balance_sheet?.liquidity?.length ? `<h4>Liquidity</h4>${renderBulletList(a.balance_sheet.liquidity)}` : ''}
        ${a.balance_sheet?.working_capital?.length ? `<h4>Working Capital</h4>${renderBulletList(a.balance_sheet.working_capital)}` : ''}
        ${a.balance_sheet?.red_flags?.length ? `<h4>⚠️ Red Flags</h4>${renderBulletList(a.balance_sheet.red_flags)}` : ''}
    `;
    html += renderSection('5️⃣', 'Balance Sheet Strength', bsHtml);

    // 6. Management Commentary
    const mgmtHtml = `
        <div class="rr-meta-row">
            <span class="rr-tag">Tone: <strong>${a.management_commentary?.tone || 'N/A'}</strong></span>
            <span class="rr-tag">Guidance: <strong>${a.management_commentary?.guidance_direction || 'N/A'}</strong></span>
        </div>
        ${a.management_commentary?.guidance_statements?.length ? `<h4>Guidance Statements</h4>${renderBulletList(a.management_commentary.guidance_statements)}` : ''}
    `;
    html += renderSection('6️⃣', 'Management Commentary', mgmtHtml);

    // 7. Competitive Position
    const compHtml = `
        ${a.competitive_position?.market_share?.length ? `<h4>Market Share</h4>${renderBulletList(a.competitive_position.market_share)}` : ''}
        ${a.competitive_position?.pricing_power?.length ? `<h4>Pricing Power</h4>${renderBulletList(a.competitive_position.pricing_power)}` : ''}
        ${a.competitive_position?.moat_indicators?.length ? `<h4>Moat Indicators</h4>${renderBulletList(a.competitive_position.moat_indicators)}` : ''}
        ${a.competitive_position?.competitive_risks?.length ? `<h4>Competitive Risks</h4>${renderBulletList(a.competitive_position.competitive_risks)}` : ''}
    `;
    html += renderSection('7️⃣', 'Competitive Position & Moat', compHtml);

    // 8. Strategic Initiatives
    const stratHtml = `
        ${a.strategic_initiatives?.new_ventures?.length ? `<h4>New Ventures</h4>${renderBulletList(a.strategic_initiatives.new_ventures)}` : ''}
        ${a.strategic_initiatives?.expansion?.length ? `<h4>Expansion</h4>${renderBulletList(a.strategic_initiatives.expansion)}` : ''}
        ${a.strategic_initiatives?.technology?.length ? `<h4>Technology & Innovation</h4>${renderBulletList(a.strategic_initiatives.technology)}` : ''}
        ${a.strategic_initiatives?.cost_optimization?.length ? `<h4>Cost Optimization</h4>${renderBulletList(a.strategic_initiatives.cost_optimization)}` : ''}
        ${a.strategic_initiatives?.long_term_drivers?.length ? `<h4>Long-Term Growth Drivers</h4>${renderBulletList(a.strategic_initiatives.long_term_drivers)}` : ''}
    `;
    html += renderSection('8️⃣', 'Strategic Initiatives & Future Plans', stratHtml);

    // 9. Risks
    const riskHtml = `
        ${a.risks?.macro?.length ? `<h4>Macro Risks</h4>${renderBulletList(a.risks.macro)}` : ''}
        ${a.risks?.regulatory?.length ? `<h4>Regulatory Risks</h4>${renderBulletList(a.risks.regulatory)}` : ''}
        ${a.risks?.execution?.length ? `<h4>Execution Risks</h4>${renderBulletList(a.risks.execution)}` : ''}
        ${a.risks?.slowdown_indicators?.length ? `<h4>Slowdown Indicators</h4>${renderBulletList(a.risks.slowdown_indicators)}` : ''}
    `;
    html += renderSection('9️⃣', 'Risks Identified', riskHtml);

    // 10. Leading Indicators
    const leadHtml = `
        ${a.leading_indicators?.metrics_to_watch?.length ? `<h4>Metrics to Watch</h4>${renderBulletList(a.leading_indicators.metrics_to_watch)}` : ''}
        ${a.leading_indicators?.acceleration_signs?.length ? `<h4>Acceleration Signs</h4>${renderBulletList(a.leading_indicators.acceleration_signs)}` : ''}
        ${a.leading_indicators?.deterioration_signs?.length ? `<h4>Deterioration Signs</h4>${renderBulletList(a.leading_indicators.deterioration_signs)}` : ''}
    `;
    html += renderSection('🔟', 'Leading Indicators', leadHtml);

    // Valuation Insights
    const valHtml = `
        ${a.valuation_insights?.growth_justification?.length ? `<h4>Growth Justification</h4>${renderBulletList(a.valuation_insights.growth_justification)}` : ''}
        ${a.valuation_insights?.margin_trajectory?.length ? `<h4>Margin Trajectory</h4>${renderBulletList(a.valuation_insights.margin_trajectory)}` : ''}
        ${a.valuation_insights?.cash_flow_durability?.length ? `<h4>Cash Flow Durability</h4>${renderBulletList(a.valuation_insights.cash_flow_durability)}` : ''}
    `;
    html += renderSection('📈', 'Valuation-Relevant Insights', valHtml);

    // Conviction Score Detail
    const convHtml = `
        <div class="rr-conviction-detail">
            <div class="rr-conv-card">
                <h4>Short-Term Trade</h4>
                ${renderScoreBadge(stScore)}
                ${renderBulletList(a.conviction_scores?.short_term?.justification)}
            </div>
            <div class="rr-conv-card">
                <h4>Long-Term Investment</h4>
                ${renderScoreBadge(ltScore)}
                ${renderBulletList(a.conviction_scores?.long_term?.justification)}
            </div>
        </div>
    `;
    html += renderSection('🎯', 'Conviction Score Breakdown', convHtml, true);

    // Red Flags
    if (a.red_flags?.length) {
        html += renderSection('🚨', 'Red Flags', renderBulletList(a.red_flags), true);
    }

    // Hidden Signals
    if (a.hidden_signals?.length) {
        html += renderSection('🔎', 'Hidden Signals', renderBulletList(a.hidden_signals), true);
    }

    html += `</div>`; // close .research-report
    container.innerHTML = html;
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
        console.error('JS_ERROR (VerifyPrices):', error);
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
        console.error('JS_ERROR (LoadTrends):', error);
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
