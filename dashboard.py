import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Config
st.set_page_config(page_title="Bike-Share Analytics", layout="wide", page_icon="🚲")

# Title and Introduction
st.title("🚲 Bike-Share Usage Analysis Dashboard")
st.markdown("Explore usage patterns, seasonal trends, and rider behaviors.")

# Data Loading
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cleaned_bikeshare.csv")
        
        # Date Conversion
        df['started_at'] = pd.to_datetime(df['started_at'])
        
        # Use pre-calculated features
        df['date'] = df['started_at'].dt.date
        
        # Rename columns to match existing dashboard variables
        if 'ride_duration' in df.columns:
            df.rename(columns={'ride_duration': 'duration_min'}, inplace=True)
        if 'start_hour' in df.columns:
            df.rename(columns={'start_hour': 'hour'}, inplace=True)
            
        # Optimize memory
        df['member_casual'] = df['member_casual'].astype('category')
        df['rideable_type'] = df['rideable_type'].astype('category')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    # Sidebar Filters
    st.sidebar.header("Filter Data")
    
    # 1. Date Range
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 2. Rider Type
    rider_types = df['member_casual'].unique()
    selected_rider_type = st.sidebar.multiselect("Rider Type", rider_types, default=rider_types)
    
    # Apply Filters
    mask = (df['date'] >= date_range[0]) & (df['date'] <= date_range[1]) & (df['member_casual'].isin(selected_rider_type))
    filtered_df = df.loc[mask]
    
    # KPIs
    st.markdown("### Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    
    total_rides = len(filtered_df)
    avg_duration = filtered_df['duration_min'].mean()
    top_station = filtered_df['start_station_name'].mode()[0] if not filtered_df.empty else "N/A"
    
    col1.metric("Total Rides", f"{total_rides:,}")
    col2.metric("Avg Duration (min)", f"{avg_duration:.2f}")
    col3.metric("Top Start Station", top_station)
    
    st.divider()
    
    # Charts Layout
    col_chart1, col_chart2 = st.columns(2)
    
    # 1. Rides Over Time
    daily_rides = filtered_df.groupby('date').size().reset_index(name='count')
    fig_daily = px.line(daily_rides, x='date', y='count', title='Daily Rides Over Time', markers=True)
    col_chart1.plotly_chart(fig_daily, use_container_width=True)
    
    # 2. Peak Hours Analysis
    hourly_rides = filtered_df.groupby('hour').size().reset_index(name='count')
    fig_hourly = px.bar(hourly_rides, x='hour', y='count', title='Peak Usage Hours', 
                        labels={'hour': 'Hour of Day', 'count': 'Number of Rides'})
    col_chart2.plotly_chart(fig_hourly, use_container_width=True)
    
    col_chart3, col_chart4 = st.columns(2)

    # 3. Rider Type Distribution
    rider_dist = filtered_df['member_casual'].value_counts().reset_index()
    fig_pie = px.pie(rider_dist, names='member_casual', values='count', title='Rider Type Distribution', hole=0.4)
    col_chart3.plotly_chart(fig_pie, use_container_width=True)
    
    # 4. Map (Sampled for performance)
    st.markdown("### Ride Starting Locations (Sampled 1000 pts)")
    if not filtered_df.empty:
        map_data = filtered_df.dropna(subset=['start_lat', 'start_lng']).sample(min(1000, len(filtered_df)))
        fig_map = px.scatter_mapbox(map_data, lat="start_lat", lon="start_lng", color="member_casual",
                                    zoom=10, mapbox_style="open-street-map", title="Start Stations Map")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No data available for map.")

else:
    st.warning("Please ensure bikeshare.csv is in the same directory.")
