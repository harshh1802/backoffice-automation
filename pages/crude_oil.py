import streamlit as st
import pandas as pd

# Streamlit App
st.title("Crude Oil Trade Data Processor")

# File uploader for Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Read the uploaded Excel file into a dataframe
    df = pd.read_excel(uploaded_file, header=None)
    
    # Apply same steps from your code
    df.columns = df.iloc[13]
    df = df.iloc[14:]
    df = df[df['Series'].str.startswith('CRUDE OIL', na=False)]

    # Fixed parameters as provided in your code
    TraderID = 10548
    ClientTrCode = 'BRD206731'
    CleintCode = 'R144'
    SeriesCode = st.text_input('Series Code')
    OrderNo = 1
    TradeNo = 1
    TradeTime = 1
    TrType = 1

    # Function to generate new dataframe entries for each row in the main dataframe
    def generate_secondary_df(main_df):
        secondary_data = []

        for index, row in main_df.iterrows():
            # Buy Entry
            secondary_data.append({
                'TraderID': TraderID,
                'ClientTrCode': ClientTrCode,
                'ClientCode': CleintCode,
                'SeriesCode': SeriesCode,
                'Qty': row['Buy'],
                'MktRate': float(row.iloc[4]),
                'OrderNo': OrderNo,
                'TradeNo': TradeNo,
                'TradeTime': TradeTime,
                'TrType': TrType
            })

            # Sell Entry
            secondary_data.append({
                'TraderID': TraderID,
                'ClientTrCode': ClientTrCode,
                'ClientCode': CleintCode,
                'SeriesCode': SeriesCode,
                'Qty': int(row['Sell']) * (-1),
                'MktRate': float(row.iloc[6]),
                'OrderNo': OrderNo,
                'TradeNo': TradeNo,
                'TradeTime': TradeTime,
                'TrType': TrType
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
        file_name='CRUDE_OIL_CONVERTED.csv',
        mime='text/csv',
    )
