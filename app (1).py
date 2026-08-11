
import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown('\n<style>\n\n.main-title {\n    font-size: 38px;\n    font-weight: 700;\n    text-align: center;\n    margin-bottom: 5px;\n}\n\n.subtitle {\n    text-align: center;\n    font-size: 18px;\n    margin-bottom: 30px;\n}\n\n[data-testid="stMetric"] {\n    border: 1px solid rgba(128,128,128,0.25);\n    border-radius: 12px;\n    padding: 15px;\n    text-align: center;\n}\n\n[data-testid="stMetricLabel"] {\n    font-size: 15px;\n}\n\n[data-testid="stMetricValue"] {\n    font-size: 25px;\n    font-weight: 700;\n}\n\n</style>\n', unsafe_allow_html=True)

st.set_page_config(
    page_title="Nassau Candy Distributor",
    page_icon="🍬",
    layout="wide"
)

st.title("🍬 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.write(
    "An interactive dashboard to analyze sales, costs, gross profit, "
    "product profitability, divisions and regional performance."
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor (1).csv")
    
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")

    df["Profit Margin (%)"] = (
        df["Gross Profit"] / df["Sales"] * 100
    )

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

# Sidebar
st.sidebar.header("🔎 Filters")

division_options = sorted(df["Division"].dropna().unique())
region_options = sorted(df["Region"].dropna().unique())

selected_divisions = st.sidebar.multiselect(
    "Select Division",
    division_options,
    default=division_options,
    key="division_filter"
)

selected_regions = st.sidebar.multiselect(
    "Select Region",
    region_options,
    default=region_options,
    key="region_filter"
)

margin_threshold = st.sidebar.slider(
    "🎚️ Minimum Profit Margin (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=1.0
)

product_search = st.sidebar.text_input(
    "🔍 Search Product",
    placeholder="Enter product name..."
)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter data
filtered_df = df[
    df["Division"].isin(selected_divisions) &
    df["Region"].isin(selected_regions)
].copy()

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

# Apply product search
if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(product_search, case=False, na=False)
    ]

# Apply margin threshold
if margin_threshold > 0:
    filtered_df = filtered_df[
        (filtered_df["Gross Profit"] /
         filtered_df["Sales"] * 100) >= margin_threshold
    ]

# KPIs
st.header("📊 Key Performance Indicators")

