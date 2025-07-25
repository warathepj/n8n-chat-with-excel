import pandas as pd
import requests
import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

CHAT_WEBHOOK_URL = 'http://localhost:5678/webhook-test/46351b0f-1a6a-4f90-9507-9f633b03aa6b'

# Global variable to track if sales data has been sent in the current session
first_message_sent = False
sales_data_global = None # To store sales data once fetched

@app.route('/chat', methods=['POST'])
def chat():
    global first_message_sent
    global sales_data_global

    user_message = request.json.get('message')
    if user_message:
        data_to_send = {'message': user_message}
        
        if not first_message_sent and sales_data_global is not None:
            data_to_send['sales_data'] = sales_data_global
            first_message_sent = True
            print("Sales data included in the first chat message.")
        
        # Send the combined data to the chat webhook and get its response
        webhook_response_text = send_data_to_webhook(data_to_send, CHAT_WEBHOOK_URL)
        
        if webhook_response_text:
            try:
                # The webhook_response_text is now already cleaned in send_data_to_webhook
                response_json = json.loads(webhook_response_text)
                print(f"DEBUG: response_json type: {type(response_json)}, content: {response_json}")
                
                if isinstance(response_json, dict) and 'output' in response_json:
                    raw_output = response_json['output']
                    
                    cleaned_lines = []
                    for line in raw_output.split('\n'):
                        temp_line = line.replace('###', '').replace('---', '').replace('*', '').replace('|', '')
                        cleaned_line = ' '.join(temp_line.split()).strip()
                        if cleaned_line:
                            cleaned_lines.append(cleaned_line)
                    
                    bot_response = '\n'.join(cleaned_lines)
                else:
                    bot_response = "Webhook response: Not a JSON object with 'output' key."
            except json.JSONDecodeError:
                print(f"DEBUG: JSONDecodeError for text: {webhook_response_text}")
                bot_response = webhook_response_text
            except Exception as e:
                print(f"DEBUG: General error: {e} for text: {webhook_response_text}")
                bot_response = f"Error processing webhook response: {e}"
        else:
            bot_response = f"Your message: '{user_message}' has been sent to the chat webhook, but no specific response was received."
            if 'sales_data' in data_to_send:
                bot_response += " (Sales data also sent as it's the first message)."
        
        return jsonify({'response': bot_response})
    return jsonify({'error': 'No message provided'}), 400

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
        
        # Decode content explicitly and strip whitespace
        decoded_response_text = response.content.decode('utf-8').strip()
        print(f"Response (decoded and stripped): {decoded_response_text}") # Updated print
        return decoded_response_text
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to webhook: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    excel_file = "daily sales.xlsx"
    sales_data = fetch_sales_data(excel_file)

    if sales_data is not None:
        print("\nSales data processing complete.")
        # Convert Timestamp objects to string format for JSON serialization
        for col in sales_data.columns:
            if pd.api.types.is_datetime64_any_dtype(sales_data[col]):
                sales_data[col] = sales_data[col].apply(lambda x: x.isoformat())
        
        # Assign sales_data to the global variable
        sales_data_global = sales_data.to_dict(orient='records')

        # The initial send of sales_data to webhook is removed as per the task.
        # It will now only be sent with the first chat message.
    
    app.run(debug=True)
