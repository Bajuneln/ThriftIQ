# =====================================
# BUY DECISION ENGINE
# =====================================

def determine_buy_decision(

    estimated_profit,

    sell_through,

    saturation_level
):

    # =============================
    # BUY
    # =============================

    if (
        estimated_profit >= 40
        and
        sell_through >= 70
        and
        saturation_level != "High"
    ):

        return {
            "decision": "BUY",
            "reason":
                (
                    "Strong resale margin "
                    "with healthy demand."
                )
        }

    # =============================
    # MAYBE
    # =============================

    elif (
        estimated_profit >= 20
        and
        sell_through >= 45
    ):

        return {
            "decision": "MAYBE",
            "reason":
                (
                    "Moderate resale potential "
                    "with some market risk."
                )
        }

    # =============================
    # PASS
    # =============================

    return {
        "decision": "PASS",
        "reason":
            (
                "Weak resale demand or "
                "insufficient profit margin."
            )
    }


# =====================================
# SELL THROUGH LABEL
# =====================================

def sell_through_label(rate):

    if rate >= 80:
        return "Very High"

    elif rate >= 65:
        return "High"

    elif rate >= 45:
        return "Moderate"

    elif rate >= 25:
        return "Low"

    return "Very Low"


# =====================================
# MARKET SATURATION LABEL
# =====================================

def saturation_label(active_count):

    if active_count >= 500:
        return "High"

    elif active_count >= 200:
        return "Moderate"

    return "Low"


# =====================================
# MATCH QUALITY LABEL
# =====================================

def comp_match_label(score):

    if score >= 3:
        return "Excellent Match"

    elif score == 2:
        return "Good Match"

    elif score == 1:
        return "Partial Match"

    return "Weak Match"
# =====================================
# MARKET DEMAND LABEL
# =====================================

def market_demand_label(

    sold_count,

    average_price
):

    score = 0

    # =============================
    # SOLD VOLUME
    # =============================

    if sold_count >= 30:
        score += 2

    elif sold_count >= 10:
        score += 1

    # =============================
    # PRICE STRENGTH
    # =============================

    if average_price >= 75:
        score += 2

    elif average_price >= 40:
        score += 1

    # =============================
    # LABELS
    # =============================

    if score >= 4:
        return "Very Strong"

    elif score >= 3:
        return "Strong"

    elif score >= 2:
        return "Moderate"

    elif score >= 1:
        return "Low"

    return "Weak"
