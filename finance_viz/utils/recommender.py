# finance_viz/utils/recommender.py
import pandas as pd
from typing import List, Dict


def _monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to year-month × category so stats are easy."""
    df = df.copy()
    df["month"] = df["valuedate"].dt.to_period("M").dt.to_timestamp()
    return (
        df.groupby(["month", "Category"])["amount"]
        .sum()
        .unstack(fill_value=0)  # rows=month, cols=category
        .sort_index()
    )


def generate_insights(
    df: pd.DataFrame, lookback_months: int | None = None, top_k: int = 5
) -> List[Dict]:
    """
    Very-first MVP: flag overspend in the most-recent month.
    Returns [{title, detail, severity, id}, …] sorted by severity desc.
    """
    monthlies = _monthly_totals(df)

    # ------ choose window we analyse ------
    if lookback_months:
        monthlies = monthlies.tail(lookback_months)

    current = monthlies.iloc[-1]  # last month
    baseline = monthlies.iloc[:-1].mean()  # mean of earlier months
    std = monthlies.iloc[:-1].std().fillna(0)

    over = current > baseline + 1.5 * std  # boolean Series
    rows = []
    for cat, flag in over.items():
        if flag and baseline[cat] > 0:
            delta = current[cat] - baseline[cat]
            pct = delta / baseline[cat] * 100
            rows.append(
                {
                    "id": f"{cat}_{current.name.strftime('%Y-%m')}",
                    "title": f"{cat} ↑ {pct:0.0f}% vs usual",
                    "detail": (
                        f"You spent €{current[cat]:,.0f} in {cat} this month; "
                        f"typical is €{baseline[cat]:,.0f}. "
                        "Consider setting a tighter budget."
                    ),
                    "severity": pct,
                }
            )

    # rank & limit
    rows.sort(key=lambda x: x["severity"], reverse=True)
    return rows[:top_k]
