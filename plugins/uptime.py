import time
from datetime import timedelta
from telethon import events, Button
from bot import client
from config import ownerId
import psutil
from utils import safeEdit

def getUptime():
    uptimeSeconds = time.time() - psutil.boot_time()
    delta = timedelta(seconds=int(uptimeSeconds))
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)

def getUptimeButtons():
    return [
        [Button.inline("Refresh", b"uptime")],
        [Button.inline("Back", b"back")]
    ]

@client.on(events.CallbackQuery(data=b"uptime"))
async def showUptime(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return
    uptimeStr = getUptime()
    text = f"**System Uptime**: {uptimeStr}"
    await safeEdit(event, text, getUptimeButtons())