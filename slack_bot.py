import os
import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack bot credentials from GitHub Secrets
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

# URL to monitor
URL = "https://www.degewo.de/immosuche#openimmo-search-result"

# Function to get apartment listings
def get_apartment_listings():
    response = requests.get(URL)
    if response.status_code != 200:
        print("Error fetching the website")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Example: Find apartment listings (adjust based on actual website structure)
    apartments = soup.find_all("article", class_=".article-list__item--immosearch")
    
    listings = []
    for apt in apartments:
        title = apt.find("h2").text.strip()
        link = apt.find("a")["href"]
        listings.append(f"{title}\n{link}")
    
    return listings

# Function to send message to Slack
def send_slack_message(message):
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Main function
def main():
    apartments = get_apartment_listings()
    if apartments:
        message = "*New Apartment Listings Found!*\n\n" + "\n\n".join(apartments)
        send_slack_message(message)
    else:
        print("No new listings found.")

if __name__ == "__main__":
    main()
