import streamlit as st

from openai import OpenAI
from dotenv import load_dotenv

from utils import (
    get_ebay_token,
    search_sold_comps,
    search_active_listings,
    calculate_pricing,
    estimate_profit,
    filter_relevant_comps,
)
from helpers.comp_helpers import (
    build_search_query
)
from helpers.sourcing_helpers import (

    determine_buy_decision,

    sell_through_label,

    saturation_label,
    comp_match_label,
    market_demand_label
)

import os
import base64

# =====================================
# LOAD ENV
# =====================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(

    page_title="Sourcing Assistant",

    page_icon="🛒",

    layout="wide"
)

# =====================================
# HEADER
# =====================================

st.title(
    "🛒 Sourcing Assistant"
)

st.markdown("""
Analyze sourcing opportunities using:
- photos
- brand
- material
- item type
- condition
- resale demand
- market velocity
- profit estimation
""")

# =====================================
# IMAGE UPLOAD
# =====================================

uploaded_files = st.file_uploader(

    "Upload Item Photos (Optional)",

    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ],

    accept_multiple_files=True
)

# =====================================
# ITEM DETAILS
# =====================================

st.subheader(
    "Item Details"
)

col1, col2 = st.columns(2)

with col1:

    brand = st.text_input(
        "Brand"
    )

    item_type = st.selectbox(

        "Item Type",

        [
            "Sweater",
            "Cardigan",
            "Shirt",
            "Blouse",
            "Dress",
            "Jeans",
            "Pants",
            "Jacket",
            "Coat",
            "Skirt",
            "Shoes",
            "Bag",
            "Other"
        ]
    )

    material = st.text_input(
        "Material"
    )

    size = st.text_input(
        "Size"
    )

with col2:

    color = st.text_input(
        "Color"
    )

    condition = st.selectbox(

        "Condition",

        [
            "New With Tags",
            "New Without Tags",
            "Excellent Used Condition",
            "Good Used Condition",
            "Fair Condition",
            "Flawed"
        ]
    )

    buy_cost = st.number_input(

        "Purchase Cost",

        min_value=0.0,

        value=5.0,

        step=1.0
    )

# =====================================
# ADDITIONAL NOTES
# =====================================

additional_notes = st.text_area(

    "Additional Notes",

    placeholder="""
Examples:
- Made in Italy
- Small flaw on sleeve
- Rare vintage tag
- Retired style
- Stretchy waist
- Heavyweight knit
- Oversized fit
- Missing button
"""
)

# =====================================
# ANALYZE BUTTON
# =====================================

