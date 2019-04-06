import json
from pyrogram import Client
from .. import glovar
from ..functions.etc import thread
from .. functions.words import words_list
from ..functions.telegram import answer_callback, edit_message


@Client.on_callback_query()
def answer(client, callback_query):
    aid = callback_query.from_user.id
    if aid == glovar.creator_id:
        cid = callback_query.message.chat.id
        mid = callback_query.message.message_id
        callback_data = json.loads(callback_query.data)
        if callback_data["action"] == "list":
            word_type = callback_data["type"]
            text, markup = words_list(word_type, callback_data["data"])
            thread(edit_message, (client, cid, mid, text, markup))
        else:
            answer_callback(client, callback_query.id, "")

    if client:
        pass
