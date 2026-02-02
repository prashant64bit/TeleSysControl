import os

async def handle_power_command(event, data):
    cmd = {
        b"sleep":     ("Entering sleep...",     "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"),
        b"shutdown":  ("Shutting down in 5s...", "shutdown /s /t 5"),
        b"restart":   ("Restarting in 5s...",    "shutdown /r /t 5"),
        b"hibernate": ("Hibernating...",         "shutdown /h")
    }.get(data)

    if cmd:
        await event.answer(cmd[0], alert=True)
        os.system(cmd[1])