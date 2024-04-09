# MyPrayer

[![PyPI version](https://badge.fury.io/py/myprayer.svg)](https://badge.fury.io/py/myprayer)

MyPrayer is a command line application for getting Islamic prayer times for a given location and date.

## Features

- Get prayer times for a specific date and location
- Show next upcoming prayer time
- Support from multiple calculation methods
- Output prayer times in different formats
- Save default location and settings

## Dependencies

- Python 3.8+
- [Typer](https://github.com/tiangolo/typer) - CLI app framework
- [Inquirer.py](https://github.com/magmax/python-inquirer) - user prompts
- [Rich](https://github.com/willmcgugan/rich) - output formatting
- [Requests](https://docs.python-requests.org/en/latest/) - HTTP client
- [adhanpy](https://pypi.org/project/adhanpy/) - Prayer times calculation
- [geopy](https://geopy.readthedocs.io/en/stable/) - Geocoding library
- [tzlocal](https://pypi.org/project/tzlocal/) - Local timezone
- [pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [tzdata](https://pypi.org/project/tzdata/) - Timezone data

### Install

```bash
pip install myprayer
```


## Usage

### myprayer

```
Usage: myprayer [OPTIONS] COMMAND [ARGS]...                                                 

MyPrayer CLI.                                                                               

Options 
  --install-completion        [bash|zsh|fish|powershell|pwsh]   Install completion for the specified shell.              
                                                                [default: None]               
  --show-completion           [bash|zsh|fish|powershell|pwsh]   Show completion for the specified shell, to copy it or customize the installation.   
                                                                [default: None]               
  --help                                                        Show this message and exit.    

Commands
  config                   Configure myprayer.                                              
  list                     List prayer times.                                               
  next                     Show next prayer.  
```

### myparyer list

```
Usage: myprayer list [OPTIONS]                                                                                                                                                                 
List prayer times.                                                                                                                                                                             
Options 
 --city         -c        TEXT                         City name.                            
 --country      -C        TEXT                         Country name.                              
 --address      -a        TEXT                         Address.                               
 --latitude     -lat      FLOAT                        Latitude.                               
 --longitude    -lon      FLOAT                        Longitude. 
 --day          -d        INTEGER RANGE [1<=x<=31]     Day (1-31) [default: (Current day)]            
 --month        -m        INTEGER RANGE [1<=x<=12]     Month [default: (Current month)]                       
 --year         -y        INTEGER                      Year [default: (Current year)]                          
 --method       -M        INTEGER                      Calculation method. [default: (Egyptian General Authority of Survey)]         
 --time-format  -t        [12|24]                      Time format. [default: 12]       
 --output       -o        [pretty|machine|table|json]  Output type. [default: table]            
 --next         -n                                     Show next prayer, has no effect if day, month, or year are given. [default: True]         
 --force        -f                                     Force update cache.       
 --help                                                Show this message and exit.  
```

### myparyer next

```
Usage: myprayer next [OPTIONS]                                                                                                                                                                 
Show next prayer. 

Options 
 --city         -c        TEXT                         City name.                            
 --country      -C        TEXT                         Country name.                              
 --address      -a        TEXT                         Address.                               
 --latitude     -lat      FLOAT                        Latitude.                               
 --longitude    -lon      FLOAT                        Longitude. 
 --day          -d        INTEGER RANGE [1<=x<=31]     Day (1-31) [default: (Current day)]            
 --method       -M        INTEGER                      Calculation method. [default: (Egyptian General Authority of Survey)]         
 --time-format  -t        [12|24]                      Time format. [default: 12]       
 --output       -o        [pretty|machine|table|json]  Output type. [default: table]            
 --force        -f                                     Force update cache.       
 --help                                                Configure default settings
```


## Configuration

Default settings like location, calculation method, and output format can be configured in `$XDG_CONFIG_HOME/myprayer/config.json` or `$HOME/.config/myprayer/config.json` using `myprayer config`.

### Example configuration

```jsonc
{
    "time_format": "12", // 12 or 24
    "print_type": "table", // pretty, machine, table, json
    "method": 5, // Calculation method
    "show_next": true, // Highlight next prayer in list
    "prayers": [ // Prayer to show
        "Fajr",
        "Dhuhr",
        "Asr",
        "Maghrib",
        "Isha"
    ],
    "location": { // Default location used if no location is provided in command
        "latitude": 30,
        "longitude": 31,
    }
}
```


## Credits
- [adhanpy](https://pypi.org/project/adhanpy/) - Prayer times calculation


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
