import asyncio
from pathlib import Path
from telethon import events, Button
from bot import client
from config import botToken

def getMainMenuButtons():
    return [
        [Button.inline("System Status", b"stats")],
        [Button.inline("Power Control", b"power")],
        [Button.inline("Screenshot", b"screenshot")],
        [Button.inline("Volume Control", b"volume")]
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
    await client.start(bot_token=botToken)
    print("Bot started.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")