import platform
import psutil
import re
from telethon import events, Button

from bot import client
from config import ownerId

def escape_md(text):
    if not text:
        return ""
    text = str(text)
    chars = r'([_*[\]()~`>#+|=])'
    return re.sub(chars, r'\\\1', text)


def find_battery():
    battery = psutil.sensors_battery()
    if battery is None:
        return None

    percent = round(battery.percent, 1)
    status = "Charging" if battery.power_plugged else "Discharging"
    time_left = "N/A"

    if battery.secsleft > 0 and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
        mins = battery.secsleft // 60
        hours = mins // 60
        minutes = mins % 60
        time_left = f"{hours}h {minutes:02d}m" if hours > 0 else f"{minutes}m"

    return {
        "percent": percent,
        "status": status,
        "time_left": time_left
    }


def build_system_info():
    lines = ["**System Information**", ""]

    hostname = escape_md(platform.node())
    lines.append(f"**Hostname:** {hostname}")

    cpu = "Unknown"
    try:
        import wmi
        cpu = wmi.WMI().Win32_Processor()[0].Name.strip()
    except:
        cpu = platform.processor() or "Unknown"

    if cpu != "Unknown":
        lines.append(f"**CPU:** {escape_md(cpu)}")

    mem = psutil.virtual_memory()
    if mem.total > 0:
        total = round(mem.total / (1024**3), 1)
        used = round(mem.used / (1024**3), 1)
        lines.append(f"**RAM:** {used}/{total} GB ({mem.percent}%)")

    battery = find_battery()
    if battery:
        lines.append(f"**Battery:** {battery['percent']}% ({escape_md(battery['status'])})")
        if (battery['time_left'] != "N/A" and
            len(battery['time_left']) <= 10 and
            "h" in battery['time_left'] and
            int(battery['time_left'].split("h")[0]) < 24):
            lines.append(f"  **Remaining:** ~{escape_md(battery['time_left'])}")

    drives = []
    for p in psutil.disk_partitions(all=True):
        if "cdrom" in p.opts:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
            if u.total < 1000000000:
                continue
            total_gb = round(u.total / (1024**3), 1)
            used_gb = round(u.used / (1024**3), 1)
            percent = u.percent
            label = (p.device.rstrip('\\') or p.mountpoint).ljust(3)
            drives.append(f"  {label} {used_gb:>5.1f}/{total_gb:>5.1f} GB ({percent:>4.1f}%)")
        except:
            pass

    if drives:
        lines.append("**Storage:**")
        lines.extend(drives)

    gpus = []
    try:
        import wmi
        c = wmi.WMI()
        for v in c.Win32_VideoController():
            name = v.Name.strip()
            if name and "microsoft" not in name.lower() and "basic" not in name.lower():
                gpus.append(escape_md(name))
    except:
        pass

    if gpus:
        lines.append("**GPU:**")
        for g in gpus:
            lines.append(f"  • {g}")

    proc_count = len(list(psutil.process_iter(['pid'])))
    if proc_count > 0:
        lines.append(f"**Processes:** {proc_count}")

    return "\n".join(lines)


def get_stats_buttons():
    return [
        [Button.inline("Refresh", b"stats")],
        [Button.inline("Back", b"back")]
    ]


@client.on(events.CallbackQuery(data=b"stats"))
async def show_system_info(event):
    if event.sender_id != ownerId:
        await event.answer("Access denied", alert=True)
        return
    try:
        text = build_system_info()
        await event.edit(text, parse_mode='md', buttons=get_stats_buttons())
    except Exception as e:
        print("System info error:", str(e))


@client.on(events.CallbackQuery(data=b"back"))
async def go_back(event):
    if event.sender_id != ownerId:
        return
    await event.edit("Control Panel", buttons=[
        [Button.inline("System Status", b"stats")],
        [Button.inline("Power Control", b"power")],
        [Button.inline("Screenshot", b"screenshot")]
    ])