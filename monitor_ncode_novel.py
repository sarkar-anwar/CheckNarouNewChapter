import os
import requests

# Configuration from environment variables / GitHub Secrets
NOVEL_ID = "n4830bu"
MESSAGE_HEADER = "New Hannelore chapter is out! "
PING_ROLE = " <@&YOUR_ROLE_ID>"  # Leave as "" if not needed
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
STATE_FILE = "last_chapter.txt"

def send_discord_webhook(chapter_url):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL is not set.")
        return

    data = {
        "content": f"{MESSAGE_HEADER}{chapter_url}{PING_ROLE}"
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code in range(200, 300):
        print("Discord notification sent successfully!")
    else:
        print(f"Discord webhook failed with status: {response.status_code}")

def check_novel():
    clean_id = NOVEL_ID.strip("/")
    baselink = f"https://syosetu.com{clean_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(baselink, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return
    content = response.text

    # Load the last known chapter from the state file
    current_chapter = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            saved_val = f.read().strip()
            if saved_val.isdigit():
                current_chapter = int(saved_val)

    word = f"{clean_id}/{current_chapter + 1}/"

    # If state file didn't exist (first run), find the current latest chapter without pinging
    if current_chapter == 0:
        print("First run detected. Finding current latest chapter...")
        while word in content:
            current_chapter += 1
            word = f"{clean_id}/{current_chapter + 1}/"
        print(f"Baseline set to chapter {current_chapter}.")
    else:
        # Check for new chapters and notify Discord
        while word in content:
            print(f"Found new chapter: {current_chapter + 1}!")
            link_to_new_chapter = f"{baselink}{current_chapter + 1}/"
            send_discord_webhook(link_to_new_chapter)
            current_chapter += 1
            word = f"{clean_id}/{current_chapter + 1}/"

    # Save the updated chapter number back to the file
    with open(STATE_FILE, "w") as f:
        f.write(str(current_chapter))

if __name__ == "__main__":
    check_novel()
