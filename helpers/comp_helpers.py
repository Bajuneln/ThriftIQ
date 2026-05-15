# =====================================
# SMART QUERY BUILDER
# =====================================

def build_search_query(

    brand="",

    item_type="",

    color="",

    size="",

    material="",

    neckline="",

    sleeve_length="",

    dress_length="",

    fit="",

    additional_notes=""
):

    query_parts = []

    # =============================
    # REQUIRED CORE FIELDS
    # =============================

    if brand:
        query_parts.append(
            brand
        )

    if color:
        query_parts.append(
            color
        )

    if material:
        query_parts.append(
            material
        )

    if fit:
        query_parts.append(
            fit
        )

    if neckline:
        query_parts.append(
            neckline
        )

    if sleeve_length:
        query_parts.append(
            sleeve_length
        )

    if dress_length:
        query_parts.append(
            dress_length
        )

    if item_type:
        query_parts.append(
            item_type
        )

    if size:
        query_parts.append(
            size
        )

    # =============================
    # ADDITIONAL NOTES
    # =============================

    important_keywords = [

        "oversized",

        "italy",

        "vintage",

        "maxi",

        "midi",

        "chunky",

        "ribbed",

        "open front",

        "button front"
    ]

    notes_lower = additional_notes.lower()

    for keyword in important_keywords:

        if keyword in notes_lower:

            query_parts.append(
                keyword
            )

    # =============================
    # CLEAN QUERY
    # =============================

    cleaned_parts = [

        str(part).strip()

        for part in query_parts

        if str(part).strip()
    ]

    return " ".join(
        cleaned_parts
    )