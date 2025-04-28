import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from finance_viz.utils.transaction_data_utils import PROJECT_ROOT
from finance_viz.utils.dashboard_utils import (
    get_monthly_labels,
    find_most_common_categories,
)
from finance_viz.utils import recommender


# ── 1. LOAD DATA ───────────────────────────────────────────────────────
data_path = PROJECT_ROOT / "input_data" / "transactions_categorized_copy.xlsx"
df = pd.read_excel(data_path)
df["valuedate"] = pd.to_datetime(df["valuedate"])
insights = recommender.generate_insights(df)

marks, month_list = get_monthly_labels(df)
custom_marks = {
    i: {
        "label": m.replace("-", "/"),
        "style": {
            "fontSize": "16px",        # was 14px
            "fontWeight": "bold",
            "color": "#D1D5DB",
            "transform": "translateY(10px) rotate(-25deg)",
        },
    } for i, m in marks.items()
}
common_categories = find_most_common_categories(df)

# ── 2. COLOURS & FONTS ────────────────────────────────────────────────
PAGE_BG, CARD_BG = "#1F2937", "#374151"
TXT_PRI, TXT_SEC = "#FFFFFF", "#D1D5DB"
GRID_CLR = "#4B5563"

INCOME_CLR, EXPENSE_CLR = "#0093D1", "#FF4C4C"
color_map = {"income": INCOME_CLR, "expense": EXPENSE_CLR}

muted_palette = [
    "#d35400",
    "#3498db",
    "#8e44ad",
    "#c8d96f",
    "#16a085",
    "#e84393",
    "#00cec9",
    "#fdcb6e",
]

BOLD_FONT = dict(family="Arial Black", size=16, color=TXT_PRI)
TRANSITION = {"duration": 600, "easing": "cubic-in-out"}

# ── 3. DASH LAYOUT ─────────────────────────────────────────────────────
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def kpi_card(title, cid, colour=TXT_PRI):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(
                    title,
                    style={"fontWeight": "bold", "fontSize": "18px", "color": TXT_SEC},
                ),
                html.H2(
                    id=cid,
                    style={"fontWeight": "bold", "fontSize": "30px", "color": colour},
                ),
            ]
        ),
        style={"backgroundColor": CARD_BG, "border": "none"},
    )


def insight_card(rec):
    return dbc.Alert(
        [
            # headline
            html.H5(
                rec["title"],
                style={
                    "fontWeight": "bold",
                    "fontSize": "20px",     # bigger
                    "color": TXT_PRI        # white
                }
            ),
            # detail
            html.P(
                rec["detail"],
                style={
                    "fontWeight": "bold",
                    "fontSize": "16px",     # also larger
                    "color": TXT_PRI        # white
                }
            ),
        ],
        color="dark",          # keeps Bootstrap-alert contrast low
        style={"backgroundColor": CARD_BG, "border": "none"},
    )