if st.button(
    "Analyze Sourcing Opportunity"
):

    # =================================
    # OPTIONAL IMAGE DISPLAY
    # =================================

    if uploaded_files:

        st.subheader(
            "Uploaded Photos"
        )

        cols = st.columns(4)

        for i, file in enumerate(
            uploaded_files
        ):

            with cols[i % 4]:

                st.image(
                    file,
                    use_container_width=True
                )

    # =================================
    # AI PROMPT
    # =================================

    content = []

    prompt = f"""
You are an expert fashion reseller
and sourcing analyst.

Analyze this item carefully.

ITEM DETAILS:

Brand: {brand}

Item Type: {item_type}

Material: {material}

Size: {size}

Color: {color}

Condition: {condition}

Additional Notes:
{additional_notes}

Provide:

1. Estimated item identification

2. Style aesthetic

3. Trend relevance

4. Estimated resale demand:
- Low
- Moderate
- High

5. Why this item is valuable
(or not valuable)

6. Estimated resale price range

7. Sourcing recommendation:
- Strong pickup
- Moderate pickup
- Risky pickup
- Avoid

8. Key risks

9. Estimated market velocity:
- Very Hot
- Strong
- Moderate
- Slow
- Saturated

10. Overall sourcing intelligence summary

Focus heavily on:
- resale value
- buyer demand
- market saturation
- trend alignment
- profitability
"""

    content.append({

        "type": "text",

        "text": prompt
    })

    # =================================
    # ADD IMAGES IF PROVIDED
    # =================================

    if uploaded_files:

        for file in uploaded_files:

            image_bytes = file.read()

            base64_image = (
                base64.b64encode(
                    image_bytes
                ).decode("utf-8")
            )

            content.append({

                "type": "image_url",

                "image_url": {

                    "url":
                    (
                        "data:image/jpeg;base64,"
                        f"{base64_image}"
                    )
                }
            })

    # =================================
    # AI ANALYSIS
    # =================================

    with st.spinner(
        "Analyzing sourcing opportunity..."
    ):

        response = (
            client.chat.completions.create(

                model="gpt-4.1-mini",

                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],

                max_tokens=1800
            )
        )

    analysis = (
        response.choices[0]
        .message.content
    )

    st.subheader(
        "Sourcing Intelligence"
    )

    st.markdown(
        analysis
    )

    # =================================
    # SEARCH QUERY
    # =================================

    search_query = build_search_query(

        brand=brand,

        item_type=item_type,

        color=color,

        size=size,

        material=material,

        additional_notes=additional_notes
    ).strip()

    if not search_query:

        search_query = (
            "women fashion"
        )

    st.subheader(
        "Market Search"
    )

    st.write(
        f"Search Query: {search_query}"
    )

    # =================================
    # EBAY TOKEN
    # =================================

    token = get_ebay_token()

    # =================================
    # SOLD COMPS
    # =================================

    comps = search_sold_comps(
        search_query,
        token
    )

    comps = filter_relevant_comps(
        comps,
        brand,
        item_type,
        size,
        condition,
        material,
        color
    )
    market_analysis = (
        analyze_90_day_market(
            comps
        )
    )
    # =====================================
    # HIGH QUALITY COMPS ONLY
    # =====================================

    prices = []

    strong_matches = [

        comp for comp in comps

        if comp.get(
            "relevance_score",
            0
        ) >= 15
    ]

    # Fallback if too few
    if len(strong_matches) < 3:
        strong_matches = comps[:10]

    for comp in strong_matches:

        try:

            prices.append(

                float(
                    comp["price"]
                )
            )

        except:
            pass

    st.subheader(
        "Sold Comps"
    )

    for comp in comps:

        match_quality = comp_match_label(

            comp.get(
                "relevance_score",
                0
            )
        )

        st.write(
            f"{match_quality} | "
            f"${comp['price']} - "
            f"{comp['title']}"
        )

    # =====================================
    # ACTIVE LISTINGS
    # =====================================

    active_count = (
        search_active_listings(
            search_query,
            token
        )
    )

    sold_count = len(comps)

    # =================================
    # MARKET VELOCITY
    # =================================

    if sold_count >= 40 and active_count <= 80:

        velocity = "🔥 Very Hot"

    elif sold_count >= 25 and active_count <= 120:

        velocity = "👍 Strong"

    elif sold_count >= 15:

        velocity = "👌 Moderate"

    elif sold_count >= 8:

        velocity = "⚠️ Slow"

    else:

        velocity = "❌ Saturated / Weak"

    # =================================
    # PRICING
    # =================================

    pricing = calculate_pricing(
        prices
    )

    average_price = pricing.get(
        "average_price",
        0
    )

    demand_label = market_demand_label(

        sold_count,

        average_price
    )

    demand_label = market_demand_label(

        sold_count,

        average_price
    )
    # =================================
    # RESELLER METRICS
    # =================================

    if pricing:

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

        expected_profit = (
            estimate_profit(

                pricing[
                    "expected_sale"
                ],

                buy_cost
            )
        )

        st.subheader(
            "Reseller Metrics"
        )

        col1, col2 = st.columns(2)

        col3, col4 = st.columns(2)

        with col1:

            st.metric(
                "Estimated Price Range",
                f"${low_price} - ${high_price}"
            )

        with col2:

            st.metric(
                "Expected Sale Price",
                f"${pricing['expected_sale']}"
            )

        with col4:

            st.metric(
                "Estimated Profit",
                f"${expected_profit}"
            )

        # =================================
        # PICKUP SIGNAL
        # =================================

        if (
            velocity == "🔥 Very Hot"
            and
            expected_profit >= 30
        ):

            signal = (
                "🔥 Excellent Pickup"
            )

        elif (
            velocity == "👍 Strong"
            and
            expected_profit >= 15
        ):

            signal = (
                "👍 Strong Pickup"
            )

        elif (
            velocity == "👌 Moderate"
            and
            expected_profit >= 8
        ):

            signal = (
                "👌 Decent Pickup"
            )

        else:

            signal = (
                "⚠️ Riskier Pickup"
            )

        st.subheader(
            "Pickup Recommendation"
        )

        st.success(
            signal
        )
        # =====================================
        # SELL THROUGH ESTIMATE
        # =====================================

        if active_count > 0:

            if active_count > 0:

                sell_through = round(

                    (
                            sold_count
                            /
                            (
                                    sold_count
                                    +
                                    active_count
                            )
                    ) * 100,

                    1
                )

            else:

                sell_through = 0

        else:

            sell_through = 0
        # =====================================
        # QUICK OVERVIEW
        # =====================================

        sell_label = sell_through_label(
            sell_through
        )

        saturation = saturation_label(
            active_count
        )

        decision = determine_buy_decision(

            expected_profit,

            sell_through,

            saturation
        )

        st.subheader(
            "Quick Overview"
        )

        overview1, overview2, overview3 = st.columns(3)

        with overview1:

            st.metric(
                "Estimated Resale",
                f"${low_price}-${high_price}"
            )

        with overview2:

            st.metric(
                "Market Demand",
                demand_label
            )

        with overview3:

            st.metric(
                "Buy Decision",
                decision["decision"]
            )

        st.info(
            decision["reason"]
        )

        # =====================================
        # SOURCING INSIGHTS
        # =====================================

        st.subheader(
            "Sourcing Insights"
        )

        strengths = []

        risks = []

        # =============================
        # MATERIAL
        # =============================

        premium_materials = [

            "linen",

            "cashmere",

            "alpaca",

            "wool",

            "silk"
        ]

        if any(

                premium.lower() in material.lower()

                for premium in premium_materials
        ):
            strengths.append(
                "Premium natural fibers."
            )

        # =============================
        # SELL THROUGH
        # =============================

        if sell_through >= 65:

            strengths.append(
                "Strong resale demand."
            )

        elif sell_through < 40:

            risks.append(
                "Slow market movement."
            )

        # =============================
        # SATURATION
        # =============================

        if saturation == "High":
            risks.append(
                "Highly saturated category."
            )

        # =============================
        # DISPLAY
        # =============================

        if strengths:
            st.success(
                "\\n".join(
                    strengths
                )
            )

        if risks:
            st.warning(
                "\\n".join(
                    risks
                )
            )
        # =================================
        # SOURCING NOTES
        # =================================

        if velocity == "🔥 Very Hot":

            st.success("""
Strong buyer demand detected.

This item appears to have:
- healthy turnover
- strong buyer interest
- lower inventory risk
- excellent liquidity
""")

        elif velocity == "👍 Strong":

            st.warning("""
Healthy resale market detected.

This item likely has:
- good buyer demand
- reasonable turnover
- manageable competition
""")

        elif velocity == "👌 Moderate":

            st.warning("""
Moderate resale demand detected.

Condition and pricing
will matter heavily.
""")

        else:

            st.error("""
Weaker resale market detected.

Possible:
- oversaturation
- slower turnover
- weaker demand
- longer holding periods
""")

    else:

        st.warning(
            "Not enough valid sold comp prices to calculate reseller metrics."
        )
