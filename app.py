import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from io import StringIO

# Streamlit page config
st.set_page_config(page_title="AU Orders Report", layout="wide")

# Custom CSS: black background, white text, preserve graph colors
st.markdown("""
    <style>
    .stApp { 
        background-color: #000000; 
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #ffffff !important;
    }
    h1, h2, h3, h4, h5, h6 { 
        color: #ffffff !important;
        font-weight: 600;
    }
    .sidebar .sidebar-content { 
        background-color: #1a1a1a; 
        border-right: 1px solid #333333;
        color: #ffffff !important;
    }
    .stMarkdown, .stWarning, .stError, .stWrite, .stCaption { 
        color: #ffffff !important;
    }
    .summary-section { 
        background-color: #000000; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #333333;
        color: #ffffff !important;
    }
    .summary-section [data-testid="stMetric"], 
    .summary-section [data-testid="stMetricLabel"], 
    .summary-section [data-testid="stMetricValue"], 
    .summary-section .css-1x8cf1d { 
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .summary-section .stMarkdown, 
    .summary-section .stMarkdown p { 
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #1976d2;
        color: #ffffff !important;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #1565c0;
        color: #ffffff !important;
    }
    .stDataFrame, .stDataFrame table, .stDataFrame td, .stDataFrame th { 
        color: #ffffff !important;
        background-color: #1a1a1a !important;
    }
    .stDataFrame table { 
        border: 1px solid #333333;
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

# Embedded sample data
order_csv = """OrderID,OrderDate,PostalCode,State
AU001,2024-01-15,200,ACT
AU002,2024-02-10,221,ACT
AU003,2024-03-05,2540,ACT
AU004,2024-03-20,2600,ACT
AU005,2024-04-01,200,ACT
AU006,2024-04-15,2540,ACT
"""

postcode_csv = """postcode,place_name,state_name,state_code,latitude,longitude,accuracy
200,Australian National University,Australian Capital Territory,ACT,-35.2777,149.1189,1
221,Barton,Australian Capital Territory,ACT,-35.3049,149.1412,4
2540,Jervis Bay,Australian Capital Territory,ACT,-35.1333,150.7,4
2600,Deakin West,Australian Capital Territory,ACT,-35.3126,149.1278,3
"""

# Load order data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(StringIO(order_csv))
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
        st.error(f"Error loading order data: {str(e)}")
        st.stop()

# Load postcode data
@st.cache_data
def load_postcode_data():
    try:
        postcode_df = pd.read_csv(StringIO(postcode_csv))
        required_cols = ['postcode', 'latitude', 'longitude']
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
    except Exception as e:
        st.error(f"Error loading postcode data: {str(e)}")
        st.stop()

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

# Summary section
st.markdown('<div class="summary-section">', unsafe_allow_html=True)
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

# Visualisations
st.header("Visualisations")

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
    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        margin={"r":0, "t":0, "l":0, "b":0},
        font=dict(color="#ffffff"),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
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
    fig_map.update_layout(
        showlegend=False,
        font=dict(color="#ffffff"),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000"
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
fig_bar.update_layout(
    showlegend=False,
    font=dict(color="#ffffff"),
    paper_bgcolor="#000000",
    plot_bgcolor="#000000"
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
fig_line.update_layout(
    font=dict(color="#ffffff"),
    paper_bgcolor="#000000",
    plot_bgcolor="#000000"
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
    fig_state_mom.update_layout(
        font=dict(color="#ffffff"),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
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
    fig_mom.update_layout(
        title="Month-over-Month Growth/Loss (%)",
        xaxis_title="Month",
        yaxis_title="MoM Change (%)",
        showlegend=True,
        font=dict(color="#ffffff"),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000"
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

# Data Table with Drill-Down
st.header("Order Details")
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

# Download button
st.header("Download Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="au_orders_filtered.csv",
    mime="text/csv"
)

# Conclusion
st.header("Conclusion")
st.markdown(
    "This report visualizes AU orders by postal code and state, with enhanced mapping using lat/lon data, "
    "growth trends, and detailed breakdowns. Filters and drill-downs enable targeted analysis of regional "
    "and temporal patterns."
)
