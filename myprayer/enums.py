# Description: This file contains all the enums used in the project

from enum import StrEnum


# Create enum for print type
class OutType(StrEnum):
    pretty = "pretty"
    machine = "machine"
    table = "table"
    json = "json"


# Create enum for time format
class TimeFormat(StrEnum):
    twelve = "12"
    twenty_four = "24"


# Create enum for prayer
class Prayer(StrEnum):
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
