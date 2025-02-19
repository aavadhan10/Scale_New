import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime

# Set page config
st.set_page_config(page_title="Law Firm Analytics Dashboard", layout="wide")

# Load data function
@st.cache_data
def load_data():
    df = pd.read_csv("Test_Full_Year.csv")
    
    # Convert numeric columns
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
            # First replace empty strings with NaN
            df[col] = df[col].replace('', pd.NA)
            # Then convert to numeric, coercing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Format year correctly (remove comma if present)
    df['Activity Year'] = df['Activity Year'].astype(str).str.replace(',', '').astype(float)
    
    # Attorney levels mapping
    attorney_levels = {
        'Aaron Swerdlow': 'Senior Counsel',
        'Aidan Toombs': 'Mid-Level Counsel',
        'Alexander Gershen': 'Senior Counsel',
        'Alexander Slafkosky': 'Senior Counsel',
        'Alfred Bridi': 'Senior Counsel',
        'Aliona Ierega': 'Mid-Level Counsel',
        'Amy Duvanich': 'Senior Counsel',
        'Andres Idarraga': 'Senior Counsel',
        'Andy Baxter': 'Mid-Level Counsel',
        'Antigone Peyton': 'Senior Counsel',
        'Ayala Magder': 'Senior Counsel',
        'Benjamin Golopol': 'Mid-Level Counsel',
        'Brian Detwiler': 'Senior Counsel',
        'Brian Elliott': 'Senior Counsel',
        'Brian Hicks': 'Senior Counsel',
        'Brian McEvoy': 'Senior Counsel',
        'Brian Scherer': 'Senior Counsel',
        'Caitlin Cunningham': 'Mid-Level Counsel',
        'Cary Ullman': 'Senior Counsel',
        'Channah Rose': 'Mid-Level Counsel',
        'Charles Caliman': 'Senior Counsel',
        'Charles Wallace': 'Senior Counsel',
        'Chris Geyer': 'Senior Counsel',
        'Chris Jones': 'Mid-Level Counsel',
        'Christopher Grewe': 'Senior Counsel',
        'Chuck Kraus': 'Senior Counsel',
        'Corey Pedersen': 'Senior Counsel',
        'Darren Collins (DS)': 'Document Specialist',
        'David Lundeen': 'Senior Counsel',
        'Derek Gilman': 'Senior Counsel',
        'Donica Forensich': 'Mid-Level Counsel',
        'Dori Karjian': 'Senior Counsel',
        'Doug Mitchell': 'Senior Counsel',
        'Elliott Gee (DS)': 'Document Specialist',
        'Emma Thompson': 'Senior Counsel',
        'Eric Blatt': 'Senior Counsel',
        'Erica Shepard': 'Senior Counsel',
        'Garrett Ordower': 'Senior Counsel',
        'Gregory Winter': 'Senior Counsel',
        'Hannah Valdez': 'Mid-Level Counsel',
        'Heather Cantua': 'Mid-Level Counsel',
        'Henry Ciocca': 'Senior Counsel',
        'Jacqueline Post Ladha': 'Senior Counsel',
        'James Cashel': 'Mid-Level Counsel',
        'James Creedon': 'Senior Counsel',
        'Jamie Wells': 'Senior Counsel',
        'Jason Altieri': 'Senior Counsel',
        'Jason Harrison': 'Mid-Level Counsel',
        'Jeff Lord': 'Senior Counsel',
        'Jeff Love': 'Senior Counsel',
        'Jenna Geuke': 'Mid-Level Counsel',
        'Joanne Wolforth': 'Mid-Level Counsel',
        'John Mitnick': 'Senior Counsel',
        'Jonathan Van Loo': 'Senior Counsel',
        'Joseph Kiefer': 'Mid-Level Counsel',
        'Josh Banerje': 'Mid-Level Counsel',
        'Julie Snyder': 'Senior Counsel',
        'Julien Apollon': 'Mid-Level Counsel',
        'Justin McAnaney': 'Mid-Level Counsel',
        'Katy Barreto': 'Senior Counsel',
        'Katy Reamon': 'Mid-Level Counsel',
        'Kimberly Griffin': 'Mid-Level Counsel',
        'Kirby Drake': 'Senior Counsel',
        'Kristen Dayley': 'Senior Counsel',
        'Kristin Bohm': 'Mid-Level Counsel',
        'Lauren Titolo': 'Mid-Level Counsel',
        'Lindsey Altmeyer': 'Senior Counsel',
        'M. Sidney Donica': 'Senior Counsel',
        'Marissa Fox': 'Senior Counsel',
        'Mary Spooner': 'Senior Counsel',
        'Matthew Angelo': 'Senior Counsel',
        'Matthew Dowd (DS)': 'Document Specialist',
        'Maureen Bumgarner': 'Mid-Level Counsel',
        'Melissa Balough': 'Senior Counsel',
        'Melissa Clarke': 'Senior Counsel',
        'Michael Keskey': 'Mid-Level Counsel',
        'Michelle Maticic': 'Senior Counsel',
        'Natasha Fedder': 'Senior Counsel',
        'Nicole Baldocchi': 'Senior Counsel',
        'Nora Wong': 'Mid-Level Counsel',
        'Ornella Bourne': 'Mid-Level Counsel',
        'Rainer Scarton': 'Mid-Level Counsel',
        'Robert Gans': 'Senior Counsel',
        'Robin Shofner': 'Senior Counsel',
        'Robyn Marcello': 'Mid-Level Counsel',
        'Sabina Schiller': 'Mid-Level Counsel',
        'Samer Korkor': 'Senior Counsel',
        'Sara Rau Frumkin': 'Senior Counsel',
        'Scale LLP': 'Other',
        'Scott Wiegand': 'Senior Counsel',
        'Shailika Kotiya': 'Mid-Level Counsel',
        'Shannon Straughan': 'Senior Counsel',
        'Stephen Bosco': 'Mid-Level Counsel',
        'Steve Forbes': 'Senior Counsel',
        'Steve Zagami, Paralegal': 'Paralegal',
        'Thomas Soave': 'Mid-Level Counsel',
        'Thomas Stine': 'Senior Counsel',
        'Tim Furin': 'Senior Counsel',
        'Trey Calver': 'Senior Counsel',
        'Tyler Hayden': 'Mid-Level Counsel',
        'Whitney Joubert': 'Senior Counsel',
        'Zach Ruby': 'Mid-Level Counsel'
    }
    
    # Clean attorney names and add level
    df['User full name (first, last)'] = df['User full name (first, last)'].str.strip()
    df['Attorney level'] = df['User full name (first, last)'].map(attorney_levels)
    
    return df

