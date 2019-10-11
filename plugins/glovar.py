# SCP-079-REGEX - Manage the regex patterns
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-REGEX.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import pickle
from configparser import RawConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from threading import Lock
from time import time
from typing import Dict, List, Union

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename='log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Init

ask_words: Dict[str, Dict[str, Union[str, List]]] = {}
# ask_words = {
#     "random": {
#         "new": "regex",
#         "old": ["regex1", "regex2"],
#         "type": "type"
#     }
# }

default_word_status: Dict[str, Union[float, int]] = {
    "time": int(time()),
    "average": 0.0,
    "today": 0,
    "total": 0
}

locks: Dict[str, Lock] = {
    "regex": Lock(),
    "test": Lock()
}

names: Dict[str, str] = {
    "ad": "广告用语",
    "aff": "推广链接",
    "ava": "头像分析",
    "bad": "敏感检测",
    "ban": "自动封禁",
    "bio": "简介封禁",
    "con": "联系方式",
    "del": "自动删除",
    "iml": "IM 链接",
    "nm": "名称封禁",
    "rm": "RM 笑话",
    "sho": "短链接",
    "spc": "特殊中文",
    "spe": "特殊英文",
    "sti": "贴纸删除",
    "tgl": "TG 链接",
    "tgp": "TG 代理",
    "wb": "追踪封禁",
    "wd": "追踪删除",
    "test": "测试用例"
}

receivers: Dict[str, List[str]] = {
    "ad": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "aff": ["CLEAN", "WATCH"],
    "ava": ["NOSPAM"],
    "bad": ["NOSPAM"],
    "ban": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "bio": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "con": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "del": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "iml": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "nm": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "rm": ["TIP"],
    "sho": ["CLEAN", "NOSPAM", "WATCH"],
    "spc": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "spe": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "sti": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "tgl": ["CLEAN", "NOPORN", "NOSPAM", "WATCH"],
    "tgp": ["CLEAN", "WATCH"],
    "wb": ["CAPTCHA", "CLEAN", "LONG", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "wd": ["NOSPAM", "WATCH"],
    "test": []
}

result_search: Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]] = {}
# result_search = {
#     "random": {
#         "result": {
#             "regex1": ["type1", "type2"]
#         },
#         "type": "type",
#         "word": "regex"
#     }
# }

sender: str = "REGEX"

should_hide: bool = False

version: str = "0.3.6"

# Generate commands lists
add_commands: list = ["add", "ad"]
list_commands: list = ["list", "ls"]
remove_commands: list = ["remove", "rm"]
same_commands: list = ["same", "copy", "c"]
search_commands: list = ["search", "s", "find"]
all_commands: list = add_commands + list_commands + remove_commands + same_commands + search_commands + ["count",
                                                                                                         "l",
                                                                                                         "long",
                                                                                                         "print",
                                                                                                         "push",
                                                                                                         "reset",
                                                                                                         "t2s",
                                                                                                         "version",
                                                                                                         "mention"]

# Read data from config.ini

# [basic]
bot_token: str = ""
prefix: List[str] = []
prefix_str: str = "/!"

# [channels]
critical_channel_id: int = 0
debug_channel_id: int = 0
exchange_channel_id: int = 0
hide_channel_id: int = 0
regex_group_id: int = 0
test_group_id: int = 0

# [custom]
per_page: int = 0
project_link: str = ""
project_name: str = ""

# [encrypt]
key: Union[str, bytes] = ""
password: str = ""

try:
    config = RawConfigParser()
    config.read("config.ini")
    # [basic]
    bot_token = config["basic"].get("bot_token", bot_token)
    prefix = list(config["basic"].get("prefix", prefix_str))
    # [channels]
    critical_channel_id = int(config["channels"].get("critical_channel_id", critical_channel_id))
    debug_channel_id = int(config["channels"].get("debug_channel_id", debug_channel_id))
    exchange_channel_id = int(config["channels"].get("exchange_channel_id", exchange_channel_id))
    hide_channel_id = int(config["channels"].get("hide_channel_id", hide_channel_id))
    test_group_id = int(config["channels"].get("test_group_id", test_group_id))
    regex_group_id = int(config["channels"].get("regex_group_id", regex_group_id))
    # [custom]
    per_page = int(config["custom"].get("per_page", per_page))
    project_link = config["custom"].get("project_link", project_link)
    project_name = config["custom"].get("project_name", project_name)
    # [encrypt]
    key = config["encrypt"].get("key", key)
    key = key.encode("utf-8")
    password = config["encrypt"].get("password", password)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}", exc_info=True)

# Check
if (bot_token in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or critical_channel_id == 0
        or debug_channel_id == 0
        or exchange_channel_id == 0
        or hide_channel_id == 0
        or test_group_id == 0
        or regex_group_id == 0
        or project_link in {"", "[DATA EXPUNGED]"}
        or project_name in {"", "[DATA EXPUNGED]"}
        or key in {b"", b"[DATA EXPUNGED]"}
        or password in {"", "[DATA EXPUNGED]"}):
    logger.critical("No proper settings")
    raise SystemExit("No proper settings")

# Load data from pickle

# Init dir
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

# Init words variables
for word_type in names:
    locals()[f"{word_type}_words"]: Dict[str, Dict[str, Union[float, int]]] = {}

# type_words = {
#     "regex": {
#         "time": 15112345678,
#         "average": 1.1,
#         "today": 3,
#         "total": 20
#     }
# }

# Load data
file_list = [f"{word_type}_words" for word_type in names]
for file in file_list:
    try:
        try:
            if exists(f"data/{file}") or exists(f"data/.{file}"):
                with open(f"data/{file}", "rb") as f:
                    locals()[f"{file}"] = pickle.load(f)
            else:
                with open(f"data/{file}", "wb") as f:
                    pickle.dump(eval(f"{file}"), f)
        except Exception as e:
            logger.error(f"Load data {file} error: {e}", exc_info=True)
            with open(f"data/.{file}", "rb") as f:
                locals()[f"{file}"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {file} backup error: {e}", exc_info=True)
        raise SystemExit("[DATA CORRUPTION]")

# Start program
copyright_text = (f"SCP-079-{sender} v{version}, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
