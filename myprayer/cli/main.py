#!/usr/bin/env python

import json
from datetime import datetime

import inquirer
import typer
from rich import print as rprint
from rich.prompt import FloatPrompt, Prompt
from rich.table import Table

from myprayer.api.client import Client
from myprayer.api.location_types import Address, City, Coordinates
from myprayer.cli import utils
from myprayer.cli.config import Config
from myprayer.cli.constants import (
    APP_NAME,
    CACHE_DIR,
    CALCULATION_METHODS,
    CONFIG_FILE,
    LOCATION_TYPES,
    PRAYERS,
    TIME_FORMATS,
)
from myprayer.cli.enums import NextOutType, OutType, TimeFormat
from myprayer.cli.output import DayOutput
from myprayer.cli.utils import format_time_left

app = typer.Typer(name=APP_NAME, pretty_exceptions_enable=False, help="MyPrayer CLI.")


# Load config
CONFIG = Config(CONFIG_FILE)


def get_client(city, country, address, latitude, longitude, method, force):
    cache = None if force else CACHE_DIR
    skip = [prayer for prayer in PRAYERS if prayer not in CONFIG.prayers]

    location = None
    if not any([city, country, address, latitude, longitude]):
        if not CONFIG.location:
            typer.echo(message="No location given.", err=True)
            exit(1)
    else:
        if city and country:
            location = City(city, country)
        elif address:
            location = Address(address)
        elif latitude and longitude:
            location = Coordinates(latitude, longitude)
        else:
            typer.echo(message="Invalid location.", err=True)
            exit(1)

    # if no location is given, use the one from config
    location = location or CONFIG.location

    return Client(location, method, skip=skip, cache_dir=cache)


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
        None,
        "--latitude",
        "-lat",
        help="Latitude.",
        show_default=False,
    ),
    longitude: float = typer.Option(
        None,
        "--longitude",
        "-lon",
        help="Longitude.",
        show_default=False,
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
        show_default=f"{utils.get_key(CALCULATION_METHODS, CONFIG.method)}",  # type: ignore
    ),
    time_format: TimeFormat = typer.Option(
        CONFIG.time_format,
        "--time-format",
        "-t",
        help="Time format.",
    ),
    out_type: OutType = typer.Option(
        CONFIG.out_type,
        "--output",
        "-o",
        help="Output type.",
    ),
    next: bool = typer.Option(
        CONFIG.next,
        "--next",
        "-n",
        help="Show next prayer, has no effect if day, month, or year are given.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force update cache."),
):
    client = get_client(city, country, address, latitude, longitude, method, force)

    today = datetime.today()
    day = day or today.day
    month = month or today.month
    year = year or today.year
    day_data = client.get_day(day, month, year)

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
        None,
        "--latitude",
        "-lat",
        help="Latitude.",
        show_default=False,
    ),
    longitude: float = typer.Option(
        None,
        "--longitude",
        "-lon",
        help="Longitude.",
        show_default=False,
    ),
    method: int = typer.Option(
        CONFIG.method,
        "--method",
        "-M",
        help="Calculation method.",
        show_default=f"{utils.get_key(CALCULATION_METHODS, CONFIG.method)}",  # type: ignore
    ),
    out_type: NextOutType = typer.Option(
        CONFIG.out_type,
        "--output",
        "-o",
        help="Output type.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force update cache."),
):
    client = get_client(city, country, address, latitude, longitude, method, force)

    next_prayer = client.get_next_prayer()

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
            day_data = client.get_day(
                next_prayer.time.day, next_prayer.time.month, next_prayer.time.year
            )

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

    location = None
    if loc_type == "City":
        city: str = Prompt.ask(
            "City",
            default=CONFIG.location.city
            if isinstance(CONFIG.location, City)
            else None,  # type: ignore
        )
        country: str = Prompt.ask(
            "Country",
            default=CONFIG.location.country
            if isinstance(CONFIG.location, City)
            else None,  # type: ignore
        )
        state: str = Prompt.ask(
            "State",
            default=CONFIG.location.state
            if isinstance(CONFIG.location, City)
            else None,  # type: ignore
        )
        location = City(city, country, state)

    elif loc_type == "Coordinates":
        latitude: float = FloatPrompt.ask(
            "Latitude",
            default=CONFIG.location.latitude
            if isinstance(CONFIG.location, Coordinates)
            else None,  # type: ignore
        )
        longitude: float = FloatPrompt.ask(
            "Longitude",
            default=CONFIG.location.longitude
            if isinstance(CONFIG.location, Coordinates)
            else None,  # type: ignore
        )
        location = Coordinates(latitude, longitude)

    elif loc_type == "Address":
        address: str = Prompt.ask(
            "Address",
            default=CONFIG.location.address
            if isinstance(CONFIG.location, Address)
            else None,  # type: ignore
        )
        location = Address(address)

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
            choices=CALCULATION_METHODS,
            default=utils.get_key(CALCULATION_METHODS, CONFIG.method),  # type: ignore
        ),
    ]
    method_choice = inquirer.prompt(method_question)
    method: int = CALCULATION_METHODS[method_choice["method"]]  # type: ignore

    # Prompt for time format
    time_format: str = Prompt.ask(
        "Time format",
        choices=[TimeFormat.twelve, TimeFormat.twenty_four],
        default=TimeFormat.twelve,
    )

    # Prompt for print type
    print_type: str = Prompt.ask(
        "Output type",
        choices=[OutType.pretty, OutType.machine, OutType.table],
        default=OutType.table,
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
        location=location,
        time_format=TimeFormat(time_format),
        out_type=OutType(print_type),
        method=method,
        next=next,
        prayers=prayers,
    )
    CONFIG.save(CONFIG_FILE)

    rprint(f"[green]✔[/green] Configuration saved to {CONFIG_FILE}.")


if __name__ == "__main__":
    app()
