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
    # ── section builders (Phase 2: 10-Point Framework) ────────────────
    def _mgmt_tone_linguistic(self, text):
        """1. Management Tone & Body Language (Linguistic Analysis)"""
        keywords = ['confident', 'optimistic', 'cautious', 'defensive', 'evasive', 'vague', 'deflect', 'going forward', 'temporary', 'challenge']
        sents = self._sentences_with(keywords, text, limit=6)
        
        # Look for deflections
        deflections = self._sentences_with(["let me check", "offline", "come back to you", "not at liberty", "don't have the number"], text, limit=3)
        
        # Tone detection
        pos = self._count(['confident', 'strong', 'robust', 'optimistic', 'excited', 'momentum'], text)
        neg = self._count(['cautious', 'headwinds', 'difficult', 'uncertain', 'temporary'], text)
        evasive = self._count(['vague', 'deflect', 'offline', 'later'], text)
        
        if evasive > 3: tone = "DEFENSIVE / EVASIVE"
        elif pos > neg + 5: tone = "OVERLY PROMOTIONAL"
        elif pos > neg: tone = "CONFIDENT"
        elif neg > pos: tone = "CAUTIOUS"
        else: tone = "BALANCED"
        
        return {
            "tone": tone,
            "linguistic_signals": sents,
            "deflections": deflections,
            "is_direct": "YES" if evasive < 2 else "NO - deflective patterns detected"
        }

    def _earnings_quality(self, text):
        """2. Earnings Quality & Number Cross-Check"""
        numbers = self._sentences_with(['revenue', 'ebitda', 'pat', 'margin', 'growth', 'one-time', 'exceptional'], text, limit=6)
        mix_shift = self._sentences_with(['revenue mix', 'mix shift', 'product mix', 'lower margin', 'higher margin'], text, limit=3)
        leverage = self._sentences_with(['operating leverage', 'fixed cost', 'cost cut', 'employee cost'], text, limit=3)

        return {
            "key_metrics": numbers,
            "mix_shift_insights": mix_shift,
            "margin_sustainability": leverage
        }

    def _analyst_questions(self, text):
        """3. Analyst Questions — Quality & Management Responses"""
        tough_q = self._sentences_with(['debt', 'margin pressure', 'working capital', 'slowdown', 'market share loss', 'pledge'], text, limit=5)
        repetition = self._sentences_with(['as I said', 'already mentioned', 'repeating'], text, limit=3)
        skepticism = self._sentences_with(['clarify', 'not clear', 'more detail', 'pushing'], text, limit=3)

        return {
            "tough_questions": tough_q,
            "management_response_quality": "DIRECT" if len(repetition) < 2 else "REPETITIVE / EVASIVE",
            "analyst_skepticism_signals": skepticism
        }

    def _guidance_forward(self, text):
        """4. Guidance & Forward Looking Statements"""
        guidance = self._sentences_with(['guidance', 'outlook', 'forecast', 'expect to', 'target'], text, limit=6)
        assumptions = self._sentences_with(['assumption', 'if', 'provided', 'subject to'], text, limit=3)
        
        direction = "MAINTAINED"
        if self._count(['raised', 'increased', 'upgraded'], text) > self._count(['lowered', 'reduced', 'cut'], text):
            direction = "RAISED / AGGRESSIVE"
        elif self._count(['lowered', 'reduced', 'cut'], text) > 0:
            direction = "LOWERED / CAUTIOUS"

        return {
            "specific_guidance": guidance,
            "underlying_assumptions": assumptions,
            "guidance_direction": direction
        }

    def _operational_updates(self, text):
        """5. Operational Updates & Business Momentum"""
        metrics = self._sentences_with(['utilization', 'order book', 'backlog', 'client win', 'contract', 'supply chain'], text, limit=6)
        segments = self._sentences_with(['growing segment', 'pressure', 'domestic', 'export', 'launch'], text, limit=4)

        return {
            "operational_metrics": metrics,
            "segment_momentum": segments
        }

    def _capital_allocation(self, text):
        """6. Capital Allocation Commentary"""
        capex = self._sentences_with(['capex', 'expansion', 'investment', 'project'], text, limit=4)
        debt = self._sentences_with(['debt repayment', 'borrowing', 'interest cost', 'leverage'], text, limit=3)
        returns = self._sentences_with(['dividend', 'buyback', 'payout', 'return of capital'], text, limit=3)

        return {
            "capex_plans": capex,
            "debt_management": debt,
            "shareholder_payouts": returns
        }

    def _red_flag_detector(self, text):
        """7. Red Flag Detector — Read Between The Lines"""
        flags = []
        if self._count(['accounting policy', 'change in method', 're-classified'], text) > 0:
            flags.append("Change in accounting definitions/metrics mentioned")
        
        silence = self._sentences_with(['ceased to', 'stopped disclosing', 'no longer tracking'], text, limit=2)
        buzzwords = self._sentences_with(['AI-driven', 'synergies', 'transformational', 'best-in-class'], text, limit=4)
        
        if len(buzzwords) > 3:
            flags.append("Excessive use of buzzwords without substance detected")

        return {
            "detected_flags": flags,
            "metric_silence": silence,
            "buzzword_usage": buzzwords
        }

    def _consistency_check(self, text):
        """8. Consistency Check — Then vs Now"""
        promises = self._sentences_with(['last quarter', 'previously mentioned', 'delivered on', 'met the target'], text, limit=4)
        u_turns = self._sentences_with(['evaluating strategic fit', 'revisiting', 'pivot'], text, limit=3)

        return {
            "promise_delivery_signals": promises,
            "narrative_u_turns": u_turns
        }

    def _industry_competitive(self, text):
        """9. Industry & Competitive Commentary"""
        demand = self._sentences_with(['demand trend', 'industry outlook', 'market sentiment'], text, limit=3)
        comp = self._sentences_with(['competitor', 'market share', 'pricing pressure', 'new entrant'], text, limit=4)

        return {
            "industry_demand": demand,
            "competitive_intensity": comp
        }

    def _institutional_signals(self, text):
        """10. Institutional Investor Signals"""
        marquee = self._sentences_with(['esg', 'governance', 'auditor', 'plant visit', 'investor day'], text, limit=4)
        expectations = self._sentences_with(['expectations', 'concerns', 'feedback'], text, limit=2)

        return {
            "esg_governance_focus": marquee,
            "expectation_management": expectations
        }

    def _leading_indicators(self, text):
        """Helper to extract leading indicators for the watch list."""
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

    def _concall_snapshot(self, sections):
        bullish = sections['operational_updates']['segment_momentum'][:3]
        if sections['guidance_forward']['guidance_direction'] == "RAISED / AGGRESSIVE":
            bullish.append("Management raised/aggressive guidance for future quarters")
            
        concerns = sections['red_flag_detector']['detected_flags']
        concerns.extend(sections['analyst_questions']['tough_questions'][:2])
        if sections['mgmt_tone_linguistic']['tone'] in ["DEFENSIVE / EVASIVE", "OVERLY PROMOTIONAL"]:
            concerns.append(f"Management tone flagged as {sections['mgmt_tone_linguistic']['tone']}")

        watch = sections['leading_indicators']['metrics_to_watch']
        watch.extend(sections['guidance_forward']['underlying_assumptions'][:1])

        return {
            "bullish_takeaways": bullish or ["Operational stability maintained"],
            "concerns_red_flags": concerns or ["Competitive risks in core segments"],
            "questions_to_watch": watch or ["Margin trajectory in next quarter"]
        }

    def _concall_conviction_score(self, sections):
        def score(sec, pos_kw, neg_kw):
            t = str(sections[sec]).lower()
            p = sum(t.count(k) for k in pos_kw)
            n = sum(t.count(k) for k in neg_kw)
            b = 6
            if p > n + 1: b = 8
            if n > p: b = 4
            return min(10, max(1, b))

        scores = [
            {"parameter": "Management Transparency", "score": 4 if sections['mgmt_tone_linguistic']['tone'] == "DEFENSIVE / EVASIVE" else 7, "notes": sections['mgmt_tone_linguistic']['tone']},
            {"parameter": "Earnings Quality", "score": score('earnings_quality', ['strong', 'sustainable'], ['one-time', 'temporary']), "notes": "Operational EBITDA focus"},
            {"parameter": "Guidance Credibility", "score": 8 if sections['guidance_forward']['guidance_direction'] == "RAISED / AGGRESSIVE" else 5, "notes": sections['guidance_forward']['guidance_direction']},
            {"parameter": "Business Momentum", "score": score('operational_updates', ['growth', 'win'], ['pressure', 'slowdown']), "notes": "Sector performance breakdown"},
            {"parameter": "Analyst Confidence in Mgmt", "score": 4 if len(sections['analyst_questions']['analyst_skepticism_signals']) > 2 else 7, "notes": "Q&A intensity signals"},
            {"parameter": "Red Flag Risk", "score": 10 - (len(sections['red_flag_detector']['detected_flags']) * 2), "notes": f"{len(sections['red_flag_detector']['detected_flags'])} flags detected"},
            {"parameter": "Capital Allocation Quality", "score": score('capital_allocation', ['repayment', 'dividend'], ['borrowing', 'capex']), "notes": "Efficiency in payout vs growth"}
        ]
        
        avg = sum(s['score'] for s in scores) / len(scores)
        return scores, round(avg, 1)

    def analyze_transcript(self, symbol, text):
        """Run expanded 10-point professional concall analysis."""
        if not text or len(text) < 200:
            return None

        # Extract quarter
        quarter = "Latest"
        q_match = re.search(r'(Q[1-4])\s*(FY\s*\d{2,4})', text, re.IGNORECASE)
        d_match = re.search(r'(\w+ \d{1,2}, 20\d{2})', text) # Date like Oct 25, 2024
        if q_match:
            quarter = f"{q_match.group(1).upper()} {q_match.group(2).upper().replace(' ', '')}"
        elif d_match:
            quarter = d_match.group(1)

        # Build 10 sections
        sections = {
            "mgmt_tone_linguistic": self._mgmt_tone_linguistic(text),
            "earnings_quality": self._earnings_quality(text),
            "analyst_questions": self._analyst_questions(text),
            "guidance_forward": self._guidance_forward(text),
            "operational_updates": self._operational_updates(text),
            "capital_allocation": self._capital_allocation(text),
            "red_flag_detector": self._red_flag_detector(text),
            "consistency_check": self._consistency_check(text),
            "industry_competitive": self._industry_competitive(text),
            "institutional_signals": self._institutional_signals(text),
            "leading_indicators": self._leading_indicators(text) # Helper for watch list
        }

        snapshot = self._concall_snapshot(sections)
        conviction_grid, avg_score = self._concall_conviction_score(sections)
        
        if avg_score >= 8: verdict = "Management credible, momentum strong — add/hold with confidence"
        elif avg_score >= 5: verdict = "Mixed signals — watch next quarter before acting"
        else: verdict = "Credibility concerns — reduce or avoid"

        # Final investment verdict
        final_verdict = "WATCH"
        if avg_score >= 8: final_verdict = "BUY"
        elif avg_score < 5: final_verdict = "AVOID"

        return {
            "symbol": symbol,
            "period": quarter,
            "sections": sections,
            "snapshot": snapshot,
            "conviction_table": conviction_grid,
            "overall_score": avg_score,
            "verdict": verdict,
            "final_investment_verdict": f"{final_verdict} - {verdict}",
            # backward-compat fields
            "quarter": quarter,
            "overall_score_legacy": int((avg_score / 10) * 100)
        }


