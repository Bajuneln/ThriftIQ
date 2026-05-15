from datetime import datetime
from statistics import median


# =====================================
# 90 DAY MARKET ANALYSIS
# =====================================

def analyze_90_day_market(comps):

    recent_prices = []

    older_prices = []

    now = datetime.utcnow()

    for comp in comps:

        try:

            sold_date = datetime.fromisoformat(

                comp[
                    "sold_date"
                ].replace(
                    "Z",
                    "+00:00"
                )
            )

            days_old = (
                now - sold_date
            ).days

            price = float(
                comp["price"]
            )

            # =========================
            # RECENT 30 DAYS
            # =========================

            if days_old <= 30:

                recent_prices.append(
                    price
                )

            # =========================
            # OLDER 31-90 DAYS
            # =========================

            elif days_old <= 90:

                older_prices.append(
                    price
                )

        except:
            pass

    # =============================
    # MEDIANS
    # =============================

    recent_median = (
        median(recent_prices)
        if recent_prices
        else 0
    )

    older_median = (
        median(older_prices)
        if older_prices
        else 0
    )

    # =============================
    # TREND DIRECTION
    # =============================

    if (
        recent_median >
        older_median * 1.1
    ):

        trend = "Rising"

    elif (
        recent_median <
        older_median * 0.9
    ):

        trend = "Declining"

    else:

        trend = "Stable"

    return {

        "trend": trend,

        "recent_median": round(
            recent_median,
            2
        ),

        "older_median": round(
            older_median,
            2
        ),

        "recent_sales": len(
            recent_prices
        ),

        "older_sales": len(
            older_prices
        )
    }