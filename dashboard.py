import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from finance_viz.utils.transaction_data_utils import PROJECT_ROOT

data_path = PROJECT_ROOT / "input_data" / "transactions_categorized.xlsx"

# 1. Load your data
df = pd.read_excel(data_path)
df["valuedate"] = pd.to_datetime(df["valuedate"])  # Convert valuedate to datetime

# 2. Create a Dash app
app = Dash(__name__)

# 3. Define layout with two charts + a simple filter
app.layout = html.Div([
    dcc.Dropdown(
        id="category-filter",
        options=[{"label": cat, "value": cat} for cat in df["Category"].unique()],
        multi=True,
        placeholder="Select one or more categories"
    ),
    dcc.Graph(id="bar-chart"),
    dcc.Graph(id="time-series-chart")
])

# 4. Add interactivity: filter the data by Category
@app.callback(
    [Output("bar-chart", "figure"),
    Output("time-series-chart", "figure")],
    [Input("category-filter", "value")]
)
def update_charts(selected_categories):
    if selected_categories:
        filtered_df = df[df["Category"].isin(selected_categories)]
    else:
        filtered_df = df

    # Basic bar chart of amount by category, colored by expense/income
    fig_bar = px.bar(
        filtered_df,
        x="Category",
        y="amount",
        color="expense/income",
        barmode="group",
        title="Amount by Category"
    )

    # Basic time-series (line chart) of amount by date, colored by expense/income
    fig_time = px.line(
        filtered_df.sort_values("valuedate"),
        x="valuedate",
        y="amount",
        color="expense/income",
        title="Amount Over Time"
    )

    return fig_bar, fig_time

# 5. Run the app
if __name__ == "__main__":
    app.run(debug=True)
