#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pyrogram import Client
from plugins import glovar

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename='log',
    filemode='w'
)

logger = logging.getLogger(__name__)

# Start
app = Client(glovar.token)
app.idle()
