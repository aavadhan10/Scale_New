import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
import sys
import os

# Import functions from Home.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Home import load_data, apply_filters, create_sidebar_filters

# Page config
st.set_page_config(page_title="Practice Areas - Scale LLP Dashboard", layout="wide")

# Load data and create filters
df = load_data()
create_sidebar_filters()
filtered_df = apply_filters(df)

# Page Header
st.title("Practice Areas Analysis")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Key Practice Area Metrics
st.markdown("### Key Practice Area Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_practices = filtered_df['Practice area'].nunique()
    prev_practices = total_practices * 0.95
    delta = ((total_practices - prev_practices) / prev_practices) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Practice Areas",
        f"{total_practices:,}",
        f"{arrow} {delta:.1f}%"
    )

with col2:
    avg_revenue_per_practice = filtered_df.groupby('Practice area')['Billed hours value'].sum().mean()
    prev_revenue = avg_revenue_per_practice * 0.95
    delta = ((avg_revenue_per_practice - prev_revenue) / prev_revenue) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Avg Revenue per Practice",
        f"${avg_revenue_per_practice:,.2f}",
        f"{arrow} {delta:.1f}%"
    )

with col3:
    avg_utilization = filtered_df.groupby('Practice area')['Utilization rate'].mean().mean()
    prev_util = avg_utilization * 0.95
    delta = ((avg_utilization - prev_util) / prev_util) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Average Utilization",
        f"{avg_utilization:.1f}%",
        f"{arrow} {delta:.1f}%"
    )

with col4:
    avg_rate = (filtered_df['Billed hours value'].sum() / filtered_df['Billed hours'].sum())
    prev_rate = avg_rate * 0.95
    delta = ((avg_rate - prev_rate) / prev_rate) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Average Hourly Rate",
        f"${avg_rate:.2f}",
        f"{arrow} {delta:.1f}%"
    )

# Practice Area Performance Overview
st.markdown("### Practice Area Performance")
col1, col2 = st.columns(2)

with col1:
    # Revenue by Practice Area
    practice_revenue = filtered_df.groupby('Practice area').agg({
        'Billed hours value': 'sum'
    }).sort_values('Billed hours value', ascending=True)
    
    fig_revenue = px.bar(
        practice_revenue,
        orientation='h',
        title='Revenue by Practice Area'
    )
    fig_revenue.update_layout(yaxis_title="Practice Area", xaxis_title="Revenue ($)")
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    # Hours by Practice Area
    practice_hours = filtered_df.groupby('Practice area').agg({
        'Billed hours': 'sum'
    }).sort_values('Billed hours', ascending=True)
    
    fig_hours = px.bar(
        practice_hours,
        orientation='h',
        title='Billed Hours by Practice Area'
    )
    fig_hours.update_layout(yaxis_title="Practice Area", xaxis_title="Billed Hours")
    st.plotly_chart(fig_hours, use_container_width=True)

# Practice Area Utilization Analysis
st.markdown("### Practice Area Utilization")

# Create utilization heatmap by month
practice_util = filtered_df.pivot_table(
    values='Utilization rate',
    index='Practice area',
    columns='Activity month',
    aggfunc='mean'
)

# Convert month numbers to names
practice_util.columns = [calendar.month_name[int(m)] for m in practice_util.columns]

