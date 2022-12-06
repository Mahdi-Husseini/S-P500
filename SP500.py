import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf

st.title("S&P500")

st.markdown("""This app retrieves the list of **S&P500** with its corresponding **stock closing price** (year-to-date)
    \n* **Python libraries:** streamlit, pandas, yfinance, matplotlib, base64
    \n* **Data source:** [Wikipedia](https://wikipedia.org/)""")

st.sidebar.header("User Input")

@st.cache
def load_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header=0)
    df = html[0]
    return df

df = load_data()

# Sidebar - Sector selection
sector_unique = sorted( df['GICS Sector'].unique() )
selected_sector = st.sidebar.multiselect('Sector', sector_unique, sector_unique)

df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

st.header("Displaying companies in selected sector")
st.write("Dimensions: " + str(df_selected_sector.shape[0]) + " rows and " + str(df_selected_sector.shape[1]) + " columns")
st.dataframe(df_selected_sector)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

data = yf.download(
        tickers = list(df_selected_sector[:10].Symbol),
        period = "ytd",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )


num_company = st.sidebar.slider('Number of companies for plots', 1, 10)

spec_symbol = st.sidebar.text_input("OR choose a specific symbol ")
spec_data = 0
t = False
if spec_symbol:
    if(spec_symbol.upper() in df['Symbol'].tolist()):
        spec_data = yf.download(
                tickers = spec_symbol,
                period = "ytd",
                interval = "1d",
                group_by = 'ticker',
                auto_adjust = True,
                prepost = True,
                threads = True,
                proxy = None
            )
        t = True
    else:
        st.sidebar.write("Symbol not found")

def price_plot(symbol):
    if(t):
        df = pd.DataFrame(spec_data.Close)
    else:
        df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
    plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol.upper(), fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Closing Price', fontweight='bold')
    return st.pyplot(plt)


if st.button('Show Plots'):
    st.header('Stock Closing Price')
    if(t):
        price_plot(spec_symbol)
    else:
        for i in list(df_selected_sector.Symbol)[:num_company]:
            price_plot(i)



