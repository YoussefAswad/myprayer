# Description: Utility functions
from myprayer.cli.constants import TIMEDELTA
from myprayer.cli.enums import NextOutType, OutType


def get_key(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key


def format_time_left(time_delta, out_type: OutType | str) -> str:
    seconds = time_delta.seconds
    if isinstance(out_type, OutType) or isinstance(out_type, NextOutType):
        format = TIMEDELTA[out_type]
    else:
        format = out_type

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return format.format(hours=hours, minutes=minutes)
