import streamlit as st
import pdfplumber
import pandas as pd

# Streamlit Web App Title
st.title("Bank Statement Debit + Withdrawals Calculator")

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
            
            # Identify columns
            description_column = 'Description'  # Adjust if necessary
            debit_column = None
            withdrawals_column = None
            
            # Check which debit-type columns exist
            if 'Debit' in combined_df.columns:
                debit_column = 'Debit'
                combined_df[debit_column] = combined_df[debit_column].str.replace(',', '', regex=False)
                combined_df[debit_column] = pd.to_numeric(combined_df[debit_column], errors='coerce')
            if 'Withdrawals' in combined_df.columns:
                withdrawals_column = 'Withdrawals'
                combined_df[withdrawals_column] = combined_df[withdrawals_column].str.replace(',', '', regex=False)
                combined_df[withdrawals_column] = pd.to_numeric(combined_df[withdrawals_column], errors='coerce')
            
            # Make sure at least one is present
            if not debit_column and not withdrawals_column:
                st.error("Neither 'Debit' nor 'Withdrawals' column found in the table.")
            else:
                # Create a unified 'Total_Debit' column
                combined_df['Total_Debit'] = 0
                if debit_column:
                    combined_df['Total_Debit'] += combined_df[debit_column].fillna(0)
                if withdrawals_column:
                    combined_df['Total_Debit'] += combined_df[withdrawals_column].fillna(0)
                
                # Filter rows with meaningful debit values
                debit_rows = combined_df[[description_column, 'Total_Debit']].copy()
                debit_rows = debit_rows[debit_rows['Total_Debit'] > 0]
                
                # Calculate total
                total_debit = debit_rows['Total_Debit'].sum()
                
                # Display results
                st.success(f"Total Debit + Withdrawals amount: {total_debit:.2f}")
                
                st.subheader("Rows considered for Debit + Withdrawals Calculation")
                st.write(debit_rows)
    
        else:
            st.error("No tables found in the uploaded PDF.")
    
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
