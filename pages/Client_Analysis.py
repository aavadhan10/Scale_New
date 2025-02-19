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
st.set_page_config(page_title="Client Analysis - Scale LLP Dashboard", layout="wide")

# Load data and create filters
df = load_data()
create_sidebar_filters(df)  # Pass df here
filtered_df = apply_filters(df)

# Add date range note
if st.session_state.filters['start_date'] and st.session_state.filters['end_date']:
    st.markdown(f"*Showing data from {st.session_state.filters['start_date'].strftime('%B %d, %Y')} to {st.session_state.filters['end_date'].strftime('%B %d, %Y')}*")


# Page Header
st.title("Client Analysis")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Key Client Metrics
st.markdown("### Key Client Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_clients = filtered_df['Company name'].nunique()
    prev_clients = total_clients * 0.95
    delta = ((total_clients - prev_clients) / prev_clients) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Active Clients",
        f"{total_clients:,}",
        f"{arrow} {delta:.1f}%"
    )

with col2:
    avg_revenue_per_client = filtered_df.groupby('Company name')['Billed hours value'].sum().mean()
    prev_avg = avg_revenue_per_client * 0.95
    delta = ((avg_revenue_per_client - prev_avg) / prev_avg) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Avg Revenue per Client",
        f"${avg_revenue_per_client:,.2f}",
        f"{arrow} {delta:.1f}%"
    )

with col3:
    avg_hours_per_client = filtered_df.groupby('Company name')['Billed hours'].sum().mean()
    prev_hours = avg_hours_per_client * 0.95
    delta = ((avg_hours_per_client - prev_hours) / prev_hours) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Avg Hours per Client",
        f"{avg_hours_per_client:.1f}",
        f"{arrow} {delta:.1f}%"
    )

with col4:
    total_matters = filtered_df['Matter number'].nunique()
    prev_matters = total_matters * 0.95
    delta = ((total_matters - prev_matters) / prev_matters) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Active Matters",
        f"{total_matters:,}",
        f"{arrow} {delta:.1f}%"
    )

# Top Clients Analysis
st.markdown("### Top Clients Overview")
col1, col2 = st.columns(2)

with col1:
    # Top 10 Clients by Revenue
    top_clients_revenue = filtered_df.groupby('Company name').agg({
        'Billed hours value': 'sum'
    }).sort_values('Billed hours value', ascending=True).tail(10)
    
    fig_top_revenue = px.bar(
        top_clients_revenue,
        x='Billed hours value',
        y=top_clients_revenue.index,
        title='Top 10 Clients by Revenue',
        orientation='h'
    )
    fig_top_revenue.update_layout(yaxis_title="Client", xaxis_title="Revenue ($)")
    st.plotly_chart(fig_top_revenue, use_container_width=True)

with col2:
    # Top 10 Clients by Hours
    top_clients_hours = filtered_df.groupby('Company name').agg({
        'Billed hours': 'sum'
    }).sort_values('Billed hours', ascending=True).tail(10)
    
    fig_top_hours = px.bar(
        top_clients_hours,
        x='Billed hours',
        y=top_clients_hours.index,
        title='Top 10 Clients by Billed Hours',
        orientation='h'
    )
    fig_top_hours.update_layout(yaxis_title="Client", xaxis_title="Billed Hours")
    st.plotly_chart(fig_top_hours, use_container_width=True)

# Client Practice Area Distribution
st.markdown("### Client Distribution by Practice Area")
client_practice = filtered_df.groupby(['Practice area', 'Company name']).agg({
    'Billed hours': 'sum'
}).reset_index()

fig_practice = px.treemap(
    client_practice,
    path=['Practice area', 'Company name'],
    values='Billed hours',
    title='Client Distribution Across Practice Areas'
)
st.plotly_chart(fig_practice, use_container_width=True)

# Client Revenue Trends
st.markdown("### Client Revenue Trends")

# Get top 5 clients for trend analysis
top_5_clients = filtered_df.groupby('Company name')['Billed hours value'].sum().nlargest(5).index

try:
    # Prepare trend data
    client_trends = filtered_df[filtered_df['Company name'].isin(top_5_clients)].groupby(
        ['Activity date', 'Company name']
    ).agg({
        'Billed hours value': 'sum'
    }).reset_index()

    # Sort by date
    client_trends = client_trends.sort_values('Activity date')

    fig_trends = px.line(
        client_trends,
        x='Activity date',
        y='Billed hours value',
        color='Company name',
        title='Revenue Trends - Top 5 Clients',
        markers=True
    )
    fig_trends.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_trends, use_container_width=True)
except Exception as e:
    st.warning(f"Unable to display trend chart: {e}")
    
# Client Matter Analysis
st.markdown("### Client Matter Analysis")
col1, col2 = st.columns(2)

with col1:
    # Matters per Client
    matters_per_client = filtered_df.groupby('Company name')['Matter number'].nunique().sort_values(ascending=True).tail(10)
    
    fig_matters = px.bar(
        matters_per_client,
        orientation='h',
        title='Top 10 Clients by Number of Matters'
    )
    fig_matters.update_layout(yaxis_title="Client", xaxis_title="Number of Matters")
    st.plotly_chart(fig_matters, use_container_width=True)

with col2:
    # Average Rate by Client
    avg_rate_by_client = (
        filtered_df.groupby('Company name').agg({
            'Billed hours value': 'sum',
            'Billed hours': 'sum'
        })
    )
    avg_rate_by_client['Average Rate'] = avg_rate_by_client['Billed hours value'] / avg_rate_by_client['Billed hours']
    avg_rate_by_client = avg_rate_by_client.sort_values('Average Rate', ascending=True).tail(10)
    
    fig_rates = px.bar(
        avg_rate_by_client,
        y=avg_rate_by_client.index,
        x='Average Rate',
        title='Top 10 Clients by Average Hourly Rate',
        orientation='h'
    )
    fig_rates.update_layout(yaxis_title="Client", xaxis_title="Average Rate ($)")
    st.plotly_chart(fig_rates, use_container_width=True)

# Detailed Client Metrics Table
st.markdown("### Detailed Client Metrics")

client_metrics = filtered_df.groupby('Company name').agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Matter number': 'nunique',
    'Utilization rate': 'mean'
}).round(2)

# Calculate additional metrics
client_metrics['Average Hourly Rate'] = (
    client_metrics['Billed hours value'] / client_metrics['Billed hours']
).round(2)

client_metrics = client_metrics.reset_index()
client_metrics.columns = [
    'Client', 'Total Hours', 'Total Revenue', 'Number of Matters',
    'Average Utilization', 'Average Hourly Rate'
]

# Format the metrics
client_metrics['Total Revenue'] = client_metrics['Total Revenue'].apply(lambda x: f"${x:,.2f}")
client_metrics['Average Hourly Rate'] = client_metrics['Average Hourly Rate'].apply(lambda x: f"${x:,.2f}")
client_metrics['Average Utilization'] = client_metrics['Average Utilization'].apply(lambda x: f"{x:.1f}%")

# Display the table with sorting enabled
st.dataframe(
    client_metrics.sort_values('Total Hours', ascending=False),
    use_container_width=True
)

# Add export functionality
csv = client_metrics.to_csv(index=False).encode('utf-8')
st.download_button(
    "Export Client Metrics to CSV",
    csv,
    "client_metrics.csv",
    "text/csv",
    key='download-client-metrics'
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
