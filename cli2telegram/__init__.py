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
import datetime
from datetime import timedelta


class RetryLimitReachedException(Exception):
    """
    Helper exception to handle giving up retries
    """

    def __init__(self, started_trying: datetime, tried_for: timedelta):
        self.message = f"All retries failed after {tried_for}. Started trying at {started_trying}."
        super().__init__(self.message)
