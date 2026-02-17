import re
import pdfplumber


class TranscriptAnalysisEngine:
    """Professional equity research analysis engine for earnings call transcripts."""

    # ── helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _pct(pattern, text):
        """Extract first percentage match from text."""
        m = re.search(pattern, text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    @staticmethod
    def _count(words, text):
        lower = text.lower()
        return sum(lower.count(w) for w in words)

    @staticmethod
    def _sentences_with(keywords, text, limit=5, min_len=30):
        """Return sentences containing any keyword."""
        results = []
        for sent in re.split(r'(?<=[.!?])\s+', text):
            if len(sent) < min_len:
                continue
            if any(k in sent.lower() for k in keywords):
                results.append(sent.strip())
                if len(results) >= limit:
                    break
        return results

    # ── PDF extraction ───────────────────────────────────────────────
    def extract_text(self, pdf_file):
        """Extract clean text from PDF using pdfplumber."""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                pages = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
                return "\n".join(pages)
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return None

    # ── section builders ─────────────────────────────────────────────
    def _executive_summary(self, text):
        takeaways = []

        # revenue headline
        rev = self._pct(r'revenue\s+(?:grew|increased|rose|up)\s+(?:by\s+)?([\d.]+)\s*%', text)
        if rev:
            takeaways.append(f"Revenue grew {rev}% year-over-year")

        # profit headline
        pat = self._pct(r'(?:net\s+)?profit\s+(?:grew|increased|rose|up)\s+(?:by\s+)?([\d.]+)\s*%', text)
        if pat:
            takeaways.append(f"Net profit grew {pat}%")

        # EBITDA
        eb = self._pct(r'ebitda\s+(?:grew|increased|rose|up|margin)\s+(?:by\s+|to\s+)?([\d.]+)\s*%', text)
        if eb:
            takeaways.append(f"EBITDA at {eb}%")

        # order book
        ob = re.search(r'order\s+book\s+(?:of|at|stands?\s+at)\s+(?:₹|Rs\.?|INR)?\s*([\d,.]+)\s*(crore|cr|billion|lakh)', text, re.IGNORECASE)
        if ob:
            takeaways.append(f"Order book at ₹{ob.group(1)} {ob.group(2)}")

        # guidance
        for kw in ['guidance', 'outlook', 'forecast']:
            sents = self._sentences_with([kw], text, limit=2)
            takeaways.extend(sents)

        # dividends / buyback
        sents = self._sentences_with(['dividend', 'buyback', 'bonus'], text, limit=2)
        takeaways.extend(sents)

        # Pad with general key sentences if we're short
        if len(takeaways) < 5:
            more = self._sentences_with(
                ['growth', 'margin', 'strong', 'improvement', 'expansion', 'execution'],
                text, limit=10 - len(takeaways)
            )
            takeaways.extend(more)

        # Determine tone
        pos = self._count(['confident', 'strong', 'robust', 'optimistic', 'excited', 'pleased', 'record'], text)
        neg = self._count(['cautious', 'challenging', 'headwinds', 'difficult', 'concerned', 'uncertain'], text)
        if pos > neg + 3:
            tone = "BULLISH"
        elif neg > pos + 3:
            tone = "CAUTIOUS"
        elif neg > pos:
            tone = "DEFENSIVE"
        else:
            tone = "CONFIDENT"

        return {
            "takeaways": takeaways[:10],
            "tone": tone,
            "surprises": self._sentences_with(
                ['surprise', 'unexpected', 'beat', 'exceeded', 'missed', 'below', 'shortfall'], text, limit=3
            )
        }

    def _revenue_growth(self, text):
        yoy = self._pct(r'revenue\s+(?:grew|increased|rose|growth|up)\s+(?:by\s+)?([\d.]+)\s*%\s*(?:yoy|year)', text)
        qoq = self._pct(r'revenue\s+(?:grew|increased|rose|growth|up)\s+(?:by\s+)?([\d.]+)\s*%\s*(?:qoq|quarter)', text)
        if not yoy:
            yoy = self._pct(r'(?:top\s*line|revenue)\s+(?:growth|grew)\s+(?:of\s+|by\s+)?([\d.]+)\s*%', text)

        segments = self._sentences_with(
            ['segment', 'division', 'vertical', 'business unit', 'product line'],
            text, limit=5
        )
        geo = self._sentences_with(
            ['domestic', 'international', 'export', 'geography', 'region', 'overseas'],
            text, limit=3
        )
        volume_price = self._sentences_with(
            ['volume', 'pricing', 'realisation', 'realization', 'price hike', 'price increase'],
            text, limit=3
        )

        sustainability = "SUSTAINABLE" if (yoy and yoy > 10) else "NEEDS_MONITORING"

        return {
            "yoy_growth": yoy,
            "qoq_growth": qoq,
            "segment_performance": segments,
            "geographic_performance": geo,
            "volume_vs_pricing": volume_price,
            "sustainability": sustainability
        }

    def _profitability(self, text):
        gross = self._pct(r'gross\s+(?:profit\s+)?margin\s+(?:at|of|was|is|to)\s+([\d.]+)\s*%', text)
        ebitda_m = self._pct(r'ebitda\s+margin\s+(?:at|of|was|is|to|stood\s+at)\s+([\d.]+)\s*%', text)
        net_m = self._pct(r'(?:net\s+(?:profit\s+)?|pat\s+)margin\s+(?:at|of|was|is|to)\s+([\d.]+)\s*%', text)

        margin_drivers = self._sentences_with(
            ['margin', 'operating leverage', 'cost', 'raw material', 'employee', 'input cost'],
            text, limit=5
        )

        trend = "STABLE"
        if re.search(r'margin\s+(?:improved|expanded|increased|higher)', text, re.IGNORECASE):
            trend = "EXPANDING"
        elif re.search(r'margin\s+(?:declined|contracted|compressed|lower|pressure)', text, re.IGNORECASE):
            trend = "CONTRACTING"

        return {
            "gross_margin": gross,
            "ebitda_margin": ebitda_m,
            "net_margin": net_m,
            "trend": trend,
            "drivers": margin_drivers
        }

    def _cash_flow(self, text):
        ocf = self._pct(r'operating\s+cash\s+flow\s+(?:of|at|was)\s+(?:₹|Rs\.?|INR)?\s*([\d,.]+)', text)
        fcf = self._pct(r'free\s+cash\s+flow\s+(?:of|at|was)\s+(?:₹|Rs\.?|INR)?\s*([\d,.]+)', text)

        capex = self._sentences_with(['capex', 'capital expenditure', 'investment'], text, limit=3)
        debt = self._sentences_with(['debt', 'borrowing', 'leverage', 'net debt'], text, limit=3)
        buyback = self._sentences_with(['buyback', 'dividend', 'payout'], text, limit=3)
        mna = self._sentences_with(['acquisition', 'merger', 'M&A', 'acquired'], text, limit=2)

        return {
            "operating_cash_flow": ocf,
            "free_cash_flow": fcf,
            "capex_commentary": capex,
            "debt_commentary": debt,
            "shareholder_returns": buyback,
            "mna_activity": mna
        }

    def _balance_sheet(self, text):
        liquidity = self._sentences_with(['cash', 'liquidity', 'bank balance', 'cash and equivalents'], text, limit=3)
        debt_maturity = self._sentences_with(['maturity', 'repayment', 'refinanc'], text, limit=2)
        working_cap = self._sentences_with(['working capital', 'receivable', 'payable', 'inventory'], text, limit=3)

        red_flags = []
        if re.search(r'(?:increase|rise)\s+(?:in\s+)?(?:debt|borrowing)', text, re.IGNORECASE):
            red_flags.append("Rising debt levels mentioned")
        if re.search(r'(?:increase|rise)\s+(?:in\s+)?(?:receivable|debtors)', text, re.IGNORECASE):
            red_flags.append("Rising receivables — potential collection risk")

        return {
            "liquidity": liquidity,
            "debt_maturity": debt_maturity,
            "working_capital": working_cap,
            "red_flags": red_flags
        }

    def _management_commentary(self, text):
        # Tone
        conf = self._count(['confident', 'excited', 'pleased', 'proud', 'strong position', 'well positioned'], text)
        caut = self._count(['cautious', 'uncertain', 'challenging', 'difficult', 'watch', 'monitor'], text)
        if conf > caut + 2:
            tone = "CONFIDENT"
        elif caut > conf + 2:
            tone = "CAUTIOUS"
        else:
            tone = "BALANCED"

        guidance = self._sentences_with(
            ['guidance', 'outlook', 'target', 'goal', 'expect', 'forecast', 'projection'],
            text, limit=5
        )

        guidance_direction = "MAINTAINED"
        if re.search(r'(?:raised|increased|upgraded|revised\s+upward)\s+(?:guidance|target|outlook)', text, re.IGNORECASE):
            guidance_direction = "RAISED"
        elif re.search(r'(?:lowered|reduced|downgraded|revised\s+downward|cut)\s+(?:guidance|target|outlook)', text, re.IGNORECASE):
            guidance_direction = "LOWERED"

        return {
            "tone": tone,
            "guidance_statements": guidance,
            "guidance_direction": guidance_direction
        }

    def _competitive_position(self, text):
        market_share = self._sentences_with(['market share', 'leadership', 'leader', 'number one', '#1'], text, limit=3)
        pricing = self._sentences_with(['pricing power', 'price hike', 'price increase', 'pass through'], text, limit=3)
        moat = self._sentences_with(['competitive advantage', 'barrier', 'moat', 'monopoly', 'dominant', 'unique'], text, limit=3)
        risks = self._sentences_with(['competition', 'competitive pressure', 'new entrant', 'disruption'], text, limit=3)

        return {
            "market_share": market_share,
            "pricing_power": pricing,
            "moat_indicators": moat,
            "competitive_risks": risks
        }

    def _strategic_initiatives(self, text):
        return {
            "new_ventures": self._sentences_with(['new product', 'launch', 'introduced', 'new venture', 'new business'], text, limit=3),
            "expansion": self._sentences_with(['expansion', 'new market', 'new geography', 'new plant', 'capacity'], text, limit=3),
            "technology": self._sentences_with(['AI', 'automation', 'digital', 'technology', 'innovation', 'R&D'], text, limit=3),
            "cost_optimization": self._sentences_with(['cost reduction', 'efficiency', 'optimization', 'streamlin'], text, limit=3),
            "long_term_drivers": self._sentences_with(['long term', 'long-term', 'structural', 'secular', 'multi-year'], text, limit=3)
        }

    def _risks(self, text):
        return {
            "macro": self._sentences_with(['macro', 'GDP', 'inflation', 'interest rate', 'currency', 'geopolitical'], text, limit=3),
            "regulatory": self._sentences_with(['regulation', 'regulatory', 'compliance', 'government', 'policy'], text, limit=3),
            "cyclicality": self._sentences_with(['cyclical', 'seasonal', 'downturn', 'slowdown'], text, limit=2),
            "execution": self._sentences_with(['execution risk', 'delay', 'ramp up', 'scale', 'timeline'], text, limit=3),
            "slowdown_indicators": self._sentences_with(['decline', 'slow', 'weaken', 'deteriorat', 'pressure'], text, limit=3)
        }

    def _leading_indicators(self, text):
        return {
            "metrics_to_watch": self._sentences_with(
                ['watch', 'monitor', 'track', 'look for', 'key metric', 'indicator', 'next quarter'],
                text, limit=5
            ),
            "acceleration_signs": self._sentences_with(
                ['accelerat', 'momentum', 'uptick', 'inflection', 'recovery'], text, limit=3
            ),
            "deterioration_signs": self._sentences_with(
                ['slowdown', 'decelerat', 'weakness', 'soften', 'moderate'], text, limit=3
            )
        }

    def _valuation_insights(self, text):
        return {
            "growth_justification": self._sentences_with(
                ['growth trajectory', 'sustainable growth', 'growth rate', 'CAGR', 'compounding'], text, limit=3
            ),
            "margin_trajectory": self._sentences_with(
                ['margin trajectory', 'margin improvement', 'margin outlook', 'long-term margin'], text, limit=3
            ),
            "cash_flow_durability": self._sentences_with(
                ['cash generation', 'cash flow visibility', 'recurring', 'predictable'], text, limit=3
            )
        }

    def _red_flags(self, text):
        flags = []
        patterns = [
            (r'(?:audit|auditor)\s+(?:qualification|concern|observation)', "Auditor qualification/concern mentioned"),
            (r'related\s+party\s+transaction', "Related party transactions discussed"),
            (r'promoter\s+(?:pledge|selling|dilut)', "Promoter pledge/selling mentioned"),
            (r'(?:increase|rise|higher)\s+(?:in\s+)?(?:debt|borrowing|leverage)', "Rising debt/leverage"),
            (r'(?:decline|fall|drop)\s+(?:in\s+)?(?:cash\s+flow|operating\s+cash)', "Declining cash flow"),
            (r'contingent\s+liabilit', "Contingent liabilities mentioned"),
            (r'(?:impairment|write[\s-]?off|provision)', "Impairment/write-off/provisions"),
            (r'customer\s+concentration', "Customer concentration risk"),
            (r'(?:management|key\s+person)\s+(?:change|exit|resign)', "Management changes"),
        ]
        for pat, label in patterns:
            if re.search(pat, text, re.IGNORECASE):
                flags.append(label)
        return flags

    def _hidden_signals(self, text):
        signals = []
        # Hedging language
        hedge_count = self._count(['may', 'might', 'could', 'possibly', 'potentially', 'somewhat'], text)
        if hedge_count > 15:
            signals.append("🔶 High use of hedging language — management may be uncertain")
        # Deflection
        if re.search(r"(?:I would|let me|we'll come back|we can discuss|offline)", text, re.IGNORECASE):
            signals.append("🔶 Possible deflection of analyst questions detected")
        # Superlatives
        sup = self._count(['best ever', 'record', 'highest ever', 'all-time', 'unprecedented'], text)
        if sup > 3:
            signals.append("🟢 Multiple superlatives used — very bullish tone")
        # Attrition / talent
        if re.search(r'(?:attrition|talent|retention|hiring\s+freeze)', text, re.IGNORECASE):
            signals.append("🔶 Talent/attrition concerns mentioned")
        # Positive hidden
        if re.search(r'(?:market\s+share\s+gain|wallet\s+share|cross[\s-]?sell|upsell)', text, re.IGNORECASE):
            signals.append("🟢 Market share gains / cross-sell opportunities mentioned")

        return signals

    def _conviction_scores(self, exec_summary, revenue, profit, mgmt, risks, red_flags):
        """Calculate short-term and long-term conviction scores (1-10)."""
        st_score = 5
        lt_score = 5

        # Revenue growth impact
        yoy = revenue.get('yoy_growth')
        if yoy:
            if yoy > 20: st_score += 2; lt_score += 2
            elif yoy > 10: st_score += 1; lt_score += 1
            elif yoy < 0: st_score -= 2; lt_score -= 2

        # Margin trend
        if profit['trend'] == 'EXPANDING': st_score += 1; lt_score += 1
        elif profit['trend'] == 'CONTRACTING': st_score -= 1; lt_score -= 1

        # Management tone
        if mgmt['tone'] == 'CONFIDENT': st_score += 1; lt_score += 1
        elif mgmt['tone'] == 'CAUTIOUS': st_score -= 1

        # Guidance
        if mgmt['guidance_direction'] == 'RAISED': st_score += 1; lt_score += 1
        elif mgmt['guidance_direction'] == 'LOWERED': st_score -= 2; lt_score -= 1

        # Executive tone
        if exec_summary['tone'] == 'BULLISH': st_score += 1; lt_score += 1
        elif exec_summary['tone'] == 'DEFENSIVE': st_score -= 1; lt_score -= 1

        # Red flags penalty
        st_score -= len(red_flags) * 0.5
        lt_score -= len(red_flags) * 0.5

        # Risk penalty
        risk_count = sum(len(v) for v in risks.values() if isinstance(v, list))
        if risk_count > 10:
            st_score -= 1
            lt_score -= 1

        st_score = max(1, min(10, round(st_score)))
        lt_score = max(1, min(10, round(lt_score)))

        # Justification
        st_just = []
        lt_just = []
        if yoy and yoy > 15: st_just.append(f"Strong revenue growth at {yoy}%")
        if profit['trend'] == 'EXPANDING': st_just.append("Margins are expanding")
        if mgmt['guidance_direction'] == 'RAISED': st_just.append("Management raised guidance")
        if red_flags: st_just.append(f"{len(red_flags)} red flag(s) detected")
        if exec_summary['tone'] == 'BULLISH': lt_just.append("Overall bullish management tone")
        if yoy and yoy > 10: lt_just.append("Healthy growth trajectory")
        if mgmt['tone'] == 'CONFIDENT': lt_just.append("Management shows high confidence")

        return {
            "short_term": {"score": st_score, "justification": st_just or ["Neutral outlook"]},
            "long_term": {"score": lt_score, "justification": lt_just or ["Neutral outlook"]}
        }

    def _conclusion(self, conviction):
        st = conviction['short_term']['score']
        lt = conviction['long_term']['score']
        avg = (st + lt) / 2

        if avg >= 7:
            verdict = "HIGH_CONVICTION"
            summary = "This appears to be a high-conviction opportunity based on strong fundamentals, positive management commentary, and favorable growth trajectory."
        elif avg >= 5:
            verdict = "NEUTRAL"
            summary = "The company shows mixed signals. While some positives exist, there are enough concerns to warrant caution. Consider position sizing accordingly."
        else:
            verdict = "AVOID"
            summary = "Multiple risk factors and weak fundamentals suggest this may not be an attractive entry point. Consider waiting for better visibility."

        return {"verdict": verdict, "summary": summary}

    # ── main entry point ─────────────────────────────────────────────
    def analyze_transcript(self, symbol, text):
        """Run full professional analysis on transcript text."""
        if not text or len(text) < 200:
            return None

        # Extract quarter
        quarter = "Latest"
        q_match = re.search(r'(Q[1-4])\s*(FY\s*\d{2,4})', text, re.IGNORECASE)
        if q_match:
            quarter = f"{q_match.group(1).upper()} {q_match.group(2).upper().replace(' ', '')}"

        # Build all sections
        exec_summary = self._executive_summary(text)
        revenue = self._revenue_growth(text)
        profit = self._profitability(text)
        cashflow = self._cash_flow(text)
        balance = self._balance_sheet(text)
        mgmt = self._management_commentary(text)
        competitive = self._competitive_position(text)
        strategy = self._strategic_initiatives(text)
        risks = self._risks(text)
        leading = self._leading_indicators(text)
        valuation = self._valuation_insights(text)
        red_flags = self._red_flags(text)
        hidden = self._hidden_signals(text)
        conviction = self._conviction_scores(exec_summary, revenue, profit, mgmt, risks, red_flags)
        conclusion = self._conclusion(conviction)

        # Overall score (0-100 for backward compat)
        overall_score = int(((conviction['short_term']['score'] + conviction['long_term']['score']) / 20) * 100)

        return {
            "quarter": quarter,
            "executive_summary": exec_summary,
            "revenue_growth": revenue,
            "profitability": profit,
            "cash_flow": cashflow,
            "balance_sheet": balance,
            "management_commentary": mgmt,
            "competitive_position": competitive,
            "strategic_initiatives": strategy,
            "risks": risks,
            "leading_indicators": leading,
            "valuation_insights": valuation,
            "conviction_scores": conviction,
            "red_flags": red_flags,
            "hidden_signals": hidden,
            "conclusion": conclusion,
            # backward-compat fields
            "overall_score": overall_score,
            "sentiment": exec_summary['tone'],
            "transcript_summary": text[:500] + "...",
            "key_insights": exec_summary['takeaways'][:5],
            "conviction_factors": {
                "revenue_growth": revenue.get('yoy_growth') or 0,
                "margin_trend": profit['trend'],
                "order_book_strength": "STRONG" if any('order' in t.lower() for t in exec_summary['takeaways']) else "MODERATE",
                "sentiment": exec_summary['tone']
            },
            "margin_trend": profit['trend'],
            "order_book_strength": "STRONG" if any('order' in t.lower() for t in exec_summary['takeaways']) else "MODERATE",
        }
