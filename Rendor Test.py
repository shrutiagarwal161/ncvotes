import dash
from dash import dcc, html
from dash.dependencies import Input, Output
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

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("North Carolina Registered Voters"),
    dcc.Graph(id='choropleth-map')
])

# Define a callback to update the map
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('choropleth-map', 'id')  # Trigger the callback on component load
)
def update_map(_):
    # Plot the choropleth map
    fig = px.choropleth(
        df,
        geojson=geojson_data,
        locations='FIPS',
        featureidkey="properties.FIPS",
        color='Total',
        color_continuous_scale="Viridis",
        range_color=(df['Total'].min(), df['Total'].max()),
        scope="usa",
        labels={'Total': 'Total Registered Voters'},
        hover_name='County',
        hover_data={'FIPS': False}
    )

    # Update layout to zoom in on North Carolina
    fig.update_geos(fitbounds="locations", visible=False)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)
