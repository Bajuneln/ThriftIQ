# =====================================
# ATTRIBUTE FLATTENER
# =====================================


def flatten_attributes(data):

    garment = data.get(
        "garment_attributes",
        {}
    )

    data["neckline"] = garment.get(
        "neckline",
        ""
    )

    data["sleeve_length"] = garment.get(
        "sleeve_length",
        ""
    )

    data["dress_length"] = garment.get(
        "dress_length",
        ""
    )

    data["construction"] = garment.get(
        "construction",
        ""
    )

    data["fit"] = garment.get(
        "fit",
        ""
    )

    data["closure"] = garment.get(
        "closure",
        ""
    )

    data["texture"] = garment.get(
        "texture",
        ""
    )

    return data
