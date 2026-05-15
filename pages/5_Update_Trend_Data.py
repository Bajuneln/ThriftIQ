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

    page_title="Trend Data Collection",

    layout="wide"
)
# =====================================
# UPDATE TREND DATA
# =====================================

st.subheader(
    "Trend Data Collection"
)

st.markdown("""
Collect fresh sold listing data
from eBay to track:
- trend momentum
- resale demand
- buyer behavior
- market shifts
""")

if st.button(
    "Update Trend Data"
):

    with st.spinner(
        "Collecting sold listings..."
    ):

        save_trend_snapshot()

    st.success(
        "Trend snapshot saved."
    )
