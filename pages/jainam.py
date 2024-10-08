import streamlit as st
import pandas as pd

# Define the path to your CSV file
csv_file_path = 'id.csv'

# Function to get ClientCode from ClientID
def get_client_code(client_id):
    # Load the CSV into a dataframe
    df = pd.read_csv(csv_file_path, index_col = False)
    
    # Find the corresponding ClientCode for the given ClientID
    result = df.loc[df['clientid'] == client_id, 'clientcode']
    
    # If a match is found, return the ClientCode, otherwise return a message
    if not result.empty:
        return result.values[0]
    else:
        return "ClientID not found."

# Streamlit App
st.title("Jainam BSE Trade Data Processor")

scode = st.text_input('Series Code')

# File uploader for Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type="csv")

if uploaded_file is not None:
    # Read the uploaded Excel file into a dataframe
    df = pd.read_csv(uploaded_file)
    


    # Fixed parameters as provided in your code
    # TraderID = 2001
    # ClientTrCode = 'BRD206731'
    # CleintCode = 'ITC2067'
    SeriesCode = scode
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
            'TraderID': row['MemberID'],
            'ClientTrCode': row['UserID'],
            'ClientCode': get_client_code(row['UserID']),
            'SeriesCode': SeriesCode,
            'Qty': row['Quantity'] * (-1) if row['Side'] == 'Sell' else row['Quantity'],
            'MktRate': row['Price'],
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
        file_name='JAINAM_CONVERTED.csv',
        mime='text/csv',
    )
