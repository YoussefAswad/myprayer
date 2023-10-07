#!/usr/bin/env python

import json
from calendar import monthrange
from datetime import datetime

import inquirer
import typer
from rich import print as rprint
from rich.prompt import Prompt

from myprayer import utils
from myprayer.config import Config
from myprayer.constants import (
    APP_NAME,
    CALCULATION_METHODS,
    CONFIG_FILE,
    PRAYER_NAMES,
    TIME_FORMATS,
)
from myprayer.day import Day
from myprayer.enums import OutType, TimeFormat
from myprayer.month import Month

app = typer.Typer(name=APP_NAME, pretty_exceptions_enable=False)


# Load config
CONFIG = Config(CONFIG_FILE)


# get the day for the next prayer
def get_next_day(force: bool) -> Day:
    day_data = Month(CONFIG, force).get_day()
    if day_data.has_passed(CONFIG.prayers[-1]):
        # if the next prayer is in the next day, get the next day
        if CONFIG.day in range(1, monthrange(CONFIG.year, CONFIG.month)[1] + 1):
            CONFIG.day += 1
            day_data = Month(CONFIG, force).get_day()
        # if the next prayer is in the next month, get the next month
        else:
            CONFIG.day = 1
            # if the next prayer is in the next year, get the next year
            if CONFIG.month == 12:
                CONFIG.month = 1
                CONFIG.year += 1
            else:
                CONFIG.month += 1
            day_data = Month(CONFIG, force).get_day()
    return day_data


@app.command(name="list", help="List prayer times.")
def list_prayers(
    city: str = typer.Argument(CONFIG.city, help="City name."),
    country: str = typer.Argument(CONFIG.country, help="Country name."),
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
        CONFIG.time_format, "--time-format", "-t", help="Time format."
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
    # Update config with command line arguments
    CONFIG.update(
        city=city,
        country=country,
        day=day or datetime.now().day,
        month=month or datetime.now().month,
        year=year or datetime.now().year,
        time_format=time_format,
        method=method,
        out_type=out_type,
        next=next,
    )

    if not city or not country:
        rprint(
            "[red]Please provide a city and country, or run config to set the defaults.[/red]"
        )
        raise typer.Exit(1)

    if not day and not month and not year:
        day_data = get_next_day(force)

    else:
        CONFIG.next = False
        day_data = Month(CONFIG, force).get_day()

    day_data.out()


@app.command(name="next", help="Show next prayer.")
def next(
    city: str = typer.Argument(CONFIG.city, help="City name."),
    country: str = typer.Argument(CONFIG.country, help="Country name."),
    method: int = typer.Option(
        CONFIG.method,
        "--method",
        "-M",
        help="Calculation method.",
        show_default=f"{utils.get_key(CALCULATION_METHODS, CONFIG.method)}",  # type: ignore
    ),
    time_format: TimeFormat = typer.Option(
        CONFIG.time_format, "--time-format", "-t", help="Time format."
    ),
    out_type: OutType = typer.Option(
        CONFIG.out_type,
        "--output",
        "-o",
        help="Output type.",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force update cache."),
):
    # Update config with command line arguments
    CONFIG.update(
        city=city,
        country=country,
        time_format=time_format,
        method=method,
        out_type=out_type,
    )

    day_data = get_next_day(force)
    day_data.out_next()


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

    # Prompt for time format
    time_format: str = Prompt.ask(
        "Time format",
        choices=[TimeFormat.twelve, TimeFormat.twenty_four],
        default=TimeFormat.twelve,
    )

    # Prompt for print type
    print_type: str = Prompt.ask(
        "Print type",
        choices=[OutType.pretty, OutType.machine, OutType.table],
        default=OutType.table,
    )

    # Prompt for prayers to show

    prayers_question = [
        inquirer.Checkbox(
            "prayers",
            message="Select prayers to show:",
            choices=PRAYER_NAMES,
            default=CONFIG.prayers,
        ),
    ]
    prayers_choice = inquirer.prompt(prayers_question)
    prayers: list[str] = prayers_choice["prayers"]  # type: ignore

    # Prompt for next prayer option
    next = typer.confirm("Show next prayer?", default=True)

    CONFIG.update(
        city=city,
        country=country,
        time_format=TimeFormat(time_format),
        out_type=OutType(print_type),
        method=method,
        next=next,
        prayers=prayers,
    )
    CONFIG.save(CONFIG_FILE)

    rprint(f"[green]✔[/green] Configuration saved to {CONFIG_FILE}.")


@app.command(name="waybar", help="Print prayer times in json waybar format.")
def waybar():
    """Print prayer times in waybar format."""
    CONFIG.update(out_type=OutType.pretty)
    day_data = get_next_day(False)

    prayer_name, time_left = day_data.get_next()
    formatted_time_left = utils.format_time_left(time_left.seconds, "{hours}H {minutes}M")  # type: ignore

    json_output = {
        "text": f"{formatted_time_left}",
        "tooltip": "\n".join(
            [
                f"{prayer}: {time.strftime(TIME_FORMATS[CONFIG.time_format])}"
                for prayer, time in day_data.timings.items()
                if prayer in CONFIG.prayers
            ]
        ),
        "class": prayer_name.lower(),
        "alt": f"{prayer_name}: {formatted_time_left}",
    }

    print(json.dumps(json_output))


if __name__ == "__main__":
    app()
