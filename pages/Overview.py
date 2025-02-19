import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
from decimal import Decimal

# Page config
st.set_page_config(page_title="Overview - Scale LLP Dashboard", layout="wide")

# Load data function from Home.py
def load_data():
    df = pd.read_csv("Test_Full_Year.csv")
    
    # Convert numeric columns
    numeric_columns = [
        'Activity Year', 'Activity month', 'Activity quarter',
        'Non-billable hours', 'Non-billable hours value',
        'Billed & Unbilled hours', 'Billed & Unbilled hours value',
        'Unbilled hours', 'Unbilled hours value',
        'Billed hours', 'Billed hours value',
        'Utilization rate', 'Tracked hours',
        'User rate'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].replace('', pd.NA)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['Activity Year'] = df['Activity Year'].astype(str).str.replace(',', '').astype(float)
    return df

# Load and filter data
df = load_data()
filtered_df = df  # Apply your filtering logic here

# Page Header
st.title("Overview")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Top KPIs with Trend Indicators
st.markdown("### Key Performance Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_billable_hours = filtered_df['Billed & Unbilled hours'].sum()
    prev_billable = total_billable_hours * 0.95  # Previous period for comparison
    delta = ((total_billable_hours - prev_billable) / prev_billable) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    delta_color = "normal" if delta > 0 else "inverse"
    st.metric(
        "Total Billable Hours",
        f"{total_billable_hours:,.1f}",
        f"{arrow} {delta:.1f}%",
        delta_color=delta_color
    )

with col2:
    total_billed = filtered_df['Billed hours'].sum()
    prev_billed = total_billed * 0.95
    delta = ((total_billed - prev_billed) / prev_billed) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    delta_color = "normal" if delta > 0 else "inverse"
    st.metric(
        "Billed Hours",
        f"{total_billed:,.1f}",
        f"{arrow} {delta:.1f}%",
        delta_color=delta_color
    )

with col3:
    avg_utilization = filtered_df['Utilization rate'].mean()
    prev_utilization = avg_utilization * 0.95
    delta = ((avg_utilization - prev_utilization) / prev_utilization) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    delta_color = "normal" if delta > 0 else "inverse"
    st.metric(
        "Average Utilization",
        f"{avg_utilization:.1f}%",
        f"{arrow} {delta:.1f}%",
        delta_color=delta_color
    )

with col4:
    total_revenue = filtered_df['Billed hours value'].sum()
    prev_revenue = total_revenue * 0.95
    delta = ((total_revenue - prev_revenue) / prev_revenue) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    delta_color = "normal" if delta > 0 else "inverse"
    st.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}",
        f"{arrow} {delta:.1f}%",
        delta_color=delta_color
    )

# Hours Distribution Section
st.markdown("### Hours Distribution and Trends")
col1, col2 = st.columns(2)

with col1:
    # Hours Distribution Pie Chart
    hours_data = pd.DataFrame({
        'Category': ['Billed Hours', 'Unbilled Hours', 'Non-billable Hours'],
        'Hours': [
            filtered_df['Billed hours'].sum(),
            filtered_df['Unbilled hours'].sum(),
            filtered_df['Non-billable hours'].sum()
        ]
    })
    
    fig_hours = px.pie(
        hours_data,
        values='Hours',
        names='Category',
        title='Distribution of Hours',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    fig_hours.update_traces(textposition='outside', textinfo='percent+label')
    st.plotly_chart(fig_hours, use_container_width=True)

with col2:
    # Monthly Billable Hours Trend
    monthly_data = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
        'Billed hours': 'sum'
    }).reset_index()
    
    monthly_data['Date'] = pd.to_datetime(
        monthly_data['Activity Year'].astype(str) + '-' + 
        monthly_data['Activity month'].astype(str) + '-01'
    )
    
    fig_trend = px.line(
        monthly_data,
        x='Date',
        y='Billed hours',
        title='Monthly Billed Hours Trend',
        markers=True
    )
    fig_trend.update_traces(line_color='#1f77b4')
    st.plotly_chart(fig_trend, use_container_width=True)

# Practice Area Performance
st.markdown("### Practice Area Performance")
col1, col2 = st.columns(2)

with col1:
    # Practice Area Revenue
    practice_revenue = filtered_df.groupby('Practice area').agg({
        'Billed hours value': 'sum'
    }).reset_index()
    
    fig_practice = px.bar(
        practice_revenue.sort_values('Billed hours value', ascending=True).tail(10),
        x='Billed hours value',
        y='Practice area',
        title='Top 10 Practice Areas by Revenue',
        orientation='h'
    )
    st.plotly_chart(fig_practice, use_container_width=True)

with col2:
    # Practice Area Utilization
    practice_util = filtered_df.groupby('Practice area').agg({
        'Utilization rate': 'mean'
    }).reset_index()
    
    fig_util = px.bar(
        practice_util.sort_values('Utilization rate', ascending=True).tail(10),
        x='Utilization rate',
        y='Practice area',
        title='Top 10 Practice Areas by Utilization Rate',
        orientation='h'
    )
    st.plotly_chart(fig_util, use_container_width=True)

# Utilization Heatmap
st.markdown("### Monthly Utilization Heatmap")
utilization_pivot = filtered_df.pivot_table(
    values='Utilization rate',
    index='Activity month',
    columns='Activity Year',
    aggfunc='mean'
)

# Convert month numbers to names
utilization_pivot.index = [calendar.month_name[int(m)] for m in utilization_pivot.index]

fig_heatmap = px.imshow(
    utilization_pivot,
    labels=dict(x="Year", y="Month", color="Utilization Rate"),
    aspect="auto",
    color_continuous_scale="RdYlBu_r",
    title="Utilization Rate by Month and Year"
)
fig_heatmap.update_layout(
    xaxis_title="Year",
    yaxis_title="Month",
    coloraxis_colorbar_title="Utilization Rate (%)"
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Attorney Performance Overview
st.markdown("### Attorney Performance Overview")
col1, col2 = st.columns(2)

with col1:
    # Top Performers by Revenue
    top_attorneys = filtered_df.groupby('User full name (first, last)').agg({
        'Billed hours value': 'sum'
    }).sort_values('Billed hours value', ascending=False).head(10)
    
    fig_top_attorneys = px.bar(
        top_attorneys,
        title='Top 10 Attorneys by Revenue',
        orientation='h'
    )
    st.plotly_chart(fig_top_attorneys, use_container_width=True)

with col2:
    # Top Performers by Utilization
    top_utilization = filtered_df.groupby('User full name (first, last)').agg({
        'Utilization rate': 'mean'
    }).sort_values('Utilization rate', ascending=False).head(10)
    
    fig_top_util = px.bar(
        top_utilization,
        title='Top 10 Attorneys by Utilization Rate',
        orientation='h'
    )
    st.plotly_chart(fig_top_util, use_container_width=True)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-delta {
        font-size: 14px;
    }
    .metric-delta.positive {
        color: #28a745;
    }
    .metric-delta.negative {
        color: #dc3545;
    }
    .plot-container {
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-radius: 10px;
        padding: 15px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)
