import streamlit as st
import pdfplumber
import pandas as pd

# Streamlit Web App Title
st.title("Bank Statement Debit Calculator (with PDF Password Support)")

# Password input field
password = st.text_input("Enter PDF password (if locked)", type="password").strip()

    
# File uploader for PDF
uploaded_file = st.file_uploader("Upload your bank statement PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # Open the PDF file with or without password
        with pdfplumber.open(uploaded_file, password=password if password else None) as pdf:
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
                df = pd.DataFrame(table[1:], columns=table[0])
                all_data.append(df)
            
            combined_df = pd.concat(all_data, ignore_index=True)
            
            st.subheader("Combined Extracted Table")
            st.write(combined_df.head())
            
            description_column = 'Description'
            debit_column = None
            withdrawals_column = None
            
            if 'Debit' in combined_df.columns:
                debit_column = 'Debit'
                combined_df[debit_column] = combined_df[debit_column].str.replace(',', '', regex=False)
                combined_df[debit_column] = pd.to_numeric(combined_df[debit_column], errors='coerce')
            if 'Withdrawals' in combined_df.columns:
                withdrawals_column = 'Withdrawals'
                combined_df[withdrawals_column] = combined_df[withdrawals_column].str.replace(',', '', regex=False)
                combined_df[withdrawals_column] = pd.to_numeric(combined_df[withdrawals_column], errors='coerce')
            
            if not debit_column and not withdrawals_column:
                st.error("Neither 'Debit' nor 'Withdrawals' column found in the table.")
            else:
                combined_df['Total_Debit'] = 0
                if debit_column:
                    combined_df['Total_Debit'] += combined_df[debit_column].fillna(0)
                if withdrawals_column:
                    combined_df['Total_Debit'] += combined_df[withdrawals_column].fillna(0)
                
                debit_rows = combined_df[[description_column, 'Total_Debit']].copy()
                debit_rows = debit_rows[debit_rows['Total_Debit'] > 0]
                
                total_debit = debit_rows['Total_Debit'].sum()
                
                st.success(f"Total Debit + Withdrawals amount: {total_debit:.2f}")
                
                st.subheader("Rows considered for Debit + Withdrawals Calculation")
                st.write(debit_rows)
    
        else:
            st.error("No tables found in the uploaded PDF.")
    
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
