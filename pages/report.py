import streamlit as st
import pandas as pd
from datetime import datetime
import os

tab1, tab2, tab3 = st.tabs(['Generate Report','Modify Client Data', '---'])

with tab1:

    # Define functions outside of the file upload section
    def holding(code, h_type, stock):
        temp_df = stock[(stock['CLIENTCODE'] == code) & (stock['instrument_type'] == h_type)]
        temp_df['SCRIPCODE2'] = temp_df['SCRIPCODE2'].str.strip()
        temp_df['total_holding'] = temp_df['NETQTY'] * temp_df['CLRATE']
        return temp_df.groupby(['SCRIPCODE2'])['total_holding'].sum().sum()

    def pl(code, stock):
        temp_df = stock[(stock['CLIENTCODE'] == code)]
        temp_df['SCRIPCODE2'] = temp_df['SCRIPCODE2'].str.strip()
        temp_df['pl'] = temp_df['MTM'] - temp_df['CLIENTSTT']
        return temp_df.groupby(['SCRIPCODE2'])['pl'].sum().sum()

    def deposit(code, bs):
        temp_df = bs[(bs['FAACCOUNTCODE'] == f'D{code}')]
        return temp_df['AMOUNT'].iloc[0] if not temp_df.empty else 0

    def ledger(code, margin_summary):
        temp_df = margin_summary[(margin_summary['CLIENTCODE'] == code)]
        return temp_df['Ledger Bal'].iloc[0] if not temp_df.empty else 0

    def interest(code, int_summary):
        temp_df = int_summary[(int_summary['Client Code'] == code)]
        return temp_df['Interest Amt'].iloc[0] if not temp_df.empty else 0

    def interest_rate(code, int_summary):
        temp_df = int_summary[(int_summary['Client Code'] == code)]
        return temp_df['Int Rate (% p.a.)'].iloc[0] if not temp_df.empty else 0

    def limit(code, limit_df):
        temp_df = limit_df[(limit_df['Code'] == code)]
        return temp_df['Limit'].iloc[0] if not temp_df.empty else 0

    def utilization(eq_holding, limit):

        try:
            return eq_holding*100/ (limit*100000)
        
        except Exception:
            return 0


    def name(code, c_data):
        temp_df = c_data[(c_data['Code'] == code)]
        return temp_df['Name'].iloc[0] if not temp_df.empty else ""

    # Load the static files
    c_data = pd.read_csv('c_data.csv')
    limit_df = pd.read_csv('limit.csv')
    limit_df['Limit'] = pd.to_numeric(limit_df['Limit'], errors='coerce').fillna(0)


    # Create a file uploader for users to upload files
    uploaded_files = st.file_uploader("Upload MTM.CSV, BL.csv, MARGIN SUMMARY.xls, and IntCalcSummary.xls", 
                                    type=['csv', 'xls', 'xlsx'], accept_multiple_files=True)

    if uploaded_files:
        # Create a dictionary to hold the uploaded files by their names
        uploaded_dict = {file.name: file for file in uploaded_files}

        # Load the files uploaded by the user
        stock = pd.read_csv(uploaded_dict['MTM.CSV'])
        stock['instrument_type'] = stock['SCRIPID'].apply(lambda x: 'FUT' if x.startswith('FUT') else ('OPT' if x.startswith('OPT') else 'EQ'))
        bs = pd.read_csv(uploaded_dict['BL.csv'])

        margin_summary = pd.read_excel(uploaded_dict['MARGIN SUMMARY.xls'], sheet_name=1, header=None)
        margin_summary.columns = margin_summary.iloc[22]
        margin_summary = margin_summary.iloc[23:].reset_index(drop=True)
        margin_summary = margin_summary.iloc[:, [0, 6, 9, 12, 15, 18, 20, 22, 26]]
        margin_summary['CLIENTCODE'] = margin_summary['Client Code & Name'].str.split(' ').str[0]

        int_summary = pd.read_excel(uploaded_dict['IntCalcSummary.xls'], sheet_name=1, header=None)
        int_summary.columns = int_summary.iloc[22]
        int_summary = int_summary.iloc[23:].reset_index(drop=True)
        int_summary = int_summary.iloc[:, [2, 4, 17, 20]]

        # Create the final DataFrame
        df = pd.DataFrame({})
        df[['Code', 'ID']] = c_data[['Code', 'ID']]
        df['EQ-Holding'] = df.apply(lambda x: holding(x['Code'], 'EQ', stock), axis=1)
        df['FO-Holding'] = df.apply(lambda x: holding(x['Code'], 'FUT', stock), axis=1)
        df['OPT-Holding'] = df.apply(lambda x: holding(x['Code'], 'OPT', stock), axis=1)
        df['P&L'] = df.apply(lambda x: pl(x['Code'], stock), axis=1)
        df['Deposit'] = df.apply(lambda x: deposit(x['Code'], bs), axis=1)
        df['Ledger'] = df.apply(lambda x: ledger(x['Code'], margin_summary), axis=1)
        df['Gross Amt'] = df['EQ-Holding'] + df['Ledger'] + df['FO-Holding'] + df['OPT-Holding']
        df['Int'] = df.apply(lambda x: interest(x['Code'], int_summary), axis=1)
        df['Int Rate %'] = df.apply(lambda x: interest_rate(x['Code'], int_summary), axis=1)
        df['Net Amount'] = df['Gross Amt'] - df['Int']
        df['A. Depo.'] = df['Net Amount'] + df['Deposit']
        df['Limit'] = df.apply(lambda x: limit(x['Code'], limit_df), axis=1)
        df['%'] = df.apply(lambda x: utilization(x['EQ-Holding'], x['Limit']), axis=1)
        df['Name'] = df.apply(lambda x: name(x['Code'], c_data), axis=1)
        df['Days'] = datetime.today().day

        # Add download button for the final CSV
        csv = df.round(2).to_csv(index=False)
        st.download_button(label="Download Final CSV", data=csv, file_name='Final.csv', mime='text/csv')

