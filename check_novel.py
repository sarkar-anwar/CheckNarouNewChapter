import json
import os
import time
import requests

# 1. ADD YOUR NOVELS HERE
NOVELS = [
    {
        "novel_id": "n4750dy",
        "message_header": "New Hannelore chapter is out! ",
        "ping_role": " <@&821044829004890192>"  # Optional: leave as "" if no ping is needed
    },
    {
        "novel_id": "n7835cj",  # Example second novel
        "message_header": "A new SS chapter is out! ",
        "ping_role": " <@&821044829004890192>"
    }
]

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
STATE_FILE = "chapters.json"

def send_discord_webhook(chapter_url, message_header, ping_role):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL is not set.")
        return

    data = {
        "content": f"{message_header}{chapter_url}{ping_role}"
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code in range(200, 300):
        print("Discord notification sent successfully!")
    else:
        print(f"Discord webhook failed with status: {response.status_code}")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def check_all_novels():
    state = load_state()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for novel in NOVELS:
        clean_id = novel["novel_id"].strip("/")
        baselink = f"https://ncode.syosetu.com/" + clean_id + "/"
        print(f"Checking {clean_id}...")

        try:
            response = requests.get(baselink, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"[{clean_id}] Failed to fetch page. Status code: {response.status_code}")
                continue
            content = response.text
        except requests.RequestException as e:
            print(f"[{clean_id}] Network error: {e}")
            continue

        current_chapter = state.get(clean_id, 0)
        word = f"{clean_id}/{current_chapter + 1}/"

        # If novel isn't in chapters.json yet, find the current latest chapter as baseline
        if current_chapter == 0:
            print(f"[{clean_id}] First time tracking. Finding current latest chapter...")
            while word in content:
                current_chapter += 1
                word = f"{clean_id}/{current_chapter + 1}/"
            print(f"[{clean_id}] Baseline set to chapter {current_chapter}.")
        else:
            # Check for any new chapters and send alerts
            while word in content:
                print(f"[{clean_id}] Found new chapter: {current_chapter + 1}!")
                link_to_new_chapter = f"{baselink}{current_chapter + 1}/"
                send_discord_webhook(
                    link_to_new_chapter,
                    novel["message_header"],
                    novel.get("ping_role", "")
                )
                current_chapter += 1
                word = f"{clean_id}/{current_chapter + 1}/"
                time.sleep(1)  # Brief pause to respect Discord rate limits

        state[clean_id] = current_chapter
        time.sleep(2)  # Polite delay between Syosetu requests

    save_state(state)

if __name__ == "__main__":
    check_all_novels()
