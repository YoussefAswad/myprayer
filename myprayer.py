#!/usr/bin/env python

import json
import os
from calendar import month_name
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Tuple

import inquirer
import requests
import typer
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

APP_NAME = "myprayer"

app = typer.Typer(name=APP_NAME, pretty_exceptions_enable=False)


# Create enum for print type
class PrintType(StrEnum):
    pretty = "pretty"
    machine = "machine"
    table = "table"
    json = "json"


# Create enum for time format
class TimeFormat(StrEnum):
    twelve = "12"
    twenty_four = "24"


# Create enum for prayer
class Prayer(StrEnum):
    fajr = "Fajr"
    sunrise = "Sunrise"
    dhuhr = "Dhuhr"
    asr = "Asr"
    sunset = "Sunset"
    maghrib = "Maghrib"
    isha = "Isha"
    imsak = "Imsak"
    midnight = "Midnight"
    firstthird = "Firstthird"
    lastthird = "Lastthird"


# Create dict for calculation methods
CALCULATION_METHODS = {
    "University of Islamic Sciences, Karachi": 1,
    "Islamic Society of North America": 2,
    "Muslim World League": 3,
    "Umm Al-Qura University, Makkah": 4,
    "Egyptian General Authority of Survey": 5,
    "Institute of Geophysics, University of Tehran": 7,
    "Gulf Region": 8,
    "Kuwait": 9,
    "Qatar": 10,
    "Majlis Ugama Islam Singapura, Singapore": 11,
    "Union Organization islamic de France": 12,
    "Diyanet İşleri Başkanlığı, Turkey": 13,
    "Spiritual Administration of Muslims of Russia": 14,
}

# Create dict for time formats (strftime/strptime)
TIME_FORMATS = {
    TimeFormat.twelve: "%I:%M %p",
    TimeFormat.twenty_four: "%H:%M",
}


# Create dataclass for config that has default values and can be loaded from file
@dataclass
class Config:
    city: str = ""
    country: str = ""
    time_format: TimeFormat = TimeFormat.twelve
    print_type: PrintType = PrintType.table
    method: int = 5
    next: bool = True

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
            self.print_type = PrintType(data["print_type"])
            self.method = data["method"]
            self.next = data["next"]

    def update(
        self,
        city: str,
        country: str,
        time_format: TimeFormat,
        print_type: PrintType,
        method: int,
        next: bool,
    ):
        self.city = city
        self.country = country
        self.time_format = time_format
        self.print_type = print_type
        self.method = method
        self.next = next


# Find config/cache dir based on OS
if str(os.name) == "nt":
    CACHE_DIR = (
        Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / APP_NAME
    )
    CONFIG_DIR = (
        Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming") / APP_NAME
    )
else:
    CACHE_DIR = (
        Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / APP_NAME
    )
    CONFIG_DIR = (
        Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / APP_NAME
    )

# config file path
CONFIG_FILE = CONFIG_DIR / "config.json"

# Create cache dir if it doesn't exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# File format for cache files
FILE_FORMAT = "{country}_{city}_{month}_{year}_{method}.json"

# Load config
CONFIG = Config(CONFIG_FILE)


def save(
    data: dict, month: int, year: int, city: str, country: str, method: int
) -> None:
    with open(
        CACHE_DIR
        / FILE_FORMAT.format(
            country=country, city=city, month=month, year=year, method=method
        ),
        "w",
    ) as f:
        json.dump(data, f)


def load(month: int, year: int, city: str, country: str, method: int) -> dict:
    with open(
        CACHE_DIR
        / FILE_FORMAT.format(
            country=country, city=city, month=month, year=year, method=method
        ),
        "r",
    ) as f:
        return json.load(f)


def fetch(month: int, year: int, city: str, country: str, method: int) -> dict:
    url = f"http://api.aladhan.com/v1/calendarByCity/{year}/{month}"
    params = {"city": city, "country": country, "method": method}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        save(data["data"], month, year, city, country, method)
        return data["data"]
    else:
        print(f"Failed to fetch data for {month}/{year} in {city}, {country}")
        raise typer.Exit(1)


def get_day(
    data: dict, day: int, month: int, year: int
) -> Tuple[dict[str, datetime], datetime]:
    # print(f"Getting data for {day}/{month}/{year}")
    try:
        day_data = data[day - 1]
    except IndexError:
        print(f"{month_name[month]} is {len(data)} days.")
        raise typer.Exit(1)

    timings = day_data["timings"]
    for prayer, time in timings.items():
        timings[prayer] = datetime.strptime(
            time[:5], TIME_FORMATS[TimeFormat.twenty_four]
        ).replace(day=day, month=month, year=year)

    date = datetime.strptime((day_data["date"]["readable"]), "%d %b %Y")
    return timings, date


