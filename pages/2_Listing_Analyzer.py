import streamlit as st
import json

from utils import (
    get_ebay_token,
    search_sold_comps,
    search_active_listings,
    calculate_sell_through,
    calculate_pricing,
    estimate_profit,
    analyze_listing
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Listing Analyzer",
    page_icon="📈",
    layout="wide"
)

# =====================================
# PAGE HEADER
# =====================================

st.title("📈 Listing Analyzer")

st.markdown("""
Analyze existing listings using:
- AI visual analysis
- SEO optimization
- pricing intelligence
- sell-through estimation
- reseller guidance
""")

# =====================================
# JSON INPUT
# =====================================

listing_json = st.text_area(
    "Paste Listing JSON From Extension",
    height=300
)

# =====================================
# MAIN APP
# =====================================

if listing_json:

    try:

        listing_data = json.loads(
            listing_json
        )

        # =================================
        # CURRENT LISTING
        # =================================

        st.subheader(
            "Current Listing"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"""
### Current Title

{listing_data['title']}
"""
            )

        with col2:

            st.markdown(
                f"""
### Current Price

{listing_data['price']}
"""
            )

        # =================================
        # LISTING IMAGES
        # =================================

        st.subheader(
            "Listing Photos"
        )

        cols = st.columns(5)

        for i, image_url in enumerate(
            listing_data["image_urls"]
        ):

            with cols[i % 5]:

                st.image(
                    image_url,
                    use_container_width=True
                )

        # =================================
        # BUY COST INPUT
        # =================================

        buy_cost = st.number_input(
            "What did you pay for this item?",
            min_value=0.0,
            value=5.0,
            step=1.0
        )

        # =================================
        # ANALYZE BUTTON
        # =================================

        if st.button(
            "Run AI Analysis"
        ):

            # =============================
            # AI ANALYSIS
            # =============================

            with st.spinner(
                "Analyzing listing..."
            ):

                ai_analysis = analyze_listing(
                    listing_data
                )

            st.subheader(
                "AI Analysis"
            )

            st.write(ai_analysis)

            # =============================
            # SEARCH QUERY
            # =============================

            search_query = listing_data[
                "title"
            ]

            st.subheader(
                "Market Analysis"
            )

            st.markdown(
                f"""
### Search Query Used

{search_query}
"""
            )

            # =============================
            # EBAY TOKEN
            # =============================

            token = get_ebay_token()

            # =============================
            # SOLD COMPS
            # =============================

            comps = search_sold_comps(
                search_query,
                token
            )

            prices = []

            st.markdown(
                "### Sold Comps"
            )

            for comp in comps:

                st.write(
                    f"${comp['price']} - "
                    f"{comp['title']}"
                )

                try:

                    prices.append(
                        float(
                            comp["price"]
                        )
                    )

                except:
                    pass

            # =============================
            # ACTIVE LISTINGS
            # =============================

            active_count = (
                search_active_listings(
                    search_query,
                    token
                )
            )

            sold_count = len(comps)

            sell_through = (
                calculate_sell_through(
                    sold_count,
                    active_count
                )
            )

            # =============================
            # PRICING
            # =============================

            pricing = calculate_pricing(
                prices
            )

            # =============================
            # RESELLER INTELLIGENCE
            # =============================

            if pricing:

                # =========================
                # PRICE RANGE
                # =========================

                low_price = round(
                    pricing["expected_sale"]
                    * 0.9,
                    2
                )

                high_price = round(
                    pricing[
                        "suggested_listing"
                    ] * 1.1,
                    2
                )

                # =========================
                # PROFIT
                # =========================

                expected_profit = (
                    estimate_profit(

                        pricing[
                            "expected_sale"
                        ],

                        buy_cost
                    )
                )

                # =========================
                # METRICS
                # =========================

                st.subheader(
                    "Reseller Intelligence"
                )

                metric1, metric2 = (
                    st.columns(2)
                )

                metric3, metric4 = (
                    st.columns(2)
                )

                with metric1:

                    st.metric(
                        "Suggested Listing Range",
                        f"${low_price} - ${high_price}"
                    )

                with metric2:

                    st.metric(
                        "Expected Sale Price",
                        f"${pricing['expected_sale']}"
                    )

                with metric3:

                    st.metric(
                        "Estimated Sell-Through",
                        f"{sell_through}%"
                    )

                with metric4:

                    st.metric(
                        "Estimated Net Profit",
                        f"${expected_profit}"
                    )

                # =========================
                # MARKET RECOMMENDATION
                # =========================

                if sell_through >= 70:

                    recommendation = (
                        "🔥 Strong Market"
                    )

                elif sell_through >= 40:

                    recommendation = (
                        "👍 Moderate Market"
                    )

                else:

                    recommendation = (
                        "⚠️ Slower Market"
                    )

                st.subheader(
                    "Market Recommendation"
                )

                st.info(
                    recommendation
                )

                # =========================
                # MARKET NOTES
                # =========================

                if sell_through >= 70:

                    st.success("""
High sell-through suggests:
- strong buyer demand
- lower inventory risk
- faster inventory turnover
""")

                elif sell_through >= 40:

                    st.warning("""
Moderate sell-through suggests:
- decent demand
- more competition
- pricing matters heavily
""")

                else:

                    st.error("""
Low sell-through suggests:
- slower-moving inventory
- possible saturation
- longer holding time
""")

    except Exception as e:

        st.error(str(e))