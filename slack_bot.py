import os
import requests
import subprocess
import time  # Import time module for sleep
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack bot credentials
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

# URL to monitor
URL = "https://www.degewo.de/immosuche#openimmo-search-result"

# File to store the last fetched HTML
HTML_FILE = "last_page.html"

# Time interval for checking the website (in seconds)
CHECK_INTERVAL = 300  # 5 minutes
NO_CHANGE_MESSAGE_INTERVAL = 12  # Send no change message every 12 checks (1 hour)

# Function to fetch the full HTML of the page
def fetch_html():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Error fetching the website. Status code: {response.status_code}")
        return None
    return response.text

# Function to save HTML content to a file
def save_html(html_content):
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML saved to {HTML_FILE}")

# Function to load last saved HTML
def load_last_html():
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return None

# Function to send a Slack notification
def send_slack_message(message):
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print("Slack message sent:", message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Function to commit and push changes to GitHub
def commit_and_push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", HTML_FILE], check=True)
        subprocess.run(["git", "diff", "--staged", "--quiet"], check=False)  # Check if there are changes
        subprocess.run(["git", "commit", "-m", "Update last_page.html"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Changes committed and pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("No changes detected. Skipping commit.")

# Main function
def main():
    no_change_counter = 0  # Counter for no change messages
    while True:  # Infinite loop
        current_html = fetch_html()
        if current_html is None:
            print("Failed to fetch HTML, skipping this iteration.")
            time.sleep(CHECK_INTERVAL)
            continue  # Exit if fetching failed

        last_html = load_last_html()

        if last_html is None:
            # First-time run: Save the HTML, notify, and push changes to GitHub
            save_html(current_html)
            commit_and_push_changes()
            send_slack_message("🔍 *Initial website HTML saved!* Monitoring for changes...")
        elif current_html != last_html:
            # If the HTML has changed, notify, update the file, and push changes
            send_slack_message("🚨 *Website content has changed!* Check for new listings.")
            save_html(current_html)
            commit_and_push_changes()
            no_change_counter = 0  # Reset counter on change
        else:
            # Increment counter for every pass with no changes
            no_change_counter += 1
            if no_change_counter >= NO_CHANGE_MESSAGE_INTERVAL:
                # Send a message to confirm that the script ran with no changes
                send_slack_message("🔄 Compared it with the file, no changes found until now.")
                no_change_counter = 0  # Reset counter after sending

        # Wait for the defined check interval before checking again
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()