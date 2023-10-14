from calendar import month_name, monthrange

from myprayer.api.day import Day
from myprayer.config import Config


class Month:
    config: Config
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
