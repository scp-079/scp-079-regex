# SCP-079-REGEX

This project is used to manage regular expression rules adopted by other bots.

## How to use

- See [this article](https://scp-079.org/regex/) to build a bot by yourself
- [README](https://github.com/scp-079/scp-079-readme) of the SCP-079 Project
- Discuss [group](https://t.me/SCP_079_CHAT)

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
- [x] Follow the hard core interaction principle

## Requirements

- Python 3.6 or higher.
- Debian 10: `sudo apt update && sudo apt install opencc -y`
- pip: `pip install -r requirements.txt` or `pip install -U APScheduler OpenCC pyAesCrypt pyrogram[fast] xeger`


## Files

- plugins
    - functions
        - `channel.py` : Functions about channel
        - `etc.py` : Miscellaneous
        - `file.py` : Save files
        - `filters.py` : Some filters
        - `receive.py` : Receive data from exchange channel
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
- `config.ini.example` -> `config.ini` : Configuration
- `LICENSE` : GPLv3
- `main.py` : Start here
- `README.md` : This file
- `requirements.txt` : Managed by pip

## Contribute

Welcome to make this project even better. You can submit merge requests, or report issues.

## License

Licensed under the terms of the [GNU General Public License v3](LICENSE).