total_sales = filtered_df["Sales"].sum()
total_cost = filtered_df["Cost"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Total Cost", f"${total_cost:,.2f}")
c3.metric("Gross Profit", f"${total_profit:,.2f}")
c4.metric("Units Sold", f"{total_units:,.0f}")
c5.metric("Profit Margin", f"{profit_margin:.2f}%")

st.divider()

# Division analysis
st.header("🏢 Division Performance")

division_summary = (
    filtered_df.groupby("Division")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
    .reset_index()
)

division_summary["Profit Margin (%)"] = (
    division_summary["Gross_Profit"] /
    division_summary["Sales"] * 100
)

c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        division_summary,
        x="Division",
        y="Sales",
        title="Sales by Division",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        division_summary,
        x="Division",
        y="Gross_Profit",
        title="Gross Profit by Division",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

# Regional analysis
st.header("🌎 Regional Performance")

region_summary = (
    filtered_df.groupby("Region")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
    .reset_index()
)

region_summary["Profit Margin (%)"] = (
    region_summary["Gross_Profit"] /
    region_summary["Sales"] * 100
)

c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        region_summary,
        x="Region",
        y="Sales",
        title="Sales by Region",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        region_summary,
        x="Region",
        y="Gross_Profit",
        title="Gross Profit by Region",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

# Product analysis
st.header("🍫 Product Profitability")

product_summary = (
    filtered_df.groupby("Product Name")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
    .reset_index()
)

product_summary["Profit Margin (%)"] = (
    product_summary["Gross_Profit"] /
    product_summary["Sales"] * 100
)

# Additional profitability metrics
product_summary["Profit per Unit"] = (
    product_summary["Gross_Profit"] /
    product_summary["Units"]
)

product_summary["Revenue Contribution (%)"] = (
    product_summary["Sales"] /
    product_summary["Sales"].sum() * 100
)

product_summary["Profit Contribution (%)"] = (
    product_summary["Gross_Profit"] /
    product_summary["Gross_Profit"].sum() * 100
)

c1, c2 = st.columns(2)

top_profit = product_summary.nlargest(10, "Gross_Profit")

with c1:
    fig = px.bar(
        top_profit.sort_values("Gross_Profit"),
        x="Gross_Profit",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Gross Profit",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

top_sales = product_summary.nlargest(10, "Sales")

with c2:
    fig = px.bar(
        top_sales.sort_values("Sales"),
        x="Sales",
        y="Product Name",
        orientation="h",
        title="Top 10 Products by Sales",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

# Margin analysis
st.subheader("🎯 Top Products by Profit Margin")

top_margin = product_summary.nlargest(10, "Profit Margin (%)")

fig = px.bar(
    top_margin.sort_values("Profit Margin (%)"),
    x="Profit Margin (%)",
    y="Product Name",
    orientation="h",
    title="Top 10 Products by Profit Margin",
    text_auto=".2f"
)

st.plotly_chart(fig, use_container_width=True)

# High sales low margin
st.subheader("⚠️ High-Sales, Lower-Margin Products")

sales_median = product_summary["Sales"].median()
margin_median = product_summary["Profit Margin (%)"].median()

attention_products = product_summary[
    (product_summary["Sales"] >= sales_median) &
    (product_summary["Profit Margin (%)"] < margin_median)
].sort_values("Sales", ascending=False).head(10)

if not attention_products.empty:
    st.dataframe(
        attention_products[
            [
                "Product Name",
                "Sales",
                "Cost",
                "Gross_Profit",
                "Profit Margin (%)"
            ]
        ],
        use_container_width=True
    )

    st.warning(
        "These products generate relatively high sales but "
        "have below-median profit margins. Pricing or cost "
        "control may improve profitability."
    )
else:
    st.success("No high-sales, lower-margin products identified.")

# Monthly trend
st.header("📈 Monthly Sales & Profit Trend")

filtered_df["Month"] = (
    filtered_df["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly = (
    filtered_df.groupby("Month")
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

fig = px.line(
    monthly,
    x="Month",
    y=["Sales", "Gross_Profit"],
    markers=True,
    title="Monthly Sales and Gross Profit"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# PROFIT CONCENTRATION / PARETO ANALYSIS
# --------------------------------------------------

st.header("🎯 Profit Concentration Analysis")

pareto = product_summary.sort_values(
    "Gross_Profit",
    ascending=False
).copy()

pareto["Cumulative Profit (%)"] = (
    pareto["Gross_Profit"].cumsum()
    / pareto["Gross_Profit"].sum()
    * 100
)

pareto["Cumulative Revenue (%)"] = (
    pareto["Sales"].cumsum()
    / pareto["Sales"].sum()
    * 100
)

# Number of products needed to reach 80% of profit
profit_80 = (
    pareto["Cumulative Profit (%)"] >= 80
)

if profit_80.any():
    products_for_80_profit = (
        profit_80.idxmax()
    )

    products_count = (
        pareto.index.get_loc(products_for_80_profit) + 1
    )
else:
    products_count = len(pareto)

total_products = len(pareto)

profit_dependency = (
    pareto.head(
        max(1, int(total_products * 0.20))
    )["Gross_Profit"].sum()
    / pareto["Gross_Profit"].sum()
    * 100
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Products",
    f"{total_products}"
)

c2.metric(
    "Products Generating 80% of Profit",
    f"{products_count}"
)

c3.metric(
    "Top 20% Profit Contribution",
    f"{profit_dependency:.2f}%"
)

fig = px.line(
    pareto,
    x=range(1, len(pareto) + 1),
    y="Cumulative Profit (%)",
    markers=True,
    title="Pareto Analysis – Cumulative Profit Contribution"
)

fig.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="80% Profit"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# MARGIN VOLATILITY ANALYSIS
# --------------------------------------------------

st.header("📊 Margin Volatility Analysis")

monthly_margin = (
    filtered_df
    .groupby(
        filtered_df["Order Date"].dt.to_period("M")
    )
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

monthly_margin["Profit Margin (%)"] = (
    monthly_margin["Gross_Profit"] /
    monthly_margin["Sales"] * 100
)

monthly_margin["Month"] = (
    monthly_margin["Order Date"]
    .astype(str)
)

if len(monthly_margin) > 1:

    margin_volatility = (
        monthly_margin["Profit Margin (%)"].std()
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Margin Volatility (Std. Dev.)",
        f"{margin_volatility:.2f}%"
    )

    c2.metric(
        "Average Monthly Margin",
        f"{monthly_margin['Profit Margin (%)'].mean():.2f}%"
    )

    fig = px.line(
        monthly_margin,
        x="Month",
        y="Profit Margin (%)",
        markers=True,
        title="Monthly Profit Margin Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "Select a wider date range to calculate margin volatility."
    )

# Cost vs profit
st.header("💰 Cost vs Gross Profit")

fig = px.scatter(
    filtered_df,
    x="Cost",
    y="Gross Profit",
    size="Sales",
    hover_name="Product Name",
    title="Cost vs Gross Profit"
)

st.plotly_chart(fig, use_container_width=True)

# Table
st.header("📋 Product Profitability Table")

st.dataframe(
    product_summary.sort_values(
        "Gross_Profit",
        ascending=False
    ).head(20),
    use_container_width=True
)

# Insights
st.header("💡 Key Business Insights & Recommendations")

st.success(
    "🏆 **Chocolate is the strongest division**, generating "
    "$88,824.62 in gross profit with a 67.45% profit margin."
)

st.info(
    "🌎 **Pacific generates the highest total gross profit** "
    "at $30,485.94, while **Interior has the highest regional "
    "profit margin** at 66.43%."
)

st.success(
    "🍫 **Wonka Bar - Scrumdiddlyumptious** is the highest "
    "gross-profit product, generating $19,357.50 at a 69.44% margin."
)

st.warning(
    "⚠️ **Kazookles has a very low profit margin of 7.69%**. "
    "Its pricing and cost structure should be reviewed."
)

st.markdown(
    """
    ### 📌 Business Recommendations

    **1. Prioritize high-profit Chocolate products**  
    Chocolate contributes the majority of company sales and gross profit.

    **2. Focus promotions on profitable Wonka products**  
    Products with strong sales and high gross profit should receive greater promotional attention.

    **3. Review low-margin products**  
    Kazookles requires pricing or cost-control review to improve profitability.

    **4. Use region-specific strategies**  
    Pacific should be monitored for total profit contribution, while Interior can be studied for its stronger margin performance.

    **5. Evaluate products using multiple metrics**  
    Sales, units, gross profit and profit margin should be considered together rather than relying on margin alone.
    """
)

st.divider()

st.caption(
    "Nassau Candy Distributor | Product Line Profitability "
    "& Margin Performance Analysis"
)
