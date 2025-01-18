import streamlit as st
import pandas as pd
import io

# Streamlit App
def main():
    st.title("Rental Market Analyzer")
    st.write("Upload your rental data in CSV format to calculate average prices and listing counts.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file:
        try:
            # Read the uploaded file into a Pandas DataFrame
            df = pd.read_csv(uploaded_file)
            st.write("Data Preview:")
            st.dataframe(df.head())
            
            # Ensure required columns exist
            required_columns = {'bedrooms', 'bathrooms', 'zipcode', 'price'}
            if not required_columns.issubset(df.columns):
                st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
                return
            
            # Clean the data: Remove rows with missing values in relevant columns
            df.dropna(subset=['bedrooms', 'bathrooms', 'zipcode', 'price'], inplace=True)
            
            # Group by zip code, bedroom, and bathroom, and calculate average price and count
            grouped = df.groupby(['zipcode', 'bedrooms', 'bathrooms']).agg(
                Average_Price=('price', 'mean'),
                Count=('price', 'size')
            ).reset_index()
            
            # Filter out groups with fewer than 3 listings
            filtered_result = grouped[grouped['Count'] >= 3]
            
            # Display the result
            st.write("Filtered Results:")
            st.dataframe(filtered_result)
            
            # Create a CSV download button
            csv = convert_df_to_csv(filtered_result)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_rent_data.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

def convert_df_to_csv(df):
    """Convert a DataFrame to a CSV string."""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

if __name__ == "__main__":
    main()
