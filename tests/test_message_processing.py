from tests import TestBase
from zed2telegram.util import prepare_code_message


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
