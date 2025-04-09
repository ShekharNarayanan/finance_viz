import pandas as pd
from finance_viz.utils.transaction_data_utils import PROJECT_ROOT

data_path = PROJECT_ROOT / "input_data" / "transactions_categorized.xlsx"

def find_most_common_categories(dataframe: pd.DataFrame, upto: int = 10):
    """Find the most common categories in the dataframe.
    This function is used to create a dropdown for the dashboard.

    Args:
        dataframe (pd.DataFrame): Transaction data with categories.

    Returns:
        list: List of the most common categories.
    """
    # Find the most common categories in the dataframe
    return dataframe["Category"].value_counts().nlargest(upto).index.tolist()


def get_monthly_labels(dataframe: pd.DataFrame):
    """Get the distinct months from the dataframe to create a slider for the dashboard.

    Args:
        dataframe (pd.DataFrame): Transaction data with categories.

    Returns:
        marks: dict, mapping of month index to month string.
        distinct_months: list, sorted list of distinct months in the format "YYYY-MM".
    """
    distinct_months = sorted(dataframe["valuedate"].dt.strftime("%Y-%m").unique())
    # We'll create a dict for marks: {0: "2024-01", 1: "2024-02", etc.}
    marks = {i: month for i, month in enumerate(distinct_months)}
    return marks, distinct_months
