# SCP-079-REGEX

This project is used to manage regular expression rules adopted by other bots.

## How to use

See [this article](https://scp-079.org/regex/).

## Features

- Easy to use
- Can merge similar or mutually contained rules
- Search patterns
- Test patterns

## To Do List

- [x] Complete phrase management for a single group
- [x] Check the pattern before add
- [x] Choose the right way to store data
- [x] Interfacing with the whole project database
- [x] Search for patterns in more ways
- [x] Test patterns in a group
- [x] Simplified Chinese to Traditional Chinese
- [x] Copy the same pattern to other groups
- [x] Support the HIDE channel
- [x] Add more types

## Requirements

- Python 3.6 or higher.
- `requirements.txt` ： APScheduler OpenCC pyAesCrypt pyrogram[fast] xeger
- Ubuntu: `sudo apt update && sudo apt install opencc`

## Files

- plugins
    - functions
        - `channel.py` : Send messages to channel
        - `etc.py` : Miscellaneous
        - `file.py` : Save files
        - `filters.py` : Some filters
        - `telegram.py` : Some telegram functions
        - `tests.py` : Test functions
        - `timers.py` : Timer functions
        - `words.py` : Manage words
    - handlers
        - `callback.py` : Handle callbacks
        - `command.py` : Handle commands
        - `message.py`: Handle messages
    - `glovar.py` : Global variables
- `.gitignore` : Ignore
- `config.ini.example` -> `config.ini` : Configures
- `LICENSE` : GPLv3
- `main.py` : Start here
- `README.md` : This file
- `requirements.txt` : Managed by pip

## Contribute

Welcome to make this project even better. You can submit merge requests, or report issues.

## License

Licensed under the terms of the [GNU General Public License v3](LICENSE).
