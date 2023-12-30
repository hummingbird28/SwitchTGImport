import logging, time, os

logging.basicConfig(level=logging.INFO)

import asyncio, subprocess, multiprocessing, sys
from functools import wraps, partial
from concurrent.futures import ThreadPoolExecutor
from swibots import (
    BotContext,
    BotCommand,
    CommandEvent,
    UploadProgress,
    InlineMarkup,
    InlineKeyboardButton,
)
from telegram.client import Telegram
from config import TELEGRAM_TOKEN, API_HASH, API_ID, DB_KEY, TASK_COUNT, WORKERS
from client import client
from functions import humanbytes, get_progress_bar

client.set_bot_commands(
    [
        BotCommand("start", "start messages", True),
        BotCommand("copy", "Copy messages", True),
    ]
)

logging.getLogger("httpx").setLevel(logging.INFO)

tg = Telegram(
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TELEGRAM_TOKEN,
    database_encryption_key=DB_KEY,
    default_workers_queue_size=WORKERS,
)
tg.login()


class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False


updateFileHandler = {}


def run_async(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5),
            partial(function, *args, **kwargs),
        )

    return wrapper


@run_async
def downloadFile(fileId):
    req = tg.call_method(
        "downloadFile",
        params={"file_id": fileId, "priority": 32, "offset": 0, "synchronous": True},
    )
    req.wait()
    return req.update


@run_async
def searchLink(chatUsername, message):
    req = tg.call_method(
        "getMessageLinkInfo", {"url": f"https://t.me/{chatUsername}/{message}"}
    )
    req.wait()
    return req.update


@run_async
def parseMarkdown(text):
    text['text'] = text['text'].replace("[", " ").replace("]", " ")
    call = tg.call_method("getMarkdownText", {"text": text})
    call.wait()
    return call.update["text"].replace("**", "*")


def searchChat():
    res = tg.call_method("searchPublicChat", {"username": "username"})
    res.wait()
    return res.update


@client.on_command("start")
async def StartM(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    await m.reply_text(
        "Hi, I am telegram forwarder bot\n\n`/copy username startId endId`"
    )


@client.on_command("copy")
async def copyMessages(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    param = ctx.event.params
    if not param:
        return await m.reply_text("Provide copy query!")
    try:
        split = param.split()
        chatUsername = split[0].split("/")[-1]
        msgStart = int(split[1])
        msgEnd = int(split[2]) + 1
    except IndexError:
        await m.reply_text("Invalid query!")
        return
    timer = Timer()

    msg = await m.send("Task Started!")
    for message in range(msgStart, msgEnd):
        try:
            update = await searchLink(chatUsername, message)
            if not update:
                continue
            buttons = []
            if update["message"].get("reply_markup"):
                dtd = update["message"]["reply_markup"]
                for row in dtd["rows"]:
                    rowbuttons = []
                    for button in row:
                        if (
                            button["@type"] == "inlineKeyboardButton"
                            and button["type"]["@type"] == "inlineKeyboardButtonTypeUrl"
                        ):
                            rowbuttons.append(
                                InlineKeyboardButton(
                                    button["text"], url=button["type"]["url"]
                                )
                            )
                    if rowbuttons:
                        buttons.append(rowbuttons)

            __msg = update["message"]["content"]
            if __msg["@type"] == "messageText":
                message = __msg["text"]
            else:
                message = __msg.get("caption", {})
            print(message)
            if message:
                try:
                    message = await parseMarkdown(message)
                except Exception as er:
                    print(er)
            #            print(__msg)
            path = None

            try:
                if __msg["@type"] == "messagePhoto":
                    fileId = __msg["photo"]["sizes"][-1]["photo"]["id"]
                elif __msg["@type"] == "messageDocument":
                    fileId = __msg["document"]["document"]["id"]
                elif __msg["@type"] == "messageAnimation":
                    fileId = __msg["animation"]["animation"]["id"]
                elif __msg["@type"] == "messageVideo":
                    fileId = __msg["video"]["video"]["id"]
                elif __msg["@type"] == "messageSticker":
                    fileId = __msg["sticker"]["sticker"]["id"]
                else:
                    print(__msg)
                    fileId = None
                assert fileId != None
                updateFileHandler[fileId] = msg.id
                file = await downloadFile(fileId)
                path = file["local"]["path"]
            except (KeyError, AssertionError) as er:
                print(er)
            except Exception as er:
                print(er)

            async def uploadCallback(upl: UploadProgress):
                if not timer.can_send():
                    return
                perc = round((upl.readed / upl.total) * 100, 2)

                name = os.path.basename(upl.path)
                message = f"""
    *Uploading* `{name}`!\n\n{get_progress_bar(perc)} [{humanbytes(upl.readed)}/{humanbytes(upl.total)}]"""
                await msg.edit_text(message)

            await m.reply_text(
                document=path,
                message=message or "",
                progress=uploadCallback,
                task_count=TASK_COUNT,
                part_size=10 * 10 * 1024,
                inline_markup=InlineMarkup(buttons) if buttons else None,
                quote=False
            )
            print(message)
            try:
                os.remove(path)
            except Exception as er:
                print(er)
        except Exception as er:
            print(er, message)
    await msg.delete()


timer = Timer()


def onFileUpdate(x):
    file = x["file"]["local"]
    if timer.can_send():
        subprocess.run(
            [
                sys.executable,
                "downloadedit.py",
                str(updateFileHandler[x["file"]["id"]]),
                str(file["downloaded_size"]),
                str(x["file"]["size"]),
            ]
        )


# async def main():
#     msg = await searchLink()
#     print(msg)
#     data = msg["message"]["content"]["caption"]
#     print(data['text'])
#     data['text'] = data['text'].replace("[", "\xad").replace("]", "\xad")

# #    exit()
#     call = tg.call_method(
#         "getMarkdownText", {"text": data}
#     )
#     call.wait()
#     print(call.update)


# asyncio.run(main())
tg.add_update_handler("updateFile", onFileUpdate)

client.run()
