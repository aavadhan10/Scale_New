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

# Key Attorney Metrics
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

# Client Relationships
st.markdown("### Attorney-Client Relationships")
col1, col2 = st.columns(2)

with col1:
    # Top Attorney-Client Pairs by Revenue
    attorney_client_revenue = filtered_df.groupby(['User full name (first, last)', 'Company name']).agg({
        'Billed hours value': 'sum'
    }).reset_index()
    
    top_pairs = attorney_client_revenue.nlargest(10, 'Billed hours value')
    
    fig_top_pairs = px.bar(
        top_pairs,
        x='Billed hours value',
        y='User full name (first, last)',
        text='Company name',
        title='Top 10 Attorney-Client Relationships by Revenue',
        orientation='h'
    )
    fig_top_pairs.update_traces(textposition='inside')
    st.plotly_chart(fig_top_pairs, use_container_width=True)

with col2:
    # Client Count by Attorney Level
    client_count_by_level = filtered_df.groupby(['Attorney level', 'Company name']).size().reset_index(name='count')
    client_count_summary = client_count_by_level.groupby('Attorney level').size().reset_index(name='Number of Clients')
    
    fig_client_count = px.pie(
        client_count_summary,
        values='Number of Clients',
        names='Attorney level',
        title='Client Distribution by Attorney Level'
    )
    st.plotly_chart(fig_client_count, use_container_width=True)

# Client Portfolio Analysis
st.markdown("### Client Portfolio Analysis")
col1, col2 = st.columns(2)

with col1:
    # Average Client Value by Attorney
    avg_client_value = filtered_df.groupby(['User full name (first, last)', 'Company name']).agg({
        'Billed hours value': 'sum'
    }).reset_index().groupby('User full name (first, last)').agg({
        'Billed hours value': 'mean'
    }).round(2).nlargest(10, 'Billed hours value')
    
    fig_avg_value = px.bar(
        avg_client_value,
        orientation='h',
        title='Top 10 Attorneys by Average Client Value'
    )
    st.plotly_chart(fig_avg_value, use_container_width=True)

with col2:
    # Client Count per Attorney
    client_count_per_attorney = filtered_df.groupby('User full name (first, last)')['Company name'].nunique().nlargest(10)
    
    fig_client_count = px.bar(
        client_count_per_attorney,
        orientation='h',
        title='Top 10 Attorneys by Number of Clients'
    )
    st.plotly_chart(fig_client_count, use_container_width=True)

# Practice Area Expertise
st.markdown("### Practice Area Expertise")
col1, col2 = st.columns(2)

with col1:
    # Practice Area Specialization
    practice_specialization = filtered_df.groupby(['User full name (first, last)', 'Practice area']).agg({
        'Billed hours': 'sum'
    }).reset_index()
    
    top_attorneys = practice_specialization.groupby('User full name (first, last)')['Billed hours'].sum().nlargest(10).index
    practice_specialization_filtered = practice_specialization[
        practice_specialization['User full name (first, last)'].isin(top_attorneys)
    ]
    
    fig_specialization = px.bar(
        practice_specialization_filtered,
        x='User full name (first, last)',
        y='Billed hours',
        color='Practice area',
        title='Practice Area Distribution - Top 10 Attorneys',
        barmode='stack'
    )
    fig_specialization.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_specialization, use_container_width=True)

with col2:
    # Attorney Level Practice Distribution
    level_practice_dist = filtered_df.groupby(['Attorney level', 'Practice area']).agg({
        'Billed hours': 'sum'
    }).reset_index()
    
    fig_level_practice = px.sunburst(
        level_practice_dist,
        path=['Attorney level', 'Practice area'],
        values='Billed hours',
        title='Practice Area Distribution by Attorney Level'
    )
    st.plotly_chart(fig_level_practice, use_container_width=True)

# Performance Heatmap
st.markdown("### Performance Heatmap")

# Create performance metrics for top attorneys
top_attorneys_list = filtered_df.groupby('User full name (first, last)')['Billed hours value'].sum().nlargest(15).index

performance_metrics = filtered_df[
    filtered_df['User full name (first, last)'].isin(top_attorneys_list)
].pivot_table(
    index='User full name (first, last)',
    columns='Activity month',
    values='Utilization rate',
    aggfunc='mean'
)

