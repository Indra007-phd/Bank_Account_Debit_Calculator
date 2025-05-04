import streamlit as st
import pdfplumber
import pandas as pd

# Streamlit Web App Title
st.title("Bank Statement Debit Calculator")

# File uploader for PDF
uploaded_file = st.file_uploader("Upload your bank statement PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # Open the PDF file
        with pdfplumber.open(uploaded_file) as pdf:
            all_tables = []  # List to store all tables from all pages
            
            # Loop through all pages and extract tables
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_tables.append(table)
        
        # Check if any tables were found
        if all_tables:
            # Combine all tables into a single DataFrame
            all_data = []
            for table in all_tables:
                # Convert each table into a DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                all_data.append(df)
            
            # Concatenate all DataFrames into one large DataFrame
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Display the first few rows of the combined table for debugging
            st.subheader("Combined Extracted Table")
            st.write(combined_df.head())
            
            # Assuming the 'Debit' and 'Description' columns (adjust names if needed)
            debit_column = 'Debit'  # Adjust if necessary
            description_column = 'Description'  # Adjust if necessary
            
            if debit_column not in combined_df.columns or description_column not in combined_df.columns:
                st.error(f"Columns '{debit_column}' or '{description_column}' not found in the table.")
            else:
                # Convert Debit column to numeric
                combined_df[debit_column] = pd.to_numeric(combined_df[debit_column], errors='coerce')
                
                # Filter the rows where Debit is a valid number
                debit_rows = combined_df[[description_column, debit_column]].dropna()
                
                # Calculate the total Debit
                total_debit = debit_rows[debit_column].sum()
                
                # Display the total debit amount
                st.success(f"Total Debit amount: {total_debit:.2f}")
                
                # Show the filtered rows considered for the debit calculation
                st.subheader("Rows considered for Debit Calculation")
                st.write(debit_rows)
    
        else:
            st.error("No tables found in the uploaded PDF.")
    
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
