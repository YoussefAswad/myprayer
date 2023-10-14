import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from myprayer.api.day import Day
from myprayer.api.exceptions import *
from myprayer.api.location_types import Address, City, Coordinates
from myprayer.api.month import Month
from myprayer.api.prayer import Prayer

API = "http://api.aladhan.com/v1/"
FILE_FORMAT = "{month}_{year}_{method}.json"
SKIP = ["Firstthird", "Lastthird", "Imsak", "Sunset"]


class Client:
    def __init__(
        self,
        location: City | Coordinates | Address,
        method: int = 3,
        skip: list[str] = [],
        cache_dir: Optional[Path] = None,
    ) -> None:
        self.location = location
        self.method = method
        self.skip = skip + SKIP
        self.cache_dir = cache_dir

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def __set_location_params(params: dict, location: City | Coordinates | Address):
        if isinstance(location, Coordinates):
            params["latitude"] = location.latitude
            params["longitude"] = location.longitude
        elif isinstance(location, Address):
            params["address"] = location.url_encoded()
        elif isinstance(location, City):
            params["city"] = location.city
            params["country"] = location.country
            if location.state:
                params["state"] = location.state

    @staticmethod
    def __get_endpoint_by_location(
        location: City | Coordinates | Address, endpoint: str
    ):
        if isinstance(location, Coordinates):
            return endpoint
        if isinstance(location, Address):
            return endpoint + "ByAddress"
        if isinstance(location, City):
            return endpoint + "ByCity"

    @staticmethod
    def __detect_exceptions(response: requests.Response, data: dict):
        if response.status_code == 429:
            raise RateLimitedException("Rate limit exceeded.")
        if response.status_code == 400:
            raise BadRequestException(data["data"])
        if response.status_code == 500:
            raise ServerErrorException(data["message"])

    # TODO: add support for different methods
    @staticmethod
    def __get_cache_file_name(
        month: int, year: int, location: City | Coordinates | Address, method: int
    ):
        suffix = f"{month}_{year}_{method}.json"
        if isinstance(location, Coordinates):
            return f"coordinates_{location.longitude}_{location.latitude}_{suffix}"
        if isinstance(location, Address):
            return f"address_{location.url_encoded()}_{suffix}"
        if isinstance(location, City):
            return f"city_{location.city}_{location.country}_{suffix}"

    def get_today(self) -> Day:
        today = datetime.today()
        return self.get_day(today.day, today.month, today.year)

    def get_next_prayers(self) -> Day:
        # Get the current month and day.
        today = datetime.today()
        current_month = self.get_month(today.month, today.year)
        current_day = current_month.get_day(today.day)

        # Check if the current day has already passed.
        if current_day.has_passed():
            # Check if the current month has passed.
            if current_month.has_passed():
                # If it's December, switch to the next year, and set the month to January.
                if current_month.month == 12:
                    next_month = self.get_month(1, today.year + 1)
                else:
                    # Otherwise, switch to the next month in the current year.
                    next_month = self.get_month(today.month + 1, today.year)
                next_day = next_month.get_day(1)
            else:
                # If the month hasn't passed, just move to the next day in the same month.
                next_day = current_month.get_day(today.day + 1)
        else:
            # If the current day hasn't passed, keep it as is.
            next_day = current_day

        return next_day

    def get_next_prayer(self) -> Prayer | None:
        return self.get_next_prayers().get_next_prayer()

    def get_day(self, day: int, month: int, year: int) -> Day:
        return self.get_month(month, year).get_day(day)

    def get_month(self, month: int, year: int) -> Month:
        if self.cache_dir:
            try:
                data = self.load(month, year)
            except FileNotFoundError:
                data = self.fetch(month, year)
                self.save(data, month, year)
        else:
            data = self.fetch(month, year)

        return Month(month, year, data, self.skip)

    def fetch(self, month: int, year: int) -> dict:
        # define parameters
        params = {
            "method": self.method,
            "month": month,
            "year": year,
        }

        if self.location is None:
            raise ValueError("No location was provided.")
        # set the location type and the ENDPOINT
        self.__set_location_params(params, self.location)
        ENDPOINT = self.__get_endpoint_by_location(self.location, "calendar")

        # send the request and get the JSON data
        response = requests.get(API + ENDPOINT, params=params)
        data = response.json()
        self.__detect_exceptions(response, data)

        return data["data"]

    def save(self, data: dict, month: int, year: int) -> None:
        if self.cache_dir is None:
            raise ValueError("No cache directory was provided.")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(
            self.cache_dir
            / self.__get_cache_file_name(month, year, self.location, self.method),
            "w",
        ) as f:
            json.dump(data, f)

    def load(self, month, year) -> dict:
        if self.cache_dir is None:
            raise ValueError("No cache directory was provided.")
        if self.cache_dir.exists() is False:
            raise FileNotFoundError("Cache directory does not exist.")
        with open(
            self.cache_dir
            / self.__get_cache_file_name(month, year, self.location, self.method),
            "r",
        ) as f:
            return json.load(f)


if __name__ == "__main__":
    client = Client(
        Address("51 Helmy Hasan Ali, Cairo, Egypt"), 5, cache_dir=Path("cache")
    )
    print(Address("51 Helmy Hasan Ali, Cairo, Egypt").url_encoded())
    for prayer in client.get_next_prayers().prayers:
        print(prayer.name, prayer.time)
    client = Client(City("Cairo", "Egypt"), 5, cache_dir=Path("cache"))
    for prayer in client.get_next_prayers().prayers:
        print(prayer.name, prayer.time)
    client = Client(Coordinates(30.0444, 31.2357), 5, cache_dir=Path("cache"))
    for prayer in client.get_next_prayers().prayers:
        print(prayer.name, prayer.time)
