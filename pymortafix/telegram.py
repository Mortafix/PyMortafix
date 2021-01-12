import sys
import traceback
from datetime import datetime

from colorifix.colorifix import Color, paint
from emoji import emojize
from telegram.utils.helpers import mention_markdown


def standard_message(update, top_message, bot_name, bot_url):
    user_mention = mention_markdown(
        update.effective_chat.id,
        update.effective_chat.username or update.effective_chat.first_name,
    )
    now = datetime.now()
    return emojize(
        f"{top_message}\n"
        f":robot_face: [{bot_name}]({bot_url})\n"
        f":calendar: {now:%d.%m.%Y}\n"
        f":eight_o’clock: {now:%H:%M}\n"
        f":bust_in_silhouette: {user_mention} (`{update.effective_chat.id}`)\n"
    )


def send_log(bot, channel, message, document=None):

    if document:
        bot.send_document(
            channel,
            document,
            caption=emojize(message),
            parse_mode="Markdown",
        )
    else:
        bot.send_message(channel, emojize(message), parse_mode="Markdown")


def error_handler(
    update,
    context,
    channel,
    message,
    logger=None,
    exception=None,
    extra_info=None,
    log=True,
):
    # error log on terminal
    user_data = (
        context.user_data.get(chat.id)
        if update and (chat := update.effective_chat)
        else "None"
    )
    trace = (exception and exception.__traceback__) or sys.exc_info()[2]
    traceback_error = "".join(traceback.format_tb(trace))
    traceback_msg = (
        f"\n{paint(user_data,229)}\n\n"
        f"{paint(traceback_error,Color.GRAY)}\n"
        f"> {paint(exception or context.error,Color.RED)}"
    )
    if logger:
        logger.warning(traceback_msg)
    else:
        print(traceback_msg)
    # send message to error channel
    if log:
        open("error.log", "w+").write(
            f"{user_data}\n\n"
            f"{extra_info or '...'}\n\n"
            f"{traceback_error}\n"
            f"> {exception or context.error}"
        )
        send_log(context.bot, channel, message, open("error.log", "r"))


def not_authorized_handler(update, context, bot_name, bot_url, channel):
    top_msg = ":face_with_symbols_on_mouth: *NO AUTH USER* :face_with_symbols_on_mouth:"
    message = standard_message(update, top_msg, bot_name, bot_url)
    send_log(context.bot, channel, message)