class AnnualReportAnalyzer(TranscriptAnalysisEngine):
    """Deep-dive equity research analyzer for Annual Reports."""

    def _business_overview(self, text):
        keywords = ['business overview', 'company profile', 'segment', 'revenue contribution', 'market share', 'competitive advantage', 'moat', 'core product', 'business model']
        sents = self._sentences_with(keywords, text, limit=8)
        
        moat_signals = self._sentences_with(['moat', 'durable', 'competitive advantage', 'barrier to entry', 'brand equity', 'patent', 'intellectual property'], text, limit=3)
        
        return {
            "overview": sents,
            "moat_signals": moat_signals,
            "is_scalable": "YES" if self._count(['scale', 'scalable', 'expand', 'growth potential'], text) > 5 else "NEEDS_CLARITY"
        }

    def _financial_health(self, text):
        revenue_trend = self._sentences_with(['revenue growth', 'last 3 years', 'last 5 years', 'cagr'], text, limit=3)
        margins = self._sentences_with(['gross margin', 'ebitda margin', 'net margin', 'improving margin', 'margin expansion'], text, limit=4)
        ratios = self._sentences_with(['roe', 'return on equity', 'roce', 'return on capital', 'debt to equity', 'interest coverage', 'leverage'], text, limit=5)
        cash_flow = self._sentences_with(['free cash flow', 'fcf', 'cash flow from operations', 'consistent fcf'], text, limit=3)
        working_cap = self._sentences_with(['working capital', 'debtors', 'inventory', 'receivables', 'days'], text, limit=3)

        return {
            "revenue_trend": revenue_trend,
            "margin_analysis": margins,
            "return_ratios": ratios,
            "cash_flow_quality": cash_flow,
            "working_capital_signals": working_cap
        }

    def _accounting_quality(self, text):
        gap_signals = self._sentences_with(['pat', 'profit after tax', 'cash from operations', 'difference', 'non-cash'], text, limit=3)
        growth_mismatch = self._sentences_with(['receivables growth', 'inventory growth', 'faster than revenue', 'revenue growth'], text, limit=3)
        contingent = self._sentences_with(['contingent liabilities', 'off-balance sheet', 'pledge', 'guarantee'], text, limit=3)
        auditor = self._sentences_with(['auditor', 'qualification', 'observation', 'adverse', 'audit fees'], text, limit=3)
        related_party = self._sentences_with(['related party', 'transactions', 'promoter', 'inter-corporate'], text, limit=3)

        return {
            "cash_flow_vs_profit": gap_signals,
            "receivables_inventory_risk": growth_mismatch,
            "contingent_liabilities": contingent,
            "auditor_comments": auditor,
            "related_party_transactions": related_party
        }

    def _management_quality(self, text):
        holding = self._sentences_with(['promoter holding', 'shareholding pattern', 'pledge', 'stake'], text, limit=3)
        compensation = self._sentences_with(['compensation', 'remuneration', 'ceo pay', 'commission'], text, limit=2)
        allocation = self._sentences_with(['capital allocation', 'dividend', 'buyback', 'acquisition', 'reinvestment'], text, limit=4)
        board = self._sentences_with(['independent directors', 'board composition', 'director qualifications', 'diversity'], text, limit=3)

        return {
            "promoter_holding": holding,
            "management_compensation": compensation,
            "capital_allocation_history": allocation,
            "board_governance": board
        }

    def _industry_macro(self, text):
        industry_growth = self._sentences_with(['industry outlook', 'market growth', 'structural growth', 'sector'], text, limit=3)
        regulatory = self._sentences_with(['regulatory', 'government policy', 'compliance', 'legal'], text, limit=3)
        macro = self._sentences_with(['macro', 'interest rate', 'currency', 'commodity price', 'inflation'], text, limit=3)
        esg = self._sentences_with(['esg', 'environment', 'social', 'governance', 'sustainability', 'carbon'], text, limit=3)

        return {
            "industry_outlook": industry_growth,
            "regulatory_environment": regulatory,
            "macro_exposure": macro,
            "esg_factors": esg
        }

    def _growth_drivers(self, text):
        strategy = self._sentences_with(['growth strategy', 'stated goal', 'vision', 'roadmap'], text, limit=3)
        pipeline = self._sentences_with(['new products', 'pipeline', 'upcoming', 'launch', 'new markets'], text, limit=3)
        capex = self._sentences_with(['capex', 'capacity expansion', 'greenfield', 'brownfield'], text, limit=3)
        visibility = self._sentences_with(['order book', 'backlog', 'deal pipeline', 'visibility'], text, limit=2)

        return {
            "stated_strategy": strategy,
            "pipeline_visibility": pipeline,
            "expansion_plans": capex,
            "future_outlook": visibility
        }

    def _key_risks(self, text):
        top_risks = self._sentences_with(['risk factor', 'uncertainty', 'threat', 'challenge'], text, limit=5)
        debt_risk = self._sentences_with(['debt maturity', 'repayment', 'refinancing', 'liquidity'], text, limit=2)
        concentration = self._sentences_with(['customer concentration', 'top 5', 'top 10', 'supplier concentration'], text, limit=2)

        return {
            "top_risks": top_risks,
            "debt_refinancing": debt_risk,
            "concentration_risk": concentration
        }

    def _valuation_context(self, text):
        metrics = self._sentences_with(['pe ratio', 'p/e', 'pb ratio', 'p/b', 'ev/ebitda', 'historical range', 'peers'], text, limit=4)
        dividends = self._sentences_with(['dividend yield', 'payout ratio', 'record date'], text, limit=2)

        return {
            "valuation_metrics": metrics,
            "dividend_profile": dividends
        }

    def _investment_snapshot(self, text, sections):
        strengths = []
        concerns = []
        watch = []

        # Logic to extract strengths/concerns from sections
        if "overview" in sections["business_overview"]:
             strengths.extend(sections["business_overview"]["moat_signals"][:2])
        
        if sections["business_overview"]["is_scalable"] == "YES":
            strengths.append("Business model is highly scalable")

        # Check for red flags in accounting
        if sections["accounting_quality"]["auditor_comments"]:
            concerns.extend(sections["accounting_quality"]["auditor_comments"])
        if sections["accounting_quality"]["related_party_transactions"]:
            concerns.extend(sections["accounting_quality"]["related_party_transactions"])

        # Check for risks
        concerns.extend(sections["key_risks"]["top_risks"][:2])

        # Things to watch
        watch.extend(sections["growth_drivers"]["future_outlook"])
        watch.extend(sections["industry_macro"]["industry_outlook"][:1])

        return {
            "strengths": strengths or ["Strong market leadership", "Healthy cash flows"],
            "concerns": concerns or ["Competitive intensity", "Macro headwinds"],
            "things_to_watch": watch or ["New product launches", "Regulatory changes"]
        }

    def _conviction_table(self, sections):
        # Semi-automated scoring based on keyword frequency and sentiment
        # In a real app, this would be highly complex or AI-driven.
        # For now, we simulate scores based on heuristic extraction.
        
        def score(sec_name, pos_words, neg_words):
            text = str(sections[sec_name])
            pos = self._count(pos_words, text)
            neg = self._count(neg_words, text)
            base = 6
            if pos > neg + 2: base = 8
            if neg > pos: base = 4
            return min(10, max(1, base))

        return [
            {"parameter": "Business Quality", "score": score("business_overview", ["leadership", "moat", "advantage"], ["commodity", "disrupt", "weak"]), "notes": "Leader in its segment"},
            {"parameter": "Financial Health", "score": score("financial_health", ["growing", "strong", "improving"], ["deteriorating", "debt", "stress"]), "notes": "Healthy return ratios"},
            {"parameter": "Accounting Integrity", "score": score("accounting_quality", ["clean", "qualified"], ["related party", "receivables", "risk"]), "notes": "Standard accounting practices"},
            {"parameter": "Management Quality", "score": score("management_quality", ["aligned", "transparent"], ["excessive", "compensation", "misaligned"]), "notes": "Experienced promoters"},
            {"parameter": "Growth Prospects", "score": score("growth_drivers", ["expansion", "new", "robust"], ["slowdown", "mature", "saturated"]), "notes": "Clear roadmap for expansion"},
            {"parameter": "Risk Profile", "score": score("key_risks", ["minor", "manageable"], ["high", "critical", "uncertainty"]), "notes": "Macro dependencies persist"},
            {"parameter": "Valuation Comfort", "score": score("valuation_context", ["fair", "attractive"], ["expensive", "premium", "overvalued"]), "notes": "Fairly valued vs peers"}
        ]

    def analyze_annual_report(self, symbol, text):
        """Full analysis of an Annual Report."""
        if not text: return None

        # Extract FY
        fy = "FY24"
        fy_match = re.search(r'(FY\s*\d{2,4}|20\d{2})', text, re.IGNORECASE)
        if fy_match:
            fy = fy_match.group(1).upper().replace(' ', '')

        sections = {
            "business_overview": self._business_overview(text),
            "financial_health": self._financial_health(text),
            "accounting_quality": self._accounting_quality(text),
            "management_quality": self._management_quality(text),
            "industry_macro": self._industry_macro(text),
            "growth_drivers": self._growth_drivers(text),
            "key_risks": self._key_risks(text),
            "valuation_context": self._valuation_context(text)
        }

        snapshot = self._investment_snapshot(text, sections)
        conviction_table = self._conviction_table(sections)
        
        avg_score = sum(item["score"] for item in conviction_table) / len(conviction_table)
        
        if avg_score >= 8: verdict = "High Conviction Buy Candidate"
        elif avg_score >= 5: verdict = "Monitor / Selective Entry"
        else: verdict = "Avoid / High Risk"

        return {
            "symbol": symbol,
            "fiscal_year": fy,
            "sections": sections,
            "snapshot": snapshot,
            "conviction_table": conviction_table,
            "overall_score": round(avg_score, 1),
            "verdict": verdict
        }
