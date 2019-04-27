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
import re
from configparser import RawConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from typing import Dict, List, Union

from .functions.etc import random_str

# Enable logging
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

names: dict = {
    "ad": "广告用语",
    "ava": "头像分析",
    "bad": "敏感检测",
    "ban": "自动封禁",
    "bio": "简介封禁",
    "con": "联系方式",
    "del": "自动删除",
    "eme": "应急模式",
    "nm": "名称封禁",
    "wb": "追踪封禁",
    "wd": "追踪删除",
    "sti": "贴纸删除",
    "test": "测试用例"
}

version = "0.2.1"

search_words: Dict[str, Dict[str, Union[str, Dict[str, List[str]]]]] = {}
# search_words = {
#     "random": {
#         "result": {
#             "regex1": ["type1", "type2"]
#         },
#         "type": "type",
#         "word": "regex"
#     }
# }

# Generate commands lists
add_commands: list = ["add", "ad"]
list_commands: list = ["list", "ls"]
remove_commands: list = ["remove", "rm"]
same_commands: list = ["same", "copy", "c"]
search_commands: list = ["search", "s", "find"]
all_commands: list = add_commands + list_commands + remove_commands + same_commands + search_commands \
                     + ["ban",
                        "forgive",
                        "version",
                        "warn"]

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
ad_words: set = set()
ava_words: set = set()
bad_words: set = set()
ban_words: set = set()
bio_words: set = set()
con_words: set = set()
del_words: set = set()
eme_words: set = set()
nm_words: set = set()
wb_words: set = set()
wd_words: set = set()
sti_words: set = set()
test_words: set = set()
# type_words = {"regex1", "regex2"}

for word_type in names:
    locals()[f"{word_type}_words"] = {f"预留{names[f'{word_type}']}词组 {random_str(16)}"}

# Load words data
for word_type in names:
    try:
        try:
            if exists(f"data/{word_type}_words") or exists(f"data/.{word_type}_words"):
                with open(f"data/{word_type}_words", 'rb') as f:
                    locals()[f"{word_type}_words"] = pickle.load(f)
            else:
                with open(f"data/{word_type}_words", 'wb') as f:
                    pickle.dump(eval(f"{word_type}_words"), f)
        except Exception as e:
            logger.error(f"Load data {word_type}_words error: {e}")
            with open(f"data/.{word_type}_words", 'rb') as f:
                locals()[f"{word_type}_words"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {word_type}_words backup error: {e}", exc_info=True)
        raise SystemExit("[DATA CORRUPTION]")

# Init compiled variable
compiled: dict = {}
# pattern = "|".join(type_words)
# compiled = {
#     "type": re.compile(pattern, re.I | re.M | re.S)
# }

for word_type in names:
    compiled[word_type] = re.compile(fr"预留{names[f'{word_type}']}词组 {random_str(16)}", re.I | re.M | re.S)

# Load compiled data
try:
    try:
        if exists("data/compiled") or exists("data/.compiled"):
            with open(f"data/compiled", 'rb') as f:
                locals()[f"compiled"] = pickle.load(f)
        else:
            with open(f"data/compiled", 'wb') as f:
                pickle.dump(eval(f"compiled"), f)
    except Exception as e:
        logger.error(f"Load data compiled error: {e}")
        with open(f"data/.compiled", 'rb') as f:
            locals()[f"compiled"] = pickle.load(f)
except Exception as e:
    logger.critical(f"Load data compiled backup error: {e}", exc_info=True)
    raise SystemExit("[DATA CORRUPTION]")

# Read data from config.ini

# [basic]
bot_token: str = ""
prefix: List[str] = []
prefix_str: str = "/!"

# [channels]
exchange_channel_id: int = 0
regex_group_id: int = 0
test_group_id: int = 0

# [custom]
per_page: int = 15
reload_path: str = ""
update_to: Union[str, list] = ""
update_type: str = "reload"

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
    exchange_channel_id = int(config["channels"].get("exchange_channel_id", exchange_channel_id))
    test_group_id = int(config["channels"].get("test_group_id", test_group_id))
    regex_group_id = int(config["channels"].get("regex_group_id", regex_group_id))
    # [custom]
    per_page = int(config["custom"].get("per_page", per_page))
    reload_path = config["custom"].get("reload_path", reload_path)
    update_to = config["custom"].get("update_to", update_to)
    update_to = update_to.split(" ")
    update_type = config["custom"].get("update_type", update_type)
    # [encrypt]
    key = config["encrypt"].get("key", key)
    key = key.encode("utf-8")
    password = config["encrypt"].get("password", password)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}", exc_info=True)

# Check
if (bot_token in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or exchange_channel_id == 0
        or test_group_id == 0
        or regex_group_id == 0
        or (update_type == "reload" and reload_path in {"", "[DATA EXPUNGED]"})
        or key in {"", b"[DATA EXPUNGED]"}
        or password in {"", "[DATA EXPUNGED]"}):
    logger.critical("No proper settings")
    raise SystemExit('No proper settings')

# Start program
copyright_text = (f"SCP-079-REGEX v{version}, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
