import re
import logging
import configparser

# Enable logging
logger = logging.getLogger(__name__)

# Init
names: dict = {
    "avatar": "头像分析",
    "bad": "敏感检测",
    "ban": "自动封禁",
    "bio": "简介封禁",
    "delete": "自动删除",
    "emergency": "应急模式",
    "nick": "昵称封禁",
    "watch": "敏感追踪",
    "sticker": "贴纸删除"
}
compiled: dict = {
    "avatar": re.compile("预留头像分析词组", re.I | re.M | re.S),
    "bad": re.compile("预留敏感检测词组", re.I | re.M | re.S),
    "ban": re.compile("预留自动封禁词组", re.I | re.M | re.S),
    "bio": re.compile("预留简介信息词组", re.I | re.M | re.S),
    "delete": re.compile("预留自动删除词组", re.I | re.M | re.S),
    "emergency": re.compile("预留应急检测词组", re.I | re.M | re.S),
    "nick": re.compile("预留昵称封禁词组", re.I | re.M | re.S),
    "watch": re.compile("预留敏感追踪词组", re.I | re.M | re.S),
    "sticker": re.compile("预留贴纸删除词组", re.I | re.M | re.S)
}

# Generate commands lists
list_commands: list = []
search_commands: list = []
add_commands: list = []
remove_commands: list = []

for operation in ["list", "search", "add", "remove"]:
    locals()[f"{operation}_commands"] = [f"{operation}_{word}" for word in names]

# Read data from config.ini
token: str = ""
creator_id: int = 0

try:
    config = configparser.ConfigParser()
    config.read("config.ini")

    if "custom" in config:
        token = config["custom"].get("token", token)
        creator_id = int(config["custom"].get("creator_id", creator_id))
except Exception as e:
    logger.warning('Read data from config.ini error: %s', e)

if token == "" or creator_id == 0:
    logger.critical("No proper settings")
    raise SystemExit('No proper settings')
