from PIL.ImageEnhance import Color
from openai import OpenAI
from dotenv import load_dotenv

import os
import requests
import base64
import statistics
def filter_outliers(prices):

    if len(prices) < 5:
        return prices

    median = statistics.median(prices)

    filtered = [
        p for p in prices
        if (
            p >= median * 0.65
            and
            p <= median * 1.5
        )
    ]

    return filtered

from PIL import Image
from io import BytesIO

# =====================================
# LOAD ENV
# =====================================

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

EBAY_CLIENT_ID = os.getenv(
    "EBAY_CLIENT_ID"
)

EBAY_CLIENT_SECRET = os.getenv(
    "EBAY_CLIENT_SECRET"
)

# =====================================
# OPENAI CLIENT
# =====================================

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# =====================================
# GET EBAY TOKEN
# =====================================

def get_ebay_token():

    url = (
        "https://api.ebay.com/"
        "identity/v1/oauth2/token"
    )

    headers = {
        "Content-Type":
        "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope":
        "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=(
            EBAY_CLIENT_ID,
            EBAY_CLIENT_SECRET
        )
    )

    response.raise_for_status()

    return response.json()["access_token"]

# =====================================
# SEARCH SOLD COMPS
# =====================================

def search_sold_comps(query, token):

    url = (
        "https://api.ebay.com/"
        "buy/browse/v1/item_summary/search"
    )

    headers = {
        "Authorization":
        f"Bearer {token}"
    }

    params = {
        "q": query,
        "filter": "soldItemsOnly:true",
        "limit": 20
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get(
        "itemSummaries",
        []
    ):

        try:

            results.append({

                "title":
                item.get("title"),

                "price":
                item.get(
                    "price",
                    {}
                ).get("value")

            })

        except:
            pass

    return results

# =====================================
# SEARCH ACTIVE LISTINGS
# =====================================

def calculate_sell_through(
    sold_count,
    active_count
):

    if active_count == 0:
        return 100

    return round(
        (
            sold_count
            /
            active_count
        ) * 100,
        1
    )

# =====================================
# CALCULATE PRICING
# =====================================

def calculate_pricing(prices):

    if not prices:

        return None

    median_price = statistics.median(
        prices
    )

    suggested_listing = round(
        median_price * 1.2,
        2
    )

    expected_sale = round(
        median_price,
        2
    )

    return {

        "median_price":
        median_price,

        "suggested_listing":
        suggested_listing,

        "expected_sale":
        expected_sale
    }

# =====================================
# ESTIMATE NET PROFIT
# =====================================

def estimate_profit(
    expected_sale_price,
    buy_cost,
    shipping_cost=8,
    fee_percent=0.15
):

    fees = (
        expected_sale_price
        * fee_percent
    )

    profit = (
        expected_sale_price
        - fees
        - shipping_cost
        - buy_cost
    )

    return round(profit, 2)

# =====================================
# ENCODE IMAGE
# =====================================

def encode_image_from_url(
    image_url
):

    response = requests.get(
        image_url
    )

    image = Image.open(
        BytesIO(response.content)
    )

    if image.mode != "RGB":

        image = image.convert("RGB")

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

# =====================================
# ANALYZE LISTING
# =====================================

def analyze_listing(
    listing_data
):

    content = [

        {
            "type": "text",

            "text": f"""
You are an expert fashion reseller
and resale analyst.

Analyze this item carefully.

CURRENT TITLE:
{listing_data['title']}

CURRENT PRICE:
{listing_data['price']}

Provide:

1. Optimized eBay title
under 80 characters

2. 10 style tags

3. SEO keywords

4. Fit/silhouette analysis

5. Style aesthetic

6. Suggested sold search query

7. Estimated sell-through:
Low / Moderate / High

8. Why this item is valuable

9. Estimated buyer demographic

10. Short reseller recommendation

11. Listing quality score out of 100

Evaluate:
- title SEO
- keyword strength
- listing clarity
- resale optimization

12. Photo quality score out of 100

Evaluate:
- lighting
- wrinkles
- framing
- completeness
- professionalism

13. Specific improvement advice for:
- listing quality
- photo quality

Use real reseller language.

Focus heavily on:
- aesthetics
- silhouette
- trend relevance
- resale desirability
- searchable keywords
"""
        }
    ]

    # =================================
    # ADD IMAGES
    # =================================

    for image_url in listing_data[
        "image_urls"
    ]:

        try:

            image_base64 = (
                encode_image_from_url(
                    image_url
                )
            )

            content.append({

                "type": "image_url",

                "image_url": {
                    "url":
                    (
                        "data:image/jpeg;base64,"
                        f"{image_base64}"
                    )
                }
            })

        except Exception as e:

            print("IMAGE ERROR:", e)

    # =================================
    # OPENAI REQUEST
    # =================================

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": content
            }
        ],

        max_tokens=1400
    )

    return response.choices[
        0
    ].message.content

# =====================================
# EXTRACT SEARCH QUERY
# =====================================

def extract_search_query(
    ai_response
):

    lines = ai_response.split(
        "\n"
    )

    for line in lines:

        if (
            "search query"
            in line.lower()
            or
            "sold search query"
            in line.lower()
        ):

            return (
                line
                .split(":")[-1]
                .strip()
            )

    return None
