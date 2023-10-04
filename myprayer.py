#!/usr/bin/env python

import json
import os
from datetime import datetime
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Tuple

import requests
import typer
from rich import print
from rich.console import Console
from rich.table import Table

app = typer.Typer(pretty_exceptions_enable=False)


# Create enum for print type
class PrintType(StrEnum):
    pretty = "pretty"
    machine = "machine"
    table = "table"


class TimeFormat(StrEnum):
    twelve = "12"
    twenty_four = "24"


cache_dir = (
    Path(os.environ.get("XDG_CACHE_HOME") or os.path.join(Path.home(), ".cache"))
    / "myprayer"
)

# Create cache dir if it doesn't exist
cache_dir.mkdir(parents=True, exist_ok=True)
file_format = "{country}_{city}_{month}_{year}.json"


def save(data: dict, month: int, year: int, city: str, country: str) -> None:
    with open(
        cache_dir
        / file_format.format(country=country, city=city, month=month, year=year),
        "w",
    ) as f:
        json.dump(data, f)


def load(month: int, year: int, city: str, country) -> dict:
    with open(
        cache_dir
        / file_format.format(country=country, city=city, month=month, year=year),
        "r",
    ) as f:
        return json.load(f)


def fetch(month: int, year: int, city: str, country: str) -> dict:
    url = f"http://api.aladhan.com/v1/calendarByCity/{year}/{month}"
    params = {"city": city, "country": country, "method": "5"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        save(data, month, year, city, country)
        return data["data"]
    else:
        print(f"Failed to fetch data for {month}/{year} in {city}, {country}")
        exit(1)


def get_day(data: dict, day: int, time_format: TimeFormat) -> Tuple[dict, datetime]:
    data["data"][day - 1]
    day_data = data["data"][day - 1]
    timings = day_data["timings"]
    for prayer, time in timings.items():
        time = time[:5]
        if time_format == TimeFormat.twelve:
            timings[prayer] = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")
        else:
            timings[prayer] = time
    date = datetime.strptime((day_data["date"]["readable"]), "%d %b %Y")
    return timings, date


def print_pretty(timings: dict):
    print(f"[bold]Fajr:[/bold] {timings['Fajr']}")
    print(f"[bold]Sunrise:[/bold] {timings['Sunrise']}")
    print(f"[bold]Dhuhr:[/bold] {timings['Dhuhr']}")
    print(f"[bold]Asr:[/bold] {timings['Asr']}")
    print(f"[bold]Maghrib:[/bold] {timings['Maghrib']}")
    print(f"[bold]Isha:[/bold] {timings['Isha']}")
    print(f"[bold]Imsak:[/bold] {timings['Imsak']}")
    print(f"[bold]Midnight:[/bold] {timings['Midnight']}")


def print_machine(timings: dict):
    for prayer, time in timings.items():
        print(f"{prayer}={time}")


def print_table(timings: dict):
    console = Console()
    table = Table(
        show_header=True, header_style="bold magenta", row_styles=["none", "dim"]
    )
    table.add_column("[bold]Prayer[/bold]")
    table.add_column("[bold]Time[/bold]")

    for prayer, time in timings.items():
        table.add_row(f"[bold]{prayer}[/bold]", time)

    console.print(table)


@app.command()
def get(
    time_format: TimeFormat = typer.Option(
        TimeFormat.twelve, "--time-format", "-F", help="Time format (12, 24)."
    ),
    print_type: PrintType = typer.Option(
        PrintType.pretty,
        "--type",
        "-t",
        help="Print type (pretty, machine, table).",
    ),
    city: str = typer.Argument(show_default=False, help="City name."),
    country: str = typer.Argument(show_default=False, help="Country name."),
    day: int = typer.Option(
        datetime.today().day,
        "--day",
        "-d",
        help="Day number (1-31), defaults to current day.",
        show_default=False,
    ),
    month: int = typer.Option(
        datetime.today().month,
        "--month",
        "-m",
        help="Month number (1-12), defaults to current month.",
        show_default=False,
    ),
    year: int = typer.Option(
        datetime.today().year,
        "--year",
        "-y",
        help="Year number, defaults to current year.",
        show_default=False,
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force update."),
):
    # Check if data is already cached
    cache_file = cache_dir / file_format.format(
        country=country, city=city, month=month, year=year
    )
    if not force and cache_file.exists():
        data = load(month, year, city, country)
    else:
        data = fetch(month, year, city, country)

    timings, date = get_day(data, day, time_format)

    match print_type:
        case PrintType.pretty:
            print_pretty(timings)
        case PrintType.machine:
            print_machine(timings)
        case PrintType.table:
            print_table(timings)


@app.command(name="list")
def list_prayers():
    ...


if __name__ == "__main__":
    app()
