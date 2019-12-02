# zed2telegram
Small utility to use Telegram as a notification backend 
for the ZFS Event Daemon.

# Install

To use this utility install it either using:
```
pip install zed2telegram
```

or - if you dont want to install it globally - using [venv-install](https://github.com/markusressel/venv-install):
```
venv-install zed2telegram zed2telegram
```

# Configuration

## zed2telegram
To be able to send you messages you have to provide a **bot token** and a **chat id**.
zed2telegram uses [container-app-conf](https://github.com/markusressel/container-app-conf) so you can use YAML, TOML, or ENV to set those. Since `zed` will run your scripts as root, if you want to use a config file you have to put it in f.ex. `/root/.config/zed2telegram.toml`:

```toml
[telegram]
chat_id="12345678"
bot_token="123456789:ABCDEFGH1234567890AB-1234567890ABC"
```

## ZED
To make `zed` call zed2telegram we will trick it and make it use zed2telegram as an E-Mail client.

Edit `/etc/zfs/zed.d/zed.rc` as root:
```bash
sudo nano -w /etc/zfs/zed.d/zed.rc
```

and
* uncomment `ZED_EMAIL_ADDR`, the value does not matter since we use our own email script, but **it is necessary to set a value to make ZED send 'emails'**
* set `ZED_EMAIL_PROG` to the path of the script, f.ex. `/usr/bin/zed2telegram`
  * it is important to note that zed does not seem to work if your command needs arguments to run
```

ZED_EMAIL_ADDR="root"

[...]

ZED_EMAIL_PROG="/usr/bin/zed2telegram"

[...]

# If you want to receive email no matter the state of your pool, you’ll want to set:
ZED_NOTIFY_VERBOSE=1

[...]
```

# Contributing

GitHub is for social coding: if you want to write code, I encourage contributions through pull requests from forks
of this repository. Create GitHub tickets for bugs and new features and comment on the ones that you are interested in.
