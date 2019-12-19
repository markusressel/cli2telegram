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
import sys
import time
from datetime import datetime

import click
from telegram.ext import Updater

from cli2telegram.config import Config
from cli2telegram.util import send_message, prepare_code_message

LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
# LOGGER.addHandler(logging.FileHandler("/tmp/cli2telegram"))

CONFIG = Config()
UPDATER = Updater(token=CONFIG.TELEGRAM_BOT_TOKEN.value, use_context=True)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-bt', '--bot-token', 'bot_token', default=None, type=str, help='Telegram Bot Token')
@click.option('-c', '--chat-id', 'chat_id', default=None, type=str, help='Telegram Chat ID')
@click.version_option()
def cli(bot_token: str or None, chat_id: str or None):
    """
    cli entry method
    """
    if bot_token is not None:
        CONFIG.TELEGRAM_BOT_TOKEN.value = bot_token
    if chat_id is not None:
        CONFIG.TELEGRAM_CHAT_ID.value = chat_id

    event_text = []
    # read event body from stdin
    for line in sys.stdin:
        event_text.append(line)

    LOGGER.debug(f"Event text: {event_text}")

    if not event_text or len(event_text) < 1:
        LOGGER.debug("Received empty event data, ignoring.")
        return

    LOGGER.debug("Processing stdin...")
    message_text = prepare_code_message(event_text)

    if len(message_text) <= 0:
        LOGGER.warning("Message is empty, sending warning instead")
        message_text = "Received empty message!"

    _try_send_message(message_text)

    click.echo("Done.")


def _try_send_message(message: str):
    """
    Sends a message
    :param message: the message to send
    """
    started_trying = datetime.now()
    success = False
    while not success:
        try:
            chat_id = CONFIG.TELEGRAM_CHAT_ID.value
            send_message(UPDATER.bot, chat_id, message, parse_mode="markdown")
            success = True
        except Exception as ex:
            LOGGER.exception(ex)

            if not CONFIG.RETRY_ENABLED.value:
                break

            tried_for = datetime.now() - started_trying
            if tried_for > CONFIG.RETRY_GIVE_UP_AFTER.value:
                LOGGER.warning(f"Giving up after trying for: {tried_for}")
                sys.exit(1)

            timeout_seconds = CONFIG.RETRY_TIMEOUT.value.total_seconds()
            LOGGER.error(f"Error sending message, retrying in {timeout_seconds} seconds...")
            time.sleep(timeout_seconds)


if __name__ == '__main__':
    cli()
