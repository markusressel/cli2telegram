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
import time
import sys
import os
from signal import signal, SIGINT, SIGTERM
from datetime import datetime

import threading, queue

from telegram.ext import Updater

from cli2telegram.config import Config
from cli2telegram.util import send_message, prepare_code_message

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

class Daemon:
    def __init__(self, CONFIG:Config):
        self.CONFIG = CONFIG
        self.RUNNING = True
        self.PIPE_NAME = CONFIG.DAEMON_PIPE_PATH.value
        self.message_queue = queue.Queue()

    def run(self):
        try:
            os.mkfifo(self.PIPE_NAME)
        except OSError as ose:
            LOGGER.debug(ose)
            if os.path.exists(self.PIPE_NAME):
                raise
     
        signal(SIGINT, self.signal_handler) # ctrl+c
        signal(SIGTERM, self.signal_handler) # systemctl stop

        threading.Thread(target=self.send_message_worker, daemon=True).start()

        LOGGER.info("daemon listening on {}".format(self.PIPE_NAME))

        while True:
            with open(self.PIPE_NAME) as pipe:
                LOGGER.debug("wating for input from pipe")
                pipe_buffer = ''
                while True:
                    data = pipe.read()
                    LOGGER.debug(f"received {data}")
                    if len(data) == 0 and self.RUNNING:
                        LOGGER.debug("No data from pipe. Sending buffer to telegram.");
                        self.message_queue.put(pipe_buffer)
                        pipe_buffer = ''
                        break
                    elif not self.RUNNING:
                        break
                    else:
                        pipe_buffer += data
            if not self.RUNNING:
                break

    def send_message_worker(self):
        while True:
            message = self.message_queue.get()
            LOGGER.debug(f"Got {message} from queue. sending...")
            self._try_send_message(message)
            self.message_queue.task_done()

    def _try_send_message(self, message: str):
        """
        Sends a message
        :param message: the message to send
        """
        started_trying = datetime.now()
        success = False
        updater = Updater(token=self.CONFIG.TELEGRAM_BOT_TOKEN.value, use_context=True)
        while not success:
            try:
                chat_id = self.CONFIG.TELEGRAM_CHAT_ID.value
                send_message(updater.bot, chat_id, message, parse_mode="markdown")
                success = True
            except Exception as ex:
                LOGGER.exception(ex)

                if not self.CONFIG.RETRY_ENABLED.value:
                    break

                tried_for = datetime.now() - started_trying
                if tried_for > self.CONFIG.RETRY_GIVE_UP_AFTER.value:
                    LOGGER.warning(f"Giving up after trying for: {tried_for}. Placing message back in queue.")
                    self.message_queue.put(message)
                    break

                timeout_seconds = self.CONFIG.RETRY_TIMEOUT.value.total_seconds()
                LOGGER.error(f"Error sending message, retrying in {timeout_seconds} seconds...")
                time.sleep(timeout_seconds)

    def signal_handler(self, signal_received, frame):
        self.RUNNING = False
        
        LOGGER.debug(f"Caught {signal_received}. Attempting to send all messages from queue.")
        
        try:
            os.unlink(self.PIPE_NAME)
        except OSError as ose:
            if os.path.exists(self.PIPE_NAME):
                LOGGER.warning("Unable to clean up named pipe")
                raise
        
        self.message_queue.join()

        sys.exit(0)
       
