from telethon import events

async def safeEdit(event, newText, newButtons=None):
    try:
        msg = await event.get_message()
        currentText = msg.message
        currentButtons = msg.buttons

        textSame = currentText == newText
        buttonsSame = str(currentButtons) == str(newButtons)

        if textSame and buttonsSame:
            await event.answer()
            return False

        await event.edit(newText, buttons=newButtons)
        return True
    except:
        try:
            await event.edit(newText, buttons=newButtons)
            return True
        except:
            await event.answer()
            return False