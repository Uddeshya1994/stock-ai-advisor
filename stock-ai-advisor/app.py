import streamlit as st
import yfinance as yf
import csv
import os
from datetime import datetime, timedelta
import pandas as pd

from data_fetcher import get_stock_data
from email_utils import build_stock_email, send_email


# ================= PAGE CONFIG =================
st.set_page_config(page_title="Stock Insight – Beginner Traders", layout="centered")


# ================= HELPERS =================
def rupees(v):
    return "N/A" if v is None else f"₹ {round(v, 2)}"

def to_cr(v):
    return "N/A" if v is None else f"₹ {round(v / 1_00_00_000, 2)} Cr"

def roe_percent(v):
    return "N/A" if v is None else f"{round(v * 100, 2)} %"


# ================= DEBT TREND =================
def get_debt_trend(stock_code):
    try:
        bs = yf.Ticker(stock_code).balance_sheet
        if bs.empty or "Total Debt" not in bs.index:
            return None, None

        d = bs.loc["Total Debt"]
        cur = d.iloc[0]
        y1 = d.iloc[1] if len(d) > 1 else None
        y3 = d.iloc[3] if len(d) > 3 else None

        def pct(old, new):
            return round(((new - old) / old) * 100, 2) if old and old > 0 else None

        return pct(y1, cur), pct(y3, cur)
    except Exception:
        return None, None


# ================= CONFIDENCE SCORE (FIXED LOGIC) =================
def calculate_confidence(stock_data):
    score = 100

    roe = stock_data.get("ROE")
    dte = stock_data.get("Debt to Equity")

    if roe is None or roe * 100 < 15:
        score -= 30

    if dte is not None and dte > 1:
        score -= 30

    return max(0, min(100, score))


# ================= BEGINNER RISK LEVEL =================
def beginner_risk_level(stock_data, confidence, debt_1y, debt_3y):
    flags = 0
    reasons = []

    if (debt_1y and debt_1y > 0) or (debt_3y and debt_3y > 0):
        flags += 1
        reasons.append("Debt is increasing")

    if stock_data.get("Debt to Equity") and stock_data["Debt to Equity"] > 1:
        flags += 1
        reasons.append("High debt to equity ratio")

    if confidence < 50:
        flags += 1
        reasons.append("Low confidence score")

    if flags >= 2:
        return "🔴 HIGH RISK", reasons
    elif flags == 1:
        return "🟡 MEDIUM RISK", reasons
    else:
        return "🟢 LOW RISK", ["No major beginner risks"]


# ================= INVESTMENT SIMULATION =================
def investment_simulation(stock_code, current_price):
    ticker = yf.Ticker(stock_code)
    today = datetime.today()
    years_list = [1, 2, 3, 5, 10]

    results = []

    for y in years_list:
        target_date = today - timedelta(days=365 * y)
        hist = ticker.history(
            start=target_date - timedelta(days=5),
            end=target_date + timedelta(days=5)
        )

        if hist.empty:
            results.append((y, None, None, None))
            continue

        buy_price = round(hist.iloc[0]["Close"], 2)
        return_pct = round(((current_price - buy_price) / buy_price) * 100, 2)
        results.append((y, buy_price, current_price, return_pct))

    return results


# ================= SAVE CONFIDENCE =================
def save_confidence(company, score):
    file = "confidence_history.csv"
    exists = os.path.exists(file)

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Timestamp", "Company Name", "Confidence Score"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            company,
            score
        ])


