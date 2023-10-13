# Description: This file contains all the constants used in the project

import os
from pathlib import Path

from myprayer.enums import OutType, TimeFormat

APP_NAME = "myprayer"
# Prayer times API URL

URL = "http://api.aladhan.com/v1/calendarByCity/"

# Find config/cache dir based on OS
if str(os.name) == "nt":
    CACHE_DIR = (
        Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / APP_NAME
    )
    CONFIG_DIR = (
        Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming") / APP_NAME
    )
else:
    CACHE_DIR = (
        Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / APP_NAME
    )
    CONFIG_DIR = (
        Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / APP_NAME
    )

# config file path
CONFIG_FILE = CONFIG_DIR / "config.json"

# Create cache dir if it doesn't exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# File format for cache files
FILE_FORMAT = "{country}_{city}_{month}_{year}_{method}.json"

# Create list for prayer names
PRAYERS = [
    "Fajr",
    "Sunrise",
    "Dhuhr",
    "Asr",
    "Maghrib",
    "Isha",
    "Midnight",
]

DEFAULT_PRAYERS = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

# Create dict for calculation methods
CALCULATION_METHODS = {
    "University of Islamic Sciences, Karachi": 1,
    "Islamic Society of North America": 2,
    "Muslim World League": 3,
    "Umm Al-Qura University, Makkah": 4,
    "Egyptian General Authority of Survey": 5,
    "Institute of Geophysics, University of Tehran": 7,
    "Gulf Region": 8,
    "Kuwait": 9,
    "Qatar": 10,
    "Majlis Ugama Islam Singapura, Singapore": 11,
    "Union Organization islamic de France": 12,
    "Diyanet İşleri Başkanlığı, Turkey": 13,
    "Spiritual Administration of Muslims of Russia": 14,
}

# Create dict for time formats (strftime/strptime)
TIME_FORMATS = {
    TimeFormat.twelve: "%I:%M %p",
    TimeFormat.twenty_four: "%H:%M",
}

# Create dict for timedelta
TIMEDELTA = {
    OutType.pretty: " ({hours}H {minutes}M)",
    OutType.machine: "{hours:02d}H{minutes:02d}M",
    OutType.table: " ({hours}H {minutes}M)",
    OutType.json: "{hours}H {minutes}M",
}


# Waybar icons
WAYBAR_ICONS = {
    "Fajr": "󰖜",
    "Dhuhr": "󰖙",
    "Asr": "󰼰",
    "Maghrib": "󰖛",
    "Isha": "󰖔",
}
