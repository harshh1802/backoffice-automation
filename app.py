import streamlit as st
import pandas as pd

# Function to process the CSV and generate the new file
def process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    # Extract required columns
    required_columns = ['CLIENTCODE', 'NAME', 'SCRIPCODE2', 'NETQTY', 'CLRATE']
    if all(col in df.columns for col in required_columns):
        df_extracted = df[required_columns].copy()
        # Calculate TOTAL column
        df_extracted['TOTAL'] = df_extracted['NETQTY'] * df_extracted['CLRATE']
        return df_extracted
    else:
        st.error('CSV file does not contain all required columns.')
        return None

# Streamlit app layout
st.title('MTM')

uploaded_file = st.file_uploader('Upload a CSV file', type='csv')

if uploaded_file is not None:
    st.success('File uploaded successfully!')
    processed_df = process_csv(uploaded_file)
    
    if processed_df is not None:
        st.write('Preview of the processed file:')
        st.dataframe(processed_df)

        # Download the new file
        csv = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label='Download Processed CSV',
            data=csv,
            file_name='mtm.csv',
            mime='text/csv',
        )
