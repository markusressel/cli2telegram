#   cli2telegram
#  Copyright (c) 2019.  Markus Ressel
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import logging
import time
from datetime import datetime, timedelta

from telegram import Bot, InlineKeyboardMarkup, Message
from telegram.ext import Updater

from cli2telegram import RetryLimitReachedException
from cli2telegram.const import CODEBLOCK_MARKER_START, CODEBLOCK_MARKER_END

LOGGER = logging.getLogger(__name__)


def send_message(
        bot: Bot, chat_id: str, message: str, parse_mode: str = None, reply_to: int = None,
        menu: InlineKeyboardMarkup = None
) -> Message:
    """
    Sends a text message to the given chat
    :param bot: the bot
    :param chat_id: the chat id to send the message to
    :param message: the message to chat (may contain emoji aliases)
    :param parse_mode: specify whether to parse the text as markdown or HTML
    :param reply_to: the message id to reply to
    :param menu: inline keyboard menu markup
    """
    from emoji import emojize
    emojized_text = emojize(message, use_aliases=True)
    return bot.send_message(
        chat_id=chat_id, parse_mode=parse_mode, text=emojized_text, reply_to_message_id=reply_to, reply_markup=menu,
        timeout=10
    )


def split_message(message: str, length: int) -> [str]:
    """
    Split lines into multiple messages if the maximum number of character is exceeded.
    :param message: original message
    :param length: max length of a single chunk
    :return: list of messages
    """
    return [message[i:i + length] for i in range(0, len(message), length)]


def prepare_code_message(message: str) -> str:
    """
    Wraps the given message inside of a code block.
    If the message already is contained within a code block, nothing is changed.
    :param message: message
    :return: prepared message
    """
    result = message
    if not result.startswith(CODEBLOCK_MARKER_START):
        result = CODEBLOCK_MARKER_START + result
    if not result.endswith(CODEBLOCK_MARKER_END):
        result = result + CODEBLOCK_MARKER_END

    return result


def _try_send_message(
        bot_token: str,
        chat_id: str, message: str,
        retry: bool, retry_timeout: timedelta, give_up_after: timedelta
):
    """
    Sends a message
    :param bot_token: telegram bot token
    :param chat_id: chat id
    :param message: the message to send
    :param retry: whether to retry if something fails
    :param retry_timeout: time to wait between retries
    :param give_up_after: when to give up trying
    """
    started_trying = datetime.now()
    success = False
    while not success:
        try:
            updater = Updater(token=bot_token, use_context=True)
            send_message(bot=updater.bot, chat_id=chat_id, message=message, parse_mode="markdown")
            success = True
        except Exception as ex:
            LOGGER.exception(ex)

            if not retry:
                break

            tried_for = datetime.now() - started_trying
            if tried_for > give_up_after:
                LOGGER.warning(f"Giving up after trying for: {tried_for}")
                raise RetryLimitReachedException(started_trying, tried_for)

            timeout_seconds = retry_timeout.total_seconds()
            LOGGER.error(f"Error sending message, retrying in {timeout_seconds} seconds...")
            time.sleep(timeout_seconds)
