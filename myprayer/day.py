import json
from calendar import month_name
from datetime import datetime, timedelta
from typing import Optional, Tuple

import typer
from rich import print
from rich.console import Console
from rich.table import Table

import myprayer.utils as utils
from myprayer.config import Config
from myprayer.constants import TIME_FORMATS
from myprayer.enums import OutType, TimeFormat


class Day:
    config: Config
    data: dict
    day: int
    date: datetime
    timings: dict[str, datetime]
    is_today: bool
    next_prayer: str
    time_for_next: Optional[timedelta]

    def __init__(self, config: Config, data: dict, day: Optional[int] = None):
        self.config: Config = config
        self.data: dict = data

        if not day:
            self.day = config.day
        else:
            self.day = day

        # print(f"Getting data for {day}/{month}/{year}")
        try:
            day_data = self.data[self.day - 1]
        except IndexError:
            print(f"{month_name[self.config.month]} is {len(self.data)} days.")
            raise typer.Exit(1)

        self.timings: dict[str, datetime] = {}
        timings = day_data["timings"]
        for prayer, time in timings.items():
            if prayer in config.prayers:
                self.timings[prayer] = datetime.strptime(
                    time[:5], TIME_FORMATS[TimeFormat.twenty_four]
                ).replace(day=self.day, month=self.config.month, year=self.config.year)

        self.date: datetime = datetime.strptime(
            (day_data["date"]["readable"]), "%d %b %Y"
        )

        self.is_today: bool = datetime.today().date() == self.date.date()
        if self.is_today:
            self.next_prayer, self.time_for_next = self.get_next()
        else:
            self.next_prayer: str = ""
            self.time_for_next = None

    def get_next(self) -> Tuple[str, timedelta | None]:
        now = datetime.now()
        for prayer, time in self.timings.items():
            if time > now:
                return prayer, time - now
        return "", None
        # self.timings["Fajr"] - now + timedelta(days=1)

    def is_next(self, prayer: str) -> bool:
        if (
            self.is_today
            and self.next_prayer
            and prayer == self.next_prayer
            and self.time_for_next is not None
        ):
            return True
        return False

    def out(self, print_type: Optional[OutType] = None) -> None:
        if not print_type:
            print_type = self.config.out_type
        if print_type == OutType.pretty:
            self.out_pretty()
        elif print_type == OutType.machine:
            self.out_machine()
        elif print_type == OutType.table:
            self.out_table()
        elif print_type == OutType.json:
            self.out_json()

    def out_pretty(self):
        for prayer, time in self.timings.items():
            formatted_time = time.strftime(TIME_FORMATS[self.config.time_format])
            if self.is_next(prayer):
                time_left = utils.format_time_left(self.time_for_next.seconds, self.config.out_type)  # type: ignore
                print(f"[bold cyan]{prayer}:[/bold cyan] {formatted_time}{time_left}")
            else:
                print(f"[bold]{prayer}:[/bold] {formatted_time}")

    def out_machine(self):
        for prayer, time in self.timings.items():
            formatted_time = time.strftime(
                TIME_FORMATS[self.config.time_format]
            ).replace(" ", "")
            if self.is_next(prayer):
                time_left = utils.format_time_left(self.time_for_next.seconds, self.config.out_type)  # type: ignore
                print(f"{prayer},{formatted_time},{time.date()},{time_left}")
                continue
            print(f"{prayer},{formatted_time},{time.date()}")

    def out_table(self):
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Prayer")
        table.add_column("Time")

        for prayer, time in self.timings.items():
            style = ""
            time_left = ""
            if self.is_next(prayer):
                style = "cyan"
                time_left = utils.format_time_left(self.time_for_next.seconds, self.config.out_type)  # type: ignore

            formatted_time = time.strftime(TIME_FORMATS[self.config.time_format])
            table.add_row(
                f"[bold]{prayer}{time_left}[/bold]", formatted_time, style=style
            )

        console.print(table)

    def out_json(self):
        out_json = {}
        out_json["date"] = self.date.strftime("%d %b %Y")
        timings = {
            prayer: time.strftime(TIME_FORMATS[self.config.time_format])
            for prayer, time in self.timings.items()
        }
        out_json["timings"] = timings

        if self.is_today:
            time_left = utils.format_time_left(
                self.time_for_next.seconds, self.config.out_type  # type: ignore
            )
            out_json["next"] = self.next_prayer
            out_json["time_left"] = time_left

        print(json.dumps(out_json, indent=4))

    def out_next(self):
        if self.is_today:
            time_left = utils.format_time_left(self.time_for_next.seconds, self.config.out_type)  # type: ignore
            match self.config.out_type:
                case OutType.pretty:
                    time_left = utils.format_time_left(self.time_for_next.seconds, "{hours}H {minutes}M")  # type: ignore
                    print(f"[bold cyan]{self.next_prayer}:[/bold cyan] {time_left}")
                case OutType.machine:
                    print(f"{self.next_prayer},{time_left}")
                case OutType.table:
                    console = Console()
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Prayer")
                    table.add_column("Time Left")
                    table.add_row(
                        f"[bold]{self.next_prayer}[/bold]",
                        time_left,
                    )
                    console.print(table)
                case OutType.json:
                    out_json = {}
                    out_json["next"] = self.next_prayer
                    out_json["time_left"] = time_left
                    print(json.dumps(out_json, indent=4))
        else:
            print("[red]Next prayer is not today.[/red]")
