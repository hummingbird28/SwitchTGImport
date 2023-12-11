import sys, asyncio
from client import client
from functions import humanbytes, get_progress_bar

async def main(messageId, downloaded, total):
    downloaded = int(downloaded)
    total = int(total)
    perc = round((downloaded / total) * 100, 2)

    message = f"""🔽 *Downloading file!*\n\n{get_progress_bar(perc)} [{humanbytes(downloaded)}/{humanbytes(total)}]"""
    await client.edit_message(
        int(messageId),
        text=message
    )

asyncio.run(main(*sys.argv[1:]))