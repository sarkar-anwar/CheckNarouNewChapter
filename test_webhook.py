import os
import sys
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TEST_MESSAGE = "✅ **GitHub Actions Test:** Your Syosetu Discord webhook is connected and working!"
# Optional: Add your role ID below (e.g., " <@&123456789>") to test role pings too, or leave empty
PING_ROLE = ""

def send_test_webhook():
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
        sys.exit(1)

    data = {
        "content": f"{TEST_MESSAGE}{PING_ROLE}"
    }

    response = requests.post(WEBHOOK_URL, json=data, timeout=10)
    
    if response.status_code in range(200, 300):
        print("Success! Test notification sent to Discord.")
    else:
        print(f"Failed! Discord returned status {response.status_code}: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    send_test_webhook()