app.layout = html.Div(
    style={"backgroundColor": PAGE_BG, "minHeight": "100vh", "padding": "1rem"},
    children=[
        dbc.Container(fluid=True, children=[

            # ── KPI ROW ───────────────────────────────────────────────
            dbc.Row([
                dbc.Col(kpi_card("Total Income",  "income-kpi",  INCOME_CLR),  md=4),
                dbc.Col(kpi_card("Total Expense", "expense-kpi", EXPENSE_CLR), md=4),
                dbc.Col(kpi_card("Net Balance",   "net-kpi"),                md=4),
            ], className="mb-4"),

            # ── CONTROLS ROW ─────────────────────────────────────────
            dbc.Row([

                # Category dropdown
                dbc.Col(
                    dcc.Dropdown(
                        id="category-filter",
                        options=[{"label": c, "value": c} for c in df["Category"].unique()],
                        multi=True,
                        placeholder="Select categories",
                        style={
                            "fontWeight": "bold",
                            "backgroundColor": "white",
                            "color": "black"
                        }
                    ),
                    md=4
                ),

                # Date‐slider + heading
                dbc.Col(
                    [
                        html.H6(
                            "Select Date Range",
                            style={
                                "color": TXT_PRI,
                                "fontSize": "18px",
                                "fontWeight": "bold"
                            }
                        ),
                        dcc.RangeSlider(
                            id="date-slider",
                            min=0,
                            max=len(month_list) - 1,
                            step=1,
                            marks=custom_marks,
                            value=[0, len(month_list) - 1],
                            tooltip={"placement": "bottom"}
                        )
                    ],
                    md=5
                ),

                # Checklist + heading
                dbc.Col(
                    [
                        html.H6(
                            "Transaction Types",
                            style={
                                "color": TXT_PRI,
                                "fontSize": "18px",
                                "fontWeight": "bold",
                                "textAlign": "center"
                            }
                        ),
                        dcc.Checklist(
                            id="checklist",
                            options=[
                                {"label": "Income",  "value": "income"},
                                {"label": "Expense", "value": "expense"}
                            ],
                            value=["income", "expense"],
                            inline=True,
                            style={
                                "fontSize": "18px",
                                "fontWeight": "bold",
                                "color": TXT_PRI,
                                "textAlign": "center"
                            }
                        )
                    ],
                    md=3
                ),

            ], className="mb-4 align-items-start"),

            # ── TOP CHARTS + INSIGHTS ROW ────────────────────────────
            dbc.Row([

                # Bar chart (left)
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id="bar-chart", animate=True),
                        body=True,
                        style={"backgroundColor": CARD_BG, "border": "none"}
                    ),
                    md=6
                ),

                # SUGGESTED ACTIONS OR INSIGHTS (right)
                dbc.Col(
                    dbc.Card(
                        children=[
                            html.H5(
                                "Suggested actions",
                                style={
                                    "color": TXT_PRI,
                                    "fontWeight": "bold",
                                    "fontSize": "20px",
                                    "paddingLeft": "1rem",
                                },
                            ),
                            html.Ul(id="insight-list", style={"paddingLeft": "1rem"})
                        ],
                        body=True,
                        style={"backgroundColor": CARD_BG, "border": "none"},
                    ),
                    md=6,
                ),

            ], className="mb-4"),

            # ── BOTTOM CHARTS ROW ─────────────────────────────────────
            dbc.Row([

                # Pie chart (~40%)
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id="pie-chart", animate=False),
                        body=True,
                        style={"backgroundColor": CARD_BG, "border": "none"}
                    ),
                    md=5
                ),

                # Time-series (~60%)
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id="time-chart", animate=True),
                        body=True,
                        style={"backgroundColor": CARD_BG, "border": "none"}
                    ),
                    md=7
                ),

            ]),

        ])
    ]
)



