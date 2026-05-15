import json
import os

from collections import Counter
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

from utils import (
    get_ebay_token,
    search_sold_comps
)

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
# TRACKED TERMS
# =====================================

KEYWORDS = [

    # FABRICS
    "linen",
    "alpaca",
    "cashmere",
    "mohair",
    "wool",
    "silk",
    "cotton",
    "leather",

    # SILHOUETTES
    "oversized",
    "boxy",
    "wide",
    "cropped",
    "barrel",
    "relaxed",
    "slouchy",

    # AESTHETICS
    "boho",
    "minimalist",
    "western",
    "coastal",
    "artisan",
    "lagenlook",

    # STYLE TERMS
    "layering",
    "draped",
    "chunky",
    "textured"
]

# =====================================
# SEARCH CATEGORIES
# =====================================

SEARCHES = [

    "women sweater",

    "women cardigan",

    "women jacket",

    "women jeans",

    "women dress",

    "women coat",

    "women pants",

    "women blouse",

    "women linen",

    "women wool"
]

# =====================================
# TREND FILE
# =====================================

TREND_FILE = "trend_data.json"

# =====================================
# COLLECT SOLD TITLES
# =====================================

def collect_sold_titles():

    token = get_ebay_token()

    titles = []

    for search in SEARCHES:

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

                    titles.append(
                        title.lower()
                    )

        except Exception as e:

            print(
                "COLLECTION ERROR:",
                e
            )

    return titles

# =====================================
# COUNT KEYWORDS
# =====================================

def count_keywords(titles):

    counter = Counter()

    for title in titles:

        for keyword in KEYWORDS:

            if keyword in title:

                counter[keyword] += 1

    return dict(counter)

# =====================================
# SAVE SNAPSHOT
# =====================================

def save_trend_snapshot():

    titles = collect_sold_titles()

    keyword_counts = count_keywords(
        titles
    )

    snapshot = {

        "date":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "counts":
        keyword_counts
    }

    # LOAD EXISTING DATA
    if os.path.exists(
        TREND_FILE
    ):

        try:

            with open(
                TREND_FILE,
                "r"
            ) as f:

                data = json.load(f)

        except json.JSONDecodeError:

            data = []

    else:

        data = []

    if not isinstance(
        data,
        list
    ):

        data = []

    # APPEND SNAPSHOT
    data.append(snapshot)

    # SAVE
    with open(
        TREND_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    return snapshot

# =====================================
# COMPARE TRENDS
# =====================================

def compare_trends():

    if not os.path.exists(
        TREND_FILE
    ):

        return None

    try:

        with open(
            TREND_FILE,
            "r"
        ) as f:

            data = json.load(f)

    except json.JSONDecodeError:

        return None

    if not isinstance(
        data,
        list
    ):

        return None

    # NEED AT LEAST 2 SNAPSHOTS
    if len(data) < 2:

        return None

    latest = data[-1]["counts"]

    previous = data[-2]["counts"]

    changes = {}

    for keyword in KEYWORDS:

        old = previous.get(
            keyword,
            0
        )

        new = latest.get(
            keyword,
            0
        )

        difference = new - old

        changes[keyword] = difference

    return changes

# =====================================
# TREND SUMMARY
# =====================================

def generate_trend_summary():

    changes = compare_trends()

    if not changes:

        return (
            "Not enough historical "
            "trend data yet."
        )

    rising = []

    declining = []

    for keyword, change in changes.items():

        if change > 0:

            rising.append(
                (keyword, change)
            )

        elif change < 0:

            declining.append(
                (keyword, change)
            )

    rising.sort(
        key=lambda x: x[1],
        reverse=True
    )

    declining.sort(
        key=lambda x: x[1]
    )

    report = []

    report.append(
        "📈 Rising Trends:\n"
    )

    for keyword, change in rising[:10]:

        report.append(
            f"↑ {keyword}: +{change}"
        )

    report.append(
        "\n📉 Declining Trends:\n"
    )

    for keyword, change in declining[:10]:

        report.append(
            f"↓ {keyword}: {change}"
        )

    return "\n".join(report)

# =====================================
# DISCOVER NEW TERMS
# =====================================

def discover_new_terms(titles):

    sample_titles = titles[:200]

    prompt = f"""
You are an expert fashion resale
market analyst.

Analyze these sold eBay listing
titles.

Identify:

1. Trending aesthetics
2. Rising fabrics
3. Strong silhouettes
4. Emerging style terms
5. Oversaturated trends
6. Rising brands
7. Fastest-moving categories
8. Seasonal flip opportunities
9. Hot search keywords
10. Categories to avoid picking up

Return results in clean markdown.

Format EXACTLY like this:

## Trending Aesthetics
- item
- item

## Rising Fabrics
- item
- item

## Strong Silhouettes
- item
- item

## Emerging Style Terms
- item
- item

## Rising Brands
- item
- item

## Fastest Sell-Through Categories
- item
- item

## Avoid Picking Up
- item
- item

## Seasonal Flip Alerts
- item
- item

## Hot Search Terms
- item
- item

## Oversaturated Trends
- item
- item

Focus ONLY on:
- resale demand
- buyer behavior
- sell-through potential
- market momentum
- sourcing intelligence

DO NOT give generic fashion advice.

ONLY identify actual resale
market signals.

LISTINGS:

{sample_titles}
"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_tokens=1400
    )

    return response.choices[
        0
    ].message.content
# =====================================
# AI TREND INTERPRETATION
# =====================================

def interpret_trend_changes():

    changes = compare_trends()

    if not changes:

        return (
            "Not enough trend "
            "history yet."
        )

    prompt = f"""
You are an expert fashion resale
market analyst.

Interpret these resale market
trend changes.

Explain:

1. Buyer behavior
2. Resale demand shifts
3. Strong sourcing opportunities
4. Oversaturated categories
5. Seasonal movement
6. Important resale signals

Focus ONLY on:
- resale market intelligence
- sourcing strategy
- sell-through implications
- buyer demand patterns

DO NOT simply repeat numbers.

Explain WHAT the changes mean.

TREND DATA:

{changes}
"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_tokens=1000
    )

    return response.choices[
        0
    ].message.content
