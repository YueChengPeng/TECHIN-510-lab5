import streamlit as st
import pandas.io.sql as sqlio
import altair as alt
import folium
from streamlit_folium import st_folium, folium_static
import re
import numpy as np

from db import conn_str

st.title("Seattle Events")
df = sqlio.read_sql_query("SELECT * FROM events", conn_str)

# what are the most common categories of events?
st.subheader("What category of events are most common in Seattle?")
st.altair_chart(
    alt.Chart(df).mark_bar().encode(x="count()", y=alt.Y("category").sort('-x')).interactive(),
    use_container_width=True,
)

# what month has the most number of events?
st.subheader("What month has the most number of events?")
df['month'] = df['date'].dt.month_name()
st.altair_chart(
    alt.Chart(df).mark_bar().encode(x="count()", y=alt.Y("month").sort('-x')).interactive(),
    use_container_width=True,
)

# What day of the week has the most number of events?
st.subheader("What day of the week has the most number of events?")
df['day'] = df['date'].dt.day_name()
st.altair_chart(
    alt.Chart(df).mark_bar().encode(x="count()", y=alt.Y("day").sort('-x')).interactive(),
    use_container_width=True,
)

# Where are events often held?
st.subheader("Where are events often held?")
st.altair_chart(
    alt.Chart(df).mark_bar().encode(x="count()", y=alt.Y("location").sort('-x')).interactive(),
    use_container_width=True,
)

# filter controls
st.subheader("Filter events by category, location, and date range")


try:
    categories = np.insert(df['category'].unique(), 0, 'All')
    locations = np.insert(df['location'].unique(), 0, 'All')

    category = st.selectbox("Select a category", categories)
    location = st.selectbox("Select a location", locations)

    # Filter the DataFrame based on the selections
    df = df[(df['category'] == category) | (category == 'All')]
    df = df[(df['location'] == location) | (location == 'All')]

    # Continue with date filtering and writing the DataFrame
    start_date, end_date = st.date_input("Select a date range", [df['date'].min(), df['date'].max()])
    df['date'] = df['date'].dt.date
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    # Create a map centered around the first location in the filtered data
    m = folium.Map(location=[47.6062, -122.3321], zoom_start=12)

    # Add a marker for each location in the filtered data
    for _, row in df.iterrows():
        try:
            folium.Marker([row['latitude'], row['longitude']], popup=row['location']).add_to(m)
        except Exception as e:
            print(e)

    # Display the map in the Streamlit app
    folium_static(m, width=600, height=600)

    st.write(df)
except:
    st.write("No event found")