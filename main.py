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
        
        # Ensure date columns are properly parsed
        date_columns = ['Activity date', 'Matter open date', 'Matter pending date', 'Matter close date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Add derived columns if not present
        if 'Activity Year' not in df.columns and 'Activity date' in df.columns:
            df['Activity Year'] = df['Activity date'].dt.year
        
        if 'Activity month' not in df.columns and 'Activity date' in df.columns:
            df['Activity month'] = df['Activity date'].dt.month
        
        if 'Activity quarter' not in df.columns and 'Activity date' in df.columns:
            df['Activity quarter'] = df['Activity date'].dt.quarter
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
df = load_data()

# Clean column names once
df.columns = df.columns.str.replace('*', '').str.replace('"', '').str.strip()

# Sidebar filters
st.sidebar.header('Filters')

# Safely get unique values with default
def get_unique_values(df, column, default_first=True):
    try:
        values = sorted(df[column].dropna().unique())
        return values if values else []
    except Exception:
        return []

# Year filter
years = get_unique_values(df, 'Activity Year')
selected_years = st.sidebar.multiselect(
    'Select Years',
    options=years,
    default=[years[0]] if years else [],
    key="year_select"
)

# Safely get months
months = get_unique_values(df, 'Activity month')
month_names = [calendar.month_name[int(m)] for m in months]

# Time filters
filter_section = st.sidebar.radio(
    "Select Additional Time Filter",
    ["Month/Quarter", "Custom Range"],
    key="time_filter_type"
)

month_selection = []
quarter_selection = []
start_month = None
end_month = None

if filter_section == "Month/Quarter":
    level = st.sidebar.radio(
        "Filter by",
        ["Month", "Quarter"],
        key="month_quarter_level"
    )
    
    if level == "Month":
        # Convert months to month names for display
        month_selection = st.sidebar.multiselect(
            'Select Months',
            options=months,
            default=[months[0]] if months else [],
            format_func=lambda x: calendar.month_name[int(x)],
            key="month_select"
        )
    else:
        quarters = get_unique_values(df, 'Activity quarter')
        quarter_selection = st.sidebar.multiselect(
            'Select Quarters',
            options=quarters,
            default=[quarters[0]] if quarters else [],
            format_func=lambda x: f'Q{int(x)}',
            key="quarter_select"
        )
else:
    # Custom Range
    start_month = st.sidebar.selectbox(
        'Start Month', 
        options=months, 
        format_func=lambda x: calendar.month_name[int(x)],
        key="start_month"
    )
    end_month = st.sidebar.selectbox(
        'End Month',
        options=months,
        format_func=lambda x: calendar.month_name[int(x)],
        index=len(months)-1 if months else 0,
        key="end_month"
    )

# Other filters with safe value extraction
attorneys = st.sidebar.multiselect(
    'Attorneys',
    options=get_unique_values(df, 'User full name (first, last)'),
    key="attorneys"
)

practices = st.sidebar.multiselect(
    'Practice Areas',
    options=get_unique_values(df, 'Practice area'),
    key="practices"
)

locations = st.sidebar.multiselect(
    'Matter Locations',
    options=get_unique_values(df, 'Matter location'),
    key="locations"
)

statuses = st.sidebar.multiselect(
    'Matter Status',
    options=get_unique_values(df, 'Matter status'),
    key="statuses"
)

clients = st.sidebar.multiselect(
    'Clients',
    options=get_unique_values(df, 'Company name'),
    key="clients"
)

def filter_data(df):
    filtered = df.copy()
    
    # Apply year filter
    if selected_years:
        filtered = filtered[filtered['Activity Year'].isin(selected_years)]
    
    # Apply month/quarter filters
    if filter_section == "Month/Quarter":
        if level == "Month" and month_selection:
            filtered = filtered[filtered['Activity month'].isin([months[month_names.index(m)] for m in month_selection])]
        elif level == "Quarter" and quarter_selection:
            filtered = filtered[filtered['Activity quarter'].isin(quarter_selection)]
    else:
        if start_month is not None and end_month is not None:
            start_idx = months.index(start_month)
            end_idx = months.index(end_month)
            filtered = filtered[
                (filtered['Activity month'] >= months[start_idx]) & 
                (filtered['Activity month'] <= months[end_idx])
            ]
    
    # Apply other filters
    if attorneys:
        filtered = filtered[filtered['User full name (first, last)'].isin(attorneys)]
    if practices:
        filtered = filtered[filtered['Practice area'].isin(practices)]
    if locations:
        filtered = filtered[filtered['Matter location'].isin(locations)]
    if statuses:
        filtered = filtered[filtered['Matter status'].isin(statuses)]
    if clients:
        filtered = filtered[filtered['Company name'].isin(clients)]
    
    return filtered

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
        monthly_data = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
            'Billed hours': 'sum'
        }).reset_index()
        monthly_data['Period'] = monthly_data['Activity Year'].astype(str) + '-' + monthly_data['Activity month'].astype(str).str.zfill(2)
        
        fig = px.line(monthly_data, x='Period', y='Billed hours',
                     title='Monthly Billed Hours Trend')
        fig.update_layout(xaxis_tickangle=-45)
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
    
    # Time series analysis by year and month
    time_metrics = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum',
        'Utilization rate': 'mean'
    }).reset_index()
    
    time_metrics['Period'] = time_metrics['Activity Year'].astype(str) + '-' + time_metrics['Activity month'].astype(str).str.zfill(2)
    
    # Multiple metrics over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_metrics['Period'], 
                            y=time_metrics['Billed hours'],
                            name='Billed Hours'))
    fig.add_trace(go.Scatter(x=time_metrics['Period'], 
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
    monthly_metrics = time_metrics[['Period', 'Billed hours', 'Billed hours value', 'Utilization rate']].round(2)
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

# Add error handling for empty DataFrame
if df.empty:
    st.error("No data found in the CSV file. Please check the file and try again."
