import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar

# Set page config
st.set_page_config(page_title="Law Firm Analytics Dashboard", layout="wide")

# Function to load and prepare data
@st.cache_data
def load_data():
    try:
        # Read the CSV file
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
        
        # Remove rows with invalid Activity date
        if 'Activity date' in df.columns:
            df = df.dropna(subset=['Activity date'])
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()
        
        # Remove any rows where Activity date is NaT (if Activity date is crucial)
        if 'Activity date' in df.columns:
            initial_rows = len(df)
            df = df.dropna(subset=['Activity date'])
            dropped_rows = initial_rows - len(df)
            if dropped_rows > 0:
                st.warning(f"{dropped_rows} rows were dropped due to invalid Activity dates")
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please ensure your CSV file contains properly formatted dates (MM/DD/YYYY)")
        return pd.DataFrame()  # Return empty DataFrame instead of None

# Load data
df = load_data()

# Validate that we have the required columns
required_columns = [
    'Activity date', 
    'Billed hours',
    'Unbilled hours',
    'Non-billable hours',
    'Billed hours value',
    'Utilization rate',
    'User full name (first, last)',
    'Practice area',
    'Company name'
]

missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# Check if we have any data
if df.empty:
    st.error("No data available to display")
    st.stop()

# Sidebar filters (same as before)
st.sidebar.header('Filters')

# Time filters
current_year = datetime.now().year
selected_year = st.sidebar.selectbox('Year', range(current_year-5, current_year+1))
selected_quarter = st.sidebar.selectbox('Quarter', [f'Q{i}' for i in range(1, 5)])
selected_month = st.sidebar.selectbox('Month', list(calendar.month_name)[1:])

# Helper function to get clean unique values
def get_clean_options(df, column):
    return sorted(list(df[column].dropna().unique()))

# User filters
selected_attorney = st.sidebar.multiselect(
    'Attorneys',
    options=get_clean_options(df, 'User full name (first, last)')
)

# Practice area filter
selected_practice = st.sidebar.multiselect(
    'Practice Areas',
    options=get_clean_options(df, 'Practice area')
)

# Location filter
selected_location = st.sidebar.multiselect(
    'Matter Locations',
    options=get_clean_options(df, 'Matter location')
)

# Matter status filter
selected_status = st.sidebar.multiselect(
    'Matter Status',
    options=get_clean_options(df, 'Matter status')
)

# Billing method filter
selected_billing = st.sidebar.multiselect(
    'Matter Billing Method',
    options=get_clean_options(df, 'Matter billing method')
)

# Client filter
selected_client = st.sidebar.multiselect(
    'Clients',
    options=get_clean_options(df, 'Company name')
)

# Apply filters function (same as before)
def filter_data(df):
    filtered_df = df.copy()
    
    if selected_attorney:
        filtered_df = filtered_df[filtered_df['User full name (first, last)'].isin(selected_attorney)]
    if selected_practice:
        filtered_df = filtered_df[filtered_df['Practice area'].isin(selected_practice)]
    
    return filtered_df

filtered_df = filter_data(df)

# Main dashboard
st.title('Law Firm Analytics Dashboard')

# Top Level Metrics
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

# Hourly Distribution
st.header('Hours Analysis')
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
    # Daily trends
    daily_hours = filtered_df.groupby('Activity date')['Billed hours'].sum().reset_index()
    fig = px.line(daily_hours, x='Activity date', y='Billed hours',
                  title='Daily Billed Hours Trend')
    st.plotly_chart(fig, use_container_width=True)

# Practice Area Analysis
st.header('Practice Area Performance')
col1, col2 = st.columns(2)

with col1:
    practice_hours = filtered_df.groupby('Practice area').agg({
        'Billed hours': 'sum',
        'Billed hours value': 'sum'
    }).reset_index()
    fig = px.bar(practice_hours, x='Practice area', y='Billed hours',
                 title='Billed Hours by Practice Area')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    practice_revenue = filtered_df.groupby('Practice area')['Billed hours value'].sum().reset_index()
    fig = px.pie(practice_revenue, values='Billed hours value', names='Practice area',
                 title='Revenue Distribution by Practice Area')
    st.plotly_chart(fig, use_container_width=True)

# Client Analysis
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
    # Client distribution by practice area
    client_practice = filtered_df.groupby(['Practice area', 'Company name'])['Billed hours'].sum().reset_index()
    fig = px.treemap(client_practice, path=['Practice area', 'Company name'], values='Billed hours',
                     title='Client Distribution by Practice Area')
    st.plotly_chart(fig, use_container_width=True)

# Attorney Analysis
st.header('Attorney Performance')

# Attorney utilization rates
attorney_metrics = filtered_df.groupby('User full name (first, last)').agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Utilization rate': 'mean',
    'User rate': 'first'
}).round(2)

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(attorney_metrics, y=attorney_metrics.index, x='Utilization rate',
                 title='Attorney Utilization Rates',
                 orientation='h')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Practice areas by attorneys
    attorney_practice = filtered_df.groupby(['User full name (first, last)', 'Practice area'])['Billed hours'].sum().reset_index()
    fig = px.bar(attorney_practice, x='User full name (first, last)', y='Billed hours', 
                 color='Practice area', title='Practice Area Distribution by Attorney')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Monthly Trends
st.header('Monthly Trends')

monthly_metrics = filtered_df.groupby(filtered_df['Activity date'].dt.to_period('M')).agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Utilization rate': 'mean'
}).reset_index()

monthly_metrics['Activity date'] = monthly_metrics['Activity date'].astype(str)

fig = go.Figure()
fig.add_trace(go.Scatter(x=monthly_metrics['Activity date'], y=monthly_metrics['Billed hours'],
                        name='Billed Hours', mode='lines+markers'))
fig.add_trace(go.Scatter(x=monthly_metrics['Activity date'], y=monthly_metrics['Utilization rate'],
                        name='Utilization Rate', mode='lines+markers', yaxis='y2'))

fig.update_layout(
    title='Monthly Trends - Billed Hours and Utilization Rate',
    yaxis=dict(title='Billed Hours'),
    yaxis2=dict(title='Utilization Rate', overlaying='y', side='right'),
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)

# Detailed Metrics Tables
st.header('Detailed Metrics')

# Attorney Performance Table
st.subheader('Attorney Performance Metrics')
attorney_metrics = attorney_metrics.reset_index()
attorney_metrics.columns = ['Attorney', 'Total Billed Hours', 'Total Revenue', 'Utilization Rate', 'Hourly Rate']
st.dataframe(attorney_metrics, use_container_width=True)

# Client Metrics Table
st.subheader('Client Metrics')
client_metrics = filtered_df.groupby('Company name').agg({
    'Billed hours': 'sum',
    'Billed hours value': 'sum',
    'Matter number': 'nunique'
}).round(2).reset_index()
client_metrics.columns = ['Client', 'Total Hours', 'Total Revenue', 'Number of Matters']
st.dataframe(client_metrics.sort_values('Total Revenue', ascending=False), use_container_width=True)

# Download filtered data
st.header("Export Data")
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_law_firm_data.csv",
    mime="text/csv"
)
