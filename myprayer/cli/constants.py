# Description: This file contains all the constants used in the project

import os
from pathlib import Path
from typing import Dict, Final, List

from myprayer.cli.enums import NextOutType, OutType, TimeFormat

APP_NAME: Final[str] = "myprayer"
# Prayer times API URL

LOCATION_TYPES: Final[List[str]] = ["City", "Coordinates", "Address"]

# Find config/cache dir based on OS
if str(os.name) == "nt":
    cache_dir = (
        Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / APP_NAME
    )
    config_dir = (
        Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming") / APP_NAME
    )
else:
    cache_dir = (
        Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / APP_NAME
    )
    config_dir = (
        Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / APP_NAME
    )

# cache dir path
CACHE_DIR: Final[Path] = cache_dir

# Create cache dir if it doesn't exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# config dir path
CONFIG_DIR: Final[Path] = config_dir

# config file path
CONFIG_FILE: Final[Path] = CONFIG_DIR / "config.json"


# File format for cache files
FILE_FORMAT: Final[str] = "{country}_{city}_{month}_{year}_{method}.json"

# Create list for prayer names
PRAYERS: Final[List[str]] = [
    "Fajr",
    "Sunrise",
    "Dhuhr",
    "Asr",
    "Maghrib",
    "Isha",
]

DEFAULT_PRAYERS: Final[List[str]] = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]


# dict for time formats (strftime/strptime)
TIME_FORMATS: Final[Dict[TimeFormat, str]] = {
    TimeFormat.twelve: "%I:%M %p",
    TimeFormat.twenty_four: "%H:%M",
}

# dict for timedelta
TIMEDELTA: Final[Dict[OutType | NextOutType, str]] = {
    OutType.pretty: "{hours}:{minutes} Hrs",
    OutType.machine: "{hours:02d}:{minutes:02d} Hrs",
    OutType.table: "{hours}:{minutes} Hrs",
    OutType.json: "{hours:02d}:{minutes:02d} Hrs",
    NextOutType.waybar: "{hours:02d}:{minutes:02d} Hrs",
}


# Waybar icons
WAYBAR_ICONS = {
    "Fajr": "󰖜",
    "Dhuhr": "󰖙",
    "Asr": "󰼰",
    "Maghrib": "󰖛",
    "Isha": "󰖔",
}
