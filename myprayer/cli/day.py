from datetime import datetime, timedelta

import tzlocal

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

    date: datetime
    prayers: list[Prayer]

    def __init__(self, date: datetime, prayers: list[Prayer], skip: list[str] = []):

        skip = [x.lower() for x in skip]

        self.date: datetime = date

        for prayer in prayers:
            if prayer.name.lower() in skip:
                prayers.remove(prayer)

        self.prayers: list[Prayer] = prayers

    def get_next_prayer(self) -> Prayer | None:
        for prayer in self.prayers:
            if not prayer.has_passed():
                return prayer

    def get_prayer(self, name: str) -> Prayer | None:
        for prayer in self.prayers:
            if prayer.name == name:
                return prayer

    def has_passed(self) -> bool:
        if self.prayers[-1].has_passed():
            return True
        return False