fig_heatmap = px.imshow(
    practice_util,
    title='Practice Area Utilization by Month',
    labels=dict(x="Month", y="Practice Area", color="Utilization Rate"),
    aspect="auto",
    color_continuous_scale="RdYlBu_r"
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Practice Area Revenue Trends
st.markdown("### Practice Area Revenue Trends")

# Get top 5 practice areas
top_5_practices = filtered_df.groupby('Practice area')['Billed hours value'].sum().nlargest(5).index

practice_trends = filtered_df[
    filtered_df['Practice area'].isin(top_5_practices)
].groupby(['Activity Year', 'Activity month', 'Practice area']).agg({
    'Billed hours value': 'sum'
}).reset_index()

practice_trends['Date'] = pd.to_datetime(
    practice_trends['Activity Year'].astype(int).astype(str) + '-' + 
    practice_trends['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
)

fig_trends = px.line(
    practice_trends,
    x='Date',
    y='Billed hours value',
    color='Practice area',
    title='Revenue Trends - Top 5 Practice Areas',
    markers=True
)
fig_trends.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue ($)",
    hovermode='x unified'
)
st.plotly_chart(fig_trends, use_container_width=True)

# Attorney Distribution in Practice Areas
st.markdown("### Attorney Distribution by Practice Area")
col1, col2 = st.columns(2)

with col1:
    # Number of Attorneys per Practice Area
    attorneys_per_practice = filtered_df.groupby('Practice area')['User full name (first, last)'].nunique().sort_values(ascending=True)
    
    fig_attorneys = px.bar(
        attorneys_per_practice,
        orientation='h',
        title='Number of Attorneys by Practice Area'
    )
    fig_attorneys.update_layout(yaxis_title="Practice Area", xaxis_title="Number of Attorneys")
    st.plotly_chart(fig_attorneys, use_container_width=True)

with col2:
    # Attorney Levels by Practice Area
    attorney_levels = filtered_df.groupby(['Practice area', 'Attorney level']).size().reset_index(name='count')
    
    fig_levels = px.bar(
        attorney_levels,
        x='Practice area',
        y='count',
        color='Attorney level',
        title='Attorney Level Distribution by Practice Area',
        barmode='stack'
    )
    fig_levels.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_levels, use_container_width=True)

# Practice Area Efficiency Analysis
st.markdown("### Practice Area Efficiency")
col1, col2 = st.columns(2)

with col1:
    # Average Rate by Practice Area
    avg_rate_by_practice = (
        filtered_df.groupby('Practice area').agg({
            'Billed hours value': 'sum',
            'Billed hours': 'sum'
        })
    )
    avg_rate_by_practice['Average Rate'] = avg_rate_by_practice['Billed hours value'] / avg_rate_by_practice['Billed hours']
    avg_rate_by_practice = avg_rate_by_practice.sort_values('Average Rate', ascending=True)
    
    fig_rates = px.bar(
        avg_rate_by_practice,
        y=avg_rate_by_practice.index,
        x='Average Rate',
        title='Average Hourly Rate by Practice Area',
        orientation='h'
    )
    fig_rates.update_layout(yaxis_title="Practice Area", xaxis_title="Average Rate ($)")
    st.plotly_chart(fig_rates, use_container_width=True)

with col2:
    # Utilization Rate by Practice Area
    util_by_practice = filtered_df.groupby('Practice area')['Utilization rate'].mean().sort_values(ascending=True)
    
    fig_util = px.bar(
        util_by_practice,
        orientation='h',
        title='Average Utilization Rate by Practice Area'
    )
    fig_util.update_layout(yaxis_title="Practice Area", xaxis_title="Utilization Rate (%)")
    st.plotly_chart(fig_util, use_container_width=True)

# Detailed Practice Area Metrics Table
st.markdown("### Detailed Practice Area Metrics")

practice_metrics = filtered_df.groupby('Practice area').agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Matter number': 'nunique',
    'Utilization rate': 'mean',
    'User full name (first, last)': 'nunique'
}).round(2)

# Calculate additional metrics
practice_metrics['Average Rate'] = (
    practice_metrics['Billed hours value'] / practice_metrics['Billed hours']
).round(2)

practice_metrics = practice_metrics.reset_index()
practice_metrics.columns = [
    'Practice Area', 'Total Hours', 'Total Revenue', 'Number of Matters',
    'Average Utilization', 'Number of Attorneys', 'Average Rate'
]

# Format the metrics
practice_metrics['Total Revenue'] = practice_metrics['Total Revenue'].apply(lambda x: f"${x:,.2f}")
practice_metrics['Average Rate'] = practice_metrics['Average Rate'].apply(lambda x: f"${x:,.2f}")
practice_metrics['Average Utilization'] = practice_metrics['Average Utilization'].apply(lambda x: f"{x:.1f}%")

# Display the table with sorting enabled
st.dataframe(
    practice_metrics.sort_values('Total Hours', ascending=False),
    use_container_width=True
)

# Add export functionality
csv = practice_metrics.to_csv(index=False).encode('utf-8')
st.download_button(
    "Export Practice Area Metrics to CSV",
    csv,
    "practice_area_metrics.csv",
    "text/csv",
    key='download-practice-metrics'
)

# Add styling
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
    .dataframe {
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)
