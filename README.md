# cli2telegram
Small utility to send Telegram messages from the CLI.

This can f.ex. be used to
* quickly send arbitrary messages to a Telegram chat of your choice
* use it as a replacement for the "mail" program on linux
* use Telegram as a notification backend for the ZFS Event Daemon (zed)

## Features
* [x] Read messages from argument or STDIN
* [x] (Optional) Configuration file
* [x] Retry sending messages for a specified amount of time
* [x] Run as a daemon and echo messages into a linux pipe

## Examples

```shell
cli2telegram -h

# From arguments
cli2telegram "This is a message"

cli2telegram "Header" "This is a multiline message."

# From STDIN
echo My Message | cli2telegram

printf "Header\nThis is a multiline message." | cli2telegram

# Config via parameters
printf "Message" | cli2telegram -b "123456789:ABCDEFG" -c "123456789"

# as a Daemon
cli2telegram -d -p "/tmp/cli2telegram"
echo "hello world!" > /tmp/cli2telegram
``` 

# Install

To use this utility install it either using:
```
pip install cli2telegram
```

or - if you don't want to install it globally - using f.ex. [venv-install](https://github.com/markusressel/venv-install):
```
venv-install cli2telegram cli2telegram
```

or your custom `venv` manager of choice.

# Configuration

To be able to send you messages you have to provide a **bot token** and a **chat id**.
You can configure cli2telegram using cli parameters, a configuration file,
environment variables, or a combination of them.

## Parameters

| Name                | Type   | Description                               |
|---------------------|--------|-------------------------------------------|
| `-b`, `--bot-token` | String | Telegram Bot Token                        |
| `-c`, `--chat-id`   | String | Telegram Chat ID                          |
| `-d`, `--daemon`    | Flag   | Run as a daemon                           |
| `-p`, `--pipe`      | String | File path to the pipe used in daemon mode |

## File
cli2telegram uses [container-app-conf](https://github.com/markusressel/container-app-conf) so you can use YAML, TOML, or ENV to set those.

Have a look at the [cli2telegram.toml_example](cli2telegram.toml_example) file to get an idea.

# Daemon

When running cli2telegram as a daemon, the pipe will close for a brief amount of time between receiving input messages.
If you are sending multiple messages to the pipe using f.ex. a script, make sure to wait a bit (f.ex. 0.5 seconds)
between sending messages, otherwise:
* multiple messages may be received as one
* messages may get lost
* you may receive a `Broken pipe` error

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
# this must not be empty!
ZED_EMAIL_ADDR="root"

[...]

ZED_EMAIL_PROG="/usr/bin/cli2telegram"

[...]

# this must not be empty!
ZED_EMAIL_OPTS="#zfs #$(hostname)"

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
