import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Set page config
st.set_page_config(page_title="Law Firm Analytics Dashboard", layout="wide")

# Load data function (same as before)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Test_Full_Year.csv")
        
        # Convert date columns to datetime
        date_columns = ['Activity date', 'Matter open date', 'Matter pending date', 'Matter close date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%m/%d/%Y', errors='coerce')
        
        # Convert numeric columns to float
        numeric_columns = [
            'Billed & Unbilled hours',
            'Billed hours',
            'Unbilled hours',
            'Non-billable hours',
            'Billed hours value',
            'Utilization rate'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load data
df = load_data()

# Sidebar filters (common across all tabs)
st.sidebar.header('Filters')

# Helper function to get clean options
def get_clean_options(df, column):
    return sorted(list(df[column].dropna().unique()))

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header('Filters')

# Helper function to get clean options
def get_clean_options(df, column):
    return sorted(list(df[column].dropna().unique()))

# Time filters
st.sidebar.subheader('Time Filters')
date_filter_type = st.sidebar.radio(
    "Select Date Filter Type",
    ["Year-Month", "Custom Date Range"]
)

if date_filter_type == "Year-Month":
    # Get unique months and quarters
    unique_months = sorted(df['Activity month'].unique())
    unique_quarters = sorted(df['Activity quarter'].unique())
    
    # Year-Month filters
    filter_level = st.sidebar.radio(
        "Filter by",
        ["Month", "Quarter"]
    )
    
    if filter_level == "Month":
        selected_months = st.sidebar.multiselect(
            'Select Months',
            options=unique_months,
            default=[unique_months[0]]
        )
    else:
        selected_quarters = st.sidebar.multiselect(
            'Select Quarters',
            options=unique_quarters,
            default=[unique_quarters[0]]
        )
else:
    # Custom date range
    min_date = pd.to_datetime(df['Activity date'].min())
    max_date = pd.to_datetime(df['Activity date'].max())
    
    start_date = st.sidebar.date_input('Start Date', 
                                      min_date,
                                      min_value=min_date,
                                      max_value=max_date)
    end_date = st.sidebar.date_input('End Date', 
                                    max_date,
                                    min_value=min_date,
                                    max_value=max_date)

# Other filters
st.sidebar.subheader('Other Filters')
selected_attorney = st.sidebar.multiselect(
    'Attorneys',
    options=get_clean_options(df, 'User full name (first, last)')
)

selected_practice = st.sidebar.multiselect(
    'Practice Areas',
    options=get_clean_options(df, 'Practice area')
)

selected_location = st.sidebar.multiselect(
    'Matter Locations',
    options=get_clean_options(df, 'Matter location')
)

selected_status = st.sidebar.multiselect(
    'Matter Status',
    options=get_clean_options(df, 'Matter status')
)

selected_billing = st.sidebar.multiselect(
    'Matter Billing Method',
    options=get_clean_options(df, 'Matter billing method')
)

selected_client = st.sidebar.multiselect(
    'Clients',
    options=get_clean_options(df, 'Company name')
)

# Apply filters function
def filter_data(df):
    filtered_df = df.copy()
    
    # Apply date filters
    if date_filter_type == "Year-Month":
        if filter_level == "Month" and selected_months:
            filtered_df = filtered_df[filtered_df['Activity month'].isin(selected_months)]
        elif filter_level == "Quarter" and selected_quarters:
            filtered_df = filtered_df[filtered_df['Activity quarter'].isin(selected_quarters)]
    else:
        # Convert dates to datetime for comparison
        filtered_df['Activity date'] = pd.to_datetime(filtered_df['Activity date'])
        filtered_df = filtered_df[
            (filtered_df['Activity date'].dt.date >= start_date) &
            (filtered_df['Activity date'].dt.date <= end_date)
        ]
    
    # Apply other filters
    if selected_attorney:
        filtered_df = filtered_df[filtered_df['User full name (first, last)'].isin(selected_attorney)]
    if selected_practice:
        filtered_df = filtered_df[filtered_df['Practice area'].isin(selected_practice)]
    if selected_location:
        filtered_df = filtered_df[filtered_df['Matter location'].isin(selected_location)]
    if selected_status:
        filtered_df = filtered_df[filtered_df['Matter status'].isin(selected_status)]
    if selected_billing:
        filtered_df = filtered_df[filtered_df['Matter billing method'].isin(selected_billing)]
    if selected_client:
        filtered_df = filtered_df[filtered_df['Company name'].isin(selected_client)]
    
    return filtered_df = filtered_df[filtered_df['Activity date'].dt.year.isin(selected_years)]
        if selected_months:
            filtered_df = filtered_df[filtered_df['Activity date'].dt.month.isin(selected_months)]
    else:
        filtered_df = filtered_df[
            (filtered_df['Activity date'].dt.date >= start_date) &
            (filtered_df['Activity date'].dt.date <= end_date)
        ]
    
    # Apply other filters
    if selected_attorney:
        filtered_df = filtered_df[filtered_df['User full name (first, last)'].isin(selected_attorney)]
    if selected_practice:
        filtered_df = filtered_df[filtered_df['Practice area'].isin(selected_practice)]
    if selected_location:
        filtered_df = filtered_df[filtered_df['Matter location'].isin(selected_location)]
    if selected_status:
        filtered_df = filtered_df[filtered_df['Matter status'].isin(selected_status)]
    if selected_billing:
        filtered_df = filtered_df[filtered_df['Matter billing method'].isin(selected_billing)]
    if selected_client:
        filtered_df = filtered_df[filtered_df['Company name'].isin(selected_client)]
    
    return filtered_df

# Apply filters to get filtered dataframe
filtered_df = filter_data(df)

# Update filter_data function
def filter_data(df):
    filtered_df = df.copy()
    
    # Apply date filters
    if date_filter_type == "Year-Month":
        if selected_years:
            filtered_df = filtered_df[filtered_df['Activity date'].dt.year.isin(selected_years)]
        if selected_months:
            filtered_df = filtered_df[filtered_df['Activity date'].dt.month.isin(selected_months)]
    else:
        filtered_df = filtered_df[
            (filtered_df['Activity date'].dt.date >= start_date) &
            (filtered_df['Activity date'].dt.date <= end_date)
        ]
    
    # Apply other filters
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
def filter_data(df):
    filtered_df = df.copy()
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

filtered_df = filter_data(df)

# Calculate period-over-period changes for metrics
def calculate_delta(df, column):
    if df.empty:
        return 0.0
        
    df['month'] = df['Activity date'].dt.to_period('M')
    current_month = df['month'].max()
    previous_month = current_month - 1
    
    current = float(df[df['month'] == current_month][column].sum())
    previous = float(df[df['month'] == previous_month][column].sum())
    
    delta = ((current - previous) / previous * 100) if previous != 0 else 0
    return delta

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Client Analysis", "Attorney Analysis", "Practice Areas", "Trending"])

# Tab 1: Overview
with tab1:
    st.header('Key Performance Metrics')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_billable_hours = float(filtered_df['Billed & Unbilled hours'].sum())
        delta_billable = calculate_delta(filtered_df, 'Billed & Unbilled hours')
        st.metric("Total Billable Hours", 
                 f"{total_billable_hours:,.1f}", 
                 f"{delta_billable:+.1f}%" if delta_billable != 0 else None)

    with col2:
        total_billed_hours = float(filtered_df['Billed hours'].sum())
        delta_billed = calculate_delta(filtered_df, 'Billed hours')
        st.metric("Billed Hours", 
                 f"{total_billed_hours:,.1f}", 
                 f"{delta_billed:+.1f}%" if delta_billed != 0 else None)

    with col3:
        avg_utilization = float(filtered_df['Utilization rate'].mean())
        delta_utilization = calculate_delta(filtered_df, 'Utilization rate')
        st.metric("Utilization Rate", 
                 f"{avg_utilization:.1f}%", 
                 f"{delta_utilization:+.1f}%" if delta_utilization != 0 else None)

    with col4:
        total_billed_value = float(filtered_df['Billed hours value'].sum())
        total_billed_hours = float(filtered_df['Billed hours'].sum())
        avg_rate = total_billed_value / total_billed_hours if total_billed_hours > 0 else 0.0
        st.metric("Average Rate", 
                 f"${avg_rate:.2f}/hr")

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
        # Monthly trend
        monthly_hours = filtered_df.groupby(filtered_df['Activity date'].dt.to_period('M')).agg({
            'Billed hours': 'sum',
            'Utilization rate': 'mean'
        }).reset_index()
        monthly_hours['Activity date'] = monthly_hours['Activity date'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_hours['Activity date'], 
                                y=monthly_hours['Billed hours'],
                                name='Billed Hours'))
        fig.update_layout(title='Monthly Billed Hours Trend')
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
        else:
            st.warning("No data available for treemap visualization")
    
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
        yaxis2=dict(title='Utilization Rate', overlaying='y', side='right')
    )
    
    st.plotly_chart(fig, use_container_width=True)

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
