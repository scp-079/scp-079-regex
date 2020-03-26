# SCP-079-REGEX - Manage the regex patterns
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
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
from string import ascii_lowercase
from threading import Lock
from time import time
from typing import Dict, List, Set, Union

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
    filename="log",
    filemode="w"
)
logger = logging.getLogger(__name__)

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
aio: Union[bool, str] = ""
backup: Union[bool, str] = ""
date_reset: str = ""
limit_temp: int = 0
per_page: int = 0
project_link: str = ""
project_name: str = ""
zh_cn: Union[bool, str] = ""

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
    aio = config["custom"].get("aio", aio)
    aio = eval(aio)
    backup = config["custom"].get("backup", backup)
    backup = eval(backup)
    date_reset = config["custom"].get("date_reset", date_reset)
    limit_temp = int(config["custom"].get("limit_temp", limit_temp))
    per_page = int(config["custom"].get("per_page", per_page))
    project_link = config["custom"].get("project_link", project_link)
    project_name = config["custom"].get("project_name", project_name)
    zh_cn = config["custom"].get("zh_cn", zh_cn)
    zh_cn = eval(zh_cn)

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
        or aio not in {False, True}
        or backup not in {False, True}
        or date_reset in {"", "[DATA EXPUNGED]"}
        or limit_temp == 0
        or per_page == 0
        or project_link in {"", "[DATA EXPUNGED]"}
        or project_name in {"", "[DATA EXPUNGED]"}
        or zh_cn not in {False, True}
        or key in {b"", b"[DATA EXPUNGED]", "", "[DATA EXPUNGED]"}
        or password in {"", "[DATA EXPUNGED]"}):
    logger.critical("No proper settings")
    raise SystemExit("No proper settings")

