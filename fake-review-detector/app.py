import streamlit as st
from review_scraper import extract_asin, fetch_reviews
from review_analyzer import analyze_reviews
from formatter import format_whatsapp

st.set_page_config(page_title="Fake Review Detector")

st.title("🕵️‍♂️ Fake / Biased Review Detector")
st.write("Paste an Amazon product link to analyze review authenticity")

url = st.text_input("Amazon Product URL")

if st.button("Analyze Reviews"):
    asin = extract_asin(url)

    if not asin:
        st.error("Invalid Amazon URL")
    else:
        with st.spinner("Fetching reviews..."):
            reviews = fetch_reviews(asin)

        if not reviews:
            st.warning("Could not fetch reviews. Try again later.")
        else:
            result = analyze_reviews(reviews)

            st.subheader("📱 WhatsApp Ready Output")
            st.code(format_whatsapp(result), language="text")
