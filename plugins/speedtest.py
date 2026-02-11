import speedtest
from telethon import events, Button
from bot import client
from config import ownerId
from utils import safeEdit

def formatSpeed(bps):
    if bps < 1024 * 1024:
        return f"{bps / 1024:.2f} Kb/s"
    if bps < 1024 * 1024 * 1024:
        return f"{bps / (1024 * 1024):.2f} Mb/s"
    return f"{bps / (1024 * 1024 * 1024):.2f} Gb/s"

def getSpeedTestButtons():
    return [
        [Button.inline("Run Again", b"speedtest")],
        [Button.inline("Back", b"back")]
    ]

@client.on(events.CallbackQuery(data=b"speedtest"))
async def runSpeedTest(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return

    message = "Running speed test...\nThis may take 20-40 seconds."
    await safeEdit(event, message, getSpeedTestButtons())

    try:
        st = speedtest.Speedtest()
        st.get_best_server()

        downloadBps = st.download()
        uploadBps = st.upload()

        downloadStr = formatSpeed(downloadBps)
        uploadStr = formatSpeed(uploadBps)
        ping = st.results.ping

        resultText = (
            "**Speed Test Result**\n\n"
            f"**Download:** {downloadStr}\n"
            f"**Upload:**   {uploadStr}\n"
            f"**Ping:**     {ping:.1f} ms\n\n"
            f"Server: {st.results.server['sponsor']} ({st.results.server['name']})"
        )
    except Exception as e:
        resultText = f"**Speed Test Failed**\n\n{str(e)}"

    await safeEdit(event, resultText, getSpeedTestButtons())