import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Media Campaign Dashboard", layout="wide")
st.title("📊 Media Campaign Dashboard")

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_excel("temp.xlsx", engine="openpyxl")
    df = df[df["Brand"].isin(['Dove', 'LIV', 'HM', 'TRES', 'DMC', 'Knorr', 'Axe'])]  # only keep these 7 brands
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    for col in ['Platform', 'Brand', 'Category', 'Funnel Stage', 'Ad Format']:
        df[col] = df[col].astype('category')
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Campaign Data")

# Date filter
date_range = st.sidebar.date_input("Date Range", [df['Date'].min(), df['Date'].max()])
filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1]))
]

# Platform filter
platform_options = filtered_df['Platform'].unique()
platforms = st.sidebar.multiselect("Platform", platform_options, default=list(platform_options))
filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]

# Brand filter
brand_options = filtered_df['Brand'].unique()
brands = st.sidebar.multiselect("Brand", brand_options, default=list(brand_options))
filtered_df = filtered_df[filtered_df['Brand'].isin(brands)]

# Category filter
category_options = filtered_df['Category'].unique()
categories = st.sidebar.multiselect("Category", category_options, default=list(category_options))
filtered_df = filtered_df[filtered_df['Category'].isin(categories)]

# Funnel Stage filter
funnel_options = filtered_df['Funnel Stage'].unique()
funnel_stages = st.sidebar.multiselect("Funnel Stage", funnel_options, default=list(funnel_options))
filtered_df = filtered_df[filtered_df['Funnel Stage'].isin(funnel_stages)]

# Ad Format filter
ad_format_options = filtered_df['Ad Format'].unique()
ad_formats = st.sidebar.multiselect("Ad Format", ad_format_options, default=list(ad_format_options))
filtered_df = filtered_df[filtered_df['Ad Format'].isin(ad_formats)]

# KPIs
total_spend = filtered_df['Spend'].sum()
total_impressions = filtered_df['Impressions'].sum()

col1, col2 = st.columns(2)
col1.metric("💰 Total Spend", f"${total_spend:,.2f}")
col2.metric("📢 Total Impressions", f"{int(total_impressions):,}")

# Time series: Spend over time by Platform
st.subheader("📆 Spend Over Time by Platform")
time_series = filtered_df.groupby(['Date', 'Platform'])['Spend'].sum().reset_index()
fig1 = px.line(time_series, x='Date', y='Spend', color='Platform', markers=True)
st.plotly_chart(fig1, use_container_width=True)

# Bar chart: Spend by Brand
st.subheader("🏷️ Spend by Brand")
brand_spend = filtered_df.groupby('Brand')['Spend'].sum().reset_index().sort_values(by='Spend', ascending=False)
fig2 = px.bar(brand_spend, x='Brand', y='Spend', color='Brand', text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Pie chart: Funnel Stage distribution
st.subheader("🔄 Funnel Stage Distribution")
funnel_dist = filtered_df['Funnel Stage'].value_counts().reset_index()
funnel_dist.columns = ['Funnel Stage', 'Count']
fig3 = px.pie(funnel_dist, names='Funnel Stage', values='Count', title='Funnel Stage Breakdown')
st.plotly_chart(fig3, use_container_width=True)

# Bar chart: Spend by Quarter and Year
st.subheader("📅 Spend by Time Period")
time_granularity = st.radio("Select Time Granularity", ["Year", "Quarter", "Month"], horizontal=True)
if time_granularity == "Year":
    filtered_df["Time Period"] = filtered_df["Date"].dt.year.astype(str)
elif time_granularity == "Quarter":
    filtered_df["Time Period"] = filtered_df["Date"].dt.to_period("Q").astype(str)
else:  # Month
    filtered_df["Time Period"] = filtered_df["Date"].dt.to_period("M").astype(str)
time_spend = filtered_df.groupby("Time Period")["Spend"].sum().reset_index()
fig4 = px.bar(
    time_spend,
    x="Time Period",
    y="Spend",
    text_auto=True,
    title=f"Spend by {time_granularity}"
)
st.plotly_chart(fig4, use_container_width=True)


# Optional: Show filtered data
with st.expander("📄 View Filtered Data"):
    filtered_df["Date"] = filtered_df["Date"].dt.date
    st.dataframe(filtered_df)
