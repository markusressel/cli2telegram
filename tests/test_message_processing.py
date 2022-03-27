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
from cli2telegram.cli import prepare_messages
from cli2telegram.util import prepare_code_message, split_message
from tests import TestBase


class MessageProcessingTest(TestBase):

    def test_long_message_with_codeblock_doesnt_exceed_limit(self):
        std_in = "A" * 4096 + "B" * 4096
        messages = prepare_messages(std_in, True)

        assert len(messages) == 3
        for m in messages:
            assert len(m) <= 4096
        assert "B" not in messages[0]
        assert "A" in messages[1]
        assert "B" in messages[1]
        assert "A" not in messages[2]

    def test_long_message_doesnt_exceed_limit(self):
        std_in = "A" * 4096 + "B" * 4096
        messages = prepare_messages(std_in, False)

        assert len(messages) == 2
        for i, m in enumerate(messages):
            if i < len(messages) - 1:
                assert len(m) == 4096
            else:
                assert len(m) <= 4096
        assert "B" not in messages[0]
        assert "A" not in messages[1]

    def test_long_message_is_split(self):
        length = 32
        std_in = "A" * length + "B" * length
        messages = split_message(std_in, length)

        assert len(messages) == 2
        for i, m in enumerate(messages):
            if i < len(messages) - 1:
                assert len(m) == length
            else:
                assert len(m) <= length
        assert "B" not in messages[0]
        assert "A" not in messages[1]

    def test_prepare_code_message(self):
        message = "Code"
        output = prepare_code_message(message)

        assert output.startswith("```\n")
        assert output.endswith("\n```")
        assert message[0] in output

    def test_newlines_are_retained_in_code_block(self):
        std_in = "\nCo\nde\n"
        output = prepare_code_message(std_in)

        assert output == "```\n\nCo\nde\n\n```"

    def test_message_preparation(self):
        std_in = """ZFS has finished a scrub:\n
                  \n
                     eid: 3337\n
                   class: scrub_finish\n
                    host: \n
                    time: 2019-12-01 19:36:01+0100\n
                    pool: rpool\n
                   state: ONLINE\n
                    scan: scrub repaired 0B in 0 days 00:00:24 with 0 errors on Sun Dec  1 19:36:01 2019\n
                  config:\n
                  \n
                  \tNAME                                                     STATE     READ WRITE CKSUM\n
                  \trpool                                                    ONLINE       0     0     0\n
                  \t  mirror-0                                               ONLINE       0     0     0\n
                  \t    ata-Samsung_SSD_860_EVO_500GB_S4XBNF1M807031E-part2  ONLINE       0     0     0\n
                  \t    ata-Samsung_SSD_860_EVO_500GB_S4XBNF1M807033B-part2  ONLINE       0     0     0\n
                  \n
                  errors: No known data errors\n"""

        output = prepare_code_message(std_in)
        assert output
