import logging
import time
from datetime import datetime

import click
from telegram.ext import Updater

from zed2telegram.config import Config

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.FileHandler("/tmp/zed2telegram"))

CONFIG = Config()
UPDATER = Updater(token=CONFIG.TELEGRAM_BOT_TOKEN.value, use_context=True)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def get_event_data(ctx, param, value):
    if not value and not click.get_text_stream('stdin').isatty():
        return click.get_text_stream('stdin').read().strip()
    else:
        return value


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option()
# @click.argument("event_text", type=str)
@click.option("--event-text", type=str, prompt=True)
def cli(event_text: str):
    """
    "notify" cli command
    """
    from zed2telegram.util import send_message

    if not event_text or len(event_text) < 1:
        LOGGER.debug("Received empty event data, ignoring.")
        return

    click.echo("Got event, sending...")
    chat_id = CONFIG.TELEGRAM_CHAT_ID.value

    message_text = _prepare_message(event_text)
    if len(message_text) <= 0:
        click.echo("Message is empty, sending warning instead")
        message_text = "Received empty message!"

    started_trying = datetime.now()
    success = False
    while not success:
        try:
            send_message(UPDATER.bot, chat_id, message_text, parse_mode="markdown")
            success = True
        except Exception as ex:
            LOGGER.exception(ex)
            click.echo(ex, err=True)

            if not CONFIG.RETRY_ENABLED.value:
                break

            tried_for = started_trying - datetime.now()
            if tried_for > CONFIG.RETRY_GIVE_UP_AFTER.value:
                click.echo(f"Giving up after trying for Tried for: {tried_for}")
                break

            click.echo("Error sending message, retrying in 10 seconds...", color="yellow")
            time.sleep(10)

    click.echo("Done.")
    # $(cat -)


def _prepare_message(text: str) -> str:
    if "\n" in text:
        lines = text.split("\n")
    else:
        lines = [text]

    header = lines[0]

    result = "\n".join([
        f"*{header}*",
        f"```",
        *lines[1:],
        "```"
    ])

    return result


if __name__ == '__main__':
    cli()
