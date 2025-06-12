import pandas as pd
import requests
import json

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

def send_data_to_webhook(data, url):
    """
    Sends data to the specified webhook URL.
    """
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(f"Data successfully sent to webhook. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to webhook: {e}")

if __name__ == "__main__":
    excel_file = "daily sales.xlsx"
    sales_data = fetch_sales_data(excel_file)

    if sales_data is not None:
        print("\nSales data processing complete.")
        # Convert Timestamp objects to string format for JSON serialization
        for col in sales_data.columns:
            if pd.api.types.is_datetime64_any_dtype(sales_data[col]):
                sales_data[col] = sales_data[col].apply(lambda x: x.isoformat())

        webhook_url = "http://localhost:5678/webhook-test/46351b0f-1a6a-4f90-9507-9f633b03aa6b"
        send_data_to_webhook(sales_data.to_dict(orient='records'), webhook_url)
