import json
from datetime import timedelta
from typing import Optional

import requests
import typer
from rich import print

from myprayer.config import Config
from myprayer.constants import CACHE_DIR, FILE_FORMAT, URL
from myprayer.day import Day


class Month:
    config: Config
    data: dict
    month: int
    year: int

    def __init__(
        self,
        config: Config,
        force: bool = False,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ):
        self.config = config
        self.month = month if month else config.date.month
        self.year = year if year else config.date.year
        self.force = force
        self.init()

    def init(self) -> None:
        cache_file = CACHE_DIR / FILE_FORMAT.format(
            year=self.year,
            month=self.month,
            country=self.config.country,
            city=self.config.city,
            method=self.config.method,
        )
        # Check if data is already cached
        if not self.force and cache_file.exists():
            self.data = self.load()
        else:
            self.data = self.fetch()

    def get(self) -> dict:
        return self.data

    def get_day(self, day: Optional[int] = None) -> Day:
        return Day(self.config, self.data, day)

    # get the day for the next prayer
    def get_next_day(self) -> Day:
        day = self.get_day()
        if day.has_passed(self.config.prayers[-1]):
            next_day = self.config.date + timedelta(days=1)
            self.month = next_day.month
            self.year = next_day.year
            self.init()
            day = self.get_day(next_day.day)
        return day

    def fetch(self) -> dict:
        url = f"{URL}{self.config.date.year}/{self.config.date.month}"
        params = {
            "city": self.config.city,
            "country": self.config.country,
            "method": self.config.method,
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.save(
                data["data"],
            )
            return data["data"]
        else:
            print(
                f"Failed to fetch data for {self.config.date.month}/{self.config.date.year} in {self.config.city}, {self.config.country}"
            )
            raise typer.Exit(1)

    def save(self, data: dict) -> None:
        with open(
            CACHE_DIR
            / FILE_FORMAT.format(
                country=self.config.country,
                city=self.config.city,
                month=self.config.date.month,
                year=self.config.date.year,
                method=self.config.method,
            ),
            "w",
        ) as f:
            json.dump(data, f)

    def load(self) -> dict:
        with open(
            CACHE_DIR
            / FILE_FORMAT.format(
                country=self.config.country,
                city=self.config.city,
                month=self.config.date.month,
                year=self.config.date.year,
                method=self.config.method,
            ),
            "r",
        ) as f:
            return json.load(f)
