#!/usr/bin/env python

import json
from datetime import datetime, timedelta
from importlib.metadata import version as get_version

import inquirer
import typer
import tzlocal
from adhanpy.calculation import CalculationMethod
from adhanpy.PrayerTimes import PrayerTimes
from geopy import Nominatim
from rich import print as rprint
from rich.prompt import FloatPrompt, Prompt
from rich.table import Table

from myprayer.cli import utils
from myprayer.cli.config import Config, Coordinates
from myprayer.cli.constants import (
    APP_NAME,
    CONFIG_FILE,
    LOCATION_TYPES,
    PRAYERS,
    TIME_FORMATS,
)
from myprayer.cli.day import Day, Prayer
from myprayer.cli.enums import NextOutType, OutType, TimeFormat
from myprayer.cli.output import DayOutput
from myprayer.cli.utils import format_time_left

app = typer.Typer(name=APP_NAME, pretty_exceptions_enable=False, help="MyPrayer CLI.")


# TODO: Add option to display date in output
# TODO: Emphasize next prayer in waybar output <span font_weight="bold">...</span>

# Load config
CONFIG = Config(CONFIG_FILE)
SKIP = [prayer for prayer in PRAYERS if prayer not in CONFIG.prayers]
# get current timezone
tz = tzlocal.get_localzone()


def get_coordinates(address: str):
    nom = Nominatim(user_agent="myprayer")
    location = nom.geocode(address)

    return location.latitude, location.longitude  # type: ignore


@app.command(name="list", help="List prayer times.")
def list_prayers(
    city: str = typer.Option(
        None,
        "--city",
        "-c",
        help="City name.",
        show_default=False,
    ),
    country: str = typer.Option(
        None,
        "--country",
        "-C",
        help="Country name.",
        show_default=False,
    ),
    address: str = typer.Option(
        None,
        "--address",
        "-a",
        help="Address.",
        show_default=False,
    ),
    latitude: float = typer.Option(
        CONFIG.location.latitude if CONFIG.location.latitude else None,
        "--latitude",
        "-lat",
        help="Latitude.",
        show_default=True,
    ),
    longitude: float = typer.Option(
        CONFIG.location.longitude if CONFIG.location.longitude else None,
        "--longitude",
        "-lon",
        help="Longitude.",
        show_default=True,
    ),
    day: int = typer.Option(
        None,
        "--day",
        "-d",
        min=1,
        max=31,
        help="Day (1-31)",
        show_default="Current day",  # type: ignore
    ),
    month: int = typer.Option(
        None,
        "--month",
        "-m",
        min=1,
        max=12,
        help="Month",
        show_default="Current month",  # type: ignore
    ),
    year: int = typer.Option(
        None,
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
        min=0,
        max=CalculationMethod.__len__() - 1,
    ),
    time_format: TimeFormat = typer.Option(
        CONFIG.time_format,
        "--time-format",
        "-t",
        help="Time format.",
        show_default=f"{TimeFormat(CONFIG.time_format).value}",  # type: ignore
    ),
    out_type: OutType = typer.Option(
        CONFIG.out_type,
        "--output",
        "-o",
        help="Output type.",
        show_default=f"{OutType(CONFIG.out_type).value}",  # type: ignore
    ),
    next: bool = typer.Option(
        CONFIG.next,
        "--next",
        "-n",
        help="Show next prayer, has no effect if day, month, or year are given.",
    ),
):
    if CONFIG.is_error:
        typer.echo(message=f"[ERROR] {CONFIG.error}", err=True)
        exit(1)

    # client = get_client(city, country, address, latitude, longitude, method, force)

    if city and country:
        latitude, longitude = get_coordinates(f"{city}, {country}")
    elif address:
        latitude, longitude = get_coordinates(address)
    elif latitude and longitude:
        pass
    else:
        latitude, longitude = CONFIG.location.latitude, CONFIG.location.longitude

    today = datetime.today().replace(tzinfo=tz)
    day = day or today.day
    month = month or today.month
    year = year or today.year
    date = datetime(year, month, day)
    # day_data = client.get_day(day, month, year)

    day_data = Day(latitude, longitude, CalculationMethod(method), date, SKIP)

    if date.date() == datetime.now(tz).date():
        if day_data.has_passed():
            day_data.next()
    else:
        next = False

    output = DayOutput(day_data, time_format, next)

    if out_type == OutType.table:
        rprint(output.table())
    elif out_type == OutType.pretty:
        rprint(output.pretty())
    elif out_type == OutType.machine:
        print(output.machine())
    elif out_type == OutType.json:
        print(json.dumps(output.json(), indent=4))


