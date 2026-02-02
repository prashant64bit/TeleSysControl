import platform
import psutil

async def get_stats():
    lines = ["System Information", ""]

    lines.append(f"Hostname: {platform.node()}")

    cpu = "Unknown"
    try:
        import wmi
        cpu = wmi.WMI().Win32_Processor()[0].Name.strip()
    except:
        cpu = platform.processor() or "Unknown"

    if cpu != "Unknown":
        lines.append(f"CPU: {cpu}")

    mem = psutil.virtual_memory()
    if mem.total > 0:
        total = round(mem.total / (1024**3), 1)
        used = round(mem.used / (1024**3), 1)
        lines.append(f"RAM: {used}/{total} GB ({mem.percent}%)")

    drives = []
    for p in psutil.disk_partitions(all=True):
        if "cdrom" in p.opts:
            continue
        try:
            u = psutil.disk_usage(p.mountpoint)
            if u.total < 1000000000:
                continue
            total = round(u.total / (1024**3), 1)
            used = round(u.used / (1024**3), 1)
            percent = u.percent
            label = p.device.rstrip('\\') or p.mountpoint
            drives.append(f"  {label:<6} {used:>5.1f}/{total:>5.1f} GB  ({percent:>4.1f}%)")
        except:
            pass

    if drives:
        lines.append("Storage:")
        lines.extend(drives)

    gpus = []
    try:
        import wmi
        c = wmi.WMI()
        for v in c.Win32_VideoController():
            name = v.Name.strip()
            if name and "microsoft" not in name.lower() and "basic" not in name.lower():
                gpus.append(name)
    except:
        pass

    if gpus:
        lines.append("GPU:")
        for g in gpus:
            lines.append(f"  - {g}")

    proc_count = len(list(psutil.process_iter()))
    if proc_count > 0:
        lines.append(f"Processes: {proc_count}")

    return "\n".join(lines)