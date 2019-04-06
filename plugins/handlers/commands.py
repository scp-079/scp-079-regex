import logging
from pyrogram import Client, Filters
from .. import glovar
from ..functions.etc import code, thread
from ..functions.telegram import send_message
from .. functions.words import words_list

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(command=["ping"],
                                                                        prefix=glovar.prefix))
def ping(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = code("Pong!")
            thread(send_message, (client, message.chat.id, text))
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & Filters.command(command=glovar.list_commands,
                                                                      prefix=glovar.prefix))
def list_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            cid = message.chat.id
            mid = message.message_id
            command_list = message.command
            if len(command_list) == 1:
                word_type = command_list[0].partition("_")[2]
                text, markup = words_list(word_type, 1)
            else:
                text = "格式有误"
                markup = None

            thread(send_message, (client, cid, text, mid, markup))
    except Exception as e:
        logger.warning(f"List words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & Filters.command(command=glovar.search_commands,
                                                                      prefix=glovar.prefix))
def search_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = code("Pong!")
            thread(send_message, (client, message.chat.id, text))
    except Exception as e:
        logger.warning(f"Search words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & Filters.command(command=glovar.add_commands,
                                                                      prefix=glovar.prefix))
def add_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = code("Pong!")
            thread(send_message, (client, message.chat.id, text))
    except Exception as e:
        logger.warning(f"Add words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & Filters.command(command=glovar.remove_commands,
                                                                      prefix=glovar.prefix))
def remove_words(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = code("Pong!")
            thread(send_message, (client, message.chat.id, text))
    except Exception as e:
        logger.warning(f"Remove words error: {e}", exc_info=True)
