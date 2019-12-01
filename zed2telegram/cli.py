import logging
import time

import click
from telegram.ext import Updater

from zed2telegram.config import Config

LOGGER = logging.getLogger(__name__)

CONFIG = Config()
UPDATER = Updater(token=CONFIG.TELEGRAM_BOT_TOKEN.value, use_context=True)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# Cli returns command line requests
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    pass


@cli.command(name="notify")
@click.argument("event_text", type=str, nargs=-1)
def c_notify(event_text: str):
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

    success = False
    while not success:
        try:
            send_message(UPDATER.bot, chat_id, message_text, parse_mode="markdown")
            success = True
        except Exception as ex:
            LOGGER.exception(ex)
            click.echo(ex, err=True)
            success = False
            click.echo("Error sending message, retrying in 10 seconds...", color="yellow")
            time.sleep(10)

    click.echo("Done.")
    # $(cat -)


def _prepare_message(lines: [str]) -> str:
    header = lines[0]

    result = "\n".join([
        f"*{header}*",
        f"```",
        *lines[:1],
        "```"
    ])

    return result


if __name__ == '__main__':
    cli()
