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

# Convert TotalVotersPerCapita to percentage
df['TotalVotersPerCapita'] = df['TotalVotersPerCapita'] * 100  # Convert to percentage

# Plot the choropleth map using 'TotalVotersPerCapita'
fig = px.choropleth(
    df,
    geojson=geojson_data,
    locations='FIPS',
    featureidkey="properties.FIPS",  # Adjust this key according to your GeoJSON properties
    color='TotalVotersPerCapita',
    color_continuous_scale="Viridis",
    range_color=(df['TotalVotersPerCapita'].min(), df['TotalVotersPerCapita'].max()),
    scope="usa",  # Limit the map to the USA
    labels={'TotalVotersPerCapita': 'Total Voters Per Capita (%)'},
    hover_name='County',  # This will add the County name to the hover label
    hover_data={
        'TotalVotersPerCapita': ':,.0f',  # Format with no decimal places and thousand separators
        'FIPS': False  # Exclude FIPS from hover data
    }
)

# Update layout to zoom in on North Carolina
fig.update_geos(fitbounds="locations", visible=False)

# Update the color bar to format as percentage and adjust the tick values
fig.update_layout(
    coloraxis_colorbar=dict(
        title='Total Voters Per Capita (%)',
        ticktext=[f'{i//100:.0%}' for i in range(0, int(df['TotalVotersPerCapita'].max())+10, 10)]  # Convert to percentage
    )
)

# Show the map
fig.show()
