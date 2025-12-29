def analyze_stock(stock):
    pros = []
    cons = []

    roe = stock.get("ROE")
    pe = stock.get("PE Ratio")
    debt_ratio = stock.get("Debt to Equity")
    ret_1y = stock.get("1Y Return (%)")
    price = stock.get("Current Price")
    high = stock.get("52 Week High")
    low = stock.get("52 Week Low")

    # Profitability
    if roe:
        roe_pct = roe * 100
        if roe_pct >= 25:
            pros.append("Excellent profitability (ROE above 25%)")
        elif roe_pct >= 15:
            pros.append("Strong profitability (ROE above 15%)")
        else:
            cons.append("Low profitability")

    # Debt Level
    if debt_ratio is not None:
        if debt_ratio < 0.5:
            pros.append("Low debt improves financial stability")
        elif debt_ratio > 1:
            cons.append("High debt increases risk")

    # Valuation
    if pe:
        if pe < 25:
            pros.append("Valuation is reasonable for long-term investors")
        elif pe > 40:
            cons.append("Stock valuation looks expensive")

    # Performance
    if ret_1y is not None:
        if ret_1y > 10:
            pros.append("Good price performance in last 1 year")
        elif ret_1y < 0:
            cons.append("Negative return in last 1 year")

    # Price Position
    if price and high and low:
        if price < low * 1.15:
            pros.append("Trading near lower range (better margin of safety)")
        elif price > high * 0.9:
            cons.append("Trading near upper range (limited upside)")

    # Final Verdict
    if len(pros) >= 4 and len(cons) <= 1:
        verdict = "Good for long-term investment"
        advice = "Can be considered for SIP or gradual accumulation"
    elif len(cons) >= 3:
        verdict = "High risk at current levels"
        advice = "Better to wait or avoid for now"
    else:
        verdict = "Moderate opportunity"
        advice = "Invest cautiously with partial exposure"

    return {
        "Pros": pros,
        "Cons": cons,
        "Verdict": verdict,
        "Investment Advice": advice
    }


def investor_confidence_score(stock):
    score = 0

    roe = stock.get("ROE")
    pe = stock.get("PE Ratio")
    debt_ratio = stock.get("Debt to Equity")
    ret_1y = stock.get("1Y Return (%)")
    price = stock.get("Current Price")
    high = stock.get("52 Week High")
    low = stock.get("52 Week Low")

    # ROE (25)
    if roe:
        roe_pct = roe * 100
        if roe_pct >= 25:
            score += 25
        elif roe_pct >= 15:
            score += 18
        elif roe_pct >= 10:
            score += 10

    # Debt to Equity (20)
    if debt_ratio is not None:
        if debt_ratio < 0.5:
            score += 20
        elif debt_ratio < 1:
            score += 12
        else:
            score += 5

    # Valuation PE (15)
    if pe:
        if pe < 25:
            score += 15
        elif pe < 40:
            score += 8
        else:
            score += 3

    # Price Position (15)
    if price and high and low:
        if price < low * 1.15:
            score += 15
        elif price < high * 0.9:
            score += 10
        else:
            score += 5

    # 1-Year Return (10)
    if ret_1y is not None:
        if ret_1y > 15:
            score += 10
        elif ret_1y > 0:
            score += 6
        else:
            score += 2

    return min(score, 100)