def get_key(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key


def get_next(timings: dict) -> str:
    now = datetime.now()
    for prayer, time in timings.items():
        if time > now:
            return prayer
    return "Fajr"


def out_pretty(timings: dict):
    for prayer, time in timings.items():
        print(
            f"[bold]{prayer}:[/bold] {time.strftime(TIME_FORMATS[CONFIG.time_format])}"
        )


def out_machine(timings: dict):
    for prayer, time in timings.items():
        print(
            f"{prayer},{time.strftime(TIME_FORMATS[CONFIG.time_format])},{time.date()}"
        )


def out_table(timings: dict, next_prayer: str = ""):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Prayer")
    table.add_column("Time")

    for prayer, time in timings.items():
        style = "cyan" if prayer == next_prayer else ""
        time = time.strftime(TIME_FORMATS[CONFIG.time_format])
        table.add_row(f"[bold]{prayer}[/bold]", time, style=style)

    console.print(table)


def out_json(timings: dict, date: datetime, next_prayer: str = ""):
    out_json = {}
    out_json["date"] = date.strftime("%d %b %Y")
    timings = {
        prayer: time.strftime(TIME_FORMATS[CONFIG.time_format])
        for prayer, time in timings.items()
    }
    out_json["timings"] = timings
    if next_prayer:
        out_json["next"] = next_prayer
    print(json.dumps(out_json, indent=4))


def get(
    city: str, country: str, month: int, year: int, method: int, force: bool = False
) -> dict:
    # Check if data is already cached
    cache_file = CACHE_DIR / FILE_FORMAT.format(
        country=country, city=city, month=month, year=year, method=method
    )
    if not force and cache_file.exists():
        data = load(month, year, city, country, method)
    else:
        data = fetch(month, year, city, country, method)
    return data


@app.command(name="list", help="List prayer times.")
def list_prayers(
    city: str = typer.Argument(CONFIG.city, help="City name."),
    country: str = typer.Argument(CONFIG.country, help="Country name."),
    day: int = typer.Option(
        datetime.today().day,
        "--day",
        "-d",
        min=1,
        max=31,
        help="Day (1-31)",
        show_default="Current day",  # type: ignore
    ),
    month: int = typer.Option(
        datetime.today().month,
        "--month",
        "-m",
        min=1,
        max=12,
        help="Month",
        show_default="Current month",  # type: ignore
    ),
    year: int = typer.Option(
        datetime.today().year,
        "--year",
        "-y",
        help="Year",
        show_default="Current year",  # type: ignore
    ),
    method: int = typer.Option(
        CONFIG.method,
        "--method",
        "-M",
        help="Calculation method.",
        show_default=f"{get_key(CALCULATION_METHODS, CONFIG.method)}",  # type: ignore
    ),
    time_format: TimeFormat = typer.Option(
        CONFIG.time_format, "--time-format", "-t", help="Time format."
    ),
    print_type: PrintType = typer.Option(
        CONFIG.print_type,
        "--output",
        "-o",
        help="Print type.",
    ),
    next: bool = typer.Option(CONFIG.next, "--next", "-n", help="Show next prayer."),
    force: bool = typer.Option(False, "--force", "-f", help="Force update cache."),
):
    CONFIG.update(city, country, time_format, print_type, method, next)
    if not city or not country:
        print(
            "[red]Please provide a city and country, or run config to set the defaults.[/red]"
        )
        raise typer.Exit(1)

    data = get(city, country, month, year, method, force)
    timings, date = get_day(data, day, month, year)

    next_prayer = ""
    if next:
        if (
            day == datetime.today().day
            and month == datetime.today().month
            and year == datetime.today().year
        ):
            next_prayer = get_next(timings)
            ...  # TODO: Implement next prayer for today

    match print_type:
        case PrintType.pretty:
            out_pretty(timings)
        case PrintType.machine:
            out_machine(timings)
        case PrintType.table:
            out_table(timings, next_prayer)
        case PrintType.json:
            out_json(timings, date, next_prayer)


@app.command(name="next", help="Show next prayer.")
def next():
    pass


@app.command(name="config", help="Configure myprayer.")
def config():
    # Prompt for city
    city: str = Prompt.ask("City")

    # Prompt for country
    country: str = Prompt.ask("Country")

    # Prompt for calculation method
    method_question = [
        inquirer.List(
            "method",
            message="Select a calculation method:",
            choices=CALCULATION_METHODS,
        ),
    ]
    method_choice = inquirer.prompt(method_question)
    method: int = CALCULATION_METHODS[method_choice["method"]]  # type: ignore
    time_format: str = Prompt.ask(
        "Time format",
        choices=[TimeFormat.twelve, TimeFormat.twenty_four],
        default=TimeFormat.twelve,
    )
    print_type: str = Prompt.ask(
        "Print type",
        choices=[PrintType.pretty, PrintType.machine, PrintType.table],
        default=PrintType.table,
    )
    next = typer.confirm("Show next prayer?", default=True)
    config = {
        "city": city,
        "country": country,
        "time_format": time_format,
        "print_type": print_type,
        "method": method,
        "next": next,
    }
    save_config(config)
    print(f"[green]✔[/green] Configuration saved to {CONFIG_FILE}.")


# @app.command(name="show-config", help="Show current configuration.")
# def load_config() -> Config:
#     with open(CONFIG_FILE, "r") as f:
#         data = json.load(f)
#     config = Config(
#         data["city"],
#         data["country"],
#         TimeFormat(data["time_format"]),
#         PrintType(data["print_type"]),
#         data["method"],
#         data["next"],
#     )
#     return config


def save_config(config: dict) -> None:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_DIR / "config.json", "w") as f:
        json.dump(config, f)


if __name__ == "__main__":
    app()
