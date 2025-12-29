import yfinance as yf
from analysis_engine import analyze_stock


def get_stock_data(stock_code):
    stock = yf.Ticker(stock_code)
    info = stock.info

    hist = stock.history(period="1y")
    if not hist.empty:
        start_price = hist.iloc[0]["Open"]
        end_price = hist.iloc[-1]["Close"]
        one_year_return = round(
            ((end_price - start_price) / start_price) * 100, 2
        )
    else:
        one_year_return = None

    data = {
        "Company Name": info.get("longName"),
        "Current Price": info.get("currentPrice"),
        "1Y Return (%)": one_year_return,
        "Market Cap": info.get("marketCap"),
        "Total Debt": info.get("totalDebt"),
        "Debt to Equity": info.get("debtToEquity"),
        "PE Ratio": info.get("trailingPE"),
        "ROE": info.get("returnOnEquity"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow"),
    }

    analysis = analyze_stock(data)
    return data, analysis
