# ซอร์สโค้ดนี้ ใช้สำหรับเป็นตัวอย่างเท่านั้น ถ้านำไปใช้งานจริง ผู้ใช้ต้องจัดการเรื่องความปลอดภัย และ ประสิทธิภาพด้วยตัวเอง

# Chat with Excel

Chat with Excel is a web application that allows users to interact with data from an Excel spreadsheet through a chat interface. It sends user queries, and initially the entire Excel dataset, to an external webhook, typically an n8n workflow, for processing. The n8n workflow then uses AI models to understand the query in context of the Excel data and generate a response, which is then displayed back to the user in the chat interface.

## Features

*   **Interactive Chat Interface**: Simple and intuitive UI for asking questions about Excel data.
*   **Excel Data Integration**: Loads data from a specified Excel file (e.g., `daily sales.xlsx`) at startup.
*   **Webhook Communication**:
    *   Sends the user's message to a configurable external webhook.
    *   On the first user interaction of a session, it also sends the complete Excel data (in JSON format) along with the message.
    *   Subsequent messages in the same session only send the user's query.
*   **Response Handling**: Receives responses from the webhook, cleans them if necessary (removes markdown-like characters), and displays them in the chat.
*   **Flask Backend**: Built with Python and Flask.
*   **Pandas for Data Handling**: Uses pandas to read and process Excel data.

## How it Works

The application consists of a frontend (HTML, CSS, JavaScript) and a backend (Python, Flask).

1.  **Frontend (`index.html`)**:
    *   Provides a chat window for users to type messages.
    *   When a user sends a message, a JavaScript function makes a `POST` request to the `/chat` endpoint on the Flask backend.
    *   Displays messages from both the user and the bot (responses from the backend).

2.  **Backend (`main.py`)**:
    *   **Initialization**:
        *   On startup, the Flask application loads data from an Excel file (e.g., `daily sales.xlsx`) into a pandas DataFrame.
        *   Date/time columns in the Excel data are converted to ISO format strings for JSON serialization.
        *   This data is stored globally.
    *   **`/chat` Endpoint**:
        *   Receives the user's message as JSON.
        *   Checks if it's the first message of the session.
            *   If yes, it prepares a payload containing both the user's message and the pre-loaded Excel data (as a list of dictionaries).
            *   If no, the payload only contains the user's message.
        *   Sends this payload to a pre-configured `CHAT_WEBHOOK_URL`.
        *   Receives the response from the webhook.
        *   It expects the webhook to return a JSON response, ideally with an `output` key containing the bot's reply.
        *   The response text is cleaned (e.g., removing `###`, `---`, `*`, `|` characters and extra whitespace) before being sent back to the frontend.
    *   **`/` Endpoint**: Serves the `index.html` page.

## n8n Flow

n8n workflow designed to process the chat messages and Excel data. This workflow acts as the backend for the `CHAT_WEBHOOK_URL` configured in `main.py`.

### Workflow Overview

*   **Webhook Node**: This node (`Webhook`) is the entry point of the n8n workflow. It listens for incoming `POST` requests from the Flask application's `/chat` endpoint.
*   **AI Agent Node**: The `AI Agent` node (`@n8n/n8n-nodes-langchain.agent`) is configured to use a language model and memory to process the user's question and the provided Excel data.
    *   **Prompt**: The prompt is dynamically constructed using `={{ $json.body.message }}` for the user's question and `{{ JSON.stringify($json.body.sales_data) }}` for the Excel data, allowing the AI to act as an Excel data analysis expert.
*   **Google Gemini Chat Model Node**: This node (`Google Gemini Chat Model`) provides the AI language model (`models/gemini-2.5-flash-preview-05-20`) used by the AI Agent for generating responses.
*   **Simple Memory Node**: The `Simple Memory` node (`@n8n/n8n-nodes-langchain.memoryBufferWindow`) maintains session context, ensuring that subsequent messages in a conversation are handled with awareness of previous interactions. The session key is set to `={{ $json.body }}`.
*   **Respond to Webhook Node**: This node (`Respond to Webhook`) sends the AI Agent's response back to the Flask application.

### How to Use the n8n Flow

