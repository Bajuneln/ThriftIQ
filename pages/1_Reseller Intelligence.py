import streamlit as st

from trend_engine import (

    save_trend_snapshot,

    collect_sold_titles,

    discover_new_terms,

    interpret_trend_changes,

    generate_trend_summary
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(

    page_title="ThriftIQ",

    page_icon="🛍️",

    layout="wide"
)

# =====================================
# HEADER
# =====================================

st.title(
    "🛍️ ThriftIQ"
)

st.markdown("""
Live reseller market intelligence
powered by real eBay sold data.
""")

# =====================================
# LIVE RESELLER INTELLIGENCE
# =====================================

st.subheader(
    "Live Reseller Intelligence"
)

st.markdown("""
Analyze:
- rising aesthetics
- hot brands
- fast-moving categories
- seasonal opportunities
- sell-through signals
- sourcing risks
""")

if st.button(
    "Generate Market Intelligence"
):

    with st.spinner(
        "Analyzing resale market..."
    ):

        titles = (
            collect_sold_titles()
        )

        intelligence = (
            discover_new_terms(
                titles
            )
        )

    st.markdown(
        intelligence
    )

# =====================================
# FOOTER NOTES
# =====================================

st.subheader(
    "Reseller Intelligence Notes"
)

st.info("""
This dashboard analyzes:
- real sold eBay listings
- repeated market language
- trend momentum
- buyer demand patterns
- resale market signals

Market intelligence improves
over time as more trend
snapshots are collected.
""")
