def format_whatsapp(result):
    return f"""
🕵️‍♂️ Fake Review Detection Report

📝 Total Reviews Analyzed: {result['total']}

🟢 Genuine Reviews: {result['genuine']}
🟡 Suspicious Reviews: {result['suspicious']}
🔴 Likely Fake Reviews: {result['fake']}

⚠️ Common Repeated Words:
{", ".join([w[0] for w in result['common_words']])}

📌 Tip:
Avoid products with many short generic 5⭐ reviews
"""
