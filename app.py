import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from io import StringIO

# Streamlit page config
st.set_page_config(page_title="AU Orders Report", layout="wide")

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state['theme'] = "Auto"

# Callback function to update theme on selection
def update_theme():
    st.session_state['theme'] = st.session_state['theme_select']

# Theme toggle with on_change callback
st.selectbox(
    "Theme",
    ["Auto", "Light", "Dark"],
    index=["Auto", "Light", "Dark"].index(st.session_state['theme']),
    key="theme_select",
    on_change=update_theme
)

# Apply theme override via CSS
theme = st.session_state['theme']
if theme == "Light":
    st.markdown("""
        <style>
        :root {
            --bg: #ffffff;
            --fg: #000000;
            --section-bg: #f5f5f5;
            --viz-bg: #e0e0e0;
            --table-bg: #f5f5f5;
            --border: #444444;
            --section-border: #333333;
            --header-border: #000000;
        }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Dark":
    st.markdown("""
        <style>
        :root {
            --bg: #000000;
            --fg: #ffffff;
            --section-bg: #1a1a1a;
            --viz-bg: #222222;
            --table-bg: #1a1a1a;
            --border: #444444;
            --section-border: #ffffff;
            --header-border: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

# Custom CSS: black/white theme, full-width layout
st.markdown("""
    <style>
    :root {
        --bg: #000000;
        --fg: #ffffff;
        --section-bg: #1a1a1a;
        --viz-bg: #222222;
        --table-bg: #1a1a1a;
        --border: #444444;
        --section-border: #ffffff;
        --button-bg: #0288d1;
        --button-hover: #0277bd;
        --header-border: #ffffff;
    }
    .stApp { 
        background-color: var(--bg); 
        font-family: 'Segoe UI', Arial, sans-serif;
        color: var(--fg) !important;
        padding: 0;
        margin: 0;
        color-scheme: auto;
        box-sizing: border-box;
        width: 100vw;
        max-width: 100%;
    }
    h1, h2, h3, h4, h5, h6 { 
        color: var(--fg) !important;
        font-weight: 700;
        padding: 10px 0;
        border-bottom: 2px solid var(--header-border);
        margin: 10px 0;
        text-align: center;
    }
    .sidebar .sidebar-content { 
        background-color: var(--section-bg); 
        border-right: 3px solid var(--border);
        color: var(--fg) !important;
        padding: 10px 5px;
        margin: 0;
        width: 100%;
        box-sizing: border-box;
    }
    .stMarkdown, .stWarning, .stError, .stWrite, .stCaption, 
    .stTextInput label, .stSelectbox label, .stDateInput label { 
        color: var(--fg) !important;
        margin: 10px 0;
        font-weight: 500;
    }
    .section { 
        background-color: var(--section-bg); 
        padding: 20px 10px; 
        border-radius: 10px; 
        box-shadow: 0 4px 8px rgba(255, 255, 255, 0.15);
        margin-bottom: 20px;
        color: var(--fg) !important;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
    }
    .section.viz-section {
        background-color: var(--viz-bg);
    }
    .section.feedback-section {
        background-color: var(--bg);
    }
    .section [data-testid="stMetric"], 
    .section [data-testid="stMetricLabel"], 
    .section [data-testid="stMetricValue"] { 
        background-color: var(--section-bg) !important;
        color: var(--fg) !important;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid var(--border);
        margin: 10px 0;
        width: 100%;
        box-sizing: border-box;
    }
    .section .stMarkdown, 
    .section .stMarkdown p { 
        color: var(--fg) !important;
    }
    .stButton>button {
        background-color: var(--button-bg);
        color: var(--fg) !important;
        border-radius: 8px;
        border: 2px solid var(--fg);
        padding: 10px 20px;
        font-weight: 600;
        transition: background-color 0.3s, opacity 0.2s;
        width: 100%;
        margin: 10px 0;
        box-sizing: border-box;
    }
    .stButton>button:hover {
        background-color: var(--button-hover);
        color: var(--fg) !important;
        opacity: 0.9;
    }
    .stDataFrame, .stDataFrame table { 
        color: var(--fg) !important;
        background-color: var(--table-bg) !important;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
        width: 100%;
        max-width: 100%;
        margin: 10px 0;
        box-sizing: border-box;
    }
    .stDataFrame table { 
        border: 2px solid var(--border);
    }
    .stDataFrame td, .stDataFrame th {
        border: 1px solid var(--border);
        padding: 12px;
        color: var(--fg) !important;
    }
    /* Fallback for chart colors */
    [data-testid="stPlotlyChart"], 
    [data-testid="stPlotlyChart"] > div, 
    [data-testid="stPlotlyChart"] > div > div {
        background-color: var(--viz-bg) !important;
    }
    @media (prefers-color-scheme: light) {
        :root {
            --bg: #ffffff;
            --fg: #000000;
            --section-bg: #f5f5f5;
            --viz-bg: #e0e0e0;
            --table-bg: #f5f5f5;
            --border: #444444;
            --section-border: #333333;
            --header-border: #000000;
        }
        [data-testid="stPlotlyChart"], 
        [data-testid="stPlotlyChart"] > div, 
        [data-testid="stPlotlyChart"] > div > div {
            background-color: #ffffff !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Password protection
password = st.text_input("Enter Password", type="password")
if password != "au_team_2025":  # Replace with a strong password
    st.error("Access denied")
    st.stop()

# Test message
st.write("Australia Location Review")

# Load order data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/lshawc/au-orders-dashboard/main/au_report.csv"
    try:
        df = pd.read_csv(url)
        required_cols = ['OrderID', 'OrderDate', 'PostalCode', 'State']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Error: Missing columns: {', '.join(missing_cols)}. Available: {', '.join(df.columns)}")
            st.stop()
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], format='%Y-%m-%d', errors='coerce')
        df['State'] = df['State'].fillna('Unknown')
        initial_len = len(df)
        df = df.dropna(subset=['OrderDate'])
        if len(df) < initial_len:
            st.warning(f"Removed {initial_len - len(df)} rows with invalid OrderDate values.")
        if df.empty:
            st.error("Error: No valid OrderDate values after cleaning.")
            st.stop()
        df = df.astype({'OrderID': str, 'PostalCode': str, 'State': str})
        if not df['OrderID'].str.startswith('AU').any():
            st.warning("No OrderIDs start with 'AU'. Expected from query WHERE ID LIKE 'AU%'.")
        return df
    except Exception as e:
        st.error(f"Error loading order data from {url}: {str(e)}")
        st.stop()

# Load postcode data
@st.cache_data
def load_postcode_data():
    url = "https://raw.githubusercontent.com/lshawc/au-orders-dashboard/main/postcode_data.csv"
    try:
        postcode_df = pd.read_csv(url)
    except:
        st.warning("Postcode data not found. Using sample data.")
        sample_csv = """postcode,place_name,state_name,state_code,latitude,longitude,accuracy
200,Australian National University,Australian Capital Territory,ACT,-35.2777,149.1189,1
221,Barton,Australian Capital Territory,ACT,-35.3049,149.1412,4
2540,Jervis Bay,Australian Capital Territory,ACT,-35.1333,150.7,4
2600,Deakin West,Australian Capital Territory,ACT,-35.3126,149.1278,3
2000,Sydney,New South Wales,NSW,-33.8688,151.2093,4
2010,Surry Hills,New South Wales,NSW,-33.8792,151.2070,4
3000,Melbourne,Victoria,VIC,-37.8136,144.9631,4
3001,Melbourne,Victoria,VIC,-37.8136,144.9631,4
"""
        postcode_df = pd.read_csv(StringIO(sample_csv))
    required_cols = ['postcode', 'place_name', 'state_name', 'state_code']
    missing_cols = [col for col in required_cols if col not in postcode_df.columns]
    if missing_cols:
        st.error(f"Postcode CSV missing columns: {', '.join(missing_cols)}")
        st.stop()
    postcode_df['postcode'] = postcode_df['postcode'].astype(str)
    if 'accuracy' in postcode_df.columns:
        postcode_df = postcode_df.sort_values(by=['postcode', 'accuracy'], ascending=[True, False])
    postcode_df = postcode_df.groupby('postcode').first().reset_index()
    initial_len = len(postcode_df)
    postcode_df = postcode_df.dropna(subset=['latitude', 'longitude'])
    if len(postcode_df) < initial_len:
        st.warning(f"Removed {initial_len - len(postcode_df)} rows with invalid lat/lon values.")
    return postcode_df

df = load_data()
postcode_df = load_postcode_data()

# Sidebar filters
st.sidebar.header("Filters")
state_options = sorted(df['State'].unique())
state_filter = st.sidebar.selectbox("State", ["All"] + state_options)
min_date = df['OrderDate'].min().date()
max_date = df['OrderDate'].max().date()
date_range = st.sidebar.date_input(
    "Order Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
order_id_filter = st.sidebar.text_input("Search OrderID", "")

# Filter data
filtered_df = df.copy()
if state_filter != "All":
    filtered_df = filtered_df[filtered_df['State'] == state_filter]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['OrderDate'].dt.date >= start_date) &
        (filtered_df['OrderDate'].dt.date <= end_date)
    ]
if order_id_filter:
    try:
        filtered_df = filtered_df[filtered_df['OrderID'].str.contains(order_id_filter, case=False, na=False)]
    except Exception as e:
        st.error(f"Invalid OrderID filter: {str(e)}")
        filtered_df = df.copy()

# Handle empty filtered data
if filtered_df.empty:
    st.warning("No orders match the selected filters.")
    st.stop()

# Determine if in light mode based on theme selection
is_light_mode = (theme == "Light") or (theme == "Auto" and st.get_option("theme.base") == "light")

# Summary section
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Summary")
total_orders = len(filtered_df)
top_state = filtered_df['State'].value_counts().index[0] if not filtered_df.empty else "N/A"
top_state_count = filtered_df['State'].value_counts().iloc[0] if not filtered_df.empty else 0
top_state_pct = (top_state_count / total_orders * 100) if total_orders > 0 else 0

# Calculate MoM growth/loss
mom_data = filtered_df.groupby(filtered_df['OrderDate'].dt.to_period('M')).size().reset_index(name='OrderCount')
mom_data['OrderCount'] = mom_data['OrderCount'].astype(float)
mom_data['MoM_Change'] = mom_data['OrderCount'].pct_change()
mom_data['MoM_Change'] = mom_data['MoM_Change'].apply(
    lambda x: 0 if pd.isna(x) or abs(x) == float('inf') else x * 100
)
latest_mom = mom_data['MoM_Change'].iloc[-1] if not mom_data.empty and len(mom_data) > 1 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", total_orders)
col2.metric("Top State", f"{top_state} ({top_state_pct:.1f}%)")
col3.metric("Latest MoM Growth", f"{latest_mom:.1f}%", delta_color="normal")

st.markdown(
    f"**Insight**: The top state, {top_state}, accounts for {top_state_pct:.1f}% of orders, "
    f"with a recent month-over-month change of {latest_mom:.1f}%, highlighting key regional trends."
)
st.markdown('</div>', unsafe_allow_html=True)

# Top Postal Codes Table
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Top 10 Postal Codes")
postal_counts = filtered_df.groupby(['PostalCode', 'State']).size().reset_index(name='OrderCount')
postal_counts = postal_counts.sort_values('OrderCount', ascending=False).head(10)
st.dataframe(
    postal_counts,
    use_container_width=True,
    column_config={
        "PostalCode": "Postal Code",
        "State": "State",
        "OrderCount": "Orders"
    }
)

# Top Suburbs Table
st.subheader("Top 10 Suburbs")
suburb_data = filtered_df.merge(
    postcode_df[['postcode', 'place_name', 'state_code']],
    left_on='PostalCode',
    right_on='postcode',
    how='left'
)
suburb_counts = suburb_data.groupby(['place_name', 'state_code']).size().reset_index(name='OrderCount')
suburb_counts = suburb_counts.sort_values('OrderCount', ascending=False).head(10)
missing_suburbs = suburb_counts[suburb_counts['place_name'].isna()]
if not missing_suburbs.empty:
    st.warning(
        f"{len(missing_suburbs)} postal codes could not be mapped to suburbs (e.g., {missing_suburbs['place_name'].iloc[0]}). "
        "These will appear as 'Unknown' in the table."
    )
suburb_counts['place_name'] = suburb_counts['place_name'].fillna('Unknown')
st.dataframe(
    suburb_counts,
    use_container_width=True,
    column_config={
        "place_name": "Suburb",
        "state_code": "State",
        "OrderCount": "Orders"
    }
)
st.markdown('</div>', unsafe_allow_html=True)

# Visualisations
st.header("Visualisations")
st.markdown('<div class="section viz-section">', unsafe_allow_html=True)

# Map of Australia
st.subheader("Orders by Postal Code")
postal_counts = filtered_df.groupby('PostalCode').size().reset_index(name='OrderCount')
map_data = postal_counts.merge(
    postcode_df[['postcode', 'latitude', 'longitude', 'state_name', 'place_name']],
    left_on='PostalCode',
    right_on='postcode',
    how='left'
)
missing_coords = map_data[map_data['latitude'].isna() | map_data['longitude'].isna()]
if not missing_coords.empty:
    st.warning(
        f"{len(missing_coords)} postcodes lack lat/lon data (e.g., {missing_coords['PostalCode'].iloc[0]}). "
        "These will not appear on the map."
    )
map_data = map_data.dropna(subset=['latitude', 'longitude'])

if not map_data.empty:
    fig_map = px.scatter_mapbox(
        map_data,
        lat='latitude',
        lon='longitude',
        size='OrderCount',
        color='OrderCount',
        color_continuous_scale='Blues',
        hover_data=['PostalCode', 'state_name', 'place_name', 'OrderCount'],
        title="Orders by Postal Code",
        size_max=30,
        zoom=3,
        center={"lat": -25.2744, "lon": 133.7751}
    )
    if is_light_mode:
        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin={"r":0, "t":0, "l":0, "b":0},
            font=dict(color="#000000"),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            coloraxis_colorbar_title="Orders"
        )
    else:
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin={"r":0, "t":0, "l":0, "b":0},
            font=dict(color="#ffffff"),
            paper_bgcolor="#222222",
            plot_bgcolor="#222222",
            coloraxis_colorbar_title="Orders"
        )
else:
    st.error("No valid lat/lon data available for mapping.")
    fig_map = px.scatter(
        postal_counts,
        x='PostalCode',
        y='OrderCount',
        size='OrderCount',
        hover_data=['PostalCode'],
        title="Orders by Postal Code (No Lat/Lon Data)",
        labels={'OrderCount': 'Number of Orders'},
        color_discrete_sequence=['#1976d2']
    )
    if is_light_mode:
        fig_map.update_layout(
            showlegend=False,
            font=dict(color="#000000"),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff"
        )
    else:
        fig_map.update_layout(
            showlegend=False,
            font=dict(color="#ffffff"),
            paper_bgcolor="#222222",
            plot_bgcolor="#222222"
        )
st.plotly_chart(fig_map, use_container_width=True)

# Bar Chart: Orders by State
st.subheader("Orders by State")
state_counts = filtered_df['State'].value_counts().reset_index()
state_counts.columns = ['State', 'OrderCount']
fig_bar = px.bar(
    state_counts,
    x='State',
    y='OrderCount',
    color='State',
    color_discrete_sequence=px.colors.sequential.Blues[::-1],
    title="Orders by State",
    labels={'OrderCount': 'Number of Orders'}
)
if is_light_mode:
    fig_bar.update_layout(
        showlegend=False,
        font=dict(color="#000000"),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
else:
    fig_bar.update_layout(
        showlegend=False,
        font=dict(color="#ffffff"),
        paper_bgcolor="#222222",
        plot_bgcolor="#222222"
    )
st.plotly_chart(fig_bar, use_container_width=True)

# Line Chart: Orders Over Time
st.subheader("Orders Over Time")
filtered_df['Month'] = filtered_df['OrderDate'].dt.to_period('M').astype(str)
time_counts = filtered_df.groupby('Month').size().reset_index(name='OrderCount')
fig_line = px.line(
    time_counts,
    x='Month',
    y='OrderCount',
    title="Orders Over Time",
    labels={'OrderCount': 'Number of Orders'},
    color_discrete_sequence=['#1976d2']
)
fig_line.update_traces(mode='lines+markers')
if is_light_mode:
    fig_line.update_layout(
        font=dict(color="#000000"),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
else:
    fig_line.update_layout(
        font=dict(color="#ffffff"),
        paper_bgcolor="#222222",
        plot_bgcolor="#222222"
    )
st.plotly_chart(fig_line, use_container_width=True)

# State-Level MoM Growth
st.subheader("State-Level MoM Growth")
state_mom_data = filtered_df.groupby(['State', filtered_df['OrderDate'].dt.to_period('M')]).size().reset_index(name='OrderCount')
state_mom_data['OrderDate'] = state_mom_data['OrderDate'].astype(str)
state_mom_data['OrderCount'] = state_mom_data['OrderCount'].astype(float)
state_mom_data['MoM_Change'] = state_mom_data.groupby('State')['OrderCount'].pct_change()
state_mom_data['MoM_Change'] = state_mom_data['MoM_Change'].apply(
    lambda x: 0 if pd.isna(x) or abs(x) == float('inf') else x * 100
)
if len(state_mom_data['OrderDate'].unique()) > 1 and state_mom_data['MoM_Change'].notna().any():
    fig_state_mom = px.line(
        state_mom_data,
        x='OrderDate',
        y='MoM_Change',
        color='State',
        title="Month-over-Month Growth by State (%)",
        labels={'MoM_Change': 'MoM Change (%)', 'OrderDate': 'Month'},
        color_discrete_sequence=px.colors.sequential.Blues[::-1]
    )
    fig_state_mom.update_traces(mode='lines+markers')
    if is_light_mode:
        fig_state_mom.update_layout(
            font=dict(color="#000000"),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=True
        )
    else:
        fig_state_mom.update_layout(
            font=dict(color="#ffffff"),
            paper_bgcolor="#222222",
            plot_bgcolor="#222222",
            showlegend=True
        )
    st.plotly_chart(fig_state_mom, use_container_width=True)
else:
    st.write("Insufficient data for state-level MoM analysis (need at least 2 months with valid data).")

# Growth/Loss Chart
st.subheader("Overall Month-over-Month Growth/Loss")
if len(mom_data) > 1:
    fig_mom = go.Figure()
    fig_mom.add_trace(go.Scatter(
        x=mom_data['OrderDate'].astype(str),
        y=mom_data['MoM_Change'].where(mom_data['MoM_Change'] >= 0),
        mode='lines+markers',
        name='Growth',
        line=dict(color='#388e3c')
    ))
    fig_mom.add_trace(go.Scatter(
        x=mom_data['OrderDate'].astype(str),
        y=mom_data['MoM_Change'].where(mom_data['MoM_Change'] < 0),
        mode='lines+markers',
        name='Loss',
        line=dict(color='#d32f2f')
    ))
    if is_light_mode:
        fig_mom.update_layout(
            title="Month-over-Month Growth/Loss (%)",
            xaxis_title="Month",
            yaxis_title="MoM Change (%)",
            showlegend=True,
            font=dict(color="#000000"),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff"
        )
    else:
        fig_mom.update_layout(
            title="Month-over-Month Growth/Loss (%)",
            xaxis_title="Month",
            yaxis_title="MoM Change (%)",
            showlegend=True,
            font=dict(color="#ffffff"),
            paper_bgcolor="#222222",
            plot_bgcolor="#222222"
        )
    st.plotly_chart(fig_mom, use_container_width=True)
    mom_data['MoM_Change'] = mom_data['MoM_Change'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
    st.dataframe(
        mom_data[['OrderDate', 'OrderCount', 'MoM_Change']].rename(
            columns={'OrderDate': 'Month', 'OrderCount': 'Orders', 'MoM_Change': 'MoM Change'}
        ),
        use_container_width=True
    )
else:
    st.write("Insufficient data for MoM analysis (need at least 2 months).")
st.markdown('</div>', unsafe_allow_html=True)

# Data Table with Drill-Down
st.header("Order Details")
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Filtered Orders")
if order_id_filter:
    st.write(f"Showing orders matching OrderID: {order_id_filter}")
elif state_filter != "All":
    st.write(f"Showing orders for State: {state_filter}")
else:
    st.write("Showing all orders")
page_size = 100
page_number = st.number_input("Page", min_value=1, value=1, step=1)
start_idx = (page_number - 1) * page_size
end_idx = start_idx + page_size
st.dataframe(
    filtered_df[['OrderID', 'OrderDate', 'PostalCode', 'State']].iloc[start_idx:end_idx],
    use_container_width=True
)
st.write(f"Showing rows {start_idx + 1} to {min(end_idx, len(filtered_df))} of {len(filtered_df)}")
st.markdown('</div>', unsafe_allow_html=True)

# Download button
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Download Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="au_orders_filtered.csv",
    mime="text/csv"
)
st.markdown('</div>', unsafe_allow_html=True)

# Feedback form
st.markdown('<div class="section feedback-section">', unsafe_allow_html=True)
st.header("Feedback")
feedback = st.text_area("Enter your feedback")
if st.button("Submit Feedback"):
    st.write("Thank you for your feedback!")
st.markdown('</div>', unsafe_allow_html=True)

# Conclusion
st.markdown('<div class="section feedback-section">', unsafe_allow_html=True)
st.header("Conclusion")
st.markdown(
    "This report visualizes AU orders by postal code and state, with enhanced mapping using lat/lon data, "
    "growth trends, and detailed breakdowns. Filters and drill-downs enable targeted analysis of regional "
    "and temporal patterns. *Note*: Renamed 'Top 10 Towns' to 'Top 10 Suburbs' and updated to use state abbreviations (e.g., NSW, VIC)."
)
st.markdown('</div>', unsafe_allow_html=True)
