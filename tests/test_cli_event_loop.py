import subprocess
import sys
import unittest
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner


class TestCliEventLoop(unittest.TestCase):

    def test_import_without_event_loop(self):
        # Python 3.14 no longer creates an event loop implicitly, so the
        # module must not need one at import time. A fresh interpreter makes
        # sure no loop was created by another test.
        result = subprocess.run([sys.executable, "-c", "import cli2telegram.cli"], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_send_message_from_stdin(self):
        from cli2telegram import cli

        with patch.object(cli, "_send_messages", new=AsyncMock()) as send_messages, \
                patch.object(cli, "Application"):
            result = CliRunner().invoke(cli.cli, ["-b", "1:token", "-c", "1"], input="hello\n")

        self.assertEqual(0, result.exit_code, result.output)
        send_messages.assert_awaited_once()
        self.assertEqual(["hello\n"], send_messages.await_args.args[1])


if __name__ == "__main__":
    unittest.main()
