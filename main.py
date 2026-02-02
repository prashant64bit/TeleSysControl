import asyncio
import os
import sys
import subprocess
from pathlib import Path
from telethon import TelegramClient, events, Button
from telethon.errors import MessageNotModifiedError

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID

try:
    from plugins import SystemStatus, screenshot, powercontrol
except ImportError:
    print("Some plugin modules are missing.")
    sys.exit(1)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

client = TelegramClient("botsession", API_ID, API_HASH)


def main_buttons():
    return [
        [Button.inline("System Status", b"stats")],
        [Button.inline("Power Control", b"power")],
        [Button.inline("Screenshot", b"screenshot")]
    ]


def stats_buttons():
    return [
        [Button.inline("Refresh", b"stats")],
        [Button.inline("Back", b"back")]
    ]


def power_buttons():
    return [
        [Button.inline("Sleep", b"sleep")],
        [Button.inline("Shutdown", b"shutdown")],
        [Button.inline("Restart", b"restart")],
        [Button.inline("Hibernate", b"hibernate")],
        [Button.inline("Back", b"back")]
    ]


@client.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    if event.sender_id != OWNER_ID:
        return
    await event.reply("Control Panel", buttons=main_buttons())


@client.on(events.CallbackQuery)
async def callback_handler(event):
    if event.sender_id != OWNER_ID:
        await event.answer("Access denied", alert=True)
        return

    data = event.data

    try:
        if data == b"stats":
            await event.edit(
                await SystemStatus.get_stats(),
                buttons=stats_buttons()
            )

        elif data == b"power":
            await event.edit("Power Control", buttons=power_buttons())

        elif data == b"back":
            await event.edit("Control Panel", buttons=main_buttons())

        elif data == b"screenshot":
            await screenshot.handle_screenshot(event)

        elif data == b"sleep":
            await event.answer("Entering sleep...", alert=True)
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        elif data == b"shutdown":
            await event.answer("Shutting down in 5 seconds...", alert=True)
            os.system("shutdown /s /t 5")

        elif data == b"restart":
            await event.answer("Restarting in 5 seconds...", alert=True)
            os.system("shutdown /r /t 5")

        elif data == b"hibernate":
            await event.answer("Hibernating...", alert=True)
            os.system("shutdown /h")

    except MessageNotModifiedError:
        pass
    except Exception as e:
        print("Callback error:", str(e))


async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("Bot started.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        import telethon, psutil, PIL, wmi
    except ImportError:
        print("Installing missing dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-r", str(Path(__file__).parent / "requirements.txt")
        ])
        print("Dependencies installed. Restart the script.")
        sys.exit(0)

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")