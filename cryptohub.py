import streamlit as st
import requests
import pandas as pd
import altair as alt
import numpy as np
import pydeck as pdk

# Set page title and background color
st.set_page_config(page_title="Crypto Hub", page_icon=":money_with_wings:", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1e2130;
        color: white;
    }
    .css-1l4y4im {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define list of popular cryptocurrencies
cryptos = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "XRP": "Ripple",
    "BCH": "Bitcoin Cash",
    "LTC": "Litecoin"
}

coinstats_api = {
    "exchanges": "https://api.coinstats.app/public/v1/exchanges",
    "markets": "https://api.coinstats.app/public/v1/markets"
}
def get_crypto_market_map():
    #define 2 coloumn layout    
    col1, col2 = st.columns(2)

    # COLUMN1 
    #get exchange list for multiselect 
    exchange_list      = requests.get(coinstats_api['exchanges']).json()
    exchange_dataframe = np.transpose(exchange_list['supportedExchanges'])

    #get generated country coord data
    countries_data = pd.read_csv("data/country-coord-curr.csv")
    #st.dataframe(countries_data) #debug
    selected_markets = None

    with col1:
        
        #ask use for exchanges of interest
        selected_markets = st.multiselect("Select any exchanges you are curious about.",
                           exchange_dataframe,
                           default=[
                                "Binance",
                                "Kraken"],
                           key=None,
                           help=None,
                           on_change=None,
                           args=None,
                           kwargs=None,
                           disabled=False,
                           label_visibility="visible",
                           max_selections=None)
        if len(selected_markets) == 0:
            st.error("you must select at least one exchange")
        else:
            st.info("ploting exchange data")


    # COLUMN2
    if len(selected_markets) > 0:
        #get exchange list for multiselect 
        #get all the markets 
        market_list = requests.get(coinstats_api['markets']+'?coinId=bitcoin').json()
        market_dataframe = pd.DataFrame(market_list)
        
        #cull echanges that user is NOT interested in
        market_dataframe = market_dataframe[market_dataframe['exchange'].isin(selected_markets)]
        market_dataframe[['from', 'to']] = market_dataframe['pair'].str.split('/', 1, expand=True)
        market_dataframe.drop(columns=['pair'], inplace=True)

        #cull non-plotables
        fiat_currencies = countries_data['currency code'].tolist()

        market_dataframe = market_dataframe[market_dataframe['to'].isin(fiat_currencies)]
        #NOTE: there are multible countries that may use a given currency
        #      this literaly doesnt care where the currency originated from
        #      it just get whatever country is seen first with a given currency code
        #      and pushes that country's coordinates.
        #TODO: push all country coordinates that use a given currency and have the market
        #      dataframe make duplicate entries for all those countries. 
        coord_dataframe = pd.DataFrame([
                [countries_data.loc[countries_data['currency code'] == fiat_curr, 'lat'].iloc[0],
                 countries_data.loc[countries_data['currency code'] == fiat_curr, 'lon'].iloc[0]]
                for fiat_curr in market_dataframe['to'].tolist()], columns=['lat','lon'])
        #st.dataframe(coord_dataframe) #debug

        #st.dataframe(market_dataframe.reset_index()) #debug
        market_dataframe = pd.merge(market_dataframe.reset_index(),
                                    coord_dataframe,
                                    left_index=True,
                                    right_index=True)
        #st.dataframe(market_dataframe) #debug

        with col2:
            st.pydeck_chart(pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=37.76,
                    longitude=-122.4,
                    zoom=.001,
                    pitch=90,
                ),
                layers=[
                pdk.Layer(
                       'ColumnLayer',
                       data=market_dataframe,
                       diskResolution=32,
                       get_position='[lon, lat]',
                       radius=600000,
                       get_elevation='[pairPrice]',
                       elevation_scale=1,
                       elevation_range=[0, 10000],
                       pickable=True,
                       extruded=True,
                       get_color='[200, 30, 0, 160]',
                       )
                    ],
            ))

