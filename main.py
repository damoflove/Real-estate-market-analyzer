import streamlit as st
import pandas as pd
import io

def safe_str_convert(series):
    """Safely convert series to string type for string operations"""
    return series.astype(str) if series.dtype != 'object' else series

def main():
    st.title("Real Estate Market Analyzer")
    st.write("Upload your data in CSV format to calculate average prices and listing counts.")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        try:
            # Read and process data
            df = pd.read_csv(uploaded_file)
            
            # Clean price column
            if 'price' in df.columns:
                df['price'] = (
                    safe_str_convert(df['price'])
                    .str.replace(r'[^\d.]', '', regex=True)
                    .astype(float)
                )

            # Clean bedrooms
            if 'beds' in df.columns:
                df['beds'] = (
                    safe_str_convert(df['beds'])
                    .str.replace('Studio', '0', case=False)
                    .str.extract(r'(\d+)', expand=False)
                    .fillna(0)
                    .astype(int)
                )

            # Clean bathrooms
            if 'baths' in df.columns:
                df['baths'] = (
                    safe_str_convert(df['baths'])
                    .str.extract(r'(\d+)', expand=False)
                    .fillna(0)
                    .astype(int)
                )

            # Clean zipcode
            if 'zipcode' in df.columns:
                df['zipcode'] = (
                    safe_str_convert(df['zipcode'])
                    .str.split('.').str[0]
                    .astype(float)
                    .astype('Int64')
                )

            # Clean square footage
            if 'sqft' in df.columns:
                df['sqft'] = (
                    safe_str_convert(df['sqft'])
                    .str.replace(',', '')
                    .str.replace(' sqft', '')
                    .str.extract(r'(\d+)', expand=False)
                    .astype(float)
                )

            # Drop rows with missing critical data
            df = df.dropna(subset=['price', 'zipcode', 'property_type', 'sqft'])

            # Create a function to filter data by +/-150 sqft
            def filter_sqft(group):
                reference_sqft = group['sqft'].median()
                return group[(group['sqft'] >= reference_sqft - 150) & (group['sqft'] <= reference_sqft + 150)]

            # Apply grouping and filtering
            grouped = (
                df.groupby(['property_type', 'zipcode', 'beds', 'baths'])
                .apply(filter_sqft)
                .reset_index(drop=True)  # Reset index before final aggregation
                .groupby(['property_type', 'zipcode', 'beds', 'baths'])
                .agg(
                    Average_Price=('price', 'mean'),
                    Count=('price', 'size')
                )
                .reset_index()  # Reset index for proper output
            )

            # Filter for meaningful results (at least 3 listings)
            filtered_result = grouped[grouped['Count'] >= 3]

            # Format numbers for display
            display_df = filtered_result.copy()
            display_df['Average_Price'] = display_df['Average_Price'].round(2)
            display_df['zipcode'] = display_df['zipcode'].astype(str)

            st.write("Average Price Results:")
            st.dataframe(display_df)

            # Create downloadable CSV
            output = io.StringIO()
            filtered_result.to_csv(output, index=False)
            csv_data = output.getvalue()

            # Download button for the filtered results
            st.download_button(
                label="Download Average Price Results",
                data=csv_data,
                file_name='filtered__averages__prices.csv',
                mime='text/csv'
            )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
