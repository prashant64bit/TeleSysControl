import asyncio
import socket
from datetime import datetime
from bot import client
from config import ownerId, botToken
import psutil
import platform
import re
import wmi

def escapeMd(text):
    if not text:
        return ""
    text = str(text)
    chars = r'([_*[\]~`>#+|=])'
    return re.sub(chars, r'\\\1', text)

def getLaptopInfo():
    try:
        c = wmi.WMI()
        cs = c.Win32_ComputerSystem()[0]
        manufacturer = cs.Manufacturer.strip() or "Unknown"
        model = cs.Model.strip() or "Unknown"
        pcName = cs.Name.strip() or "Unknown"
        return manufacturer, model, pcName
    except:
        return "Unknown", "Unknown", "Unknown"

def hasInternet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        return False

def buildStartupMessage():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manufacturer, model, pcName = getLaptopInfo()
    lines = ["**Laptop Started**", ""]
    lines.append(f"**Manufacturer:** {escapeMd(manufacturer)}")
    lines.append(f"**Model:** {escapeMd(model)}")
    lines.append(f"**Computer Name:** {escapeMd(pcName)}")

    cpu = "Unknown"
    try:
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

    battery = psutil.sensors_battery()
    if battery:
        percent = round(battery.percent, 1)
        status = "Charging" if battery.power_plugged else "Discharging"
        lines.append(f"**Battery:** {percent}% ({escapeMd(status)})")

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

    lines.append("")
    lines.append(f"**Laptop started:** {now}")
    return "\n".join(lines)

async def checkAndNotify():
    for attempt in range(60):
        if hasInternet():
            try:
                msg = buildStartupMessage()
                await client.send_message(ownerId, msg, parse_mode='md')
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Startup notification sent")
                return
            except Exception as e:
                print(f"Notification send failed: {e}")
        await asyncio.sleep(10)

async def startupMonitor():
    await asyncio.sleep(15)
    asyncio.create_task(checkAndNotify())

asyncio.create_task(startupMonitor())