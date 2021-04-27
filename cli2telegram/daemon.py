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
import os
from time import time, sleep
from signal import signal, SIGINT, SIGTERM

import threading, queue

from telegram.ext import Updater

from cli2telegram.config import Config
from cli2telegram.util import _try_send_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Daemon:
    def __init__(self, config:Config):
        self.config = config
        self.running = True
        self.pipe_name = config.DAEMON_PIPE_PATH.value
        self.message_queue = queue.Queue()

    def run(self):
        try:
            os.mkfifo(self.pipe_name)
        except OSError as ose:
            logger.debug(ose)
            if os.path.exists(self.pipe_name):
                raise

        signal(SIGINT, self.signal_handler) # ctrl+c
        signal(SIGTERM, self.signal_handler) # systemctl stop

        threading.Thread(target=self.send_message_worker, daemon=True).start()

        logger.info("daemon listening on {}".format(self.pipe_name))

        while True:
            with open(self.pipe_name) as pipe:
                logger.debug("wating for input from pipe")
                pipe_buffer = ''
                while True:
                    data = pipe.read()
                    logger.debug(f"received {data}")
                    if len(data) == 0 and self.running:
                        logger.debug("No data from pipe. Sending buffer to telegram.")
                        formatted_buffer = "".join(["```\n", pipe_buffer, "```"])
                        self.message_queue.put(formatted_buffer)
                        pipe_buffer = ''
                        break
                    elif not self.running:
                        break
                    else:
                        pipe_buffer += data
            if not self.running:
                break

    def send_message_worker(self):
        while True:
            message = self.message_queue.get()
            logger.debug(f"Got {message} from queue. sending...")
            _try_send_message(message, self.config, logger, True)
            self.message_queue.task_done()

    def signal_handler(self, signal_received, frame):
        self.running = False

        logger.debug(f"Caught {signal_received}. Attempting to send all messages from queue.")

        try:
            os.unlink(self.pipe_name)
        except OSError as ose:
            if os.path.exists(self.pipe_name):
                logger.warning("Unable to clean up named pipe")
                logger.exception(ose)
        
        stop = time() + 5
        while self.message_queue.unfinished_tasks and time() < stop:
            sleep(1)

        sys.exit(0)
