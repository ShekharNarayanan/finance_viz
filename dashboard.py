import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from finance_viz.utils.transaction_data_utils import PROJECT_ROOT
from finance_viz.utils.dashboard_utils import get_monthly_labels, find_most_common_categories

data_path = PROJECT_ROOT / "input_data" / "transactions_categorized.xlsx"

# 1. Load your data
df = pd.read_excel(data_path)
df["valuedate"] = pd.to_datetime(df["valuedate"])  # Convert valuedate to datetime

# get data for date slider
marks, month_list = get_monthly_labels(df)

# get the most common categories for the dropdown
common_categories = find_most_common_categories(df)

color_discrete_map = {"income": "green", "expense": "red"}

# 2. Create a Dash app
app = Dash(__name__)

# 3. Define layout with two charts + a simple filter
app.layout = html.Div(
    [
        dcc.Dropdown(
            id="category-filter",
            options=[{"label": cat, "value": cat} for cat in df["Category"].unique()],
            multi=True,
            placeholder="Select one or more categories",
        ),
        dcc.RangeSlider(
            id="date-slider",
            min=0,
            max=len(month_list) - 1,
            marks=get_monthly_labels(df)[0],
            value=[0, len(month_list) - 1],  # [start_index, end_index]
        ),
        dcc.Graph(id="bar-chart"),
        dcc.Graph(id="time-series-chart"),
        dcc.Graph(id="pie-chart"),
    ]
)


# 4. Single callback: filter the data and return 3 figures
@app.callback(
    [
        Output("bar-chart", "figure"),
        Output("time-series-chart", "figure"),
        Output("pie-chart", "figure"),
    ],
    [Input("category-filter", "value"), Input("date-slider", "value")],
)
# decorator function for the callback - this is how Dash knows to call this function when the input changes
def update_charts(selected_categories, dateslider):
    # If none selected, use common_categories
    if not selected_categories:
        selected_categories = common_categories

    # Ensure dateslider always has a valid value
    if not dateslider or len(dateslider) != 2:
        dateslider = [0, len(month_list) - 1]

    # Filter by category
    filtered_df = df[df["Category"].isin(selected_categories)]

    # Use the global 'month_list' for converting slider indices to dates
    start_index= int(dateslider[0])
    end_index = int(dateslider[1])

    start_month_str = month_list[start_index]
    end_month_str = month_list[end_index]
    
    # Convert the month strings to datetime objects
    start_date = pd.to_datetime(start_month_str, format="%Y-%m")
    # Adding MonthEnd(0) to capture the entire ending month
    end_date = pd.to_datetime(end_month_str, format="%Y-%m") + pd.offsets.MonthEnd(0)

    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df["valuedate"] >= start_date)
        & (filtered_df["valuedate"] <= end_date)
    ]

    # Pie chart
    fig_pie = px.pie(
        filtered_df,
        names="Category",
        values="amount",
        color="expense/income",
        title="Amount by Category",
        color_discrete_map=color_discrete_map,
    )
    # Bar chart
    fig_bar = px.bar(
        filtered_df,
        x="Category",
        y="amount",
        color="expense/income",
        barmode="group",
        title="Amount by Category",
        color_discrete_map=color_discrete_map,
    )
    # Time-series (line chart)
    fig_time = px.line(
        filtered_df.sort_values("valuedate"),
        x="valuedate",
        y="amount",
        color="expense/income",
        title="Amount Over Time",
        color_discrete_map=color_discrete_map,
    )

    return fig_bar, fig_time, fig_pie



# 5. Run the app
if __name__ == "__main__":
    app.run(debug=True)
