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
        } else if (tabId === 'tab3') {
            loadTranscriptHistory();
        } else if (tabId === 'tab4') {
            loadAnnualReportHistory();
            const sym = document.getElementById('arSymbolInput').value;
            if (sym) loadLatestAnnualReport(sym);
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
            loadActiveTrades();
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

// ============= ACTIVE TRADE TRACKER =============

const loadActiveTrades = async () => {
    const tbody = document.getElementById('activeTradesTableBody');
    const refreshBtn = document.getElementById('refreshActiveBtn');

    if (refreshBtn) refreshBtn.classList.add('loading-spin');

    try {
        const response = await fetch('/api/active_trades');
        const data = await response.json();

        if (data.success) {
            displayActiveTrades(data.active_trades);
        }
    } catch (error) {
        console.error('JS_ERROR (ActiveTrades):', error);
    } finally {
        if (refreshBtn) refreshBtn.classList.remove('loading-spin');
    }
};

const displayActiveTrades = (trades) => {
    const tbody = document.getElementById('activeTradesTableBody');

    if (!trades || trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">No active calls being tracked</td></tr>';
        return;
    }

    tbody.innerHTML = trades.map(t => {
        const gainClass = t.gain_loss_percent >= 0 ? 'price-up' : 'price-down';
        const pnlSign = t.gain_loss_amount >= 0 ? '+' : '';

        return `
            <tr>
                <td><strong>${t.symbol}</strong><br><small class="text-secondary">${t.recommendation}</small></td>
                <td>${t.call_date}</td>
                <td>${formatCurrency(t.entry_price)}</td>
                <td class="${gainClass}">${t.current_price ? formatCurrency(t.current_price) : 'N/A'}</td>
                <td>
                    <div class="target-sl-group">
                        <div class="ts-tag"><span class="ts-label">T:</span> <span>${formatCurrency(t.target_price)}</span></div>
                        <div class="ts-tag"><span class="ts-label">SL:</span> <span>${t.stop_loss ? formatCurrency(t.stop_loss) : '-'}</span></div>
                    </div>
                </td>
                <td class="${gainClass}">${t.gain_loss_percent.toFixed(2)}%</td>
                <td class="${gainClass}">${pnlSign}${formatCurrency(t.gain_loss_amount)}</td>
                <td>
                    <button class="btn btn-success btn-sm" onclick="closeTrade(${t.id})">Close</button>
                </td>
            </tr>
        `;
    }).join('');
};

const refreshBtn = document.getElementById('refreshActiveBtn');
if (refreshBtn) {
    refreshBtn.addEventListener('click', loadActiveTrades);
}

// Initial load and set interval
loadActiveTrades();
setInterval(loadActiveTrades, 60000); // Auto-refresh every 60s

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
            loadTranscriptHistory();
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

const loadTranscriptHistory = async () => {
    try {
        const response = await fetch('/api/history/transcripts');
        const data = await response.json();
        if (data.success) {
            renderHistoryList('transcriptHistoryList', data.history, 'transcript');
        }
    } catch (error) {
        console.error('JS_ERROR (TranscriptHistory):', error);
    }
};

const renderHistoryList = (containerId, history, type) => {
    const container = document.getElementById(containerId);
    if (!history || history.length === 0) {
        container.innerHTML = '<p class="empty-state">No recent reports</p>';
        return;
    }

    container.innerHTML = history.map(h => `
        <div class="history-item" onclick="loadHistoricalReport('${h.symbol}', '${type}')">
            <div class="hist-top">
                <span class="hist-symbol">${h.symbol}</span>
                <span class="hist-score" style="color: ${h.score >= 8 ? 'var(--success)' : h.score >= 5 ? 'var(--warning)' : 'var(--danger)'}">${h.score}/10</span>
            </div>
            <div class="hist-period">${h.period || h.fy || 'Report'}</div>
            <div class="hist-date">Analyzed on ${h.date}</div>
        </div>
    `).join('');
};

window.loadHistoricalReport = async (symbol, type) => {
    showLoading();
    try {
        const endpoint = type === 'transcript' ? `/api/conviction/${symbol}` : `/api/annual_report/${symbol}`;
        const response = await fetch(endpoint);
        const data = await response.json();
        if (data.success) {
            if (type === 'transcript') {
                displayConvictionAnalysis(symbol, data.analysis);
            } else {
                displayAnnualReportAnalysis(symbol, data.analysis);
            }
        }
    } catch (error) {
        console.error('JS_ERROR (LoadHistReport):', error);
    } finally {
        hideLoading();
    }
};

const displayConvictionAnalysis = (symbol, a) => {
    const container = document.getElementById('analysisContainer');
    const s = a.sections;
    const snap = a.snapshot;
    const table = a.conviction_table;

    let html = `
        <div class="research-report">
            <div class="rr-hero">
                <div class="rr-title">CONCALL SNAPSHOT: ${symbol} | ${a.period || a.quarter}</div>
                <div class="rr-meta-row">
                    <span class="rr-tag">Conviction: <strong style="color:var(--accent-primary)">${a.overall_score}/10</strong></span>
                    <span class="rr-tag">Tone: <strong>${s.mgmt_tone_linguistic.tone}</strong></span>
                </div>
            </div>

            <div class="rr-verdict-card">
                <div class="verdict-label">FINAL INVESTMENT VERDICT</div>
                <div class="verdict-value ${a.overall_score >= 8 ? 'text-success' : a.overall_score >= 5 ? 'text-warning' : 'text-danger'}">
                    ${a.final_investment_verdict || a.verdict}
                </div>
            </div>

            <!-- Concall Snapshot -->
            <div class="rr-snapshot-grid">
                <div class="snapshot-card strength">
                    <div class="snap-title">✅ BULLISH TAKEAWAYS</div>
                    ${renderBulletList(snap.bullish_takeaways)}
                </div>
                <div class="snapshot-card concern">
                    <div class="snap-title">⚠️ CONCERNS & RED FLAGS</div>
                    ${renderBulletList(snap.concerns_red_flags)}
                </div>
                <div class="snapshot-card watch">
                    <div class="snap-title">🔍 QUESTIONS TO MONITOR</div>
                    ${renderBulletList(snap.questions_to_watch)}
                </div>
            </div>

            <!-- 10 Detailed Sections -->
            ${renderSection('🎯', 'Management Tone & Body Language', `
                <div class="rr-meta-row"><span class="rr-tag">Tone: <strong>${s.mgmt_tone_linguistic.tone}</strong></span><span class="rr-tag">Direct Answers: <strong>${s.mgmt_tone_linguistic.is_direct}</strong></span></div>
                ${renderBulletList(s.mgmt_tone_linguistic.linguistic_signals)}
                ${s.mgmt_tone_linguistic.deflections.length ? `<h4>Deflections</h4>${renderBulletList(s.mgmt_tone_linguistic.deflections)}` : ''}
            `)}

            ${renderSection('📊', 'Earnings Quality & Number Cross-Check', renderBulletList(s.earnings_quality.key_metrics.concat(s.earnings_quality.mix_shift_insights)))}
            ${renderSection('❓', 'Analyst Questions & Management Quality', renderBulletList(s.analyst_questions.tough_questions.concat(s.analyst_questions.analyst_skepticism_signals)))}
            ${renderSection('📉', 'Guidance & Forward Looking', `
                <div class="rr-meta-row"><span class="rr-tag">Direction: <strong>${s.guidance_forward.guidance_direction}</strong></span></div>
                ${renderBulletList(s.guidance_forward.specific_guidance)}
            `)}
            ${renderSection('🏭', 'Operational Updates & Momentum', renderBulletList(s.operational_updates.operational_metrics.concat(s.operational_updates.segment_momentum)))}
            ${renderSection('💸', 'Capital Allocation', renderBulletList(s.capital_allocation.capex_plans.concat(s.capital_allocation.debt_management, s.capital_allocation.shareholder_payouts)))}
            ${renderSection('🚨', 'Red Flag Detector (Between Lines)', renderBulletList(s.red_flag_detector.detected_flags.concat(s.red_flag_detector.metric_silence)))}
            ${renderSection('🔁', 'Consistency Check (Then vs Now)', renderBulletList(s.consistency_check.promise_delivery_signals.concat(s.consistency_check.narrative_u_turns)))}
            ${renderSection('🌍', 'Industry & Competitive Commentary', renderBulletList(s.industry_competitive.industry_demand.concat(s.industry_competitive.competitive_intensity)))}
            ${renderSection('👥', 'Institutional Investor Signals', renderBulletList(s.institutional_signals.esg_governance_focus.concat(s.institutional_signals.expectation_management)))}

            <!-- Conviction Score Table -->
            <div class="rr-section" open>
                <summary class="rr-section-header">🎯 CONCALL CONVICTION SCORE</summary>
                <div class="rr-section-content">
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">Rating management and business momentum from this call:</p>
                    <table class="conviction-table">
                        <thead>
                            <tr>
                                <th>Parameter</th>
                                <th>Score (1-10)</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${table.map(row => `
                                <tr>
                                    <td>${row.parameter}</td>
                                    <td><span class="score-pill ${row.score >= 8 ? 'high' : row.score >= 5 ? 'mid' : 'low'}">${row.score}</span></td>
                                    <td>${row.notes}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
};

// ============= TAB 4: ANNUAL REPORT DEEP-DIVE =============

const loadAnnualReportHistory = async () => {
    try {
        const response = await fetch('/api/history/annual_reports');
        const data = await response.json();
        if (data.success) {
            renderHistoryList('arHistoryList', data.history, 'annual_report');
        }
    } catch (error) {
        console.error('JS_ERROR (ARHistory):', error);
    }
};

const arUploadBtn = document.getElementById('arUploadBtn');
const arAnalyzeBtn = document.getElementById('arAnalyzeBtn');
const annualReportFile = document.getElementById('annualReportFile');

if (arUploadBtn) {
    arUploadBtn.addEventListener('click', () => annualReportFile.click());
}

if (arAnalyzeBtn) {
    arAnalyzeBtn.addEventListener('click', async () => {
        const symbol = document.getElementById('arSymbolInput').value.trim().toUpperCase();
        const file = annualReportFile.files[0];

        if (!symbol) {
            alert('Please enter a stock symbol');
            return;
        }

        if (!file) {
            alert('Please upload an annual report PDF first');
            return;
        }

        const formData = new FormData();
        formData.append('symbol', symbol);
        formData.append('file', file);

        showLoading();
        try {
            const response = await fetch('/api/analyze_annual_report', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                displayAnnualReportAnalysis(symbol, data.analysis);
                loadAnnualReportHistory();
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error('JS_ERROR (AnalyzeAR):', error);
            alert('Failed to analyze annual report. Check console for details.');
        } finally {
            hideLoading();
        }
    });
}

const loadLatestAnnualReport = async (symbol) => {
    try {
        const response = await fetch(`/api/annual_report/${symbol}`);
        const data = await response.json();
        if (data.success) {
            displayAnnualReportAnalysis(symbol, data.analysis);
        }
    } catch (error) {
        console.error('JS_ERROR (LoadAR):', error);
    }
};

const displayAnnualReportAnalysis = (symbol, a) => {
    const container = document.getElementById('arAnalysisContainer');
    const sections = a.sections;
    const snap = a.snapshot;
    const table = a.conviction_table;

    let html = `
        <div class="research-report">
            <div class="rr-hero">
                <div class="rr-title">Investment Analysis: ${symbol}</div>
                <div class="rr-meta-row">
                    <span class="rr-tag">Fiscal Year: <strong>${a.fiscal_year}</strong></span>
                    <span class="rr-tag">Score: <strong style="color:var(--accent-primary)">${a.overall_score}/10</strong></span>
                </div>
            </div>

            <div class="rr-verdict-card">
                <div class="verdict-label">VERDICT</div>
                <div class="verdict-value ${a.overall_score >= 8 ? 'text-success' : a.overall_score >= 5 ? 'text-warning' : 'text-danger'}">
                    ${a.verdict}
                </div>
            </div>

            <!-- Investment Snapshot -->
            <div class="rr-snapshot-grid">
                <div class="snapshot-card strength">
                    <div class="snap-title">✅ STRENGTHS</div>
                    ${renderBulletList(snap.strengths)}
                </div>
                <div class="snapshot-card concern">
                    <div class="snap-title">⚠️ CONCERNS</div>
                    ${renderBulletList(snap.concerns)}
                </div>
                <div class="snapshot-card watch">
                    <div class="snap-title">🔍 THINGS TO WATCH</div>
                    ${renderBulletList(snap.things_to_watch)}
                </div>
            </div>

            <!-- Detailed Sections -->
            ${renderSection('🏢', 'Business Overview & Moat', renderBulletList(sections.business_overview.overview.concat(sections.business_overview.moat_signals)))}
            ${renderSection('📈', 'Financial Health', renderBulletList(sections.financial_health.revenue_trend.concat(sections.financial_health.margin_analysis, sections.financial_health.return_ratios, sections.financial_health.cash_flow_quality)))}
            ${renderSection('🧾', 'Accounting Quality', renderBulletList(sections.accounting_quality.cash_flow_vs_profit.concat(sections.accounting_quality.receivables_inventory_risk, sections.accounting_quality.auditor_comments)))}
            ${renderSection('👨‍💼', 'Management & Governance', renderBulletList(sections.management_quality.promoter_holding.concat(sections.management_quality.capital_allocation_history, sections.management_quality.board_governance)))}
            ${renderSection('🌍', 'Industry & Macro', renderBulletList(sections.industry_macro.industry_outlook.concat(sections.industry_macro.regulatory_environment, sections.industry_macro.macro_exposure)))}
            ${renderSection('🚀', 'Growth & Outlook', renderBulletList(sections.growth_drivers.stated_strategy.concat(sections.growth_drivers.pipeline_visibility, sections.growth_drivers.expansion_plans)))}
            ${renderSection('⚠️', 'Key Risks', renderBulletList(sections.key_risks.top_risks.concat(sections.key_risks.debt_refinancing)))}
            ${renderSection('💰', 'Valuation Context', renderBulletList(sections.valuation_context.valuation_metrics.concat(sections.valuation_context.dividend_profile)))}

            <!-- Conviction Score Table -->
            <div class="rr-section">
                <details open>
                    <summary class="rr-section-header">🎯 Conviction Score Table</summary>
                    <div class="rr-section-content">
                        <table class="conviction-table">
                            <thead>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Score (1-10)</th>
                                    <th>Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${table.map(row => `
                                    <tr>
                                        <td>${row.parameter}</td>
                                        <td><span class="score-pill ${row.score >= 8 ? 'high' : row.score >= 5 ? 'mid' : 'low'}">${row.score}</span></td>
                                        <td>${row.notes}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </details>
            </div>
        </div>
    `;

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
