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
st.set_page_config(page_title="Attorney Analysis - Scale LLP Dashboard", layout="wide")

# Load data and create filters
df = load_data()
create_sidebar_filters()
filtered_df = apply_filters(df)

# Page Header
st.title("Attorney Analysis")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Key Attorney Metrics with zero division handling
st.markdown("### Key Attorney Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_attorneys = filtered_df['User full name (first, last)'].nunique()
    prev_attorneys = max(total_attorneys * 0.95, 1)  # Prevent zero division
    delta = ((total_attorneys - prev_attorneys) / prev_attorneys) * 100 if prev_attorneys > 0 else 0
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Attorneys",
        f"{total_attorneys:,}",
        f"{arrow} {delta:.1f}%"
    )

with col2:
    avg_utilization = filtered_df['Utilization rate'].mean()
    prev_util = max(avg_utilization * 0.95, 1)  # Prevent zero division
    delta = ((avg_utilization - prev_util) / prev_util) * 100 if prev_util > 0 else 0
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Average Utilization",
        f"{avg_utilization:.1f}%",
        f"{arrow} {delta:.1f}%"
    )

with col3:
    avg_revenue_per_attorney = filtered_df.groupby('User full name (first, last)')['Billed hours value'].sum().mean()
    prev_revenue = max(avg_revenue_per_attorney * 0.95, 1)  # Prevent zero division
    delta = ((avg_revenue_per_attorney - prev_revenue) / prev_revenue) * 100 if prev_revenue > 0 else 0
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Avg Revenue per Attorney",
        f"${avg_revenue_per_attorney:,.2f}",
        f"{arrow} {delta:.1f}%"
    )

with col4:
    avg_hours_per_attorney = filtered_df.groupby('User full name (first, last)')['Billed hours'].sum().mean()
    prev_hours = max(avg_hours_per_attorney * 0.95, 1)  # Prevent zero division
    delta = ((avg_hours_per_attorney - prev_hours) / prev_hours) * 100 if prev_hours > 0 else 0
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Avg Hours per Attorney",
        f"{avg_hours_per_attorney:.1f}",
        f"{arrow} {delta:.1f}%"
    )

# Attorney Performance Matrix
st.markdown("### Attorney Performance Matrix")
attorney_metrics = filtered_df.groupby('User full name (first, last)').agg({
    'Billed hours': 'sum',
    'Utilization rate': 'mean',
    'Billed hours value': 'sum',
    'Attorney level': 'first'
}).reset_index()

# Handle any null or infinite values
attorney_metrics = attorney_metrics.fillna(0)
attorney_metrics = attorney_metrics.replace([float('inf'), float('-inf')], 0)

fig_matrix = px.scatter(
    attorney_metrics,
    x='Billed hours',
    y='Utilization rate',
    size='Billed hours value',
    color='Attorney level',
    hover_name='User full name (first, last)',
    title='Attorney Performance Matrix',
    labels={
        'Billed hours': 'Total Billed Hours',
        'Utilization rate': 'Utilization Rate (%)',
        'Billed hours value': 'Revenue',
        'Attorney level': 'Attorney Level'
    }
)
st.plotly_chart(fig_matrix, use_container_width=True)

# Attorney Level Analysis
st.markdown("### Analysis by Attorney Level")
col1, col2 = st.columns(2)

with col1:
    # Revenue by Attorney Level
    level_revenue = filtered_df.groupby('Attorney level').agg({
        'Billed hours value': 'sum'
    }).reset_index()
    
    fig_level_revenue = px.pie(
        level_revenue,
        values='Billed hours value',
        names='Attorney level',
        title='Revenue Distribution by Attorney Level'
    )
    st.plotly_chart(fig_level_revenue, use_container_width=True)

with col2:
    # Utilization by Attorney Level
    level_util = filtered_df.groupby('Attorney level').agg({
        'Utilization rate': 'mean'
    }).reset_index()
    
    fig_level_util = px.bar(
        level_util,
        x='Attorney level',
        y='Utilization rate',
        title='Average Utilization Rate by Attorney Level'
    )
    st.plotly_chart(fig_level_util, use_container_width=True)

# Attorney Utilization Trends
st.markdown("### Attorney Utilization Trends")
# Get top 5 attorneys by revenue for trend analysis
top_5_attorneys = filtered_df.groupby('User full name (first, last)')['Billed hours value'].sum().nlargest(5).index

