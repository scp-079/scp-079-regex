from pyrogram import Client


@Client.on_callback_query()
def answer(client, callback_query):
    callback_query.answer('Button contains: "{}"'.format(callback_query.data))

    if client:
        pass
