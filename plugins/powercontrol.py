import os
from telethon import events, Button
from bot import client
from config import ownerId

@client.on(events.CallbackQuery(data=b"power"))
async def showPowerMenu(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return
    await event.edit("Power Control", buttons=[
        [Button.inline("Sleep", b"sleep")],
        [Button.inline("Shutdown", b"shutdown")],
        [Button.inline("Restart", b"restart")],
        [Button.inline("Hibernate", b"hibernate")],
        [Button.inline("Back", b"back")]
    ])

@client.on(events.CallbackQuery(data=b"sleep"))
async def doSleep(event):
    if event.sender_id != ownerId:
        return
    await event.answer("Entering sleep...", alert=True)
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

@client.on(events.CallbackQuery(data=b"shutdown"))
async def doShutdown(event):
    if event.sender_id != ownerId:
        return
    await event.answer("Shutting down in 5 seconds...", alert=True)
    os.system("shutdown /s /t 5")

@client.on(events.CallbackQuery(data=b"restart"))
async def doRestart(event):
    if event.sender_id != ownerId:
        return
    await event.answer("Restarting in 5 seconds...", alert=True)
    os.system("shutdown /r /t 5")

@client.on(events.CallbackQuery(data=b"hibernate"))
async def doHibernate(event):
    if event.sender_id != ownerId:
        return
    await event.answer("Hibernating...", alert=True)
    os.system("shutdown /h")