attorney_trends = filtered_df[
    filtered_df['User full name (first, last)'].isin(top_5_attorneys)
].groupby(['Activity Year', 'Activity month', 'User full name (first, last)']).agg({
    'Utilization rate': 'mean'
}).reset_index()

# Fix date handling
attorney_trends['Date'] = pd.to_datetime(
    attorney_trends['Activity Year'].astype(int).astype(str) + '-' + 
    attorney_trends['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
)

fig_trends = px.line(
    attorney_trends,
    x='Date',
    y='Utilization rate',
    color='User full name (first, last)',
    title='Utilization Rate Trends - Top 5 Attorneys',
    markers=True
)
fig_trends.update_layout(
    xaxis_title="Date",
    yaxis_title="Utilization Rate (%)",
    hovermode='x unified'
)
st.plotly_chart(fig_trends, use_container_width=True)

# Performance Metrics by Attorney Level
st.markdown("### Performance Metrics by Attorney Level")
col1, col2 = st.columns(2)

with col1:
    level_hours = filtered_df.groupby(['Attorney level', 'Activity Year', 'Activity month']).agg({
        'Billed hours': 'sum'
    }).reset_index()
    
    # Fix date handling
    level_hours['Date'] = pd.to_datetime(
        level_hours['Activity Year'].astype(int).astype(str) + '-' + 
        level_hours['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
    )
    
    fig_level_hours = px.line(
        level_hours,
        x='Date',
        y='Billed hours',
        color='Attorney level',
        title='Monthly Billed Hours by Attorney Level',
        markers=True
    )
    st.plotly_chart(fig_level_hours, use_container_width=True)

with col2:
    level_revenue = filtered_df.groupby(['Attorney level', 'Activity Year', 'Activity month']).agg({
        'Billed hours value': 'sum'
    }).reset_index()
    
    # Fix date handling
    level_revenue['Date'] = pd.to_datetime(
        level_revenue['Activity Year'].astype(int).astype(str) + '-' + 
        level_revenue['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
    )
    
    fig_level_revenue = px.line(
        level_revenue,
        x='Date',
        y='Billed hours value',
        color='Attorney level',
        title='Monthly Revenue by Attorney Level',
        markers=True
    )
    st.plotly_chart(fig_level_revenue, use_container_width=True)

# Detailed Attorney Metrics Table
st.markdown("### Detailed Attorney Metrics")

attorney_detail_metrics = filtered_df.groupby('User full name (first, last)').agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Matter number': 'nunique',
    'Utilization rate': 'mean',
    'User rate': 'first',
    'Attorney level': 'first'
}).round(2)

# Calculate additional metrics with zero division handling
attorney_detail_metrics['Revenue per Hour'] = (
    attorney_detail_metrics['Billed hours value'] / 
    attorney_detail_metrics['Billed hours'].replace(0, float('nan'))
).round(2)

attorney_detail_metrics = attorney_detail_metrics.reset_index()
attorney_detail_metrics.columns = [
    'Attorney Name', 'Total Hours', 'Total Revenue', 'Number of Matters',
    'Average Utilization', 'Standard Rate', 'Attorney Level', 'Effective Rate'
]

# Format the metrics
attorney_detail_metrics['Total Revenue'] = attorney_detail_metrics['Total Revenue'].apply(lambda x: f"${x:,.2f}")
attorney_detail_metrics['Standard Rate'] = attorney_detail_metrics['Standard Rate'].apply(lambda x: f"${x:,.2f}")
attorney_detail_metrics['Effective Rate'] = attorney_detail_metrics['Effective Rate'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A")
attorney_detail_metrics['Average Utilization'] = attorney_detail_metrics['Average Utilization'].apply(lambda x: f"{x:.1f}%")

# Display the table with sorting enabled
st.dataframe(
    attorney_detail_metrics.sort_values('Total Hours', ascending=False),
    use_container_width=True
)

# Add export functionality
csv = attorney_detail_metrics.to_csv(index=False).encode('utf-8')
st.download_button(
    "Export Attorney Metrics to CSV",
    csv,
    "attorney_metrics.csv",
    "text/csv",
    key='download-attorney-metrics'
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
