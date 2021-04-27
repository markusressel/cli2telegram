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
from typing import Tuple

import click

from cli2telegram.config import Config
from cli2telegram.util import prepare_code_message, _try_send_message
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

    _try_send_message(prepared_message, CONFIG, LOGGER, False)

if __name__ == '__main__':
    cli()
