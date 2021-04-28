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

from telegram import Bot, InlineKeyboardMarkup, Message
from cli2telegram.config import Config
from logging import Logger
from datetime import datetime

from telegram.ext import Updater

def send_message(bot: Bot, chat_id: str, message: str, parse_mode: str = None, reply_to: int = None,
                 menu: InlineKeyboardMarkup = None) -> Message:
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
    return bot.send_message(chat_id=chat_id, parse_mode=parse_mode, text=emojized_text, reply_to_message_id=reply_to,
                            reply_markup=menu)


def prepare_code_message(lines: [str]) -> str:
    """
    Prepares the given lines of text to send them as a code block message
    :param lines: text lines
    :return: prepared message
    """
    lines = list(map(lambda x: x + "\n" if not x.endswith("\n") else x, lines))

    result = "".join([
        f"```\n",
        *lines,
        "```"
    ])
    return result

def _try_send_message(message: str, config: Config, logger: Logger, daemon: bool):
    """
    Sends a message
    :param message: the message to send
    :param config: current configuration data
    :param daemon: whether or not cli2telegram is in daemon mode
    """
    started_trying = datetime.now()
    success = False
    updater = Updater(token=config.TELEGRAM_BOT_TOKEN.value, use_context=True)
    while not success:
        try:
            chat_id = config.TELEGRAM_CHAT_ID.value
            send_message(updater.bot, chat_id, message, parse_mode="markdown")
            success = True
        except Exception as ex:
            logger.exception(ex)

            if not config.RETRY_ENABLED.value:
                break

            tried_for = datetime.now() - started_trying
            if tried_for > config.RETRY_GIVE_UP_AFTER.value:
                logger.warning(f"Giving up after trying for: {tried_for}")
                if not daemon:
                    sys.exit(1)
                else:
                    break

            timeout_seconds = config.RETRY_TIMEOUT.value.total_seconds()
            logger.error(f"Error sending message, retrying in {timeout_seconds} seconds...")
            time.sleep(timeout_seconds)
