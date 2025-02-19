import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
from plotly.subplots import make_subplots
import sys
import os

# Import functions from Home.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Home import load_data, apply_filters, create_sidebar_filters

# Page config
st.set_page_config(page_title="Trending - Scale LLP Dashboard", layout="wide")

# Load data and create filters
df = load_data()
create_sidebar_filters(df)  # Pass df here
filtered_df = apply_filters(df)

# Add date range note
if st.session_state.filters['start_date'] and st.session_state.filters['end_date']:
    st.markdown(f"*Showing data from {st.session_state.filters['start_date'].strftime('%B %d, %Y')} to {st.session_state.filters['end_date'].strftime('%B %d, %Y')}*")

# Page Header
st.title("Trending Analysis")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Overall Performance Trends
st.markdown("### Overall Performance Trends")

# Create monthly trends dataframe
monthly_trends = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Utilization rate': 'mean',
    'Matter number': 'nunique',
    'Company name': 'nunique'
}).reset_index()

# Fix date handling
monthly_trends['Date'] = pd.to_datetime(
    monthly_trends['Activity Year'].astype(int).astype(str) + '-' + 
    monthly_trends['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
)

# Create subplot with multiple metrics
fig = make_subplots(
    rows=3, cols=1,
    subplot_titles=('Revenue Trend', 'Utilization Rate Trend', 'Billable Hours Trend'),
    vertical_spacing=0.1
)

# Revenue trend
fig.add_trace(
    go.Scatter(
        x=monthly_trends['Date'],
        y=monthly_trends['Billed hours value'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#1f77b4')
    ),
    row=1, col=1
)

# Utilization trend
fig.add_trace(
    go.Scatter(
        x=monthly_trends['Date'],
        y=monthly_trends['Utilization rate'],
        mode='lines+markers',
        name='Utilization Rate',
        line=dict(color='#2ca02c')
    ),
    row=2, col=1
)

# Billable hours trend
fig.add_trace(
    go.Scatter(
        x=monthly_trends['Date'],
        y=monthly_trends['Billed hours'],
        mode='lines+markers',
        name='Billable Hours',
        line=dict(color='#ff7f0e')
    ),
    row=3, col=1
)

fig.update_layout(height=800, showlegend=True, title_text="Key Metrics Trends")
st.plotly_chart(fig, use_container_width=True)

# Year-over-Year Comparison
st.markdown("### Year-over-Year Comparison")
col1, col2 = st.columns(2)

with col1:
    # YoY Revenue Comparison
    yearly_revenue = filtered_df.groupby('Activity Year').agg({
        'Billed hours value': 'sum'
    }).reset_index()
    
    fig_yoy_revenue = px.bar(
        yearly_revenue,
        x='Activity Year',
        y='Billed hours value',
        title='Annual Revenue Comparison',
        labels={'Billed hours value': 'Revenue ($)'}
    )
    st.plotly_chart(fig_yoy_revenue, use_container_width=True)

with col2:
    # YoY Utilization Comparison
    yearly_util = filtered_df.groupby('Activity Year').agg({
        'Utilization rate': 'mean'
    }).reset_index()
    
    fig_yoy_util = px.bar(
        yearly_util,
        x='Activity Year',
        y='Utilization rate',
        title='Annual Utilization Rate Comparison',
        labels={'Utilization rate': 'Utilization Rate (%)'}
    )
    st.plotly_chart(fig_yoy_util, use_container_width=True)

# Practice Area Trends
st.markdown("### Practice Area Trends")

# Create practice area trends
practice_trends = filtered_df.groupby(['Activity Year', 'Activity month', 'Practice area']).agg({
    'Billed hours value': 'sum'
}).reset_index()

practice_trends['Date'] = pd.to_datetime(
    practice_trends['Activity Year'].astype(int).astype(str) + '-' + 
    practice_trends['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
)

# Top 5 practice areas
top_practices = filtered_df.groupby('Practice area')['Billed hours value'].sum().nlargest(5).index

practice_trends_filtered = practice_trends[practice_trends['Practice area'].isin(top_practices)]

fig_practice_trends = px.line(
    practice_trends_filtered,
    x='Date',
    y='Billed hours value',
    color='Practice area',
    title='Revenue Trends by Practice Area (Top 5)',
    markers=True
)
st.plotly_chart(fig_practice_trends, use_container_width=True)

# Attorney Level Trends
st.markdown("### Attorney Level Trends")

# Create attorney level trends
level_trends = filtered_df.groupby(['Activity Year', 'Activity month', 'Attorney level']).agg({
    'Billed hours': 'sum',
    'Utilization rate': 'mean'
}).reset_index()

level_trends['Date'] = pd.to_datetime(
    level_trends['Activity Year'].astype(int).astype(str) + '-' + 
    level_trends['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
)

col1, col2 = st.columns(2)

with col1:
    # Hours by Attorney Level
    fig_level_hours = px.line(
        level_trends,
        x='Date',
        y='Billed hours',
        color='Attorney level',
        title='Billable Hours by Attorney Level',
        markers=True
    )
    st.plotly_chart(fig_level_hours, use_container_width=True)

with col2:
    # Utilization by Attorney Level
    fig_level_util = px.line(
        level_trends,
        x='Date',
        y='Utilization rate',
        color='Attorney level',
        title='Utilization Rate by Attorney Level',
        markers=True
    )
    st.plotly_chart(fig_level_util, use_container_width=True)

# Client Growth Analysis
st.markdown("### Client Growth Analysis")

# Monthly client metrics
client_trends = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
    'Company name': 'nunique',
    'Matter number': 'nunique'
}).reset_index()

client_trends['Date'] = pd.to_datetime(
    client_trends['Activity Year'].astype(int).astype(str) + '-' + 
    client_trends['Activity month'].astype(int).astype(str).str.zfill(2) + '-01'
)

# Create subplot for client metrics
fig_clients = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Active Clients per Month', 'Active Matters per Month'),
    horizontal_spacing=0.1
)

# Active clients trend
fig_clients.add_trace(
    go.Scatter(
        x=client_trends['Date'],
        y=client_trends['Company name'],
        mode='lines+markers',
        name='Active Clients'
    ),
    row=1, col=1
)

# Active matters trend
fig_clients.add_trace(
    go.Scatter(
        x=client_trends['Date'],
        y=client_trends['Matter number'],
        mode='lines+markers',
        name='Active Matters'
    ),
    row=1, col=2
)

fig_clients.update_layout(height=400, showlegend=True, title_text="Client and Matter Growth Trends")
st.plotly_chart(fig_clients, use_container_width=True)

# Quarterly Performance Table
st.markdown("### Quarterly Performance Metrics")

quarterly_metrics = filtered_df.groupby(['Activity Year', 'Activity quarter']).agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Utilization rate': 'mean',
    'Company name': 'nunique',
    'Matter number': 'nunique'
}).round(2)