# =====================================
# GENERATE TREND REPORT
# =====================================

def generate_trend_report():

    token = get_ebay_token()

    broad_searches = [

        "women sweater",

        "women cardigan",

        "women jeans",

        "women dress",

        "women jacket",

        "women coat",

        "women linen",

        "women wool",

        "women blouse",

        "women pants"
    ]

    sold_titles = []

    for search in broad_searches:

        try:

            comps = search_sold_comps(
                search,
                token
            )

            for comp in comps:

                title = comp.get(
                    "title",
                    ""
                )

                if title:

                    sold_titles.append(
                        title
                    )

        except Exception as e:

            print(
                "TREND ERROR:",
                e
            )

    # REMOVE DUPLICATES
    sold_titles = list(
        set(sold_titles)
    )

    # LIMIT SIZE
    sold_titles = sold_titles[:200]

    # =================================
    # AI TREND ANALYSIS
    # =================================

    prompt = f"""
You are an expert fashion resale
market analyst.

Analyze these recently sold eBay
fashion listings.

Identify:

1. Trending aesthetics

2. Rising silhouettes

3. Strong fabrics/materials

4. Strong resale categories

5. Oversaturated categories

6. Important recurring keywords

7. Emerging resale trends

8. Buyer demand patterns

Focus ONLY on:
- resale demand
- sell-through potential
- buyer behavior
- resale market intelligence

DO NOT give generic fashion trends.

Find actual resale market signals.

SOLD LISTINGS:

{sold_titles}
"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_tokens=1200
    )

    return response.choices[
        0
    ].message.content
def apply_condition_adjustment(
    price,
    condition
):

    adjustments = {
        "New With Tags": 1.10,
        "New Without Tags": 1.05,
        "Excellent Used Condition": 1.0,
        "Good Used Condition": 0.90,
        "Fair Condition": 0.75,
        "Flawed": 0.60
    }

    multiplier = adjustments.get(
        condition,
        1.0
    )

    return round(
        price * multiplier,
        2
    )
# =====================================
# SMART COMP FILTERING
# =====================================


def filter_relevant_comps(
    comps,
    brand,
    item_type,
    size,
    condition,
    material,
    color

):

    filtered = []
    brand_term = brand.strip().lower()
    item_type_term = item_type.strip().lower()

    for comp in comps:

        title = comp.get(
            "title",
            ""
        ).lower()

        # =============================
        # BRAND MUST MATCH
        # =============================

        if (
            brand_term
            and
            brand_term not in title
        ):
            continue

        # =============================
        # ITEM TYPE MUST MATCH
        # =============================

        if (
            item_type_term
            and
            item_type_term != "other"
            and
            item_type_term not in title
        ):
            continue

        # =============================
        # SIZE BOOSTING
        # =============================

        size_match = False

        if size:

            size_variations = [
                size.lower(),
                f"size {size.lower()}",
                f"sz {size.lower()}"
            ]

            for variation in size_variations:

                if variation in title:
                    size_match = True
                    break

        # =============================
        # CONDITION MATCHING
        # =============================

        condition_score = 0

        condition_map = {

            "New With Tags": [
                "new with tags",
                "nwt"
            ],

            "New Without Tags": [
                "new without tags",
                "nwot"
            ],

            "Excellent Used Condition": [
                "excellent",
                "euc"
            ],

            "Good Used Condition": [
                "good"
            ],

            "Flawed": [
                "flawed",
                "distressed",
                "stain",
                "hole"
            ]
        }

        keywords = condition_map.get(
            condition,
            []
        )

        for keyword in keywords:

            if keyword in title:
                condition_score += 1

        # =============================
        # RELEVANCE SCORING
        # =============================

        relevance_score = 0

        # =============================
        # WEIGHTED MATCHING
        # =============================

        # BRAND
        if (
            brand_term
            and
            brand_term in title
        ):
            relevance_score += 10

        # ITEM TYPE
        if (
            item_type_term
            and
            item_type_term != "other"
            and
            item_type_term in title
        ):
            relevance_score += 8

        # SIZE
        if size_match:
            relevance_score += 5

        # CONDITION
        relevance_score += condition_score * 3

        # COLOR
        if (
            color
            and
            color.lower() in title
        ):
            relevance_score += 2

        # MATERIAL
        if (
                material
                and
                material.lower() in title
        ):
            relevance_score += 4

        relevance_score += condition_score

        comp[
            "relevance_score"
        ] = relevance_score

        filtered.append(comp)

    # =============================
    # SORT BEST MATCHES FIRST
    # =============================

    filtered.sort(
        key=lambda x: x.get(
            "relevance_score",
            0
        ),
        reverse=True
    )

    return filtered
# =====================================
# ACTIVE LISTING SEARCH
# =====================================

def search_active_listings(
    query,
    token
):

    url = (
        "https://api.ebay.com/"
        "buy/browse/v1/item_summary/search"
    )

    headers = {
        "Authorization":
        f"Bearer {token}"
    }

    params = {
        "q": query,
        "limit": 50
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "total",
        0
    )
