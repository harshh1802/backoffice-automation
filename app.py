import streamlit as st
import pandas as pd

# Function to process the CSV and generate the new file
def process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # Step 1: Categorize the instrument types
    df['instrument_type'] = df['SCRIPID'].apply(lambda x: 'Future' if x.startswith('FUT') else ('Option' if x.startswith('OPT') else 'Cash'))

    # Step 2: Filter for Future and Cash types
    df2 = df[df['instrument_type'].isin(['Future', 'Cash'])]

    df2['SCRIPCODE2'] = df['SCRIPCODE2'].str.strip()

    # Step 3: Group by CLIENTCODE and SCRIPCODE2 and sum NETQTY
    group_df = df2.groupby(['CLIENTCODE', 'SCRIPCODE2'])['NETQTY'].sum().reset_index()


    # Step 4: Create a dictionary to store the CLRATE and NAME of Cash positions
    clrate_dict = df2[df2['instrument_type'] == 'Cash'].set_index(['CLIENTCODE', 'SCRIPCODE2'])['CLRATE'].to_dict()
    name_dict = df2[df2['instrument_type'] == 'Cash'].set_index(['CLIENTCODE'])['NAME'].to_dict()

    # Step 5: Calculate the TOTAL by multiplying the summed NETQTY by the CLRATE of the Cash position
    group_df['CLRATE'] = group_df.apply(lambda row: clrate_dict.get((row['CLIENTCODE'], row['SCRIPCODE2']), 0), axis=1)
    group_df['NAME'] = group_df.apply(lambda row: name_dict.get((row['CLIENTCODE']), ''), axis=1)
    group_df['TOTAL'] = group_df['NETQTY'] * group_df['CLRATE']

    # Step 6: Reorder the columns as required
    group_df = group_df[['CLIENTCODE', 'NAME', 'SCRIPCODE2', 'NETQTY', 'CLRATE', 'TOTAL']]

    return group_df

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
