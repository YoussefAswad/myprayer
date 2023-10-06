import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from myprayer.enums import OutType, TimeFormat


# Create dataclass for config that has default values and can be loaded from file
class Config:
    day: int = datetime.today().day
    month: int = datetime.today().month
    year: int = datetime.today().year
    city: str = ""
    country: str = ""
    time_format: TimeFormat = TimeFormat.twelve
    out_type: OutType = OutType.table
    method: int = 5
    next: bool = True
    prayers: list[str] = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

    def __init__(
        self,
        config_file: Path,
    ):
        if config_file.exists():
            with open(config_file, "r") as f:
                data = json.load(f)

            self.city = data["city"]
            self.country = data["country"]
            self.time_format = TimeFormat(data["time_format"])
            self.out_type = OutType(data["print_type"])
            self.method = data["method"]
            self.next = data["next"]

    def update(
        self,
        day: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        time_format: Optional[TimeFormat] = None,
        out_type: Optional[OutType] = None,
        method: Optional[int] = None,
        next: Optional[bool] = None,
        prayers: Optional[list[str]] = None,
    ):
        if day is not None:
            self.day = day
        if month is not None:
            self.month = month
        if year is not None:
            self.year = year
        if city is not None:
            self.city = city
        if country is not None:
            self.country = country
        if time_format is not None:
            self.time_format = time_format
        if out_type is not None:
            self.out_type = out_type
        if method is not None:
            self.method = method
        if next is not None:
            self.next = next
        if prayers is not None:
            self.prayers = prayers

    def save(self, config_file: Path):
        with open(config_file, "w") as f:
            json.dump(
                {
                    "city": self.city,
                    "country": self.country,
                    "time_format": self.time_format.value,
                    "print_type": self.out_type.value,
                    "method": self.method,
                    "next": self.next,
                },
                f,
                indent=4,
            )
