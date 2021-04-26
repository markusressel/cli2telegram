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
from typing import Tuple

import click
from telegram.ext import Updater

from cli2telegram.config import Config
from cli2telegram.util import send_message, prepare_code_message
from cli2telegram.daemon import Daemon

LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
# LOGGER.addHandler(logging.FileHandler("/tmp/cli2telegram"))

CONFIG = Config(validate=False)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--bot-token', 'bot_token', default=None, type=str, help='Telegram Bot Token')
@click.option('-c', '--chat-id', 'chat_id', default=None, type=str, help='Telegram Chat ID')
@click.option('-d', '--daemon', 'daemon', default=False, type=bool, help='Daemon mode')
@click.option('-p', '--pipe', 'pipe', default=None, type=str, help='Daemon mode pipe')
@click.argument('lines', type=str, nargs=-1)
@click.version_option()
def cli(bot_token: str or None, chat_id: str or None, lines: Tuple[str], daemon: bool, pipe: str or None):
    """
    cli entry method
    """

    if bot_token is not None:
        CONFIG.TELEGRAM_BOT_TOKEN.value = bot_token
    if chat_id is not None:
        CONFIG.TELEGRAM_CHAT_ID.value = chat_id
    if pipe is not None:
        CONFIG.DAEMON_PIPE_PATH.value = pipe
    CONFIG.validate()

    if daemon:
        d = Daemon(CONFIG)
        d.run()
        return

    if len(lines) <= 0:
        # read message from stdin
        lines = []
        for line in sys.stdin:
            lines.append(line)

    LOGGER.debug(f"Message text: {lines}")
    if not lines or len(lines) < 1:
        LOGGER.debug("Message is empty, ignoring.")
        return

    LOGGER.debug("Processing message...")
    prepared_message = prepare_code_message(lines)

    if len(prepared_message) <= 0:
        LOGGER.warning("Message is empty, sending warning instead")
        prepared_message = f"Message is empty after processing, original message: {lines}"

    _try_send_message(prepared_message)


def _try_send_message(message: str):
    """
    Sends a message
    :param message: the message to send
    """
    started_trying = datetime.now()
    success = False
    updater = Updater(token=CONFIG.TELEGRAM_BOT_TOKEN.value, use_context=True)
    while not success:
        try:
            chat_id = CONFIG.TELEGRAM_CHAT_ID.value
            send_message(updater.bot, chat_id, message, parse_mode="markdown")
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
