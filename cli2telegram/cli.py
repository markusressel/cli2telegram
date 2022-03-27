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
from typing import Tuple, List

import click

from cli2telegram.config import Config
from cli2telegram.const import CODEBLOCK_MARKER_END, CODEBLOCK_MARKER_START, TELEGRAM_MESSAGE_LENGTH_LIMIT
from cli2telegram.daemon import Daemon
from cli2telegram.util import split_message, prepare_code_message, _try_send_message

LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
# LOGGER.addHandler(logging.FileHandler("/tmp/cli2telegram"))

CONFIG = Config(validate=False)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-b', '--bot-token', 'bot_token', default=None, type=str, help='Telegram Bot Token')
@click.option('-c', '--chat-id', 'chat_id', default=None, type=str, help='Telegram Chat ID')
@click.option('-C', '--code-block', 'code_block', is_flag=True, default=False, help='Send message in a code block')
@click.option('-d', '--daemon', 'daemon', is_flag=True, help='Daemon mode')
@click.option('-p', '--pipe', 'pipe', default=None, type=str, help='File path to the pipe used in daemon mode')
@click.argument('lines', type=str, nargs=-1)
@click.version_option()
def cli(bot_token: str or None, chat_id: str or None, code_block: bool, lines: Tuple[str], daemon: bool,
        pipe: str or None):
    """
    cli entry method
    """

    # set log level globally
    log_level = logging._nameToLevel.get(str(CONFIG.LOG_LEVEL.value).upper(), CONFIG.LOG_LEVEL.default)
    LOGGER.setLevel(log_level)
    logging.getLogger("cli2telegram").setLevel(log_level)

    if bot_token is not None:
        CONFIG.TELEGRAM_BOT_TOKEN.value = bot_token
    if chat_id is not None:
        CONFIG.TELEGRAM_CHAT_ID.value = chat_id
    if pipe is not None:
        CONFIG.DAEMON_PIPE_PATH.value = pipe
    CONFIG.validate()

    # ------------------
    # daemon

    if daemon:
        d = Daemon(CONFIG)
        d.run()
        return

    # ------------------
    # one-shot operation

    if len(lines) <= 0:
        # read message from stdin
        lines = []
        for line in sys.stdin:
            lines.append(line)

    LOGGER.debug(f"Message text: {lines}")
    if not lines or len(lines) < 1:
        LOGGER.warning("Message is empty, ignoring.")
        return

    text = "".join(lines)
    messages = prepare_messages(text, code_block)

    for message in messages:
        _try_send_message(
            bot_token=CONFIG.TELEGRAM_BOT_TOKEN.value,
            chat_id=CONFIG.TELEGRAM_CHAT_ID.value,
            message=message,
            retry=CONFIG.RETRY_ENABLED.value,
            retry_timeout=CONFIG.RETRY_TIMEOUT.value,
            give_up_after=CONFIG.RETRY_GIVE_UP_AFTER.value
        )


def prepare_messages(text: str, code_block: bool) -> List[str]:
    result = []

    LOGGER.debug("Processing message...")

    length = TELEGRAM_MESSAGE_LENGTH_LIMIT
    if code_block:
        length -= (len(CODEBLOCK_MARKER_START) + len(CODEBLOCK_MARKER_END))
    messages = split_message(text, length)
    for message in messages:
        if code_block:
            message = prepare_code_message(message)
        result.append(message)

    return result


if __name__ == '__main__':
    cli()
