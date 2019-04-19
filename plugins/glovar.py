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
from configparser import ConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from typing import Dict, List, Union

from .functions.etc import random_str

# Enable logging
logger = logging.getLogger(__name__)

# Init
names: dict = {
    "ad": "广告用语",
    "avatar": "头像分析",
    "bad": "敏感检测",
    "ban": "自动封禁",
    "bio": "简介封禁",
    "contact": "联系方式",
    "delete": "自动删除",
    "emergency": "应急模式",
    "nick": "昵称封禁",
    "watch_bad": "追踪封禁",
    "watch_delete": "追踪删除",
    "sticker": "贴纸删除"
}
ask_words: Dict[str, Dict[str, Union[str, List]]] = {}

# Generate commands lists
list_commands: list = []
search_commands: list = []
add_commands: list = []
remove_commands: list = []

for operation in ["list", "search", "add", "remove"]:
    locals()[f"{operation}_commands"] = [f"{operation}_{word}" for word in names]

# Load data form pickle
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

avatar_words: set = set()
bad_words: set = set()
ban_words: set = set()
bio_words: set = set()
delete_words: set = set()
emergency_words: set = set()
nick_words: set = set()
watch_bad_words: set = set()
watch_delete_words: set = set()
sticker_words: set = set()

for word_type in names:
    locals()[f"{word_type}_words"] = {f"预留{names[f'{word_type}']}词组 {random_str(16)}"}

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

compiled: dict = {}
for word_type in names:
    compiled[word_type] = re.compile(f"预留{names[f'{word_type}']}词组 {random_str(16)}", re.I | re.M | re.S)

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
creator_id: int = 0
exchange_id: int = 0
main_group_id: int = 0
password: str = ""
per_page: int = 15
prefix: List[str] = []
prefix_str: str = "/!！"
reload_path: str = ""
token: str = ""
update_to: Union[str, list] = ""
update_type: str = "reload"

try:
    config = ConfigParser()
    config.read("config.ini")

    if "custom" in config:
        creator_id = int(config["custom"].get("creator_id", creator_id))
        exchange_id = int(config["custom"].get("exchange_id", exchange_id))
        main_group_id = int(config["custom"].get("main_group_id", main_group_id))
        password = config["custom"].get("password", password)
        per_page = int(config["custom"].get("per_page", per_page))
        prefix = list(config["custom"].get("prefix", prefix_str))
        reload_path = config["custom"].get("reload_path", reload_path)
        token = config["custom"].get("token", token)
        update_to = config["custom"].get("update_to", update_to)
        update_to = update_to.split(" ")
        update_type = config["custom"].get("update_type", update_type)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}")

if (creator_id == 0
        or exchange_id == 0
        or main_group_id == 0
        or password in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or token in {"", "[DATA EXPUNGED]"}
        or (update_type == "reload" and reload_path in {"", "[DATA EXPUNGED]"})):
    logger.critical("No proper settings")
    raise SystemExit('No proper settings')

copyright_text = ("SCP-079-REGEX v0.1.2, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