# Define function to get current price of a cryptocurrency
def get_crypto_price(crypto, time_frame):
    time_frames = {"day": 1, "week": 7, "month": 30, "year": 365, "5year": 1825}
    limit = time_frames[time_frame]
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={crypto}&tsym=USD&limit={limit}"
    response = requests.get(url)
    data = response.json()["Data"]["Data"]
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('date', inplace=True)
    latest_price = df['close'].iloc[-1]
    st.success(f"The current price of {crypto} is US$ {latest_price:.2f}")
    st.line_chart(df['close'])
    st.markdown("<br>", unsafe_allow_html=True)
    return latest_price



# Define function to get fun facts and recommendations for a cryptocurrency
def get_crypto_info(crypto):
    if crypto == "BTC":
        return "Bitcoin is the first cryptocurrency and has a maximum supply of 21 million coins. It is currently the most valuable cryptocurrency. Bitcoin prices can be volatile, and it's important not to make investment decisions based solely on emotions like fear and greed. Always do your research and make informed decisions."
    elif crypto == "ETH":
        return "Ethereum is a blockchain platform that enables developers to build decentralized applications (dApps). It has a maximum supply of 18 million coins per year. Like all cryptocurrencies, Ethereum prices can be volatile, and it's important not to make investment decisions based solely on emotions like fear and greed. Always do your research and make informed decisions."
    elif crypto == "XRP":
        return "XRP is a cryptocurrency created by Ripple Labs. It is designed for cross-border payments and has a maximum supply of 100 billion coins. XRP prices can be volatile, and its value may be affected by factors such as regulatory changes and competition from other payment systems. Always invest only what you can afford to lose, and consider diversifying your portfolio with other assets."
    elif crypto == "BCH":
        return "Bitcoin Cash is a fork of Bitcoin that was created to improve transaction speed and lower fees. It has a maximum supply of 21 million coins. Make sure to buy and store your Bitcoin Cash on a reputable exchange that prioritizes security and has a good reputation in the cryptocurrency community."
    elif crypto == "LTC":
        return "Litecoin is a cryptocurrency created by Charlie Lee, a former Google engineer. It is a 'lite' version of Bitcoin with faster transaction speed and lower fees. When buying or trading Litecoin, make sure to use a reputable cryptocurrency exchange with a good track record for security and customer support."



# Define Streamlit app
def main():
    # This centers the header
    st.markdown("<h1 style='text-align: center;'>Crypto Hub</h1>", unsafe_allow_html=True)
    # Add spacing between the header and the subheader
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Allow user to select a cryptocurrency from a dropdown menu
    col1, col2 = st.columns([0.2, 1])
    with col1:
        st.markdown("<h3 style='text-align: left; padding-top: 35px;'>Current value of</h3>", unsafe_allow_html=True)
    with col2:
        crypto_selected = st.selectbox("", options = {k: f"{k} - {v}" for k, v in cryptos.items()})

    # Display current price of selected cryptocurrency
    time_frame = st.radio("Select a time frame:", ["day", "week", "month", "year", "5year"], index=3)
    price = get_crypto_price(crypto_selected, time_frame)

    # Display list of popular cryptocurrencies
    st.subheader("Most popular cryptocurrencies")
    crypto_table_data = {'Cryptocurrency': [f"{k} - {v}" for k, v in cryptos.items()]}
    crypto_table = pd.DataFrame(crypto_table_data, columns=['Cryptocurrency'])
    crypto_table.index = crypto_table.index + 1  # Starts list with 1
    st.table(crypto_table)

    # Display fun facts and recommendations for selected cryptocurrency
    st.header(f"Fun facts and recommendations for {crypto_selected}")
    info = get_crypto_info(crypto_selected)
    st.write(info)

if __name__ == "__main__": main()

