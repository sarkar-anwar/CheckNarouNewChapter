import asyncio
import datetime
import aiohttp

# Helper function for timestamped logs
def log(message, level="INFO"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] [{level}] {message}")

async def call_discord_webhook(webhook_url, chapter_url, message_header, ping_role):
    data = {
        "content": f"{message_header}{chapter_url}{ping_role}"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=data) as response:
                if response.status not in range(200, 300):
                    log(f"Discord webhook failed with status: {response.status}", level="WARNING")
                else:
                    log("Discord notification sent successfully!")
        except aiohttp.ClientError as e:
            log(f"Failed to send Discord webhook: {e}", level="WARNING")

async def monitor_novel(novel_id, message_header, ping_role="", webhook_url="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", interval_minutes=5):
    """
    Continuously checks Shōsetsuka ni Narō for new chapters of a given novel ID.
    """
    # Clean the novel_id and construct the base URL
    clean_id = novel_id.strip("/")
    baselink = f"https://syosetu.com{clean_id}/"
    current_chapter = 0
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    headers = {'User-Agent': user_agent}

    log(f"Starting chapter monitor for {clean_id} ({baselink})...")

    while True:
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(baselink) as response:
                    if response.status != 200:
                        log(f"[{clean_id}] Failed to fetch page. Status code: {response.status}", level="WARNING")
                        await asyncio.sleep(interval_minutes * 60)
                        continue
                    content = await response.text()
            except aiohttp.ClientError as e:
                log(f"[{clean_id}] Network error fetching chapter index: {e}", level="WARNING")
                await asyncio.sleep(interval_minutes * 60)
                continue

        word = f"{clean_id}/{current_chapter + 1}/"

        # Initial run: find the current latest chapter
        if current_chapter == 0:
            log(f"[{clean_id}] First time running. Finding the latest chapter number...")
            while word in content:
                current_chapter += 1
                word = f"{clean_id}/{current_chapter + 1}/"
            log(f"[{clean_id}] Latest chapter number = {current_chapter}")

        # Subsequent runs: check if the next chapter exists
        # Using a while loop here ensures that if 2 chapters drop at once, both get caught
        while word in content:
            log(f"[{clean_id}] Found chapter {current_chapter + 1}!")
            link_to_new_chapter = f"{baselink}{current_chapter + 1}/"
            
            await call_discord_webhook(webhook_url, link_to_new_chapter, message_header, ping_role)
            
            current_chapter += 1
            word = f"{clean_id}/{current_chapter + 1}/"
            log(f"[{clean_id}] Now checking for chapter {current_chapter + 1}")

        # Wait before the next check
        await asyncio.sleep(interval_minutes * 60)

# ==========================================
# RUN THE FUNCTION
# ==========================================
await monitor_novel(
    novel_id="n4830bu",  # Just the n-code (e.g., "n4830bu")
    message_header="New Hannelore chapter is out! ",
    ping_role=" <@&YOUR_ROLE_ID>", # Optional: leave as "" if no ping is needed
    webhook_url="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)
