
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
client relationships, attorney productivity, and practice area analysis.

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
