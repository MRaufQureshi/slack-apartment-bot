import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack bot credentials from GitHub Secrets
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

# URL to monitor
URL = "https://www.degewo.de/immosuche#openimmo-search-result"

# File to store the last fetched HTML
HTML_FILE = "last_page.html"

# Function to fetch the full HTML of the page
def fetch_html():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Error fetching the website. Status code: {response.status_code}")
        return None
    return response.text

# Function to save the HTML to a file
def save_html(html_content):
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML saved to", HTML_FILE)

# Function to load the last saved HTML
def load_last_html():
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return None

# Function to send message to Slack
def send_slack_message(message):
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print("Slack message sent:", message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Main function
def main():
    current_html = fetch_html()
    if current_html is None:
        return  # Exit if we couldn't fetch the page

    last_html = load_last_html()

    if last_html is None:
        # First-time run: Save the HTML and notify
        save_html(current_html)
        send_slack_message("🔍 *Initial website HTML saved!* Monitoring for changes...")
    elif current_html != last_html:
        # If the HTML has changed, notify and update the saved file
        send_slack_message("🚨 *Website content has changed!* Check for new listings.")
        save_html(current_html)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
