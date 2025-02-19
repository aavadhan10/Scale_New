import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar

# Set page config
st.set_page_config(page_title="Law Firm Analytics Dashboard", layout="wide")

# Load data function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Test_Full_Year.csv")
        df['Activity date'] = pd.to_datetime(df['Activity date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header('Filters')

# Time filters
st.sidebar.subheader('Time Filters')
date_filter_type = st.sidebar.radio(
    "Select Date Filter Type",
    ["Month/Quarter", "Custom Date Range"]
)

# Initialize filter variables
selected_months = None
selected_quarters = None
start_date = None
end_date = None
filter_level = None

if date_filter_type == "Month/Quarter":
    filter_level = st.sidebar.radio(
        "Filter by",
        ["Month", "Quarter"]
    )
    
    if filter_level == "Month":
        months = sorted(df['Activity month'].unique())
        selected_months = st.sidebar.multiselect(
            'Select Months',
            options=months,
            default=[months[0]] if len(months) > 0 else []
        )
    else:
        quarters = sorted(df['Activity quarter'].unique())
        selected_quarters = st.sidebar.multiselect(
            'Select Quarters',
            options=quarters,
            default=[quarters[0]] if len(quarters) > 0 else []
        )
else:
    min_date = df['Activity date'].min()
    max_date = df['Activity date'].max()
    start_date = st.sidebar.date_input('Start Date', min_date)
    end_date = st.sidebar.date_input('End Date', max_date)

# Other filters
selected_attorney = st.sidebar.multiselect(
    'Attorneys',
    options=sorted(df['User full name (first, last)'].unique())
)

selected_practice = st.sidebar.multiselect(
    'Practice Areas',
    options=sorted(df['Practice area'].dropna().unique())
)

selected_location = st.sidebar.multiselect(
    'Matter Locations',
    options=sorted(df['Matter location'].dropna().unique())
)

selected_status = st.sidebar.multiselect(
    'Matter Status',
    options=sorted(df['Matter status'].dropna().unique())
)

selected_client = st.sidebar.multiselect(
    'Clients',
    options=sorted(df['Company name'].dropna().unique())
)

def filter_data(df):
    filtered_df = df.copy()
    
    # Date filtering
    if date_filter_type == "Month/Quarter":
        if filter_level == "Month" and selected_months:
            filtered_df = filtered_df[filtered_df['Activity month'].isin(selected_months)]
        elif filter_level == "Quarter" and selected_quarters:
            filtered_df = filtered_df[filtered_df['Activity quarter'].isin(selected_quarters)]
    else:
        if start_date and end_date:
            filtered_df = filtered_df[
                (filtered_df['Activity date'].dt.date >= start_date) & 
                (filtered_df['Activity date'].dt.date <= end_date)
            ]
    
    # Other filters
    if selected_attorney:
        filtered_df = filtered_df[filtered_df['User full name (first, last)'].isin(selected_attorney)]
    if selected_practice:
        filtered_df = filtered_df[filtered_df['Practice area'].isin(selected_practice)]
    if selected_location:
        filtered_df = filtered_df[filtered_df['Matter location'].isin(selected_location)]
    if selected_status:
        filtered_df = filtered_df[filtered_df['Matter status'].isin(selected_status)]
    if selected_client:
        filtered_df = filtered_df[filtered_df['Company name'].isin(selected_client)]
    
    return filtered_df

# Apply filters
filtered_df = filter_data(df)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Client Analysis", "Attorney Analysis", "Practice Areas", "Trending"])

# Tab 1: Overview
with tab1:
    st.header('Key Performance Metrics')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_billable_hours = float(filtered_df['Billed & Unbilled hours'].sum())
        st.metric("Total Billable Hours", f"{total_billable_hours:,.1f}")

    with col2:
        total_billed_hours = float(filtered_df['Billed hours'].sum())
        st.metric("Billed Hours", f"{total_billed_hours:,.1f}")

    with col3:
        avg_utilization = float(filtered_df['Utilization rate'].mean())
        st.metric("Utilization Rate", f"{avg_utilization:.1f}%")

    with col4:
        total_billed_value = float(filtered_df['Billed hours value'].sum())
        total_billed_hours = float(filtered_df['Billed hours'].sum())
        avg_rate = total_billed_value / total_billed_hours if total_billed_hours > 0 else 0.0
        st.metric("Average Rate", f"${avg_rate:.2f}/hr")

    # Overview charts
    col1, col2 = st.columns(2)
    
    with col1:
        hours_data = pd.DataFrame({
            'Category': ['Billed Hours', 'Unbilled Hours', 'Non-billable Hours'],
            'Hours': [
                filtered_df['Billed hours'].sum(),
                filtered_df['Unbilled hours'].sum(),
                filtered_df['Non-billable hours'].sum()
            ]
        })
        fig = px.pie(hours_data, values='Hours', names='Category', 
                     title='Distribution of Hours')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        monthly_hours = filtered_df.groupby(filtered_df['Activity date'].dt.to_period('M')).agg({
            'Billed hours': 'sum'
        }).reset_index()
        monthly_hours['Activity date'] = monthly_hours['Activity date'].astype(str)
        
        fig = px.line(monthly_hours, x='Activity date', y='Billed hours',
                     title='Monthly Billed Hours Trend')
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Client Analysis
with tab2:
    st.header('Client Analysis')
    
    # Top 10 Clients
    top_clients = filtered_df.groupby('Company name').agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum'
    }).sort_values('Billed hours value', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(top_clients, y=top_clients.index, x='Billed hours',
                     title='Top 10 Clients by Billed Hours',
                     orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Prepare data for treemap by removing NaN values
        treemap_df = filtered_df.copy()
        treemap_df = treemap_df.dropna(subset=['Practice area', 'Company name'])
        
        # Aggregate the data
        client_practice = treemap_df.groupby(['Practice area', 'Company name'])['Billed hours'].sum().reset_index()
        
        # Only create treemap if we have data
        if not client_practice.empty:
            fig = px.treemap(
                client_practice,
                path=['Practice area', 'Company name'],
                values='Billed hours',
                title='Client Distribution by Practice Area'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Client metrics table
    st.subheader('Client Metrics')
    client_metrics = filtered_df.groupby('Company name').agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum',
        'Matter number': 'nunique'
    }).round(2).reset_index()
    client_metrics.columns = ['Client', 'Total Hours', 'Total Revenue', 'Number of Matters']
    st.dataframe(client_metrics.sort_values('Total Revenue', ascending=False))

# Tab 3: Attorney Analysis
with tab3:
    st.header('Attorney Performance')
    
    # Attorney metrics
    attorney_metrics = filtered_df.groupby('User full name (first, last)').agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum',
        'Utilization rate': 'mean',
        'User rate': 'first'
    }).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(attorney_metrics, 
                     y=attorney_metrics.index, 
                     x='Utilization rate',
                     title='Attorney Utilization Rates',
                     orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        attorney_practice = filtered_df.groupby(
            ['User full name (first, last)', 'Practice area'])['Billed hours'].sum().reset_index()
        fig = px.bar(attorney_practice, 
                     x='User full name (first, last)', 
                     y='Billed hours',
                     color='Practice area', 
                     title='Practice Area Distribution by Attorney')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Attorney metrics table
    st.subheader('Attorney Performance Metrics')
    attorney_metrics = attorney_metrics.reset_index()
    attorney_metrics.columns = ['Attorney', 'Total Billed Hours', 'Total Revenue', 'Utilization Rate', 'Hourly Rate']
    st.dataframe(attorney_metrics.sort_values('Total Revenue', ascending=False))

# Tab 4: Practice Areas
with tab4:
    st.header('Practice Area Analysis')
    
    col1, col2 = st.columns(2)
    
    with col1:
        practice_hours = filtered_df.groupby('Practice area').agg({
            'Billed hours': 'sum',
            'Billed hours value': 'sum'
        }).reset_index()
        fig = px.bar(practice_hours, 
                     x='Practice area', 
                     y='Billed hours',
                     title='Billed Hours by Practice Area')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        practice_revenue = filtered_df.groupby('Practice area')['Billed hours value'].sum().reset_index()
        fig = px.pie(practice_revenue, 
                     values='Billed hours value', 
                     names='Practice area',
                     title='Revenue Distribution by Practice Area')
        st.plotly_chart(fig, use_container_width=True)
    
    # Practice area metrics table
    st.subheader('Practice Area Metrics')
    practice_metrics = filtered_df.groupby('Practice area').agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum',
        'Matter number': 'nunique',
        'Utilization rate': 'mean'
    }).round(2).reset_index()
    practice_metrics.columns = ['Practice Area', 'Total Hours', 'Total Revenue', 'Number of Matters', 'Avg Utilization']
    st.dataframe(practice_metrics.sort_values('Total Revenue', ascending=False))

