import logging
import sys
import time
from datetime import datetime

import click
from telegram.ext import Updater

from zed2telegram.config import Config
from zed2telegram.util import send_message, prepare_code_message

LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
# LOGGER.addHandler(logging.FileHandler("/tmp/zed2telegram"))

CONFIG = Config()
UPDATER = Updater(token=CONFIG.TELEGRAM_BOT_TOKEN.value, use_context=True)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def try_send_message(message: str):
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

            tried_for = started_trying - datetime.now()
            if tried_for > CONFIG.RETRY_GIVE_UP_AFTER.value:
                LOGGER.warning(f"Giving up after trying for: {tried_for}")
                sys.exit(1)

            timeout_seconds = CONFIG.RETRY_TIMEOUT.value.total_seconds()
            LOGGER.error(f"Error sending message, retrying in {timeout_seconds} seconds...")
            time.sleep(timeout_seconds)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    """
    "notify" cli command
    """
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

    try_send_message(message_text)

    click.echo("Done.")


if __name__ == '__main__':
    cli()