# ── 4. CALLBACK ---------------------------------------------------------
@app.callback(
    # add one more Output for your insights-list, e.g. html.Ul children
    Output("insight-list", "children"),
    Output("income-kpi","children"),
    Output("expense-kpi","children"),
    Output("net-kpi","children"),
    Output("bar-chart","figure"),
    Output("pie-chart","figure"),
    Output("time-chart","figure"),
    Input("category-filter","value"),
    Input("date-slider","value"),
    Input("checklist","value"),
)
def refresh(cats, slider, types):
    if not types:
        types = ["income", "expense"]
    if not cats:
        cats = common_categories
    s_idx, e_idx = (int(round(v)) for v in slider)
    start = pd.to_datetime(f"{month_list[s_idx]}-01")
    end = pd.to_datetime(f"{month_list[e_idx]}-01") + pd.offsets.MonthEnd(0)

    d = df[
        df["Category"].isin(cats)
        & df["expense/income"].isin(types)
        & df["valuedate"].between(start, end)
    ].copy()

    # insights 
    lookback_n = e_idx - s_idx + 1
    insights = recommender.generate_insights(
        df,                    # still feed the *full* df so it can compute historical
        lookback_months=lookback_n,
        top_k=5
    )

    # UI of insights
    insight_items = []
    for rec in insights:
        insight_items.append(
            html.Li([
                html.Strong(rec["title"], style={"color":TXT_PRI}),
                html.Br(),
                html.Small(rec["detail"], style={"color":TXT_PRI})
            ], style={"marginBottom":"0.5rem"})
        )
    if not insight_items:
        insight_items = [html.Li("No urgent insights 🙂", style={"color":TXT_PRI})]

    # KPIs
    inc, exp = (
        d.loc[d["expense/income"] == t, "amount"].sum() for t in ("income", "expense")
    )
    net = inc - exp

    # Month label optional for top bar; keep real date for bottom
    d_tot = d.groupby(["Category", "expense/income"], as_index=False)["amount"].sum()

    # Colour scheme
    if len(types) == 1:
        cmap = {
            c: muted_palette[i % len(muted_palette)]
            for i, c in enumerate(d_tot["Category"].unique())
        }
        hue = "Category"
    else:
        cmap = color_map
        hue = "expense/income"

    # ── TOP LEFT BAR (legend kept) --------------------------------------
    bar_fig = px.bar(
        d_tot,
        x="Category", y="amount",
        color=hue,
        color_discrete_map=cmap,
        title="Amount by Category",
        template="plotly_dark"
    )

    # define the same clean ticks you used below
    clean_ticks = [1_000, 5_000, 10_000, 20_000]

    bar_fig.update_layout(
        font=BOLD_FONT,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        xaxis=dict(gridcolor=GRID_CLR, tickfont=BOLD_FONT),
        yaxis=dict(
            # keep linear scale here, but force only these ticks
            type="linear",
            tickmode="array",
            tickvals=clean_ticks,
            ticktext=[f"€{v:,}" for v in clean_ticks],
            gridcolor=GRID_CLR,
            tickfont=BOLD_FONT
        ),
        legend_title_text="",
        transition=TRANSITION
    )


    # ── PIE -------------------------------------------------------------
    pie_data = d_tot[d_tot["amount"] > 0]
    pie_fig = px.pie(
        pie_data,
        names="Category",
        values="amount",
        color=hue,
        color_discrete_map=cmap,
        title="Category Breakdown",
        template="plotly_dark",
    )
    pie_fig.update_traces(
        textinfo="label+percent", textfont=BOLD_FONT, showlegend=False
    )
    pie_fig.update_layout(font=BOLD_FONT, paper_bgcolor=CARD_BG)

    # --- BOTTOM TIME CHART (y-axis tweak) ---------------------------------
    time_fig = px.bar(
        d, x="valuedate", y="amount",
        color="expense/income", color_discrete_map=color_map,
        title="Transactions Over Time", template="plotly_dark"
    )

    clean_ticks = [100, 500, 2_000]          # adjust max if needed
    time_fig.update_layout(
        font=BOLD_FONT,
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        xaxis=dict(
            range=[start, end], dtick="M1", tickformat="%Y-%m",
            tickangle=-45, tickfont=BOLD_FONT, gridcolor=GRID_CLR
        ),
        yaxis=dict(
            type="log",                # ← keep log
            tickvals=clean_ticks,
            ticktext=[f"€{v:,}" for v in clean_ticks],
            gridcolor=GRID_CLR, tickfont=BOLD_FONT
        ),
        margin=dict(b=120),
        legend_title_text="",
        transition=TRANSITION
    )


    return (
      insight_items,               # goes to Output("insight-list","children")
      f"€{inc:,.2f}",              # Output("income-kpi","children")
      f"€{exp:,.2f}",              # Output("expense-kpi","children")
      f"€{net:,.2f}",              # Output("net-kpi","children")
      bar_fig,                     # Output("bar-chart","figure")
      pie_fig,                     # Output("pie-chart","figure")
      time_fig                     # Output("time-chart","figure")
    )


# ── 5. RUN SERVER ──────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
