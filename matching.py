import re

# -----------------------------------
# NORMALIZATION HELPERS
# -----------------------------------

CONDITION_MAP = {
    "new with tags": "new",
    "nwt": "new",
    "brand new": "new",

    "new without tags": "like_new",
    "nwot": "like_new",

    "excellent used condition": "used_good",
    "excellent condition": "used_good",
    "pre-owned": "used_good",
    "preowned": "used_good",
    "used": "used_good",

    "fair": "used_fair",
    "poor": "used_poor"
}


STOPWORDS = {
    "womens",
    "women",
    "mens",
    "men",
    "soft",
    "cozy",
    "boho",
    "minimalist",
    "quiet",
    "luxury",
    "casual",
    "cute",
    "classic",
    "style",
    "oversized"
}


MATERIALS = [
    "wool",
    "cotton",
    "linen",
    "silk",
    "cashmere",
    "alpaca",
    "nylon",
    "polyester",
    "rayon",
    "spandex"
]


ITEM_TYPES = [
    "shirt",
    "sweater",
    "cardigan",
    "dress",
    "blazer",
    "jacket",
    "coat",
    "jeans",
    "pants",
    "skirt"
]


COLORS = [
    "black",
    "white",
    "blue",
    "pink",
    "red",
    "green",
    "gray",
    "grey",
    "cream",
    "brown",
    "beige"
]


# -----------------------------------
# CLEAN TEXT
# -----------------------------------

def clean_text(text):
    text = text.lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    words = text.split()

    words = [w for w in words if w not in STOPWORDS]

    return " ".join(words)


# -----------------------------------
# EXTRACT SIZE
# -----------------------------------

def extract_size(title):
    title = title.upper()

    sizes = [
        "XXS", "XS", "S", "M", "L",
        "XL", "XXL", "2XL", "3XL"
    ]

    for size in sizes:
        pattern = rf"\b{size}\b"

        if re.search(pattern, title):
            return size

    return None


# -----------------------------------
# EXTRACT CONDITION
# -----------------------------------

def extract_condition(text):
    text = text.lower()

    for key, value in CONDITION_MAP.items():
        if key in text:
            return value

    return "unknown"


# -----------------------------------
# EXTRACT MATERIALS
# -----------------------------------

def extract_materials(text):
    text = text.lower()

    found = []

    for material in MATERIALS:
        if material in text:
            found.append(material)

    return found


# -----------------------------------
# EXTRACT ITEM TYPE
# -----------------------------------

def extract_item_type(text):
    text = text.lower()

    for item_type in ITEM_TYPES:
        if item_type in text:
            return item_type

    return None


# -----------------------------------
# EXTRACT COLOR
# -----------------------------------

def extract_color(text):
    text = text.lower()

    for color in COLORS:
        if color in text:
            return color

    return None


# -----------------------------------
# BUILD STRUCTURED ITEM
# -----------------------------------

def build_item_data(title, brand="", description=""):
    full_text = f"{title} {description}"

    return {
        "brand": brand.lower().strip(),
        "title": title,
        "clean_title": clean_text(title),
        "size": extract_size(full_text),
        "condition": extract_condition(full_text),
        "materials": extract_materials(full_text),
        "item_type": extract_item_type(full_text),
        "color": extract_color(full_text)
    }


# -----------------------------------
# SIZE COMPARISON
# -----------------------------------

def sizes_are_close(size1, size2):
    order = ["XXS", "XS", "S", "M", "L", "XL", "XXL"]

    if size1 not in order or size2 not in order:
        return False

    return abs(order.index(size1) - order.index(size2)) == 1


# -----------------------------------
# MATCH SCORING
# -----------------------------------

def calculate_match_score(user_item, listing):
    score = 0

    # --------------------------
    # BRAND
    # --------------------------

    if user_item["brand"] == listing["brand"]:
        score += 40

    # --------------------------
    # ITEM TYPE
    # --------------------------

    if user_item["item_type"] == listing["item_type"]:
        score += 25

    # --------------------------
    # SIZE
    # --------------------------

    if user_item["size"] == listing["size"]:
        score += 15

    elif sizes_are_close(
        user_item["size"],
        listing["size"]
    ):
        score += 5

    # --------------------------
    # CONDITION
    # --------------------------

    if user_item["condition"] == listing["condition"]:
        score += 10

    # --------------------------
    # MATERIALS
    # --------------------------

    shared_materials = set(
        user_item["materials"]
    ).intersection(
        set(listing["materials"])
    )

    score += len(shared_materials) * 5

    # --------------------------
    # COLOR
    # --------------------------

    if user_item["color"] == listing["color"]:
        score += 5

    return score


# -----------------------------------
# FILTER LISTINGS
# -----------------------------------

def filter_comparables(user_item, listings):

    scored = []

    for listing in listings:

        score = calculate_match_score(
            user_item,
            listing
        )

        listing["match_score"] = score

        if score >= 60:
            scored.append(listing)

    scored.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return scored


# -----------------------------------
# EXAMPLE USAGE
# -----------------------------------

if __name__ == "__main__":
    my_item = build_item_data(
        title="Rixo Aara Wool Blend Cardigan Size L NWT",
        brand="Rixo"
    )

    marketplace_listings = [
        build_item_data(
            title="Rixo Wool Cardigan Size L NWT",
            brand="Rixo"
        ),

        build_item_data(
            title="Rixo Wool Cardigan Size M Pre-Owned",
            brand="Rixo"
        ),

        build_item_data(
            title="Madewell Cotton Sweater Size L",
            brand="Madewell"
        )
    ]

    results = filter_comparables(
        my_item,
        marketplace_listings
    )

    for item in results:
        print(item["title"])
        print("Match Score:", item["match_score"])
        print("-" * 40)
