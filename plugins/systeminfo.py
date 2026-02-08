import platform
import psutil
import re
from telethon import events, Button
from bot import client
from config import ownerId

def escapeMd(text):
    if not text:
        return ""
    text = str(text)
    chars = r'([_*[\]~`>#+|=])'
    return re.sub(chars, r'\\\1', text)

def getBatteryInfo():
    battery = psutil.sensors_battery()
    if battery is None:
        return None
    percent = round(battery.percent, 1)
    status = "Charging" if battery.power_plugged else "Discharging"
    timeLeft = "N/A"
    if battery.secsleft > 0 and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
        mins = battery.secsleft // 60
        hours = mins // 60
        minutes = mins % 60
        timeLeft = f"{hours}h {minutes:02d}m" if hours > 0 else f"{minutes}m"
    return {"percent": percent, "status": status, "timeLeft": timeLeft}

def buildSystemInfo():
    lines = ["**System Information**", ""]
    lines.append(f"**Hostname:** {escapeMd(platform.node())}")

    cpu = "Unknown"
    try:
        import wmi
        cpu = wmi.WMI().Win32_Processor()[0].Name.strip()
    except:
        cpu = platform.processor() or "Unknown"
    if cpu != "Unknown":
        lines.append(f"**CPU:** {escapeMd(cpu)}")

    mem = psutil.virtual_memory()
    if mem.total > 0:
        total = round(mem.total / (1024**3), 1)
        used = round(mem.used / (1024**3), 1)
        lines.append(f"**RAM:** {used}/{total} GB ({mem.percent}%)")

    battery = getBatteryInfo()
    if battery:
        lines.append(f"**Battery:** {battery['percent']}% ({escapeMd(battery['status'])})")
        if battery["timeLeft"] != "N/A" and "h" in battery["timeLeft"]:
            hours = int(battery["timeLeft"].split("h")[0])
            if hours < 24:
                lines.append(f"  **Remaining:** ~{escapeMd(battery['timeLeft'])}")

    drives = []
    for p in psutil.disk_partitions(all=True):
        if "cdrom" in p.opts:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
            if u.total < 1_000_000_000:
                continue
            totalGb = round(u.total / (1024**3), 1)
            usedGb = round(u.used / (1024**3), 1)
            percent = u.percent
            label = (p.device.rstrip('\\') or p.mountpoint).ljust(3)
            drives.append(f"  {label} {usedGb:>5.1f}/{totalGb:>5.1f} GB ({percent:>4.1f}%)")
        except:
            pass

    if drives:
        lines.append("**Storage:**")
        lines.extend(drives)

    gpus = []
    try:
        import wmi
        for v in wmi.WMI().Win32_VideoController():
            name = v.Name.strip()
            if name and "microsoft" not in name.lower() and "basic" not in name.lower():
                gpus.append(escapeMd(name))
    except:
        pass
    if gpus:
        lines.append("**GPU:**")
        for g in gpus:
            lines.append(f"  • {g}")

    procCount = len(list(psutil.process_iter(['pid'])))
    if procCount > 0:
        lines.append(f"**Processes:** {procCount}")

    return "\n".join(lines)

def getStatsButtons():
    return [
        [Button.inline("Refresh", b"stats")],
        [Button.inline("Back", b"back")]
    ]

@client.on(events.CallbackQuery(data=b"stats"))
async def showSystemInfo(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return
    try:
        text = buildSystemInfo()
        await event.edit(text, parse_mode='md', buttons=getStatsButtons())
    except Exception as e:
        if "MessageNotModifiedError" in str(e):
            await event.answer()
        else:
            print("System info error:", str(e))
            await event.answer("Error refreshing", alert=True)
