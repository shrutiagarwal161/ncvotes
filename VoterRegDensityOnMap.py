import json
import pandas as pd
import plotly.express as px
from web_data_scraper import WebDataScraper

# Get the processed DataFrame
scraper = WebDataScraper()
df = scraper.get_dataframe()

# Load GeoJSON data
with open('north_carolina.geojson') as f:
    geojson_data = json.load(f)

# Plot the choropleth map
fig = px.choropleth(
    df,
    geojson=geojson_data,
    locations='FIPS',
    featureidkey="properties.FIPS",  # Adjust this key according to your GeoJSON properties
    color='Total',
    color_continuous_scale="Viridis",
    range_color=(df['Total'].min(), df['Total'].max()),
    scope="usa",  # Limit the map to the USA
    labels={'Total': 'Total Registered Voters'},
    hover_name='County',  # This will add the County name to the hover label
    hover_data={'FIPS': False}  # Exclude FIPS from hover data
)

# Update layout to zoom in on North Carolina
fig.update_geos(fitbounds="locations", visible=False)

# Show the map
fig.show()
