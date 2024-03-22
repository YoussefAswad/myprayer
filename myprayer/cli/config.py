import json
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, validator

from myprayer.api.location_types import Address, City, Coordinates
from myprayer.cli.constants import CALCULATION_METHODS, DEFAULT_PRAYERS
from myprayer.cli.enums import OutType, TimeFormat


class LocationType(str, Enum):
    city = "city"
    coordinates = "coordinates"
    address = "address"


class CityModel(BaseModel):
    type: Literal["city"]
    city: str
    country: str
    state: Optional[str] = None


class CoordinatesModel(BaseModel):
    type: Literal["coordinates"]
    latitude: float
    longitude: float


class AddressModel(BaseModel):
    type: Literal["address"]
    address: str


class ConfigModel(BaseModel):
    location: CityModel | CoordinatesModel | AddressModel
    time_format: TimeFormat
    print_type: OutType
    method: int
    show_next: bool
    prayers: list[str]

    @validator("method")
    def method_is_valid(cls, v):
        if v not in CALCULATION_METHODS.values():
            raise ValueError(f"Invalid method: {v}")
        return v


# Create dataclass for config that has default values and can be loaded from file
class Config:
    location: City | Coordinates | Address
    time_format: TimeFormat = TimeFormat.twelve
    out_type: OutType = OutType.table
    method: int = 5
    next: bool = True
    prayers: list[str] = DEFAULT_PRAYERS
    is_error: bool = False
    error: Optional[str] = None

    def __init__(
        self,
        config_file: Path,
    ):
        self.location = City("Cairo", "Egypt")
        self.time_format = TimeFormat.twelve
        self.out_type = OutType.table
        self.method = 5
        self.next = True
        self.prayers = DEFAULT_PRAYERS
        self.is_error = False
        self.error = None

        if config_file.exists():
            with open(config_file, "r") as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    self.is_error = True
                    self.error = "Invalid config file"
                    return

            # Validate data
            try:
                ConfigModel(**data)
            except Exception:
                self.is_error = True
                self.error = "Invalid config file structure"
                return

            location_type: str = data["location"]["type"]
            if location_type == "city":
                self.location = City(
                    data["location"]["city"],
                    data["location"]["country"],
                    data["location"]["state"] if "state" in data["location"] else None,
                )
            elif location_type == "coordinates":
                self.location = Coordinates(
                    data["location"]["latitude"],
                    data["location"]["longitude"],
                )
            elif location_type == "address":
                self.location = Address(
                    data["location"]["address"],
                )

            self.time_format = TimeFormat(data["time_format"])
            self.out_type = OutType(data["print_type"])
            self.method = data["method"]
            self.next = data["show_next"]
            self.prayers = data["prayers"]
        else:
            self.is_error = True
            self.error = "Config file not found, please run `myprayer config` to create one."

    def update(
        self,
        location: Optional[City | Coordinates | Address],
        time_format: Optional[TimeFormat] = None,
        out_type: Optional[OutType] = None,
        method: Optional[int] = None,
        next: Optional[bool] = None,
        prayers: Optional[list[str]] = None,
    ):
        if location is not None:
            self.location = location
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
        if not config_file.parent.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)
        config_data = {
            "time_format": self.time_format.value,
            "print_type": self.out_type.value,
            "method": self.method,
            "show_next": self.next,
            "prayers": self.prayers,
        }

        if isinstance(self.location, City):
            config_data["location"] = {
                "type": "city",
                "city": self.location.city,
                "country": self.location.country,
                "state": self.location.state,
            }
        elif isinstance(self.location, Coordinates):
            config_data["location"] = {
                "type": "coordinates",
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
            }
        elif isinstance(self.location, Address):
            config_data["location"] = {
                "type": "address",
                "address": self.location.address,
            }

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=4)
