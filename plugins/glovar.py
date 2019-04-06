import re
import pickle
import logging
from os.path import exists
from typing import List
from configparser import ConfigParser

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
    "avatar": re.compile("预留头像分析词组 tp2R6sOCjTZX0dZc", re.I | re.M | re.S),
    "bad": re.compile("预留敏感检测词组 72exw46Lcbu6pREC", re.I | re.M | re.S),
    "ban": re.compile("预留自动封禁词组 3wiyx9d6tWncV574", re.I | re.M | re.S),
    "bio": re.compile("预留简介信息词组 uZYBnIeWTjsH4Tp8", re.I | re.M | re.S),
    "delete": re.compile("预留自动删除词组 uJL50YWS1CImkNNF", re.I | re.M | re.S),
    "emergency": re.compile("预留应急检测词组 Nl3j6V59Al58vUPz", re.I | re.M | re.S),
    "nick": re.compile("预留昵称封禁词组 ees47GZonrr7UPTt", re.I | re.M | re.S),
    "watch": re.compile("预留敏感追踪词组 tsK0sOwUMxbtM3dU", re.I | re.M | re.S),
    "sticker": re.compile("预留贴纸删除词组 pI1S28cjRf1cdW8g", re.I | re.M | re.S)
}

# Generate commands lists
list_commands: list = []
search_commands: list = []
add_commands: list = []
remove_commands: list = []

for operation in ["list", "search", "add", "remove"]:
    locals()[f"{operation}_commands"] = [f"{operation}_{word}" for word in names]

# Load words form pickle (need a better way to store data [?])
avatar_words: set = set()
bad_words: set = set()
ban_words: set = set()
bio_words: set = set()
delete_words: set = set()
emergency_words: set = set()
nick_words: set = set()
watch_words: set = set()

for word_type in names:
    try:
        try:
            if exists(f"data/{word_type}_words") or exists(f"data/.{word_type}_words"):
                with open(f"data/{word_type}_words", 'rb') as f:
                    locals()[f"{word_type}_words"] = pickle.load(f)
            else:
                locals()[f"{word_type}_words"] = {"预留词组 w0PXcf249698wPpw"}
                with open(f"data/{word_type}_words", 'wb') as f:
                    pickle.dump(eval(f"{word_type}_words"), f)
        except Exception as e:
            logger.error(f"Load data {word_type}_words error: {e}")
            with open(f"data/.{word_type}_words", 'rb') as f:
                locals()[f"{word_type}_words"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {word_type}_words backup error: {e}")
        raise SystemExit("[DATA CORRUPTION]")

# Read data from config.ini
token: str = ""
creator_id: int = 0
prefix: List[str] = []
prefix_str: str = "/!！"

try:
    config = ConfigParser()
    config.read("config.ini")

    if "custom" in config:
        token = config["custom"].get("token", token)
        creator_id = int(config["custom"].get("creator_id", creator_id))
        prefix = list(config["custom"].get("prefix", prefix_str))
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}")

if token == "" or creator_id == 0 or prefix == []:
    logger.critical("No proper settings")
    raise SystemExit('No proper settings')
