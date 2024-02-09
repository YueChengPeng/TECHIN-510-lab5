# TECHIN 510 Lab 5

## Getting Started
Open the terminal and run the following commands:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## What's Included
- app.py: The streamlit app on Seattle events, has following features.
    - Read data from the PostgreSQL database (which is updated everyday).
    - Several visualizations:
        - What category of events are most common in Seattle?
        - What month has the most number of events?
        - What day of the week has the most number of events?
        - Where are events often held?
    - User selection and filtering: users can filter events by category, location, and date range, and get a map visualization of where these events going to take place (also with a table showing the raw data).

## Lessions Learned
- Use altair to create interactive visualization graphs. Also the use of folium to visualize geolocations with maps.
- How to connect PostgreSQL with Python (upload and read data). How to use GitHub Actions along with Repository secrets (environmental variables).
- How to acquire data from PostgreSQL Azure via either connecting to the database with the shell on Azure or DBeaver.


## Questions/Uncertainties
- Is it possible to customize visualizations created by altair, e.g. change color, font, font-size, style of the tooltip, etc.
- How can we use altair to create more complicated visualizations, e.g. force directed graph from d3.js?