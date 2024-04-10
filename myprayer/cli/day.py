from datetime import datetime, timedelta

import tzlocal
from adhanpy.calculation import CalculationMethod
from adhanpy.PrayerTimes import PrayerTimes

tz = tzlocal.get_localzone()


class Prayer:
    def __init__(self, name: str, time: datetime) -> None:
        self.name = name
        self.time = time

    def has_passed(self) -> bool:
        return datetime.now(tz) > self.time

    def time_left(self) -> timedelta:
        return self.time - datetime.now(tz)

    def __str__(self) -> str:
        return f"{self.name}: {self.time.strftime('%H:%M')}"


class Day:
    """Represents a single day with prayer times.

    Attributes:
        day (int): The day number in the month
        month (int): The month number 1-12
        year (int): The year
        data (dict): The prayer time data for this day
        prayers (list[Prayer]): List of Prayer objects
        skip (list[str]): Prayer names to skip

    Methods:
        get_next_prayer(): Returns the next prayer that has not passed yet
        get_prayer(name): Returns the Prayer object with the given name
        has_passed(): Checks if the last prayer of the day has passed

    Raises:
        ValueError: If day is not 1-31 or month is not 1-12

    Examples:
        >>> data = Client().get_day(15, 1, 2022)
        >>> print(day.prayers[0].name)
        Fajr

        >>> day.get_prayer("fajr").__str__()
        Fajr: 05:20
    """

    latitude: float
    longitude: float
    method: CalculationMethod
    date: datetime
    prayers: list[Prayer]
    skip: list[str]

    def __init__(
        self,
        latitude: float = 30,
        longitude: float = 31,
        method: CalculationMethod = CalculationMethod.EGYPTIAN,
        date: datetime = datetime.now(tz),
        skip: list[str] = [],
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.method = method
        self.skip = [x.lower() for x in skip]

        self.date: datetime = date
        prayers = self.__get_prayer_times(latitude, longitude, date, method)

        for prayer in prayers:
            if prayer.name.lower() in self.skip:
                prayers.remove(prayer)

        self.prayers: list[Prayer] = prayers

    @staticmethod
    def __get_prayer_times(
        latitude: float,
        longitude: float,
        date: datetime,
        method: CalculationMethod = CalculationMethod.EGYPTIAN,
    ):
        prayer_times = PrayerTimes(
            (latitude, longitude),
            date,
            method,
            time_zone=tz,
        )

        return [
            Prayer("Fajr", prayer_times.fajr),
            Prayer("Sunrise", prayer_times.sunrise),
            Prayer("Dhuhr", prayer_times.dhuhr),
            Prayer("Asr", prayer_times.asr),
            Prayer("Maghrib", prayer_times.maghrib),
            Prayer("Isha", prayer_times.isha),
        ]

    def next(self) -> None:
        self.__init__(
            self.latitude,
            self.longitude,
            self.method,
            self.date + timedelta(days=1),
            self.skip,
        )

    def get_next_prayer(self) -> Prayer | None:
        for prayer in self.prayers:
            if not prayer.has_passed():
                return prayer

    def get_prayer(self, name: str) -> Prayer | None:
        for prayer in self.prayers:
            if prayer.name == name:
                return prayer

    def has_passed(self) -> bool:
        return self.prayers[-1].has_passed()