# Tab 5: Trending
with tab5:
    st.header('Trending Analysis')
    
    # Time series analysis
    time_metrics = filtered_df.groupby(filtered_df['Activity date'].dt.to_period('M')).agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum',
        'Utilization rate': 'mean'
    }).reset_index()
    
    time_metrics['Activity date'] = time_metrics['Activity date'].astype(str)
    
    # Multiple metrics over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_metrics['Activity date'], 
                            y=time_metrics['Billed hours'],
                            name='Billed Hours'))
    fig.add_trace(go.Scatter(x=time_metrics['Activity date'], 
                            y=time_metrics['Utilization rate'],
                            name='Utilization Rate', 
                            yaxis='y2'))
    
    fig.update_layout(
        title='Trending Metrics Over Time',
        yaxis=dict(title='Billed Hours'),
        yaxis2=dict(title='Utilization Rate', overlaying='y', side='right'),
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trending tables
    st.subheader('Monthly Metrics')
    monthly_metrics = time_metrics[['Activity date', 'Billed hours', 'Billed hours value', 'Utilization rate']].round(2)
    monthly_metrics.columns = ['Month', 'Billed Hours', 'Revenue', 'Utilization Rate']
    st.dataframe(monthly_metrics)

# Add CSS to style the tabs
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 24px;
        padding-right: 24px;
    }
    </style>
    """, unsafe_allow_html=True)
