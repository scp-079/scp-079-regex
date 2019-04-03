import logging
from threading import Thread
from pyrogram import Client, Filters
from .. import glovar
from ..functions.telegram import send_message, send_reply_keyboard

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(["ping"]))
def ping(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = "`Pong!`"
            t = Thread(target=send_message, args=(client, message.chat.id, text))
            t.start()
    except Exception as e:
        logger.warning(f"Ping error: {e}")


@Client.on_message(Filters.incoming & Filters.private & Filters.command(glovar.list_commands))
def list_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            t = Thread(target=send_reply_keyboard, args=(client, message.chat.id))
            t.start()
    except Exception as e:
        logger.warning(f"List words error: {e}")


@Client.on_message(Filters.incoming & Filters.private & Filters.command(glovar.search_commands))
def search_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            t = Thread(target=send_reply_keyboard, args=(client, message.chat.id))
            t.start()
    except Exception as e:
        logger.warning(f"Search words error: {e}")


@Client.on_message(Filters.incoming & Filters.private & Filters.command(glovar.add_commands))
def add_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            t = Thread(target=send_reply_keyboard, args=(client, message.chat.id))
            t.start()
    except Exception as e:
        logger.warning(f"Add words error: {e}")


@Client.on_message(Filters.incoming & Filters.private & Filters.command(glovar.remove_commands))
def remove_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            t = Thread(target=send_reply_keyboard, args=(client, message.chat.id))
            t.start()
    except Exception as e:
        logger.warning(f"Remove words error: {e}")
