import streamlit as st
import requests
import pandas as pd
import altair as alt

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

# Define function to get current price of a cryptocurrency
def get_crypto_price(crypto):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={crypto}&tsym=USD&limit=365"
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
        return "Bitcoin is the first cryptocurrency and has a maximum supply of 21 million coins. It is currently the most valuable cryptocurrency."
    elif crypto == "ETH":
        return "Ethereum is a blockchain platform that enables developers to build decentralized applications (dApps). It has a maximum supply of 18 million coins per year."
    elif crypto == "XRP":
        return "XRP is a cryptocurrency created by Ripple Labs. It is designed for cross-border payments and has a maximum supply of 100 billion coins."
    elif crypto == "BCH":
        return "Bitcoin Cash is a fork of Bitcoin that was created to improve transaction speed and lower fees. It has a maximum supply of 21 million coins."
    elif crypto == "LTC":
        return "Litecoin is a cryptocurrency created by Charlie Lee, a former Google engineer. It is a 'lite' version of Bitcoin with faster transaction speed and lower fees."


# Define Streamlit app
def main():
    # This centers the header
    st.markdown("<h1 style='text-align: center;'>Crypto Hub</h1>", unsafe_allow_html=True)
    # Add spacing between the header and the subheader
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Allow user to select a cryptocurrency from a dropdown menu
    col1, col2 = st.columns([0.2, 1])
    with col1:
        st.markdown("<h3 style='text-align: left;'>Current value of</h3>", unsafe_allow_html=True)
    with col2:
        crypto_selected = st.selectbox("", options = {k: f"{k} - {v}" for k, v in cryptos.items()})

    # Display current price of selected cryptocurrency
    price = get_crypto_price(crypto_selected)

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



if __name__ == "__main__":
    main()
