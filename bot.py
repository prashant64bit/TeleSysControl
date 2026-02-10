from telethon import TelegramClient, events, Button
from config import apiID, apiHASH, botToken, ownerId

client = TelegramClient(
    "botsession",
    apiID,
    apiHASH,
    connection_retries=None,
    retry_delay=5,
    timeout=30,
    flood_sleep_threshold=60
)