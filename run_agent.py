import asyncio
import os

from dotenv import load_dotenv
import uvicorn

from tg_bot.bot import build_application


async def start_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    application = build_application(token)

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("✅ Telegram bot started")


async def start_api():
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

    server = uvicorn.Server(config)
    await server.serve()


async def main():
    load_dotenv()

    await asyncio.gather(
        start_api(),
        start_telegram(),
    )


if __name__ == "__main__":
    asyncio.run(main())