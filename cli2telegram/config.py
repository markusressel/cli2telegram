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
import re

from container_app_conf import ConfigBase
from container_app_conf.entry.bool import BoolConfigEntry
from container_app_conf.entry.int import IntConfigEntry
from container_app_conf.entry.string import StringConfigEntry
from container_app_conf.entry.timedelta import TimeDeltaConfigEntry
from container_app_conf.source.env_source import EnvSource
from container_app_conf.source.toml_source import TomlSource
from container_app_conf.source.yaml_source import YamlSource

FILE_NAME = "cli2telegram"

KEY_ROOT = "cli2telegram"
KEY_TELEGRAM = "telegram"
KEY_RETRY = "retry"

KEY_DAEMON = "daemon"


class Config(ConfigBase):

    def __new__(cls, *args, **kwargs):
        data_sources = [
            EnvSource(),
            YamlSource(FILE_NAME),
            TomlSource(FILE_NAME)
        ]
        kwargs["data_sources"] = data_sources
        return super(Config, cls).__new__(cls, *args, **kwargs)

    LOG_LEVEL = StringConfigEntry(
        description="Log level",
        key_path=[
            KEY_ROOT,
            "log_level"
        ],
        regex=re.compile(f"{'|'.join(logging._nameToLevel.keys())}", flags=re.IGNORECASE),
        default="INFO",
    )

    TELEGRAM_BOT_TOKEN = StringConfigEntry(
        key_path=[KEY_ROOT, KEY_TELEGRAM, "bot_token"],
        description="ID of the telegram chat to send messages to.",
        required=True,
        secret=True,
        example="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    )

    TELEGRAM_CHAT_ID = StringConfigEntry(
        key_path=[KEY_ROOT, KEY_TELEGRAM, "chat_id"],
        description="ID of the telegram chat to send messages to.",
        required=True,
        secret=True,
        example="-123456789"
    )

    RETRY_ENABLED = BoolConfigEntry(
        key_path=[KEY_ROOT, KEY_RETRY, "enabled"],
        description="Whether to retry sending messages or not.",
        default=True,
    )

    RETRY_TIMEOUT = TimeDeltaConfigEntry(
        key_path=[KEY_ROOT, KEY_RETRY, "timeout"],
        description="Timeout between tries.",
        default="10s",
    )

    RETRY_GIVE_UP_AFTER = TimeDeltaConfigEntry(
        key_path=[KEY_ROOT, KEY_RETRY, "give_up_after"],
        description="Time interval after which the retry should be cancelled.",
        default="1h",
    )

    DAEMON_PIPE_PATH = StringConfigEntry(
        key_path=[KEY_ROOT, KEY_DAEMON, "pipe_path"],
        description="Unix named pipe path.",
        default="/tmp/cli2telegram",
        example="/path/to/some/named/pipe"
    )

    DAEMON_PIPE_PERMISSIONS = IntConfigEntry(
        key_path=[KEY_ROOT, KEY_DAEMON, "pipe_permissions"],
        description="Unix file permissions for the named pipe.",
        default=0o666,
    )
