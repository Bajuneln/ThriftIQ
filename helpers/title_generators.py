# =====================================
# EBAY TITLE
# =====================================


def generate_ebay_title(data):

    parts = [

        data.get("brand", ""),

        data.get(
            "gender",
            "Womens"
        ),

        data.get("size", ""),

        data.get("color", ""),

        data.get(
            "construction",
            ""
        ),

        data.get(
            "dress_length",
            ""
        ),

        data.get(
            "item_type",
            ""
        ),

        data.get(
            "neckline",
            ""
        ),

        data.get(
            "sleeve_length",
            ""
        ),

        data.get(
            "material",
            ""
        )
    ]

    title = " ".join(

        [
            str(p).strip()
            for p in parts
            if p
        ]
    )

    return title[:80]


# =====================================
# POSHMARK TITLE
# =====================================


def generate_poshmark_title(data):

    style_tags = " ".join(
        data.get(
            "style_tags",
            []
        )[:2]
    )

    parts = [

        data.get("brand", ""),

        data.get(
            "item_type",
            ""
        ),

        style_tags,

        data.get(
            "material",
            ""
        )
    ]

    title = " ".join(

        [
            str(p).strip()
            for p in parts
            if p
        ]
    )

    return title[:60]


# =====================================
# DEPOP TITLE
# =====================================


def generate_depop_title(data):

    aesthetics = " ".join(
        data.get(
            "style_tags",
            []
        )[:3]
    )

    parts = [

        aesthetics,

        data.get("color", ""),

        data.get(
            "item_type",
            ""
        ),

        data.get("fit", "")
    ]

    title = " ".join(

        [
            str(p).strip()
            for p in parts
            if p
        ]
    )

    return title[:70]


# =====================================
# MERCARI TITLE
# =====================================


def generate_mercari_title(data):

    parts = [

        data.get("brand", ""),

        data.get(
            "item_type",
            ""
        ),

        data.get("color", ""),

        data.get("size", "")
    ]

    title = " ".join(

        [
            str(p).strip()
            for p in parts
            if p
        ]
    )

    return title[:40]


# =====================================
# ETSY TITLE
# =====================================


def generate_etsy_title(data):

    style_tags = " ".join(
        data.get(
            "style_tags",
            []
        )[:2]
    )

    parts = [

        data.get("brand", ""),

        data.get(
            "material",
            ""
        ),

        data.get(
            "item_type",
            ""
        ),

        style_tags
    ]

    title = " ".join(

        [
            str(p).strip()
            for p in parts
            if p
        ]
    )

    return title[:140]


# =====================================
# GRAILED TITLE
# =====================================


def generate_grailed_title(data):

    parts = [

        data.get("brand", ""),

        data.get(
            "construction",
            ""
        ),

        data.get(
            "item_type",
            ""
        ),

        data.get(
            "material",
            ""
        )
    ]

    title = " ".join(

        [
            str(p).strip()
            for p in parts
            if p
        ]
    )

    return title[:70]


# =====================================
# MASTER ROUTER
# =====================================


def generate_platform_title(
    marketplace,
    data
):

    if marketplace == "eBay":

        return generate_ebay_title(
            data
        )

    elif marketplace == "Poshmark":

        return generate_poshmark_title(
            data
        )

    elif marketplace == "Depop":

        return generate_depop_title(
            data
        )

    elif marketplace == "Mercari":

        return generate_mercari_title(
            data
        )

    elif marketplace == "Etsy":

        return generate_etsy_title(
            data
        )

    elif marketplace == "Grailed":

        return generate_grailed_title(
            data
        )

    return ""
