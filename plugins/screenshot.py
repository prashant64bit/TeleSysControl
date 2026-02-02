import os
from datetime import datetime
from PIL import ImageGrab

async def handle_screenshot(event):
    await event.answer("Capturing...", alert=False)
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f"screenshot_{ts}.png"
        ImageGrab.grab().save(fn, "PNG")
        await event.client.send_file(event.chat_id, fn, caption="Screenshot", force_document=True)
        os.remove(fn)
    except Exception as e:
        await event.answer(f"Failed: {str(e)}", alert=True)