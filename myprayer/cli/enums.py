# Description: This file contains all the enums used in the project

from enum import Enum


# Create enum for print type
class OutType(str, Enum):
    pretty = "pretty"
    machine = "machine"
    table = "table"
    json = "json"


class NextOutType(str, Enum):
    pretty = "pretty"
    machine = "machine"
    table = "table"
    json = "json"
    waybar = "waybar"


# Create enum for time format
class TimeFormat(str, Enum):
    twelve = "12"
    twenty_four = "24"


# Create enum for prayer
class Prayer(str, Enum):
    fajr = "Fajr"
    sunrise = "Sunrise"
    dhuhr = "Dhuhr"
    asr = "Asr"
    sunset = "Sunset"
    maghrib = "Maghrib"
    isha = "Isha"
    imsak = "Imsak"
    midnight = "Midnight"
    firstthird = "Firstthird"
    lastthird = "Lastthird"
