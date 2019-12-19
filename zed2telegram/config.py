from container_app_conf import ConfigBase
from container_app_conf.entry.bool import BoolConfigEntry
from container_app_conf.entry.string import StringConfigEntry
from container_app_conf.entry.timedelta import TimeDeltaConfigEntry
from container_app_conf.source.env_source import EnvSource
from container_app_conf.source.toml_source import TomlSource
from container_app_conf.source.yaml_source import YamlSource

FILE_NAME = "zed2telegram"

KEY_ROOT = "zed2telegram"
KEY_TELEGRAM = "telegram"
KEY_RETRY = "retry"


class Config(ConfigBase):

    def __new__(cls, *args, **kwargs):
        data_sources = [
            EnvSource(),
            YamlSource(FILE_NAME),
            TomlSource(FILE_NAME)
        ]
        return super(Config, cls).__new__(cls, data_sources=data_sources)

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
