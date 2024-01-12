from rich.table import Table

from myprayer.api.day import Day
from myprayer.cli.constants import TIME_FORMATS
from myprayer.cli.enums import OutType, TimeFormat
from myprayer.cli.utils import format_time_left


class DayOutput:
    day: Day
    time_format: TimeFormat
    show_next: bool

    def __init__(
        self, day: Day, time_format: TimeFormat, show_next: bool = False
    ) -> None:
        self.day = day
        self.show_next = show_next
        self.time_format = time_format

    def table(self) -> Table:
        # table = Table(show_header=True, header_style="bold", border_style="magenta")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Prayer")
        table.add_column("Time")

        for prayer in self.day.prayers:
            is_next = self.day.get_next_prayer() == prayer
            if self.show_next and is_next:
                time_until = format_time_left(prayer.time_left(), OutType.table)
                table.add_row(
                    f"{prayer.name} ({time_until})",
                    prayer.time.strftime(TIME_FORMATS[self.time_format]),
                    style="bold cyan",
                )
            else:
                table.add_row(
                    prayer.name,
                    prayer.time.strftime(TIME_FORMATS[self.time_format]),
                    style="bold",
                )

        return table

    def pretty(self) -> str:
        output = ""

        for i, prayer in enumerate(self.day.prayers):
            formatted_time = prayer.time.strftime(TIME_FORMATS[self.time_format])
            is_next = self.day.get_next_prayer() == prayer
            if self.show_next and is_next:
                if is_next:
                    time_left = format_time_left(prayer.time_left(), OutType.pretty)
                    output += f"[bold cyan]{prayer.name}:[/bold cyan] {formatted_time} ({time_left})"
            else:
                output += f"[bold]{prayer.name}: {formatted_time}[/bold]"
            if i != len(self.day.prayers) - 1:
                output += "\n"

        return output

    def machine(self) -> str:
        output = ""
        for i, prayer in enumerate(self.day.prayers):
            formatted_time = prayer.time.strftime(
                TIME_FORMATS[self.time_format]
            ).replace(" ", "")

            prayer_output = f"{prayer.name},{formatted_time},{prayer.time.date()}"

            if self.show_next:
                is_next = self.day.get_next_prayer() == prayer
                if is_next:
                    time_left = format_time_left(prayer.time_left(), OutType.machine)
                    prayer_output += f",{time_left}"

            output += prayer_output
            if i != len(self.day.prayers) - 1:
                output += "\n"
        return output

    def json(self) -> dict:
        out_json = {
            "date": self.day.date.strftime("%d %b %Y"),
            "timings": {
                prayer.name: prayer.time.strftime(TIME_FORMATS[self.time_format])
                for prayer in self.day.prayers
            },
        }
        next_prayer = self.day.get_next_prayer()
        if self.show_next and next_prayer is not None:
            time_left = format_time_left(next_prayer.time_left(), OutType.json)
            out_json["next"] = next_prayer.name
            out_json["time_left"] = time_left

        return out_json
