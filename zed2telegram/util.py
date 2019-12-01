from telegram import Bot, InlineKeyboardMarkup, Message


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
    if "\n" in lines[0]:
        lines = lines[0].split("\n") + lines[1:]
    else:
        lines = [lines]

    result = "".join([
        f"```\n",
        *lines,
        "```"
    ])

    return result
