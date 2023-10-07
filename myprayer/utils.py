# Description: Utility functions
import sys
from io import StringIO

from myprayer.constants import TIMEDELTA
from myprayer.enums import OutType


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def get_key(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key


def format_time_left(seconds, out_type: OutType | str) -> str:
    if isinstance(out_type, str):
        format = out_type
    else:
        format = TIMEDELTA[out_type]

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return format.format(hours=hours, minutes=minutes)