# Load data
df = load_data()

# Clean column names
df.columns = df.columns.str.strip()

# Sidebar filters
st.sidebar.header('Filters')

# Time period filters
st.sidebar.subheader('Time Period Filters')

# Year filter
years = sorted(df['Activity Year'].dropna().unique().astype(int).tolist())
selected_years = st.sidebar.multiselect(
    'Select Years',
    options=years,
    default=[years[-1]] if years else []
)

# Month filter
months = sorted(df['Activity month'].dropna().unique().astype(int).tolist())
month_names = [calendar.month_name[m] for m in months if 1 <= m <= 12]
selected_months = st.sidebar.multiselect(
    'Select Months',
    options=month_names,
    default=[]
)

# Quarter filter
quarters = sorted(df['Activity quarter'].dropna().unique().astype(int).tolist())
selected_quarters = st.sidebar.multiselect(
    'Select Quarters',
    options=[f'Q{q}' for q in quarters],
    default=[]
)

# Other filters
st.sidebar.subheader('Other Filters')

attorneys = sorted(df['User full name (first, last)'].dropna().unique())
practices = sorted(df['Practice area'].dropna().unique())
locations = sorted(df['Matter location'].dropna().unique())
statuses = sorted(df['Matter status'].dropna().unique())
clients = sorted(df['Company name'].dropna().unique())

