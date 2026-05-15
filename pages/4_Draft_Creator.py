import streamlit as st

from openai import OpenAI
from dotenv import load_dotenv
from helpers.attribute_helpers import (
    flatten_attributes
)

from helpers.title_generators import (
    generate_platform_title
)

from utils import (
    filter_relevant_comps
)

from utils import (
    get_ebay_token,
    search_sold_comps,
    calculate_pricing,
    filter_outliers,
    apply_condition_adjustment

)

from style_taxonomy import (
    STYLE_TAGS,
    SILHOUETTES,
    OCCASIONS
)

import os
import base64
import json
import re

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

    page_title="Draft Creator",

    page_icon="📝",

    layout="wide"
)

# =====================================
# HEADER
# =====================================

st.title(
    "📝 Multi-Platform Draft Creator"
)

st.markdown("""
Generate marketplace-specific
listing drafts optimized for:
- eBay
- Poshmark
- Depop
- Mercari
- Etsy
- Grailed
""")

# =====================================
# IMAGE UPLOAD
# =====================================

uploaded_files = st.file_uploader(

    "Upload Item Photos (Required)",

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

    material = st.multiselect(

        "Material",

        [
            "Unknown",
            "Linen",
            "Wool",
            "Cashmere",
            "Cotton",
            "Silk",
            "Denim",
            "Leather",
            "Alpaca",
            "Mohair",
            "Rayon",
            "Polyester",
            "Nylon",
            "Acrylic",
            "Spandex",
            "Viscose"
        ]
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

# =====================================
# NOTES
# =====================================

additional_notes = st.text_area(

    "Additional Notes",

    placeholder="""
Examples:
- Made in Italy
- Vintage tag
- Rare style
- Oversized fit
- Small flaw
- Heavyweight knit
"""
)

# =====================================
# MARKETPLACES
# =====================================

marketplaces = st.multiselect(

    "Select Marketplaces",

    [
        "eBay",
        "Poshmark",
        "Depop",
        "Mercari",
        "Etsy",
        "Grailed"
    ]
)

# =====================================
# GENERATE
# =====================================

if st.button(
    "Generate Draft Listings"
):

    if not uploaded_files:

        st.warning(
            "Please upload photos."
        )

    elif not marketplaces:

        st.warning(
            "Select marketplaces."
        )

    else:

        # =============================
        # IMAGE PREVIEW
        # =============================

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

        # =============================
        # MATERIAL INFERENCE
        # =============================

        inferred_material = ", ".join(
            material
        )

        if (
            not material
            or
            "Unknown" in material
        ):

            material_prompt = """
Analyze these clothing photos.

Infer the MOST LIKELY fabric composition.

Examples:
- wool blend
- linen cotton blend
- alpaca wool blend
- cotton
- rayon nylon blend

Return ONLY the likely material composition.

Do not explain.
"""

            material_content = [

                {
                    "type": "text",
                    "text": material_prompt
                }
            ]

            for file in uploaded_files:

                file.seek(0)

                image_bytes = file.read()

                base64_image = (
                    base64.b64encode(
                        image_bytes
                    ).decode("utf-8")
                )

                material_content.append(

                    {
                        "type": "image_url",

                        "image_url": {
                            "url": (
                                "data:image/jpeg;base64,"
                                f"{base64_image}"
                            )
                        }
                    }

                )

            response = (
                client.chat.completions.create(

                    model="gpt-4.1-mini",

                    messages=[
                        {
                            "role": "user",
                            "content": material_content
                        }
                    ],

                    max_tokens=75
                )
            )

            inferred_material = (
                response.choices[0]
                .message.content
                .strip()
            )

            st.info(
                f"Inferred Material: "
                f"{inferred_material}"
            )

        # =============================
        # SOLD COMPS
        # =============================

        search_query = " ".join([
            brand,
            color,
            item_type,
            size,
            inferred_material
        ]).strip()

        token = get_ebay_token()

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
            inferred_material,
            color
        )

        prices = []

        for comp in comps[:15]:

            try:

                prices.append(
                    float(
                        comp["price"]
                    )
                )

            except:
                pass

        prices = filter_outliers(
            prices
        )

        pricing = calculate_pricing(
            prices
        )

        # =============================
        # CONDITION ADJUSTMENT
        # =============================

        if pricing:

            adjusted_price = (
                apply_condition_adjustment(

                    pricing[
                        "expected_sale"
                    ],

                    condition
                )
            )

            low_price = round(
                adjusted_price * 0.9,
                2
            )

            high_price = round(
                adjusted_price * 1.1,
                2
            )

        else:

            low_price = 20
            high_price = 30

        # =============================
        # AI PROMPT
        # =============================

        content = []

        prompt = f"""
You are an expert fashion reseller.

Descriptions should be:

- detailed
- SEO-friendly
- natural sounding
- platform appropriate
- 2-4 paragraphs
- include styling language
- include garment details
- include silhouette
- include material feel
- include use cases
- include condition transparency
- avoid repetitive filler

PLATFORM DESCRIPTION STYLES:

eBay:
- highly searchable
- detailed garment specifics
- SEO-rich
- factual
- buyer confidence focused

Poshmark:
- lifestyle-oriented
- styling-focused
- fashion-forward
- conversational

Depop:
- aesthetic-heavy
- trend-aware
- Gen Z fashion language

Mercari:
- concise but informative
- clean formatting
- trust-building
Return ONLY valid JSON.

STYLE TAG OPTIONS:
{STYLE_TAGS}

SILHOUETTE OPTIONS:
{SILHOUETTES}

OCCASION OPTIONS:
{OCCASIONS}

ITEM DETAILS:

Brand: {brand}

Item Type: {item_type}

Material: {inferred_material}

Size: {size}

Color: {color}

Condition: {condition}

Additional Notes:
{additional_notes}

SELECTED MARKETPLACES:
{marketplaces}

REALISTIC PRICE RANGE:
${low_price}-${high_price}

IMPORTANT:
- ONLY generate requested marketplaces
- Use professional language
- Use realistic resale pricing
- Use style tags from taxonomy
- Avoid hallucinated aesthetics
- confidence scores MUST be integers from 1-100
- do not use words like High or Medium

JSON SCHEMA:

{{
  "ebay": {{}},
  "poshmark": {{}},
  "mercari": {{}},
  "depop": {{}},
  "etsy": {{}},
  "grailed": {{}}
}}

ONLY include marketplaces selected by the user.

Each marketplace object must contain:

{{
  "brand": "",
  "gender": "",
  "size": "",
  "color": "",
  "item_type": "",
  "material": "",

  "style_tags": [],
  "silhouettes": [],
  "hashtags": [],
  "keywords": [],

  "description": "",

  "garment_attributes": {{

    "neckline": "",
    "sleeve_length": "",
    "dress_length": "",
    "construction": "",
    "fit": "",
    "closure": "",
    "texture": ""

  }},

  "confidence": {{

  "aesthetic": 0,
  "material": 0,
  "silhouette": 0

  }}

}}

IF marketplace is ebay ALSO include:

{{
  "theme": [],
  "features": [],
  "pattern": "",
  "occasion": [],
  "performance_activity": []
}}
"""

        content.append(

            {
                "type": "text",
                "text": prompt
            }

        )

        # =============================
        # ADD IMAGES
        # =============================

        for file in uploaded_files:

            file.seek(0)

            image_bytes = file.read()

            base64_image = (
                base64.b64encode(
                    image_bytes
                ).decode("utf-8")
            )

            content.append(

                {
                    "type": "image_url",

                    "image_url": {
                        "url": (
                            "data:image/jpeg;base64,"
                            f"{base64_image}"
                        )
                    }
                }

            )

        # =============================
        # AI GENERATION
        # =============================

        with st.spinner(
            "Generating drafts..."
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

                    max_tokens=3000
                )
            )

        raw_output = (
            response.choices[0]
            .message.content
        )

        # =============================
        # CLEAN JSON OUTPUT
        # =============================

        cleaned_output = raw_output.strip()

        cleaned_output = re.sub(
            r"```json|```",
            "",
            cleaned_output
        )

        match = re.search(
            r"\{.*\}",
            cleaned_output,
            re.DOTALL
        )

        if match:

            cleaned_output = match.group(0)

        # =============================
        # PARSE JSON
        # =============================

        try:

            parsed = json.loads(
                cleaned_output
            )

        except Exception as e:

            st.error(
                f"JSON parse failed: {e}"
            )

            st.subheader(
                "Raw AI Output"
            )

            st.code(
                raw_output
            )

            st.stop()

        # =============================
        # SOLD COMPS
        # =============================

        st.subheader(
            "Sold Market Reference"
        )

        for comp in comps[:10]:
            score = comp.get(
                "relevance_score",
                0
            )

            if score >= 3:

                match_quality = "Excellent Match"

            elif score == 2:

                match_quality = "Good Match"

            elif score == 1:

                match_quality = "Partial Match"

            else:

                match_quality = "Weak Match"

            st.write(
                f"{match_quality} | "
                f"${comp['price']} - "
                f"{comp['title']}"
            )

        # =============================
        # MARKETPLACE TABS
        # =============================

        tabs = st.tabs(
            marketplaces
        )

        for i, marketplace in enumerate(
            marketplaces
        ):

            with tabs[i]:

                key = marketplace.lower()

                if key not in parsed:
                    continue

                data = parsed[key]

                data = flatten_attributes(data)

                platform_title = (
                    generate_platform_title(
                        marketplace,
                        data
                    )
                )
                # =====================================
                # PLATFORM TITLE
                # =====================================

                platform_title = (
                    generate_platform_title(
                        marketplace,
                        data
                    )
                )

                # =====================
                # TITLE
                # =====================

                st.subheader(
                    "Optimized Title"
                )

                st.code(

                    platform_title,

                    language="text"
                )

                # =====================
                # PRICE
                # =====================

                st.metric(

                    "Suggested Price Range",

                    f"${low_price} - ${high_price}"
                )

                # =====================
                # STYLE TAGS
                # =====================

                st.subheader(
                    "Style Tags"
                )

                for tag in data.get(
                    "style_tags",
                    []
                ):

                    st.markdown(
                        f"`{tag}`"
                    )

                # =====================
                # SILHOUETTES
                # =====================

                st.subheader(
                    "Silhouettes"
                )

                for silhouette in data.get(
                    "silhouettes",
                    []
                ):

                    st.markdown(
                        f"`{silhouette}`"
                    )

                # =====================
                # CONFIDENCE
                # =====================

                st.subheader(
                    "Confidence"
                )

                confidence = data.get(
                    "confidence",
                    {}
                )

                conf1, conf2, conf3 = st.columns(3)

                with conf1:

                    st.metric(

                        "Aesthetic Confidence",

                        f"{confidence.get('aesthetic', 0)}%"
                    )

                with conf2:

                    st.metric(

                        "Material Confidence",

                        f"{confidence.get('material', 0)}%"
                    )

                with conf3:

                    st.metric(

                        "Silhouette Confidence",

                        f"{confidence.get('silhouette', 0)}%"
                    )

                # =====================
                # DESCRIPTION
                # =====================

                st.subheader(
                    "Description"
                )

                st.text_area(

                    "",

                    value=data.get(

                        "description",
                        ""
                    ),

                    height=250,

                    key=f"desc_{marketplace}"
                )

                # =====================
                # HASHTAGS
                # =====================

                st.subheader(
                    "Hashtags"
                )

                hashtags = " ".join(

                    data.get(
                        "hashtags",
                        []
                    )
                )

                st.code(

                    hashtags,

                    language="text"
                )

                # =====================
                # KEYWORDS
                # =====================

                st.subheader(
                    "Keywords"
                )

                keywords = ", ".join(

                    data.get(
                        "keywords",
                        []
                    )
                )

                st.write(
                    keywords
                )

                # =====================
                # EBAY SPECIFICS
                # =====================

                if marketplace == "eBay":

                    st.subheader(
                        "eBay Item Specifics"
                    )

                    st.write(

                        "Theme:",

                        ", ".join(
                            data.get(
                                "theme",
                                []
                            )
                        )
                    )

                    st.write(

                        "Features:",

                        ", ".join(
                            data.get(
                                "features",
                                []
                            )
                        )
                    )

                    st.write(

                        "Pattern:",

                        data.get(
                            "pattern",
                            ""
                        )
                    )

                    st.write(

                        "Occasion:",

                        ", ".join(
                            data.get(
                                "occasion",
                                []
                            )
                        )
                    )

                    st.write(

                        "Performance/Activity:",

                        ", ".join(
                            data.get(
                                "performance_activity",
                                []
                            )
                        )
                    )