@app.command(name="next", help="Show next prayer.")
def next(
    city: str = typer.Option(
        None,
        "--city",
        "-c",
        help="City name.",
        show_default=False,
    ),
    country: str = typer.Option(
        None,
        "--country",
        "-C",
        help="Country name.",
        show_default=False,
    ),
    address: str = typer.Option(
        None,
        "--address",
        "-a",
        help="Address.",
        show_default=False,
    ),
    latitude: float = typer.Option(
        CONFIG.location.latitude if CONFIG.location.latitude else None,
        "--latitude",
        "-lat",
        help="Latitude.",
        show_default=True,
    ),
    longitude: float = typer.Option(
        CONFIG.location.longitude if CONFIG.location.longitude else None,
        "--longitude",
        "-lon",
        help="Longitude.",
        show_default=True,
    ),
    method: int = typer.Option(
        CONFIG.method,
        "--method",
        "-M",
        help="Calculation method.",
        min=0,
        max=CalculationMethod.__len__() - 1,
    ),
    out_type: NextOutType = typer.Option(
        CONFIG.out_type,
        "--output",
        "-o",
        help="Output type.",
        show_default=f"{NextOutType(CONFIG.out_type).value}",  # type: ignore
    ),
):
    if CONFIG.is_error:
        typer.echo(message=f"[ERROR] {CONFIG.error}", err=True)
        exit(1)

    if city and country:
        latitude, longitude = get_coordinates(f"{city}, {country}")
    elif address:
        latitude, longitude = get_coordinates(address)
    elif latitude and longitude:
        pass
    else:
        latitude, longitude = CONFIG.location.latitude, CONFIG.location.longitude

    today = datetime.now(tz)
    # day_data = client.get_day(day, month, year)
    day_data = Day(latitude, longitude, CalculationMethod(method), today, SKIP)

    if day_data.has_passed():
        day_data.next()

    next_prayer = day_data.get_next_prayer()

    if next_prayer is not None:
        time_left = format_time_left(next_prayer.time_left(), out_type)  # type: ignore
        if out_type == OutType.table:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Prayer")
            table.add_column("Time Left")
            table.add_row(next_prayer.name, time_left, style="bold")
            rprint(table)
        elif out_type == OutType.pretty:
            rprint(f"[bold cyan]{next_prayer.name}:[/bold cyan] {time_left}")
        elif out_type == OutType.machine:
            print(f"{next_prayer.name},{time_left}")
        elif out_type == OutType.json:
            out_json = {
                "next": next_prayer.name,
                "time_left": time_left,
            }
            print(json.dumps(out_json, indent=4))
        elif out_type == NextOutType.waybar:
            tooltip_date = day_data.date.strftime("%A, %B %d")
            tooltip_data = "\n".join(
                [
                    f"{prayer.name}: {prayer.time.strftime(TIME_FORMATS[CONFIG.time_format])}"
                    for prayer in day_data.prayers
                ]
            )
            tooltip = f"{tooltip_date}\n\n{tooltip_data}"

            out_json = {
                "text": f"{time_left}",
                "tooltip": tooltip,
                "class": next_prayer.name.lower(),
                "alt": f"{next_prayer.name}: {time_left}",
            }

            print(json.dumps(out_json, indent=4))