quarterly_metrics = quarterly_metrics.reset_index()
quarterly_metrics['Quarter'] = quarterly_metrics.apply(
    lambda x: f"Q{int(x['Activity quarter'])} {int(x['Activity Year'])}",
    axis=1
)

# Format metrics
quarterly_metrics_display = quarterly_metrics.copy()
quarterly_metrics_display['Billed hours value'] = quarterly_metrics_display['Billed hours value'].apply(
    lambda x: f"${x:,.2f}"
)
quarterly_metrics_display['Utilization rate'] = quarterly_metrics_display['Utilization rate'].apply(
    lambda x: f"{x:.1f}%"
)

quarterly_metrics_display = quarterly_metrics_display[[
    'Quarter', 'Billed hours', 'Billed hours value', 'Utilization rate',
    'Company name', 'Matter number'
]]
quarterly_metrics_display.columns = [
    'Quarter', 'Billable Hours', 'Revenue', 'Utilization Rate',
    'Active Clients', 'Active Matters'
]

st.dataframe(
    quarterly_metrics_display.sort_values('Quarter', ascending=False),
    use_container_width=True
)

# Add export functionality
csv = quarterly_metrics_display.to_csv(index=False).encode('utf-8')
st.download_button(
    "Export Quarterly Metrics to CSV",
    csv,
    "quarterly_metrics.csv",
    "text/csv",
    key='download-quarterly-metrics'
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
