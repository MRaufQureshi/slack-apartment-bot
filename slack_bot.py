import os
import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json

# Slack bot credentials from GitHub Secrets
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

# URL to monitor
URL = "https://www.degewo.de/immosuche#openimmo-search-result"

# File to store the last fetched listings
LISTINGS_FILE = "last_listings.json"

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
            link_tag = apt.find("a", href=True)
            if link_tag:
                title = link_tag.text.strip()
                link = "https://www.degewo.de" + link_tag["href"]  # Append base URL
                listings.append(f"{title}\n{link}")
    
    return listings

# Function to save the current listings to a file
def save_listings(listings):
    with open(LISTINGS_FILE, "w") as f:
        json.dump(listings, f)

# Function to load the last fetched listings from the file
def load_last_listings():
    if os.path.exists(LISTINGS_FILE):
        try:
            with open(LISTINGS_FILE, "r") as f:
                listings = json.load(f)
                if not listings:  # If the file is empty, return an empty list
                    return []
                return listings
        except json.JSONDecodeError:
            # If the file is corrupted or invalid, return an empty list
            return []
    else:
        return []

# Function to send message to Slack
def send_slack_message(message):
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

# Main function
def main():
    # Get the current apartment listings
    current_listings = get_apartment_listings()

    # Load the previously fetched listings
    last_listings = load_last_listings()

    if not last_listings:  # If there are no previous listings (empty or first run)
        # Save the current listings to the file for future comparison
        save_listings(current_listings)
        message = "*Initial Apartment Listings Scraped and Saved! 🎉*\n\n" + "\n\n".join(current_listings)
        send_slack_message(message)
    else:
        # Find new listings by comparing current listings to last ones
        new_listings = [listing for listing in current_listings if listing not in last_listings]

        if new_listings:
            message = "*New Apartment Listings Found! 🎉*\n\n" + "\n\n".join(new_listings)
            send_slack_message(message)
            # Save the current listings to the file for future comparison
            save_listings(current_listings)
        else:
            message = "*🤖 No new listings found.*"
            send_slack_message(message)

if __name__ == "__main__":
    main()
