import pandas as pd

def fetch_sales_data(file_path):
    """
    Fetches sales data from an Excel file.
    """
    try:
        df = pd.read_excel(file_path)
        print("Data fetched successfully:")
        print(df.head())  # Print the first 5 rows of the DataFrame
        return df
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    excel_file = "daily sales.xlsx"
    sales_data = fetch_sales_data(excel_file)

    if sales_data is not None:
        print("\nSales data processing complete.")
