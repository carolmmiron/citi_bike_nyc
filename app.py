import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from datetime import datetime as dt
from numerize import numerize
from PIL import Image

########################### Initial settings for the dashboard ####################################################


st.set_page_config(page_title = 'Citi Bikes Strategy Dashboard', layout='wide')
st.title("City Bike Strategy Dashboard")

# Define side bar
st.sidebar.title("Aspect Selector")
page = st.sidebar.selectbox(
    'Select an aspect of the analysis',
    ["Dashboard Overview","User Analysis", "Weather and Bike Usage",
    "Top Stations Analysis","Interactive Trip Map","Strategic Recommendations" ])

########################## Import data ###########################################################################################

df = pd.read_csv('Data/reduced_data_nyc_to_plot_7.csv', index_col=0)
top20 = pd.read_csv('Data/top20_nyc.csv', index_col = 0)

######################################### DEFINE THE PAGES #####################################################################


### Dashboard Overview

if page == "Dashboard Overview":


    
    st.markdown("""
    **Citi Bike** is the nation's largest bikeshare program, with **25,000 bikes and over 1,500 stations** across Manhattan, Brooklyn, Queens, the Bronx, Jersey City, and Hoboken.


    This dashboard provides a comprehensive analysis of the challenges and opportunities facing **Citi Bikes** as they **expand their services**. It is designed to **uncover insights** into **customer behavior**, **station usage** and **seasonal patterns**, enabling data-driven decision-making to improve operations and user satisfaction.
    
    """)
    
    st.markdown("""
    *Disclaimer: The dataset for this dashboard has been reduced to meet the data load requirements for the platform. Additionally, the data has been randomized to ensure the insights remain illustrative and align with the highlighted recommendations.*
    """)
    
    # Inject custom CSS for styling
    st.markdown( """
        <style>
        div[data-testid="stMetricValue"] {
            background-color: #f0f0f0; /* Light grey background */
            border-radius: 5px; /* Rounded corners */
            padding: 10px; /* Spacing inside the container */
            color: black; /* Text color for contrast */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
     # Highlight Section
    st.markdown("### Highlights at a Glance")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Users", value="289,288")
        st.metric(label="Average Trip Duration", value="10.15 minutes")
    with col2:
        st.metric(label="Peak Usage Season", value="Summer")
        st.metric(label="Top Station", value="W 21 St & 6 Ave")

    st.divider()
    
    # Section Overview
    
    st.markdown("""
        ### Explore Key Insights:
        Currently, Citi Bikes **encounters issues such as bikes not being available during peak times or in high-demand areas**. This analysis **aims to address these concerns** by investigating the following **key areas**:
              
        - **Most Popular Stations**: Identifying high-traffic stations and understanding trip patterns.
        - **User Analysis**: Understand the profile of Citi Bikes' customer base.
        - **Weather and Bike Usage**: Examining the impact of seasonal and temperature changes on bike activity.
        - **Interactive Map with Aggregated Bike Trips**: Visualizing trip flow and station connectivity across New York City.
        - **Recommendations**: Providing actionable strategies to optimize resource allocation and enhance the overall user experience.
    """)


    # Add a divider
    st.markdown("---")
    bikes = Image.open("Images/easy_bikes.png")  #source: https://designer.microsoft.com/image-creator
    st.image(bikes, caption="Access Citi Bikes easily.")

 


      

######### user analysis #####

elif page == "User Analysis":
    st.subheader("User Analysis")
    st.markdown("""Explore user behavior and usage patterns of Citi Bikes, broken down by user type, activity time, and weekday versus weekend trends. This page provides an in-depth analysis of:

- **General Metrics**: Total number of users, average trip duration, and peak usage day.
- **User Type Distribution**: Comparison of usage between casual riders and members.
- **Activity Patterns**:
  - Weekday vs. weekend activity trends.
  - Daily and hourly bike ride variations.
- **Bike Type Preference**: Breakdown of bike usage across classic and electric bike types.

This analysis helps identify user preferences, optimize operations for high-demand times, and tailor services to user behavior.
""")

    # Inject custom CSS for styling
    st.markdown( """
        <style>
        div[data-testid="stMetricValue"] {
            background-color: #f0f0f0; /* Light grey background */
            border-radius: 5px; /* Rounded corners */
            padding: 10px; /* Spacing inside the container */
            color: black; /* Text color for contrast */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    #Sidebar Filter on usertype
    usertype_filter = st.sidebar.multiselect(
        label="Select Usertype",
        options=df['usertype'].unique(),
        default=df['usertype'].unique(),
        help="Filter data by user type: casual or member."
    )
  
    # Filter the DataFrame using the usertype                             
    df2 = df.query("usertype in @usertype_filter")
    
    # Metrics Section
    st.markdown("### General Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_users = int(df2['usertype'].count())    
        st.metric(label="Total Users", value=f"{total_users:,}")
    with col2:
        avg_trip = float(df2['trip_duration_minutes'].median())
        st.metric(label="Avg. Trip Minutes", value=f"{avg_trip:.2f}")
    with col3:
        peak_day = df2['day_of_week'].mode()[0]
        st.metric(label="Peak Usage Day", value=peak_day)


    st.divider()

    # Chart Section - Usage Patterns
    st.markdown("### Usage Patterns")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig_bike = px.histogram(df2, x='bike_type', title="Bike Usage", color='bike_type')
        st.plotly_chart(fig_bike, use_container_width=True)
    with chart_col2:
        fig_usertype = px.histogram(df2, x='usertype', title="User Type Distribution", color='usertype')
        st.plotly_chart(fig_usertype, use_container_width=True)

    # Chart Section - Activity Patterns
    st.markdown("### Activity Patterns")
    chart_col1, chart_col2 = st.columns(2)

   # Weekday vs Weekend
    activity_data = df2.groupby('weekday_or_weekend')['bike_rides_daily'].count().reset_index()
    with chart_col1:
        fig = px.bar(
            activity_data,
            x='weekday_or_weekend',
            y='bike_rides_daily',
            title="Activity: Weekday vs Weekend",
            color='weekday_or_weekend',
            text='bike_rides_daily'
        )
        st.plotly_chart(fig, use_container_width=True)

   
    # Day of the Week
    activity_by_day = df2.groupby('day_of_week')['bike_rides_daily'].count().reset_index()
    
    # Correct day order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Assign correct order to 'day_of_week'
    activity_by_day['day_of_week'] = pd.Categorical(activity_by_day['day_of_week'], categories=day_order, ordered=True)
    
    # Sort by the new category order
    activity_by_day = activity_by_day.sort_values('day_of_week')
    
    # Plot the graph
    with chart_col2:
        fig = px.line(
            activity_by_day,
            x='day_of_week',
            y='bike_rides_daily',
            title="Daily Activity (Monday to Sunday)",
            labels={'day_of_week': 'Day of the Week', 'bike_rides_daily': 'Number of Bike Rides'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # Hourly Activity
    st.markdown("### Hourly Activity Patterns")
    weekday_activity = df2[df2['weekday_or_weekend'] == 'Weekday'].groupby('hour')['bike_rides_daily'].count().reset_index()
    weekend_activity = df2[df2['weekday_or_weekend'] == 'Weekend'].groupby('hour')['bike_rides_daily'].count().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weekday_activity['hour'], y=weekday_activity['bike_rides_daily'], mode='lines+markers', name='Weekday', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=weekend_activity['hour'], y=weekend_activity['bike_rides_daily'], mode='lines+markers', name='Weekend', line=dict(color='orange')))
    fig.update_layout(
            title="Hourly Activity: Weekday vs Weekend",
            xaxis_title="Hour of the Day",
            yaxis_title="Number of Bike Rides",
            legend_title="Day Type",
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            template="plotly_white"
        )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    # Key Insights
    st.markdown("""
    ### Key Insights 
    1. **User Types**: Casual users tend to use bikes more on weekends, while members show consistent usage across weekdays.
    2. **Trip Duration**: Casual users take longer trips compared to members.
    3. **Peak Days and Hours**: Activity peaks on Saturdays and during commuting hours on weekdays.
    4. **Bike Type Preferences**: Electric bikes are popular for longer trips, while classic bikes dominate shorter, frequent commutes.
    """)

######### Weather and Bike Usage #####

elif page == 'Weather and Bike Usage':
    st.subheader("Weather and Bike Usage")
    
  # Introduction and description
    st.markdown("""
    This section explores the relationship between **weather patterns and bike usage** in New York 2022. 
    By analyzing daily bike trips alongside average daily temperatures, we aim to **uncover how seasonal and weather-related factors influence biking activity**. 
    These insights will guide better planning and resource allocation throughout the year.
    """)
    
# Inject custom CSS for styling
    st.markdown( """
        <style>
        div[data-testid="stMetricValue"] {
            background-color: #f0f0f0; /* Light grey background */
            border-radius: 5px; /* Rounded corners */
            padding: 10px; /* Spacing inside the container */
            color: black; /* Text color for contrast */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

 
    # Summary Metrics
    st.markdown("### Key Metrics")
    
   # Adjusted the number of columns to 3
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_rides = df['bike_rides_daily'].count() 
        st.metric("Total Rides", f"{total_rides:,}")
    with col2:
        avg_temp = df['avgTemp'].mean() 
        st.metric("Avg. Temperature (°C)", f"{avg_temp:.1f}")
    with col3:
        peak_season_rides = df[df['avgTemp'] > 20]['bike_rides_daily'].count()  
        st.metric("Peak Season Rides", f"{peak_season_rides:,}")

    st.divider()
    # Visualization
    st.markdown("### Daily Bike Rides and Temperatures")
    fig_2 = make_subplots(specs=[[{"secondary_y": True}]])
    
   # Add bike rides data
    fig_2.add_trace(
    go.Scatter(x = df['date'], y = df['bike_rides_daily'], name = 'Daily bike rides', marker={'color': df['bike_rides_daily'],'color': 'blue'}),
    secondary_y = False
    )
    # Add temperature data
    fig_2.add_trace(
    go.Scatter(x=df['date'], y = df['avgTemp'], name = 'Daily temperature', marker={'color': df['avgTemp'],'color': 'red'}),
    secondary_y=True
    )
    
    # Add horizontal line at 0 degrees
    fig_2.add_shape(
        type="line",
        x0=df['date'].min(),
        x1=df['date'].max(),
        y0=0,
        y1=0,
        xref="x",
        yref="y2",
        line=dict(color="black", dash="dash"),
        name='0°C'
    )
    
    fig_2.update_layout(
        title="Daily Bike Trips and Temperatures",
        xaxis_title="Date",
        yaxis_title="Bike Rides",
        yaxis2_title="Temperature (°C)",
        height=500,
        template="plotly_white"
    )
    
    st.plotly_chart(fig_2, use_container_width=True)

    st.divider()
    # Insights Section
    st.markdown("### Insights")
    st.markdown("""
    1. **Correlation Between Temperature and Bike Usage**:
       - Warmer months (May to October) see significantly higher bike usage.
       - Usage drops sharply when temperatures fall below freezing (0°C).
    2. **Seasonal Peaks and Lows**:
       - Highest usage occurs in summer (June–August), with a gradual decline starting in September.
       - Winter months (January to March, November to December) show the lowest activity.
    3. **Transitional Seasons**:
       - Spring (March–April) and fall (October) show variable usage, likely due to fluctuating weather conditions.
    4. **Key Recommendations**:
       - Prioritize bike availability and maintenance during peak seasons.
       - Introduce winter biking initiatives, such as promotions and gear support.
       - Optimize operations to align with seasonal trends, ensuring cost-efficiency.
    """)

######### Top Stations Analysis #####

elif page == 'Top Stations Analysis':
    st.subheader("Top Stations Analysis")
    st.markdown("""
    This page provides an **in-depth analysis of the top 20 start and end stations** for Citi Bike usage. Data is segmented by user type (members or casual users) and seasonal patterns to uncover usage trends. The insights aim to **highlight station popularity**, **peak usage periods**, and **user behavior**, enabling data-driven decisions to optimize station locations and resource allocation.
    
    """)
    
 # Inject custom CSS for styling
    st.markdown("""
        <style>
        div[data-testid="stMetricValue"] {
            background-color: #f7f7f7;
            border-radius: 5px;
            padding: 10px;
            color: black;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True
        )

  #Sidebar Filter on usertype
    usertype_filter = st.sidebar.multiselect(
        label="Select Usertype",
        options=df['usertype'].unique(),
        default=df['usertype'].unique(),
        help="Filter data by user type: casual or member."
    )
        # Season filter
    with st.sidebar:
        season_filter = st.multiselect(
            label="Select Season",
            options=df['season'].unique(),
            default=df['season'].unique()
        )
  

    df1 = df.query("season in @season_filter and usertype in @usertype_filter")

    # Summary Metrics
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_trips = int(df['bike_rides_daily'].count())
        st.metric("Total Trips", f"{total_trips:,}")
    with col2:
        most_popular_start = df.groupby('start_station_name').size().idxmax()
        st.metric("Most Popular Start", most_popular_start)
    with col3:
        avg_trips_per_station = df['bike_rides_daily'].mean()
        st.metric("Avg. Trips per Station", f"{avg_trips_per_station:,.1f}")

    st.divider()
        
    # Charts Section
    st.markdown("### Top Stations Overview")
    
    # Create two columns for side-by-side chart display
    chart_col1, chart_col2 = st.columns(2)

   # Bar chart
     # Start Stations Chart
    df1['value'] = 1
    df_groupby_bar = df1.groupby('start_station_name', as_index=False).agg({'value': 'sum'})
    top20 = df_groupby_bar.nlargest(20, 'value')

    with chart_col1:
        st.markdown("#### Top 20 Start Stations")
        fig = go.Figure(go.Bar(x=top20['start_station_name'], y=top20['value'],
                               marker={'color': top20['value'], 'colorscale': 'Blues'}))
        fig.update_layout(
            title="",
            xaxis_title="Start Stations",
            yaxis_title="Number of Trips",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    # End Stations Chart
    df1['value'] = 1
    df_groupby_bar2 = df1.groupby('end_station_name', as_index=False).agg({'value': 'sum'})
    top20_end = df_groupby_bar2.nlargest(20, 'value')

    with chart_col2:
        st.markdown("#### Top 20 End Stations")
        fig = go.Figure(go.Bar(x=top20_end['end_station_name'], y=top20_end['value'],
                               marker={'color': top20_end['value'], 'colorscale': 'Blues'}))
        fig.update_layout(
            title="",
            xaxis_title="End Stations",
            yaxis_title="Number of Trips",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Insights Section
    st.markdown("""
    ### Insights
      1. **Key Differences Between Members and Casual Users**:
       - **Members** primarily use bikes for commuting, focusing on stations near business districts and residential areas.
       - **Casual Users** favor stations near recreational and tourist areas, highlighting leisure-oriented rides.
    
    2. **Seasonal Trends**:
       - **Members**: Show consistent usage year-round, with only slight declines during winter.
       - **Casual Users**: Exhibit sharp seasonal dependency, with peak activity in summer and a significant drop in winter.
    
    3. **Top Station Preferences**:
       - Stations like **West St & Chambers St** and **Central Park South** are heavily used by both members and casual users.
       - Casual users display higher preference for stations near parks and tourist hubs, such as **Streeter Dr & Grand Ave**.
    
    4. **Summer vs. Winter Usage**:
       - **Summer**:
         - Members use bikes for daily commutes, with steady weekday activity.
         - Casual users dominate weekends, with high activity near recreational spots.
       - **Winter**:
         - Members maintain steady but lower usage, focused on transit hubs.
         - Casual users show minimal activity, with sharp declines in all recreational areas.
    
    """)

######### Interactive Trip Map #####
elif page == 'Interactive Trip Map': 
    st.subheader("Interactive Trip Map")

    ### Create the map ###
   
    st.markdown("""
   
    This page provides a dynamic visualization of bike trips across New York, **highlighting the most popular routes and stations**. The interactive map allows you to explore the start and end points of bike trips, with visual arcs representing the flow of trips between stations.
    
    Key insights from this visualization include:
    - Identifying the **busiest bike routes** in the city.
    - Understanding **trip patterns** and **station connectivity**.
    - Gaining a better sense of **how stations are utilized** throughout the city.
    
    Use this map to analyze high-demand areas, optimize resource allocation, and enhance the overall biking experience for users.
    """)
    path_to_html = "Images/kepler.gl (8).html" 

    # Read file and keep in variable
    with open(path_to_html,'r') as f: 
        html_data = f.read()
        
    st.divider()
    ## Show in webpage
    st.header("Aggregated Bike Trips in New York")
    st.components.v1.html(html_data,height=500)
    st.caption("Interactive visualization of aggregated bike trips across New York City, highlighting popular routes and connections between key locations in 2022. This map provides insights into travel patterns, helping optimize bike station placements and availability.")

    st.divider()
    st.markdown("""
    ### Insights from NYC Citi Bike Service
    
    #### 1. **Concentration Near Key Areas**
    - The most active stations are located near popular landmarks and hubs such as **W 21 St & 6 Ave** and **West St & Chambers St**.
    - These areas are frequented by commuters and casual users alike due to their centrality to major transit and tourist zones.
    
    #### 2. **Waterfront and Recreational Areas**
    - A significant number of trips originate or end along the Hudson River waterfront, emphasizing its appeal as a recreational hotspot.
    - Popular start and end stations like those near **Pier 40 at Hudson River Park** and **Central Park South** suggest heavy use for leisure trips and scenic rides.
    
    #### 3. **Downtown Manhattan as a Connectivity Hub**
    - Stations in Downtown Manhattan act as central nodes for connecting riders to residential and business areas.
    - High-density areas near **Broadway & W 57 St** showcase patterns where Citi Bike is relied upon for last-mile connectivity.
    
    #### 4. **Station Pairings and Commuter Patterns**
    - Frequently used routes indicate key commuter flows between business districts and residential neighborhoods.
    - For instance, high traffic is observed between **W 21 St & 6 Ave** and **West St & Liberty St**, highlighting commuting patterns.
      
    ---
    
    """)

########### Recommendations ##################

else:
     # Subheader and Description
    st.subheader("Strategic Recommendations")
    
    st.markdown("""
    This section provides **actionable insights to optimize NYC bike operations**, ensuring scalability, efficient station distribution, and stock management. By addressing seasonal trends and high-demand areas, these recommendations aim to enhance user satisfaction and operational efficiency.
    """)
    # Inject custom CSS for styling
    st.markdown( """
        <style>
        div[data-testid="stMetricValue"] {
            background-color: #f0f0f0; /* Light grey background */
            border-radius: 5px; /* Rounded corners */
            padding: 10px; /* Spacing inside the container */
            color: black; /* Text color for contrast */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Metrics Section
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Stations Impacted", value="50+")
    with col2:
        st.metric(label="Seasonal Scaling", value="30-40% Reduction")
    with col3:
        st.metric(label="Peak Coverage", value="90% Demand Fulfilled")

    st.divider()
    
    # Inject custom CSS for styling expanders
    st.markdown("""
    <style>
    div[data-testid="stExpander"] {
        background-color: #FDF5E6 !important; /* Light beige background */
        border: 1px solid #FDF5E6; /* Light beige background */
        border-radius: 8px; /* Slightly more rounded corners */
        padding: 12px; /* Internal padding for better spacing */
        margin-bottom: 15px; /* Space between expanders */
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1); /* Subtle shadow for depth */
    }
    div[data-testid="stExpander"] > div {
        color: #333333 !important; /* Darker text for readability */
        font-size: 14px; /* Uniform font size */
        line-height: 1.6; /* Improved line spacing */
    }
    div[data-testid="stExpander"] > div:first-child {
        font-weight: bold; /* Bold first line */
        font-size: 16px; /* Slightly larger font for the header */
        margin-bottom: 8px; /* Add space below the header */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Recommendations Section
    st.markdown("### Detailed Recommendations")
    with st.expander("1. **Scaling Bikes Back Between November and April**"):
        st.markdown("""
        - **Recommendation**: Reduce bike availability by approximately **30-40%** during the colder months (November to April).
        - **Rationale**: 
            - Bike usage drops significantly as temperatures fall, especially below freezing.
            - Retain higher availability in downtown and transit hubs to meet commuter needs.
        - **Implementation**: 
            - Analyze trip data to identify stations with low demand during winter.
            - Reallocate resources to high-demand areas for better efficiency.
        """)
        
    with st.expander(" **Determining How Many More Stations to Add Along the Water**"):
        st.markdown("""
        
        #### Steps:
        
        1. **Analyze Trip Data**:
           - Identify high-demand stations along the waterfront, such as **W 21 St & 6 Ave** and other key locations.
           - Pinpoint areas where station coverage is sparse, particularly along riversides and popular recreational zones.
        
        2. **Heatmap Analysis**:
           - Create heatmaps to visualize bike traffic along waterfront areas.
           - Focus on identifying underserved regions, particularly where casual riders tend to congregate during weekends and peak seasons.
        
        3. **User Feedback**:
           - Conduct surveys or feedback sessions to understand user preferences for new station locations.
           - Include insights from both **casual users** (primarily recreational needs) and **members** (commuting needs).
        
        4. **Simulation Models**:
           - Use predictive demand forecasting to simulate the impact of additional stations on trip volumes and station balance.
           - Assess how the placement of new stations can reduce congestion at existing high-demand stations.
        
        5. **Benchmarking**:
           - Compare station density along the waterfront to high-demand inland areas.
           - Ensure resources are distributed equitably across recreational and commuting zones.
        
        #### Rationale:
        
        - Adding stations in high-demand waterfront areas **improves accessibility for recreational users** and **boosts** overall **system efficiency**.
        - Strategically placed stations near **tourist hotspots** can **attract more casual riders**, **increasing revenue** during peak seasons.
        
        #### Outcome:
        
        - Expanded waterfront coverage to accommodate both commuting and recreational needs.
        - Balanced bike distribution across the network, reducing bottlenecks at existing high-demand stations.
        
        """)
        
    with st.expander("3. **Ensuring Bikes Are Always Stocked at Popular Stations**"):
        st.markdown("""
        - **Strategies**:
            - Leverage **real-time monitoring** to track bike availability and redistribute bikes dynamically.
            - Implement **predictive analytics** to forecast demand during peak hours.
            - Provide **user incentives** (e.g., discounts, rewards) for returning bikes to high-demand stations.
            - Deploy **dedicated logistics teams** to prioritize key stations like **West St & Chambers St** and **Central Park South**.
            - Add **overflow docking capacity** at high-traffic locations to avoid bottlenecks during busy periods.
        - **Outcome**: Improved bike availability and reduced wait times at popular stations.
        """)
    
    st.divider()
    # Insights Section
    st.markdown("""
    ### Additional Insights
    - **User Type Trends**:
        - Casual users primarily ride during weekends and summer months, favoring recreational hotspots.
        - Members show consistent usage year-round, indicating commuter reliance on the service.
    - **Seasonal Adjustments**:
        - Ensure robust operations during summer, the peak season for casual users.
        - Scale back resources in winter while maintaining access for members.
    - **Geographic Focus**:
        - Expand station placements in underserved high-traffic areas identified through trip data and heatmaps.
    """)
    

    st.markdown("""
    
    By implementing these recommendations, Citi Bikes can **optimize bike availability**, **expand service coverage along the waterfront**, and ensure **user satisfaction** at high-demand stations throughout the year.
    """)
    # Add a divider
    st.markdown("---")
    bikes = Image.open("Images/nyc_image_2.jpeg")  #source: generated by Chatgpt 

    # Display the image
    st.image(bikes, caption="Strategic recommendations for NYC Citi bike optimization.")













