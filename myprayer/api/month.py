from calendar import month_name, monthrange

from myprayer.api.day import Day


class Month:
    """A class representing a calendar month.

    Attributes:
        data (dict): The prayer time data for each day of the month
        name (str): The name of the month (e.g. "January"), derived from the month number
        month (int): The number of the month, 1-12
        year (int): The year
        days (int): The number of days in the month, derived from the month and year
        skip (list[str]): Prayers to skip when getting prayer times

    Methods:
        get_day(day): Returns a Day object for the given day number
        has_passed(): Checks if the last day of the month has passed, i.e. if the last prayer time in the last day has passed

    Raises:
        ValueError: If month is not 1-12 or day is invalid for the month

    Examples:
        >>> jan = Client().get_month(1, 2022)
        >>> jan.name
        "January"

        >>> day = jan.get_day(15)
        >>> day.get_prayer("fajr").__str__()
        Fajr: 05:20

        >>> jan.has_passed()
        False
    """

    data: dict
    name: str
    month: int
    year: int
    days: int

    def __init__(
        self,
        month: int,
        year: int,
        data: dict,
        skip: list[str] = [],
    ):
        if month not in range(1, 13):
            raise ValueError("Month must be in range 1 to 12")

        self.name = month_name[month]
        self.month = month
        self.year = year
        self.data = data
        self.skip = skip
        self.days = monthrange(year, month)[1]

    def get_day(self, day: int) -> Day:
        if day not in range(1, self.days + 1):
            raise ValueError(f"{self.name} {self.year} is only {self.days} days long.")

        return Day(day, self.month, self.year, self.data[day - 1], self.skip)

    def has_passed(self) -> bool:
        # Check if the last day of the month has passed.
        return self.get_day(self.days).has_passed()