with tab2:
    # Define the path to your CSV file
    csv_file_path = 'c_data.csv'

    # Load existing data
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
    else:
        # If the CSV does not exist, create an empty dataframe with specified columns
        df = pd.DataFrame(columns=["Code", "ID", "Name"])

    # Display the current data in the CSV
    st.write("Existing Data:")
    st.dataframe(df)

    # Dropdown for selecting action (Create, Update, Delete)
    action = st.selectbox('Select action', ['Create', 'Update', 'Delete'])

    # Section to add new data (Create)
    if action == 'Create':
        st.write("Add New Entry")
        with st.form(key='add_data_form'):
            code = st.text_input('Enter Code')
            c_id = st.text_input('Enter ID')
            name = st.text_input('Enter Name')
            submit_button = st.form_submit_button(label='Submit')

        # Append new data if the form is submitted
        if submit_button:
            if code and c_id and name:
                # Create a new dataframe from the form inputs
                new_data = pd.DataFrame({
                    'Code': [code],
                    'ID': [c_id],
                    'Name': [name]
                })
                
                # Append the new data to the existing dataframe
                df = df._append(new_data, ignore_index=True)
                
                # Save the updated dataframe back to the CSV
                df.to_csv(csv_file_path, index=False)
                
                st.success("Data successfully added to the CSV!")
                
                # Display the updated data
                st.write("Updated Data:")
                st.dataframe(df)
            else:
                st.error("Please enter both Client ID and Client Code.")

    # Section to update an existing entry by clientid (Update)
    elif action == 'Update':
        if not df.empty:
            st.write("Update Entry by Client ID")
            client_code_to_update = st.selectbox('Select Client Code to update', df['Code'].unique())
            if client_code_to_update:
                # Get the row corresponding to the selected client ID
                row_to_update = df[df['Code'] == client_code_to_update].index[0]

                with st.form(key='update_data_form'):
                    new_c_id = st.text_input('Enter new Client Code', df.loc[row_to_update, 'ID'])
                    new_name = st.text_input('Enter new Client Code', df.loc[row_to_update, 'Name'])
                    update_button = st.form_submit_button(label='Update')

                if update_button:
                    # Update the selected row
                    df.at[row_to_update, 'ID'] = new_c_id
                    df.at[row_to_update, 'Name'] = new_name

                    # Save the updated dataframe to the CSV
                    df.to_csv(csv_file_path, index=False)

                    st.success(f"Data for Client ID {client_code_to_update} successfully updated!")
                    st.write("Updated Data:")
                    st.dataframe(df)
        else:
            st.error("No data available to update.")

    # Section to delete an entry by clientid (Delete)
    elif action == 'Delete':
        if not df.empty:
            st.write("Delete Entry by Client ID")
            client_code_to_delete = st.selectbox('Select Client ID to delete', df['Code'].unique(), key="delete")
            if st.button('Delete'):
                df = df[df['Code'] != client_code_to_delete]
                
                # Save the updated dataframe to the CSV
                df.to_csv(csv_file_path, index=False)
                
                st.success(f"Data for Client ID {client_code_to_delete} successfully deleted!")
                
                # Display the updated data
                st.write("Updated Data:")
                st.dataframe(df)
        else:
            st.error("No data available to delete.")