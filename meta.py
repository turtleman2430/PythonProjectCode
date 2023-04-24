import os 
import pandas as pd
import altair as alt
import numpy as np
import pydeck as pdk
from tabulate import tabulate

# make a csv from country coord and currency csv
def main():
    # read in csvs    
    country_generic_data = pd.read_csv('readonly/countries.csv')
    country_coord_data = pd.read_csv('readonly/countries-avg-coords.csv')

    # Print original csvs
    # print(tabulate(country_coord_data, headers='keys', tablefmt='psql'))
    # print(tabulate(country_generic_data, headers='keys', tablefmt='psql'))
    country_coord_data.drop(columns=["country"], inplace=True)
    country_generic_data.drop(columns=[
        "Country (local)","Continent",
        "Capital","Population","Area (sq km)","Area (sq mi)","Coastline (km)",
        "Coastline (mi)","Government form","Currency",
        "Dialing prefix","Birthrate","Deathrate","Url"
        ], inplace=True)
  
    intersect = pd.merge(country_generic_data, country_coord_data, how='inner', on=['Country code'])
    coin_paprica_curr = [
            'BTC', 'ETH', 'USD', 'EUR', 'PLN', 'KRW', 'GBP', 'CAD',
            'JPY', 'RUB', 'TRY', 'NZD', 'AUD', 'CHF', 'UAH', 'HKD',
            'SGD', 'NGN', 'PHP', 'MXN', 'BRL', 'THB', 'CLP', 'CNY',
            'CZK', 'DKK', 'HUF', 'IDR', 'ILS', 'INR', 'MYR', 'NOK',
            'PKR', 'SEK', 'TWD', 'ZAR', 'VND', 'BOB', 'COP', 'PEN',
            'ARS', 'ISK']
    # exlclued rows that arent in the coinpaprika list
    intersect = intersect[intersect['Currency code'].isin(coin_paprica_curr)]
    #print(tabulate(country_coord_data, headers='keys', tablefmt='psql'))
    print(tabulate(intersect, headers='keys', tablefmt='psql'))

    os.makedirs('data', exist_ok=True)  
    intersect.to_csv('data/country-coord-curr.csv') 


if __name__ == "__main__":
    main()
