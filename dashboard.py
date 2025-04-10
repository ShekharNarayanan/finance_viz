import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from finance_viz.utils.transaction_data_utils import PROJECT_ROOT
from plotly.subplots import make_subplots
from finance_viz.utils.dashboard_utils import (
    get_monthly_labels,
    find_most_common_categories,
)

data_path = PROJECT_ROOT / "input_data" / "transactions_categorized_copy.xlsx"

# 1. Load your data
df = pd.read_excel(data_path)
df["valuedate"] = pd.to_datetime(df["valuedate"])  # Convert valuedate to datetime

# get data for date slider
marks, month_list = get_monthly_labels(df)
custom_marks = {
    k: {"label": v, "style": {"fontSize": "18px", "fontWeight": "bold"}}
    for k, v in marks.items()
}

# get the most common categories for the dropdown
common_categories = find_most_common_categories(df)

color_discrete_map = {"income": "green", "expense": "red"}

# 2. Create a Dash app
app = Dash(__name__)

# 3. Define layout with two charts + a simple filter
app.layout = html.Div(
    [
        # Other components in order
        html.Div(
            dcc.Dropdown(
                id="category-filter",
                options=[
                    {"label": cat, "value": cat} for cat in df["Category"].unique()
                ],
                multi=True,
                placeholder="Select one or more categories",
            ),
            style={"marginBottom": "20px"},  # add spacing after dropdown
        ),
        html.Div(
            dcc.RangeSlider(
                id="date-slider",
                min=0,
                max=len(month_list) - 1,
                marks=custom_marks,
                value=[0, len(month_list) - 1],  # [start_index, end_index]
            ),
            style={"marginBottom": "20px"},
        ),
        html.Div(
            dcc.Checklist(
                id="checklist",  # use your desired id
                options=[
                    {"label": "Income", "value": "income"},
                    {"label": "Expenses", "value": "expense"},
                ],
                value=["income", "expense"],
                inline=True,
                style={
                    "fontWeight": "bold",
                    "fontSize": "30px",
                    "display": "inline-block",
                },
            ),
            style={"width": "100%", "textAlign": "center", "marginBottom": "20px"},
        ),
        dcc.Graph(id="combined-chart"),
    ]
)


