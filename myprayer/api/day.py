from datetime import datetime, timedelta

from myprayer.api.prayer import Prayer


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

    day: int
    month: int
    year: int
    data: dict
    prayers: list[Prayer]

    def __init__(
        self, day: int, month: int, year: int, data: dict, skip: list[str] = []
    ):
        if day not in range(1, 32):
            raise ValueError("Day must be in range 1 to 31")
        if month not in range(1, 13):
            raise ValueError("Month must be in range 1 to 12")

        self.data: dict = data
        self.day: int = day
        self.month: int = month
        self.year: int = year
        self.date: datetime = datetime(year, month, day)
        self.prayers: list[Prayer] = []
        self.skip: list[str] = skip

        timings = data["timings"]
        day_passed = False
        last_prayer = None
        for prayer, time in timings.items():
            if prayer in self.skip:
                continue
            prayer_time = datetime.strptime(time[:5], "%H:%M").replace(
                day=self.day,
                month=self.month,
                year=self.year,
            )
            if last_prayer and (prayer_time - last_prayer).total_seconds() < 0:
                day_passed = True

            if day_passed:
                prayer_time += timedelta(days=1)
            self.prayers += [Prayer(prayer, prayer_time)]
            last_prayer = prayer_time

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
