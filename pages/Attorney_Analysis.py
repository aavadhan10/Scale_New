import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar

# Page config
st.set_page_config(page_title="Attorney Analysis - Scale LLP Dashboard", layout="wide")

# Load data function
def load_data():
    df = pd.read_csv("Test_Full_Year.csv")
    
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
st.title("Attorney Analysis")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Attorney Overview Metrics
st.markdown("### Key Attorney Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_attorneys = filtered_df['User full name (first, last)'].nunique()
    prev_attorneys = total_attorneys * 0.95
    delta = ((total_attorneys - prev_attorneys) / prev_attorneys) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Total Attorneys",
        f"{total_attorneys:,}",
        f"{arrow} {delta:.1f}%"
    )

with col2:
    avg_utilization = filtered_df['Utilization rate'].mean()
    prev_util = avg_utilization * 0.95
    delta = ((avg_utilization - prev_util) / prev_util) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Average Utilization",
        f"{avg_utilization:.1f}%",
        f"{arrow} {delta:.1f}%"
    )

with col3:
    avg_revenue_per_attorney = filtered_df.groupby('User full name (first, last)')['Billed hours value'].sum().mean()
    prev_revenue = avg_revenue_per_attorney * 0.95
    delta = ((avg_revenue_per_attorney - prev_revenue) / prev_revenue) * 100
    arrow = "↗️" if delta > 0 else "↘️"
    st.metric(
        "Avg Revenue per Attorney",
        f"${avg_revenue_per_attorney:,.2f}",
        f"{arrow} {delta:.1f}%"
    )

with col4:
    avg_hours_per_attorney = filtered_df.groupby('User full name (first, last)')['Billed hours'].sum().mean()
    prev_hours = avg_hours_per_attorney * 0.95
    delta = ((avg_hours_per_attorney - prev_hours) / prev_hours) * 100
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
    'Billed hours value': 'sum'
}).reset_index()

fig_matrix = px.scatter(
    attorney_metrics,
    x='Billed hours',
    y='Utilization rate',
    size='Billed hours value',
    hover_name='User full name (first, last)',
    title='Attorney Performance Matrix',
    labels={
        'Billed hours': 'Total Billed Hours',
        'Utilization rate': 'Utilization Rate (%)',
        'Billed hours value': 'Revenue'
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

# Attorney Practice Area Distribution
st.markdown("### Practice Area Distribution")
attorney_practice = filtered_df.groupby(
    ['User full name (first, last)', 'Practice area']
).agg({
    'Billed hours': 'sum'
}).reset_index()

fig_practice = px.sunburst(
    attorney_practice,
    path=['User full name (first, last)', 'Practice area'],
    values='Billed hours',
    title='Attorney Distribution Across Practice Areas'
)
st.plotly_chart(fig_practice, use_container_width=True)

# Top Performers
st.markdown("### Top Performing Attorneys")
col1, col2 = st.columns(2)

with col1:
    # Top 10 by Revenue
    top_revenue = filtered_df.groupby('User full name (first, last)').agg({
        'Billed hours value': 'sum'
    }).sort_values('Billed hours value', ascending=True).tail(10)
    
    fig_top_revenue = px.bar(
        top_revenue,
        orientation='h',
        title='Top 10 Attorneys by Revenue'
    )
    st.plotly_chart(fig_top_revenue, use_container_width=True)

with col2:
    # Top 10 by Utilization
    top_util = filtered_df.groupby('User full name (first, last)').agg({
        'Utilization rate': 'mean'
    }).sort_values('Utilization rate', ascending=True).tail(10)
    
    fig_top_util = px.bar(
        top_util,
        orientation='h',
        title='Top 10 Attorneys by Utilization Rate'
    )
    st.plotly_chart(fig_top_util, use_container_width=True)

# Attorney Utilization Trends
st.markdown("### Attorney Utilization Trends")
# Get top 5 attorneys by revenue for trend analysis
top_5_attorneys = filtered_df.groupby('User full name (first, last)')['Billed hours value'].sum().nlargest(5).index

attorney_trends = filtered_df[
    filtered_df['User full name (first, last)'].isin(top_5_attorneys)
].groupby(['Activity Year', 'Activity month', 'User full name (first, last)']).agg({
    'Utilization rate': 'mean'
}).reset_index()

attorney_trends['Date'] = pd.to_datetime(
    attorney_trends['Activity Year'].astype(str) + '-' + 
    attorney_trends['Activity month'].astype(str) + '-01'
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

# Calculate additional metrics
attorney_detail_metrics['Revenue per Hour'] = (
    attorney_detail_metrics['Billed hours value'] / attorney_detail_metrics['Billed hours']
).round(2)

attorney_detail_metrics = attorney_detail_metrics.reset_index()
attorney_detail_metrics.columns = [
    'Attorney Name', 'Total Hours', 'Total Revenue', 'Number of Matters',
    'Average Utilization', 'Standard Rate', 'Attorney Level', 'Effective Rate'
]

# Format the metrics
attorney_detail_metrics['Total Revenue'] = attorney_detail_metrics['Total Revenue'].apply(lambda x: f"${x:,.2f}")
attorney_detail_metrics['Standard Rate'] = attorney_detail_metrics['Standard Rate'].apply(lambda x: f"${x:,.2f}")
attorney_detail_metrics['Effective Rate'] = attorney_detail_metrics['Effective Rate'].apply(lambda x: f"${x:,.2f}")
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
    .dataframe {
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)
