import json
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from adhanpy.calculation import CalculationMethod
from pydantic import BaseModel, ValidationError, validator

from myprayer.cli.constants import DEFAULT_PRAYERS
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
    # type: Literal["coordinates"]
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
        valid_methods = [m.value for m in CalculationMethod]
        if v not in valid_methods:
            raise ValueError(f"Invalid method: {v}")
        return v


class Coordinates:
    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude


# Create dataclass for config that has default values and can be loaded from file
class Config:
    location: Coordinates
    time_format: TimeFormat
    out_type: OutType
    method: int
    next: bool
    prayers: list[str]
    is_error: bool
    error: Optional[str]

    def __init__(
        self,
        config_file: Path,
    ):
        self.location = Coordinates(latitude=30, longitude=31)
        self.time_format = TimeFormat.twelve
        self.out_type = OutType.table
        self.method = CalculationMethod.EGYPTIAN.value
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
            except ValidationError as e:
                self.is_error = True
                self.error = f"Invalid config file structure: {e}"
                return

            # location_type: str = data["location"]["type"]
            # if location_type == "city":
            #     self.location = City(
            #         data["location"]["city"],
            #         data["location"]["country"],
            #         data["location"]["state"] if "state" in data["location"] else None,
            #     )

            try:
                self.location = Coordinates(
                    latitude=data["location"]["latitude"],
                    longitude=data["location"]["longitude"],
                )
            except KeyError:
                self.is_error = True
                self.error = "Invalid location data"
                return
            # elif location_type == "address":
            #     self.location = Address(
            #         data["location"]["address"],
            #     )

            self.time_format = TimeFormat(data["time_format"])
            self.out_type = OutType(data["print_type"])
            # FIXME: add validation for method
            self.method = data["method"]

            try:
                CalculationMethod(self.method)
            except ValueError:
                self.is_error = True
                self.error = "Invalid method"
                return

            self.next = data["show_next"]
            self.prayers = data["prayers"]
        else:
            self.is_error = True
            self.error = (
                "Config file not found, please run `myprayer config` to create one."
            )

    def update(
        self,
        location: Optional[Coordinates],
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

        config_data["location"] = {
            "latitude": self.location.latitude,
            "longitude": self.location.longitude,
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=4)
