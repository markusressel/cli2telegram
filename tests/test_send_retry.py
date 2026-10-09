import asyncio
import unittest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from telegram.error import BadRequest, InvalidToken, NetworkError

from cli2telegram import RetryLimitReachedException
from cli2telegram.util import try_send_message


def send(retry=True, give_up_after=timedelta(hours=1)):
    return asyncio.run(try_send_message(
        app=MagicMock(), chat_id="1", message="a_b", retry=retry,
        retry_timeout=timedelta(seconds=1), give_up_after=give_up_after
    ))


class TestTrySendMessage(unittest.TestCase):

    def test_invalid_markdown_is_sent_as_plain_text(self):
        parse_error = BadRequest("Can't parse entities: can't find end of the entity starting at byte offset 1180")
        with patch("cli2telegram.util.send_message", new=AsyncMock(side_effect=[parse_error, None])) as send_message, \
                patch("cli2telegram.util.time.sleep") as sleep:
            send()

        self.assertEqual(["markdown", None], [call.kwargs["parse_mode"] for call in send_message.await_args_list])
        sleep.assert_not_called()

    def test_other_bad_requests_are_not_retried(self):
        with patch("cli2telegram.util.send_message", new=AsyncMock(side_effect=BadRequest("Chat not found"))) as send_message, \
                patch("cli2telegram.util.time.sleep") as sleep:
            with self.assertRaises(BadRequest):
                send()

        self.assertEqual(1, send_message.await_count)
        sleep.assert_not_called()

    def test_invalid_token_is_not_retried(self):
        with patch("cli2telegram.util.send_message", new=AsyncMock(side_effect=InvalidToken("Unauthorized"))) as send_message, \
                patch("cli2telegram.util.time.sleep") as sleep:
            with self.assertRaises(InvalidToken):
                send()

        self.assertEqual(1, send_message.await_count)
        sleep.assert_not_called()

    def test_network_errors_are_retried(self):
        with patch("cli2telegram.util.send_message", new=AsyncMock(side_effect=[NetworkError("down"), None])) as send_message, \
                patch("cli2telegram.util.time.sleep") as sleep:
            send()

        self.assertEqual(2, send_message.await_count)
        sleep.assert_called_once_with(1.0)

    def test_gives_up_after_the_retry_limit(self):
        with patch("cli2telegram.util.send_message", new=AsyncMock(side_effect=NetworkError("down"))), \
                patch("cli2telegram.util.time.sleep"):
            with self.assertRaises(RetryLimitReachedException):
                send(give_up_after=timedelta(seconds=-1))


if __name__ == "__main__":
    unittest.main()
