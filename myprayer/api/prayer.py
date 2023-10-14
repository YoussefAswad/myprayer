from datetime import datetime, timedelta


class Prayer:
    def __init__(self, name: str, time: datetime) -> None:
        self.name = name
        self.time = time

    def has_passed(self) -> bool:
        return datetime.now() > self.time

    def time_left(self) -> timedelta:
        return self.time - datetime.now()

    def __str__(self) -> str:
        return f"{self.name}: {self.time.strftime('%H:%M')}"
