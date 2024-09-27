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
    df = pd.DataFrame(columns=["ClientID", "ClientCode"])

# Display the current data in the CSV
st.write("Existing Data:")
st.dataframe(df)

# Form for input
st.write("Add New Entry")
with st.form(key='add_data_form'):
    client_id = st.text_input('Enter Client ID')
    client_code = st.text_input('Enter Client Code')
    submit_button = st.form_submit_button(label='Submit')

# Append new data if the form is submitted
if submit_button:
    # Create a new dataframe from the form inputs
    new_data = pd.DataFrame({
        'clientid': [client_id],
        'clientcode': [client_code]
    })
    
    # Append the new data to the existing dataframe
    df = df.concat(new_data, ignore_index=True)
    
    # Save the updated dataframe back to the CSV
    df.to_csv(csv_file_path, index=False)
    
    st.success("Data successfully appended to the CSV!")
    
    # Display the updated data
    st.write("Updated Data:")
    st.dataframe(df)