# Convert month numbers to names
performance_metrics.columns = [calendar.month_name[int(m)] for m in performance_metrics.columns]

fig_heatmap = px.imshow(
    performance_metrics,
    title='Monthly Utilization Rate - Top 15 Attorneys',
    labels=dict(x="Month", y="Attorney", color="Utilization Rate"),
    aspect='auto',
    color_continuous_scale='RdYlBu_r'
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Workload Distribution
st.markdown("### Workload Analysis")
col1, col2 = st.columns(2)

with col1:
    # Matter Count Distribution
    matter_dist = filtered_df.groupby(['Attorney level', 'User full name (first, last)'])['Matter number'].nunique().reset_index()
    
    fig_matter_dist = px.box(
        matter_dist,
        x='Attorney level',
        y='Matter number',
        title='Matter Count Distribution by Attorney Level',
        points='all'
    )
    st.plotly_chart(fig_matter_dist, use_container_width=True)

with col2:
    # Hours Distribution
    hours_dist = filtered_df.groupby(['Attorney level', 'User full name (first, last)'])['Billed hours'].sum().reset_index()
    
    fig_hours_dist = px.box(
        hours_dist,
        x='Attorney level',
        y='Billed hours',
        title='Hours Distribution by Attorney Level',
        points='all'
    )
    st.plotly_chart(fig_hours_dist, use_container_width=True)

# Detailed Attorney Metrics Table
st.markdown("### Detailed Attorney Metrics")

attorney_detail_metrics = filtered_df.groupby('User full name (first, last)').agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Matter number': 'nunique',
    'Utilization rate': 'mean',
    'User rate': 'first',
    'Attorney level': 'first',
    'Company name': 'nunique'  # Added client count
}).round(2)

# Calculate additional metrics with zero division handling
attorney_detail_metrics['Revenue per Hour'] = (
    attorney_detail_metrics['Billed hours value'] / 
    attorney_detail_metrics['Billed hours'].replace(0, float('nan'))
).round(2)

attorney_detail_metrics = attorney_detail_metrics.reset_index()
attorney_detail_metrics.columns = [
    'Attorney Name', 'Total Hours', 'Total Revenue', 'Number of Matters',
    'Average Utilization', 'Standard Rate', 'Attorney Level', 'Number of Clients', 'Effective Rate'
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

# Summary Statistics
st.markdown("### Summary Statistics by Attorney Level")

summary_stats = filtered_df.groupby('Attorney level').agg({
    'Billed hours': ['sum', 'mean', 'std'],
    'Billed hours value': ['sum', 'mean'],
    'Utilization rate': ['mean', 'std'],
    'User full name (first, last)': 'nunique',
    'Company name': 'nunique',
    'Matter number': 'nunique'
}).round(2)

# Flatten column names
summary_stats.columns = [
    f"{col[0]}_{col[1]}" for col in summary_stats.columns
]

summary_stats = summary_stats.reset_index()
summary_stats.columns = [
    'Attorney Level', 'Total Hours', 'Avg Hours per Attorney', 'Hours Std Dev',
    'Total Revenue', 'Avg Revenue per Attorney', 'Avg Utilization', 'Utilization Std Dev',
    'Number of Attorneys', 'Number of Clients', 'Number of Matters'
]

# Format the metrics
summary_stats['Total Revenue'] = summary_stats['Total Revenue'].apply(lambda x: f"${x:,.2f}")
summary_stats['Avg Revenue per Attorney'] = summary_stats['Avg Revenue per Attorney'].apply(lambda x: f"${x:,.2f}")
summary_stats['Avg Utilization'] = summary_stats['Avg Utilization'].apply(lambda x: f"{x:.1f}%")
summary_stats['Utilization Std Dev'] = summary_stats['Utilization Std Dev'].apply(lambda x: f"{x:.1f}%")

# Display the summary statistics
st.dataframe(summary_stats, use_container_width=True)

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
    .stDataFrame {
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Footer with last update time
st.markdown("---")
st.markdown(f"*Last data refresh: Wednesday Feb 19, 2025*")
