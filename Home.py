import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime

# Set page configuration
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
    
    # Format year correctly
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

# Function to apply filters
def apply_filters(df):
    filtered = df.copy()
    
    # Apply year filter
    if st.session_state.filters['years']:
        filtered = filtered[filtered['Activity Year'].isin(st.session_state.filters['years'])]
    
    # Apply month filter
    if st.session_state.filters['months']:
        selected_month_numbers = [list(calendar.month_name).index(month) for month in st.session_state.filters['months']]
        filtered = filtered[filtered['Activity month'].isin(selected_month_numbers)]
    
    # Apply quarter filter
    if st.session_state.filters['quarters']:
        selected_quarter_numbers = [int(q[1]) for q in st.session_state.filters['quarters']]
        filtered = filtered[filtered['Activity quarter'].isin(selected_quarter_numbers)]
    
    # Apply attorney level filter
    if st.session_state.filters['attorney_levels']:
        filtered = filtered[filtered['Attorney level'].isin(st.session_state.filters['attorney_levels'])]
    
    # Apply attorney filter
    if st.session_state.filters['attorneys']:
        filtered = filtered[filtered['User full name (first, last)'].isin(st.session_state.filters['attorneys'])]
    
    # Apply practice area filter
    if st.session_state.filters['practices']:
        filtered = filtered[filtered['Practice area'].isin(st.session_state.filters['practices'])]
    
    # Apply location filter
    if st.session_state.filters['locations']:
        filtered = filtered[filtered['Matter location'].isin(st.session_state.filters['locations'])]
    
    # Apply status filter
    if st.session_state.filters['statuses']:
        filtered = filtered[filtered['Matter status'].isin(st.session_state.filters['statuses'])]
    
    # Apply client filter
    if st.session_state.filters['clients']:
        filtered = filtered[filtered['Company name'].isin(st.session_state.filters['clients'])]
    
    return filtered

# Create sidebar filters
def create_sidebar_filters(df):
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

# Add custom CSS
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
</style>
""", unsafe_allow_html=True)

# Main page content
def main():
    # Load data
    df = load_data()
    
    # Create sidebar filters
    create_sidebar_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df)
    
    # Main page header
    st.title("Scale LLP Analytics Dashboard")
    st.markdown(f"*Last refreshed: Wednesday Feb 19, 2025*")
    
    # Welcome message and instructions
    st.write("""
    Welcome to the Scale LLP Analytics Dashboard. This dashboard provides comprehensive insights into the firm's performance metrics, 
    client relationships, attorney productivity, and practice area analysis. Use the navigation menu on the left to explore different 
    aspects of the firm's operations.
    
    📊 **Available Pages:**
    - Overview: Key performance metrics and high-level insights
    - Client Analysis: Detailed client performance and relationship metrics
    - Attorney Analysis: Individual attorney performance and productivity metrics
    - Practice Areas: Practice-specific analysis and trends
    - Trending: Historical trends and performance patterns
    
    Use the filters in the sidebar to customize the view according to your needs.
    """)
    
