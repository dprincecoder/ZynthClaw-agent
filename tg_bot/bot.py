from __future__ import annotations

import asyncio
import re
from typing import Final

from telegram import Message, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.email_service import EmailServiceError, is_valid_email, send_funding_targets_email
from core.agent_controller import scan_topic, scan_repo, get_funding_targets
from tg_bot.formatters import format_scan_results, format_repo_analysis, format_funding_targets

PENDING_ACTION_KEY: Final[str] = "pending_action"
PENDING_EMAIL_RESULTS_KEY: Final[str] = "pending_email_results"
LAST_BOT_MESSAGE_ID_KEY: Final[str] = "last_bot_message_id"
PENDING_SCAN: Final[str] = "scan"
PENDING_REPO: Final[str] = "repo"
PENDING_EMAIL: Final[str] = "email_targets"


def _normalize_email(text: str) -> str:
    return re.sub(r"\s+", "", text).strip()


async def _delete_last_bot_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat:
        return

    message_id = context.chat_data.get(LAST_BOT_MESSAGE_ID_KEY)
    if not message_id:
        return

    try:
        await context.bot.delete_message(chat_id=chat.id, message_id=message_id)
    except BadRequest:
        pass
    finally:
        context.chat_data.pop(LAST_BOT_MESSAGE_ID_KEY, None)


async def _send_bot_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
) -> Message | None:
    if not update.message:
        return None

    await _delete_last_bot_message(update, context)
    sent_message = await update.message.reply_text(text)
    context.chat_data[LAST_BOT_MESSAGE_ID_KEY] = sent_message.message_id
    return sent_message


def _set_pending_action(context: ContextTypes.DEFAULT_TYPE, action: str | None) -> None:
    if action is None:
        context.chat_data.pop(PENDING_ACTION_KEY, None)
        context.chat_data.pop(PENDING_EMAIL_RESULTS_KEY, None)
        return
    context.chat_data[PENDING_ACTION_KEY] = action


async def _get_latest_funding_targets() -> dict:
    return await asyncio.to_thread(get_funding_targets)


async def _run_scan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    topic: str,
) -> None:
    await _send_bot_message(update, context, "Scanning ecosystem, this may take a while...")

    try:
        results = await asyncio.to_thread(scan_topic, topic)
        text = format_scan_results(results)
        await _send_bot_message(update, context, text)
    except Exception as exc:
        await _send_bot_message(update, context, f"Error while scanning topic: {exc}")


async def _run_repo_analysis(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    repo_url: str,
) -> None:
    await _send_bot_message(update, context, "Analyzing repository...")

    try:
        results = await asyncio.to_thread(scan_repo, repo_url)
        text = format_repo_analysis(results)
        await _send_bot_message(update, context, text)
    except Exception as exc:
        await _send_bot_message(update, context, f"Error while analyzing repository: {exc}")


async def _run_email_delivery(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    recipient_email: str,
    results: dict,
) -> None:
    await _send_bot_message(update, context, "Preparing the PDF and sending the email...")

    try:
        sent_count = await asyncio.to_thread(send_funding_targets_email, recipient_email, results)
        await _send_bot_message(
            update,
            context,
            f"Email sent to {recipient_email} with {sent_count} funding candidates attached as a PDF. Also check your spam folder.",
        )
    except EmailServiceError as exc:
        await _send_bot_message(update, context, str(exc))
    except Exception as exc:
        await _send_bot_message(update, context, f"Error while sending email: {exc}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Hello. my name is Zyntux. more like ZynthClaw \n\n"
        "I am your go to guy for detecting critical open-source infrastructure that may require funding or community support.\n\n"
        "Think of me as a funding radar for open-source infrastructure.\n\n"
        "If you want, i can even email you the top candidates that require funding or community support.\n\n"
        "Commands:\n\n"
        "/scan <topic>\n"
        "/repo <github_url>\n"
        "/funding_targets\n"
        "/request_email_report <email>\n"

    )
    _set_pending_action(context, None)
    if update.message:
        await _send_bot_message(update, context, message)


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        _set_pending_action(context, PENDING_SCAN)
        await _send_bot_message(update, context, "Now send me a topic to crawl.")
        return

    _set_pending_action(context, None)
    topic = " ".join(context.args).strip()
    await _run_scan(update, context, topic)


async def repo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not context.args:
        _set_pending_action(context, PENDING_REPO)
        await _send_bot_message(update, context, "Now send me the repo URL to evaluate.")
        return

    _set_pending_action(context, None)
    repo_url = " ".join(context.args).strip()
    await _run_repo_analysis(update, context, repo_url)


async def funding_targets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    _set_pending_action(context, None)
    await _send_bot_message(update, context, "Fetching funding targets...")

    try:
        results = await asyncio.to_thread(get_funding_targets)
        text = format_funding_targets(results)
        await _send_bot_message(update, context, text)

    except Exception as exc:
        await _send_bot_message(update, context, f"Error while fetching funding targets: {exc}")


async def email_targets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    _set_pending_action(context, None)

    try:
        results = await _get_latest_funding_targets()
    except Exception as exc:
        await _send_bot_message(update, context, f"Error while loading funding targets: {exc}")
        return

    if not (results.get("funding_candidates") or []):
        await _send_bot_message(
            update,
            context,
            "No funding targets are available yet. Run /scan, /repo, or /funding_targets first.",
        )
        return

    if not context.args:
        context.chat_data[PENDING_EMAIL_RESULTS_KEY] = results
        _set_pending_action(context, PENDING_EMAIL)
        await _send_bot_message(update, context, "Now send me the email address to receive the PDF report.")
        return

    recipient_email = _normalize_email(" ".join(context.args))
    if not is_valid_email(recipient_email):
        context.chat_data[PENDING_EMAIL_RESULTS_KEY] = results
        _set_pending_action(context, PENDING_EMAIL)
        await _send_bot_message(update, context, "Please send a valid email address.")
        return

    await _run_email_delivery(update, context, recipient_email, results)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    pending_action = context.chat_data.get(PENDING_ACTION_KEY)
    if pending_action == PENDING_SCAN:
        _set_pending_action(context, None)
        topic = update.message.text.strip()
        if not topic:
            await _send_bot_message(update, context, "Please send a non-empty topic.")
            _set_pending_action(context, PENDING_SCAN)
            return
        await _run_scan(update, context, topic)
        return

    if pending_action == PENDING_REPO:
        _set_pending_action(context, None)
        repo_url = update.message.text.strip()
        if not repo_url:
            await _send_bot_message(update, context, "Please send a valid repository URL.")
            _set_pending_action(context, PENDING_REPO)
            return
        await _run_repo_analysis(update, context, repo_url)
        return

    if pending_action == PENDING_EMAIL:
        results = context.chat_data.get(PENDING_EMAIL_RESULTS_KEY)
        recipient_email = _normalize_email(update.message.text)
        if not is_valid_email(recipient_email):
            await _send_bot_message(update, context, "Please send a valid email address.")
            context.chat_data[PENDING_EMAIL_RESULTS_KEY] = results
            context.chat_data[PENDING_ACTION_KEY] = PENDING_EMAIL
            return

        _set_pending_action(context, None)
        await _run_email_delivery(update, context, recipient_email, results or {})
        return


def build_application(token: str) -> Application:
    """
    Build and return the python-telegram-bot Application with all handlers
    registered. This is used by the main entrypoint to start polling.
    """
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("repo", repo_command))
    application.add_handler(CommandHandler("funding_targets", funding_targets_command))
    application.add_handler(CommandHandler("request_email_report", email_targets_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    # application.add_handler(CommandHandler("h", help_command))

    return application

