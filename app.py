from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

########################### Initial settings for the dashboard ###########################

st.set_page_config(page_title="Citi Bike Strategy Dashboard", layout="wide")
st.title("Citi Bike Strategy Dashboard")

# Shared styling (applies to every page)
st.markdown(
    """
    <style>
    div[data-testid="stMetricValue"] {
        background-color: #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        color: black;
    }
    div[data-testid="stExpander"] {
        background-color: #FDF5E6;
        border: 1px solid #FDF5E6;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Side bar
st.sidebar.title("Aspect Selector")
page = st.sidebar.selectbox(
    "Select an aspect of the analysis",
    [
        "Dashboard Overview",
        "User Analysis",
        "Weather and Bike Usage",
        "Top Stations Analysis",
        "Interactive Trip Map",
        "Strategic Recommendations",
    ],
)

########################### Import data ###########################

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
COLUMNS = [
    "bike_type", "start_station_name", "end_station_name", "usertype", "date",
    "avgTemp", "bike_rides_daily", "trip_duration_minutes", "month", "season",
    "weekday_or_weekend", "day_of_week", "hour",
]


@st.cache_data
def load_data():
    """Random ~3% sample of all 2022 Citi Bike trips, one row per trip."""
    df = pd.read_csv("Data/citibike_2022_sample.csv.gz", usecols=COLUMNS, parse_dates=["date"])
    # Durations below 1 min or above 3 h are docking errors / lost bikes, not real trips
    df["valid_duration"] = df["trip_duration_minutes"].between(1, 180)
    return df


@st.cache_data
def daily_table(df):
    """One row per day: total rides in the full 2022 dataset + average temperature."""
    daily = (
        df.groupby("date", as_index=False)
        .agg(bike_rides_daily=("bike_rides_daily", "first"), avgTemp=("avgTemp", "first"))
        .sort_values("date")
    )
    return daily


df = load_data()
daily = daily_table(df)

TOTAL_TRIPS_2022 = int(daily["bike_rides_daily"].sum())
SAMPLE_SIZE = len(df)
SAMPLE_SHARE = SAMPLE_SIZE / TOTAL_TRIPS_2022


def rides_per_day(data, column, order=None):
    """Average number of sampled trips per calendar day, so groups with more days are not favoured."""
    trips = data.groupby(column).size()
    days = data.groupby(column)["date"].nunique()
    out = (trips / days).rename("avg_trips_per_day").reset_index()
    if order:
        out[column] = pd.Categorical(out[column], categories=order, ordered=True)
        out = out.sort_values(column)
    return out


def usertype_filter_widget():
    return st.sidebar.multiselect(
        label="Select Usertype",
        options=sorted(df["usertype"].unique()),
        default=sorted(df["usertype"].unique()),
        help="Filter data by user type: casual or member.",
    )


########################### DEFINE THE PAGES ###########################

### Dashboard Overview
if page == "Dashboard Overview":

    st.markdown(
        """
    **Citi Bike** is the nation's largest bikeshare program, with **25,000 bikes and over 1,500 stations** across Manhattan, Brooklyn, Queens, the Bronx, Jersey City, and Hoboken.

    This dashboard provides a comprehensive analysis of the challenges and opportunities facing **Citi Bike** as it **expands its services**. It is designed to **uncover insights** into **customer behavior**, **station usage** and **seasonal patterns**, enabling data-driven decision-making to improve operations and user satisfaction.
    """
    )

    st.caption(
        f"Data: {TOTAL_TRIPS_2022:,} Citi Bike trips from 2022 combined with NOAA daily temperatures. "
        f"Trip-level charts use a random sample of {SAMPLE_SIZE:,} trips (~{SAMPLE_SHARE:.0%}) to fit the hosting limits; "
        "daily totals use the full dataset."
    )

    st.markdown("### Highlights at a Glance")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Trips Analysed (2022)", value=f"{TOTAL_TRIPS_2022:,}")
        median_trip = df.loc[df["valid_duration"], "trip_duration_minutes"].median()
        st.metric(label="Median Trip Duration", value=f"{median_trip:.1f} minutes")
    with col2:
        peak_season = df["season"].value_counts().idxmax().capitalize()
        st.metric(label="Peak Usage Season", value=peak_season)
        st.metric(label="Top Start Station", value=df["start_station_name"].value_counts().idxmax())

    st.divider()

    st.markdown(
        """
        ### Explore Key Insights:
        Currently, Citi Bike **encounters issues such as bikes not being available during peak times or in high-demand areas**. This analysis **aims to address these concerns** by investigating the following **key areas**:

        - **User Analysis**: Understand the profile of Citi Bike's customer base.
        - **Weather and Bike Usage**: Examining the impact of seasonal and temperature changes on bike activity.
        - **Most Popular Stations**: Identifying high-traffic stations and understanding trip patterns.
        - **Interactive Map with Aggregated Bike Trips**: Visualizing trip flow and station connectivity across New York City.
        - **Recommendations**: Providing actionable strategies to optimize resource allocation and enhance the overall user experience.
    """
    )

    st.markdown("---")
    bikes = Image.open("Images/easy_bikes.png")  # source: https://designer.microsoft.com/image-creator
    st.image(bikes, caption="Access Citi Bike easily.")


### User Analysis
elif page == "User Analysis":
    st.subheader("User Analysis")
    st.markdown(
        """Explore user behavior and usage patterns of Citi Bike, broken down by user type, activity time, and weekday versus weekend trends. This page provides an in-depth analysis of:

- **General Metrics**: Number of trips, median trip duration, and peak usage day.
- **User Type Distribution**: Comparison of usage between casual riders and members.
- **Activity Patterns**: Weekday vs. weekend activity, and daily and hourly variations.
- **Bike Type Preference**: Breakdown of bike usage across classic and electric bike types.
"""
    )

    usertype_filter = usertype_filter_widget()
    df2 = df[df["usertype"].isin(usertype_filter)]

    if df2.empty:
        st.warning("Select at least one user type in the sidebar.")
        st.stop()

    st.markdown("### General Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Trips in Sample", value=f"{len(df2):,}")
    with col2:
        median_trip = df2.loc[df2["valid_duration"], "trip_duration_minutes"].median()
        st.metric(label="Median Trip Minutes", value=f"{median_trip:.1f}")
    with col3:
        peak_day = rides_per_day(df2, "day_of_week").sort_values("avg_trips_per_day").iloc[-1]["day_of_week"]
        st.metric(label="Peak Usage Day", value=peak_day)

    st.divider()

    st.markdown("### Usage Patterns")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig_bike = px.histogram(df2, x="bike_type", title="Bike Usage", color="bike_type")
        fig_bike.update_layout(yaxis_title="Trips", xaxis_title="Bike type", showlegend=False)
        st.plotly_chart(fig_bike, width="stretch")
    with chart_col2:
        fig_usertype = px.histogram(df2, x="usertype", title="User Type Distribution", color="usertype")
        fig_usertype.update_layout(yaxis_title="Trips", xaxis_title="User type", showlegend=False)
        st.plotly_chart(fig_usertype, width="stretch")

    # Trip duration by user type (supports the insight below)
    fig_dur = px.box(
        df2[df2["valid_duration"]],
        x="usertype",
        y="trip_duration_minutes",
        color="usertype",
        points=False,
        title="Trip Duration by User Type (trips of 1–180 min)",
        labels={"usertype": "User type", "trip_duration_minutes": "Minutes"},
    )
    fig_dur.update_yaxes(range=[0, 60])
    fig_dur.update_layout(showlegend=False)
    st.plotly_chart(fig_dur, width="stretch")

    st.markdown("### Activity Patterns")
    chart_col1, chart_col2 = st.columns(2)

    # Weekday vs Weekend, averaged per day (5 weekdays vs 2 weekend days)
    activity_data = rides_per_day(df2, "weekday_or_weekend")
    with chart_col1:
        fig = px.bar(
            activity_data,
            x="weekday_or_weekend",
            y="avg_trips_per_day",
            title="Average Trips per Day: Weekday vs Weekend",
            color="weekday_or_weekend",
            text_auto=".0f",
            labels={"weekday_or_weekend": "", "avg_trips_per_day": "Avg. sampled trips per day"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    activity_by_day = rides_per_day(df2, "day_of_week", order=DAY_ORDER)
    with chart_col2:
        fig = px.line(
            activity_by_day,
            x="day_of_week",
            y="avg_trips_per_day",
            title="Average Trips per Day of the Week",
            labels={"day_of_week": "Day of the week", "avg_trips_per_day": "Avg. sampled trips per day"},
            markers=True,
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("### Hourly Activity Patterns")
    hourly = rides_per_day(df2, ["weekday_or_weekend", "hour"])
    fig = go.Figure()
    for day_type, color in [("Weekday", "blue"), ("Weekend", "orange")]:
        part = hourly[hourly["weekday_or_weekend"] == day_type].sort_values("hour")
        fig.add_trace(go.Scatter(x=part["hour"], y=part["avg_trips_per_day"], mode="lines+markers",
                                 name=day_type, line=dict(color=color)))
    fig.update_layout(
        title="Hourly Activity: Weekday vs Weekend (average per day)",
        xaxis_title="Hour of the day",
        yaxis_title="Avg. sampled trips per day",
        legend_title="Day type",
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        template="plotly_white",
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.markdown(
        """
    ### Key Insights
    1. **User Types**: Members account for about 78% of trips. Casual users ride proportionally more on weekends (around 37% of their trips vs 24% for members).
    2. **Trip Duration**: Casual users take longer trips (median ~15 min) than members (~9 min), consistent with leisure vs commuting use.
    3. **Peak Days and Hours**: Weekdays are busier than weekends, with the highest demand mid-week. On weekdays activity peaks at the commuting hours (8 am and especially 5–6 pm); weekends show a single broad afternoon peak.
    4. **Bike Type Preferences**: Classic bikes make up about 60% of trips. Trip durations are very similar for classic and electric bikes.
    """
    )


### Weather and Bike Usage
elif page == "Weather and Bike Usage":
    st.subheader("Weather and Bike Usage")
    st.markdown(
        """
    This section explores the relationship between **weather patterns and bike usage** in New York in 2022.
    By analyzing daily bike trips alongside average daily temperatures, we aim to **uncover how seasonal and weather-related factors influence biking activity**.
    These insights will guide better planning and resource allocation throughout the year.
    """
    )

    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trips Analysed (2022)", f"{TOTAL_TRIPS_2022:,}")
    with col2:
        st.metric("Avg. Daily Temperature (°C)", f"{daily['avgTemp'].mean():.1f}")
    with col3:
        corr = daily["bike_rides_daily"].corr(daily["avgTemp"])
        st.metric("Temperature–Rides Correlation", f"{corr:.2f}")

    st.divider()
    st.markdown("### Daily Bike Rides and Temperatures")
    fig_2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig_2.add_trace(
        go.Scatter(x=daily["date"], y=daily["bike_rides_daily"], name="Daily bike rides", line=dict(color="blue")),
        secondary_y=False,
    )
    fig_2.add_trace(
        go.Scatter(x=daily["date"], y=daily["avgTemp"], name="Daily temperature", line=dict(color="red")),
        secondary_y=True,
    )
    fig_2.add_hline(y=0, line_dash="dash", line_color="black", secondary_y=True,
                    annotation_text="0°C", annotation_position="bottom right")
    fig_2.update_layout(
        title="Daily Bike Trips and Temperatures in 2022",
        xaxis_title="Date",
        height=500,
        template="plotly_white",
    )
    fig_2.update_yaxes(title_text="Bike rides", secondary_y=False)
    fig_2.update_yaxes(title_text="Temperature (°C)", secondary_y=True)
    st.plotly_chart(fig_2, width="stretch")

    cold = daily.loc[daily["avgTemp"] < 0, "bike_rides_daily"].mean()
    warm = daily.loc[daily["avgTemp"] > 20, "bike_rides_daily"].mean()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg. rides on days below 0°C", f"{cold:,.0f}")
    with col2:
        st.metric("Avg. rides on days above 20°C", f"{warm:,.0f}")

    st.divider()
    st.markdown("### Insights")
    st.markdown(
        f"""
    1. **Correlation Between Temperature and Bike Usage**:
       - Daily rides and temperature are strongly correlated (r = {corr:.2f}).
       - On days below freezing the network averages about {cold:,.0f} rides, versus about {warm:,.0f} on days above 20°C.
    2. **Seasonal Peaks and Lows**:
       - Demand is highest from June to September and starts to decline in October.
       - January, February and December are the quietest months.
    3. **Transitional Seasons**:
       - March–April and November show intermediate, more variable usage, likely due to fluctuating weather.
    4. **Key Recommendations**:
       - Prioritize bike availability and maintenance during peak seasons.
       - Introduce winter biking initiatives, such as promotions and gear support.
       - Align fleet size and rebalancing staff with seasonal demand to stay cost-efficient.
    """
    )


### Top Stations Analysis
elif page == "Top Stations Analysis":
    st.subheader("Top Stations Analysis")
    st.markdown(
        """
    This page provides an **in-depth analysis of the top 20 start and end stations** for Citi Bike usage. Use the sidebar to segment by user type and season. The insights aim to **highlight station popularity**, **peak usage periods**, and **user behavior**, enabling data-driven decisions to optimize station locations and resource allocation.
    """
    )

    usertype_filter = usertype_filter_widget()
    season_filter = st.sidebar.multiselect(
        label="Select Season",
        options=["spring", "summer", "fall", "winter"],
        default=["spring", "summer", "fall", "winter"],
    )

    df1 = df[df["season"].isin(season_filter) & df["usertype"].isin(usertype_filter)]

    if df1.empty:
        st.warning("Select at least one user type and one season in the sidebar.")
        st.stop()

    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trips in Selection", f"{len(df1):,}")
    with col2:
        st.metric("Most Popular Start", df1["start_station_name"].value_counts().idxmax())
    with col3:
        st.metric("Active Start Stations", f"{df1['start_station_name'].nunique():,}")

    st.divider()
    st.markdown("### Top Stations Overview")
    chart_col1, chart_col2 = st.columns(2)

    top20 = df1["start_station_name"].value_counts().head(20).rename_axis("station").reset_index(name="trips")
    with chart_col1:
        st.markdown("#### Top 20 Start Stations")
        fig = go.Figure(go.Bar(x=top20["station"], y=top20["trips"],
                               marker={"color": top20["trips"], "colorscale": "Blues"}))
        fig.update_layout(xaxis_title="Start stations", yaxis_title="Trips (sample)", height=500)
        st.plotly_chart(fig, width="stretch")

    top20_end = df1["end_station_name"].value_counts().head(20).rename_axis("station").reset_index(name="trips")
    with chart_col2:
        st.markdown("#### Top 20 End Stations")
        fig = go.Figure(go.Bar(x=top20_end["station"], y=top20_end["trips"],
                               marker={"color": top20_end["trips"], "colorscale": "Blues"}))
        fig.update_layout(xaxis_title="End stations", yaxis_title="Trips (sample)", height=500)
        st.plotly_chart(fig, width="stretch")

    st.divider()
    st.markdown(
        """
    ### Insights
    1. **Key Differences Between Members and Casual Users**:
       - **Members** primarily use bikes for commuting, focusing on stations near business districts and transit hubs.
       - **Casual Users** favor stations near parks, the Hudson River waterfront and tourist areas, highlighting leisure-oriented rides.

    2. **Seasonal Trends**:
       - **Members**: Consistent usage year-round, with a moderate decline in winter.
       - **Casual Users**: Strong seasonal dependency, peaking in summer and dropping sharply in winter.

    3. **Top Station Preferences**:
       - **W 21 St & 6 Ave**, **West St & Chambers St** and **Broadway & W 58 St** lead both start and end stations.
       - For casual users the top station is **Central Park S & 6 Ave**, followed by Hudson waterfront stations such as **West St & Chambers St** and **12 Ave & W 40 St** (filter by user type to see it).

    4. **Summer vs. Winter Usage**:
       - **Summer**: Members keep steady weekday activity while casual users dominate weekends near recreational spots.
       - **Winter**: Members maintain lower but steady usage around transit hubs; casual activity is minimal.
    """
    )


### Interactive Trip Map
elif page == "Interactive Trip Map":
    st.subheader("Interactive Trip Map")
    st.markdown(
        """
    This page provides a dynamic visualization of bike trips across New York, **highlighting the most popular routes and stations**. The interactive map shows the start and end points of bike trips, with arcs representing the flow of trips between stations.

    Key insights from this visualization include:
    - Identifying the **busiest bike routes** in the city.
    - Understanding **trip patterns** and **station connectivity**.
    - Gaining a better sense of **how stations are utilized** throughout the city.
    """
    )

    st.divider()
    st.header("Aggregated Bike Trips in New York")
    st.iframe(Path("Images/kepler.gl (8).html"), height=600)
    st.caption(
        "Interactive visualization of aggregated bike trips across New York City in 2022, highlighting popular routes "
        "and connections between key locations."
    )

    st.divider()
    st.markdown(
        """
    ### Insights from NYC Citi Bike Service

    #### 1. **Concentration Near Key Areas**
    - The most active stations are located in Chelsea, Midtown and Lower Manhattan, such as **W 21 St & 6 Ave** and **West St & Chambers St**.
    - These areas combine commuter traffic with tourist and leisure trips.

    #### 2. **Waterfront and Recreational Areas**
    - Many trips start or end along the Hudson River Greenway, emphasizing its appeal for recreational and scenic rides.
    - Stations near **Central Park South** and along the West Side waterfront point to heavy leisure use.

    #### 3. **Manhattan as a Connectivity Hub**
    - Stations in Midtown and Downtown act as central nodes linking residential and business areas.
    - Dense clusters around **Broadway & W 58 St** and the Penn Station area (**6 Ave & W 33 St**, **8 Ave & W 33 St**) show Citi Bike's role in last-mile connectivity.

    #### 4. **Station Pairings and Commuter Patterns**
    - Frequently used routes indicate key commuter flows between business districts and residential neighborhoods.
    """
    )


### Recommendations
else:
    st.subheader("Strategic Recommendations")
    st.markdown(
        """
    This section provides **actionable insights to optimize NYC bike operations**, ensuring scalability, efficient station distribution, and stock management. By addressing seasonal trends and high-demand areas, these recommendations aim to enhance user satisfaction and operational efficiency.
    """
    )

    monthly = daily.groupby(daily["date"].dt.month)["bike_rides_daily"].mean()
    winter_drop = 1 - monthly.loc[[1, 2, 12]].mean() / monthly.loc[[6, 7, 8]].mean()
    hourly_weekday = df[df["weekday_or_weekend"] == "Weekday"]["hour"].value_counts()
    peak_hour = int(hourly_weekday.idxmax())
    member_share = (df["usertype"] == "member").mean()

    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Winter vs Summer Demand", value=f"-{winter_drop:.0%}")
    with col2:
        st.metric(label="Weekday Peak Hour", value=f"{peak_hour}:00")
    with col3:
        st.metric(label="Trips by Members", value=f"{member_share:.0%}")

    st.divider()
    st.markdown("### Detailed Recommendations")

    with st.expander("1. **Scaling Bikes Back Between November and April**"):
        st.markdown(
            f"""
        - **Recommendation**: Reduce bike availability by approximately **30-40%** during the colder months (November to April).
        - **Rationale**:
            - Average daily demand in December–February is about {winter_drop:.0%} lower than in June–August, so a 30–40% reduction still leaves a comfortable buffer.
            - Members keep riding in winter, so availability should stay high in downtown and around transit hubs.
        - **Implementation**:
            - Analyze trip data to identify stations with low demand during winter.
            - Use the off-season for maintenance and reallocate bikes to high-demand areas.
        """
        )

    with st.expander("2. **Determining How Many More Stations to Add Along the Water**"):
        st.markdown(
            """
        #### Steps:
        1. **Analyze Trip Data**: Identify high-demand stations along the Hudson waterfront, such as **West St & Chambers St**, **12 Ave & W 40 St** and **11 Ave & W 41 St**, and find stretches with sparse coverage.
        2. **Heatmap Analysis**: Map trip density along the waterfront to find underserved areas, especially where casual riders gather on weekends and in summer.
        3. **User Feedback**: Survey both **casual users** (recreational needs) and **members** (commuting needs) about preferred new locations.
        4. **Simulation Models**: Forecast how new stations would change trip volumes and relieve congestion at existing high-demand stations.
        5. **Benchmarking**: Compare station density along the waterfront with high-demand inland areas.

        #### Rationale:
        - Adding stations in high-demand waterfront areas **improves accessibility for recreational users** and **boosts overall system efficiency**.
        - Stations near **tourist hotspots** can **attract more casual riders**, **increasing revenue** during peak seasons.
        """
        )

    with st.expander("3. **Ensuring Bikes Are Always Stocked at Popular Stations**"):
        st.markdown(
            f"""
        - **Strategies**:
            - Leverage **real-time monitoring** to track bike availability and redistribute bikes dynamically, especially before the weekday peak around {peak_hour}:00.
            - Implement **predictive analytics** using temperature forecasts, given the strong link between weather and demand.
            - Provide **user incentives** (e.g., discounts, rewards) for returning bikes to high-demand stations.
            - Deploy **dedicated logistics teams** to prioritize key stations like **W 21 St & 6 Ave**, **West St & Chambers St** and **Broadway & W 58 St**.
            - Add **overflow docking capacity** at high-traffic locations to avoid bottlenecks during busy periods.
        - **Outcome**: Improved bike availability and reduced wait times at popular stations.
        """
        )

    st.divider()
    st.markdown(
        """
    ### Additional Insights
    - **User Type Trends**: Casual users ride mainly on weekends and in summer, favoring recreational hotspots; members ride year-round, indicating commuter reliance on the service.
    - **Seasonal Adjustments**: Ensure robust operations in summer and scale back in winter while maintaining access for members.
    - **Geographic Focus**: Expand station placements in underserved high-traffic areas identified through trip data and heatmaps.

    By implementing these recommendations, Citi Bike can **optimize bike availability**, **expand service coverage along the waterfront**, and ensure **user satisfaction** at high-demand stations throughout the year.
    """
    )
    st.markdown("---")
    bikes = Image.open("Images/nyc_image_2.jpeg")  # source: generated by ChatGPT
    st.image(bikes, caption="Strategic recommendations for NYC Citi Bike optimization.")