# Add Attorney Level filter
attorney_levels = sorted(df['Attorney level'].dropna().unique())
selected_levels = st.sidebar.multiselect('Attorney Levels', options=attorney_levels)

# Add filters to sidebar
selected_attorneys = st.sidebar.multiselect('Attorneys', options=attorneys)
selected_practices = st.sidebar.multiselect('Practice Areas', options=practices)
selected_locations = st.sidebar.multiselect('Matter Locations', options=locations)
selected_statuses = st.sidebar.multiselect('Matter Status', options=statuses)
selected_clients = st.sidebar.multiselect('Clients', options=clients)

def filter_data(df):
    filtered = df.copy()
    
    # Time period filters
    if selected_years:
        filtered = filtered[filtered['Activity Year'].isin(selected_years)]
    
    if selected_months:
        selected_month_numbers = [list(calendar.month_name).index(month) for month in selected_months]
        filtered = filtered[filtered['Activity month'].isin(selected_month_numbers)]
    
    if selected_quarters:
        selected_quarter_numbers = [int(q[1]) for q in selected_quarters]
        filtered = filtered[filtered['Activity quarter'].isin(selected_quarter_numbers)]
    
    # Attorney level filter
    if selected_levels:
        filtered = filtered[filtered['Attorney level'].isin(selected_levels)]
    
    # Other filters
    if selected_attorneys:
        filtered = filtered[filtered['User full name (first, last)'].isin(selected_attorneys)]
    if selected_practices:
        filtered = filtered[filtered['Practice area'].isin(selected_practices)]
    if selected_locations:
        filtered = filtered[filtered['Matter location'].isin(selected_locations)]
    if selected_statuses:
        filtered = filtered[filtered['Matter status'].isin(selected_statuses)]
    if selected_clients:
        filtered = filtered[filtered['Company name'].isin(selected_clients)]
    
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
        total_billable_hours = filtered_df['Billed & Unbilled hours'].sum()
        st.metric("Total Billable Hours", f"{total_billable_hours:,.1f}")

    with col2:
        total_billed_hours = filtered_df['Billed hours'].sum()
        st.metric("Billed Hours", f"{total_billed_hours:,.1f}")

    with col3:
        avg_utilization = filtered_df['Utilization rate'].mean()
        st.metric("Average Utilization", f"{avg_utilization:.1f}%")

    with col4:
        total_value = filtered_df['Billed hours value'].sum()
        total_hours = filtered_df['Billed hours'].sum()
        avg_rate = total_value / total_hours if total_hours > 0 else 0
        st.metric("Average Rate", f"${avg_rate:.2f}/hr")

    # Overview charts
    col1, col2 = st.columns(2)
    
    with col1:
        hours_data = pd.DataFrame({
            'Category': ['Billed Hours', 'Unbilled Hours', 'Non-billable Hours'],
            'Hours': [
                filtered_df['Billed hours'].astype(float).sum(),
                filtered_df['Unbilled hours'].astype(float).sum(),
                filtered_df['Non-billable hours'].astype(float).sum()
            ]
        })
        fig = px.pie(hours_data, values='Hours', names='Category', 
                     title='Distribution of Hours')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        monthly_data = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
            'Billed hours': lambda x: x.astype(float).sum()
        }).reset_index()
        monthly_data['Period'] = monthly_data['Activity Year'].astype(str) + '-' + \
                                monthly_data['Activity month'].astype(str).str.zfill(2)
        
        fig = px.line(monthly_data, x='Period', y='Billed hours',
                     title='Monthly Billed Hours Trend')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Client Analysis