# Languages
lang: Dict[str, str] = {
    # Admin
    "admin": (zh_cn and "管理员") or "Admin",
    "admin_group": (zh_cn and "群管理") or "Group Admin",
    "admin_project": (zh_cn and "项目管理员") or "Project Admin",
    # Basic
    "action": (zh_cn and "执行操作") or "Action",
    "action_page": (zh_cn and "翻页") or "Change Page",
    "colon": (zh_cn and "：") or ": ",
    "comma": (zh_cn and "，") or ", ",
    "error": (zh_cn and "错误") or "Error",
    "page": (zh_cn and "第 {} 页") or "Page {}",
    "reason": (zh_cn and "原因") or "Reason",
    "reset": (zh_cn and "重置数据") or "Reset Data",
    "result": (zh_cn and "结果") or "Result",
    "rollback": (zh_cn and "数据回滚") or "Rollback",
    "see": (zh_cn and "查看") or "See",
    "status_error": (zh_cn and "出现错误") or "Error Occurred",
    "status_failed": (zh_cn and "未执行") or "Failed",
    "status_succeeded": (zh_cn and "成功执行") or "Succeeded",
    "version": (zh_cn and "版本") or "Version",
    # Command
    "command_lack": (zh_cn and "命令参数缺失") or "Lack of Parameter",
    "command_para": (zh_cn and "命令参数有误") or "Incorrect Command Parameter",
    "command_permission": (zh_cn and "权限有误") or "Permission Error",
    "command_reply": (zh_cn and "来源有误") or "Reply to Message Error",
    "command_type": (zh_cn and "命令类别有误") or "Incorrect Command Type",
    "command_usage": (zh_cn and "用法有误") or "Incorrect Usage",
    # Emergency
    "issue": (zh_cn and "发现状况") or "Issue",
    "exchange_invalid": (zh_cn and "数据交换频道失效") or "Exchange Channel Invalid",
    "auto_fix": (zh_cn and "自动处理") or "Auto Fix",
    "protocol_1": (zh_cn and "启动 1 号协议") or "Initiate Protocol 1",
    "transfer_channel": (zh_cn and "频道转移") or "Transfer Channel",
    "emergency_channel": (zh_cn and "应急频道") or "Emergency Channel",
    # Group
    "reason_none": (zh_cn and "无数据") or "No Data",
    # Record
    "project": (zh_cn and "项目编号") or "Project",
    "project_origin": (zh_cn and "原始项目") or "Original Project",
    "status": (zh_cn and "状态") or "Status",
    "user_id": (zh_cn and "用户 ID") or "User ID",
    "level": (zh_cn and "操作等级") or "Level",
    "rule": (zh_cn and "规则") or "Rule",
    "message_type": (zh_cn and "消息类别") or "Message Type",
    "message_game": (zh_cn and "游戏标识") or "Game Short Name",
    "message_lang": (zh_cn and "消息语言") or "Message Language",
    "message_len": (zh_cn and "消息长度") or "Message Length",
    "message_freq": (zh_cn and "消息频率") or "Message Frequency",
    "user_score": (zh_cn and "用户得分") or "User Score",
    "user_bio": (zh_cn and "用户简介") or "User Bio",
    "user_name": (zh_cn and "用户昵称") or "User Name",
    "from_name": (zh_cn and "来源名称") or "Forward Name",
    "contact": (zh_cn and "联系方式") or "Contact Info",
    "more": (zh_cn and "附加信息") or "Extra Info",
    # Regex
    "ad": (zh_cn and "广告用语") or "Ad",
    "ava": (zh_cn and "头像分析") or "Avatar",
    "bad": (zh_cn and "敏感检测") or "Bad",
    "ban": (zh_cn and "自动封禁") or "Ban",
    "bio": (zh_cn and "简介检查") or "Bio",
    "con": (zh_cn and "联系方式") or "Contact",
    "del": (zh_cn and "自动删除") or "Delete",
    "fil": (zh_cn and "文件名称") or "Filename",
    "iml": (zh_cn and "IM 链接") or "IM Link",
    "pho": (zh_cn and "电话号码") or "Phone Number",
    "rm": (zh_cn and "RM 笑话") or "RM Joke",
    "nm": (zh_cn and "名称封禁") or "Name",
    "sho": (zh_cn and "短链接") or "Short Link",
    "spc": (zh_cn and "特殊中文") or "Special Chinese",
    "spe": (zh_cn and "特殊英文") or "Special English",
    "sti": (zh_cn and "贴纸删除") or "Sticker",
    "tgl": (zh_cn and "TG 链接") or "TG Link",
    "tgp": (zh_cn and "TG 代理") or "TG Proxy",
    "wb": (zh_cn and "追踪封禁") or "Watch Ban",
    "wd": (zh_cn and "追踪删除") or "Watch Delete",
    "test": (zh_cn and "测试用例") or "Test",
    "ad_": (zh_cn and "广告 {} 组") or "Ad {}",
    # Special
    "action_add": (zh_cn and "添加规则") or "Add Rule",
    "action_cancel": (zh_cn and "取消添加") or "Cancel Add",
    "action_captcha": (zh_cn and "验证未通过数据") or "CAPTCHA Failure Data",
    "action_captcha_request": (zh_cn and "查询验证未通过数据") or "Request CAPTCHA Failure Data",
    "action_cc": (zh_cn and "抄送") or "CC",
    "action_check": (zh_cn and "查询数据") or "Check the Count Data",
    "action_comment": (zh_cn and "添加备注") or "Add Comment",
    "action_count": (zh_cn and "请求统计") or "Request Statistics",
    "action_escape": (zh_cn and "转义字符") or "Escape",
    "action_list": (zh_cn and "查看列表") or "Show the List",
    "action_match": (zh_cn and "匹配结果") or "Show Match Result",
    "action_push": (zh_cn and "手动推送") or "Push Manually",
    "action_regex": (zh_cn and "手动测试") or "Test Manually",
    "action_remove": (zh_cn and "删除规则") or "Remove Rule",
    "action_remove_auto": (zh_cn and "自动移除") or "Auto Remove Rules",
    "action_reset": (zh_cn and "重置计数") or "Reset Count",
    "action_same": (zh_cn and "复制命令") or "Copy Command",
    "action_search": (zh_cn and "查询规则") or "Search Rules",
    "action_who": (zh_cn and "查询添加者") or "Find the Adder",
    "all": (zh_cn and "全部") or "All",
    "ask_new": (zh_cn and "另增新词") or "Add as New",
    "ask_replace": (zh_cn and "替换全部") or "Replace All",
    "cancel": (zh_cn and "取消") or "Cancel",
    "comment": (zh_cn and "备注") or "Comment",
    "duplicated": (zh_cn and "重复") or "Duplicated",
    "expired": (zh_cn and "会话已失效") or "Session Expired",
    "find": (zh_cn and "包含搜索") or "Include Search",
    "mode": (zh_cn and "模式") or "Mode",
    "order": (zh_cn and "顺序") or "Order",
    "order_asc": (zh_cn and "升序") or "Ascending",
    "order_desc": (zh_cn and "降序") or "Descending",
    "query": (zh_cn and "查询") or "Query",
    "reason_duplicated": (zh_cn and "跨类别重复") or "Duplicated",
    "reason_existed": (zh_cn and "已存在") or "Existed",
    "reason_not_exist": (zh_cn and "不存在") or "Does Not Exist",
    "reason_not_found": (zh_cn and "没有找到") or "Not Found",
    "reason_not_specific": (zh_cn and "不具有特殊性") or "Not specific",
    "reason_wait": (zh_cn and "等待确认") or "Wait for Confirmation",
    "removed": (zh_cn and "移除") or "Removed",
    "replaced": (zh_cn and "替换") or "Replaced",
    "s": (zh_cn and "宽松搜索") or "Loose Search",
    "search": (zh_cn and "正则搜索") or "REGEX Search",
    "t2t": (zh_cn and "文字转换") or "Text Transfer",
    "type": (zh_cn and "类别") or "Type",
    "unknown": (zh_cn and "未知") or "Unknown",
    "valid_types": (zh_cn and "可选类别") or "Valid Types",
    "word": (zh_cn and "词组") or "Word",
    # Test
    "message_print": (zh_cn and "消息结构") or "Print the Message",
    "sticker_name": (zh_cn and "贴纸名称") or "Sticker Name",
    "sticker_title": (zh_cn and "贴纸标题") or "Sticker Title",
    # Unit
    "rules": (zh_cn and "条") or "rule(s)"
}
for c in ascii_lowercase:
    lang[f"ad{c}"] = lang.get("ad_", "ad{}").format(c.upper())

