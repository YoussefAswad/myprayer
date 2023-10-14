from datetime import datetime, timedelta

from myprayer.api.prayer import Prayer


class Day:
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