with tab2:
    st.header('Client Analysis')
    
    # Top 10 Clients
    top_clients = filtered_df.groupby('Company name').agg({
        'Billed hours': lambda x: x.astype(float).sum(),
        'Billed hours value': lambda x: x.astype(float).sum()
    }).sort_values('Billed hours value', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(top_clients, y=top_clients.index, x='Billed hours',
                     title='Top 10 Clients by Billed Hours',
                     orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        client_practice = filtered_df.groupby(['Practice area', 'Company name'])\
                         .agg({'Billed hours': lambda x: x.astype(float).sum()})\
                         .reset_index()
        
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
        'Billed hours': lambda x: x.astype(float).sum(),
        'Billed hours value': lambda x: x.astype(float).sum(),
        'Matter number': 'nunique'
    }).round(2).reset_index()
    client_metrics.columns = ['Client', 'Total Hours', 'Total Revenue', 'Number of Matters']
    st.dataframe(client_metrics.sort_values('Total Revenue', ascending=False))

# Tab 3: Attorney Analysis
with tab3:
    st.header('Attorney Performance')
    
    attorney_metrics = filtered_df.groupby('User full name (first, last)').agg({
        'Billed hours': lambda x: x.astype(float).sum(),
        'Billed hours value': lambda x: x.astype(float).sum(),
        'Utilization rate': lambda x: x.astype(float).mean(),
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
            ['User full name (first, last)', 'Practice area'])\
            .agg({'Billed hours': lambda x: x.astype(float).sum()})\
            .reset_index()
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
    attorney_metrics.columns = ['Attorney', 'Total Billed Hours', 'Total Revenue', 
                              'Utilization Rate', 'Hourly Rate']
    st.dataframe(attorney_metrics.sort_values('Total Revenue', ascending=False))

# Tab 4: Practice Areas
with tab4:
    st.header('Practice Area Analysis')
    
    col1, col2 = st.columns(2)
    
    with col1:
        practice_hours = filtered_df.groupby('Practice area').agg({
            'Billed hours': lambda x: x.astype(float).sum(),
            'Billed hours value': lambda x: x.astype(float).sum()
        }).reset_index()
        fig = px.bar(practice_hours, 
                     x='Practice area', 
                     y='Billed hours',
                     title='Billed Hours by Practice Area')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        practice_revenue = filtered_df.groupby('Practice area')\
                          .agg({'Billed hours value': lambda x: x.astype(float).sum()})\
                          .reset_index()
        fig = px.pie(practice_revenue, 
                     values='Billed hours value', 
                     names='Practice area',
                     title='Revenue Distribution by Practice Area')
        st.plotly_chart(fig, use_container_width=True)
    
    # Practice area metrics table
    st.subheader('Practice Area Metrics')
    practice_metrics = filtered_df.groupby('Practice area').agg({
        'Billed hours': lambda x: x.astype(float).sum(),
        'Billed hours value': lambda x: x.astype(float).sum(),
        'Matter number': 'nunique',
        'Utilization rate': lambda x: x.astype(float).mean()
    }).round(2).reset_index()
    practice_metrics.columns = ['Practice Area', 'Total Hours', 'Total Revenue', 
                              'Number of Matters', 'Avg Utilization']
    st.dataframe(practice_metrics.sort_values('Total Revenue', ascending=False))

# Tab 5: Trending
with tab5:
    st.header('Trending Analysis')
    
    time_metrics = filtered_df.groupby(['Activity Year', 'Activity month']).agg({
        'Billed hours': lambda x: x.astype(float).sum(),
        'Billed hours value': lambda x: x.astype(float).sum(),
        'Utilization rate': lambda x: x.astype(float).mean()
    }).reset_index()
    
    time_metrics['Period'] = time_metrics['Activity Year'].astype(str) + '-' + \
                            time_metrics['Activity month'].astype(str).str.zfill(2)
    
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
    monthly_metrics = time_metrics[['Period', 'Billed hours', 
                                  'Billed hours value', 'Utilization rate']].round(2)
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

# Handle empty DataFrame
if df.empty:
    st.error("No data found in the CSV file. Please check the file and try again.")
