import json
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

    def __init__(
        self,
        config: Config,
        force: bool = False,
    ):
        self.config = config
        cache_file = CACHE_DIR / FILE_FORMAT.format(
            country=config.country,
            city=config.city,
            month=config.month,
            year=config.year,
            method=config.method,
        )
        self.force = force
        # Check if data is already cached
        if not self.force and cache_file.exists():
            self.data = self.load()
        else:
            self.data = self.fetch()

    def get(self) -> dict:
        return self.data

    def get_day(self, day: Optional[int] = None) -> Day:
        return Day(self.config, self.data, day)

    def fetch(self) -> dict:
        url = f"{URL}{self.config.year}/{self.config.month}"
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
                f"Failed to fetch data for {self.config.month}/{self.config.year} in {self.config.city}, {self.config.country}"
            )
            raise typer.Exit(1)

    def save(self, data: dict) -> None:
        with open(
            CACHE_DIR
            / FILE_FORMAT.format(
                country=self.config.country,
                city=self.config.city,
                month=self.config.month,
                year=self.config.year,
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
                month=self.config.month,
                year=self.config.year,
                method=self.config.method,
            ),
            "r",
        ) as f:
            return json.load(f)