# ================= SESSION STATE =================
for key in ["stock_data", "analysis", "confidence", "risk", "debt", "stock_code"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ================= UI =================
st.title("📊 Stock Insight – Beginner Retail Traders")
st.caption("Fixed logic • Transparent • Long-term focused")


with st.expander("ℹ️ How this analysis works"):
    st.markdown("""
• Confidence starts at **100**
• −30 if **ROE < 15%**
• −30 if **Debt to Equity > 1**

Risk level is based on:
• Debt trend  
• Leverage  
• Confidence score  
""")


stock_code = st.text_input(
    "Enter NSE / BSE Stock Code",
    placeholder="Example: TCS.NS"
)


# ================= ANALYZE =================
if st.button("Analyze"):
    if stock_code:
        stock_data, analysis = get_stock_data(stock_code)
        debt_1y, debt_3y = get_debt_trend(stock_code)

        confidence = calculate_confidence(stock_data)
        risk, reasons = beginner_risk_level(
            stock_data, confidence, debt_1y, debt_3y
        )

        st.session_state.stock_code = stock_code
        st.session_state.stock_data = stock_data
        st.session_state.analysis = analysis
        st.session_state.confidence = confidence
        st.session_state.risk = (risk, reasons)
        st.session_state.debt = (debt_1y, debt_3y)

        save_confidence(stock_data.get("Company Name"), confidence)


# ================= RESULTS =================
if st.session_state.stock_data:
    sd = st.session_state.stock_data
    d1, d3 = st.session_state.debt

    st.subheader("📈 Confidence Score")
    st.progress(st.session_state.confidence / 100)
    st.markdown(f"### {st.session_state.confidence} / 100")

    st.subheader("🛡️ Beginner Risk Level")
    st.markdown(f"### {st.session_state.risk[0]}")
    for r in st.session_state.risk[1]:
        st.write("•", r)

    st.divider()

    # ================= KEY METRICS =================
    st.subheader("📌 Key Metrics")

    st.write("Company Name:", sd.get("Company Name"))
    st.write("Current Price:", rupees(sd.get("Current Price")))
    st.write("1Y Return (%):", sd.get("1Y Return (%)"))

    st.markdown("— Valuation —")
    st.write("PE Ratio:", sd.get("PE Ratio"))
    st.write("Market Cap:", to_cr(sd.get("Market Cap")))

    st.markdown("— Profitability —")
    st.write("ROE:", roe_percent(sd.get("ROE")))

    st.markdown("— Debt & Risk —")
    st.write("Total Debt:", to_cr(sd.get("Total Debt")))
    st.write("Debt to Equity:", sd.get("Debt to Equity"))
    st.write("Debt Change (1Y):", f"{d1} %" if d1 is not None else "N/A")
    st.write("Debt Change (3Y):", f"{d3} %" if d3 is not None else "N/A")

    st.markdown("— Price Range —")
    st.write("52W High:", rupees(sd.get("52 Week High")))
    st.write("52W Low:", rupees(sd.get("52 Week Low")))

    st.divider()

    # ================= INVESTMENT SIMULATION =================
    st.subheader("📊 If You Bought 1 Share Earlier")

    sim = investment_simulation(
        st.session_state.stock_code,
        sd.get("Current Price")
    )

    sim_df = pd.DataFrame(
        [
            [f"{y} Years Ago",
             "N/A" if buy is None else f"₹ {buy}",
             f"₹ {sd.get('Current Price')}",
             "N/A" if ret is None else f"{ret} %"]
            for y, buy, _, ret in sim
        ],
        columns=[
            "Investment Time",
            "Buy Price (1 Share)",
            "Value Today",
            "Return %"
        ]
    )

    st.dataframe(sim_df, use_container_width=True)

    st.divider()

    # ================= EMAIL SEND =================
    st.subheader("📧 Send This Analysis via Email")

    email = st.text_input("Recipient Email")

    if st.button("Send Email"):
        if email:
            body = build_stock_email(
                stock_data=sd,
                confidence_score=st.session_state.confidence,
                risk_level=st.session_state.risk[0],
                debt_1y=d1,
                debt_3y=d3,
                app_url="https://your-app-url.streamlit.app",
                stock_code=st.session_state.stock_code
            )

            send_email(
                sender_email="uddeshya.srivastava9@gmail.com",
                receiver_email=email,
                subject=f"Stock Insight – {sd.get('Company Name')}",
                body=body
            )

            st.success("📧 Email sent successfully!")
        else:
            st.warning("Please enter an email address.")

    st.divider()

    # ================= SUBSCRIPTION =================
    st.subheader("📬 Subscribe for Weekly Updates")

    sub_email = st.text_input("Email for subscription", key="sub_email")

    if st.button("Subscribe"):
        if sub_email:
            file = "subscriptions.csv"
            exists = os.path.exists(file)

            with open(file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not exists:
                    writer.writerow([
                        "email", "stock_code", "frequency", "subscribed_on"
                    ])

                writer.writerow([
                    sub_email,
                    st.session_state.stock_code,
                    "Weekly",
                    datetime.now().strftime("%Y-%m-%d")
                ])

            st.success("✅ Subscribed successfully!")
        else:
            st.warning("Please enter an email address.")


# ================= CONFIDENCE HISTORY =================
st.divider()
st.subheader("📁 Confidence History")

if os.path.exists("confidence_history.csv"):
    df = pd.read_csv("confidence_history.csv")
    st.dataframe(df, use_container_width=True)

    if st.button("🗑️ Clear Confidence History"):
        os.remove("confidence_history.csv")
        st.rerun()
else:
    st.info("No confidence history yet.")
