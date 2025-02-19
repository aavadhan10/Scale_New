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
st.set_page_config(page_title="Overview - Scale LLP Dashboard", layout="wide")

# Load data and create filters
df = load_data()
create_sidebar_filters()
filtered_df = apply_filters(df)

# Page Header
st.title("Overview")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Key Performance Metrics
st.markdown("### Key Performance Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_billable_hours = filtered_df['Billed & Unbilled hours'].sum()
    prev_total = total_billable_hours * 0.95
    delta = ((total_billable_hours - prev_total) / prev_total) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Billable Hours",
        f"{total_billable_hours:,.1f}",
        f"{arrow} {delta:.1f}%"
    )

with col2:
    total_billed = filtered_df['Billed hours'].sum()
    prev_billed = total_billed * 0.95
    delta = ((total_billed - prev_billed) / prev_billed) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Billed Hours",
        f"{total_billed:,.1f}",
        f"{arrow} {delta:.1f}%"
    )

with col3:
    avg_utilization = filtered_df['Utilization rate'].mean()
    prev_util = avg_utilization * 0.95
    delta = ((avg_utilization - prev_util) / prev_util) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Average Utilization",
        f"{avg_utilization:.1f}%",
        f"{arrow} {delta:.1f}%"
    )

with col4:
    total_revenue = filtered_df['Billed hours value'].sum()
    prev_revenue = total_revenue * 0.95
    delta = ((total_revenue - prev_revenue) / prev_revenue) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Revenue",
        f"${total_revenue:,.2f}",
        f"{arrow} {delta:.1f}%"
    )

# Hours Distribution and Trends
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
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_hours, use_container_width=True)

with col2:
    # Monthly Billable Hours Trend
    monthly_data = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
        'Billed hours': 'sum'
    }).reset_index()
    
    monthly_data['Date'] = pd.to_datetime(
        monthly_data['Activity Year'].astype(int).astype(str) + '-' + 
        monthly_data['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
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
    # Revenue by Practice Area
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
    # Utilization by Practice Area
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
        y=top_attorneys.index,
        x='Billed hours value',
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
        y=top_utilization.index,
        x='Utilization rate',
        title='Top 10 Attorneys by Utilization Rate',
        orientation='h'
    )
    st.plotly_chart(fig_top_util, use_container_width=True)

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
</style>
""", unsafe_allow_html=True)
