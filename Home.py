import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Scale LLP Analytics Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            df[col] = df[col].replace('', pd.NA)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
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

# Initialize session state for filters
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'years': [],
        'months': [],
        'quarters': [],
        'attorney_levels': [],
        'attorneys': [],
        'practices': [],
        'locations': [],
        'statuses': [],
        'clients': []
    }

# Load data
df = load_data()

# Create sidebar filters
def create_sidebar_filters():
    st.sidebar.header('Filters')
    
    # Time period filters
    st.sidebar.subheader('Time Period Filters')
    
    # Year filter
    years = sorted(df['Activity Year'].dropna().unique().astype(int).tolist())
    st.session_state.filters['years'] = st.sidebar.multiselect(
        'Select Years',
        options=years,
        default=[years[-1]] if years else []
    )
    
    # Month filter
    months = sorted(df['Activity month'].dropna().unique().astype(int).tolist())
    month_names = [calendar.month_name[m] for m in months if 1 <= m <= 12]
    st.session_state.filters['months'] = st.sidebar.multiselect(
        'Select Months',
        options=month_names,
        default=[]
    )
    
    # Quarter filter
    quarters = sorted(df['Activity quarter'].dropna().unique().astype(int).tolist())
    st.session_state.filters['quarters'] = st.sidebar.multiselect(
        'Select Quarters',
        options=[f'Q{q}' for q in quarters],
        default=[]
    )
    
    # Other filters
    st.sidebar.subheader('Other Filters')
    
    # Attorney level filter
    attorney_levels = sorted(df['Attorney level'].dropna().unique())
    st.session_state.filters['attorney_levels'] = st.sidebar.multiselect(
        'Attorney Levels',
        options=attorney_levels
    )
    
    # Attorney filter
    attorneys = sorted(df['User full name (first, last)'].dropna().unique())
    st.session_state.filters['attorneys'] = st.sidebar.multiselect(
        'Attorneys',
        options=attorneys
    )
    
    # Practice area filter
    practices = sorted(df['Practice area'].dropna().unique())
    st.session_state.filters['practices'] = st.sidebar.multiselect(
        'Practice Areas',
        options=practices
    )
    
    # Location filter
    locations = sorted(df['Matter location'].dropna().unique())
    st.session_state.filters['locations'] = st.sidebar.multiselect(
        'Matter Locations',
        options=locations
    )
    
    # Status filter
    statuses = sorted(df['Matter status'].dropna().unique())
    st.session_state.filters['statuses'] = st.sidebar.multiselect(
        'Matter Status',
        options=statuses
    )
    
    # Client filter
    clients = sorted(df['Company name'].dropna().unique())
    st.session_state.filters['clients'] = st.sidebar.multiselect(
        'Clients',
        options=clients
    )

# Function to apply filters
def apply_filters(df):
    filtered = df.copy()
    
    if st.session_state.filters['years']:
        filtered = filtered[filtered['Activity Year'].isin(st.session_state.filters['years'])]
    
    if st.session_state.filters['months']:
        selected_month_numbers = [list(calendar.month_name).index(month) for month in st.session_state.filters['months']]
        filtered = filtered[filtered['Activity month'].isin(selected_month_numbers)]
    
    if st.session_state.filters['quarters']:
        selected_quarter_numbers = [int(q[1]) for q in st.session_state.filters['quarters']]
        filtered = filtered[filtered['Activity quarter'].isin(selected_quarter_numbers)]
    
    if st.session_state.filters['attorney_levels']:
        filtered = filtered[filtered['Attorney level'].isin(st.session_state.filters['attorney_levels'])]
    
    if st.session_state.filters['attorneys']:
        filtered = filtered[filtered['User full name (first, last)'].isin(st.session_state.filters['attorneys'])]
    
    if st.session_state.filters['practices']:
        filtered = filtered[filtered['Practice area'].isin(st.session_state.filters['practices'])]
    
    if st.session_state.filters['locations']:
        filtered = filtered[filtered['Matter location'].isin(st.session_state.filters['locations'])]
    
    if st.session_state.filters['statuses']:
        filtered = filtered[filtered['Matter status'].isin(st.session_state.filters['statuses'])]
    
    if st.session_state.filters['clients']:
        filtered = filtered[filtered['Company name'].isin(st.session_state.filters['clients'])]
    
    return filtered

# Create sidebar filters
create_sidebar_filters()

# Apply filters to get filtered dataframe
filtered_df = apply_filters(df)

# Main page content
st.title("Scale LLP Analytics Dashboard")
st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")

# Welcome message
st.write("""
Welcome to the Scale LLP Analytics Dashboard. This dashboard provides comprehensive insights into the firm's performance metrics, 
client relationships, attorney productivity, and practice area analysis. Refreshed Weekly on Friday at 12:00 AM PST 

📊 **Available Pages:**
- Overview: Key performance metrics and high-level insights
- Client Analysis: Detailed client performance and relationship metrics
- Attorney Analysis: Individual attorney performance and productivity metrics
- Practice Areas: Practice-specific analysis and trends
- Trending: Historical trends and performance patterns

Use the filters in the sidebar to customize the view according to your needs.
""")
# Display key metrics on the home page
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_billable_hours = filtered_df['Billed & Unbilled hours'].sum()
    prev_total = total_billable_hours * 0.95  # Example comparison
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

# Display summary visualizations
st.markdown("### Summary Visualizations")
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
    # Practice Area Revenue Distribution
    practice_revenue = filtered_df.groupby('Practice area').agg({
        'Billed hours value': 'sum'
    }).reset_index()
    
    fig_practice = px.pie(
        practice_revenue,
        values='Billed hours value',
        names='Practice area',
        title='Revenue by Practice Area'
    )
    st.plotly_chart(fig_practice, use_container_width=True)

# Add custom CSS for styling
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
    .stApp {
        background-color: #ffffff;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #2c3e50;
    }
    .stSidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        padding-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Add export functionality for raw data
st.sidebar.markdown("---")
if st.sidebar.button("Export Raw Data"):
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download CSV",
        csv,
        "scale_llp_data.csv",
        "text/csv",
        key='download-csv'
    )

# Display last refresh time in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("*Last data refresh:*  \nWednesday Feb 19, 2025")
