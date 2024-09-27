import streamlit as st
import pandas as pd
import os

# Define the path to your CSV file
csv_file_path = 'id.csv'

# Load existing data
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
else:
    # If the CSV does not exist, create an empty dataframe with specified columns
    df = pd.DataFrame(columns=["clientid", "clientcode"])

# Display the current data in the CSV
st.write("Existing Data:")
st.dataframe(df)

# Dropdown for selecting action (Create, Update, Delete)
action = st.selectbox('Select action', ['Create', 'Update', 'Delete'])

# Section to add new data (Create)
if action == 'Create':
    st.write("Add New Entry")
    with st.form(key='add_data_form'):
        client_id = st.text_input('Enter Client ID')
        client_code = st.text_input('Enter Client Code')
        submit_button = st.form_submit_button(label='Submit')

    # Append new data if the form is submitted
    if submit_button:
        if client_id and client_code:
            # Create a new dataframe from the form inputs
            new_data = pd.DataFrame({
                'clientid': [client_id],
                'clientcode': [client_code]
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
        client_id_to_update = st.selectbox('Select Client ID to update', df['clientid'].unique())
        if client_id_to_update:
            # Get the row corresponding to the selected client ID
            row_to_update = df[df['clientid'] == client_id_to_update].index[0]

            with st.form(key='update_data_form'):
                new_client_code = st.text_input('Enter new Client Code', df.loc[row_to_update, 'clientcode'])
                update_button = st.form_submit_button(label='Update')

            if update_button:
                # Update the selected row
                df.at[row_to_update, 'clientcode'] = new_client_code

                # Save the updated dataframe to the CSV
                df.to_csv(csv_file_path, index=False)

                st.success(f"Data for Client ID {client_id_to_update} successfully updated!")
                st.write("Updated Data:")
                st.dataframe(df)
    else:
        st.error("No data available to update.")

# Section to delete an entry by clientid (Delete)
elif action == 'Delete':
    if not df.empty:
        st.write("Delete Entry by Client ID")
        client_id_to_delete = st.selectbox('Select Client ID to delete', df['clientid'].unique(), key="delete")
        if st.button('Delete'):
            df = df[df['clientid'] != client_id_to_delete]
            
            # Save the updated dataframe to the CSV
            df.to_csv(csv_file_path, index=False)
            
            st.success(f"Data for Client ID {client_id_to_delete} successfully deleted!")
            
            # Display the updated data
            st.write("Updated Data:")
            st.dataframe(df)
    else:
        st.error("No data available to delete.")
