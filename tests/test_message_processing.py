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

from cli2telegram.util import prepare_code_message
from tests import TestBase


class MessageProcessingTest(TestBase):

    def test_message_preparation(self):
        std_in = ['ZFS has finished a scrub:\n',
                  '\n',
                  '   eid: 3337\n',
                  ' class: scrub_finish\n',
                  '  host: \n',
                  '  time: 2019-12-01 19:36:01+0100\n',
                  '  pool: rpool\n',
                  ' state: ONLINE\n',
                  '  scan: scrub repaired 0B in 0 days 00:00:24 with 0 errors on Sun Dec  1 19:36:01 2019\n',
                  'config:\n',
                  '\n',
                  '\tNAME                                                     STATE     READ WRITE CKSUM\n',
                  '\trpool                                                    ONLINE       0     0     0\n',
                  '\t  mirror-0                                               ONLINE       0     0     0\n',
                  '\t    ata-Samsung_SSD_860_EVO_500GB_S4XBNF1M807031E-part2  ONLINE       0     0     0\n',
                  '\t    ata-Samsung_SSD_860_EVO_500GB_S4XBNF1M807033B-part2  ONLINE       0     0     0\n',
                  '\n',
                  'errors: No known data errors\n']

        output = prepare_code_message(std_in)
        assert output
