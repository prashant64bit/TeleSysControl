import asyncio
import os
import sys
import subprocess
from pathlib import Path
from telethon import TelegramClient, events, Button
from bot import client
from config import apiID, apiHASH, botToken, ownerId

def load_plugins():
    plugin_dir = Path(__file__).parent / "plugins"
    for file in plugin_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_name = f"plugins.{file.stem}"
        __import__(module_name)

@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    if event.sender_id != ownerId:
        return
    await event.reply("Control Panel", buttons=[
        [Button.inline("System Status", b"stats")],
        [Button.inline("Power Control", b"power")],
        [Button.inline("Screenshot", b"screenshot")]
    ])

async def main():
    load_plugins()
    await client.start(bot_token=botToken)
    print("Bot started.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")