import streamlit as st

from matching import (
    build_item_data,
    filter_comparables
)

st.set_page_config(
    page_title="TriftIQ",
    layout="wide",
    page_icon="🛍️",
)

st.title(
    "🛍️ ThriftIQ"
)

st.markdown("""
## Welcome

Use the sidebar to navigate:

- Reseller Intelligence
- Listing Analyzer
- Sourcing Assistant
- Draft Creator
""")