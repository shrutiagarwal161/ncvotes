import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta

class WebDataScraper:
    def __init__(self):
        self.saturdays_in_2024 = self.saturdays(2024)
        self.json_data = ""

    # Generate a list of all Saturdays in the year up to the current date.
    @staticmethod
    def saturdays(year: int):
        SAT = 5
        START_MONTH = 1
        START_DAY = 1
        start_date = datetime(year, START_MONTH, START_DAY) # starting on Jan 1
        start_day_of_the_week = start_date.weekday()
        days_until_saturday = SAT - start_day_of_the_week + 7
        if days_until_saturday < 0:
            days_until_saturday += 7
        upcoming_sat = start_date + timedelta(days=days_until_saturday)
        
        saturdays = []
        saturdays.append(start_date.strftime('%m/%d/%Y')) # data starts at Jan 1
        current_sat = upcoming_sat
        
        while current_sat < datetime.now():
            saturdays.append(current_sat.strftime('%m/%d/%Y'))
            current_sat += timedelta(weeks=1)

        return saturdays
    
    # Fetch data from the URL for the given Saturday and store the JSON content.
    def fetch_data(self, saturday_date: str):
        url = f'https://vt.ncsbe.gov/RegStat/Results/?date={saturday_date}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')

        self.json_data = ""  # Clear previous JSON data

        for script in scripts:
            if script.string and 'SetupGrid' in script.string:
                script_content = script.string
                start_index = script_content.find("var data = ")
                end_index = script_content.find("// initialize the igGrid control")
                if start_index != -1 and end_index != -1:
                    self.json_data = script_content[start_index + len("var data = "):end_index].strip()
                    break

        if self.json_data:
            self.json_data = self.json_data.rstrip(',')
        else:
            raise ValueError("JSON data not found.")
        
    # Parse the JSON data into a DataFrame and add a 'Week Ending' column.
    def parse_json(self, saturday_date: str):
        if not self.json_data:
            raise ValueError("No JSON data to parse.")

        data = json.loads(self.json_data)
        df = pd.DataFrame(data)

        # Drop the 'AppVersion' column
        if 'AppVersion' in df.columns:
            df = df.drop(columns=['AppVersion'])

        # Add the 'Week Ending' column with the Saturday's date
        df['Week Ending'] = saturday_date

        # Capitalize the first letter of each county name
        df['CountyName'] = df['CountyName'].str.capitalize()

        # Merge FIPS with scraped dataframe
        df_fips = pd.read_csv('FIPS.csv')
        df_fips['FIPS'] = df_fips['FIPS'].astype(str).str.zfill(3)
        merged_df = pd.merge(df, df_fips, left_on='CountyName', right_on='County', how='inner')

        # Drop the 'CountyName' column
        merged_df = merged_df.drop(columns=['CountyName'])

        # Load in County Populations
        df_pop = pd.read_csv('CountyPopulations.csv')
        merged_df = pd.merge(merged_df, df_pop, left_on='County', right_on='County', how='inner')

        # Calculate Total Voters per capita
        merged_df['TotalVotersPerCapita'] = merged_df['Total'] / merged_df['Population']

        # Reorder columns to put 'County', 'FIPS', 'Population' at the front
        columns_order = ['County', 'FIPS', 'Population', 'Total', 'TotalVotersPerCapita', 'Week Ending'] + \
                        [col for col in merged_df.columns if col not in ['County', 'FIPS', 'Population', 'Total', 'TotalVotersPerCapita', 'Week Ending']]
        merged_df = merged_df[columns_order]

        # Capitalize everything in the 'County' column
        merged_df['County'] = merged_df['County'].str.upper()

        return merged_df
    
    # Fetch and parse data for all Saturdays in the year, returning a list of DataFrames.
    def sat_dataframes(self):
        dfs = []
        for sat in self.saturdays_in_2024:
            self.fetch_data(sat)
            df = self.parse_json(sat)
            dfs.append(df)
        return dfs

# Create an instance of the WebDataScraper class
scraper = WebDataScraper()

# Fetch and process the data, returning a DataFrame
sat_dfs = scraper.sat_dataframes()

# Concatenate all DataFrames into a single DataFrame
final_df = pd.concat(sat_dfs, ignore_index=True)

# Save the final DataFrame to a CSV file
final_df.to_csv('voter_registrations_up_until_08102024.csv', index=False)
