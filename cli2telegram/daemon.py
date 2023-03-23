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
import asyncio
import logging
import os
import sys
from signal import signal, SIGINT, SIGTERM
from time import time, sleep

import aiofiles
from telegram.ext import ApplicationBuilder

from cli2telegram import RetryLimitReachedException
from cli2telegram.config import Config
from cli2telegram.util import try_send_message, prepare_code_message

LOGGER = logging.getLogger(__name__)
HANDLER = logging.StreamHandler(sys.stdout)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)


class Daemon:
    def __init__(self, config: Config):
        self.config = config
        self.running = True
        self.pipe_file_path = config.DAEMON_PIPE_PATH.value
        self.message_queue = asyncio.Queue()
        self._app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN.value).build()

    def run(self):
        if os.path.exists(self.pipe_file_path):
            raise AssertionError(f"Pipe path '{self.pipe_file_path}' already exists!")
        try:
            os.mkfifo(self.pipe_file_path, mode=self.config.DAEMON_PIPE_PERMISSIONS.value)
        except OSError as ose:
            LOGGER.error(ose)
            raise ose

        signal(SIGINT, self.signal_handler)  # ctrl+c
        signal(SIGTERM, self.signal_handler)  # systemctl stop

        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(
            self.send_message_worker(),
            self.read_pipe_loop(),
        )
        loop.run_until_complete(tasks)
        loop.close()

    async def read_pipe_loop(self):
        LOGGER.info(f"Daemon is listening for input on {self.pipe_file_path}...")
        while True:
            LOGGER.debug("Waiting for new input on pipe")

            async with aiofiles.open(self.pipe_file_path, 'r') as pipe:
                pipe_buffer = ''
                while True:
                    data = await pipe.read()
                    LOGGER.debug(f"received: {data}")
                    if len(data) == 0 and self.running:
                        LOGGER.debug("No new data from pipe, adding current buffer to message queue")
                        await self.message_queue.put(pipe_buffer)
                        break
                    elif not self.running:
                        break
                    else:
                        pipe_buffer += data

            if not self.running:
                break

    async def send_message_worker(self):
        while True:
            LOGGER.debug("Waiting for item in message queue...")
            message = await self.message_queue.get()
            LOGGER.debug(f"Got new message: {message}")

            if not message.strip():
                LOGGER.warning("Message is empty, ignoring")
                self.message_queue.task_done()
                continue

            prepared_message = prepare_code_message(message)
            LOGGER.debug(f"Trying to send message from queue...")

            try:
                await try_send_message(
                    app=self._app,
                    chat_id=self.config.TELEGRAM_CHAT_ID.value,
                    message=prepared_message,
                    retry=self.config.RETRY_ENABLED.value,
                    retry_timeout=self.config.RETRY_TIMEOUT.value,
                    give_up_after=self.config.RETRY_GIVE_UP_AFTER.value)
                LOGGER.debug(f"Message sent successfully")
            except RetryLimitReachedException as ex:
                LOGGER.exception(ex)
                LOGGER.warning(f"Retry limit exceeded while trying to send message, it will be skipped: {message}")

            self.message_queue.task_done()

    def signal_handler(self, signal_received, frame):
        self.running = False

        LOGGER.debug(f"Caught {signal_received}. Attempting to send all messages from queue.")

        try:
            os.unlink(self.pipe_file_path)
        except OSError as ose:
            LOGGER.exception(ose)
            if os.path.exists(self.pipe_file_path):
                LOGGER.warning("Unable to clean up named pipe")

        stop = time() + 5

        while self.message_queue._unfinished_tasks and time() < stop:
            sleep(1)

        sys.exit(0)