1.  **Create the Flow**: In your n8n create workflow.
2.  **Activate the Workflow**: Ensure the workflow is active in n8n.
3.  **Configure Webhook URL**: Copy the webhook URL from the `Webhook` node in n8n (it will typically look like `YOUR_N8N_INSTANCE_URL/webhook/aaa51b0f-1a6a-4f90-9507-9f633b03abbb`) and set it as the `CHAT_WEBHOOK_URL` in your `main.py` file.

## Setup and Installation

1.  **Prerequisites**:
    *   Python 3.x
    *   pip (Python package installer)

2.  **Clone the Repository (if applicable)**:
    ```bash
    git clone https://github.com/warathepj/n8n-chat-with-excel.git
    cd n8n-chat-with-excel
    ```

3.  **Install Dependencies**:
    The project dependencies are listed in `requirements.txt`. You can install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare Excel File**:
    *   Place your Excel data file (e.g., `daily sales.xlsx`) in the root directory of the project, or update the `excel_file` variable in `main.py` to point to its location.

5.  **Configure Webhook URL**:
    *   Open `main.py`.
    *   Modify the `CHAT_WEBHOOK_URL` constant to point to your actual chat processing webhook.
      ```python
      CHAT_WEBHOOK_URL = 'YOUR_ACTUAL_WEBHOOK_URL_HERE'
      ```
    *   The webhook should be capable of receiving a JSON payload with a `message` key (string) and optionally a `sales_data` key (list of records). It should return a JSON response, ideally with an `output` key containing the text response.

6.  **Run the Application**:
    ```bash
    python main.py
    ```
    The application will start, typically on `http://127.0.0.1:5000/`.

7.  **Access the Application**:
    *   Open your web browser and navigate to `http://120.0.1:5000/`.

## Usage

1.  Once the application is running and you've opened it in your browser, you'll see a chat interface.
2.  Type your question or query related to the Excel data into the input field at the bottom.
3.  Press "Send" or hit Enter.
4.  Your message will be sent to the backend. If it's your first message, the Excel data will also be sent to the webhook.
5.  The response from the webhook will be processed and displayed in the chat window.

## Project Structure

. ├── main.py # Flask backend logic ├── templates/ │ └── index.html # Frontend HTML, CSS, and JavaScript └── daily sales.xlsx # Example Excel data file (you need to provide this) └── README.md # This file

plaintext

## Key Components in `main.py`

*   **`fetch_sales_data(file_path)`**: Reads the Excel file into a pandas DataFrame.
*   **`send_data_to_webhook(data, url)`**: Sends JSON data to the specified webhook URL and returns the response text.
*   **`chat()` (route: `/chat`)**: Handles incoming chat messages, interacts with the webhook, processes the response, and returns it to the frontend.
*   **Global Variables**:
    *   `first_message_sent`: Tracks if the initial message (with sales data) has been sent.
    *   `sales_data_global`: Stores the loaded Excel data.
*   **Data Preprocessing**: Converts datetime objects from Excel into ISO format strings for JSON compatibility.
*   **Response Cleaning**: The chat response from the webhook undergoes cleaning to remove common markdown-like formatting characters before being displayed.

## Future Improvements / Considerations

*   **Error Handling**: Enhance error handling for webhook communication and data processing.
*   **Session Management**: Implement more robust session management if persistence across browser refreshes or multiple users is needed (currently, `first_message_sent` is global and resets on app restart).
*   **Security**: If dealing with sensitive data, ensure secure communication with the webhook (HTTPS) and consider authentication/authorization.
*   **Streaming Responses**: For long-running webhook processes, consider streaming responses to the frontend.
*   **Configuration File**: Move configurations like `CHAT_WEBHOOK_URL` and `excel_file` to a separate configuration file or environment variables.
*   **Frontend Enhancements**: Improve UI/UX, add loading indicators, etc.
    *   **Loading Indicators**: Display a visual cue while waiting for the webhook response.
    *   **Message Formatting**: Better rendering of multi-line responses or responses with special formatting (e.g., tables, lists if the AI provides them).
    *   **Input History**: Allow users to navigate through previously sent messages.
    *   **Clear Chat**: Add a button to clear the current chat history.
    *   **Responsive Design**: Ensure the chat interface works well on different screen sizes.
