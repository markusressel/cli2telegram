# cli2telegram
Small utility to send Telegram messages from the CLI.

This can be used to
* use Telegram as a notification backend for the ZFS Event Daemon (zed)

## Features
* [x] Read messages from argument or STDIN
* [x] (Optional) Configuration file
* [x] Retry sending messages for a specified amount of time

## Examples

```shell
# From arguments
cli2telegram "This is a message"

cli2telegram "Header" "This is a multiline message."

# From STDIN
echo My Message | cli2telegram

printf "Header\nThis is a multiline message." | cli2telegram

# Config via parameters
printf "Message" | cli2telegram -b "123456789:ABCDEFG" -c "123456789"
``` 

# Install

To use this utility install it either using:
```
pip install cli2telegram
```

or - if you don't want to install it globally - using [venv-install](https://github.com/markusressel/venv-install):
```
venv-install cli2telegram cli2telegram
```

or your custom venv manager of choice.

# Configuration

## File
To be able to send you messages you have to provide a **bot token** and a **chat id**.
cli2telegram uses [container-app-conf](https://github.com/markusressel/container-app-conf) so you can use YAML, TOML, or ENV to set those:

```toml
[cli2telegram.telegram]
chat_id="12345678"
bot_token="123456789:ABCDEFGH1234567890AB-1234567890ABC"

[cli2telegram.retry]
enabled="True"
timeout="10s"
give_up_after="4h"
```

## Parameters
If you do not want to create a configuration file you can pass them using parameters:

* `-b` - Telegram Bot Token
* `-c` - Telegram Chat ID

# Use Cases

## ZFS Event Daemon (ZED)
To make `zed` call cli2telegram we will trick it and make it use cli2telegram as an E-Mail client.

Edit `/etc/zfs/zed.d/zed.rc` as root:
```bash
sudo nano -w /etc/zfs/zed.d/zed.rc
```

and
* uncomment `ZED_EMAIL_ADDR`, the value does not matter since we use our own email script, but **it is necessary to set a value to make ZED send 'emails'**
* set `ZED_EMAIL_PROG` to the path of the script, f.ex. `/usr/bin/cli2telegram`
  * it is important to note that zed does not seem to work if your command needs arguments to run
```

ZED_EMAIL_ADDR="root"

[...]

ZED_EMAIL_PROG="/usr/bin/cli2telegram"

[...]

# If you want to receive email no matter the state of your pool, you’ll want to set:
ZED_NOTIFY_VERBOSE=1

[...]
```

Since `zed` will run your scripts as root, if you want to use a config file 
you have to put it in f.ex. `/root/.config/cli2telegram.toml`.

# Contributing

GitHub is for social coding: if you want to write code, I encourage contributions through pull requests from forks
of this repository. Create GitHub tickets for bugs and new features and comment on the ones that you are interested in.

# License

```text
cli2telegram by Markus Ressel
Copyright (C) 2018  Markus Ressel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