# 4. Single callback: filter the data and return 3 figures
@app.callback(
    Output("combined-chart", "figure"),
    [
        Input("category-filter", "value"),
        Input("date-slider", "value"),
        Input("checklist", "value"),
    ],
)
# decorator function for the callback - this is how Dash knows to call this function when the input changes
def update_charts(selected_categories, dateslider, selected_types):
    # ============ 1) HANDLE INPUTS ============

    # Select expense or income
    if not selected_types:
        selected_types = ["income", "expense"]

    # If none selected, use common_categories
    if not selected_categories:
        selected_categories = common_categories

    # If date slider is invalid, fall back to full range
    if not dateslider or len(dateslider) != 2:
        dateslider = [0, len(month_list) - 1]

    start_index = int(dateslider[0])
    end_index = int(dateslider[1])

    start_month_str = month_list[start_index]
    end_month_str = month_list[end_index]

    start_date = pd.to_datetime(start_month_str, format="%Y-%m")
    end_date = pd.to_datetime(end_month_str, format="%Y-%m") + pd.offsets.MonthEnd(0)

    # Filter df
    filtered_df = df[
        (df["Category"].isin(selected_categories))
        & (df["expense/income"].isin(selected_types))  # this line is key
        & (df["valuedate"] >= start_date)
        & (df["valuedate"] <= end_date)
    ]

    # ============ 2) CREATE INDIVIDUAL FIGS ============

    # Pie chart
    fig_pie = px.pie(
        filtered_df,
        names="Category",
        values="amount",
        color="expense/income",
        title="Amount by Category",
        color_discrete_map=color_discrete_map,
    )
    fig_pie.update_traces(
        textposition="outside",
        textinfo="label+percent",
        showlegend=False,  # no legend for the pie
    )

    # Bar chart
    fig_bar = px.bar(
        filtered_df,
        x="Category",
        y="amount",
        labels={"amount": "Amount (Euros)"},
        color="expense/income",
        barmode="group",
        title="Amount by Category",
        color_discrete_map=color_discrete_map,
    )

    # Time-series with discrete bar charts
    fig_time_bar = px.bar(
    filtered_df.sort_values("valuedate"),
    # If you want to treat each date as a category, you can convert it to a string.
    x=filtered_df.sort_values("valuedate")["valuedate"].dt.strftime("%Y-%m-%d"),
    y="amount",  # or "amount (euros)" if you use labels; see next step.
    color="expense/income",
    barmode="group",
    title="Spending Over Time",
    color_discrete_map=color_discrete_map
)
    # Now, update the layout of fig_bars so that the x-axis is treated as a discrete category axis.
    fig_time_bar.update_layout(
        xaxis=dict(type="category"),
        # You can also adjust margins, font sizes, etc. here if desired:
        margin=dict(l=50, r=50, t=50, b=100)
    )

    # ============ 3) MAKE SUBPLOTS ============

    combined_fig = make_subplots(
        rows=2,
        cols=2,
        # row_heights: proportion of total height each row gets
        row_heights=[0.4, 0.4],
        # column_widths: proportion of total width each col gets
        column_widths=[0.6, 0.4],
        # If you want spacing between rows, e.g., 0.1 is 10% of figure height
        vertical_spacing=0.2,
        # We won't rely heavily on subplot_titles for the pie cell
        subplot_titles=("Amount by Category", "", "Amount spent over time"),
        # Note the second subplot in the top row is a pie/donut => domain
        specs=[
            [{"type": "xy"}, {"type": "domain"}],
            [{"type": "xy"}, None],
        ],
    )

    # ============ 4) ADD TRACES TO SUBPLOTS ============

    # (A) Bar Chart => row=1, col=1
    for trace in fig_bar.data:
        combined_fig.add_trace(trace, row=1, col=1)
        combined_fig.update_yaxes(
            title_text=fig_time_bar.layout.yaxis.title.text, row=1, col=1
        )

    # (B) Pie Chart => row=1, col=2
    # We'll update the domain to push it down or up.
    # Setting y=[0,0.75] means the pie occupies bottom 75% of that cell, leaving 25% at the top
    for trace in fig_pie.data:
        trace.showlegend = False
        trace.update(
            domain=dict(x=[0.0, 1.0], y=[0.0, 0.95])
        )  # Adjust to push it further down or up
        trace.update(
            textfont=dict(
                family="Arial Black",
                size=14,
                # color="black"  # optional
            )
        )
        combined_fig.add_trace(trace, row=1, col=2)

    # (C) Time Series => row=2, col=1 (spanning both columns if you like, but let's keep it col=1 for now)
    for trace in fig_time_bar.data:
        combined_fig.add_trace(trace, row=2, col=1)
    
        combined_fig.update_yaxes(
            title_text=fig_time_bar.layout.yaxis.title.text, row=2, col=1
        )
        

    # ============ 5) UPDATE LAYOUT ============

    combined_fig.update_layout(
        # More top margin => extra space above the top row
        margin=dict(l=100, b=80, t=100),
        height=1200,
        width=1800,
        showlegend=True,
        font=dict(family="Arial Black", size=14),
        # Move the figure title to the left
        title=dict(
            text="Visualized finances",
            x=0.01,  # 0.0 = far left, 0.5 = center, 1.0 = far right
            xanchor="left",
        ),
        # Position the legend near the top, to the right of the title
        legend=dict(
            orientation="h",  # horizontal legend
            yanchor="bottom",
            y=1.05,  # just above the top plotting area
            xanchor="left",
            x=0.3,  # shift it right so it sits beside the title
        ),
    )

    return combined_fig


# 5. Run the app
if __name__ == "__main__":
    app.run(debug=True)
