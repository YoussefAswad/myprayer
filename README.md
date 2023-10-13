# MyPrayer

MyPrayer is a command line application for getting Islamic prayer times for a given location and date.

## Features

- Get prayer times for a specific date and location
- Show next upcoming prayer time
- Support from multiple calculation methods
- Output prayer times in different formats
- Save default location and settings

## Usage

```
myprayer list <city> <country> [options]   Show prayer times for a date
myprayer next <city> <country> [options]   Show next prayer time
myprayer config                          Configure default settings
```

### Options

```
-d, --day        Specify day of month (default: today)
-m, --month      Specify month number (default: current month)
-y, --year       Specify year (default: current year)
-M, --method     Calculation method (default: Muslim World League)
-t, --time-format  Output time format (default: 24h)
-o, --output     Output type (default: table)
-n, --next       Show next prayer time (no effect with date options)
-f, --force      Force refresh cache
```

## Dependencies

- Python 3.6+
- [Typer](https://github.com/tiangolo/typer) - CLI app framework
- [Inquirer.py](https://github.com/magmax/python-inquirer) - user prompts
- [Rich](https://github.com/willmcgugan/rich) - output formatting
- [Requests](https://docs.python-requests.org/en/latest/) - HTTP client
- [Prayer Times API](https://prayertimes.date) - for prayer time data

## Configuration

Default settings like location, calculation method, and output format can be configured in `~/.myprayer/config.json`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
