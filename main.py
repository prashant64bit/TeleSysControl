import asyncio
import time
from pathlib import Path
from telethon import events, Button
from bot import client
from config import botToken

def getMainMenuButtons():
    return [
        [Button.inline("System Status", b"stats")],
        [Button.inline("Uptime", b"uptime")],
        [Button.inline("CMD", b"cmd")],
        [Button.inline("Volume Control", b"volume")],
        [Button.inline("Power Control", b"power")],
        [Button.inline("Speed Test", b"speedtest")],
        [Button.inline("Screenshot", b"screenshot")]
    ]

@client.on(events.NewMessage(pattern="/start"))
async def startHandler(event):
    await event.reply("Control Panel", buttons=getMainMenuButtons())

@client.on(events.CallbackQuery(data=b"back"))
async def backToMain(event):
    await event.edit("Control Panel", buttons=getMainMenuButtons())

def loadPlugins():
    pluginDir = Path(__file__).parent / "plugins"
    for file in pluginDir.glob("*.py"):
        if file.name == "__init__.py":
            continue
        moduleName = f"plugins.{file.stem}"
        __import__(moduleName)

async def main():
    loadPlugins()
    while True:
        try:
            await client.start(bot_token=botToken)
            print(f"[{time.strftime('%H:%M:%S')}] Bot started.")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {type(e).__name__}: {e}")
            print("Reconnecting in 7s...")
            await asyncio.sleep(7)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")