@app.command(name="config", help="Configure myprayer.")
def config():
    # Prompt for city
    loc_type_question = [
        inquirer.List(
            "type",
            message="Select a location type:",
            choices=LOCATION_TYPES,
            default=type(CONFIG.location).__name__,  # type: ignore
        ),
    ]
    loc_type_choice = inquirer.prompt(loc_type_question)
    loc_type: str = loc_type_choice["type"]  # type: ignore

    latitude = 30
    longitude = 31
    if loc_type == "City":
        city: str = Prompt.ask(
            "City",
        )
        country: str = Prompt.ask(
            "Country",
        )
        state: str = Prompt.ask(
            "State",
            default=None,  # type: ignore
        )
        location = f"{city}, {country}, {state}" if state else f"{city}, {country}"
        latitude, longitude = get_coordinates(location)

    elif loc_type == "Coordinates":
        latitude: float = FloatPrompt.ask(
            "Latitude",
            default=(
                CONFIG.location.latitude if CONFIG.location.latitude else None
            ),  # type: ignore
        )
        longitude: float = FloatPrompt.ask(
            "Longitude",
            default=(
                CONFIG.location.longitude if CONFIG.location.longitude else None
            ),  # type: ignore
        )

    elif loc_type == "Address":
        address: str = Prompt.ask(
            "Address",
        )
        latitude, longitude = get_coordinates(address)

    # city: str = Prompt.ask(
    #     "City",
    #     default=CONFIG.city,
    #     show_default=True if CONFIG.city else False,
    # )
    #
    # # Prompt for country
    # country: str = Prompt.ask(
    #     "Country",
    #     default=CONFIG.country,
    #     show_default=True if CONFIG.country else False,
    # )

    # Prompt for calculation method
    method_question = [
        inquirer.List(
            "method",
            message="Select a calculation method:",
            choices=CalculationMethod.__members__.keys(),
            default=utils.get_key(
                CalculationMethod.__members__, CalculationMethod(CONFIG.method)
            ),  # type: ignore
        ),
    ]

    method_choice = inquirer.prompt(method_question)

    if method_choice is None:
        raise typer.Abort()

    method: int = CalculationMethod[method_choice["method"]].value
    # Prompt for time format
    time_format: str = Prompt.ask(
        "Time format",
        choices=[TimeFormat.twelve, TimeFormat.twenty_four],
        default=TimeFormat.twelve.value,
    )

    # Prompt for print type
    print_type: str = Prompt.ask(
        "Output type",
        choices=[OutType.pretty, OutType.machine, OutType.table],
        default=OutType.table.value,
    )

    # Prompt for prayers to show

    prayers_question = [
        inquirer.Checkbox(
            "prayers",
            message="Select prayers to show:",
            choices=PRAYERS,
            default=CONFIG.prayers,
        ),
    ]
    prayers_choice = inquirer.prompt(prayers_question)
    prayers: list[str] = prayers_choice["prayers"]  # type: ignore

    # Prompt for next prayer option
    next = typer.confirm("Show next prayer?", default=True)

    CONFIG.update(
        location=Coordinates(latitude, longitude),
        time_format=TimeFormat(time_format),
        out_type=OutType(print_type),
        method=method,
        next=next,
        prayers=prayers,
    )
    CONFIG.save(CONFIG_FILE)

    rprint(f"[green]✔[/green] Configuration saved to {CONFIG_FILE}.")


def version_callback(value: bool):
    if value:
        print(f"{APP_NAME} {get_version(APP_NAME)}")
        raise typer.Exit()


def method_callback(value: bool):
    if value:
        for method in CalculationMethod:
            print(f"{method.value}: {method.name}")
        raise typer.Exit()


@app.callback()
def version(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit.",
    ),
    method: bool = typer.Option(
        None,
        "--method",
        "-M",
        callback=method_callback,
        help="Print the calculation methods and exit.",
    ),
):
    pass


if __name__ == "__main__":
    app()
