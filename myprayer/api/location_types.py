from typing import Optional
from urllib.parse import quote


class City:
    def __init__(self, city: str, country: str, state: Optional[str] = None) -> None:
        self.city = city
        self.state = state
        self.country = country


class Coordinates:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude


class Address:
    def __init__(self, address: str) -> None:
        self.address = address

    def url_encoded(self) -> str:
        return quote(self.address, safe="")
