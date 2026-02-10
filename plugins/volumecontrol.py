import subprocess
from telethon import events, Button
from bot import client
from config import ownerId
from utils import safeEdit

def sendVolumeKeys(keyCode, count=1):
    try:
        script = f"""
        $shell = New-Object -ComObject WScript.Shell
        for ($i = 0; $i -lt {count}; $i++) {{
            $shell.SendKeys([char]{keyCode})
            Start-Sleep -Milliseconds 35
        }}
        """
        subprocess.run(
            ["powershell", "-Command", script],
            timeout=6,
            capture_output=True
        )
        return True
    except:
        return False

def getVolumeButtons():
    return [
        [Button.inline("−", b"volDown"), Button.inline("+", b"volUp")],
        [Button.inline("Min", b"volMin"), Button.inline("Max", b"volMax")],
        [Button.inline("Back", b"back")]
    ]

@client.on(events.CallbackQuery(data=b"volume"))
async def showVolumeMenu(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return
    await safeEdit(event, "Volume Control", getVolumeButtons())

@client.on(events.CallbackQuery(data=b"volUp"))
async def changeVolUp(event):
    if event.sender_id != ownerId:
        return
    sendVolumeKeys(175, count=4)
    await event.answer("Volume +", alert=False)

@client.on(events.CallbackQuery(data=b"volDown"))
async def changeVolDown(event):
    if event.sender_id != ownerId:
        return
    sendVolumeKeys(174, count=4)
    await event.answer("Volume −", alert=False)

@client.on(events.CallbackQuery(data=b"volMax"))
async def setMax(event):
    if event.sender_id != ownerId:
        return
    success = sendVolumeKeys(175, count=60)
    await event.answer("Volume → MAX" if success else "Failed", alert=True)

@client.on(events.CallbackQuery(data=b"volMin"))
async def setMin(event):
    if event.sender_id != ownerId:
        return
    sendVolumeKeys(173, count=1)
    sendVolumeKeys(174, count=60)
    await event.answer("Volume → MIN", alert=True)