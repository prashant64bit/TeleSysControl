from datetime import datetime
from PIL import ImageGrab
from telethon import events
from bot import client
from config import ownerId
import os

@client.on(events.CallbackQuery(data=b"screenshot"))
async def takeScreenshot(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return

    await event.answer("Capturing...", alert=False)
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{ts}.png"
        ImageGrab.grab().save(filename, "PNG")
        await event.client.send_file(event.chat_id, filename, caption=ts, force_document=True)
        os.remove(filename)
    except Exception as e:
        await event.answer(f"Failed: {str(e)}", alert=True)