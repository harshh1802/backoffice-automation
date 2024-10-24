import streamlit as st
import pandas as pd
from datetime import datetime

def convert_to_24_hour_format(time_str):
    # Parse the time in 12-hour format
    time_12hr = datetime.strptime(time_str, '%H:%M:%S')
    # Convert to 24-hour format
    time_24hr = time_12hr.strftime('%H:%M:%S')
    return time_24hr

# Streamlit App
st.title("BSE SENSEX SHAREKHAN")

scode = st.text_input('Series Code')

# File uploader for Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read the uploaded Excel file into a dataframe
    df = pd.read_excel(uploaded_file,  index_col=None)
    print(df)

    # Function to generate new dataframe entries for each row in the main dataframe
    def generate_secondary_df(main_df):
        secondary_data = []

        for index, row in main_df.iterrows():
            # Buy Entry
            secondary_data.append({
                'TraderID': row['MemberId'],
                'ClientTrCode': row['Client'],
                'ClientCode': 'A200',
                'SeriesCode': scode,
                'Qty': row['Quantity'] if row['B/S'] == 'B' else (row['Quantity']*(-1)),
                'MktRate': row['Price'],
                'OrderNo': str(row['Exch. Order No.']),
                'TradeNo': row['TraderId'],
                'TradeTime': convert_to_24_hour_format(str(row['Time'])),
                'TrType': 1
            })


        secondary_df = pd.DataFrame(secondary_data)
        return secondary_df

    # Generate the secondary dataframe
    secondary_df = generate_secondary_df(df)

    # Display the generated secondary dataframe
    st.write("Generated Secondary DataFrame:")
    st.dataframe(secondary_df)

    # Download button for the secondary dataframe
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(secondary_df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='BSE_SENSEX_SK.csv',
        mime='text/csv',
    )