# Init

add_commands: List[str] = ["ad", "add"]
list_commands: List[str] = ["list", "ls"]
remove_commands: List[str] = ["rm", "remove"]
same_commands: List[str] = ["copy", "same"]
search_commands: List[str] = ["find", "s", "search"]
all_commands: List[str] = add_commands + list_commands + remove_commands + same_commands + search_commands
all_commands += [
    "captcha",
    "check",
    "comment",
    "count",
    "escape",
    "findall",
    "group",
    "groupdict",
    "groups",
    "l",
    "long",
    "mention",
    "print",
    "push",
    "regex",
    "reset",
    "t2t",
    "version",
    "who"
]

contains: Dict[str, Set[str]] = {
    "con": {"iml", "pho"},
    "nm": {"bio"},
    "wb": {"ad", "ad_", "iml", "pho", "sho", "spc"},
    "wd": {"adi", "con", "spe", "tgp"}
}

default_word_status: Dict[str, Union[float, int]] = {
    "time": int(time()),
    "average": 0.0,
    "today": 0,
    "total": 0,
    "temp": 0,
    "who": 0
}

locks: Dict[str, Lock] = {
    "receive": Lock(),
    "regex": Lock(),
    "test": Lock()
}

receivers: Dict[str, List[str]] = {
    "ad": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "ava": ["NOSPAM"],
    "bad": ["NOSPAM"],
    "ban": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "bio": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "con": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "del": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "fil": ["CLEAN", "LANG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "iml": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "pho": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "nm": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "rm": ["TIP"],
    "sho": ["CAPTCHA", "CLEAN", "LONG", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "spc": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "spe": ["AVATAR", "CAPTCHA", "CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "sti": ["CLEAN", "LANG", "LONG", "NOPORN", "NOSPAM", "RECHECK", "WATCH"],
    "tgl": ["CLEAN", "NOPORN", "NOSPAM", "WATCH"],
    "tgp": ["CLEAN", "WATCH"],
    "wb": ["CAPTCHA", "CLEAN", "LONG", "NOFLOOD", "NOPORN", "NOSPAM", "RECHECK", "TIP", "WATCH"],
    "wd": ["NOSPAM", "WATCH"],
    "test": []
}

for c in ascii_lowercase:
    receivers[f"ad{c}"] = receivers["ad"]

regex: Dict[str, bool] = {
    "ad": True,
    "ava": True,
    "bad": True,
    "ban": True,
    "bio": True,
    "con": True,
    "del": True,
    "fil": True,
    "iml": True,
    "pho": True,
    "nm": True,
    "rm": True,
    "sho": True,
    "spc": True,
    "spe": True,
    "sti": True,
    "tgl": True,
    "tgp": True,
    "wb": True,
    "wd": True,
    "test": False
}

for c in ascii_lowercase:
    regex[f"ad{c}"] = True

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

sticker_titles: Dict[str, str] = {}
# sticker_titles = {
#     "short_name": "sticker_title"
# }

version: str = "0.5.2"

# Load data from pickle

# Init dir
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

# Init data variables

ask_words: Dict[str, Dict[str, Union[bool, int, str, List[str]]]] = {}
# ask_words = {
#     "random": {
#         "lock": False,
#         "time": 1512345678,
#         "admin": 12345678,
#         "mid": 123,
#         "new": "regex",
#         "old": ["regex1", "regex2"],
#         "type": "type"
#     }
# }

comments: Dict[str, str] = {}
# comments = {
#     "ada": "ADA"
# }

# Init word variables

for word_type in regex:
    locals()[f"{word_type}_words"]: Dict[str, Dict[str, Union[float, int]]] = {}

# type_words = {
#     "regex": {
#         "time": 15112345678,
#         "average": 1.1,
#         "today": 3,
#         "total": 20,
#         "temp": 0,
#         "who": 12345678
#     }
# }

# Load data
file_list: List[str] = ["ask_words", "comments"]
file_list += [f"{f}_words" for f in regex]

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

# Generate special characters dictionary
for special in ["spc", "spe"]:
    locals()[f"{special}_dict"]: Dict[str, str] = {}

    for rule in locals()[f"{special}_words"]:
        # Check keys
        if "[" not in rule:
            continue

        # Check value
        if "?#" not in rule:
            continue

        keys = rule.split("]")[0][1:]
        value = rule.split("?#")[1][1]

        for k in keys:
            locals()[f"{special}_dict"][k] = value

# Start program
copyright_text = (f"SCP-079-{sender} v{version}, Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
