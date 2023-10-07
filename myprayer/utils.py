# Description: Utility functions
from myprayer.constants import TIMEDELTA
from myprayer.enums import OutType


def get_key(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key


def format_time_left(seconds, out_type: OutType | str) -> str:
    if isinstance(out_type, OutType):
        format = TIMEDELTA[out_type]
    else:
        format = out_type

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return format.format(hours=hours, minutes=minutes)
