import asyncio
import os
import time
import json
import random
import logging
import traceback
import re
import glob
import signal
import sys
import math
import datetime
import hashlib
import base64
import threading
from typing import Dict, Set, Optional, List, Any, Tuple
from io import BytesIO
from collections import defaultdict

import requests
import qrcode
from gtts import gTTS
import yt_dlp
from cryptography.fernet import Fernet
import asyncpg

from flask import Flask
from waitress import serve

from telethon import TelegramClient, events, functions, types, errors
from telethon.errors import (
    FloodWaitError, RPCError, MessageNotModifiedError,
    UnauthorizedError, AuthKeyDuplicatedError,
    SessionPasswordNeededError, UserNotParticipantError,
    ChannelInvalidError, ChannelPrivateError
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest, InviteToChannelRequest, EditTitleRequest
from telethon.tl.functions.messages import EditChatTitleRequest, AddChatUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.contacts import UnblockRequest, BlockRequest
from telethon.tl.types import (
    InputPeerUser, KeyboardButtonUrl,
    KeyboardButtonCallback, DocumentAttributeAudio,
    ChatBannedRights, InputDocument
)

# ═══════════════════════════════════════════════════════════════════════
# SECTION 1: CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MY_OWNER_IDS = {int(x) for x in os.environ.get("OWNER_IDS", "8909378644,8711082433").split(",") if x.strip()}
UPI_ID = os.environ.get("UPI_ID", "paryush01@nyes")
QR_IMAGE_PATH = os.environ.get("QR_IMAGE_PATH", "upi_qr.jpg")
PREMIUM_FEATURES_LINK = os.environ.get("PREMIUM_FEATURES_LINK", "https://t.me/userbotsupport_ZA/20")
BROADCAST_JSON_PATH = "broadcast.json"
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USER_DATA_DIR = "user_data"

# ─── Required Channels for Verification ──
REQUIRED_CHANNELS = [
    {"id": -1004404975416, "invite": "https://t.me/+j9ndQJG6wdc3ZDE1", "name": "Channel 1"},
    {"id": -1004334756214, "invite": "https://t.me/+5DvNxDnfAApjYWNk", "name": "Channel 2"},
    {"id": -1004452969098, "invite": "https://t.me/+A1qEdXj8ZUI5ZGM1", "name": "Channel 3"},
    {"id": -1004331434090, "invite": "https://t.me/+Wkmu7JUvlrBkZTI1", "name": "Channel 4"},
]

# ─── Protected Commands ──
PROTECTED_COMMANDS = [
    "reply", "sreply", "rr", "srr", "flag", "sflag", "hrr", "shrr",
    "replygod", "sgod", "customraid", "stopcustomraid",
    "shayariraid", "sshayariraid", "rizzraid", "srizzraid",
    "pickupraid", "spickupraid", "romanceraid", "sromanceraid",
    "trollraid", "strollraid", "ragebaitraid", "sragebaitraid",
    "roastraid", "sroastraid",
    "attackraid", "sattackraid", "warraid", "swarraid",
    "savageraid", "ssavageraid", "ultraraid", "sultraraid",
    "shameraid", "sshameraid", "dissraid", "sdissraid",
    "devilraid", "sdevilraid", "karmaraid", "skarmaraid",
    "doomraid", "sdoomraid",
    "spray", "dspray", "tspray", "rspray", "multispray", "countspray",
    "deathgod", "sdeathgod",
    "mr", "smr", "mr2", "smr2", "br", "sbr", "br2", "sbr2", "br3", "sbr3",
    "sqr", "ssqr", "sq2", "ssq2", "cr", "scr", "bar", "sbar", "gr", "sgr",
    "ms", "sms", "ms2", "sms2", "bs", "sbs", "bs2", "sbs2", "bs3", "sbs3",
    "sqs", "ssqs", "sqs2", "ssqs2", "cs", "scs", "bas", "sbas", "gs", "sgs",
    "pwr", "spwr", "ows", "sows"
]

# ─── ALL TEXT LISTS — EMPTIED ──
# ─── TEXT LISTS ──────────────────────────────────────────────────────
# ─── PREMIUM RAID TEXT LISTS ──────────────────────────────────────────
mr_texts = [
"TTTTTTT🍷EEEEEE💊RRRRR🔘OOOOO🎲BBBBB🤍EEEEEE💊GGGGGG🖤EEEEEE💊JJJJJJ👅 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊OOOOO🎲 AAAAAA👿AAAAAA👿AAAAAA👿MMMMM🚀MMMMM🚀AAAAAA👿 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘OOOOO🎲 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 LLLLLL🔨AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘",
"OOOOOO👅YYYYYYEEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜 BBBBB🤍JJJJJJ👅OOOOO🎲SSSSS⚒️RRRRR🔘WWWWW🥰",
"TTTTTTT🍷EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜 FFFFFF🔥AAAAAA👿NNNNNN🤣RRRRR🔘",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷RRRRR🔘",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿KKKKKK💜IIIIII🍷 GGGGGG🖤EEEEEE💊TTTTT🚭IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 MMMMM🚀UUUUU💣HHHHH🖤",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 CCCCCC⚔️HHHHH🖤IIIIII🍷NNNNNN🤣AAAAAA👿LLLLLL🔨",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 MMMMM🚀AAAAAA👿RRRRR🔘 GGGGGG🖤AAAAAA👿YYYYYYIIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣TTTTT🚭IIIIII🍷 RRRRR🔘AAAAAA👿DDDDD👿IIIIII🍷 KKKKKK💜IIIIII🍷 HHHHH🖤EEEEEE💊TTTTT🚭",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 CCCCCC⚔️IIIIII🍷OOOOO🎲DDDDD👿AAAAAA👿 AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿KKKKKK💜 MMMMM🚀",
"OOOOOO👅YYYYYYEEEEEE💊 KKKKKK💜IIIIII🍷NNNNNN🤣NNNNNN🤣AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA??CCCCCC⚔️CCCCCC⚔️GGGGGG🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII?? MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍IIIIII🍷OOOOO🎲AAAAAA👿RRRRR🔘SSSSS⚒️",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 MMMMM🚀AAAAAA👿RRRRR🔘AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿OOOOO🎲UUUUU💣AAAAAA👿 JJJJJJ👅AAAAAA👿AAAAAA👿NNNNNN🤣 CCCCCC⚔️JJJJJJ👅OOOOO🎲DDDDD👿YYYYYYAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 BBBBB🤍HHHHH🖤OOOOO🎲AAAAAA👿DDDDD👿AAAAAA👿 CCCCCC⚔️OOOOO🎲DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 CCCCCC⚔️HHHHH🖤UUUUU💣TTTTT??EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿.    KKKKKK📌AAAAAA👿AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍RRRRR🔘HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY KKKKKK💜UUUUU💣TTTTT🚭IIIIII🍷YYYYYYAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿HHHHH🖤IIIIII🍷 KKKKKK💜AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️GGGGGG🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 CCCCCC⚔️GGGGGG🖤OOOOO🎲DDDDD👿UUUUU💣",
"OOOOOO??YYYYYYEEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 CCCCCC⚔️HHHHH🖤UUUUU💣CCCCCC⚔️HHHHH🖤OOOOO🎲 KKKKKK💜AAAAAA👿TTTTT🚭YYYYYY",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿HHHHH🖤IIIIII🍷 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 CCCCCC⚔️GGGGGG🖤OOOOO🎲DDDDD👿YYYYYY",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀YYYYYY CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜IIIIII🍷 LLLLLL🔨AAAAAA👿DDDDD👿KKKKKK💜IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 JJJJJJ👅AAAAAA👿AAAAAA👿NNNNNN🤣 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE??RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘 FFFFFF🔥AAAAAA👿DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 BBBBB🤍AAAAAA👿NNNNNN🤣AAAAAA👿 DDDDD👿UUUUU💣NNNNNN🤣GGGGGG🖤AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿KKKKKK💜EEEEEE💊 FFFFFF🔥EEEEEE💊KKKKKK💜UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 MMMMM🚀UUUUU💣HHHHH🖤 MMMMM🚀EEEEEE💊IIIIII🍷 PPPPPP📌AAAAAA👿KKKKKK💜IIIIII🍷SSSSS⚒️TTTTT🚭AAAAAA👿NNNNNN🤣IIIIII🍷 LLLLLL🔨AAAAAA👿VVVVDDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 PPPPPP📌KKKKKK💜AAAAAA👿OOOOO🎲SSSSS⚒️TTTTT🚭AAAAAA👿NNNNNN🤣IIIIII🍷 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍EEEEEE💊TTTTT🚭",
"TTTTTTT🍷EEEEEE💊RRRRR🔘UUUUU💣 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣TTTTT🚭",
"OOOOOO👅YYYYYYEEEEEE💊 TTTTT🚭AAAAAA👿TTTTT🚭TTTTT🚭TTTTT🚭EEEEEE💊 UUUUU💣TTTTT🚭HHHHH🖤",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️UUUUU💣UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿 DDDDD👿EEEEEE💊DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘OOOOO🎲 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 KKKKKK💜EEEEEE💊 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿EEEEEE💊 PPPPPP📌EEEEEE💊 LLLLLL🔨OOOOO🎲LLLLLL🔨LLLLLL🔨AAAAAA👿",
"LLLLLLL🎲OOOOO🎲LLLLLL🔨LLLLLL🔨EEEEEE💊 HHHHH🖤OOOOO🎲 LLLLLL🔨OOOOO🎲LLLLLL🔨LLLLLL🔨EEEEEE💊 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 PPPPPP📌EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 DDDDD👿EEEEEE💊 MMMMM🚀UUUUU💣JJJJJJ👅GGGGGG🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀YYYYYY CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜 BBBBB🤍UUUUU💣RRRRR🔘 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 VVVVEEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 AAAAAA👿MMMMM🚀MMMMM🚀AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 FFFFFF🔥AAAAAA👿BBBBB🤍DDDDD👿 MMMMM🚀AAAAAA👿RRRRR🔘VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘  MMMMM🚀AAAAAA👿RRRRR🔘VVVVAAAAAA👿",
"IIIIIIII⚒️DDDDD👿GGGGGG🖤AAAAAA👿RRRRR🔘 AAAAAA👿JJJJJJ👅AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜AAAAAA👿 LLLLLL🔨AAAAAA👿DDDDD👿KKKKKK💜AAAAAA👿",
"IIIIIIII⚒️DDDDD👿HHHHH🖤AAAAAA👿 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿 DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 HHHHH🖤AAAAAA👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜YYYYYYTTTTT🚭TTTTT🚭OOOOO🎲 HHHHH🖤AAAAAA👿IIIIII🍷",
"YYYYYY🤍EEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"MMMMM💥AAAAAA👿RRRRR🔘 GGGGGG🖤AAAAAA👿YYYYYYAAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿 AAAAAA👿 DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊. KKKKKK📌 PPPPPP📌EEEEEE💊LLLLLL🔨UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 LLLLLL🔨EEEEEE💊UUUUU💣 LLLLLL🔨UUUUU💣NNNNNN🤣DDDDD👿 PPPPPP📌EEEEEE💊 AAAAAA👿PPPPPP📌NNNNNN🤣EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 MMMMM🚀AAAAAA👿RRRRR🔘AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿 MMMMM🚀AAAAAA👿RRRRR🔘AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿AAAAAA👿",
"OOOOOO👅YYYYYYEEEEEE💊 TTTTT🚭AAAAAA👿TTTTT🚭TTTTT🚭EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 AAAAAA👿CCCCCC⚔️UUUUU💣DDDDD👿AAAAAA👿. AAAAAA👿BBBBB🤍",
"MMMMM💥AAAAAA👿RRRRR🔘NNNNNN??AAAAAA👿 MMMMM🚀AAAAAA👿NNNNNN🤣AAAAAA👿 HHHHH🖤AAAAAA👿IIIIII🍷 RRRRR🔘AAAAAA👿 DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊",
"MMMMM💥AAAAAA👿RRRRR🔘 MMMMM🚀AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 LLLLLL🔨IIIIII🍷MMMMM🚀HHHHH🖤EEEEEE💊AAAAAA👿 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿HHHHH🖤",
"OOOOOO👅YYYYYYEEEEEE💊 KKKKKK💜IIIIII🍷NNNNNN🤣AAAAAA👿AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA??CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊 UUUUU💣TTTTT🚭HHHHH🖤",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿 OOOOO🎲YYYYYYEEEEEE💊 TTTTT🚭AAAAAA👿TTTTT🚭TTTTT🚭EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊 CCCCCC⚔️BBBBB🤍UUUUU💣DDDDD👿VVVVAAAAAA👿 LLLLLL🔨EEEEEE💊",
"GGGGGG🌿EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 FFFFFF🔥AAAAAA👿NNNNNN🤣DDDDD👿 OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 KKKKKK💜AAAAAA👿AAAAAA👿AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘 TTTTT🚭OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷AAAAAA👿TTTTT🚭TTTTT🚭TTTTT🚭EEEEEE💊 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 MMMMM🚀UUUUU💣HHHHH🖤 PPPPPP📌EEEEEE💊 LLLLLL🔨OOOOO🎲DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 PPPPPP📌EEEEEE💊 LLLLLL🔨OOOOO🎲DDDDD👿AAAAAA👿",
"OOOOOO👅YYYYYYEEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 SSSSS⚒️AAAAAA👿MMMMM🚀JJJJJJ👿 WWWWW??AAAAAA👿LLLLLL🔨EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷.GGGGGG🖤AAAAAA👿 DDDDD👿 SSSSS⚒️AAAAAA👿MMMMM🚀BBBBB🤍HHHHH🖤AAAAAA👿LLLLLL🔨AAAAAA👿 KKKKKK💜EEEEEE💊 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 IIIIII🍷EEEEEE💊 BBBBB🤍EEEEEE💊YYYYYY",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 CCCCCC⚔️HHHHH🖤UUUUU💣TTTTT🚭EEEEEE💊 WWWWW🥰AAAAAA👿LLLLLL🔨IIIIII🍷 RRRRR🔘AAAAAA👿 DDDDD👿IIIIII🍷",
"MMMMM💥AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿",
"KKKKKK📌WWWWW🥰EEEEEE💊EEEEEE💊EEEEEE💊 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿EEEEEE💊 DDDDD👿EEEEEE💊",
"OOOOOO👅YYYYYYEEEEEE💊 BBBBB🤍HHHHH🖤AAAAAA👿NNNNNN🤣GGGGGG🖤IIIIII🍷 TTTTT🚭AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"KKKKKK📌IIIIII🍷NNNNNN🤣NNNNNN🤣AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 NNNNNN🤣AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿BBBBB🤍YYYYYYEEEEEE💊GGGGGG🖤AAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 KKKKKK💜AAAAAA👿AAAAAA👿AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿SSSSS⚒️ DDDDD👿EEEEEE💊DDDDD👿EEEEEE💊",
"AAAAAA👿BBBBB🤍 CCCCCC⚔️HHHHH🖤AAAAAA??LLLLLL🔨 LLLLLL🔨UUUUU💣NNNNNN🤣DDDDD👿 KKKKKK💜EEEEEE💊 CCCCCC⚔️HHHHH🖤UUUUU💣PPPPPP📌PPPPPP📌EEEEEE💊 KKKKKK💜AAAAAA👿RRRRR🔘",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣 OOOOO🎲YYYYYYEEEEEE💊"
]

mr2_texts = [
"B⃠a⃠a⃠p⃠ b⃠h⃠i⃠ b⃠n⃠a⃠l⃠e⃠ m⃠u⃠j⃠e⃠ r⃠n⃠d⃠i⃠k⃠e⃠",
"T⃠e⃠r⃠a⃠ b⃠a⃠a⃠p⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ e⃠y⃠ y⃠a⃠a⃠d⃠ e⃠y⃠ t⃠u⃠j⃠h⃠e⃠",
"T⃠u⃠ a⃠p⃠n⃠i⃠ M⃠a⃠a⃠ c⃠u⃠d⃠a⃠ n⃠a⃠ t⃠y⃠m⃠p⃠a⃠s⃠s⃠",
"O⃠y⃠e⃠ u⃠n⃠f⃠u⃠n⃠n⃠y⃠ s⃠w⃠i⃠p⃠e⃠ m⃠t⃠t⃠ k⃠r⃠",
"O⃠h⃠ h⃠e⃠l⃠l⃠o⃠ b⃠i⃠h⃠a⃠r⃠i⃠ t⃠e⃠r⃠a⃠ b⃠a⃠a⃠p⃠ b⃠i⃠h⃠a⃠r⃠i⃠ o⃠r⃠ t⃠u⃠ v⃠ b⃠i⃠h⃠a⃠r⃠i⃠ a⃠a⃠u⃠k⃠a⃠t⃠ m⃠e⃠ r⃠h⃠a⃠ k⃠r⃠.",
"O⃠y⃠y⃠ k⃠i⃠n⃠n⃠e⃠r⃠ t⃠u⃠j⃠h⃠e⃠ g⃠c⃠ m⃠e⃠ a⃠a⃠n⃠e⃠ k⃠i⃠ p⃠e⃠r⃠m⃠i⃠s⃠s⃠i⃠o⃠n⃠ k⃠i⃠s⃠n⃠e⃠ d⃠i⃠.",
"C⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"C⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠ e⃠k⃠ b⃠a⃠a⃠r⃠.",
"S⃠u⃠n⃠ s⃠u⃠n⃠ m⃠a⃠ c⃠u⃠d⃠a⃠.",
"T⃠e⃠r⃠i⃠ m⃠a⃠c⃠a⃠ b⃠h⃠o⃠s⃠d⃠a⃠.",
"O⃠y⃠e⃠ c⃠h⃠o⃠t⃠i⃠ j⃠a⃠t⃠i⃠ k⃠e⃠ t⃠m⃠r⃠.",
"K⃠y⃠? j⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ k⃠i⃠d⃠d⃠e⃠.",
"B⃠i⃠h⃠a⃠r⃠i⃠ c⃠o⃠m⃠ g⃠a⃠n⃠g⃠ k⃠e⃠ b⃠a⃠a⃠p⃠ k⃠o⃠ t⃠a⃠g⃠ c⃠r⃠e⃠g⃠a⃠ t⃠u⃠",
"M⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ t⃠u⃠ b⃠i⃠h⃠a⃠r⃠i⃠ e⃠y⃠ t⃠m⃠k⃠c⃠ b⃠s⃠",
"J⃠a⃠l⃠d⃠i⃠ s⃠e⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ p⃠a⃠p⃠a⃠ b⃠o⃠l⃠",
"S⃠i⃠d⃠e⃠ h⃠o⃠j⃠a⃠ b⃠i⃠h⃠a⃠r⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ a⃠b⃠",
"H⃠y⃠e⃠ p⃠g⃠l⃠ b⃠h⃠g⃠ m⃠a⃠t⃠ a⃠c⃠h⃠e⃠ s⃠e⃠ c⃠u⃠d⃠",
"b⃠h⃠g⃠ n⃠y⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ t⃠u⃠ a⃠j⃠j⃠",
"H⃠y⃠e⃠ p⃠g⃠l⃠ k⃠e⃠ b⃠c⃠h⃠e⃠ b⃠h⃠a⃠g⃠ m⃠a⃠t⃠",
"H⃠y⃠e⃠ d⃠u⃠r⃠ h⃠a⃠t⃠t⃠ m⃠a⃠d⃠h⃠c⃠h⃠o⃠d⃠ k⃠e⃠ b⃠a⃠c⃠h⃠e⃠",
"k⃠o⃠i⃠ b⃠a⃠t⃠ n⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠ e⃠s⃠l⃠i⃠y⃠e⃠ m⃠a⃠f⃠ c⃠r⃠ r⃠h⃠a⃠ h⃠u⃠ t⃠u⃠j⃠h⃠e⃠",
"k⃠o⃠i⃠ b⃠a⃠a⃠t⃠ n⃠y⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠ m⃠a⃠f⃠i⃠ d⃠e⃠ d⃠u⃠n⃠g⃠a⃠",
"A⃠c⃠h⃠e⃠ s⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠ m⃠a⃠f⃠i⃠ m⃠i⃠l⃠ j⃠a⃠y⃠e⃠g⃠i⃠ t⃠u⃠j⃠h⃠e⃠",
"a⃠p⃠n⃠i⃠ m⃠a⃠ m⃠a⃠t⃠ c⃠h⃠u⃠d⃠a⃠ m⃠u⃠j⃠e⃠ s⃠w⃠i⃠p⃠e⃠ c⃠r⃠k⃠e⃠",
"A⃠c⃠h⃠e⃠ s⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ s⃠w⃠i⃠p⃠e⃠ c⃠r⃠k⃠e⃠",
"F⃠r⃠ b⃠o⃠l⃠n⃠a⃠ n⃠a⃠ k⃠i⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ s⃠w⃠i⃠p⃠e⃠ c⃠r⃠k⃠e⃠",
"C⃠y⃠a⃠ h⃠u⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠ k⃠e⃠s⃠e⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠",
"m⃠u⃠j⃠h⃠e⃠ p⃠t⃠a⃠ t⃠h⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"m⃠e⃠y⃠ n⃠y⃠ m⃠a⃠n⃠t⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠ r⃠n⃠d⃠y⃠",
"l⃠o⃠d⃠e⃠ s⃠e⃠ u⃠t⃠r⃠ m⃠c⃠",
"l⃠u⃠n⃠ m⃠t⃠ c⃠h⃠u⃠s⃠ m⃠e⃠r⃠a⃠",
"n⃠i⃠k⃠a⃠l⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠d⃠",
"c⃠h⃠u⃠p⃠ o⃠y⃠e⃠ g⃠a⃠s⃠h⃠t⃠i⃠ k⃠ b⃠a⃠c⃠h⃠e⃠",
"m⃠a⃠k⃠i⃠c⃠h⃠u⃠t⃠ t⃠e⃠r⃠i⃠",
"c⃠h⃠u⃠p⃠ r⃠n⃠d⃠y⃠k⃠e⃠",
"m⃠a⃠ r⃠n⃠d⃠y⃠ t⃠e⃠r⃠i⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠ k⃠ h⃠a⃠t⃠h⃠ t⃠o⃠d⃠h⃠ k⃠ t⃠e⃠r⃠e⃠ b⃠a⃠a⃠p⃠ k⃠ m⃠u⃠h⃠ m⃠e⃠ f⃠a⃠s⃠a⃠d⃠u⃠n⃠g⃠a⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"l⃠e⃠a⃠v⃠e⃠ l⃠e⃠ t⃠u⃠ r⃠n⃠d⃠y⃠k⃠e⃠ p⃠a⃠s⃠a⃠n⃠d⃠ n⃠a⃠i⃠ a⃠y⃠a⃠ m⃠e⃠k⃠o⃠",
"l⃠e⃠a⃠v⃠e⃠ l⃠e⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ i⃠d⃠e⃠r⃠ s⃠e⃠",
"L⃠e⃠a⃠v⃠e⃠ l⃠e⃠ j⃠l⃠d⃠i⃠ s⃠e⃠ w⃠r⃠n⃠a⃠ m⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"L⃠e⃠a⃠v⃠e⃠ n⃠y⃠ l⃠e⃠g⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"S⃠m⃠j⃠h⃠ b⃠a⃠t⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ l⃠e⃠a⃠v⃠e⃠ l⃠e⃠",
"f⃠a⃠s⃠t⃠ l⃠e⃠a⃠v⃠e⃠ l⃠e⃠ k⃠a⃠m⃠j⃠o⃠r⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"t⃠u⃠t⃠o⃠ c⃠h⃠u⃠p⃠ r⃠n⃠d⃠y⃠k⃠",
"o⃠y⃠ h⃠i⃠j⃠d⃠e⃠ k⃠h⃠a⃠n⃠a⃠ k⃠h⃠a⃠ k⃠e⃠ a⃠a⃠ k⃠a⃠m⃠z⃠o⃠r⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠k⃠o⃠ i⃠l⃠y⃠ r⃠e⃠y⃠🌚😂",
"c⃠h⃠u⃠p⃠ c⃠h⃠a⃠p⃠ c⃠h⃠u⃠d⃠ t⃠m⃠k⃠c⃠",
"c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠",
"s⃠h⃠i⃠ s⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠ c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠",
"f⃠r⃠ s⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠",
"s⃠h⃠i⃠ s⃠e⃠ l⃠i⃠k⃠h⃠ w⃠r⃠n⃠a⃠ m⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"m⃠a⃠ c⃠y⃠u⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠",
"p⃠r⃠o⃠o⃠f⃠ c⃠r⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠o⃠o⃠f⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"p⃠r⃠o⃠o⃠f⃠ h⃠o⃠ c⃠h⃠u⃠k⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"C⃠h⃠u⃠p⃠ c⃠h⃠i⃠l⃠l⃠a⃠r⃠",
"c⃠h⃠u⃠p⃠ c⃠h⃠u⃠p⃠ m⃠a⃠a⃠ k⃠ b⃠o⃠s⃠d⃠a⃠ t⃠e⃠r⃠y⃠",
"o⃠y⃠ h⃠i⃠j⃠d⃠e⃠ k⃠h⃠a⃠n⃠a⃠ k⃠h⃠a⃠ k⃠e⃠ a⃠a⃠ k⃠a⃠m⃠z⃠o⃠r⃠",
"c⃠h⃠u⃠p⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠o⃠d⃠ ?",
"A⃠b⃠ t⃠k⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ h⃠o⃠g⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ ?",
"n⃠y⃠ n⃠y⃠ m⃠e⃠ k⃠u⃠c⃠h⃠ n⃠y⃠ j⃠a⃠n⃠t⃠a⃠ b⃠s⃠ t⃠e⃠r⃠i⃠ m⃠a⃠ r⃠n⃠d⃠y⃠ e⃠y⃠",
"S⃠b⃠s⃠e⃠ p⃠h⃠e⃠l⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠a⃠ k⃠o⃠ b⃠o⃠l⃠ c⃠h⃠u⃠d⃠n⃠a⃠ k⃠a⃠a⃠m⃠ k⃠r⃠e⃠",
"Y⃠a⃠h⃠a⃠ b⃠h⃠i⃠ c⃠h⃠u⃠d⃠a⃠ t⃠u⃠ r⃠n⃠d⃠y⃠c⃠e⃠ p⃠i⃠l⃠l⃠e⃠",
"t⃠e⃠r⃠i⃠m⃠a⃠k⃠a⃠b⃠o⃠s⃠d⃠a⃠",
"t⃠e⃠r⃠i⃠ t⃠o⃠ b⃠h⃠e⃠n⃠ c⃠u⃠d⃠e⃠g⃠i⃠",
"c⃠h⃠u⃠p⃠ r⃠n⃠d⃠y⃠k⃠e⃠ t⃠o⃠m⃠m⃠y⃠",
"n⃠i⃠k⃠a⃠l⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠d⃠ c⃠u⃠d⃠k⃠e⃠ y⃠h⃠a⃠ s⃠e⃠",
"c⃠o⃠z⃠ t⃠e⃠r⃠i⃠ m⃠a⃠ a⃠n⃠d⃠h⃠i⃠ r⃠a⃠n⃠d⃠i⃠ h⃠e⃠",
"n⃠y⃠t⃠o⃠ b⃠a⃠a⃠p⃠ b⃠o⃠l⃠ m⃠u⃠j⃠h⃠e⃠",
"n⃠y⃠n⃠y⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ h⃠o⃠g⃠i⃠ r⃠n⃠d⃠i⃠i⃠ j⃠o⃠ c⃠h⃠u⃠d⃠w⃠a⃠t⃠i⃠ j⃠o⃠g⃠i⃠",
"t⃠r⃠y⃠ a⃠m⃠m⃠i⃠ c⃠e⃠ b⃠h⃠o⃠s⃠d⃠e⃠ m⃠e⃠ e⃠m⃠o⃠j⃠i⃠ d⃠a⃠l⃠ m⃠c⃠",
"c⃠y⃠a⃠ ? c⃠h⃠m⃠r⃠ c⃠h⃠u⃠d⃠ g⃠y⃠a⃠ c⃠y⃠a⃠ ?",
"t⃠m⃠ c⃠h⃠u⃠d⃠r⃠i⃠ h⃠o⃠g⃠i⃠ f⃠r⃠r⃠t⃠o⃠",
"c⃠y⃠a⃠ ? k⃠b⃠ ? p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ r⃠n⃠d⃠k⃠e⃠k⃠",
"c⃠y⃠a⃠ s⃠c⃠h⃠ m⃠e⃠y⃠ p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠u⃠d⃠w⃠a⃠ l⃠i⃠ t⃠u⃠n⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠",
"i⃠t⃠n⃠a⃠ s⃠c⃠h⃠ n⃠y⃠ b⃠o⃠l⃠ m⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"s⃠c⃠h⃠ m⃠e⃠y⃠ p⃠g⃠l⃠ e⃠y⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ l⃠i⃠a⃠ m⃠e⃠r⃠e⃠ s⃠t⃠h⃠",
"m⃠t⃠l⃠b⃠ t⃠m⃠r⃠",
"n⃠y⃠t⃠o⃠",
"p⃠u⃠r⃠a⃠ l⃠i⃠k⃠h⃠ m⃠c⃠",
"t⃠m⃠r⃠ f⃠r⃠r⃠t⃠o⃠",
"o⃠h⃠ o⃠k⃠ c⃠u⃠d⃠l⃠e⃠ f⃠i⃠r⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠a⃠ d⃠a⃠m⃠a⃠d⃠",
"c⃠y⃠a⃠ ? a⃠c⃠h⃠e⃠ s⃠e⃠ l⃠i⃠k⃠h⃠e⃠ p⃠e⃠h⃠l⃠e⃠ r⃠n⃠d⃠i⃠k⃠e⃠b⃠a⃠c⃠h⃠e⃠",
"n⃠y⃠t⃠o⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠n⃠e⃠ m⃠e⃠ v⃠y⃠a⃠s⃠t⃠ h⃠u⃠",
"n⃠y⃠t⃠o⃠ p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ k⃠u⃠c⃠h⃠ b⃠i⃠",
"o⃠y⃠e⃠e⃠ c⃠y⃠a⃠ ? c⃠h⃠u⃠d⃠ g⃠y⃠a⃠ ?",
"c⃠h⃠u⃠d⃠ m⃠t⃠ h⃠s⃠s⃠",
"y⃠u⃠r⃠ r⃠n⃠d⃠i⃠i⃠ m⃠o⃠m⃠",
"a⃠r⃠e⃠ s⃠b⃠k⃠i⃠ m⃠a⃠a⃠ r⃠n⃠d⃠i⃠i⃠ o⃠r⃠ t⃠e⃠r⃠i⃠ b⃠i⃠",
"a⃠r⃠e⃠ i⃠d⃠a⃠r⃠ c⃠u⃠d⃠l⃠e⃠ e⃠k⃠ b⃠a⃠a⃠r⃠",
"t⃠r⃠i⃠ m⃠a⃠a⃠ c⃠i⃠ t⃠r⃠h⃠",
"e⃠k⃠ l⃠i⃠n⃠e⃠ m⃠e⃠ t⃠m⃠r⃠",
"Q⃠",
"o⃠c⃠y⃠ a⃠b⃠ c⃠h⃠u⃠d⃠l⃠e⃠",
"p⃠e⃠h⃠e⃠l⃠e⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠u⃠",
"n⃠y⃠t⃠o⃠",
"q⃠ ?",
"h⃠y⃠y⃠y⃠ c⃠h⃠u⃠d⃠ k⃠e⃠ d⃠i⃠k⃠a⃠ e⃠k⃠ b⃠a⃠a⃠r⃠",
"o⃠y⃠e⃠e⃠ s⃠u⃠n⃠ d⃠o⃠s⃠t⃠ t⃠m⃠r⃠",
"b⃠h⃠a⃠g⃠ j⃠a⃠ r⃠a⃠a⃠n⃠d⃠ m⃠a⃠a⃠f⃠ c⃠r⃠r⃠ d⃠u⃠n⃠g⃠a⃠",
"o⃠y⃠e⃠e⃠ p⃠g⃠l⃠ r⃠n⃠d⃠i⃠i⃠ i⃠d⃠a⃠r⃠ a⃠a⃠",
"c⃠y⃠a⃠ t⃠m⃠r⃠ f⃠r⃠r⃠t⃠o⃠",
"o⃠y⃠e⃠e⃠ i⃠d⃠a⃠r⃠ a⃠a⃠k⃠e⃠ c⃠h⃠u⃠d⃠ l⃠e⃠ c⃠h⃠m⃠r⃠",
"n⃠y⃠t⃠o⃠ a⃠e⃠s⃠e⃠ h⃠i⃠ c⃠u⃠d⃠",
"o⃠y⃠e⃠e⃠ h⃠y⃠y⃠ a⃠i⃠s⃠e⃠ h⃠i⃠ c⃠u⃠d⃠ l⃠e⃠n⃠a⃠",
"o⃠r⃠ c⃠h⃠u⃠d⃠ l⃠e⃠",
"c⃠h⃠u⃠d⃠ k⃠e⃠ d⃠i⃠k⃠a⃠ o⃠r⃠",
"h⃠y⃠y⃠ c⃠h⃠u⃠d⃠o⃠ n⃠a⃠",
"c⃠h⃠u⃠d⃠o⃠ m⃠t⃠ b⃠h⃠a⃠g⃠ j⃠a⃠o⃠",
"b⃠y⃠y⃠e⃠e⃠ h⃠y⃠y⃠ c⃠y⃠a⃠ ?",
"Q⃠c⃠h⃠u⃠d⃠ q⃠ r⃠h⃠e⃠ h⃠o⃠ ?",
"p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ m⃠c⃠",
"c⃠h⃠u⃠d⃠ m⃠t⃠",
"c⃠y⃠a⃠ p⃠g⃠l⃠ r⃠n⃠d⃠i⃠i⃠ i⃠d⃠a⃠r⃠ a⃠a⃠",
"t⃠e⃠r⃠i⃠ a⃠m⃠m⃠i⃠ c⃠e⃠ b⃠h⃠o⃠s⃠d⃠e⃠ m⃠e⃠ c⃠h⃠a⃠p⃠p⃠a⃠l⃠",
"o⃠y⃠e⃠e⃠ i⃠d⃠a⃠r⃠ a⃠a⃠ m⃠c⃠",
"k⃠m⃠z⃠r⃠o⃠r⃠ e⃠y⃠ c⃠y⃠a⃠ r⃠n⃠d⃠i⃠e⃠k⃠",
"c⃠y⃠a⃠ l⃠i⃠k⃠h⃠ r⃠h⃠a⃠ ?",
"c⃠h⃠u⃠d⃠ t⃠h⃠a⃠ c⃠y⃠a⃠ ?",
"o⃠y⃠e⃠e⃠ s⃠l⃠i⃠d⃠e⃠ l⃠e⃠k⃠e⃠ b⃠a⃠a⃠t⃠ c⃠r⃠m⃠c⃠",
"i⃠d⃠a⃠r⃠ a⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠u⃠",
"o⃠y⃠e⃠e⃠ c⃠p⃠ m⃠t⃠ c⃠r⃠r⃠ c⃠h⃠u⃠d⃠l⃠e⃠",
"o⃠y⃠e⃠e⃠ h⃠y⃠y⃠ c⃠h⃠u⃠d⃠ k⃠e⃠ d⃠i⃠k⃠a⃠",
"i⃠d⃠a⃠r⃠ a⃠a⃠ t⃠r⃠y⃠ m⃠a⃠ s⃠c⃠h⃠o⃠f⃠u⃠ k⃠h⃠a⃠c⃠h⃠a⃠r⃠ k⃠h⃠a⃠c⃠h⃠a⃠r⃠",
"i⃠d⃠a⃠r⃠ a⃠a⃠ j⃠a⃠ m⃠c⃠",
"h⃠y⃠y⃠ i⃠d⃠a⃠r⃠ a⃠a⃠k⃠e⃠ c⃠h⃠u⃠d⃠l⃠e⃠",
"o⃠y⃠e⃠e⃠ k⃠m⃠z⃠o⃠r⃠ m⃠c⃠ i⃠d⃠a⃠r⃠ a⃠a⃠",
"y⃠e⃠ c⃠y⃠a⃠ t⃠m⃠r⃠",
"o⃠y⃠e⃠e⃠ n⃠y⃠ c⃠p⃠ n⃠y⃠ c⃠r⃠r⃠",
"o⃠y⃠e⃠e⃠ p⃠g⃠l⃠ m⃠t⃠ c⃠r⃠r⃠",
"c⃠u⃠d⃠l⃠e⃠ a⃠r⃠a⃠m⃠ s⃠e⃠ m⃠c⃠",
"p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ r⃠n⃠d⃠i⃠e⃠k⃠",
"c⃠p⃠ c⃠r⃠c⃠e⃠ c⃠h⃠u⃠d⃠e⃠g⃠a⃠ !",
"b⃠a⃠a⃠p⃠ ? m⃠c⃠ m⃠e⃠r⃠a⃠ c⃠o⃠i⃠ m⃠a⃠ b⃠a⃠a⃠p⃠ n⃠y⃠ e⃠y⃠ m⃠a⃠i⃠ u⃠p⃠a⃠r⃠ s⃠e⃠ r⃠o⃠c⃠k⃠e⃠t⃠ p⃠e⃠ b⃠e⃠t⃠h⃠ c⃠e⃠ b⃠s⃠s⃠ t⃠e⃠r⃠i⃠ m⃠a⃠ c⃠h⃠o⃠d⃠n⃠e⃠ a⃠y⃠a⃠ h⃠u⃠",
"C⃠h⃠o⃠t⃠a⃠ l⃠i⃠k⃠h⃠ r⃠n⃠d⃠i⃠ k⃠ b⃠a⃠c⃠h⃠e⃠",
"C⃠h⃠o⃠t⃠a⃠ l⃠i⃠k⃠h⃠a⃠ w⃠r⃠n⃠a⃠ t⃠r⃠y⃠ m⃠a⃠ r⃠n⃠d⃠y⃠",
"T⃠r⃠y⃠ m⃠a⃠ b⃠a⃠k⃠a⃠ c⃠o⃠d⃠e⃠g⃠a⃠",
"T⃠m⃠k⃠c⃠ m⃠a⃠i⃠n⃠ b⃠u⃠r⃠f⃠",
"B⃠h⃠i⃠k⃠a⃠r⃠i⃠ k⃠i⃠ j⃠h⃠a⃠t⃠ m⃠a⃠ c⃠u⃠d⃠a⃠ l⃠e⃠",
"C⃠h⃠o⃠d⃠k⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ m⃠a⃠r⃠j⃠a⃠y⃠e⃠g⃠i⃠",
"T⃠m⃠k⃠c⃠ m⃠a⃠i⃠n⃠ M⃠o⃠u⃠n⃠t⃠ E⃠v⃠e⃠r⃠e⃠s⃠t⃠",
"M⃠u⃠h⃠ m⃠e⃠y⃠ l⃠e⃠g⃠a⃠ l⃠u⃠n⃠d⃠ m⃠e⃠r⃠a⃠",
"H⃠i⃠j⃠d⃠e⃠ k⃠i⃠ j⃠h⃠a⃠t⃠ c⃠h⃠u⃠p⃠ w⃠r⃠n⃠a⃠ t⃠r⃠y⃠ m⃠a⃠ r⃠n⃠d⃠i⃠",
"M⃠e⃠n⃠u⃠ n⃠y⃠ p⃠t⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠",
"M⃠e⃠n⃠u⃠ k⃠i⃠ p⃠t⃠a⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"M⃠e⃠n⃠u⃠ p⃠t⃠a⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"M⃠e⃠n⃠u⃠ s⃠b⃠ p⃠t⃠a⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"M⃠e⃠n⃠u⃠ p⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠",
"R⃠a⃠n⃠d⃠y⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠ m⃠e⃠n⃠u⃠ p⃠t⃠a⃠",
"T⃠e⃠n⃠u⃠ o⃠r⃠ m⃠e⃠n⃠u⃠ p⃠t⃠a⃠ e⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"B⃠s⃠ b⃠s⃠ m⃠a⃠a⃠ c⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠",
"B⃠s⃠ b⃠s⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠ t⃠h⃠n⃠k⃠s⃠s⃠",
"B⃠s⃠ b⃠s⃠ c⃠h⃠u⃠d⃠w⃠a⃠ l⃠i⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ m⃠a⃠a⃠",
"B⃠s⃠ b⃠s⃠ k⃠a⃠m⃠j⃠o⃠r⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"S⃠m⃠j⃠h⃠ g⃠y⃠a⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠b⃠",
"s⃠m⃠j⃠h⃠ g⃠y⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"s⃠m⃠j⃠h⃠ g⃠y⃠a⃠ t⃠u⃠ s⃠a⃠b⃠i⃠t⃠ k⃠r⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"C⃠y⃠a⃠ h⃠u⃠a⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"E⃠a⃠s⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ t⃠u⃠",
"E⃠a⃠s⃠y⃠ w⃠8⃠ m⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ a⃠b⃠",
"S⃠a⃠n⃠s⃠ a⃠r⃠i⃠ h⃠a⃠ k⃠y⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠g⃠i⃠ a⃠j⃠j⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠o⃠ b⃠i⃠n⃠a⃠ s⃠a⃠n⃠s⃠s⃠ l⃠e⃠t⃠e⃠ h⃠u⃠e⃠ c⃠h⃠o⃠d⃠u⃠n⃠g⃠a⃠",
"c⃠h⃠u⃠p⃠ r⃠a⃠n⃠d⃠i⃠k⃠e⃠ k⃠a⃠m⃠j⃠o⃠r⃠",
"a⃠p⃠n⃠i⃠ m⃠a⃠ n⃠o⃠r⃠m⃠i⃠e⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ t⃠u⃠",
"f⃠r⃠ c⃠y⃠a⃠ n⃠o⃠r⃠m⃠i⃠e⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"b⃠a⃠s⃠ t⃠h⃠e⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠",
"b⃠a⃠s⃠ t⃠h⃠e⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠",
"k⃠a⃠m⃠j⃠o⃠r⃠ t⃠h⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ e⃠s⃠l⃠i⃠y⃠e⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"M⃠a⃠i⃠ s⃠b⃠ j⃠a⃠n⃠t⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"c⃠h⃠l⃠ c⃠h⃠l⃠ h⃠t⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠",
"f⃠r⃠ k⃠a⃠i⃠s⃠e⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠",
"m⃠a⃠a⃠ t⃠e⃠r⃠y⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"b⃠a⃠s⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"f⃠r⃠ r⃠a⃠n⃠d⃠y⃠ m⃠a⃠ t⃠e⃠r⃠y⃠ e⃠y⃠",
"K⃠a⃠m⃠j⃠o⃠r⃠ m⃠a⃠ k⃠a⃠ b⃠c⃠h⃠a⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"b⃠h⃠o⃠t⃠ g⃠n⃠d⃠i⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠ k⃠a⃠i⃠s⃠e⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ i⃠t⃠n⃠a⃠ g⃠n⃠d⃠a⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ b⃠t⃠a⃠ r⃠h⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ p⃠t⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"f⃠i⃠r⃠ m⃠u⃠j⃠h⃠e⃠ n⃠y⃠ p⃠t⃠a⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠t⃠a⃠ n⃠y⃠ k⃠o⃠n⃠ c⃠o⃠d⃠ d⃠i⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ k⃠o⃠",
"r⃠u⃠k⃠ a⃠a⃠y⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠o⃠d⃠k⃠e⃠",
"w⃠a⃠i⃠t⃠ c⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠o⃠d⃠ r⃠h⃠a⃠ h⃠u⃠",
"w⃠a⃠i⃠t⃠ c⃠r⃠ r⃠a⃠b⃠d⃠y⃠k⃠e⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ r⃠h⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"w⃠a⃠i⃠t⃠ k⃠r⃠ s⃠m⃠j⃠h⃠ r⃠h⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠o⃠d⃠k⃠e⃠",
"w⃠a⃠i⃠t⃠ l⃠e⃠ t⃠h⃠o⃠d⃠a⃠ c⃠h⃠o⃠d⃠n⃠e⃠ d⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"r⃠u⃠k⃠ j⃠a⃠ a⃠a⃠n⃠d⃠ r⃠k⃠h⃠ d⃠u⃠n⃠g⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ l⃠i⃠y⃠e⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ f⃠a⃠m⃠o⃠u⃠s⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"m⃠a⃠a⃠n⃠ l⃠i⃠a⃠ m⃠e⃠n⃠e⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ s⃠a⃠l⃠i⃠ t⃠e⃠r⃠y⃠",
"m⃠a⃠a⃠n⃠ l⃠i⃠a⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"s⃠h⃠a⃠n⃠t⃠ b⃠e⃠t⃠h⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"s⃠h⃠a⃠n⃠t⃠ b⃠e⃠t⃠h⃠k⃠e⃠ c⃠h⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠k⃠o⃠ t⃠u⃠",
"f⃠r⃠ s⃠e⃠ s⃠h⃠a⃠n⃠t⃠ B⃠e⃠t⃠h⃠ t⃠u⃠ c⃠u⃠d⃠ a⃠b⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ y⃠h⃠a⃠",
"m⃠e⃠r⃠e⃠ s⃠m⃠j⃠h⃠ n⃠y⃠ a⃠y⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"L⃠e⃠ k⃠e⃠l⃠a⃠ K⃠h⃠a⃠ t⃠u⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠o⃠d⃠",
"H⃠y⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ c⃠y⃠a⃠",
"h⃠y⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ m⃠a⃠r⃠ g⃠a⃠i⃠ c⃠y⃠a⃠",
"H⃠y⃠e⃠ s⃠c⃠h⃠ b⃠t⃠a⃠ c⃠o⃠m⃠ c⃠o⃠d⃠ d⃠i⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"C⃠h⃠l⃠ c⃠h⃠o⃠d⃠ d⃠i⃠a⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠o⃠ s⃠m⃠j⃠h⃠l⃠e⃠",
"B⃠a⃠k⃠i⃠ k⃠o⃠i⃠ d⃠i⃠k⃠k⃠a⃠t⃠ n⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"b⃠a⃠k⃠i⃠ s⃠b⃠ j⃠a⃠n⃠t⃠e⃠ e⃠y⃠ k⃠i⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠d⃠k⃠a⃠d⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ p⃠t⃠a⃠ t⃠h⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠n⃠e⃠ w⃠l⃠i⃠ e⃠y⃠",
"p⃠r⃠ m⃠e⃠i⃠ k⃠a⃠i⃠s⃠e⃠ j⃠n⃠t⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ k⃠o⃠ k⃠o⃠i⃠ c⃠h⃠o⃠d⃠ d⃠i⃠a⃠",
"p⃠r⃠ m⃠e⃠r⃠a⃠ v⃠i⃠ m⃠a⃠n⃠n⃠a⃠ s⃠h⃠i⃠ t⃠h⃠a⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠ w⃠o⃠ g⃠l⃠t⃠ n⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"p⃠r⃠ w⃠o⃠ s⃠h⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠d⃠k⃠a⃠d⃠ e⃠y⃠",
"p⃠r⃠ k⃠a⃠i⃠s⃠e⃠ k⃠i⃠a⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ o⃠m⃠f⃠o⃠o⃠",
"b⃠u⃠r⃠ c⃠h⃠e⃠e⃠r⃠ d⃠u⃠n⃠g⃠a⃠ t⃠r⃠i⃠ m⃠a⃠ k⃠a⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠ k⃠e⃠ d⃠i⃠l⃠ m⃠e⃠ l⃠o⃠d⃠a⃠ m⃠a⃠r⃠k⃠e⃠ u⃠s⃠k⃠i⃠ d⃠h⃠a⃠d⃠k⃠a⃠n⃠ r⃠o⃠k⃠ d⃠u⃠n⃠g⃠a⃠",
"l⃠u⃠l⃠l⃠e⃠ k⃠h⃠a⃠ t⃠r⃠i⃠ m⃠a⃠k⃠a⃠b⃠h⃠o⃠s⃠d⃠a⃠",
"t⃠r⃠i⃠ b⃠h⃠n⃠ k⃠i⃠ b⃠h⃠o⃠s⃠d⃠i⃠ b⃠e⃠t⃠a⃠",
"t⃠r⃠i⃠ m⃠a⃠ r⃠n⃠d⃠i⃠ b⃠a⃠a⃠t⃠ k⃠h⃠t⃠m⃠",
"S⃠u⃠n⃠ e⃠k⃠ m⃠a⃠z⃠e⃠ k⃠i⃠ b⃠a⃠a⃠t⃠ b⃠a⃠t⃠a⃠o⃠ k⃠y⃠a⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠"
"c⃠o⃠d⃠u⃠ c⃠o⃠d⃠u⃠ m⃠a⃠k⃠o⃠ t⃠e⃠r⃠y⃠",
"a⃠j⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ o⃠y⃠e⃠",
"s⃠u⃠n⃠ s⃠u⃠n⃠ r⃠a⃠n⃠d⃠y⃠ m⃠a⃠k⃠e⃠ b⃠a⃠c⃠h⃠e⃠ t⃠u⃠",
"k⃠i⃠l⃠a⃠s⃠ n⃠y⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ p⃠t⃠a⃠ t⃠e⃠r⃠y⃠ b⃠h⃠e⃠n⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"p⃠r⃠ p⃠r⃠ c⃠y⃠a⃠ h⃠o⃠t⃠e⃠ e⃠y⃠ t⃠m⃠k⃠c⃠",
"t⃠m⃠c⃠l⃠ s⃠u⃠n⃠l⃠e⃠",
"m⃠o⃠o⃠t⃠ d⃠u⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ m⃠e⃠y⃠",
"b⃠h⃠g⃠n⃠y⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠ f⃠r⃠",
"f⃠r⃠ s⃠e⃠ c⃠u⃠d⃠l⃠e⃠ t⃠u⃠",
"y⃠e⃠ v⃠i⃠ s⃠h⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠k⃠c⃠ b⃠s⃠",
"a⃠j⃠ k⃠u⃠c⃠h⃠ n⃠y⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"t⃠r⃠y⃠ k⃠r⃠ m⃠e⃠r⃠a⃠ l⃠u⃠n⃠d⃠ c⃠h⃠u⃠s⃠k⃠e⃠",
"t⃠o⃠r⃠m⃠a⃠k⃠i⃠b⃠u⃠r⃠ s⃠u⃠n⃠",
"t⃠o⃠r⃠ m⃠a⃠k⃠i⃠ f⃠u⃠d⃠d⃠i⃠ o⃠y⃠e⃠",
"H⃠a⃠y⃠e⃠ H⃠a⃠y⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"o⃠y⃠e⃠ l⃠u⃠n⃠d⃠k⃠e⃠ p⃠a⃠s⃠i⃠n⃠e⃠..",
"k⃠u⃠t⃠t⃠e⃠ k⃠e⃠ t⃠a⃠t⃠t⃠e⃠ s⃠u⃠n⃠",
"k⃠u⃠t⃠t⃠a⃠ j⃠a⃠i⃠s⃠a⃠ c⃠u⃠d⃠ r⃠h⃠a⃠ t⃠u⃠",
"M⃠u⃠h⃠ m⃠e⃠i⃠ l⃠e⃠ m⃠e⃠r⃠a⃠..",
"j⃠h⃠a⃠a⃠t⃠ k⃠e⃠ p⃠i⃠s⃠s⃠u⃠ s⃠u⃠n⃠ t⃠m⃠k⃠c⃠",
"H⃠a⃠h⃠a⃠h⃠h⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"w⃠e⃠a⃠k⃠ t⃠a⃠t⃠t⃠e⃠ u⃠t⃠h⃠",
"w⃠e⃠a⃠k⃠ e⃠y⃠ t⃠u⃠ c⃠u⃠d⃠ r⃠h⃠a⃠",
"w⃠e⃠a⃠k⃠ a⃠c⃠h⃠e⃠ s⃠e⃠ c⃠u⃠d⃠ t⃠u⃠",
"w⃠e⃠a⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ r⃠h⃠i⃠ d⃠e⃠k⃠h⃠",
"w⃠e⃠e⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ a⃠b⃠",
"m⃠u⃠j⃠h⃠e⃠ n⃠y⃠ r⃠o⃠k⃠ t⃠u⃠ w⃠e⃠a⃠k⃠ e⃠y⃠",
"c⃠h⃠u⃠p⃠ h⃠i⃠z⃠d⃠e⃠",
"o⃠k⃠a⃠t⃠ n⃠y⃠ m⃠e⃠r⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"l⃠u⃠n⃠ l⃠e⃠g⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ g⃠a⃠n⃠d⃠ m⃠e⃠i⃠ ?",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ b⃠a⃠c⃠h⃠i⃠ c⃠o⃠d⃠u⃠..",
"t⃠e⃠r⃠y⃠ b⃠h⃠e⃠n⃠ k⃠i⃠ c⃠h⃠u⃠t⃠ a⃠j⃠ f⃠a⃠d⃠ d⃠u⃠",
"s⃠p⃠e⃠e⃠d⃠ l⃠e⃠k⃠r⃠ a⃠a⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"s⃠p⃠e⃠e⃠d⃠ n⃠y⃠ t⃠e⃠r⃠e⃠ a⃠n⃠d⃠r⃠ w⃠e⃠a⃠k⃠ p⃠r⃠o⃠s⃠n⃠",
"u⃠g⃠l⃠y⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠h⃠u⃠p⃠",
"m⃠a⃠k⃠a⃠f⃠u⃠d⃠d⃠a⃠t⃠e⃠r⃠y⃠",
"t⃠e⃠r⃠a⃠ b⃠a⃠a⃠p⃠ k⃠o⃠ t⃠a⃠g⃠ k⃠r⃠..?",
"a⃠c⃠h⃠e⃠ s⃠e⃠ t⃠a⃠g⃠ k⃠r⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠h⃠a⃠g⃠w⃠n⃠ k⃠o⃠..",
"c⃠u⃠d⃠k⃠e⃠ p⃠g⃠l⃠ n⃠y⃠ h⃠o⃠ t⃠u⃠",
"c⃠u⃠d⃠k⃠e⃠ p⃠g⃠l⃠ h⃠o⃠ r⃠h⃠a⃠ t⃠u⃠ k⃠i⃠d⃠",
"m⃠a⃠ t⃠o⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ h⃠a⃠w⃠a⃠b⃠z⃠i⃠ c⃠r⃠..",
"b⃠s⃠ m⃠a⃠ c⃠o⃠d⃠n⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"t⃠o⃠w⃠n⃠ m⃠e⃠i⃠ c⃠u⃠d⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ l⃠e⃠k⃠r⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠ s⃠e⃠x⃠y⃠ k⃠o⃠ b⃠e⃠j⃠ - r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠h⃠g⃠w⃠n⃠ p⃠e⃠",
"s⃠p⃠e⃠e⃠d⃠ p⃠k⃠d⃠ c⃠p⃠ n⃠y⃠ k⃠r⃠",
"T⃠r⃠y⃠ m⃠a⃠ r⃠e⃠n⃠d⃠y⃠",
"B⃠h⃠k⃠k⃠ c⃠u⃠d⃠",
"t⃠e⃠y⃠ m⃠a⃠a⃠ r⃠n⃠d⃠i⃠",
"t⃠e⃠r⃠y⃠ b⃠e⃠h⃠e⃠n⃠ r⃠a⃠n⃠d⃠i⃠",
"C⃠u⃠d⃠ j⃠a⃠",
"t⃠e⃠r⃠y⃠ d⃠i⃠d⃠i⃠ r⃠n⃠d⃠i⃠",
"S⃠l⃠o⃠w⃠",
"t⃠e⃠r⃠i⃠ M⃠a⃠i⃠y⃠a⃠ c⃠i⃠o⃠d⃠u⃠",
"B⃠h⃠a⃠g⃠?",
"B⃠h⃠a⃠k⃠ c⃠u⃠d⃠",
"T⃠m⃠a⃠ c⃠o⃠d⃠u⃠",
"S⃠l⃠o⃠w⃠",
"S⃠l⃠o⃠w⃠ f⃠i⃠r⃠s⃠e⃠",
"C⃠u⃠d⃠g⃠r⃠i⃠b⃠",
"T⃠r⃠y⃠ m⃠a⃠ d⃠o⃠u⃠",
"t⃠b⃠k⃠c⃠ c⃠o⃠d⃠u⃠",
"N⃠e⃠t⃠ o⃠n⃠ o⃠f⃠f⃠ w⃠a⃠l⃠i⃠ r⃠n⃠d⃠y⃠",
"O⃠y⃠e⃠ t⃠r⃠y⃠ m⃠a⃠ c⃠o⃠d⃠u⃠",
"I⃠d⃠h⃠a⃠r⃠ a⃠a⃠k⃠e⃠ c⃠u⃠d⃠ c⃠h⃠u⃠p⃠ c⃠h⃠a⃠a⃠p⃠",
"t⃠b⃠k⃠c⃠ m⃠r⃠d⃠u⃠",
"o⃠i⃠ m⃠a⃠a⃠k⃠e⃠ l⃠o⃠d⃠e⃠e⃠",
"r⃠a⃠n⃠d⃠y⃠k⃠e⃠ b⃠e⃠e⃠j⃠",
"t⃠m⃠k⃠c⃠ c⃠h⃠o⃠d⃠u⃠",
"s⃠u⃠a⃠r⃠ k⃠e⃠ b⃠e⃠e⃠j⃠",
"n⃠e⃠t⃠ o⃠f⃠f⃠ o⃠n⃠ k⃠r⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ l⃠a⃠d⃠k⃠e⃠",
"T⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠i⃠ k⃠e⃠s⃠e⃠",
"C⃠h⃠u⃠p⃠ s⃠l⃠o⃠w⃠ m⃠a⃠d⃠h⃠a⃠r⃠c⃠o⃠d⃠",
"t⃠b⃠k⃠c⃠ c⃠o⃠d⃠u⃠ k⃠r⃠ m⃠s⃠g⃠ d⃠e⃠l⃠e⃠t⃠e⃠",
"o⃠i⃠ s⃠u⃠a⃠r⃠ k⃠e⃠ l⃠a⃠d⃠k⃠e⃠",
"t⃠m⃠k⃠c⃠ f⃠u⃠f⃠i⃠",
"t⃠e⃠r⃠y⃠ d⃠i⃠d⃠i⃠ c⃠h⃠u⃠d⃠i⃠",
"t⃠m⃠k⃠c⃠ d⃠i⃠k⃠h⃠a⃠",
"C⃠u⃠d⃠ a⃠b⃠",
"r⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠u⃠d⃠",
"B⃠h⃠a⃠k⃠ c⃠u⃠d⃠",
"c⃠u⃠d⃠l⃠e⃠ t⃠b⃠k⃠c⃠ m⃠r⃠u⃠",
"t⃠m⃠k⃠l⃠ c⃠u⃠d⃠l⃠e⃠ g⃠r⃠i⃠b⃠",
"t⃠e⃠r⃠y⃠ b⃠e⃠h⃠e⃠n⃠ v⃠e⃠s⃠i⃠y⃠a⃠a⃠ r⃠n⃠d⃠i⃠",
"I⃠t⃠n⃠a⃠ g⃠n⃠d⃠a⃠ c⃠h⃠u⃠d⃠a⃠ t⃠u⃠ f⃠i⃠r⃠s⃠e⃠ n⃠e⃠t⃠ o⃠n⃠ o⃠f⃠f⃠",
"g⃠r⃠i⃠b⃠ k⃠e⃠ b⃠e⃠t⃠e⃠",
"B⃠h⃠a⃠g⃠ j⃠a⃠ l⃠o⃠d⃠e⃠ t⃠m⃠k⃠c⃠ m⃠a⃠r⃠u⃠ d⃠u⃠n⃠g⃠a⃠",
"t⃠b⃠k⃠c⃠ m⃠r⃠d⃠u⃠n⃠g⃠a⃠a⃠",
"b⃠h⃠a⃠g⃠ t⃠m⃠k⃠c⃠",
"b⃠h⃠a⃠g⃠ t⃠b⃠k⃠c⃠",
"t⃠b⃠k⃠c⃠ m⃠e⃠y⃠ c⃠p⃠",
"c⃠p⃠ t⃠b⃠k⃠c⃠ m⃠e⃠h⃠h⃠",
"c⃠p⃠ t⃠m⃠k⃠l⃠ m⃠e⃠h⃠",
"c⃠p⃠ b⃠o⃠l⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"A⃠b⃠e⃠ c⃠p⃠ b⃠o⃠l⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"d⃠o⃠u⃠b⃠l⃠e⃠ s⃠e⃠n⃠d⃠ k⃠o⃠ c⃠p⃠ t⃠m⃠k⃠c⃠ c⃠o⃠d⃠u⃠",
"t⃠b⃠k⃠c⃠ m⃠e⃠ c⃠p⃠ c⃠o⃠d⃠ d⃠u⃠n⃠g⃠a⃠ A⃠a⃠j⃠ m⃠e⃠h⃠h⃠",
"h⃠t⃠ t⃠b⃠k⃠c⃠ d⃠a⃠l⃠a⃠l⃠ k⃠e⃠ b⃠e⃠t⃠e⃠.",
"R⃠n⃠d⃠y⃠ j⃠l⃠d⃠i⃠ j⃠l⃠d⃠i⃠ c⃠u⃠d⃠q⃠ t⃠r⃠y⃠m⃠a⃠",
"P⃠a⃠r⃠a⃠ l⃠i⃠k⃠h⃠e⃠g⃠a⃠..",
"T⃠r⃠a⃠ r⃠n⃠d⃠h⃠b⃠h⃠a⃠k⃠",
"L⃠a⃠g⃠d⃠i⃠ k⃠e⃠ l⃠a⃠d⃠c⃠e⃠ c⃠p⃠ b⃠o⃠l⃠",
"c⃠p⃠ b⃠o⃠l⃠ l⃠a⃠g⃠d⃠i⃠ k⃠e⃠ b⃠e⃠t⃠e⃠..",
"c⃠u⃠d⃠k⃠e⃠ c⃠p⃠ b⃠o⃠l⃠",
"b⃠h⃠i⃠k⃠a⃠r⃠i⃠ l⃠u⃠n⃠d⃠ c⃠h⃠u⃠s⃠ m⃠e⃠r⃠a⃠.",
"L⃠o⃠w⃠ l⃠e⃠v⃠e⃠l⃠ c⃠p⃠ c⃠r⃠",
"c⃠p⃠ b⃠o⃠l⃠ l⃠o⃠w⃠ l⃠e⃠v⃠e⃠l⃠ w⃠e⃠a⃠k⃠",
"m⃠e⃠r⃠e⃠ l⃠u⃠n⃠d⃠ p⃠e⃠ e⃠y⃠ t⃠u⃠ h⃠i⃠j⃠d⃠e⃠",
"f⃠r⃠e⃠e⃠ c⃠u⃠d⃠w⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"F⃠r⃠e⃠e⃠ m⃠e⃠y⃠ c⃠u⃠d⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠"
"s⃠p⃠e⃠e⃠d⃠ n⃠y⃠ w⃠e⃠a⃠k⃠ t⃠a⃠t⃠t⃠e⃠ t⃠e⃠r⃠m⃠e⃠",
"k⃠i⃠t⃠n⃠i⃠ b⃠r⃠ c⃠u⃠d⃠w⃠a⃠y⃠e⃠g⃠a⃠ t⃠e⃠r⃠y⃠m⃠a⃠k⃠o⃠",
"l⃠u⃠n⃠d⃠ l⃠e⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠a⃠p⃠k⃠a⃠",
"l⃠u⃠n⃠ c⃠u⃠s⃠ j⃠a⃠l⃠d⃠i⃠ s⃠e⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠a⃠p⃠k⃠a⃠",
"k⃠o⃠i⃠ n⃠y⃠ d⃠e⃠k⃠h⃠ r⃠h⃠a⃠ c⃠u⃠d⃠l⃠e⃠ t⃠u⃠",
"c⃠u⃠d⃠l⃠e⃠ b⃠e⃠t⃠i⃠c⃠h⃠o⃠d⃠ a⃠c⃠h⃠e⃠ s⃠e⃠",
"m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ t⃠e⃠r⃠y⃠ b⃠s⃠ y⃠e⃠h⃠i⃠ j⃠a⃠n⃠t⃠a⃠ m⃠e⃠y⃠",
"c⃠p⃠ b⃠o⃠l⃠e⃠g⃠a⃠ t⃠o⃠ t⃠m⃠k⃠c⃠",
"w⃠r⃠n⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ j⃠a⃠y⃠e⃠g⃠i⃠",
"s⃠l⃠o⃠w⃠ e⃠y⃠ t⃠u⃠ k⃠i⃠d⃠",
"j⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠..t⃠m⃠k⃠c⃠",
"j⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠..r⃠a⃠n⃠d⃠c⃠e⃠ t⃠u⃠",
"t⃠y⃠m⃠ s⃠e⃠ p⃠h⃠l⃠e⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"t⃠y⃠m⃠ h⃠o⃠g⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠w⃠a⃠",
"m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ t⃠y⃠m⃠ s⃠e⃠ p⃠h⃠l⃠e⃠",
"u⃠t⃠h⃠ r⃠a⃠n⃠d⃠c⃠e⃠ k⃠e⃠ l⃠d⃠k⃠e⃠",
"m⃠a⃠c⃠a⃠b⃠o⃠s⃠d⃠a⃠t⃠e⃠r⃠y⃠",
"c⃠o⃠n⃠ k⃠b⃠ c⃠o⃠d⃠ d⃠i⃠a⃠ m⃠a⃠k⃠o⃠ t⃠e⃠r⃠y⃠",
"k⃠o⃠i⃠ h⃠o⃠g⃠a⃠ t⃠m⃠l⃠",
"m⃠a⃠c⃠h⃠a⃠r⃠ c⃠u⃠d⃠l⃠e⃠ t⃠u⃠",
"m⃠e⃠n⃠u⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ c⃠o⃠d⃠n⃠a⃠ s⃠e⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ b⃠o⃠l⃠ m⃠u⃠j⃠h⃠e⃠ c⃠o⃠d⃠ d⃠e⃠",
"b⃠s⃠ m⃠e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ s⃠e⃠ c⃠u⃠d⃠n⃠a⃠ c⃠h⃠t⃠a⃠ h⃠u⃠",
"E⃠w⃠w⃠ m⃠a⃠k⃠a⃠ l⃠o⃠d⃠e⃠ u⃠t⃠h⃠",
"M⃠e⃠o⃠w⃠ c⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ c⃠o⃠d⃠u⃠",
"l⃠u⃠n⃠d⃠ r⃠k⃠h⃠ d⃠i⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ f⃠u⃠d⃠e⃠ p⃠e⃠",
"m⃠e⃠r⃠a⃠ l⃠u⃠n⃠d⃠ k⃠e⃠ b⃠a⃠l⃠ u⃠t⃠h⃠",
"k⃠i⃠d⃠e⃠e⃠ Z⃠i⃠n⃠d⃠a⃠ h⃠o⃠",
"m⃠a⃠r⃠ n⃠y⃠ k⃠i⃠d⃠d⃠e⃠ t⃠y⃠p⃠e⃠ k⃠r⃠",
"c⃠h⃠u⃠p⃠ b⃠k⃠l⃠",
"b⃠c⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠",
"m⃠c⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ l⃠i⃠k⃠h⃠ f⃠a⃠s⃠t⃠",
"f⃠a⃠s⃠t⃠ l⃠i⃠k⃠h⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"f⃠a⃠s⃠t⃠ l⃠i⃠k⃠h⃠ k⃠a⃠m⃠z⃠o⃠r⃠"
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ c⃠l⃠a⃠i⃠m⃠ c⃠r⃠w⃠a⃠",
"a⃠w⃠z⃠ n⃠i⃠c⃠h⃠e⃠ r⃠a⃠n⃠d⃠c⃠e⃠ k⃠e⃠ b⃠c⃠h⃠e⃠",
"s⃠a⃠w⃠a⃠l⃠ n⃠y⃠ p⃠u⃠c⃠h⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠a⃠b⃠o⃠s⃠d⃠a⃠",
"f⃠y⃠t⃠e⃠r⃠ b⃠n⃠e⃠g⃠a⃠ l⃠a⃠g⃠d⃠e⃠ m⃠a⃠d⃠r⃠c⃠h⃠o⃠d⃠",
"o⃠y⃠e⃠ k⃠a⃠a⃠l⃠e⃠ r⃠o⃠ k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"o⃠y⃠e⃠ k⃠a⃠a⃠l⃠e⃠ r⃠o⃠o⃠ n⃠y⃠",
"s⃠h⃠o⃠r⃠t⃠ n⃠y⃠ c⃠u⃠d⃠ t⃠u⃠ b⃠i⃠n⃠a⃠ r⃠u⃠k⃠e⃠",
"s⃠h⃠o⃠r⃠t⃠ n⃠y⃠ c⃠u⃠d⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ m⃠a⃠k⃠o⃠ l⃠e⃠k⃠r⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ s⃠t⃠h⃠ t⃠e⃠r⃠y⃠ b⃠h⃠e⃠n⃠ v⃠i⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ s⃠t⃠h⃠ t⃠e⃠r⃠y⃠ d⃠i⃠d⃠i⃠ v⃠i⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"C⃠h⃠a⃠t⃠ f⃠y⃠t⃠e⃠r⃠ b⃠n⃠e⃠g⃠a⃠ r⃠a⃠n⃠d⃠c⃠e⃠ c⃠o⃠d⃠u⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"b⃠o⃠l⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ d⃠a⃠d⃠d⃠y⃠ e⃠y⃠",
"b⃠u⃠l⃠l⃠y⃠x⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ u⃠t⃠h⃠",
"m⃠a⃠r⃠ m⃠a⃠r⃠k⃠e⃠ c⃠u⃠d⃠ r⃠h⃠a⃠ t⃠u⃠",
"o⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ m⃠a⃠r⃠k⃠e⃠ c⃠u⃠d⃠ g⃠a⃠i⃠"
"J⃠a⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ r⃠n⃠d⃠y⃠k⃠e⃠ b⃠e⃠j⃠",
"O⃠r⃠ b⃠d⃠a⃠ l⃠i⃠k⃠h⃠ t⃠m⃠c⃠",
"O⃠r⃠ b⃠d⃠a⃠ 2⃠ l⃠i⃠n⃠e⃠ w⃠l⃠a⃠ l⃠i⃠k⃠h⃠ t⃠m⃠k⃠c⃠",
"O⃠r⃠ b⃠d⃠a⃠ o⃠y⃠e⃠ l⃠i⃠k⃠h⃠ t⃠m⃠l⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠a⃠ b⃠u⃠r⃠",
"O⃠y⃠e⃠ k⃠e⃠e⃠d⃠e⃠",
"R⃠a⃠n⃠d⃠i⃠ k⃠e⃠ l⃠a⃠d⃠k⃠e⃠",
"J⃠a⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ t⃠e⃠r⃠i⃠ b⃠e⃠h⃠e⃠n⃠ c⃠h⃠o⃠d⃠u⃠",
"M⃠k⃠l⃠ u⃠t⃠h⃠ r⃠a⃠n⃠d⃠i⃠ k⃠e⃠ b⃠a⃠c⃠c⃠h⃠e⃠",
"T⃠e⃠r⃠i⃠ n⃠a⃠n⃠i⃠ m⃠e⃠r⃠i⃠ m⃠a⃠a⃠l⃠",
"T⃠e⃠j⃠ l⃠i⃠k⃠h⃠ r⃠a⃠n⃠d⃠c⃠e⃠",
"O⃠y⃠e⃠ m⃠a⃠a⃠k⃠e⃠ l⃠o⃠d⃠e⃠ m⃠r⃠e⃠n⃠g⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠y⃠",
"T⃠e⃠r⃠i⃠ M⃠a⃠i⃠y⃠a⃠ k⃠i⃠ g⃠a⃠n⃠d⃠",
"T⃠e⃠r⃠y⃠ d⃠a⃠d⃠i⃠ k⃠a⃠ f⃠u⃠d⃠d⃠a⃠",
"M⃠k⃠l⃠ u⃠t⃠h⃠ b⃠e⃠h⃠e⃠n⃠c⃠o⃠d⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠i⃠ b⃠u⃠r⃠ d⃠e⃠",
"T⃠e⃠r⃠y⃠ m⃠a⃠a⃠ k⃠a⃠ f⃠u⃠d⃠d⃠a⃠ m⃠e⃠ l⃠a⃠u⃠d⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠v⃠a⃠",
"R⃠a⃠n⃠d⃠i⃠ k⃠e⃠ b⃠e⃠t⃠e⃠ m⃠a⃠r⃠ g⃠a⃠y⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠i⃠ c⃠h⃠u⃠t⃠ m⃠r⃠u⃠",
"J⃠a⃠l⃠i⃠d⃠ k⃠r⃠ s⃠p⃠a⃠m⃠",
"M⃠c⃠ s⃠p⃠a⃠m⃠ r⃠o⃠k⃠e⃠n⃠g⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ s⃠p⃠a⃠m⃠ k⃠r⃠",
"s⃠p⃠a⃠m⃠ k⃠r⃠.⃠m⃠a⃠a⃠k⃠e⃠ l⃠o⃠d⃠e⃠",
"R⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠h⃠o⃠d⃠e⃠ s⃠p⃠a⃠m⃠ k⃠r⃠ w⃠r⃠n⃠a⃠ c⃠u⃠d⃠ t⃠u⃠",
"S⃠p⃠a⃠m⃠ k⃠r⃠ k⃠i⃠d⃠",
"N⃠o⃠o⃠b⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠u⃠",
"R⃠n⃠d⃠y⃠k⃠e⃠ b⃠e⃠t⃠e⃠ m⃠a⃠r⃠ m⃠a⃠t⃠ t⃠u⃠",
"N⃠o⃠o⃠b⃠ j⃠a⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ w⃠r⃠n⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠",
"c⃠u⃠d⃠ g⃠a⃠i⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠ n⃠o⃠o⃠b⃠",
"u⃠t⃠h⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ n⃠o⃠o⃠b⃠",
"c⃠h⃠l⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠ n⃠o⃠o⃠b⃠",
"j⃠l⃠d⃠i⃠ t⃠y⃠p⃠ c⃠r⃠ n⃠o⃠o⃠b⃠ h⃠a⃠l⃠k⃠e⃠",
"c⃠u⃠d⃠ k⃠e⃠ p⃠g⃠l⃠ n⃠y⃠ h⃠o⃠ n⃠o⃠o⃠b⃠",
"c⃠u⃠d⃠ c⃠u⃠d⃠ k⃠e⃠ r⃠a⃠n⃠d⃠ b⃠n⃠j⃠a⃠ t⃠u⃠ n⃠o⃠o⃠b⃠",
"m⃠a⃠k⃠i⃠c⃠h⃠u⃠t⃠ t⃠e⃠r⃠y⃠ n⃠o⃠o⃠b⃠",
"g⃠a⃠n⃠d⃠a⃠ c⃠y⃠u⃠ c⃠u⃠d⃠ r⃠h⃠a⃠ t⃠u⃠ ?",
"i⃠t⃠n⃠a⃠ g⃠n⃠d⃠a⃠ n⃠y⃠ c⃠u⃠d⃠ a⃠c⃠h⃠e⃠ s⃠e⃠ c⃠u⃠d⃠",
"M⃠a⃠a⃠n⃠ l⃠e⃠ c⃠u⃠d⃠ g⃠y⃠a⃠ t⃠u⃠ s⃠u⃠n⃠ b⃠a⃠t⃠ a⃠b⃠",
"m⃠a⃠k⃠a⃠f⃠u⃠d⃠d⃠a⃠ f⃠a⃠t⃠ g⃠y⃠a⃠ t⃠e⃠r⃠y⃠ r⃠u⃠k⃠",
]
br_texts = [
"ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝓃ᕗᕙ𝒶ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝒯ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓏ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓎ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝒹ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝒯ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙℳᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓎ᕗᕙ𝓂ᕗᕙ𝓅ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝓈ᕗ",
"ᕙ𝒪ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓊ᕗᕙ𝓃ᕗᕙ𝒻ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗᕙ𝓉ᕗ ᕙ𝓀ᕗᕙ𝓇ᕗ",
"ᕙ𝒪ᕗᕙ𝒽ᕗ ᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓁ᕗᕙ𝓁ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓋ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒶ᕗᕙ𝓊ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝓇ᕗ.",
"ᕙ𝒪ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝓃ᕗᕙ𝓃ᕗᕙ𝑒ᕗᕙ𝓇ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙℊᕗᕙ𝒸ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗ ᕙ𝓅ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓂ᕗᕙ𝒾ᕗᕙ𝓈ᕗᕙ𝓈ᕗᕙ𝒾ᕗᕙ𝑜ᕗᕙ𝓃ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝓈ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗ.",
"ᕙ𝒞ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ",
"ᕙ𝒞ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓇ᕗ.",
"ᕙ𝒮ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝒮ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ.",
"ᕙ𝒯ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝒶ᕗ.",
"ᕙ𝒪ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ.",
"ᕙ𝒦ᕗᕙ𝓎ᕗ? ᕙ𝒿ᕗᕙ𝓁ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒹ᕗᕙ𝑒ᕗ.",
"ᕙℬᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝑜ᕗᕙ𝓂ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙℊᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓀ᕗᕙ𝑜ᕗ ᕙ𝓉ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ",
"ᕙℳᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓀ᕗᕙ𝒸ᕗ ᕙ𝒷ᕗᕙ𝓈ᕗ",
"ᕙ𝒥ᕗᕙ𝒶ᕗᕙ𝓁ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓏ᕗ ᕙ𝓅ᕗᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ",
"ᕙ𝒮ᕗᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒿ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝒶ᕗᕙ𝒷ᕗ",
"ᕙℋᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙℊᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ",
"ᕙ𝒷ᕗᕙ𝒽ᕗᕙℊᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝒿ᕗᕙ𝒿ᕗ",
"ᕙℋᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓉ᕗ",
"ᕙℋᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓇ᕗ ᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝓉ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝒽ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓀ᕗᕙ𝑜ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓈ᕗᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒻ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗ ᕙ𝓇ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝒽ᕗᕙ𝓊ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓀ᕗᕙ𝑜ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒻ᕗᕙ𝒾ᕗ ᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙℊᕗᕙ𝒶ᕗ",
"ᕙ𝒜ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ??ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒻ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒾ᕗᕙ𝓁ᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝒜ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙℱᕗᕙ𝓇ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝒞ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ",
"ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝓉ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝓉ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ",
"ᕙ𝓁ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓊ᕗᕙ𝓉ᕗᕙ𝓇ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝓁ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓈ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒶ᕗ",
"ᕙ𝓃ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒹ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝒽ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓉ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗ ᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝒽ᕗ ᕙ𝓉ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝒽ᕗ ᕙ𝓀ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓀ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝒻ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙℊᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝒶ᕗᕙ??ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓀ᕗᕙ𝑜ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝑒ᕗᕙ𝓇ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒿ᕗᕙ𝓁ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓌ᕗᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝒮ᕗᕙ𝓂ᕗᕙ𝒿ᕗᕙ𝒽ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝒻ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝓉ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝒿ᕗᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗᕙ𝒿ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝓏ᕗᕙ𝑜ᕗᕙ𝓇ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝑜ᕗ ᕙ𝒾ᕗᕙ𝓁ᕗᕙ𝓎ᕗ ᕙ𝓇ᕗᕙ𝑒ᕗᕙ𝓎ᕗ 🌚😂",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓀ᕗᕙ𝒸ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ",
"ᕙ𝓈ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ",
"ᕙ𝒻ᕗᕙ𝓇ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ??ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ",
"ᕙ𝓈ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗ ᕙ𝓌ᕗᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝓊ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗᕙ𝑜ᕗᕙ𝑜ᕗᕙ𝒻ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗᕙ𝑜ᕗᕙ𝑜ᕗᕙ𝒻ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗᕙ𝑜ᕗᕙ𝑜ᕗᕙ𝒻ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒾ᕗᕙ𝓁ᕗᕙ𝓁ᕗᕙ𝒶ᕗᕙ𝓇ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ??ᕗᕙ𝓎ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗᕙ𝒿ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝓏ᕗᕙ𝑜ᕗᕙ𝓇ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝓇ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗ ?",
"ᕙ𝒶ᕗᕙ𝒷ᕗ ᕙ𝓉ᕗᕙ𝓀ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ?",
"ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝓊ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝓉ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝓈ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ",
"ᕙ𝒮ᕗᕙ𝒷ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗ ᕙ𝓀ᕗᕙ𝓇ᕗᕙ𝑒ᕗ",
"ᕙ𝓎ᕗᕙ𝒶ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝒸ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝒾ᕗᕙ𝓁ᕗᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝒶ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓃ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒾ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝑜ᕗᕙ𝓂ᕗᕙ𝓂ᕗᕙ𝓎ᕗ",
"ᕙ𝓃ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒹ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓎ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ",
"ᕙ𝒸ᕗᕙ𝑜ᕗᕙ𝓏ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝒿ᕗᕙ𝑜ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝒿ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ",
"ᕙ𝓉ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝓂ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝑒ᕗᕙ𝓂ᕗᕙ𝑜ᕗᕙ𝒿ᕗᕙ𝒾ᕗ ᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓂ᕗᕙ𝓇ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ?",
"ᕙ𝓉ᕗᕙ𝓂ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝒻ᕗᕙ𝓇ᕗᕙ𝓇ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝓀ᕗᕙ𝒷ᕗ ? ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗᕙ𝓀ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ",
"ᕙ𝒾ᕗᕙ𝓉ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓃ᕗᕙ??ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓈ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝓉ᕗᕙ𝒽ᕗ",
"ᕙ𝓂ᕗᕙ𝓉ᕗᕙ𝓁ᕗᕙ𝒷ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝓅ᕗᕙ𝓊ᕗᕙ𝓇ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ ᕙ𝒻ᕗᕙ𝓇ᕗᕙ𝓇ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝑜ᕗᕙ𝒽ᕗ ᕙ𝑜ᕗᕙ𝓀ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒻ᕗᕙ𝒾ᕗᕙ𝓇ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝑒ᕗᕙ𝒽ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝑒ᕗᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓋ᕗᕙ𝓎ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝓉ᕗ ᕙ𝒽ᕗᕙ𝓊ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝓊ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒶ᕗ ?",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ ᕙ𝒽ᕗᕙ𝓈ᕗᕙ𝓈ᕗ",
"ᕙ𝓎ᕗᕙ𝓊ᕗᕙ𝓇ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝑜ᕗᕙ𝓂ᕗ",
"ᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝒷ᕗᕙ𝓀ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗ",
"ᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓇ᕗ",
"ᕙ𝓉ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓇ᕗᕙ𝒽ᕗ",
"ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝒬ᕗ",
"ᕙ𝑜ᕗᕙ𝒸ᕗᕙ𝓎ᕗ ᕙ𝒶ᕗᕙ𝒷ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝓅ᕗᕙ𝑒ᕗᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝓊ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝓆ᕗ ?",
"ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓇ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝒹ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝓉ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝒿ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝒻ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓇ᕗ ᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙℊᕗᕙ𝒶ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ ᕙ𝒻ᕗᕙ𝓇ᕗᕙ𝓇ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒶ᕗᕙ𝑒ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒶ᕗᕙ𝒾ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝓃ᕗᕙ𝒶ᕗ",
"ᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝑜ᕗᕙ𝓇ᕗ",
"ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝑜ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝑜ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝑜ᕗ",
"ᕙ𝒷ᕗᕙ𝓎ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ?",
"ᕙ𝒬ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝒬ᕗ ᕙ𝓇ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗ ?",
"ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ",
]
br2_texts = [
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇸​⋰⋰🇪​⋰⋰🇼​⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰⋰🇰​⋰⋰🇪​⋰⋰🇧​⋰⋰🇦​⋰⋰🇨​⋰⋰🇭​⋰⋰🇪​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇮​⋰⋰🇸​⋰⋰🇸​⋰⋰🇦​⋰⋰🇬​⋰⋰🇦​⋰",
"⋰🇦​⋰⋰🇦​⋰⋰🇯​⋰ ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇭​⋰⋰🇦​⋰⋰🇮​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇩​⋰⋰🇷​⋰⋰🇨​⋰⋰🇭​⋰⋰🇴​⋰⋰🇩​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇰​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇯​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇸​⋰⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇮​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇸​⋰⋰🇰​⋰⋰🇹​⋰⋰🇦​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇸​⋰⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇫​⋰⋰🇮​⋰⋰🇷​⋰⋰🇸​⋰⋰🇪​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰, ⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰ ⋰🇩​⋰⋰🇴​⋰⋰🇺​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰ ⋰🇼​⋰⋰🇦​⋰⋰🇱​⋰⋰🇮​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰",
"⋰🇴​⋰⋰🇾​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇮​⋰⋰🇩​⋰⋰🇭​⋰⋰🇦​⋰⋰🇷​⋰ ⋰🇦​⋰⋰🇦​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇴​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇦​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇩​⋰⋰🇪​⋰⋰🇪​⋰",
"⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇪​⋰⋰🇯​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇸​⋰⋰🇺​⋰⋰🇦​⋰⋰🇷​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇪​⋰⋰🇯​⋰, ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇰​⋰⋰🇷​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰⋰🇸​⋰⋰🇪​⋰, ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇵​⋰ ⋰🇸​⋰⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇩​⋰⋰🇭​⋰⋰🇦​⋰⋰🇷​⋰⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇷​⋰ ⋰🇲​⋰⋰🇸​⋰⋰🇬​⋰ ⋰🇩​⋰⋰🇪​⋰⋰🇱​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰, ⋰🇴​⋰⋰🇮​⋰ ⋰🇸​⋰⋰🇺​⋰⋰🇦​⋰⋰🇷​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇫​⋰⋰🇺​⋰⋰🇫​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇦​⋰, ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇦​⋰⋰🇧​⋰",
"⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇺​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇮​⋰⋰🇹​⋰⋰🇳​⋰⋰🇦​⋰ ⋰🇬​⋰⋰🇳​⋰⋰🇩​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇫​⋰⋰🇮​⋰⋰🇷​⋰⋰🇸​⋰⋰🇪​⋰ ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰",
"⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇯​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇩​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇷​⋰⋰🇺​⋰ ⋰🇩​⋰⋰🇺​⋰⋰??​⋰⋰🇬​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰⋰🇦​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰, ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇵​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰, ⋰🇦​⋰⋰🇧​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇩​⋰⋰🇴​⋰⋰🇺​⋰⋰🇧​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇸​⋰⋰🇪​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇰​⋰⋰🇴​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰ ⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰ ⋰🇦​⋰⋰🇦​⋰⋰🇯​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰",
"⋰🇭​⋰⋰🇹​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇦​⋰⋰🇱​⋰⋰🇦​⋰⋰🇱​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰., ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇶​⋰ ⋰🇹​⋰⋰??​⋰⋰🇾​⋰⋰🇲​⋰⋰🇦​⋰",
"⋰🇵​⋰⋰🇦​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇪​⋰⋰🇬​⋰⋰🇦​⋰.., ⋰🇹​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇭​⋰⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰",
"⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇨​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰..",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰⋰🇰​⋰⋰🇦​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇸​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇦​⋰.",
"⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇷​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇼​⋰⋰🇪​⋰⋰🇦​⋰⋰🇰​⋰",
"⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇵​⋰⋰🇪​⋰ ⋰🇪​⋰⋰🇾​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇭​⋰⋰🇮​⋰⋰🇯​⋰⋰🇩​⋰⋰🇪​⋰, ⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇼​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇴​⋰",
"⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇭​⋰⋰🇦​⋰⋰🇮​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰ ⋰🇨​⋰⋰🇱​⋰⋰🇦​⋰⋰🇮​⋰⋰🇲​⋰ ⋰🇨​⋰⋰🇷​⋰⋰🇼​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇸​⋰⋰🇰​⋰⋰🇹​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇯​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇦​⋰",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇦​⋰⋰🇧​⋰, ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰, ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇺​⋰",
"⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇬​⋰⋰🇷​⋰⋰??​⋰⋰🇧​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇮​⋰⋰🇹​⋰⋰🇳​⋰⋰🇦​⋰ ⋰🇬​⋰⋰🇳​⋰⋰🇩​⋰⋰??​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇫​⋰⋰🇮​⋰⋰🇷​⋰⋰🇸​⋰⋰🇪​⋰ ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰, ⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇯​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇩​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇷​⋰⋰🇺​⋰ ⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰⋰🇦​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇵​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇦​⋰⋰🇧​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰, ⋰🇩​⋰⋰🇴​⋰⋰🇺​⋰⋰🇧​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇸​⋰⋰🇪​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇰​⋰⋰🇴​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰ ⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰ ⋰🇦​⋰⋰🇦​⋰⋰🇯​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰, ⋰🇭​⋰⋰🇹​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇦​⋰⋰🇱​⋰⋰🇦​⋰⋰🇱​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰.",
"⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇶​⋰ ⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰⋰🇲​⋰⋰🇦​⋰, ⋰🇵​⋰⋰🇦​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇪​⋰⋰🇬​⋰⋰🇦​⋰..",
"⋰🇹​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇭​⋰⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰, ⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇨​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰.., ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰⋰🇰​⋰⋰🇦​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇸​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇦​⋰., ⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇷​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇼​⋰⋰🇪​⋰⋰🇦​⋰⋰🇰​⋰, ⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇵​⋰⋰🇪​⋰ ⋰🇪​⋰⋰🇾​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇭​⋰⋰🇮​⋰⋰🇯​⋰⋰🇩​⋰⋰🇪​⋰",
"⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇼​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰??​⋰⋰🇦​⋰⋰🇰​⋰⋰🇴​⋰, ⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰ ⋰🇨​⋰⋰🇱​⋰⋰🇦​⋰⋰🇮​⋰⋰🇲​⋰ ⋰🇨​⋰⋰🇷​⋰⋰🇼​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇸​⋰⋰🇰​⋰⋰🇹​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇯​⋰⋰🇦​⋰"
"⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇫⋰⋰🇦⋰⋰🇹⋰⋰🇮⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇭⋰⋰🇴⋰⋰🇯⋰⋰🇦⋰",
"⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰",
"⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇳⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇲⋰⋰🇦⋰⋰🇷⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰??⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇩⋰⋰🇮⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇧⋰⋰🇭⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇳⋰⋰🇪⋰⋰🇹⋰ ⋰🇴⋰⋰🇫⋰⋰🇫⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰, ⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰??⋰⋰🇰⋰⋰🇨⋰ ⋰🇲⋰⋰🇦⋰⋰🇷⋰⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇹⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇬⋰⋰🇷⋰⋰🇮⋰⋰🇧⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰, ⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇩⋰⋰🇴⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇳⋰⋰🇦⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇵⋰⋰🇺⋰⋰🇷⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇪⋰⋰🇨⋰⋰🇭⋰ ⋰🇩⋰⋰🇴⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇴⋰⋰🇩⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰🇴⋰",
"⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇦⋰⋰🇩⋰⋰🇮⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰",
"⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰🇹⋰⋰🇾⋰⋰🇵⋰⋰🇪⋰⋰🇷⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰??⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇦⋰⋰🇦⋰⋰🇯⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇲⋰⋰🇪⋰⋰🇮⋰⋰🇳⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇸⋰⋰🇰⋰⋰🇹⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇷⋰⋰🇨⋰⋰🇴⋰⋰🇩⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇩⋰⋰🇮⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇧⋰⋰🇭⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇳⋰⋰🇪⋰⋰🇹⋰ ⋰🇴⋰⋰🇫⋰⋰🇫⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰, ⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇲⋰⋰🇦⋰⋰🇷⋰⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇹⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰??⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇬⋰⋰🇷⋰⋰🇮⋰⋰🇧⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰, ⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇩⋰⋰🇴⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇳⋰⋰🇦⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇵⋰⋰🇺⋰⋰🇷⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇪⋰⋰🇨⋰⋰🇭⋰ ⋰🇩⋰⋰🇴⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇴⋰⋰🇩⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰🇴⋰",
"⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇦⋰⋰🇩⋰⋰🇮⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰",
"⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰🇹⋰⋰🇾⋰⋰🇵⋰⋰🇪⋰⋰🇷⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇦⋰⋰🇦⋰⋰🇯⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰??⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇲⋰⋰🇪⋰⋰🇮⋰⋰🇳⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇸⋰⋰🇰⋰⋰🇹⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇷⋰⋰🇨⋰⋰🇴⋰⋰🇩⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇩⋰⋰🇮⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇧⋰⋰🇭⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰"
"⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇧⋰⋰🇳⋰⋰🇦⋰⋰🇱⋰⋰🇪⋰ ⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇪⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇦⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇿⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇾⋰⋰🇦⋰⋰🇦⋰⋰🇩⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰ ⋰🇳⋰⋰🇦⋰ ⋰🇹⋰⋰🇾⋰⋰🇲⋰⋰🇵⋰⋰🇦⋰⋰🇸⋰⋰🇸⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇺⋰⋰🇳⋰⋰🇫⋰⋰🇺⋰⋰🇳⋰⋰🇳⋰⋰🇾⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇲⋰⋰🇹⋰⋰🇹⋰ ⋰🇰⋰⋰🇷⋰",
"⋰🇴⋰⋰🇭⋰ ⋰🇭⋰⋰🇪⋰⋰🇱⋰⋰🇱⋰⋰🇴⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇦⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇴⋰⋰🇷⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇻⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇦⋰⋰🇺⋰⋰🇰⋰⋰🇦⋰⋰🇹⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇷⋰⋰🇭⋰⋰🇦⋰ ⋰🇰⋰⋰🇷⋰.",
"⋰🇴⋰⋰🇾⋰⋰🇾⋰ ⋰🇰⋰⋰🇮⋰⋰🇳⋰⋰🇳⋰⋰🇪⋰⋰🇷⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰ ⋰🇬⋰⋰🇨⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇦⋰⋰🇦⋰⋰🇳⋰⋰🇪⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇵⋰⋰🇪⋰⋰🇷⋰⋰🇲⋰⋰🇮⋰⋰🇸⋰⋰🇸⋰⋰🇮⋰⋰🇴⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰⋰🇸⋰⋰🇳⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰.",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰⋰🇦⋰",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰⋰🇦⋰ ⋰🇪⋰⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇷⋰.",
"⋰🇸⋰⋰🇺⋰⋰🇳⋰ ⋰🇸⋰⋰🇺⋰⋰🇳⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰.",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰??⋰ ⋰🇲⋰⋰🇦⋰⋰🇨⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰.",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇹⋰⋰🇮⋰ ⋰🇯⋰⋰🇦⋰⋰🇹⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰.",
"⋰🇰⋰⋰🇾⋰? ⋰🇯⋰⋰🇱⋰⋰🇩⋰⋰🇮⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰ ⋰🇰⋰⋰🇮⋰⋰🇩⋰⋰🇩⋰⋰🇪⋰.",
"⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇨⋰⋰🇴⋰⋰🇲⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇬⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇰⋰⋰🇴⋰ ⋰🇹⋰⋰🇦⋰⋰🇬⋰ ⋰🇨⋰⋰🇷⋰⋰🇪⋰⋰🇬⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰",
"⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇧⋰⋰🇸⋰",
"⋰🇯⋰⋰🇦⋰⋰🇱⋰⋰🇩⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇿⋰ ⋰🇵⋰⋰🇦⋰⋰🇵⋰⋰🇦⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰",
"⋰🇸⋰⋰🇮⋰⋰🇩⋰⋰🇪⋰ ⋰🇭⋰⋰🇴⋰⋰🇯⋰⋰🇦⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇦⋰⋰🇧⋰",
"⋰🇭⋰⋰🇾⋰⋰🇪⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇧⋰⋰🇭⋰⋰🇬⋰ ⋰🇲⋰⋰🇦⋰⋰🇹⋰ ⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰",
"⋰🇧⋰⋰🇭⋰⋰🇬⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇯⋰⋰🇯⋰",
"⋰🇭⋰⋰🇾⋰⋰🇪⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇲⋰⋰🇦⋰⋰🇹⋰",
"⋰🇭⋰⋰🇾⋰⋰🇪⋰ ⋰🇩⋰⋰🇺⋰⋰🇷⋰ ⋰🇭⋰⋰🇦⋰⋰🇹⋰⋰🇹⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰",
"⋰🇰⋰⋰🇴⋰⋰🇮⋰ ⋰🇧⋰⋰🇦⋰⋰🇹⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇪⋰⋰🇸⋰⋰🇱⋰⋰🇮⋰⋰🇾⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇫⋰ ⋰🇨⋰⋰🇷⋰ ⋰🇷⋰⋰🇭⋰⋰🇦⋰ ⋰🇭⋰⋰🇺⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇰⋰⋰🇴⋰⋰🇮⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇹⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇲⋰⋰🇦⋰⋰🇫⋰⋰🇮⋰ ⋰🇩⋰⋰🇪⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇲⋰⋰🇦⋰⋰🇫⋰⋰🇮⋰ ⋰🇲⋰⋰🇮⋰⋰🇱⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰ ⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇪⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇨⋰⋰🇷⋰⋰🇰⋰⋰🇪⋰",
"⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇨⋰⋰🇷⋰⋰🇰⋰⋰🇪⋰",
"⋰🇫⋰⋰🇷⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰⋰🇳⋰⋰🇦⋰ ⋰🇳⋰⋰🇦⋰ ⋰??⋰⋰🇮⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇨⋰⋰🇷⋰⋰🇰⋰⋰🇪⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇺⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇵⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰",
"⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰ ⋰🇵⋰⋰🇹⋰⋰🇦⋰ ⋰🇹⋰⋰🇭⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇲⋰⋰🇪⋰⋰🇾⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇳⋰⋰🇹⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰",
"⋰🇱⋰⋰🇴⋰⋰🇩⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇺⋰⋰🇹⋰⋰🇷⋰ ⋰🇲⋰⋰??⋰",
"⋰🇱⋰⋰🇺⋰⋰🇳⋰ ⋰🇲⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇸⋰ ⋰🇲⋰⋰🇪⋰⋰🇷⋰⋰🇦⋰",
"⋰🇳⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇱⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰⋰🇨⋰⋰🇭⋰⋰🇩⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇬⋰⋰🇦⋰⋰🇸⋰⋰🇭⋰⋰🇹⋰⋰🇮⋰ ⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰",
"⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇮⋰⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰",
"⋰🇲⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇰⋰ ⋰🇭⋰⋰🇦⋰⋰🇹⋰⋰🇭⋰ ⋰🇹⋰⋰🇴⋰⋰🇩⋰⋰🇭⋰ ⋰🇰⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇪⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇰⋰ ⋰🇲⋰⋰🇺⋰⋰🇭⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇫⋰⋰🇦⋰⋰🇸⋰⋰🇦⋰⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰??⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇵⋰⋰🇦⋰⋰🇸⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇳⋰⋰🇦⋰⋰🇮⋰ ⋰🇦⋰⋰🇾⋰⋰🇦⋰ ⋰🇲⋰⋰🇪⋰⋰🇰⋰⋰🇴⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇮⋰⋰🇩⋰⋰🇪⋰⋰🇷⋰ ⋰🇸⋰⋰🇪⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇯⋰⋰🇱⋰⋰🇩⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇼⋰⋰🇷⋰⋰🇳⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇱⋰⋰🇪⋰⋰🇬⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇸⋰⋰🇲⋰⋰🇯⋰⋰🇭⋰ ⋰🇧⋰⋰🇦⋰⋰🇹⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰",
"⋰🇫⋰⋰🇦⋰⋰🇸⋰⋰🇹⋰ ⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰⋰🇯⋰⋰🇴⋰⋰🇷⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰",
"⋰🇹⋰⋰🇺⋰⋰🇹⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰",
"⋰🇴⋰⋰🇾⋰ ⋰🇭⋰⋰🇮⋰⋰🇯⋰⋰🇩⋰⋰🇪⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰⋰🇳⋰⋰🇦⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰⋰🇿⋰⋰🇴⋰⋰🇷⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇮⋰⋰🇱⋰⋰🇾⋰ ⋰🇷⋰⋰🇪⋰⋰🇾",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰",
"⋰🇸⋰⋰🇭⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰",
"⋰🇫⋰⋰🇷⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰??⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰",
"⋰🇸⋰⋰🇭⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰ ⋰🇼⋰⋰🇷⋰⋰🇳⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇾⋰⋰🇺⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰",
"⋰🇵⋰⋰🇷⋰⋰🇴⋰⋰🇴⋰⋰🇫⋰ ⋰🇨⋰⋰🇷⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇵⋰⋰🇷⋰⋰🇴⋰⋰🇴⋰⋰🇫⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰",
"⋰🇵⋰⋰🇷⋰⋰🇴⋰⋰🇴⋰⋰🇫⋰ ⋰🇭⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇰⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇮⋰⋰🇱⋰⋰🇱⋰⋰🇦⋰⋰🇷⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇰⋰ ⋰🇧⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰ ⋰🇹⋰⋰🇪⋰⋰??⋰⋰🇾⋰",
"⋰🇴⋰⋰🇾⋰ ⋰🇭⋰⋰🇮⋰⋰🇯⋰⋰🇩⋰⋰🇪⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰⋰🇳⋰⋰🇦⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰⋰🇿⋰⋰🇴⋰⋰🇷⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇩​⋰⋰🇷​⋰⋰🇨​⋰⋰🇭​⋰⋰🇴​⋰⋰🇩​⋰ ?",
"⋰🇦⋰⋰🇧⋰ ⋰🇹⋰⋰🇰⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇭⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ?",
"⋰🇳⋰⋰🇾⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇰⋰⋰🇺⋰⋰🇨⋰⋰🇭⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇯⋰⋰🇦⋰⋰🇳⋰⋰🇹⋰⋰🇦⋰ ⋰🇧⋰⋰🇸⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰",
"⋰🇸⋰⋰🇧⋰⋰🇸⋰⋰🇪⋰ ⋰🇵⋰⋰🇭⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇴⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇳⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰ ⋰🇰⋰⋰🇷⋰⋰🇪⋰",
"⋰🇾⋰⋰🇦⋰⋰🇭⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇨⋰⋰🇪⋰ ⋰🇵⋰⋰🇮⋰⋰🇱⋰⋰🇱⋰⋰🇪⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰⋰🇧⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇹⋰⋰🇴⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇹⋰⋰🇴⋰⋰🇲⋰⋰🇲⋰⋰🇾⋰",
"⋰🇳⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇱⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰⋰🇨⋰⋰🇭⋰⋰🇩⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰ ⋰🇾⋰⋰🇭⋰⋰🇦⋰ ⋰🇸⋰⋰🇪⋰",
"⋰🇨⋰⋰🇴⋰⋰🇿⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇭⋰⋰🇮⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰ ⋰🇭⋰⋰🇪⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰ ⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇳⋰⋰🇾⋰⋰🇳⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇭⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇯⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰⋰🇹⋰⋰🇮⋰ ⋰🇯⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰",
"⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇦⋰⋰🇲⋰⋰🇲⋰⋰🇮⋰ ⋰🇨⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇪⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇪⋰⋰🇲⋰⋰🇴⋰⋰🇯⋰⋰🇮⋰ ⋰🇩⋰⋰🇦⋰⋰🇱⋰ ⋰🇲⋰⋰🇨⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇨⋰⋰🇭⋰⋰🇲⋰⋰🇷⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇦⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ?",
"⋰🇹⋰⋰🇲⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇷⋰⋰🇮⋰ ⋰🇭⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰ ⋰🇫⋰⋰🇷⋰⋰🇷⋰⋰🇹⋰⋰🇴⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇰⋰⋰🇧⋰ ? ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰⋰🇰⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇸⋰⋰🇨⋰⋰🇭⋰ ⋰🇲⋰⋰🇪⋰⋰🇾⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇱⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰⋰🇳⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰",
"⋰🇮⋰⋰🇹⋰⋰🇳⋰⋰🇦⋰ ⋰🇸⋰⋰🇨⋰⋰🇭⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇸⋰⋰🇨⋰⋰🇭⋰ ⋰🇲⋰⋰🇪⋰⋰🇾⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇱⋰⋰🇮⋰⋰🇦⋰ ⋰🇲⋰⋰🇪⋰⋰🇷⋰⋰🇪⋰ ⋰🇸⋰⋰🇹⋰⋰🇭⋰",
"⋰🇲⋰⋰🇹⋰⋰🇱⋰⋰🇧⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰",
"⋰🇵⋰⋰🇺⋰⋰🇷⋰⋰🇦⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰ ⋰🇲⋰⋰🇨⋰",
"⋰🇹⋰⋰🇲⋰⋰🇷⋰ ⋰🇫⋰⋰🇷⋰⋰🇷⋰⋰🇹⋰⋰🇴⋰",
"⋰🇴⋰⋰🇭⋰ ⋰🇴⋰⋰🇰⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰ ⋰🇩⋰⋰🇦⋰⋰🇲⋰⋰🇦⋰⋰🇩⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰⋰🇪⋰ ⋰🇵⋰⋰🇪⋰⋰🇭⋰⋰🇱⋰⋰🇪⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰⋰🇧⋰⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇳⋰⋰🇪⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇻⋰⋰🇾⋰⋰🇦⋰⋰🇸⋰⋰🇹⋰ ⋰🇭⋰⋰🇺⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇰⋰⋰🇺⋰⋰🇨⋰⋰🇭⋰ ⋰🇧⋰⋰🇮⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇦⋰ ?",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇲⋰⋰🇹⋰ ⋰🇭⋰⋰🇸⋰⋰🇸⋰",
"⋰🇾⋰⋰🇺⋰⋰🇷⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇲⋰⋰🇴⋰⋰🇲⋰",
"⋰🇦⋰⋰🇷⋰⋰🇪⋰ ⋰🇸⋰⋰🇧⋰⋰🇰⋰⋰🇮⋰ ⋰🇲⋰⋰??⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇴⋰⋰🇷⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇮⋰",
"⋰🇦⋰⋰🇷⋰⋰🇪⋰ ⋰🇮⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰ ⋰🇪⋰⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇷⋰",
"⋰🇹⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇮⋰ ⋰🇹⋰⋰🇷⋰⋰🇭⋰",
"⋰🇪⋰⋰🇰⋰ ⋰🇱⋰⋰🇮⋰⋰🇳⋰⋰🇪⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰",
"⋰🇶⋰",
"⋰🇴⋰⋰🇨⋰⋰🇾⋰ ⋰🇦⋰⋰🇧⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰",
"⋰🇵⋰⋰🇪⋰⋰🇭⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰",
"⋰🇶⋰ ?",
"⋰??⋰⋰🇾⋰⋰🇾⋰⋰🇾⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰ ⋰🇪⋰⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇷⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇸⋰⋰🇺⋰⋰🇳⋰ ⋰🇩⋰⋰🇴⋰⋰🇸⋰⋰🇹⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰",
"⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰⋰🇫⋰ ⋰🇨⋰⋰🇷⋰⋰🇷⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇮⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰ ⋰🇦⋰⋰🇦⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰ ⋰🇫⋰⋰🇷⋰⋰🇷⋰⋰🇹⋰⋰🇴⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇮⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰ ⋰🇦⋰⋰🇦⋰⋰🇰⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇲⋰⋰🇷⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇦⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰ ⋰🇭⋰⋰🇮⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇭⋰⋰🇾⋰⋰🇾⋰ ⋰🇦⋰⋰🇮⋰⋰🇸⋰⋰🇪⋰ ⋰🇭⋰⋰🇮⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇱⋰⋰🇪⋰⋰🇳⋰⋰🇦⋰",
"⋰🇴⋰⋰🇷⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇱⋰⋰🇪⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰ ⋰🇴⋰⋰🇷⋰",
"⋰🇭⋰⋰🇾⋰⋰🇾⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇴⋰ ⋰??⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇴⋰ ⋰🇲⋰⋰🇹⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰⋰🇴⋰",
"⋰🇧⋰⋰🇾⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇭⋰⋰🇾⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ?",
"⋰🇶⋰⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇶⋰ ⋰🇷⋰⋰🇭⋰⋰🇪⋰ ⋰🇭⋰⋰🇴⋰ ?",
"⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇲⋰⋰🇨⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇲⋰⋰🇹⋰",
]
br3_texts = [
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰ ⋰🅃⋰⋰🄾⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄳⋰⋰??⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄼⋰⋰🅄⋰⋰🄷⋰ ⋰🄼⋰⋰🄴⋰ ⋰🅁⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄳⋰ ⋰🄳⋰⋰🅄⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰??⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄼⋰⋰🄰⋰⋰🅂⋰⋰🄰⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰",
"⋰🄵⋰⋰🄰⋰⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄿⋰⋰🄴⋰ ⋰🅃⋰⋰🄷⋰⋰🄰⋰⋰🄿⋰⋰🄿⋰⋰🄰⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰",
"⋰🅇⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄷⋰⋰🄴⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰??⋰⋰🄳⋰",
"⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🅄⋰⋰🄳⋰⋰🄷⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄸⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄷⋰⋰🄴⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄰⋰⋰🄺⋰⋰🄴⋰⋰🄻⋰⋰🄰⋰ ⋰🄿⋰⋰🄰⋰⋰🄽⋰ ⋰🄼⋰⋰🄸⋰⋰🅃⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄸⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰ ⋰🅇⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄿⋰⋰🄿⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄽⋰⋰🄰⋰⋰🄽⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🄾⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🅁⋰⋰🅁⋰ ⋰🄵⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄵⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰??⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄻⋰⋰🄰⋰⋰🄰⋰⋰🄼⋰⋰🄼⋰⋰🄼⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄾⋰⋰🄾⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄰⋰⋰🄰⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄶⋰⋰🄶⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄳⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰⋰🄽⋰ ⋰🄷⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰⋰🄷⋰⋰🄷⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰ ⋰??⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰",
"⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄿⋰⋰🄰⋰⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰ ⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄰⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🄽⋰⋰🄰⋰⋰🄽⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄰⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄳⋰ ⋰🄺⋰⋰🄸⋰⋰🄳⋰⋰🄳⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅂⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🅅⋰⋰🄾⋰⋰🄸⋰⋰🄲⋰⋰🄴⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🅂⋰⋰🄰⋰⋰🄺⋰⋰🅃⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄸⋰⋰🄶⋰⋰🄽⋰⋰🄾⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🅄⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄸⋰⋰🄶⋰⋰🄽⋰⋰🄾⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🅁⋰⋰🄰⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰??⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄰⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰ ⋰🄹⋰⋰🅄⋰⋰🄱⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰??⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄽⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄼⋰⋰🄰⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄱⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄻⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰ ⋰🄰⋰⋰🄱⋰ ⋰🅃⋰⋰🅄⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰⋰🅁⋰ ⋰🄶⋰⋰??⋰⋰🅄⋰⋰🄼⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄸⋰⋰🄽⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄹⋰⋰🄷⋰⋰🅄⋰⋰🄺⋰⋰🄽⋰⋰🄴⋰ ⋰🄽⋰⋰🄰⋰⋰🄸⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰ ⋰🄷⋰⋰🄾⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄽⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🅃⋰⋰🄾⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄰⋰⋰🅃⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰⋰🄹⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🄿⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🅁⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰??⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄾⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄱⋰⋰🄷⋰⋰🄸⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰??⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🄶⋰⋰🄰⋰⋰🄸⋰⋰🅁⋰⋰🄱⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄸⋰ ⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅃⋰⋰🄲⋰⋰🄷⋰ ⋰🄺⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🄶⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰⋰🄱⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄴⋰⋰🄴⋰⋰🄹⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰??⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄾⋰ ⋰🅃⋰⋰🄰⋰⋰🄶⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄻⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰ ⋰🄰⋰⋰🄱⋰ ⋰🅃⋰⋰🅄⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰⋰🅁⋰ ⋰🄶⋰⋰🄷⋰⋰🅄⋰⋰🄼⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄸⋰⋰🄽⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄹⋰⋰🄷⋰⋰🅄⋰⋰🄺⋰⋰🄽⋰⋰🄴⋰ ⋰🄽⋰⋰🄰⋰⋰🄸⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰ ⋰🄷⋰⋰🄾⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰??⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰??⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄽⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🅃⋰⋰🄾⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄰⋰⋰🅃⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰??⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰⋰🄹⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰??⋰⋰🄶⋰⋰🄰⋰",
"⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🄿⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🅁⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄾⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄱⋰⋰🄷⋰⋰🄸⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🄶⋰⋰🄰⋰⋰🄸⋰⋰🅁⋰⋰🄱⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄸⋰ ⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅃⋰⋰🄲⋰⋰🄷⋰ ⋰🄺⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🄶⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰⋰🄱⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄴⋰⋰🄴⋰⋰🄹⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄾⋰ ⋰🅃⋰⋰🄰⋰⋰🄶⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰"
]

sqr_texts = [
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ, ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓒ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ",
"⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓑ⊶Ⓗ⊶Ⓘ ⊶Ⓑ⊶Ⓝ⊶Ⓐ⊶Ⓛ⊶Ⓔ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓔ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓩ ⊶Ⓔ⊶Ⓨ ⊶Ⓨ⊶Ⓐ⊶Ⓐ⊶Ⓓ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓝ⊶Ⓐ ⊶Ⓣ⊶Ⓨ⊶Ⓜ⊶Ⓟ⊶Ⓐ⊶Ⓢ⊶Ⓢ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓤ⊶Ⓝ⊶Ⓕ⊶Ⓤ⊶Ⓝ⊶Ⓝ⊶Ⓨ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓜ⊶Ⓣ⊶Ⓣ ⊶Ⓚ⊶Ⓡ",
"⊶Ⓞ⊶Ⓗ ⊶Ⓗ⊶Ⓔ⊶Ⓛ⊶Ⓛ⊶Ⓞ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓤ ⊶Ⓥ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓤ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓡ.",
"⊶Ⓞ⊶Ⓨ⊶Ⓨ ⊶Ⓚ⊶Ⓘ⊶Ⓝ⊶Ⓝ⊶Ⓔ⊶Ⓡ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓖ⊶Ⓒ ⊶Ⓜ⊶Ⓔ ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓔ ⊶Ⓚ⊶Ⓘ ⊶Ⓟ⊶Ⓔ⊶Ⓡ⊶Ⓜ⊶Ⓘ⊶Ⓢ⊶Ⓢ⊶Ⓘ⊶Ⓞ⊶Ⓝ ⊶Ⓚ⊶Ⓘ⊶Ⓢ⊶Ⓝ⊶Ⓔ ⊶Ⓓ⊶Ⓘ.",
"⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ",
"⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓡ.",
"⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓐ.",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓒ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ.",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓘ ⊶Ⓙ⊶Ⓐ⊶Ⓣ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓜ⊶Ⓡ.",
"⊶Ⓚ⊶Ⓨ? ⊶Ⓙ⊶Ⓛ⊶Ⓓ⊶Ⓘ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓚ⊶Ⓘ⊶Ⓓ⊶Ⓓ⊶Ⓔ.",
"⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓒ⊶Ⓞ⊶Ⓜ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓖ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓐ⊶Ⓖ ⊶Ⓒ⊶Ⓡ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓑ⊶Ⓢ",
"⊶Ⓙ⊶Ⓐ⊶Ⓛ⊶Ⓓ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓩ ⊶Ⓟ⊶Ⓐ⊶Ⓟ⊶Ⓐ ⊶Ⓑ⊶Ⓞ⊶Ⓛ",
"⊶Ⓢ⊶Ⓘ⊶Ⓓ⊶Ⓔ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓐ⊶Ⓑ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓑ⊶Ⓗ⊶Ⓖ ⊶Ⓜ⊶Ⓐ⊶Ⓣ ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ",
"⊶Ⓑ⊶Ⓗ⊶Ⓖ ⊶Ⓝ⊶Ⓨ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓙ⊶Ⓙ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ ⊶Ⓜ⊶Ⓐ⊶Ⓣ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓓ⊶Ⓤ⊶Ⓡ ⊶Ⓗ⊶Ⓐ⊶Ⓣ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓔ⊶Ⓢ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓕ ⊶Ⓒ⊶Ⓡ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓗ⊶Ⓤ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓕ⊶Ⓘ ⊶Ⓓ⊶Ⓔ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓕ⊶Ⓘ ⊶Ⓜ⊶Ⓘ⊶Ⓛ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓖ⊶Ⓘ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓔ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓒ⊶Ⓡ⊶Ⓚ⊶Ⓔ",
"⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓒ⊶Ⓡ⊶Ⓚ⊶Ⓔ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓑ⊶Ⓞ⊶Ⓛ⊶Ⓝ⊶Ⓐ ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓒ⊶Ⓡ⊶Ⓚ⊶Ⓔ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓤ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓚ⊶Ⓔ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓛ⊶Ⓞ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓤ⊶Ⓣ⊶Ⓡ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓛ⊶Ⓤ⊶Ⓝ ⊶Ⓜ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓢ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ",
"⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓓ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓢ⊶Ⓗ⊶Ⓣ⊶Ⓘ ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ ⊶Ⓗ⊶Ⓐ⊶Ⓣ⊶Ⓗ ⊶Ⓣ⊶Ⓞ⊶Ⓓ⊶Ⓗ ⊶Ⓚ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓚ ⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ ⊶Ⓕ⊶Ⓐ⊶Ⓢ⊶Ⓐ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓢ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓝ⊶Ⓐ⊶Ⓘ ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓚ⊶Ⓞ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓔ⊶Ⓡ ⊶Ⓢ⊶Ⓔ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓙ⊶Ⓛ⊶Ⓓ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓝ⊶Ⓨ ⊶Ⓛ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ",
"⊶Ⓕ⊶Ⓐ⊶Ⓢ⊶Ⓣ ⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓣ⊶Ⓤ⊶Ⓣ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ",
"⊶Ⓞ⊶Ⓨ ⊶Ⓗ⊶Ⓘ⊶Ⓙ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓩ⊶Ⓞ⊶Ⓡ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ ⊶Ⓘ⊶Ⓛ⊶Ⓨ ⊶Ⓡ⊶Ⓔ⊶Ⓨ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ",
"⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓨ⊶Ⓤ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶ⓒ⊶ⓤ⊶ⓓ⊶ⓦ⊶ⓐ",
"⊶Ⓟ⊶Ⓡ⊶Ⓞ⊶Ⓞ⊶Ⓕ ⊶Ⓒ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ⊶Ⓞ⊶Ⓞ⊶Ⓕ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ⊶Ⓞ⊶Ⓞ⊶Ⓕ ⊶Ⓗ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓚ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓐ⊶Ⓡ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ ⊶Ⓑ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓞ⊶Ⓨ ⊶Ⓗ⊶Ⓘ⊶Ⓙ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓩ⊶Ⓞ⊶Ⓡ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶ⓜ⊶ⓐ⊶ⓓ⊶ⓡ⊶ⓒ⊶ⓗ⊶ⓞ⊶ⓓ?",
"⊶Ⓐ⊶Ⓑ ⊶Ⓣ⊶Ⓚ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓗ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ?",
"⊶Ⓝ⊶Ⓨ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓔ ⊶Ⓚ⊶Ⓤ⊶Ⓒ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓙ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓑ⊶Ⓢ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓢ⊶Ⓑ⊶Ⓢ⊶Ⓔ ⊶Ⓟ⊶Ⓗ⊶Ⓔ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓞ⊶Ⓛ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓜ ⊶Ⓚ⊶Ⓡ⊶Ⓔ",
"⊶Ⓨ⊶Ⓐ⊶Ⓗ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓒ⊶Ⓔ ⊶Ⓟ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓐ⊶Ⓑ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓣ⊶Ⓞ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓔ⊶Ⓖ⊶Ⓘ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓞ⊶Ⓜ⊶Ⓜ⊶Ⓨ",
"⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓓ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓨ⊶Ⓗ⊶Ⓐ ⊶Ⓢ⊶Ⓔ",
"⊶Ⓒ⊶Ⓞ⊶Ⓩ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓗ⊶Ⓘ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓗ⊶Ⓔ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓑ⊶Ⓞ⊶Ⓛ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓝ⊶Ⓨ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓗ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓙ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ⊶Ⓣ⊶Ⓘ ⊶Ⓙ⊶Ⓞ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓘ ⊶Ⓒ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓔ⊶Ⓜ⊶Ⓞ⊶Ⓙ⊶Ⓘ ⊶Ⓓ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓒ⊶Ⓗ⊶Ⓜ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓣ⊶Ⓜ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓡ⊶Ⓘ ⊶Ⓗ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓕ⊶Ⓡ⊶Ⓡ⊶Ⓣ⊶Ⓞ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓚ⊶Ⓑ ? ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓚ⊶Ⓔ⊶Ⓚ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓘ ⊶Ⓣ⊶Ⓤ⊶Ⓝ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ",
"⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓐ ⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓑ⊶Ⓞ⊶Ⓛ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓣ⊶Ⓗ",
"⊶Ⓜ⊶Ⓣ⊶Ⓛ⊶Ⓑ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ",
"⊶Ⓟ⊶Ⓤ⊶Ⓡ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓣ⊶Ⓜ⊶Ⓡ ⊶Ⓕ⊶Ⓡ⊶Ⓡ⊶Ⓣ⊶Ⓞ",
"⊶Ⓞ⊶Ⓗ ⊶Ⓞ⊶Ⓚ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓕ⊶Ⓘ⊶Ⓡ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓐ⊶Ⓜ⊶Ⓐ⊶Ⓓ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓔ ⊶Ⓟ⊶Ⓔ⊶Ⓗ⊶Ⓛ⊶Ⓔ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓔ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓥ⊶Ⓨ⊶Ⓐ⊶Ⓢ⊶Ⓣ ⊶Ⓗ⊶Ⓤ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓚ⊶Ⓤ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓘ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓜ⊶Ⓣ ⊶Ⓗ⊶Ⓢ⊶Ⓢ",
"⊶Ⓨ⊶Ⓤ⊶Ⓡ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓜ⊶Ⓞ⊶Ⓜ",
"⊶Ⓐ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓑ⊶Ⓚ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓘ",
"⊶Ⓐ⊶Ⓡ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓡ",
"⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓘ ⊶Ⓣ⊶Ⓡ⊶Ⓗ",
"⊶Ⓔ⊶Ⓚ ⊶Ⓛ⊶Ⓘ⊶Ⓝ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓠ",
"⊶Ⓞ⊶Ⓒ⊶Ⓨ ⊶Ⓐ⊶Ⓑ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ",
"⊶Ⓟ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ",
"⊶Ⓠ ?",
"⊶Ⓗ⊶Ⓨ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓐ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓡ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓓ⊶Ⓞ⊶Ⓢ⊶Ⓣ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ ⊶Ⓙ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓕ ⊶Ⓒ⊶Ⓡ⊶Ⓡ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓜ⊶Ⓡ ⊶Ⓕ⊶Ⓡ⊶Ⓡ⊶Ⓣ⊶Ⓞ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓛ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓜ⊶Ⓡ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓐ⊶Ⓔ⊶Ⓢ⊶Ⓔ ⊶Ⓗ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓗ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓛ⊶Ⓔ⊶Ⓝ⊶Ⓐ",
"⊶Ⓞ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓛ⊶Ⓔ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓐ ⊶Ⓞ⊶Ⓡ",
"⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓞ ⊶Ⓝ⊶Ⓐ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓞ ⊶Ⓜ⊶Ⓣ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ ⊶Ⓙ⊶Ⓐ⊶Ⓞ",
"⊶Ⓑ⊶Ⓨ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓠ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓠ ⊶Ⓡ⊶Ⓗ⊶Ⓔ ⊶Ⓗ⊶Ⓞ ?",
"⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓜ⊶Ⓣ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓘ ⊶Ⓒ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓚ⊶Ⓜ⊶Ⓩ⊶Ⓡ⊶Ⓞ⊶Ⓡ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓔ⊶Ⓚ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ?",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓢ⊶Ⓛ⊶Ⓘ⊶Ⓓ⊶Ⓔ ⊶Ⓛ⊶Ⓔ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶ⒶⓉ ⊶Ⓒ⊶Ⓡ⊶Ⓜ⊶Ⓒ",
"⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓒ⊶Ⓟ ⊶Ⓜ⊶Ⓣ ⊶Ⓒ⊶Ⓡ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓐ",
"⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓢ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓕ⊶Ⓤ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓡ",
"⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ ⊶Ⓙ⊶Ⓐ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓚ⊶Ⓜ⊶Ⓩ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓒ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ",
"⊶Ⓨ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓝ⊶Ⓨ ⊶Ⓒ⊶Ⓟ ⊶Ⓝ⊶Ⓨ ⊶Ⓒ⊶Ⓡ⊶Ⓡ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓜ⊶Ⓣ ⊶Ⓒ⊶Ⓡ⊶Ⓡ",
"⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓡ⊶ⒶⓂ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓔ⊶Ⓚ",
"⊶Ⓒ⊶Ⓟ ⊶Ⓒ⊶Ⓡ⊶Ⓒ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓔ⊶Ⓖ⊶Ⓐ !",
"⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ? ⊶Ⓜ⊶Ⓒ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓝ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓘ ⊶Ⓤ⊶Ⓟ⊶Ⓐ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓡ⊶Ⓞ⊶Ⓒ⊶Ⓚ⊶Ⓔ⊶Ⓣ ⊶Ⓟ⊶Ⓔ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ ⊶Ⓒ⊶Ⓔ ⊶ⒷⓈⓈ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓤ",
"⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶ⓉⓇ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓚ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓔ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓜ⊶Ⓐ⊶Ⓘ⊶Ⓝ ⊶Ⓑ⊶Ⓤ⊶Ⓡ⊶Ⓕ",
"⊶Ⓑ⊶Ⓗ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓙ⊶Ⓗ⊶Ⓐ⊶Ⓣ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓛ⊶Ⓔ",
"⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓜ⊶Ⓐ⊶Ⓘ⊶Ⓝ ⊶Ⓜ⊶Ⓞ⊶Ⓤ⊶Ⓝ⊶Ⓣ ⊶Ⓔ⊶Ⓥ⊶Ⓔ⊶Ⓡ⊶Ⓔ⊶Ⓢ⊶Ⓣ",
"⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓛ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ",
"⊶Ⓗ⊶Ⓘ⊶Ⓙ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓘ ⊶Ⓙ⊶Ⓗ⊶Ⓐ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶ⓉⓇ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓝ⊶Ⓨ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓚ⊶Ⓘ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓢ⊶Ⓑ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓣ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓔ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓣ⊶Ⓗ⊶Ⓝ⊶Ⓚ⊶Ⓢ⊶Ⓢ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓑ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓢ⊶Ⓐ⊶Ⓑ⊶Ⓘ⊶Ⓣ ⊶Ⓚ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓤ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓔ⊶Ⓐ⊶Ⓢ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓔ⊶Ⓐ⊶Ⓢ⊶Ⓨ ⊶Ⓦ⊶8 ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓐ⊶Ⓑ",
"⊶Ⓢ⊶Ⓐ⊶Ⓝ⊶Ⓢ ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓖ⊶Ⓘ ⊶Ⓐ⊶Ⓙ⊶Ⓙ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓘ⊶Ⓝ⊶Ⓐ ⊶Ⓢ⊶Ⓐ⊶Ⓝ⊶Ⓢ⊶Ⓢ ⊶Ⓛ⊶Ⓔ⊶Ⓣ⊶Ⓔ ⊶Ⓗ⊶Ⓤ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓔ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ",
"⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓡ⊶Ⓜ⊶Ⓘ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓡ⊶Ⓜ⊶Ⓘ⊶Ⓔ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓢ ⊶Ⓣ⊶Ⓗ⊶Ⓔ⊶Ⓚ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓢ ⊶Ⓣ⊶Ⓗ⊶Ⓔ⊶Ⓚ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ",
"⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓗ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓔ⊶Ⓢ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ",
"⊶Ⓜ⊶Ⓐ⊶Ⓘ ⊶Ⓢ⊶Ⓑ ⊶Ⓙ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓒ⊶Ⓗ⊶Ⓛ ⊶Ⓒ⊶Ⓗ⊶Ⓛ ⊶Ⓗ⊶Ⓣ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓢ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓒ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓣ ⊶Ⓖ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓐ ⊶Ⓖ⊶Ⓝ⊶Ⓓ⊶Ⓐ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓑ⊶Ⓣ⊶Ⓐ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓕ⊶Ⓘ⊶Ⓡ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓝ⊶Ⓨ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓝ⊶Ⓨ ⊶Ⓚ⊶Ⓞ⊶Ⓝ ⊶Ⓒ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ",
"⊶Ⓡ⊶Ⓤ⊶Ⓚ ⊶Ⓐ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓚ⊶Ⓔ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓒ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓗ⊶Ⓤ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓒ⊶Ⓡ ⊶Ⓡ⊶Ⓐ⊶Ⓑ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓡ⊶Ⓗ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓚ⊶Ⓡ ⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓚ⊶Ⓔ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓓ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ",
"⊶Ⓡ⊶Ⓤ⊶Ⓚ ⊶Ⓙ⊶Ⓐ ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓡ⊶Ⓚ⊶Ⓗ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓕ⊶Ⓐ⊶Ⓜ⊶Ⓞ⊶Ⓤ⊶Ⓢ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ⊶ⒶⓃ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓢ⊶Ⓐ⊶Ⓛ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ⊶ⒶⓃ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓣ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓢ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓣ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓢ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓣ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ ⊶Ⓣ⊶Ⓤ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓐ⊶Ⓑ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓨ⊶Ⓗ⊶Ⓐ",
"⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓛ⊶Ⓔ ⊶ⓛ⊶ⓤ⊶ⓝ⊶ⓓ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓒ⊶Ⓨ⊶Ⓐ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓒ⊶Ⓨ⊶Ⓐ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓣ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓜ ⊶Ⓒ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ",
"⊶Ⓒ⊶Ⓗ⊶Ⓛ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ⊶Ⓛ⊶Ⓔ",
"⊶Ⓑ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓢ⊶Ⓑ ⊶Ⓙ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓔ ⊶Ⓔ⊶Ⓨ ⊶Ⓚ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓓ⊶Ⓚ⊶Ⓐ⊶Ⓓ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓦ⊶Ⓛ⊶Ⓘ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓘ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓙ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓥ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓝ⊶Ⓝ⊶Ⓐ ⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓦ⊶Ⓞ ⊶Ⓖ⊶Ⓛ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓦ⊶Ⓞ ⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓓ⊶Ⓚ⊶Ⓐ⊶Ⓓ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓚ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓞ⊶Ⓜ⊶Ⓕ⊶Ⓞ⊶Ⓞ",
"⊶Ⓑ⊶Ⓤ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓔ⊶Ⓔ⊶Ⓡ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓛ ⊶Ⓜ⊶Ⓔ ⊶Ⓛ⊶Ⓞ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓚ⊶Ⓔ ⊶Ⓤ⊶Ⓢ⊶Ⓚ⊶Ⓘ ⊶Ⓓ⊶Ⓗ⊶Ⓐ⊶Ⓓ⊶Ⓚ⊶Ⓐ⊶Ⓝ ⊶Ⓡ⊶Ⓞ⊶Ⓚ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓛ⊶Ⓤ⊶Ⓛ⊶Ⓛ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓐ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ",
"⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓐ",
"⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶ⒶⓉ ⊶Ⓚ⊶Ⓗ⊶ⓉⓂ",
"⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓔ⊶Ⓚ ⊶Ⓜ⊶Ⓐ⊶Ⓩ⊶Ⓔ ⊶Ⓚ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶ⒶⓉ ⊶Ⓑ⊶Ⓐ⊶Ⓣ⊶Ⓐ⊶Ⓞ ⊶Ⓚ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶रैं⊶डी ⊶Ⓗ⊶Ⓐ⊶Ⓘ",
"⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓤ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓐ⊶Ⓙ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓞ⊶Ⓨ⊶Ⓔ",
"⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓚ⊶Ⓘ⊶Ⓛ⊶Ⓐ⊶Ⓢ ⊶Ⓝ⊶Ⓨ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓟ⊶Ⓡ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓔ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ",
"⊶Ⓣ⊶Ⓜ⊶Ⓒ⊶Ⓛ ⊶Ⓢ⊶Ⓤ⊶Ⓝ⊶Ⓛ⊶Ⓔ",
"⊶Ⓜ⊶Ⓞ⊶Ⓞ⊶Ⓣ ⊶Ⓓ⊶Ⓤ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ⊶Ⓨ",
"⊶Ⓑ⊶Ⓗ⊶Ⓖ⊶Ⓝ⊶Ⓨ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓕ⊶Ⓡ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓨ⊶Ⓔ ⊶Ⓥ⊶Ⓘ ⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓑ⊶Ⓢ",
"⊶Ⓐ⊶Ⓙ ⊶Ⓚ⊶Ⓤ⊶Ⓒ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓚ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓢ⊶Ⓚ⊶Ⓔ",
"⊶Ⓣ⊶Ⓞ⊶Ⓡ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ⊶Ⓑ⊶Ⓤ⊶Ⓡ ⊶Ⓢ⊶Ⓤ⊶Ⓝ",
"⊶Ⓣ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓕ⊶Ⓤ⊶Ⓓ⊶Ⓓ⊶Ⓘ ⊶Ⓞ⊶Ⓨ⊶Ⓔ",
"⊶Ⓗ⊶Ⓐ⊶Ⓨ⊶Ⓔ ⊶Ⓗ⊶Ⓐ⊶Ⓨ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓢ⊶Ⓘ⊶Ⓝ⊶Ⓔ..",
"⊶Ⓚ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓐ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓢ⊶Ⓤ⊶Ⓝ",
"⊶Ⓚ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓐ ⊶Ⓙ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓘ ⊶Ⓛ⊶Ⓔ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ..",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓚ⊶Ⓔ ⊶Ⓕ⊶Ⓔ⊶Ⓝ⊶Ⓚ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓝ ⊶Ⓢ⊶Ⓣ⊶Ⓞ⊶Ⓟ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓐ⊶ⒶⓉ ⊶Ⓖ⊶Ⓐ⊶Ⓨ⊶Ⓘ ⊶Ⓐ⊶Ⓙ⊶Ⓣ⊶Ⓞ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓔ ⊶Ⓚ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓒ⊶Ⓗ⊶Ⓘ⊶Ⓟ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓝ ⊶Ⓢ⊶Ⓣ⊶Ⓞ⊶Ⓟ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓤ⊶Ⓢ⊶Ⓢ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶100 ⊶Ⓒ⊶Ⓗ⊶Ⓔ⊶Ⓓ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓦ⊶Ⓐ⊶Ⓢ⊶Ⓘ⊶Ⓡ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓛ⊶Ⓐ⊶Ⓥ⊶Ⓓ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓡ ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓣ⊶Ⓘ ⊶Ⓗ⊶Ⓐ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓣ⊶Ⓐ⊶Ⓜ⊶Ⓐ⊶Ⓣ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓐ⊶Ⓡ⊶Ⓐ⊶Ⓗ ⊶Ⓛ⊶Ⓐ⊶ⒶⓁ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓐ⊶ⒶⓅ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓑ⊶Ⓘ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓙ⊶Ⓐ⊶Ⓡ ⊶Ⓜ⊶Ⓔ ⊶Ⓝ⊶Ⓘ⊶Ⓛ⊶Ⓐ⊶Ⓜ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓕ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓜ⊶Ⓔ ⊶Ⓓ⊶Ⓐ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓙ⊶Ⓐ⊶Ⓓ⊶Ⓐ ⊶Ⓝ⊶Ⓐ ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ ⊶Ⓦ⊶Ⓐ⊶Ⓡ⊶Ⓝ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓢ⊶Ⓐ⊶Ⓢ⊶Ⓣ⊶Ⓐ ⊶Ⓚ⊶Ⓔ⊶Ⓨ⊶Ⓑ⊶Ⓞ⊶Ⓐ⊶Ⓡ⊶Ⓓ ⊶Ⓛ⊶Ⓐ⊶Ⓖ⊶Ⓐ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓐ⊶Ⓖ⊶Ⓐ⊶Ⓡ ⊶Ⓣ⊶Ⓤ ⊶Ⓒ⊶Ⓟ ⊶Ⓑ⊶Ⓞ⊶Ⓛ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓜ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓡ⊶Ⓐ⊶Ⓜ ⊶Ⓜ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓗ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓤ⊶Ⓡ ⊶Ⓜ⊶Ⓔ ⊶Ⓗ⊶Ⓐ⊶Ⓣ⊶Ⓗ⊶Ⓞ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓚ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓘ ⊶Ⓣ⊶Ⓗ⊶Ⓞ⊶Ⓚ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓙ⊶Ⓙ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓕ⊶Ⓐ⊶ⒶⓉ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓙ⊶Ⓐ⊶ⒶⓃ ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓐ⊶Ⓝ⊶Ⓒ⊶Ⓔ⊶Ⓡ ⊶Ⓦ⊶Ⓐ⊶Ⓛ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓝ ⊶Ⓢ⊶Ⓣ⊶Ⓞ⊶Ⓟ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓙ⊶Ⓐ⊶ⒶⓃ ⊶Ⓚ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓛ⊶Ⓘ⊶Ⓣ⊶Ⓒ⊶Ⓗ ⊶Ⓣ⊶Ⓨ⊶Ⓟ⊶Ⓘ⊶Ⓝ⊶Ⓖ ⊶Ⓚ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓥ⊶Ⓐ⊶Ⓢ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓗ⊶Ⓐ⊶Ⓘ ⊶Ⓢ⊶Ⓐ⊶Ⓑ⊶Ⓚ⊶Ⓐ ⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓗ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓛ⊶Ⓔ⊶Ⓚ⊶Ⓡ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ⊶Ⓐ⊶Ⓣ⊶Ⓘ ⊶Ⓗ⊶Ⓐ⊶Ⓘ",
"⊶Ⓣ⊶Ⓤ ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓑ⊶Ⓘ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓙ⊶Ⓐ⊶Ⓡ ⊶Ⓜ⊶Ⓔ ⊶Ⓜ⊶Ⓞ⊶Ⓙ⊶Ⓡ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓦ⊶Ⓐ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓓ⊶Ⓤ⊶Ⓢ⊶Ⓡ⊶Ⓐ ⊶Ⓑ⊶Ⓛ⊶Ⓐ⊶Ⓒ⊶Ⓚ ⊶Ⓗ⊶Ⓞ⊶Ⓛ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓕ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓜ⊶Ⓔ ⊶Ⓓ⊶Ⓐ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓘ⊶ⓨ⊶Ⓞ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓓ⊶Ⓩ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓓ⊶Ⓐ⊶Ⓛ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓖ⊶Ⓞ⊶Ⓓ⊶Ⓩ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓢ⊶Ⓔ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓓ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓕ⊶Ⓛ⊶Ⓨ ⊶Ⓚ⊶Ⓘ⊶Ⓢ⊶Ⓢ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓘ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓓ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓤ⊶Ⓜ⊶Ⓜ⊶Ⓨ ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓘ⊶ⓨ⊶Ⓞ ⊶Ⓚ⊶Ⓞ ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓟ⊶Ⓐ⊶Ⓚ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓙ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓤ⊶Ⓝ⊶Ⓝ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓤ⊶Ⓢ⊶Ⓢ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓘ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓓ⊶Ⓞ⊶Ⓝ⊶Ⓐ⊶Ⓣ⊶Ⓔ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓗ⊶Ⓐ⊶Ⓡ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓨ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓙ⊶Ⓘ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓤ⊶Ⓛ⊶Ⓛ⊶Ⓓ⊶Ⓞ⊶Ⓩ⊶Ⓔ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓛ⊶Ⓐ⊶Ⓣ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓙ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓕ⊶Ⓐ⊶ⒶⓉ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓓ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓐ⊶Ⓚ⊶49 ⊶Ⓢ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶9 ⊶Ⓤ⊶Ⓝ⊶Ⓘ⊶Ⓥ⊶Ⓔ⊶Ⓡ⊶Ⓢ ⊶Ⓐ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓓ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶ⓨ⊶Ⓞ ⊶Ⓚ⊶Ⓐ ⊶Ⓚ⊶Ⓞ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ⊶Ⓝ⊶Ⓔ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓐ⊶Ⓘ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓞ⊶Ⓣ⊶Ⓗ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓡ⊶Ⓡ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓒ⊶Ⓗ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓙ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓐ⊶Ⓝ⊶Ⓒ⊶Ⓔ⊶Ⓡ ⊶Ⓦ⊶Ⓐ⊶Ⓛ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓘ⊶Ⓚ⊶Ⓣ⊶Ⓞ⊶Ⓚ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓐ⊶Ⓡ⊶Ⓐ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓘ⊶Ⓢ⊶Ⓢ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓢ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓐ ⊶Ⓟ⊶Ⓞ⊶Ⓦ⊶Ⓔ⊶Ⓡ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ",
"⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓜ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓗ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓟ⊶Ⓞ⊶Ⓛ⊶Ⓘ⊶Ⓒ⊶Ⓔ ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓤ⊶Ⓢ⊶Ⓢ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓐ ⊶Ⓦ⊶Ⓞ⊶Ⓡ⊶Ⓚ⊶Ⓞ⊶Ⓤ⊶Ⓣ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓐ ⊶Ⓔ⊶Ⓝ⊶Ⓔ⊶Ⓡ⊶Ⓖ⊶Ⓨ ⊶Ⓗ⊶Ⓐ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶ⒶⓇ ⊶Ⓜ⊶Ⓔ ⊶10 ⊶Ⓛ⊶Ⓞ⊶Ⓖ⊶Ⓞ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ⊶Ⓐ ⊶Ⓛ⊶Ⓔ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓒ⊶Ⓗ⊶Ⓐ ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ⊶Ⓔ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓞ ⊶Ⓤ⊶Ⓛ⊶Ⓣ⊶Ⓐ ⊶Ⓛ⊶Ⓐ⊶Ⓣ⊶Ⓚ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓗ⊶Ⓞ⊶Ⓛ⊶Ⓛ⊶Ⓞ⊶Ⓦ ⊶Ⓟ⊶Ⓤ⊶Ⓡ⊶Ⓟ⊶Ⓛ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓔ⊶Ⓓ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ"
]

sq2_texts = [
"⋰Ⓑ⋰⋰⒪⋰⋰⒧⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰Ⓓ⋰⋰⒤⋰⋰Ⓓ⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒨⋰⋰⒰⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒭⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰⋰⒟⋰ ⋰⒟⋰⋰⒰⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒮⋰⋰⒜⋰⋰⒧⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰",
"⋰⒡⋰⋰⒜⋰⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒫⋰⋰⒠⋰ ⋰⒯⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰⋰⒫⋰⋰⒜⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒰⋰",
"⋰⒳⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒣⋰⋰⒠⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒝⋰⋰⒰⋰⋰⒟⋰⋰⒣⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒣⋰⋰⒠⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒜⋰⋰⒦⋰⋰⒠⋰⋰⒧⋰⋰⒜⋰ ⋰⒫⋰⋰⒜⋰⋰⒩⋰ ⋰⒨⋰⋰⒤⋰⋰⒯⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒳⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰⋰⒯⋰ ⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰⋰⒫⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒩⋰⋰⒜⋰⋰⒩⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒪⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒠⋰⋰⒭⋰⋰⒭⋰ ⋰⒡⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰⋰⒯⋰ ⋰⒮⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰⋰⒥⋰⋰⒥⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒡⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒩⋰⋰⒤⋰⋰⒧⋰⋰⒜⋰⋰⒜⋰⋰⒨⋰⋰⒨⋰⋰⒨⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒪⋰⋰⒪⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒜⋰⋰⒜⋰ ⋰⒮⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒢⋰⋰⒢⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒟⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰⋰⒩⋰ ⋰⒣⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰⋰⒣⋰⋰⒣⋰ ⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰⋰⒥⋰⋰⒥⋰⋰⒥⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰⋰⒩⋰⋰⒩⋰",
"⋰⒮⋰⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒫⋰⋰⒜⋰⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰",
"⋰⒮⋰⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰⋰⒦⋰⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰ ⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰",
"⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰ ⋰⒩⋰⋰⒜⋰⋰⒩⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒜⋰⋰⒰⋰⋰⒧⋰⋰⒜⋰⋰⒟⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒜⋰⋰⒰⋰⋰⒧⋰⋰⒜⋰⋰⒟⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒟⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒮⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰ ⋰⒮⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒱⋰⋰⒪⋰⋰⒤⋰⋰⒞⋰⋰⒠⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒮⋰⋰⒜⋰⋰⒦⋰⋰⒯⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒤⋰⋰⒢⋰⋰⒩⋰⋰⒪⋰⋰⒭⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒤⋰⋰⒢⋰⋰⒩⋰⋰⒪⋰⋰⒭⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒭⋰⋰⒜⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒯⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒧⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒧⋰⋰⒤⋰ ⋰⒥⋰⋰⒰⋰⋰⒝⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒠⋰⋰⒩⋰⋰⒦⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒩⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒨⋰⋰⒜⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒝⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒯⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒜⋰⋰⒝⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰??⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰⋰⒭⋰ ⋰⒢⋰⋰??⋰⋰⒰⋰⋰⒨⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒧⋰⋰⒠⋰⋰⒦⋰⋰⒤⋰⋰⒩⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒥⋰⋰⒣⋰⋰⒰⋰⋰⒦⋰⋰⒩⋰⋰⒠⋰ ⋰⒩⋰⋰⒜⋰⋰⒤⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒩⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰⋰⒰⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒜⋰⋰⒯⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒣⋰⋰⒪⋰⋰⒥⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒡⋰⋰⒠⋰⋰⒩⋰⋰⒦⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒦⋰⋰⒪⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒪⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒨⋰⋰⒠⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒮⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒝⋰⋰⒣⋰⋰⒤⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰",
"⋰⒢⋰⋰⒜⋰⋰⒤⋰⋰⒭⋰⋰⒝⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒜⋰⋰⒰⋰⋰⒧⋰⋰⒜⋰⋰⒟⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒮⋰⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰⋰⒞⋰⋰⒣⋰ ⋰⒦⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒢⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰⋰⒝⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒠⋰⋰⒦⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒠⋰⋰⒥⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒯⋰⋰⒜⋰⋰⒢⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒯⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒜⋰⋰⒝⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰⋰⒭⋰ ⋰⒢⋰⋰⒣⋰⋰⒰⋰⋰⒨⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒧⋰⋰⒠⋰⋰⒦⋰⋰⒤⋰⋰⒩⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒥⋰⋰⒣⋰⋰⒰⋰⋰⒦⋰⋰⒩⋰⋰⒠⋰ ⋰⒩⋰⋰⒜⋰⋰⒤⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒩⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰⋰⒰⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒝⋰⋰⒪⋰⋰",
"⋰Ⓑ⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰Ⓑ⋰⋰⒣⋰⋰⒤⋰ ⋰Ⓑ⋰⋰⒩⋰⋰⒜⋰⋰⒧⋰⋰⒠⋰ ⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒠⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒵⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰ ⋰⒯⋰⋰⒴⋰⋰⒨⋰⋰⒫⋰⋰⒜⋰⋰⒮⋰⋰⒮⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒰⋰⋰⒩⋰⋰⒡⋰⋰⒰⋰⋰⒩⋰⋰⒩⋰⋰⒴⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒨⋰⋰⒯⋰⋰⒯⋰ ⋰⒦⋰⋰⒭⋰",
"⋰⒪⋰⋰⒣⋰ ⋰⒣⋰⋰⒠⋰⋰⒧⋰⋰⒧⋰⋰⒪⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒪⋰⋰⒭⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒱⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒜⋰⋰⒜⋰⋰⒰⋰⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒭⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒭⋰.",
"⋰⒪⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰⋰⒩⋰⋰⒩⋰⋰⒠⋰⋰⒭⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰ ⋰⒢⋰⋰⒞⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰⋰⒩⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒫⋰⋰⒠⋰⋰⒭⋰⋰⒨⋰⋰⒤⋰⋰⒮⋰⋰⒮⋰⋰⒤⋰⋰⒪⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰⋰⒮⋰⋰⒩⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰.",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒠⋰⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰.",
"⋰⒮⋰⋰⒰⋰⋰⒩⋰ ⋰⒮⋰⋰⒰⋰⋰⒩⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰.",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒞⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰.",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒯⋰⋰⒤⋰ ⋰⒥⋰⋰⒜⋰⋰⒯⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰.",
"⋰⒦⋰⋰⒴⋰? ⋰⒥⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰⋰⒟⋰⋰⒠⋰.",
"⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒞⋰⋰⒪⋰⋰⒨⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒢⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒯⋰⋰⒜⋰⋰⒢⋰ ⋰⒞⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒨⋰⋰⒦⋰⋰⒞⋰ ⋰⒝⋰⋰⒮⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒵⋰ ⋰⒫⋰⋰⒜⋰⋰⒫⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰",
"⋰⒮⋰⋰⒤⋰⋰⒟⋰⋰⒠⋰ ⋰⒣⋰⋰⒪⋰⋰⒥⋰⋰⒜⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒜⋰⋰⒝⋰",
"⋰⒣⋰⋰⒴⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒝⋰⋰⒣⋰⋰⒢⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰ ⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰",
"⋰⒝⋰⋰⒣⋰⋰⒢⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒥⋰⋰⒥⋰",
"⋰⒣⋰⋰⒴⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰",
"⋰⒣⋰⋰⒴⋰⋰⒠⋰ ⋰⒟⋰⋰⒰⋰⋰⒭⋰ ⋰⒣⋰⋰⒜⋰⋰⒯⋰⋰⒯⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒦⋰⋰⒪⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒯⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒠⋰⋰⒮⋰⋰⒧⋰⋰⒤⋰⋰⒴⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒡⋰ ⋰⒞⋰⋰⒭⋰ ⋰⒭⋰⋰⒣⋰⋰⒜⋰ ⋰⒣⋰⋰⒰⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒦⋰⋰⒪⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒯⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒜⋰⋰⒡⋰⋰⒤⋰ ⋰⒟⋰⋰⒠⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒜⋰⋰⒡⋰⋰⒤⋰ ⋰⒨⋰⋰⒤⋰⋰⒧⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒠⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒞⋰⋰⒭⋰⋰⒦⋰⋰⒠⋰",
"⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒞⋰⋰⒭⋰⋰⒦⋰⋰⒠⋰",
"⋰⒡⋰⋰⒭⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰⋰⒩⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒞⋰⋰⒭⋰⋰⒦⋰⋰⒠⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒣⋰⋰⒰⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒫⋰⋰⒭⋰ ⋰⒦⋰⋰⒠⋰⋰⒮⋰⋰⒠⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰",
"⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰ ⋰⒫⋰⋰⒯⋰⋰⒜⋰ ⋰⒯⋰⋰⒣⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒨⋰⋰⒠⋰⋰⒴⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒩⋰⋰⒯⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰",
"⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒰⋰⋰⒯⋰⋰⒭⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒧⋰⋰⒰⋰⋰⒩⋰ ⋰⒨⋰⋰⒯⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒮⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰",
"⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒟⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒢⋰⋰⒜⋰⋰⒮⋰⋰⒣⋰⋰⒯⋰⋰⒤⋰ ⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰",
"⋰⒨⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒦⋰ ⋰⒣⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰ ⋰⒯⋰⋰⒪⋰⋰⒟⋰⋰⒣⋰ ⋰⒦⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰ ⋰⒨⋰⋰⒰⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒮⋰⋰⒜⋰⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒫⋰⋰⒜⋰⋰⒮⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒩⋰⋰⒜⋰⋰⒤⋰ ⋰⒜⋰⋰⒴⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰⋰⒦⋰⋰⒪⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒤⋰⋰⒟⋰⋰⒠⋰⋰⒭⋰ ⋰⒮⋰⋰⒠⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒥⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒲⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒧⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒮⋰⋰⒨⋰⋰⒥⋰⋰⒣⋰ ⋰⒝⋰⋰⒜⋰⋰⒯⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰",
"⋰⒡⋰⋰⒜⋰⋰⒮⋰⋰⒯⋰ ⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰⋰⒥⋰⋰⒪⋰⋰⒭⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰",
"⋰⒯⋰⋰⒰⋰⋰⒯⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰",
"⋰⒪⋰⋰⒴⋰ ⋰⒣⋰⋰⒤⋰⋰⒥⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰⋰⒵⋰⋰⒪⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒪⋰ ⋰⒤⋰⋰⒧⋰⋰⒴⋰ ⋰⒭⋰⋰⒠⋰⋰⒴⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒯⋰⋰⒨⋰⋰⒦⋰⋰⒞⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒮⋰⋰⒣⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰",
"⋰⒡⋰⋰⒭⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰",
"⋰⒮⋰⋰⒣⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒲⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒴⋰⋰⒰⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰",
"⋰⒫⋰⋰⒭⋰⋰⒪⋰⋰⒪⋰⋰⒡⋰ ⋰⒞⋰⋰⒭⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒫⋰⋰⒭⋰⋰⒪⋰⋰⒪⋰⋰⒡⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰",
"⋰⒫⋰⋰⒭⋰⋰⒪⋰⋰⒪⋰⋰⒡⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒦⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒤⋰⋰⒧⋰⋰⒧⋰⋰⒜⋰⋰⒭⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒪⋰⋰⒴⋰ ⋰⒣⋰⋰⒤⋰⋰⒥⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰⋰⒵⋰⋰⒪⋰⋰⒭⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ?",
"⋰⒜⋰⋰⒝⋰ ⋰⒯⋰⋰⒦⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ?",
"⋰⒩⋰⋰⒴⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒦⋰⋰⒰⋰⋰⒞⋰⋰⒣⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒥⋰⋰⒜⋰⋰⒩⋰⋰⒯⋰⋰⒜⋰ ⋰⒝⋰⋰⒮⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰",
"⋰⒮⋰⋰⒝⋰⋰⒮⋰⋰⒠⋰ ⋰⒫⋰⋰⒣⋰⋰⒠⋰⋰⒧⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰⋰⒠⋰",
"⋰⒴⋰⋰⒜⋰⋰⒣⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒞⋰⋰⒠⋰ ⋰⒫⋰⋰⒤⋰⋰⒧⋰⋰⒧⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒜⋰⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒯⋰⋰⒪⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰",
"⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒟⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒴⋰⋰⒣⋰⋰⒜⋰ ⋰⒮⋰⋰⒠⋰",
"⋰⒞⋰⋰⒪⋰⋰⒵⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒣⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒣⋰⋰⒠⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰ ⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒩⋰⋰⒴⋰⋰⒩⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒥⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰⋰⒯⋰⋰⒤⋰ ⋰⒥⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒭⋰⋰⒴⋰ ⋰⒜⋰⋰⒨⋰⋰⒨⋰⋰⒤⋰ ⋰⒞⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒠⋰⋰⒨⋰⋰⒪⋰⋰⒥⋰⋰⒤⋰ ⋰⒟⋰⋰⒜⋰⋰⒧⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒞⋰⋰⒣⋰⋰⒨⋰⋰⒭⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒜⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ?",
"⋰⒯⋰⋰⒨⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒭⋰⋰⒤⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰ ⋰⒡⋰⋰⒭⋰⋰⒭⋰⋰⒯⋰⋰⒪⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒦⋰⋰⒝⋰ ? ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰⋰⒦⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒮⋰⋰⒞⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰⋰⒴⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰⋰⒩⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰",
"⋰⒤⋰⋰⒯⋰⋰⒩⋰⋰⒜⋰ ⋰⒮⋰⋰⒞⋰⋰⒣⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒮⋰⋰⒞⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰⋰⒴⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒮⋰⋰⒯⋰⋰⒣⋰",
"⋰⒨⋰⋰⒯⋰⋰⒧⋰⋰⒝⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰",
"⋰⒫⋰⋰⒰⋰⋰⒭⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒯⋰⋰⒨⋰⋰⒭⋰ ⋰⒡⋰⋰⒭⋰⋰⒭⋰⋰⒯⋰⋰⒪⋰",
"⋰⒪⋰⋰⒣⋰ ⋰⒪⋰⋰⒦⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒧⋰⋰⒠⋰ ⋰⒡⋰⋰⒤⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒨⋰⋰⒜⋰⋰⒟⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰⋰⒣⋰⋰⒧⋰⋰⒠⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒠⋰⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒩⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒱⋰⋰⒴⋰⋰⒜⋰⋰⒮⋰⋰⒯⋰ ⋰⒣⋰⋰⒰⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒰⋰⋰⒞⋰⋰⒣⋰ ⋰⒝⋰⋰⒤⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒜⋰ ?",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒨⋰⋰⒯⋰ ⋰⒣⋰⋰⒮⋰⋰⒮⋰",
"⋰⒴⋰⋰⒰⋰⋰⒭⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒪⋰⋰⒨⋰",
"⋰⒜⋰⋰⒭⋰⋰⒠⋰ ⋰⒮⋰⋰⒝⋰⋰⒦⋰⋰⒤⋰ ⋰⒨⋰⋰??⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒪⋰⋰⒭⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒤⋰",
"⋰⒜⋰⋰⒭⋰⋰⒠⋰ ⋰⒤⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒧⋰⋰⒠⋰ ⋰⒠⋰⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒤⋰ ⋰⒯⋰⋰⒭⋰⋰⒣⋰",
"⋰⒠⋰⋰⒦⋰ ⋰⒧⋰⋰⒤⋰⋰⒩⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰",
"⋰⒬⋰",
"⋰⒪⋰⋰⒞⋰⋰⒴⋰ ⋰⒜⋰⋰⒝⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒧⋰⋰⒠⋰",
"⋰⒫⋰⋰⒠⋰⋰⒣⋰⋰⒠⋰⋰⒧⋰⋰⒠⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰",
"⋰⒬⋰ ?",
"⋰⒣⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰ ⋰⒠⋰⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒮⋰⋰⒰⋰⋰⒩⋰ ⋰⒟⋰⋰⒪⋰⋰⒮⋰⋰⒯⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰",
"⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒡⋰ ⋰⒞⋰⋰⒭⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒤⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰ ⋰⒜⋰⋰⒜⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰ ⋰⒡⋰⋰⒭⋰⋰⒭⋰⋰⒯⋰⋰⒪⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒤⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰ ⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒨⋰⋰⒭⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒜⋰⋰⒠⋰⋰⒮⋰⋰⒠⋰ ⋰⒣⋰⋰⒤⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒣⋰⋰⒴⋰⋰⒴⋰ ⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒣⋰⋰⒤⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰⋰⒩⋰⋰⒜⋰",
"⋰⒪⋰⋰⒭⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰ ⋰⒪⋰⋰⒭⋰",
"⋰⒣⋰⋰⒴⋰⋰⒴⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒪⋰ ⋰⒩⋰⋰⒜⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒪⋰ ⋰⒨⋰⋰⒯⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒪⋰",
"⋰⒝⋰⋰⒴⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒣⋰⋰⒴⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ?",
"⋰⒬⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒬⋰ ⋰⒭⋰⋰⒣⋰⋰⒠⋰ ⋰⒣⋰⋰⒪⋰ ?",
"⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒨⋰⋰⒯⋰",
"⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒥⋰",
"⋰⒪⋰⋰⒭⋰ ⋰⒝⋰⋰⒟⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰",
"⋰⒪⋰⋰⒭⋰ ⋰⒝⋰⋰⒟⋰⋰⒜⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰⋰⒟⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒰⋰⋰⒭⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒦⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰⋰⒠⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰",
"⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒠⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰",
"⋰⒨⋰⋰⒦⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒩⋰⋰⒜⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰",
"⋰⒯⋰⋰⒠⋰⋰⒥⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒞⋰⋰⒠⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒭⋰⋰⒠⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒴⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒟⋰⋰⒜⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒡⋰⋰⒰⋰⋰⒟⋰⋰⒟⋰⋰⒜⋰",
"⋰⒨⋰⋰⒦⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒝⋰⋰⒠⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒞⋰⋰⒪⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒝⋰⋰⒰⋰⋰⒭⋰ ⋰⒟⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒡⋰⋰⒰⋰⋰⒟⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒱⋰⋰⒜⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒯⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒢⋰⋰⒜⋰⋰⒴⋰⋰⒜⋰",
"⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒭⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰",
"⋰⒨⋰⋰⒞⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒭⋰⋰⒪⋰⋰⒦⋰⋰⒠⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰",
"⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰.⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰",
"⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰",
"⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰",
"⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰",
"⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒯⋰⋰⒠⋰",
"⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰ ⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒲⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒝⋰⋰⒩⋰⋰⒥⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒣⋰⋰⒜⋰⋰⒧⋰⋰⒦⋰⋰⒠⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒱⋰⋰⒜⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒯⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒢⋰⋰⒜⋰⋰⒴⋰⋰⒜⋰",
"⋰Ⓓ⋰⋰⒪⋰⋰⒮⋰⋰⒯⋰",
]
cr_texts = [
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇧​ะะ🇴​ะะ🇸​ะะ🇪​ะะ🇼​ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะะ🇰​ะะ🇪​ะะ🇧​ะะ🇦​ะะ🇨​ะะ🇭​ะะ🇪​ะ, ะ🇹​ะะ🇺​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇰​ะะ🇮​ะะ🇸​ะะ🇸​ะะ🇦​ะะ🇬​ะะ🇦​ะ",
"ะ🇦​ะะ🇦​ะะ🇯​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ, ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะ ะ🇯​ะะ🇦​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇩​ะะ🇮​ะะ🇩​ะะ🇮​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ะ🇸​ะะ🇱​ะะ🇴​ะะ🇼​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇮​ะะ🇾​ะะ🇦​ะ ะ🇨​ะะ🇮​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇸​ะะ🇰​ะะ🇹​ะะ🇦​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ, ะ🇹​ะะ🇲​ะะ🇦​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇸​ะะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇫​ะะ🇮​ะะ🇷​ะะ🇸​ะะ🇪​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ",
"ะ🇨​ะะ🇺​ะะ🇩​ะะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ, ะ🇹​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะ ะ🇩​ะะ🇴​ะะ🇺​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ, ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇳​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ ะ🇼​ะะ🇦​ะะ🇱​ะะ??​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ??​ะ",
"ะ🇴​ะะ🇾​ะะ🇪​ะ ะ🇹​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ, ะ🇮​ะะ🇩​ะะ🇭​ะะ🇦​ะะ🇷​ะ ะ🇦​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇩​ะะ🇺​ะ, ะ🇴​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะะ🇪​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇪​ะะ🇯​ะ, ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇸​ะะ🇺​ะะ🇦​ะะ🇷​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇪​ะะ🇯​ะ, ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ ะ🇴​ะะ🇳​ะ ะ🇰​ะะ🇷​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇰​ะะ🇪​ะ",
"ะ🇹​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะะ🇸​ะะ🇪​ะ, ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇸​ะะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇭​ะะ🇦​ะะ🇷​ะะ🇨​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ ะ🇰​ะะ🇷​ะ ะ🇲​ะะ🇸​ะะ🇬​ะ ะ🇩​ะะ🇪​ะะ🇱​ะะ🇪​ะะ🇹​ะะ🇪​ะ, ะ🇴​ะะ🇮​ะ ะ🇸​ะะ🇺​ะะ🇦​ะะ🇷​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇰​ะะ🇪​ะ",
"ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇫​ะะ🇺​ะะ🇫​ะะ🇮​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇩​ะะ🇮​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇮​ะ",
"ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇦​ะ, ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇦​ะะ🇧​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ",
"ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇺​ะ, ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ, ะ🇮​ะะ🇹​ะะ🇳​ะะ🇦​ะ ะ🇬​ะะ🇳​ะะ🇩​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇦​ะ ะ🇹​ะะ🇺​ะ ะ🇫​ะะ🇮​ะะ🇷​ะะ🇸​ะะ🇪​ะ ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇳​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ",
"ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇯​ะะ🇦​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇦​ะะ🇷​ะะ🇺​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะะ🇦​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ, ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇵​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ, ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇲​ะะ🇪​ะะ🇭​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ, ะ🇦​ะะ🇧​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ",
"ะ🇩​ะะ🇴​ะะ🇺​ะะ🇧​ะะ🇱​ะะ🇪​ะ ะ🇸​ะะ🇪​ะะ🇳​ะะ🇩​ะ ะ🇰​ะะ🇴​ะ ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ, ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇴​ะะ🇩​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇦​ะะ🇦​ะะ🇯​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ",
"ะ🇭​ะะ🇹​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇦​ะะ🇱​ะะ🇦​ะะ🇱​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ., ะ🇷​ะะ🇳​ะะ🇩​ะะ🇾​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇶​ะ ะ🇹​ะะ🇷​ะะ🇾​ะะ🇲​ะะ🇦​ะ",
"ะ🇵​ะะ🇦​ะะ🇷​ะะ🇦​ะ ะ🇱​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇪​ะะ🇬​ะะ🇦​ะ.., ะ🇹​ะะ🇷​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇭​ะะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ",
"ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇨​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ, ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ..",
"ะ🇨​ะะ🇺​ะะ🇩​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ, ะ🇧​ะะ🇭​ะะ🇮​ะะ🇰​ะะ🇦​ะะ🇷​ะะ🇮​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ??​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ.",
"ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇷​ะ, ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇼​ะะ🇪​ะะ🇦​ะะ🇰​ะ",
"ะ🇲​ะะ🇪​ะะ🇷​ะะ🇪​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇵​ะะ🇪​ะ ะ🇪​ะะ🇾​ะ ะ🇹​ะะ🇺​ะ ะ🇭​ะะ🇮​ะะ🇯​ะะ🇩​ะะ🇪​ะ, ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇼​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇴​ะ",
"ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ, ะ🇹​ะะ🇺​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇰​ะะ🇮​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇨​ะะ🇱​ะะ🇦​ะะ🇮​ะะ🇲​ะ ะ🇨​ะะ🇷​ะะ🇼​ะะ🇦​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇸​ะะ🇰​ะะ🇹​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ, ะ??​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇨​ะะ??​ะะ🇺​ะะ🇩​ะ ะ🇯​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇩​ะะ🇮​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇮​ะ, ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇦​ะ",
"ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇦​ะะ🇧​ะ, ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ, ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇺​ะ",
"ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ, ะ🇹​ะะ🇪​ะะ??​ะะ🇾​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ะ🇮​ะะ🇹​ะะ🇳​ะะ🇦​ะ ะ🇬​ะะ🇳​ะะ🇩​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇦​ะ ะ🇹​ะะ🇺​ะ ะ🇫​ะะ🇮​ะะ🇷​ะะ🇸​ะะ🇪​ะ ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇳​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ, ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇯​ะะ🇦​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇦​ะะ🇷​ะะ🇺​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ, ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะะ🇦​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇵​ะ, ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇲​ะะ🇪​ะะ🇭​ะ, ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ",
"ะ??​ะะ🇧​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ, ะ🇩​ะะ🇴​ะะ🇺​ะะ🇧​ะะ🇱​ะะ🇪​ะ ะ🇸​ะะ🇪​ะะ🇳​ะะ🇩​ะ ะ🇰​ะะ🇴​ะ ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇴​ะะ🇩​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇦​ะะ🇦​ะะ🇯​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ, ะ🇭​ะะ🇹​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇦​ะะ🇱​ะะ🇦​ะะ🇱​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ.",
"ะ🇷​ะะ🇳​ะะ🇩​ะะ🇾​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇶​ะ ะ🇹​ะะ🇷​ะะ🇾​ะะ🇲​ะะ🇦​ะ, ะ🇵​ะะ🇦​ะะ🇷​ะะ🇦​ะ ะ🇱​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇪​ะะ🇬​ะะ🇦​ะ..",
"ะ🇹​ะะ🇷​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇭​ะะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ, ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇨​ะะ🇪​ะ ะ??​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ.., ะ🇨​ะะ🇺​ะะ🇩​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ",
"ะ🇧​ะะ🇭​ะะ🇮​ะะ🇰​ะะ🇦​ะะ🇷​ะะ🇮​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇸​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ., ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇷​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇼​ะะ🇪​ะะ🇦​ะะ🇰​ะ, ะ🇲​ะะ🇪​ะะ🇷​ะะ🇪​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇵​ะะ🇪​ะ ะ🇪​ะะ🇾​ะ ะ🇹​ะะ🇺​ะ ะ🇭​ะะ🇮​ะะ🇯​ะะ🇩​ะะ🇪​ะ",
"ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇼​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇴​ะ, ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇨​ะะ🇱​ะะ🇦​ะะ🇮​ะะ🇲​ะ ะ🇨​ะะ🇷​ะะ🇼​ะะ🇦​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇸​ะะ🇰​ะะ🇹​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะ ะ🇯​ะะ🇦​ะ"
"ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇷ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ ะ🇧ะะ🇪ะะ🇯ะ",
"ะ🇴ะะ🇷ะ ะ🇧ะะ🇩ะะ🇦ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ",
"ะ🇴ะะ🇷ะ ะ🇧ะะ🇩ะะ🇦ะ",
"ะ🇴ะะ🇷ะ ะ🇧ะะ🇩ะะ🇦ะ ะ🇴ะะ🇾ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇺ะะ🇷ะ",
"ะ🇴ะะ🇾ะะ🇪ะ ะ🇰ะะ🇪ะะ🇩ะะ🇪ะ",
"ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇰ะะ🇪ะ",
"ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะะ🇳ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ",
"ะ🇲ะะ🇰ะะ🇱ะ ะ??ะะ🇹ะะ🇭ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇨ะะ🇭ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇳ะะ🇦ะะ🇳ะะ🇮ะ ะ🇲ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇱ะ",
"ะ🇹ะะ🇪ะะ🇯ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇷ะะ🇳ะะ🇩ะะ🇨ะะ🇪ะ",
"ะ🇴ะะ🇾ะะ🇪ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇲ะะ🇷ะะ🇪ะะ🇳ะะ🇬ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇾ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇮ะะ🇾ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇬ะะ🇦ะะ🇳ะะ🇩ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇩ะะ🇦ะะ🇩ะะ🇮ะ ะ🇰ะะ🇦ะ ะ🇫ะะ🇺ะะ🇩ะะ🇩ะะ🇦ะ",
"ะ🇲ะะ🇰ะะ🇱ะ ะ🇺ะะ🇹ะะ🇭ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะะ🇳ะะ🇨ะะ🇴ะะ🇩ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ??ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇧ะะ🇺ะะ🇷ะ ะ🇩ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇦ะ ะ🇫ะะ🇺ะะ🇩ะะ🇩ะะ🇦ะ ะ🇲ะะ🇪ะ ะ🇱ะะ🇦ะะ🇺ะะ🇩ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇻ะะ🇦ะ",
"ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇲ะะ🇦ะะ🇷ะ ะ🇬ะะ🇦ะะ🇾ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇲ะะ🇷ะะ🇺ะ",
"ะ🇯ะะ🇦ะะ🇱ะะ🇮ะะ🇩ะ ะ🇰ะะ🇷ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ",
"ะ🇲ะะ🇨ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇷ะะ🇴ะะ🇰ะะ🇪ะะ🇳ะะ🇬ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ",
"ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ.ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ",
"ะ🇷ะะ🇳ะะ🇮ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ",
"ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ ะ🇰ะะ🇮ะะ🇩ะ",
"ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ",
"ะ🇷ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ",
"ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ ะ??ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇼ะะ🇷ะะ🇳ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ",
"ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇺ะะ🇹ะะ🇭ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇨ะะ🇭ะะ🇱ะ ะ🇨ะะ🇺ะะ🇩ะะ🇰ะะ🇪ะ ะ🇩ะะ🇮ะะ🇰ะะ🇭ะะ🇦ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇯ะะ🇱ะะ🇩ะะ🇮ะ ะ🇹ะะ🇾ะะ🇵ะ ะ🇨ะะ🇷ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ ะ🇭ะะ🇦ะะ🇱ะะ🇰ะะ🇪ะ",
"ะ🇨ะะ🇺ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇬ะะ🇱ะ ะ🇳ะะ🇾ะ ะ🇭ะะ🇴ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇨ะะ🇺ะะ🇩ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ ะ🇧ะะ🇳ะะ🇯ะะ🇦ะ ะ🇹ะะ🇺ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇲ะะ🇦ะะ🇰ะะ🇮ะะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇬ะะ🇦ะะ🇳ะะ🇩ะะ🇦ะ ะ🇨ะะ🇾ะะ🇺ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇷ะะ🇭ะะ🇦ะ ะ🇹ะะ🇺ะ ?",
"ะ🇮ะะ🇹ะะ🇳ะะ🇦ะ ะ🇬ะะ🇳ะะ🇩ะะ🇦ะ ะ🇳ะะ🇾ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇦ะะ🇨ะะ🇭ะะ🇪ะ ะ🇸ะะ🇪ะ ะ🇨ะะ🇺ะะ🇩ะ",
"ะ🇲ะะ🇦ะะ🇦ะ⍟ ะ🇱ะะ🇪ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇾ะะ🇦ะ ะ🇹ะะ🇺ะ ะ🇸ะะ🇺ะ⍟ ะ🇧ะะ🇦ะะ🇹ะ ะ🇦ะะ🇧",
"ะ🇲ะะ🇦ะะ🇰ะะ🇦ะะ🇫ะะ🇺ะะ🇩ะะ🇩ะะ🇦ะ ะ🇫ะะ🇦ะะ🇹ะ ะ🇬ะะ🇾ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇷ะะ🇺ะะ🇰ะ",
"ะ🇸ะะ🇭ะะ🇦ะะ🇳ะะ🇹ะ ะ🇧ะะ🇪ะะ🇹ะะ🇭ะ ะ🇲ะะ🇦ะะ🇩ะะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇼ะะ🇷ะะ🇳ะะ🇦ะ ะ🇲ะะ🇦ะะ🇰ะะ🇦ะะ🇧ะะ🇴ะะ🇸ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇪ะะ🇾ะ.",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ..",
"ะ🇱ะะ🇼ะะ🇩ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะะ🇰ะะ🇪ะ ะ🇵ะะ🇬ะะ🇱ะ ะ🇩ะะ🇪ะะ🇰ะะ🇭ะ.",
"ะ🇲ะะ🇦ะะ🇨ะะ🇭ะะ🇦ะะ🇷ะ ะ🇰ะะ🇮ะ ะ🇯ะะ🇭ะะ🇦ะะ🇦ะะ🇹ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇦ะะ🇨ะะ🇭ะะ🇪ะ ะ🇸ะะ🇪ะ ะ🇾ะะ🇭ะะ🇦ะะ🇵ะะ🇪ะ ะ🇹ะะ🇺ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇲ะ ะ🇩ะะ🇺ะ ะ🇹ะะ🇦ะะ🇵ะะ🇦ะ ะ🇹ะะ🇦ะะ🇵ะ?",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ะꜱะะ🇩ะะ🇦ะะ??ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇭ะะ🇳ะ ꜱะ🇧ะꜱะ🇧ะะ🇪ะ ะ🇧ะะ🇩ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ.",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇴ะꜱะꜱะะ🇪ะ ะ🇧ะะ🇦ะะ🇩ะะ🇮ะ ะ??ะะ🇦ะะ🇳ะะ🇩ะะ🇩ะะ🇩ะะ🇩ะะ🇩ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇦ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇧ะะ🇦ะะ🇦ะะ🇿ะ ะ🇪ะะ🇾ะ ะ🇩ะะ🇪ะะ🇰ะะ🇭ะ",
"ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇮ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇦ะะ🇧ะ ะ🇴ะะ🇷..",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇮ะ ะ🇭ะะ🇲ะ ะ🇳ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇪ะ ꜱะ🇹ะะ🇭ะ ะ🇷ะะ🇪ะะ🇪ะะ🇱ะꜱะ ะ🇧ะะ🇳ะะ🇪ะะ🇬ะะ🇦ะ ะ🇷ะะ🇴ะะ🇦ะะ🇩ะ ะ🇵ะะ🇪ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇪ะะ🇰ะ ะ🇩ะะ🇦ะะ🇲ะ ะ🇹ะะ🇴ะะ🇵ะ ꜱะ🇪ะxะ🇾ะ",
"ะ🇲ะะ🇦ะะ🇱ะะ🇺ะ🇲ะ ะ🇳ะะ🇦ะ ะ🇵ะะ🇭ะ🇷ะ ะ🇰ะะ🇪ꜱะะ🇪ะ ะ🇱ะะ🇪ะะ🇹ะะ🇦ะ ะ🇭ะะ🇺ะ ะ🇲ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇹ะะ🇦ะะ🇵ะะ🇦ะ ะ🇹ะะ🇦ะะ🇵ะะ🇵ะะ🇵ะะ🇵ะะ🇵ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ ะ🇹ะะ🇺ะ ะ🇰ะะ🇪ะะ🇷ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇾ะะ🇵ะะ🇮ะะ🇳ะะ🇬ะ ะ🇰ะะ🇷ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ",
"ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇵ะะ🇰ะะ🇩ะ ะ🇱ะะ🇼ะะ🇩ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะ ะ🇼ะะ🇷ะะ🇳ะะ🇦ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇵ะะ🇰ะะ🇩ะ",
"ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇰ะะ🇮ะ ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇲ะะ🇹ะะ🇨ะะ🇭ะ ะ🇰ะะ🇷ะะ🇷ะะ🇷ะ",
"ะ🇱ะะ🇼ะะ🇩ะะ🇦ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ ะ🇹ะะ🇺ะ",
"ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ะ🇰ะะ🇮ะ ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇲ะะ🇹ะะ🇨ะะ🇭ะ ะ🇳ะะ🇭ะะ🇮ะ ะ🇭ะะ🇴ะ ะ🇷ะะ🇭ะะ🇮ะ ะ🇰ะะ🇾ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇪ะะ🇸ะะ🇪ะ",
"ะ🇦ะะ🇱ะะ🇪ะ ะ🇦ะะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇱ะะ🇦ะ ะ🇧ะะ🇨ะะ🇭ะะ🇦ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇰ะะ🇦ะ ะ🇧ะะ🇴ะะ🇸ะะ🇩ะะ🇦ะ ะ🇸ะะ🇺ะะ🇳ะ",
"ะ🇨ะะ🇭ะะ🇺ะะ🇩ะ ะ🇬ะะ🇾ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇧ะะ🇦ะะ🇦ะะ🇿ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ꜱะ🇪ะะ🇪ะะ🇪ะ ะ🇹ะะ🇺ะ",
"ะ🇲ะะ🇪ะะ🇳ะะ🇺ะ ะ🇰ะะ🇮ะ ะ🇵ะะ🇹ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ",
"ะ🇰ะะ🇴ะะ🇮ะ ะ🇧ะะ🇦ะะ🇦ะะ🇹ะ ะ🇳ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ",
"ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะ ะ🇲ะะ🇦ะะ🇰ะะ🇦ะะ🇧ะะ🇴ะะ🇸ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ",
"ะ🇽ะะ🇭ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇰ะะ🇮ะะ🇩ะꜱะꜱะꜱะꜱะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะ ะ🇬ะะ🇾ะะ🇮ะ ะ🇦ะะ🇧ะ ꜰะ🇷ะะ🇦ะ🇷ะ ะ🇲ะะ🇹ะ ะ🇭ะะ🇴ะะ🇳ะะ🇦ะ",
"ะ🇾ะะ🇪ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇨ะะ🇭ะะ🇱ะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ",
"ะ🇰ะะ🇮ะะ🇩ะꜱะꜱะꜱะ ꜰะ🇷ะะ🇦ะ🇷ะ ะ🇳ะะ🇦ะ ะ🇭ะะ🇴ะ ะ🇹ะะ🇺ะ ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇭ะ",
"ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇼ะะ🇩ะะ🇪ะ ꜱะ🇭ะ🇷ะ🇲ะ ะ🇰ะะ🇷ะ",
"ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇮ะ ะ🇬ะะ🇱ะะ🇮ะะ🇾ะะ🇦ะ ะ🇵ะะ🇩ะะ🇼ะะ🇪ะะ🇬ะะ🇦ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇴ะ",
"ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇳ะะ🇦ะะ🇱ะะ🇱ะะ🇮ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇰ะะ🇪ะ",
"ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ꜱะ🇦ะะ🇩ะะ🇦ะ🇰ะ ะ🇵ะ🇷ะ ะ🇱ะะ🇮ะะ🇹ะะ🇦ะะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ 😂😆🤤",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ ะ🇲ะะ🇦ะะ🇩ะะ🇪ะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇴ะะ🇩ะ ะ🇰ะ🇷ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ꜱะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇺ะ 😼😂🤤",
"ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇳ะะ🇪ะ ꜱะ🇭ะ🇴ะ🇷ะ ะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇨ะะ🇭ะะ🇴ะ🇷ะ ะ🇭ะะ🇪ะ 💋💋💦",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ 😂👻🔥",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇦ะะ🇮ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇦ะ ะ🇦ะะ🇮ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะ ะ🇧ะะ🇪ะะ🇩ะ ะ🇵ะะ🇪ะะ🇭ะะ🇮ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะ ะ🇩ะะ🇮ะะ🇦ะ 💦💦💦💦",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇪ะ ะ🇲ะะ🇪ะ ะ🇦ะะ🇦ะะ🇦ะ🇬ะ ะ🇱ะะ🇦ะะ🇬ะะ🇦ะะ🇩ะะ🇮ะะ🇦ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇲ะะ🇴ะะ🇹ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇰ะะ🇪ะ 🔥🔥💦😆😆",
"ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇳ะะ🇮ะะ🇰ะะ🇦ะะ🇱ะ",
"ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ 😆👻🤤",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะะ🇹ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇰ะะ🇪ะ ะ🇵ะะ🇺ะะ🇷ะะ🇦ะ ꜰะ🇦ะะ🇦ะะ🇩ะ ะ🇩ะะ🇮ะะ🇦ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇰ะะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ 😆💦🤤",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇰ะะ🇴ะ ะ🇪ะะ🇹ะะ🇳ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇹ะะ🇴ะ ะ🇲ะะ🇪ะะ🇷ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇧ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะะ🇾ะะ🇮ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇹ะะ🇦ะ ꜰะ🇮ะ🇷ꜱะะ🇪ะ ♥️💦😆😆😆😆",
"ะ🇭ะะ🇦ะะ🇷ะะ🇮ะ ะ🇭ะะ🇦ะะ🇷ะะ🇮ะ ะ🇬ะะ🇭ะะ🇦ะะ🇦ꜱะ ะ🇲ะะ🇪ะ ะ🇯ะะ🇭ะะ🇴ะะ🇵ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ 🤣🤣💋💦",
"ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇹ะะ🇪ะะ🇷ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇰ะะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ ะ🇹ะะ🇪ะะ🇷ะะ🇦ะ ะ🇧ะะ🇦ꜱะะ🇰ะะ🇦ะ ะ🇳ะะ🇭ะะ🇮ะ ะ🇭ะะ🇪ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ꜱะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇺ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇧ะะ🇴ะะ🇲ะ🇧ะ ะ🇩ะะ🇦ะะ🇱ะะ🇰ะะ🇪ะ ะ🇺ะะ🇩ะะ🇦ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇼ะะ🇩ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇹ะะ🇷ะะ🇦ะะ🇮ะ🇳ะ ะ🇲ะะ🇪ะ ะ🇱ะะ🇪ะะ🇯ะะ🇦ะะ🇰ะะ🇪ะ ะ🇹ะะ🇴ะะ🇵ะ ะ🇧ะะ🇪ะะ🇩ะ ะ🇵ะะ🇪ะ ะ🇱ะะ🇮ะะ🇹ะะ🇦ะะ🇰ะะ🇪ะ ะ🇨ะะ??ะะ🇴ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 🤣🤣💋💋",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇳ะะ🇺ะะ🇩ะะ🇪ꜱะ ะ🇬ะะ🇴ะะ🇴ะ🇬ะ🇱ะะ🇪ะ ะ🇵ะะ🇪ะ ะ🇺ะะ🇵ะะ🇱ะะ🇴ะะ🇦ะ🇩ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇪ะะ🇼ะะ🇩ะะ🇪ะ 👻🔥",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇳ะะ🇺ะะ🇩ะะ🇪ꜱะ ะ🇬ะะ🇴ะะ🇴ะ🇬ะ🇱ะะ🇪ะ ะ🇵ะะ🇪ะ ะ🇺ะะ🇵ะะ🇱ะะ🇴ะะ🇦ะ🇩ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇪ะะ🇼ะะ🇩ะะ🇪ะ 👻🔥",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇰ะะ🇪ะ ะ🇻ะะ🇮ะะ🇩ะะ🇪ะ🇴ะ ะ🇧ะะ🇦ะะ🇳ะะ🇦ะะ🇰ะะ🇪ะ ะ🇽ะ🇳🇽🇽.🇨🇴🇲 ะ🇵ะะ🇪ะ ะ🇳ะะ🇪ะะ🇪ะะ🇱ะะ🇦ะ🇲ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 💦💋",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇦ะะ🇮ะ ะ🇰ะะ🇴ะ ะ🇵ะ🇴🇷🇳🇭🇺🇧.🇨🇴🇲 ะ🇵ะะ🇪ะ ะ🇺ะะ🇵ะะ🇱ะะ🇴ะะ🇦ะ🇩ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ 🤣💋💦",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇪ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇦ะะ🇰ะะ🇰ะ🇴ะ ꜱะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇼ะะ🇦ะะ🇻ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ 🤣🤣",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ꜰะะ🇦ะะ🇦ะะ🇩ะะ🇰ะะ🇪ะ ะ🇷ะะ🇦ะะ🇰ะะ🇩ะะ🇮ะะ🇦ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇯ะะ🇦ะะ🇦ะ ะ🇦ะะ🇧ะะ🇧ะ ꜱะะ🇮ะะ🇱ะะ🇼ะะ🇦ะะ🇱ะะ🇪ะ 👄👄",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇦ะะ🇦ะะ🇱ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇱ะะ🇪ะะ🇹ะะ🇮ะ ะ🇲ะะ🇪ะะ🇷ะะ🇮ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇧ะะ🇦ะะ🇩ะะ🇪ะ ะ🇲ะะ🇦ꜱะะ🇹ะะ🇮ะ ꜱะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇲ะะ🇪ะะ🇳ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇦ะ ะ🇧ะะ🇴ะะ🇭ะะ🇴ะะ🇹ะ ꜱะะ🇦ꜱะะ🇹ะะ🇪ะ ꜱะะ🇪ะ",
"ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇹ะะ🇺ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ꜱะะ🇪ะ ะ🇱ะะ🇪ะะ🇬ะะ🇦ะ ะ🇵ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇰ะะ🇦ะ🇷ะะ🇰ะะ🇪ะ ะ🇳ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะ 💦💋",
"ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇦ะะ🇬ะะ🇱ะะ🇮ะ ะ🇧ะะ🇦ะะ🇦ะ🇷ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇱ะะ🇪ะะ🇰ะะ🇪ะ ะ🇦ะะ🇦ะะ🇾ะะ🇦ะ ะ🇲ะะ🇦ะะ🇹ะะ🇭ะ ะ🇰ะะ🇦ะะ🇹ะ ะ🇴ะ🇷ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇲ะะ🇴ะะ🇹ะะ🇪ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇼ะะ🇦ะะ🇾ะะ🇦ะ ะ🇲ะะ🇦ะะ🇹ะะ🇭ะ ะ🇰ะะ🇦ะ🇷ะ",
"ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇧ะะ🇪ะะ🇹ะะ🇦ะ ะ🇹ะะ🇺ะะ🇯ะะ🇭ะะ🇪ะ ะ🇲ะะ🇦ะะ🇦ꜱะ🇫ะ ะ🇰ะะ🇮ะะ🇦ะ 🤣ะ🇹ะะ🇺ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇰ะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ",
"ꜱะ🇭ะะ🇦ะะ🇷ะะ🇦ะ🇲ะ ะ🇰ะะ🇦ะ🇷ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇦ะ ะ🇬ะะ🇦ะะ🇦ะะ🇱ะะ🇮ะะ🇦ะ ꜱะ🇺ะะ🇳ะะ🇼ะะ🇦ะะ🇾ะะ🇪ะะ🇬ะะ🇦ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇺ะะ🇵ะะ🇪ะ🇷ะ",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇦ะะ🇺ะะ🇰ะะ🇦ะะ🇹ะ ะ🇳ะะ🇭ะะ🇮ะ ะ🇭ะะ🇪ะะ🇹ะ🇴ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇱ะะ🇪ะะ🇰ะะ🇪ะ ะ🇦ะะ🇦ะะ🇾ะะ🇦ะ ะ🇲ะะ🇦ะะ🇹ะะ🇭ะ ะ🇰ะะ🇦ะ??ะ ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะ",
"ะ🇰ะะ🇮ะะ🇩ะ🇿ะ ะ🇲ะะ🇦ะะ🇩ะะ🇦ะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇰ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะ🇷ะ ะ🇱ะะ🇮ะะ🇾ะะ🇪ะ ะ🇧ะะ🇭ะะ🇦ะะ🇮ะ ะ🇩ะะ🇪ะะ🇩ะะ🇮ะะ🇾ะะ🇦ะ",
"ะ🇯ะะ🇺ะะ🇳ะะ🇬ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะ ะ🇳ะะ🇦ะะ🇨ะะ🇭ะะ🇹ะะ🇦ะ ะ🇭ะะ🇪ะ ะ🇲ะะ🇴ะ🇷ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇦ะะ🇮ะ ะ🇩ะะ🇪ะะ🇰ะะ🇰ะะ🇪ะ ꜱะ🇦ะ🇧ะ ะ🇧ะะ🇴ะะ🇱ะะ🇹ะะ🇪ะ ะ🇴ะะ🇳ะ🇨ะะ🇪ะ ะ🇲ะะ🇴ะ🇷ะะ🇪ะ ะ🇴ะะ🇳ะ🇨ะะ🇪ะ ะ🇲ะะ🇴ะ🇷ะะ🇪ะ 🤣🤣💦💋",
"ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇲ะะ🇪ะ ะ🇷ะะ🇪ะะ🇭ะะ🇹ะะ🇦ะ ะ🇭ะะ🇪ะ ꜱะ🇦ะะ🇳ะะ🇩ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇦ะ ะ🇴ะ🇷ะ ะ🇧ะะ🇦ะะ🇳ะะ🇦ะ ะ🇩ะะ🇮ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ 🤤🤣",
"ꜱะ🇦ะ🇧ะ ะ🇧ะะ🇴ะะ🇱ะะ🇹ะะ🇪ะ ะ🇲ะะ🇺ะะ🇯ะะ🇭ะะ🇰ะ🇴ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ะ🇨ะะ🇾ะะ🇺ะะ🇰ะะ🇮ะ ะ🇲ะะ🇪ะะ🇳ะะ🇪ะ ะ🇰ะ🇷ะะ??ะะ🇮ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇵ะ🇷ะะ🇪ะะ🇬ะะ🇳ะะ🇪ะะ🇳ะะ🇹ะ 🤣🤣",
"ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇦ะ ะ🇱ะะ🇴ะะ🇺ะะ🇩ะะ🇦ะ ะ🇴ะ🇷ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇴ะะ🇩ะะ🇦ะ",
"ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇹ะะ🇺ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇨ะะ🇭ะะ🇮ะะ🇾ะะ🇦ะ ะ🇩ะะ🇮ะะ🇰ะะ🇦ะ",
"ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇮ะะ🇦ะ ะ🇳ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะ ะ🇰ะะ🇦ะ🇷ะะ🇰ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇭ะะ🇪ะ ะ🇧ะะ🇦ะะ🇩ะะ🇮ะ ꜱะ🇪xะ🇾ะ ะ🇺ꜱะะ🇰ะ??ะ ะ🇵ะะ🇮ะะ🇱ะะ🇦ะะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇴ะะ🇩ะะ🇪ะะ🇳ะะ🇬ะะ🇪ะ ะ🇵ะะ🇪ะะ🇵ꜱะะ🇮ะ",
"2 ะ🇷ะะ🇺ะะ🇵ะะ🇦ะ🇾ะ ะ🇰ะะ🇮ะ ะ🇵ะะ🇪ะะ🇵ꜱะะ🇮ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇺ะะ🇲ะะ🇲ะะ🇾ะ ꜱะ🇦ะ🇧ꜱะะ🇪ะ ꜱะ🇪xะ🇾ะ 💋💦",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇪ะะ🇪ะ🇲ꜱะ ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇼ะะ🇦ะะ🇻ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇲ะะ🇦ะะ🇩ะะ🇪ะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇴ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 💦🤣",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะะ🇰ะะ🇪ะ ꜰะะ🇦ะ🇷ะะ🇦ะ🇷ะ ะ🇭ะะ🇴ะะ🇯ะะ🇦ะะ🇻ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇭ะะ🇺ะะ🇮ะ ะ🇭ะะ🇺ะะ🇮ะ ะ🇭ะะ🇺ะะ🇮ะ",
"ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇱ะะ🇦ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 💋💦🤣",
"ะ🇦ะะ🇷ะะ🇪ะ ะ🇷ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇨ะะ🇾ะะ🇺ะ ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇵ะะ🇦ะะ🇰ะะ🇦ะะ🇩ะ ะ🇳ะะ🇦ะ ะ🇵ะะ🇦ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇭ะะ🇦ะ ะ🇦ะะ🇵ะะ🇳ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇰ะะ🇦ะ ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ🤣🤣",
"ꜱะ🇺ะะ🇳ะ ꜱะ🇺ะะ🇳ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇯ะะ🇭ะะ🇦ะะ🇳ะะ🇹ะ🇴ะ ะ🇰ะะ🇪ะ ꜱะ🇴ะะ🇺ะะ🇩ะะ🇦ะะ🇬ะะ🇦ะ🇷ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇺ะะ🇲ะะ🇲ะะ🇾ะ ะ🇰ะะ🇮ะ ะ🇳ะะ🇺ะะ🇩ะะ🇪ꜱะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ",
"ะ🇦ะะ🇧ะะ🇪ะ ꜱะ🇺ะะ🇳ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ ꜰะะ🇦ะะ🇦ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇰ะะ🇭ะะ🇺ะะ🇱ะะ🇪ะ ะ🇧ะะ🇦ะะ🇯ะะ🇦ะ🇷ะ ะ🇲ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇦ะ 🤣🤣💋",
"ꜱะ🇭ะ🇷ะ🇲ะ ะ🇰ะ🇷ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะ ะ🇵ะะ🇰ะะ🇩ะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ",
"ะ🇹ะะ🇺ะ ะ🇪ะะ🇰ะ ะ🇰ะะ🇦ะะ🇦ะ🇲ะ ะ🇰ะ🇷ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇺ะะ🇩ะะ🇼ะะ🇦ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇸ะะ🇹ะะ🇭ะ",
"ะ🇷ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇩ะะ🇰ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇴ะ🇷ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ ะ🇰ะะ🇮ะะ🇩ꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะ",
"ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇪ะะ??ะ🇳ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะะ🇮ะ ะ🇩ะะ🇦ะะ🇦ะะ🇱ะ",
"ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇴ꜱะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ",
"ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇺ꜱะะ🇼ะะ🇦ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ",
"ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇺ะะ🇩ะะ🇪ะ ะ🇹ะะ🇲ะะ🇨ะ",
"ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇹ะะ🇦ะะ🇰ะะ🇰ะะ🇪ะ ะ🇹ะะ🇲ะะ🇱ะ",
"ะ🇦ะะ🇧ะะ🇱ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇦ะ ะ🇰ะะ🇭ะะ🇦ะ🇳ะ ะ🇩ะะ🇦ะ🇳ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇳ะะ🇪ะ ะ🇰ะะ🇮ะ ะ🇧ะะ🇦ะ🇷ะะ🇮ะะ🇮ะ",
"ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ꜱะ🇧ꜱะะ🇪ะ ะ🇧ะะ🇩ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะ ะ🇯ะะ🇭ะะ🇦ะะ🇹ะ ะ??ะะ🇪ะ ะ🇵ะะ🇮ꜱะꜱะꜱะ🇺ะะ🇺ะะ🇺ะะ🇺ะะ🇺ะะ🇺ะะ🇺ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇵ะะ🇪ะ ะ🇱ะะ🇹ะะ🇰ะะ🇮ะะ🇹ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะ ะ🇰ะะ🇮ะ ะ🇧ะะ🇴ะะ🇳ะะ🇩ะ ะ🇭ะ ะ🇹ะะ🇺ะะ🇺ะะ🇺ะ",
"ะ🇰ะะ🇦ꜱะะ🇭ะ ะ🇴ꜱะ ะ🇩ะะ🇮ะ🇳ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะ🇷ะะ🇰ะะ🇪ะ ꜱะ🇴ะะ🇯ะะ🇹ะะ🇦ะ ะ🇲ะ ะ🇹ะะ🇺ะ ะ🇵ะะ🇦ะะ🇮ะะ🇩ะะ🇦ะ ะ🇳ะะ🇦ะ ะ🇭ะะ🇴ะะ🇹ะะ🇦ะะ🇦ะ",
"ะ🇬ะะ🇱ะะ🇹ะะ🇮ะ ะ🇰ะ🇷ะะ🇩ะะ🇮ะ ะ🇹ะะ🇺ะะ🇯ะะ🇼ะ ะ🇵ะะ🇦ะะ🇮ะะ🇩ะะ🇦ะ ะ🇰ะ🇷ะะ🇰ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะ ะ🇳ะะ🇪ะ ะ🇦ะะ🇧ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇹ะะ🇺ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇵ะะ🇰ะะ🇩ะะ🇩ะะ??ะ",
"ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇦ะะ🇮ะ🇳ะ ะ🇱ะะ🇼ะะ🇩ะะ🇦ะ ะ🇩ะะ🇦ะะ🇱ะ ะ🇱ะะ🇪ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะะ🇦ะะ🇦ะ",
"ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇪ะะ🇮ะ🇳ะ ะ🇧ะะ🇦ะะ🇲ะะ🇧ะ🇺ะ ะ🇩ะะ🇪ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะ",
"ะ🇬ะะ🇦ะะ🇳ะะ🇩ะ ꜰะะ🇹ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇱ะะ🇰ะะ🇰ะะ🇰ะ ะ🇹ะะ🇺ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ะ🇬ะะ🇴ะะ🇹ะะ🇪ะ ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇪ะ ะ🇧ะะ🇭ะะ🇮ะ ะ🇧ะะ🇦ะะ🇩ะะ🇪ะ ะ🇭ะะ🇴ะ, ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇳ะะ🇮ะะ🇨ะะ🇭ะะ🇪ะ ะ🇭ะะ🇮ะ ะ🇷ะะ🇪ะะ🇭ะะ🇹ะะ🇪ะ ะ🇭ะะ🇦ะ",
"ะ🇭ะะ🇦ะะ🇿ะะ🇦ะะ🇦ะ🇷ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇦ะะ🇮ะ🇳ะ",
"ะ🇯ะะ🇭ะะ🇦ะะ🇦ะะ🇳ะะ🇹ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ꜱะꜱะ🇺ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ ะ🇸ะะ🇺ะะ🇳ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇰ะะ🇦ะะ🇱ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ",
"ะ🇰ะะ🇭ะะ🇴ะะ🇹ะะ🇪ะ🇾ะ ะ🇰ะะ🇮ะ ะ🇦ะะ🇺ะะ🇱ะะ🇩ะะ🇦ะ ะ🇪ะะ🇾ะ ะ🇹ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ",
"ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇦ะ ะ🇦ะะ🇼ะะ🇱ะะ🇦ะะ🇹ะ ะ🇯ะะ🇦ะะ🇮ะꜱะะ🇦ะ ะ🇱ะะ🇬ะ ะ🇷ะะ🇭ะะ🇦ะ ะ🇹ะะ🇺ะ",
"ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇮ะ ะ🇯ะะ🇦ะะ🇹ะ ะ🇯ะะ🇦ะะ🇮ꜱะะ🇦ะ ะ🇪ะะ🇾ะ ะ🇹ะะ🇺ะ ",
"ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇹ะะ🇦ะะ🇹ะะ🇹ะะ🇦ะ ะ🇪ะะ🇾ะ ะ🇹ะะ🇺ะ",
"ะ🇹ะะ🇪ะะ🇹ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ.ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ , ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇷ะะ🇳ะะ🇩ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะ",
"ะ🇱ะะ🇦ะะ🇻ะะ🇩ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇱ะ ะ🇵ะะ🇰ะะ🇩ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ",
"ะ🇲ะะ🇺ะะ🇭ะ ะ🇲ะะ🇪ะะ🇮ะ ะ🇱ะะ🇪ะะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇦ꜱะะ🇮ะะ🇳ะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇧ะะ🇪ะะ🇹ะะ🇭ะ ะ🇴ะ🇷ะ ะ🇨ะะ🇺ะะ🇩ะ",
"ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇱ะะ🇼ะะ🇩ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะ",
"ะ🇭​ะะ🇦​ะะ🇭​ะะ🇦​ะะ🇭​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇬​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇺​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะ ะ🇬​ะะ🇾​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇭​ะะ🇦​ะะ🇳​ะะ🇪​ะ ะ🇰​ะะ🇮​ะ ะ🇺​ะะ🇱​ะะ🇦​ะะ🇩​ะะ🇩​ะะ🇩​ะ",
"ꜱ​ะ🇦​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇺​ะะ🇮​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇦​ะะ🇮​ะ🇳​ะ ะ🇰​ะะ🇺​ะะ🇹​ะะ🇪​ะ ะ🇰​ะะ🇦​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇪​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇪​ะะ🇮​ะ🇳​ะ ะ🇰​ะะ🇪​ะะ🇪​ะะ🇩​ะะ🇪​ะ ะ🇵​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇾​ะ",
"ะ🇳​ะะ🇾​ะ ะ🇳​ะะ🇾​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ꜱ​ะ🇺​ะะ🇳​ะะ🇳​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇪​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ ะ🇹​ะะ🇲​ะะ🇱​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะ",
"ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะ🇳​ะ ะ🇰​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะะ🇨​ะะ🇭​ะะ🇦​ะะ🇵​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇾​ะะ🇭​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇹​ะะ🇳​ะะ🇮​ะะ🇮​ะะ🇮​ะ",
"ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇱​ะะ🇦​ะะ🇼​ะะ🇩​ะะ🇦​ะ ะ🇱​ะะ🇪​ะะ🇱​ะะ🇪​ะ ะ🇹​ะะ🇺​ะ ะ🇦​ะะ🇬​ะะ🇦​ะ🇷​ะ ะ🇨​ะะ🇭​ะะ🇦​ะะ🇮​ะะ🇾​ะะ🇪​ะ ะ🇹​ะะ🇴​ะะ🇭​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ🇺​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇮​ะะ🇾​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇵​ะะ🇪​ะ ะ🇯​ะ🇨​ะ🇧​ะ ะ🇨​ะะ🇭​ะะ🇦​ะะ🇩​ะะ🇭​ะะ🇦​ะะ🇦​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ꜱ​ะ🇦​ะะ🇲​ะะ🇯​ะะ🇭​ะะ🇦​ะะ🇦​ะ ะ🇱​ะะ🇦​ะะ🇼​ะะ🇩​ะะ🇪​ะ",
"ะ🇾​ะะ🇦​ะ ะ🇩​ะะ🇺​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇪​ะ ะ🇹​ะะ🇦​ะะ🇵​ะะ🇦​ะะ🇦​ะ ะ🇹​ะะ🇦​ะะ🇵​",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะ🇳​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇷​ะะ🇴​ะะ🇿​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇪​ะ ꜱ​ะะ🇦​ะะ🇦​ะะ🇹​ะะ🇭​ะ ะ🇲​ะ🇲​ꜱ​ะ ะ🇧​ะะ🇦​ะะ🇳​ะะ🇦​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇰​ะะ🇦​ะ ะ🇭​ะะ🇺​",
"ะ🇹​ะะ🇺​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇮​ะะ🇾​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇰​ะะ🇭​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇦​ะะ🇦​ะ🇳​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇮​ะะ🇾​ะะ🇦​ะ",
"ะ🇦​ะะ🇺​ะ🇷​ะ ะ🇰​ะะ🇮​ะะ🇹​ะะ🇳​ะะ🇦​ะ ะ🇧​ะะ🇴​ะะ🇱​ะะ🇺​ะ ะ🇧​ะะ🇪​ะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇳​ะะ🇳​ะ ะ🇧​ะะ🇭​ะะ🇦​ะ🇷​ะ ะ🇬​ะะ🇦​ะะ🇾​ะะ🇦​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇹​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇦​ะะ🇧​ะ🇨​ะ🇩​ะ ะ🇱​ะะ🇮​ะะ🇰​ะะ🇭​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ะ ะ🇱​ะะ🇪​ะะ🇰​ะะ🇦​ะ🇷​ะ ะ🇲​ะะ🇦​ะะ🇮​ะ ꜰ​ะะ🇦​ะ🇷​ะะ🇦​ะ🇷​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇮​ะะ🇩​ะะ🇮​ะะ🇮​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇧​ะะ🇦​ะะ🇨​ะะ🇭​ะะ🇪​ะะ🇪​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ??​ะ🇴​ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ",
"ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇵​ะะ🇮​ะะ🇱​ะะ🇱​ะะ🇦​ะ ะ🇪​ะะ🇾​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇯​ะะ🇯​ะะ🇯​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇵​ะ ะ🇭​ะะ🇺​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇭​ะะ🇦​ะะ🇦​ะะ🇹​ะ ะ🇩​ะะ🇦​ะะ🇦​ะะ🇱​ะะ🇱​ะะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇦​ะ🇬​ะ ะ🇯​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇺​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ะ ꜱ​ะะ🇦​ะ🇷​ะะ🇦​ะะ🇰​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇦​ะะ🇦​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ะ🇬​ะ🇧​ะ ะ🇷​ะ🇴​ะ🇦​ะ🇩​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇯​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะ🇨​ะ🇭​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​É​ะ ะ🇰​ะะ🇦​ะะ🇦​ะะ🇱​ะะ🇮​ะ ะ🇲​ะะ🇮​ะะ🇹​ะ🇨​ะ🇭​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ꜱ​ะะ🇦​ꜱ​ะะ🇹​ะะ🇮​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇰​ะะ🇦​ะะ🇧​ะะ🇺​ะะ🇹​ะะ🇦​ะ🇷​ะ ะ??​ะะ🇦​ะะ🇦​ะะ🇱​ะ ะ🇰​ะะ🇪​ะ ꜱ​ะ🇴​ะะ🇺​ะะ🇵​ะ ะ🇧​ะะ🇦​ะะ🇳​ะะ🇦​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇩​ะะ🇪​ะะ🇹​ะ🇴​ะ🇱​ะ ะ🇩​ะะ??​ะะ🇦​ะะ🇱​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇵​ะะ🇹​ะ🇴​ะ🇵​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ะ🇧​ะะ🇮​ꜱ​ะะ🇹​ะะ🇦​ะ🇷​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇦​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ??​ะะ🇴​ ะ🇦​ะะ🇲​ะะ🇪​ะ🇷​ะะ🇮​ะ🇨​ะะ🇦​ะ ะ🇬​ะะ🇭​ะะ🇺​ะะ🇲​ะะ🇦​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇳​ะะ🇦​ะะ🇦​ะ🇷​ะะ🇮​ะะ🇾​ะะ🇦​ะ🇱​ะ ะ🇵​ะะ🇭​ะ🇴​ะ🇷​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇪​ะ ะ🇬​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇪​ะ ะ🇩​ะะ🇪​ะะ🇹​ะ🇴​ะ🇱​ะ ะ🇩​ะะ🇦​ะะ🇦​ะะ🇱​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ะ🇭​ะ🇴​🇷​🇱​🇮​🇨​🇰​ꜱ​ะ ะ🇵​ะะ🇮​ะะ🇱​ะะ🇦​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ꜱ​ะะ🇦​ะ🇷​ะะ🇦​ะะ🇰​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะ",
"ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะะ🇦​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇵​ะะ🇦​ะะ🇰​ะะ🇦​ะะ🇩​ะ ะ🇱​ะะ🇪​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇦​ะะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ꜱ​ะ ะ🇬​ะะ🇪​ะะ🇾​ะะ🇮​ะ ะ🇰​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇱​ะะ🇦​ะะ🇼​ะะ🇩​ะะ🇪​ะะ🇪​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇯​ꜱ​ะะ🇴​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะ🇽​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇩​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇺​ะะ🇺​ะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ꜱ​ะะ🇴​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะ🇳​ะะ🇳​ะะ🇳​ะ ะ🇰​ะะ🇴​ะ ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇩​ะะ🇩​ะะ🇺​ะะ🇺​ะะ🇺​ะะ🇺​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะ🇽​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇩​ะะ🇩​ะะ🇩​ะ",
"ะ🇹​ะะ🇺​ะ ะ🇳​ะะ🇮​ะะ🇰​ะะ🇦​ะะ🇱​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇦​ะะ🇨​ะะ🇭​ะะ🇪​ะ",
"ะ??​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇯​ะะ🇦​ะะ🇦​ะ🇳​ะ ะ🇪​ะะ🇾​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ꜱ​ะ🇪​x​ะ🇾​ะ ะ🇧​ะะ🇦​ะะ🇭​ะะ🇪​ะ🇳​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇴​ะะ🇵​ะ",
"⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇧⚡🇭⚡?? ⚡🇧⚡🇳⚡🇦⚡🇱⚡🇪 ⚡🇲⚡🇺⚡🇯⚡🇪 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇰⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇪⚡🇾 ⚡🇾⚡🇦⚡🇦⚡🇩 ⚡🇪⚡🇾 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇦 ⚡🇳⚡🇦 ⚡🇹⚡🇾⚡🇲⚡🇵⚡🇦⚡🇸⚡🇸",
"⚡🇴⚡🇾⚡🇪 ⚡🇺⚡🇳⚡🇫⚡🇺⚡🇳⚡🇳⚡🇾 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇲⚡🇹⚡🇹 ⚡🇰⚡🇷",
"⚡🇴⚡🇭 ⚡🇭⚡🇪⚡🇱⚡🇱⚡🇴 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇹⚡🇪⚡??⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇴⚡🇷 ⚡🇹⚡🇺 ⚡🇻 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇦⚡🇺⚡🇰⚡🇦⚡🇹 ⚡🇲⚡🇪 ⚡🇷⚡🇭⚡🇦 ⚡🇰⚡🇷.",
"⚡🇴⚡🇾⚡🇾 ⚡🇰⚡🇮⚡🇳⚡🇳⚡🇪⚡🇷 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇬⚡🇨 ⚡🇲⚡🇪 ⚡🇦⚡🇦⚡🇳⚡🇪 ⚡🇰⚡🇮 ⚡🇵⚡🇪⚡🇷⚡🇲⚡🇮⚡🇸⚡🇸⚡🇮⚡🇴⚡🇳 ⚡🇰⚡🇮⚡🇸⚡🇳⚡🇪 ⚡🇩⚡🇮.",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇪⚡🇰 ⚡🇧⚡🇦⚡🇦⚡🇷.",
"⚡🇸⚡🇺⚡🇳 ⚡🇸⚡🇺⚡🇳 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇦.",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇨⚡🇦 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇦.",
"⚡🇴⚡🇾⚡🇪 ⚡🇨⚡🇭⚡🇴⚡🇹⚡🇮 ⚡🇯⚡🇦⚡🇹⚡🇮 ⚡🇰⚡🇪 ⚡🇹⚡🇲⚡🇷.",
"⚡🇰⚡🇾? ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇰⚡🇮⚡🇩⚡🇩⚡🇪.",
"⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇨⚡🇴⚡🇲 ⚡🇬⚡🇦⚡🇳⚡🇬 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇰⚡🇴 ⚡🇹⚡🇦⚡🇬 ⚡🇨⚡🇷⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇺",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇧⚡🇸",
"⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇸⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇵⚡🇦⚡🇵⚡🇦 ⚡🇧⚡🇴⚡🇱",
"⚡🇸⚡🇮⚡🇩⚡🇪 ⚡🇭⚡🇴⚡🇯⚡🇦 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇦⚡🇧",
"⚡🇭⚡🇾⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇧⚡🇭⚡🇬 ⚡🇲⚡🇦⚡🇹 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩",
"⚡🇧⚡🇭⚡🇬 ⚡🇳⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇹⚡🇺 ⚡🇦⚡🇯⚡🇯",
"⚡🇭⚡🇾⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇰⚡🇪 ⚡🇧⚡🇨⚡🇭⚡🇪 ⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇲⚡🇦⚡🇹",
"⚡🇭⚡🇾⚡🇪 ⚡🇩⚡🇺⚡🇷 ⚡🇭⚡🇦⚡🇹⚡🇹 ⚡🇲⚡🇦⚡🇩⚡🇭⚡🇦⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇰⚡🇴⚡🇮 ⚡🇧⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾 ⚡🇪⚡🇸⚡🇱⚡🇮⚡🇾⚡🇪 ⚡🇲⚡🇦⚡🇫 ⚡🇨⚡🇷 ⚡🇷⚡🇭⚡🇦 ⚡🇭⚡🇺 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇰⚡🇴⚡🇮 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺 ⚡🇲⚡🇦⚡🇫⚡🇮 ⚡🇩⚡🇪 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺 ⚡🇲⚡🇦⚡🇫⚡🇮 ⚡🇲⚡🇮⚡🇱 ⚡🇯⚡🇦⚡🇾⚡🇪⚡🇬⚡🇮 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇲⚡🇦⚡🇹 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇦 ⚡🇲⚡🇺⚡🇯⚡🇪 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇨⚡🇷⚡🇰⚡🇪",
"⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇨⚡🇷⚡🇰⚡🇪",
"⚡🇫⚡🇷 ⚡🇧⚡🇴⚡🇱⚡🇳⚡🇦 ⚡🇳⚡🇦 ⚡🇰⚡🇮 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇨⚡🇷⚡🇰⚡🇪",
"⚡🇨⚡🇾⚡🇦 ⚡🇭⚡🇺⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷 ⚡🇰⚡🇪⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇭⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇾 ⚡🇳⚡🇾 ⚡🇲⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾",
"⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇸⚡🇪 ⚡🇺⚡🇹⚡🇷 ⚡🇲⚡🇨",
"⚡🇱⚡🇺⚡🇳 ⚡🇲⚡🇹 ⚡🇨⚡🇭⚡🇺⚡🇸 ⚡🇲⚡🇪⚡🇷⚡🇦",
"⚡🇳⚡🇮⚡🇰⚡🇦⚡🇱 ⚡🇲⚡🇦⚡🇩⚡🇦⚡🇷⚡🇨⚡🇭⚡🇩",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇴⚡🇾⚡🇪 ⚡🇬⚡🇦⚡🇸⚡🇭⚡🇹⚡🇮 ⚡🇰 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇲⚡🇦⚡🇰⚡🇮⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇮",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇮",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇰 ⚡🇭⚡🇦⚡🇹⚡🇭 ⚡🇹⚡🇴⚡🇩⚡🇭 ⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇪 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇰 ⚡🇲⚡🇺⚡🇭 ⚡🇲⚡🇪 ⚡🇫⚡🇦⚡🇸⚡🇦⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇹⚡🇺 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇵⚡🇦⚡🇸⚡🇦⚡🇳⚡🇩 ⚡🇳⚡🇦⚡🇮 ⚡🇦⚡🇾⚡🇦 ⚡🇲⚡🇪⚡🇰⚡🇴",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇮⚡🇩⚡🇪⚡🇷 ⚡🇸⚡🇪",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇸⚡🇪 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇳⚡🇾 ⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇧⚡🇦⚡🇹 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪",
"⚡🇫⚡🇦⚡🇸⚡🇹 ⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇹⚡🇺⚡🇹⚡🇴 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰",
"⚡🇴⚡🇾 ⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪 ⚡🇰⚡🇭⚡??⚡🇳⚡🇦 ⚡🇰⚡🇭⚡🇦 ⚡🇰⚡🇪 ⚡🇦⚡🇦 ⚡🇰⚡🇦⚡🇲⚡🇿⚡🇴⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇮⚡🇱⚡🇾 ⚡🇷⚡🇪⚡🇾 🌚😂",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇦⚡🇵 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺",
"⚡🇸⚡🇭⚡🇮 ⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡??⚡🇺 ⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵",
"⚡🇫⚡🇷 ⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵",
"⚡🇸⚡🇭⚡🇮 ⚡🇸⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡??⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇦 ⚡🇨⚡🇾⚡🇺 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵",
"⚡🇵⚡🇷⚡🇴⚡🇴⚡🇫 ⚡🇨⚡🇷 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷⚡🇴⚡🇴⚡🇫 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇵⚡🇷⚡🇴⚡🇴⚡🇫 ⚡🇭⚡🇴 ⚡🇨⚡🇭⚡🇺⚡🇰⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇮⚡🇱⚡🇱⚡🇦⚡🇷",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇲⚡🇦⚡🇦 ⚡🇰 ⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇴⚡🇾 ⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪 ⚡🇰⚡🇭⚡🇦⚡🇳⚡🇦 ⚡🇰⚡🇭⚡🇦 ⚡🇰⚡🇪 ⚡🇦⚡🇦 ⚡🇰⚡🇦⚡🇲⚡🇿⚡🇴⚡🇷",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇲⚡🇦⚡🇩⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩 ?",
"⚡🇦⚡🇧 ⚡🇹⚡🇰 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇭⚡🇴⚡🇬⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ?",
"⚡🇳⚡🇾 ⚡🇳⚡🇾 ⚡🇲⚡🇪 ⚡🇰⚡🇺⚡🇨⚡🇭 ⚡🇳⚡🇾 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇧⚡🇸 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇸⚡🇧⚡🇸⚡🇪 ⚡🇵⚡🇭⚡🇪⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴 ⚡🇧⚡🇴⚡🇱 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇳⚡🇦 ⚡🇰⚡🇦⚡🇲 ⚡🇰⚡🇷⚡🇪",
"⚡🇾⚡🇦⚡🇭⚡🇦 ⚡🇧⚡🇭⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇦 ⚡🇹⚡🇺 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇨⚡🇪 ⚡🇵⚡🇮⚡🇱⚡🇱⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇮⚡🇲⚡🇦⚡🇰⚡🇦⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇹⚡🇴 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇨⚡🇺⚡🇩⚡🇪⚡🇬⚡🇮",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇹⚡🇴⚡🇲⚡🇲⚡🇾",
"⚡🇳⚡🇮⚡🇰⚡🇦⚡🇱 ⚡🇲⚡🇦⚡🇩⚡🇦⚡🇷⚡🇨⚡🇭⚡🇩 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇾⚡🇭⚡🇦 ⚡🇸⚡🇪",
"⚡🇨⚡🇴⚡🇿 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇦⚡🇳⚡🇩⚡🇭⚡🇮 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇭⚡🇪",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇳⚡🇾⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇭⚡🇴⚡🇬⚡🇮 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇯⚡🇴 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦⚡🇹⚡🇮 ⚡🇯⚡🇴⚡🇬⚡🇮",
"⚡🇹⚡🇷⚡🇾 ⚡🇦⚡🇲⚡🇲⚡🇮 ⚡🇨⚡🇪 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇪 ⚡🇲⚡🇪 ⚡🇪⚡🇲⚡🇴⚡🇯⚡🇮 ⚡🇩⚡🇦⚡🇱 ⚡🇲⚡🇨",
"⚡🇨⚡🇾⚡🇦 ? ⚡🇨⚡🇭⚡🇲⚡🇷 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇦 ⚡🇨⚡🇾⚡🇦 ?",
"⚡🇹⚡🇲 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇷⚡🇮 ⚡🇭⚡🇴⚡🇬⚡🇮 ⚡🇫⚡🇷⚡🇷⚡🇹⚡🇴",
"⚡🇨⚡🇾⚡🇦 ? ⚡🇰⚡🇧 ? ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇰⚡🇪⚡🇰",
"⚡🇨⚡🇾⚡🇦 ⚡🇸⚡🇨⚡🇭 ⚡🇲⚡🇪⚡🇾 ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇼⚡?? ⚡🇱⚡🇮 ⚡🇹⚡🇺⚡🇳⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦",
"⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇸⚡🇨⚡🇭 ⚡🇳⚡🇾 ⚡🇧⚡🇴⚡🇱 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇨⚡🇭 ⚡🇲⚡🇪⚡🇾 ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇮⚡🇦 ⚡🇲⚡🇪⚡🇷⚡🇪 ⚡🇸⚡🇹⚡🇭",
"⚡🇲⚡🇹⚡🇱⚡🇧 ⚡🇹⚡🇲⚡🇷",
"⚡🇳⚡🇾⚡🇹⚡🇴",
"⚡🇵⚡🇺⚡🇷⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇲⚡🇨",
"⚡🇹⚡🇲⚡🇷 ⚡🇫⚡🇷⚡🇷⚡🇹⚡🇴",
"⚡🇴⚡🇭 ⚡🇴⚡🇰 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇫⚡🇮⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇦 ⚡🇩⚡🇦⚡🇲⚡🇦⚡🇩",
"⚡🇨⚡🇾⚡🇦 ? ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭⚡🇪 ⚡🇵⚡🇪⚡🇭⚡🇱⚡🇪 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇰⚡🇪⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇳⚡🇪 ⚡🇲⚡🇪 ⚡🇻⚡🇾⚡🇦⚡🇸⚡🇹 ⚡🇭⚡🇺",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇰⚡🇺⚡🇨⚡🇭 ⚡🇧⚡🇮",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇨⚡🇾⚡🇦 ? ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇦 ?",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇲⚡🇹 ⚡🇭⚡🇸⚡🇸",
"⚡🇾⚡🇺⚡🇷 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇲⚡🇴⚡🇲",
"⚡🇦⚡🇷⚡🇪 ⚡🇸⚡🇧⚡🇰⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇴⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇧⚡🇮",
"⚡🇦⚡🇷⚡🇪 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇪⚡🇰 ⚡🇧⚡🇦⚡🇦⚡🇷",
"⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇮 ⚡🇹⚡🇷⚡🇭",
"⚡🇪⚡🇰 ⚡🇱⚡🇮⚡🇳⚡🇪 ⚡🇲⚡🇪 ⚡🇹⚡🇲⚡🇷",
"⚡🇶",
"⚡🇴⚡🇨⚡🇾 ⚡🇦⚡🇧 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇱⚡🇪",
"⚡🇵⚡🇪⚡🇭⚡🇪⚡🇱⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇳⚡🇾⚡🇹⚡🇴",
"⚡?? ?",
"⚡🇭⚡🇾⚡🇾⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇦 ⚡🇪⚡🇰 ⚡🇧⚡🇦⚡🇦⚡🇷",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇸⚡🇺⚡🇳 ⚡🇩⚡🇴⚡🇸⚡🇹 ⚡🇹⚡🇲⚡🇷",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇯⚡🇦 ⚡🇷⚡🇦⚡🇦⚡🇳⚡🇩 ⚡🇲⚡🇦⚡🇦⚡🇫 ⚡🇨⚡🇷⚡🇷 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦",
"⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇲⚡🇷 ⚡🇫⚡🇷⚡🇷⚡🇹⚡🇴",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇱⚡🇪 ⚡🇨⚡🇭⚡🇲⚡🇷",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇦⚡🇪⚡🇸⚡🇪 ⚡🇭⚡🇮 ⚡🇨⚡🇺⚡🇩",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇭⚡🇾⚡🇾 ⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇭⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇱⚡🇪⚡🇳⚡🇦",
"⚡🇴⚡🇷 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇱⚡🇪",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇦 ⚡🇴⚡🇷",
"⚡🇭⚡🇾⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇴 ⚡🇳⚡🇦",
"⚡🇨⚡🇭⚡🇺⚡🇩⚡🇴 ⚡🇲⚡🇹 ⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇯⚡🇦⚡🇴",
"⚡🇧⚡🇾⚡🇾⚡🇪⚡🇪 ⚡🇭⚡🇾⚡🇾 ⚡🇨⚡🇾⚡🇦 ?",
"⚡🇶⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇶 ⚡🇷⚡🇭⚡🇪 ⚡🇭⚡🇴 ?",
"⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇲⚡🇨",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇲⚡🇹",
"⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇬⚡🇱 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇦⚡🇲⚡🇲⚡🇮 ⚡🇨⚡🇪 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇪 ⚡🇲⚡🇪 ⚡🇨⚡🇭⚡🇦⚡🇵⚡🇵⚡🇦⚡🇱",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦 ⚡🇲⚡🇨",
"⚡🇰⚡🇲⚡🇿⚡🇷⚡🇴⚡🇷 ⚡🇪⚡🇾 ⚡🇨⚡??⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇪⚡🇰",
"⚡🇨⚡🇾⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇭⚡🇦 ?",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇹⚡🇭⚡🇦 ⚡🇨⚡🇾⚡🇦 ?",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇸⚡🇱⚡🇮⚡🇩⚡🇪 ⚡🇱⚡🇪⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇨⚡🇷⚡🇲⚡🇨",
"⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇨⚡🇵 ⚡🇲⚡🇹 ⚡🇨⚡🇷⚡🇷 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇱⚡🇪",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇭⚡🇾⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇦",
"⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇸⚡🇨⚡🇭⚡🇴⚡🇫⚡🇺 ⚡🇰⚡🇭⚡🇦⚡🇨⚡🇭⚡🇦⚡🇷 ⚡🇰⚡🇭⚡🇦⚡🇨⚡🇭⚡🇦⚡🇷",
"⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦 ⚡🇯⚡🇦 ⚡🇲⚡🇨",
"⚡🇭⚡🇾⚡🇾 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇱⚡🇪",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇰⚡🇲⚡🇿⚡🇴⚡🇷 ⚡🇲⚡🇨 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦",
"⚡🇾⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇲⚡🇷",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇳⚡🇾 ⚡🇨⚡🇵 ⚡🇳⚡🇾 ⚡🇨⚡🇷⚡🇷",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇲⚡🇹 ⚡🇨⚡🇷⚡🇷",
"⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇦⚡🇷⚡🇦⚡🇲 ⚡🇸⚡🇪 ⚡🇲⚡🇨",
"⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇪⚡🇰",
"⚡🇨⚡🇵 ⚡🇨⚡🇷⚡🇨⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇪⚡🇬⚡🇦 !",
"⚡🇧⚡🇦⚡🇦⚡🇵 ? ⚡🇲⚡🇨 ⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇨⚡🇴⚡🇮 ⚡🇲⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇳⚡🇾 ⚡🇪⚡🇾 ⚡🇲⚡🇦⚡🇮 ⚡🇺⚡🇵⚡🇦⚡🇷 ⚡🇸⚡🇪 ⚡🇷⚡🇴⚡🇨⚡🇰⚡🇪⚡🇹 ⚡🇵⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇭 ⚡🇨⚡🇪 ⚡🇧⚡🇸⚡🇸 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇳⚡🇪 ⚡🇦⚡🇾⚡🇦 ⚡🇭⚡🇺",
"⚡🇨⚡🇭⚡🇴⚡🇹⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇰 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇨⚡🇭⚡🇴⚡🇹⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇧⚡🇦⚡🇰⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇪⚡🇬⚡🇦",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇲⚡🇦⚡🇮⚡🇳 ⚡🇧⚡🇺⚡🇷⚡🇫",
"⚡🇧⚡🇭⚡🇮⚡🇰⚡🇦⚡🇷⚡🇮 ⚡🇰⚡🇮 ⚡🇯⚡🇭⚡🇦⚡🇹 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇦 ⚡🇱⚡🇪",
"⚡🇨⚡🇭⚡🇴⚡🇩⚡🇰⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇲⚡🇦⚡🇷⚡🇯⚡🇦⚡🇾⚡🇪⚡🇬⚡🇮",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇲⚡🇦⚡🇮⚡🇳 ⚡🇲⚡🇴⚡🇺⚡🇳⚡🇹 ⚡🇪⚡🇻⚡🇪⚡🇷⚡🇪⚡🇸⚡🇹",
"⚡🇲⚡🇺⚡🇭 ⚡🇲⚡🇪⚡🇾 ⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇲⚡🇪⚡🇷⚡🇦",
"⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪 ⚡🇰⚡🇮 ⚡🇯⚡🇭⚡🇦⚡🇹 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇳⚡🇾 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇰⚡🇮 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇸⚡🇧 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇹⚡🇦",
"⚡🇹⚡🇪⚡🇳⚡🇺 ⚡🇴⚡🇷 ⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇹⚡🇦 ⚡🇪⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇧⚡🇸 ⚡🇧⚡🇸 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇧⚡🇸 ⚡🇧⚡🇸 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇹⚡🇭⚡🇳⚡🇰⚡🇸⚡🇸",
"⚡🇧⚡🇸 ⚡??⚡🇸 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇮⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇦",
"⚡🇧⚡🇸 ⚡🇧⚡🇸 ⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇬⚡🇾⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇧",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇸⚡🇦⚡🇧⚡🇮⚡🇹 ⚡🇰⚡🇷 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇾⚡🇦 ⚡🇭⚡🇺⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇪⚡🇦⚡🇸⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺",
"⚡🇪⚡🇦⚡🇸⚡🇾 ⚡🇼8 ⚡🇲⚡?? ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇦⚡🇧",
"⚡🇸⚡🇦⚡🇳⚡🇸 ⚡🇦⚡🇷⚡🇮 ⚡🇭⚡🇦 ⚡🇰⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇬⚡🇮 ⚡🇦⚡🇯⚡🇯",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴 ⚡🇧⚡🇮⚡🇳⚡🇦 ⚡🇸⚡🇦⚡🇳⚡🇸⚡🇸 ⚡🇱⚡🇪⚡🇹⚡🇪 ⚡🇭⚡🇺⚡🇪 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇰⚡🇪 ⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷",
"⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇳⚡🇴⚡🇷⚡🇲⚡🇮⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇫⚡🇷 ⚡🇨⚡🇾⚡🇦 ⚡🇳⚡🇴⚡🇷⚡🇲⚡🇮⚡🇪 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇧⚡🇦⚡🇸 ⚡🇹⚡🇭⚡🇪⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾",
"⚡🇧⚡🇦⚡🇸 ⚡🇹⚡🇭⚡🇪⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮",
"⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇹⚡🇭⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇪⚡🇸⚡🇱⚡🇮⚡🇾⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇲⚡🇦⚡🇮 ⚡🇸⚡🇧 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇭⚡🇱 ⚡🇨⚡🇭⚡🇱 ⚡🇭⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮",
"⚡🇫⚡🇷 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇧⚡🇦⚡🇸 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇫⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇲⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇪⚡🇾",
"⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇲⚡🇦 ⚡🇰⚡🇦 ⚡🇧⚡🇨⚡🇭⚡🇦 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇧⚡🇭⚡🇴⚡🇹 ⚡🇬⚡🇳⚡🇩⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇬⚡🇳⚡🇩⚡🇦",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇧⚡🇹⚡🇦 ⚡🇷⚡🇭⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇫⚡🇮⚡🇷 ⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇳⚡🇾 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇹⚡🇦 ⚡🇳⚡🇾 ⚡🇰⚡🇴⚡🇳 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴",
"⚡🇷⚡🇺⚡🇰 ⚡🇦⚡🇦⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇰⚡🇪",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇨⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇴⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇭⚡🇺",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇨⚡🇷 ⚡🇷⚡🇦⚡🇧⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇰⚡🇷 ⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇰⚡🇪",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇱⚡🇪 ⚡🇹⚡🇭⚡🇴⚡🇩⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇳⚡🇪 ⚡🇩⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇷⚡🇺⚡🇰 ⚡🇯⚡🇦 ⚡🇦⚡🇦⚡🇳⚡🇩 ⚡🇷⚡🇰⚡🇭 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇮⚡🇾⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇫⚡🇦⚡🇲⚡🇴⚡🇺⚡🇸 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇲⚡🇦⚡🇦⚡🇳 ⚡🇱⚡🇮⚡🇦 ⚡🇲⚡🇪⚡🇳⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇸⚡🇦⚡🇱⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇦⚡🇦⚡🇳 ⚡🇱⚡🇮⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇭⚡🇦⚡🇳⚡🇹 ⚡🇧⚡🇪⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇸⚡🇭⚡🇦⚡🇳⚡🇹 ⚡🇧⚡🇪⚡🇹⚡🇭⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇹⚡🇺",
"⚡🇫⚡🇷 ⚡🇸⚡🇪 ⚡🇸⚡🇭⚡🇦⚡🇳⚡🇹 ⚡🇧⚡🇪⚡🇹⚡🇭 ⚡🇹⚡🇺 ⚡🇨⚡🇺⚡🇩 ⚡🇦⚡🇧 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇾⚡🇭⚡🇦",
"⚡🇲⚡🇪⚡🇷⚡🇪 ⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇳⚡🇾 ⚡🇦⚡🇾⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇱⚡🇪 ⚡🇰⚡🇪⚡🇱⚡🇦 ⚡🇰⚡🇭⚡🇦 ⚡🇹⚡🇺 ⚡🇲⚡🇦⚡🇩⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩",
"⚡🇭⚡🇾⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇨⚡🇾⚡🇦",
"⚡🇭⚡🇾⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇲⚡🇦⚡🇷 ⚡🇬⚡🇦⚡🇮 ⚡🇨⚡🇾⚡🇦",
"⚡🇭⚡🇾⚡🇪 ⚡🇸⚡🇨⚡🇭 ⚡🇧⚡🇹⚡🇦 ⚡🇨⚡🇴⚡🇲 ⚡🇨⚡??⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇨⚡🇭⚡🇱 ⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴 ⚡🇸⚡🇲⚡🇯⚡🇭⚡🇱⚡🇪",
"⚡🇧⚡🇦⚡🇰⚡🇮 ⚡🇰⚡🇴⚡🇮 ⚡🇩⚡🇮⚡🇰⚡🇰⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇧⚡🇦⚡🇰⚡🇮 ⚡🇸⚡🇧 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇪 ⚡🇪⚡🇾 ⚡🇰⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇩⚡🇰⚡🇦⚡🇩 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇭⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇳⚡🇪 ⚡🇼⚡🇱⚡🇮 ⚡🇪⚡🇾",
"⚡🇵⚡🇷 ⚡🇲⚡🇪⚡🇮 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇯⚡🇳⚡🇹⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇰⚡🇴 ⚡🇰⚡🇴⚡🇮 ⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦",
"⚡🇵⚡🇷 ⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇻⚡🇮 ⚡🇲⚡🇦⚡🇳⚡🇳⚡🇦 ⚡🇸⚡🇭⚡🇮 ⚡🇹⚡🇭⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷 ⚡🇼⚡🇴 ⚡🇬⚡🇱⚡🇹 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇵⚡🇷 ⚡🇼⚡🇴 ⚡🇸⚡🇭⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇩⚡🇰⚡🇦⚡🇩 ⚡🇪⚡🇾",
"⚡🇵⚡🇷 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇰⚡🇮⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇴⚡🇲⚡🇫⚡🇴⚡🇴",
"⚡🇧⚡🇺⚡🇷 ⚡🇨⚡🇭⚡🇪⚡🇪⚡🇷 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇰⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇱 ⚡🇲⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇦 ⚡🇲⚡🇦⚡🇷⚡🇰⚡🇪 ⚡🇺⚡🇸⚡🇰⚡🇮 ⚡🇩⚡🇭⚡🇦⚡🇩⚡🇰⚡🇦⚡🇳 ⚡🇷⚡🇴⚡🇰 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇱⚡🇺⚡🇱⚡🇱⚡🇪 ⚡🇰⚡🇭⚡🇦 ⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇦⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇦",
"⚡🇹⚡🇷⚡🇮 ⚡🇧⚡🇭⚡🇳 ⚡🇰⚡🇮 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇮 ⚡🇧⚡🇪⚡🇹⚡🇦",
"⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇰⚡🇭⚡🇹⚡🇲",
"⚡🇸⚡🇺⚡🇳 ⚡🇪⚡🇰 ⚡🇲⚡🇦⚡🇿⚡🇪 ⚡🇰⚡🇮 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇧⚡🇦⚡🇹⚡🇦⚡🇴 ⚡🇰⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇭⚡🇦⚡🇮",
"⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇦⚡🇯 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇴⚡🇾⚡🇪",
"⚡🇸⚡🇺⚡🇳 ⚡🇸⚡🇺⚡🇳 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇹⚡🇺",
"⚡🇰⚡🇮⚡🇱⚡🇦⚡🇸 ⚡🇳⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇵⚡?? ⚡🇵⚡🇷 ⚡🇨⚡🇾⚡🇦 ⚡🇭⚡🇴⚡🇹⚡🇪 ⚡🇪⚡🇾 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇹⚡🇲⚡🇨⚡🇱 ⚡🇸⚡🇺⚡🇳⚡🇱⚡🇪",
"⚡🇲⚡🇴⚡🇴⚡🇹 ⚡🇩⚡🇺 ⚡🇹⚡🇪⚡🇷⚡?? ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇲⚡🇪⚡🇾",
"⚡🇧⚡🇭⚡🇬⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇫⚡🇷",
"⚡🇫⚡🇷 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇾⚡🇪 ⚡🇻⚡🇮 ⚡🇸⚡🇭⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇰⚡🇸 ⚡🇧⚡🇸",
"⚡🇦⚡🇯 ⚡🇰⚡🇺⚡🇨⚡🇭 ⚡🇳⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇹⚡🇷⚡🇾 ⚡🇰⚡🇷 ⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇨⚡🇭⚡🇺⚡🇸⚡🇰⚡🇪",
"⚡🇹⚡🇴⚡🇷⚡🇲⚡🇦⚡🇰⚡🇮⚡🇧⚡🇺⚡🇷 ⚡🇸⚡🇺⚡🇳",
"⚡🇹⚡🇴⚡🇷 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇫⚡🇺⚡🇩⚡🇩⚡🇮 ⚡🇴⚡🇾⚡🇪",
"⚡🇭⚡🇦⚡🇾⚡🇪 ⚡🇭⚡🇦⚡🇾⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇴⚡🇾⚡🇪 ⚡🇱⚡🇺⚡🇳⚡🇩⚡🇰⚡🇪 ⚡🇵⚡🇦⚡🇸⚡🇮⚡🇳⚡🇪..",
"⚡🇰⚡🇺⚡🇹⚡🇹⚡🇪 ⚡🇰⚡🇪 ⚡🇹⚡🇦⚡🇹⚡🇹⚡🇪 ⚡🇸⚡🇺⚡🇳",
"⚡🇰⚡🇺⚡🇹⚡🇹⚡🇦 ⚡🇯⚡🇦⚡🇮⚡🇸⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺",
"⚡🇲⚡🇺⚡🇭 ⚡🇲⚡🇪⚡🇮 ⚡🇱⚡🇪 ⚡🇲⚡🇪⚡🇷⚡🇦..",
"⚡🇯⚡🇭⚡🇦⚡🇹 ⚡🇰⚡🇪 ⚡🇵⚡🇮⚡🇸⚡🇸⚡🇺 ⚡🇸⚡🇺⚡🇳 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇭⚡🇦⚡🇭⚡🇦⚡🇭⚡🇭⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇹⚡🇦⚡🇹⚡🇹⚡🇪 ⚡🇺⚡🇹⚡🇭",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇮 ⚡🇩⚡🇪⚡🇰⚡🇭",
"⚡🇼⚡🇪⚡🇪⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇦⚡🇧",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇳⚡🇾 ⚡🇷⚡🇴⚡🇰 ⚡🇹⚡🇺 ⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇪⚡🇾",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇭⚡🇮⚡🇿⚡🇩⚡🇪",
"⚡🇴⚡🇰⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇲⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇱⚡🇺⚡🇳 ⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇬⚡🇦⚡🇳⚡🇩 ⚡🇲⚡🇪⚡🇮 ?",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇮 ⚡🇨⚡🇴⚡🇩⚡🇺..",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇦⚡🇯 ⚡🇫⚡🇦⚡🇩 ⚡🇩⚡🇺",
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇱⚡🇪⚡🇰⚡🇷 ⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇪 ⚡🇦⚡🇳⚡🇩⚡🇷 ⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇵⚡🇷⚡🇴⚡🇸⚡🇳",
"⚡🇺⚡🇬⚡🇱⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇵",
"⚡🇲⚡🇦⚡🇰⚡🇦⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇹⚡🇪⚡🇷⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇰⚡🇴 ⚡🇹⚡🇦⚡🇬 ⚡🇰⚡🇷..?",
"⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇹⚡🇦⚡🇬 ⚡🇰⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇭⚡🇦⚡🇬⚡🇼⚡🇳 ⚡🇰⚡🇴..",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇳⚡🇾 ⚡🇭⚡🇴 ⚡🇹⚡🇺",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇭⚡🇴 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺 ⚡🇰⚡🇮⚡🇩",
"⚡🇲⚡🇦 ⚡🇹⚡🇴 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇭⚡🇦⚡🇼⚡🇦⚡🇧⚡🇿⚡🇮 ⚡🇨⚡🇷..",
"⚡🇧⚡🇸 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇳⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇹⚡🇴⚡🇼⚡🇳 ⚡🇲⚡🇪⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇱⚡🇪⚡🇰⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇸⚡🇪⚡🇽⚡🇾 ⚡🇰⚡🇴 ⚡🇧⚡🇪⚡🇯 - ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇭⚡🇬⚡🇼⚡🇳 ⚡🇵⚡🇪",
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇵⚡🇰⚡🇩 ⚡🇨⚡🇵 ⚡🇳⚡🇾 ⚡🇰⚡🇷",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇪⚡🇳⚡🇩⚡🇾",
"⚡🇧⚡🇭⚡🇰⚡🇰 ⚡🇨⚡🇺⚡🇩",
"⚡🇹⚡🇪⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮",
"⚡🇨⚡🇺⚡🇩 ⚡🇯⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇮⚡🇩⚡🇮 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇸⚡🇱⚡🇴⚡🇼",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇮⚡🇾⚡🇦 ⚡🇨⚡🇮⚡🇴⚡🇩⚡🇺",
"⚡🇧⚡🇭⚡🇦⚡🇬?",
"⚡🇧⚡🇭⚡🇦⚡🇰 ⚡🇨⚡🇺⚡🇩",
"⚡🇹⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇸⚡🇱⚡🇴⚡🇼",
"⚡🇸⚡🇱⚡🇴⚡🇼 ⚡🇫⚡🇮⚡🇷⚡🇸⚡🇪",
"⚡🇨⚡🇺⚡🇩⚡🇬⚡🇷⚡🇮⚡🇧",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇩⚡🇴⚡🇺",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇳⚡🇪⚡🇹 ⚡🇴⚡🇳 ⚡🇴⚡🇫⚡🇫 ⚡🇼⚡🇦⚡🇱⚡🇮 ⚡🇷⚡🇳⚡🇩⚡🇾",
"⚡🇴⚡🇾⚡🇪 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇮⚡🇩⚡🇭⚡🇦⚡🇷 ⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇦⚡🇦⚡🇵",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇷⚡🇩⚡🇺",
"⚡🇴⚡🇮 ⚡🇲⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇪⚡🇪",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇪⚡🇯",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇸⚡🇺⚡🇦⚡🇷 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇪⚡🇯",
"⚡🇳⚡🇪⚡🇹 ⚡🇴⚡🇫⚡🇫 ⚡🇴⚡🇳 ⚡🇰⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇰⚡🇪",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇮 ⚡🇰⚡🇪⚡🇸⚡🇪",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇸⚡🇱⚡🇴⚡🇼 ⚡🇲⚡🇦⚡🇩⚡🇭⚡🇦⚡🇷⚡🇨⚡🇴⚡🇩",
"⚡🇹⚡??⚡🇰⚡🇨 ⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇰⚡🇷 ⚡🇲⚡🇸⚡🇬 ⚡🇩⚡🇪⚡🇱⚡🇪⚡🇹⚡🇪",
"⚡🇴⚡🇮 ⚡🇸⚡🇺⚡🇦⚡🇷 ⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇰⚡🇪",
"⚡🇹⚡??⚡🇰⚡🇨 ⚡🇫⚡🇺⚡🇫⚡🇮",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇮⚡🇩⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇮",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇨⚡🇺⚡🇩 ⚡🇦⚡🇧",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩",
"⚡🇧⚡🇭⚡🇦⚡🇰 ⚡🇨⚡🇺⚡🇩",
"⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇷⚡🇺",
"⚡🇹⚡🇲⚡🇰⚡🇱 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇬⚡🇷⚡🇮⚡🇧",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳 ⚡🇻⚡🇪⚡🇸⚡🇮⚡🇾⚡🇦⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇬⚡🇳⚡🇩⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇦 ⚡🇹⚡🇺 ⚡🇫⚡🇮⚡🇷⚡🇸⚡🇪 ⚡🇳⚡🇪⚡🇹 ⚡🇴⚡🇳 ⚡🇴⚡🇫⚡🇫",
"⚡🇬⚡🇷⚡🇮⚡🇧 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇯⚡🇦 ⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇲⚡🇦⚡🇷⚡🇺 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇷⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦⚡🇦",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇹⚡🇧⚡🇰⚡🇨",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇪⚡🇾 ⚡🇨⚡🇵",
"⚡🇨⚡🇵 ⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇪⚡🇭⚡🇭",
"⚡🇨⚡🇵 ⚡🇹⚡🇲⚡🇰⚡🇱 ⚡🇲⚡🇪⚡🇭",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇦⚡🇧⚡🇪 ⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇩⚡🇴⚡🇺⚡🇧⚡🇱⚡🇪 ⚡🇸⚡🇪⚡🇳⚡🇩 ⚡🇰⚡🇴 ⚡🇨⚡🇵 ⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇪 ⚡🇨⚡🇵 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇦⚡🇦⚡🇯 ⚡🇲⚡🇪⚡🇭⚡🇭",
"⚡🇭⚡🇹 ⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇩⚡🇦⚡🇱⚡🇦⚡🇱 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪.",
"⚡🇷⚡🇳⚡🇩⚡🇾 ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇨⚡🇺⚡🇩⚡🇶 ⚡🇹⚡🇷⚡🇾⚡🇲⚡🇦",
"⚡🇵⚡🇦⚡🇷⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭⚡🇪⚡🇬⚡🇦..",
"⚡🇹⚡🇷⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇭⚡🇧⚡🇭⚡🇦⚡🇰",
"⚡🇱⚡🇦⚡🇬⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇨⚡🇪 ⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇱⚡🇦⚡🇬⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪..",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱",
"⚡🇧⚡🇭⚡🇮⚡🇰⚡🇦⚡🇷⚡🇮 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇨⚡🇭⚡🇺⚡🇸 ⚡🇲⚡🇪⚡🇷⚡??.",
"⚡🇱⚡🇴⚡🇼 ⚡🇱⚡🇪⚡🇻⚡🇪⚡🇱 ⚡🇨⚡🇵 ⚡🇨⚡🇷",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇱⚡🇴⚡🇼 ⚡🇱⚡🇪⚡🇻⚡🇪⚡🇱 ⚡🇼⚡🇪⚡🇦⚡🇰",
"⚡🇲⚡🇪⚡🇷⚡🇪 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇵⚡🇪 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪",
"⚡🇫⚡🇷⚡🇪⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇫⚡🇷⚡🇪⚡🇪 ⚡🇲⚡🇪⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪"
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇳⚡🇾 ⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇹⚡🇦⚡🇹⚡🇹⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇲⚡🇪",
"⚡??⚡🇮⚡🇹⚡🇳⚡🇮 ⚡🇧⚡🇷 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦⚡🇾⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇱⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇦⚡🇵⚡🇰⚡🇦",
"⚡🇱⚡🇺⚡🇳 ⚡🇨⚡🇺⚡🇸 ⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇸⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇦⚡🇵⚡🇰⚡🇦",
"⚡🇰⚡🇴⚡🇮 ⚡🇳⚡🇾 ⚡🇩⚡🇪⚡🇰⚡🇭 ⚡🇷⚡🇭⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇮⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪",
"⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇸 ⚡🇾⚡🇪⚡🇭⚡🇮 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇲⚡🇪⚡🇾",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇴 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇯⚡🇦⚡🇾⚡🇪⚡🇬⚡🇮",
"⚡🇸⚡🇱⚡🇴⚡🇼 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇰⚡🇮⚡🇩",
"⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭..",
"⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭..",
"⚡🇹⚡🇾⚡🇲 ⚡🇸⚡🇪 ⚡🇵⚡🇭⚡🇱⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇹⚡🇾⚡🇲 ⚡🇭⚡🇴⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦",
"⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇹⚡🇾⚡🇲 ⚡🇸⚡🇪 ⚡🇵⚡🇭⚡🇱⚡🇪",
"⚡🇺⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪 ⚡🇰⚡🇪 ⚡🇱⚡🇩⚡🇰⚡🇪",
"⚡🇲⚡🇦⚡🇨⚡🇦⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇴⚡🇳 ⚡🇰⚡🇧 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇰⚡🇴⚡🇮 ⚡🇭⚡🇴⚡🇬⚡🇦 ⚡🇹⚡🇲⚡🇱",
"⚡🇲⚡🇦⚡🇨⚡🇭⚡🇦⚡🇷 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇨⚡🇴⚡🇩⚡🇳⚡🇦 ⚡🇸⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇧⚡🇴⚡🇱 ⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇪",
"⚡🇧⚡🇸 ⚡🇲⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇳⚡🇦 ⚡🇨⚡🇭⚡🇹⚡🇦 ⚡🇭⚡🇺",
"⚡🇪⚡🇼⚡🇼 ⚡🇲⚡🇦⚡🇰⚡🇦 ⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇺⚡🇹⚡🇭",
"⚡🇲⚡🇪⚡🇴⚡🇼 ⚡🇨⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇷⚡🇰⚡🇭 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇫⚡🇺⚡🇩⚡🇪 ⚡🇵⚡🇪",
"⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇱 ⚡🇺⚡🇹⚡🇭",
"⚡🇰⚡🇮⚡🇩⚡🇪⚡🇪 ⚡🇿⚡🇮⚡🇳⚡🇩⚡🇦 ⚡🇭⚡🇴",
"⚡🇲⚡🇦⚡🇷 ⚡🇳⚡🇾 ⚡🇰⚡🇮⚡🇩⚡🇩⚡🇪 ⚡🇹⚡🇾⚡🇵⚡🇪 ⚡🇰⚡🇷",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇧⚡🇰⚡🇱",
"⚡🇧⚡🇨 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹",
"⚡🇲⚡🇨 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇫⚡🇦⚡🇸⚡🇹",
"⚡🇫⚡🇦⚡🇸⚡🇹 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇫⚡🇦⚡🇸⚡🇹 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇰⚡🇦⚡🇲⚡🇿⚡🇴⚡🇷"
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇨⚡🇱⚡🇦⚡🇮⚡🇲 ⚡🇨⚡🇷⚡🇼⚡🇦",
"⚡🇦⚡🇼⚡🇿 ⚡🇳⚡🇮⚡🇨⚡🇭⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪 ⚡🇰⚡🇪 ⚡🇧⚡🇨⚡🇭⚡🇪",
"⚡🇸⚡🇦⚡🇼⚡🇦⚡🇱 ⚡🇳⚡🇾 ⚡🇵⚡🇺⚡🇨⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇦⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦",
"⚡🇫⚡🇾⚡🇹⚡🇪⚡🇷 ⚡🇧⚡🇳⚡🇪⚡🇬⚡🇦 ⚡🇱⚡🇦⚡🇬⚡🇩⚡🇪 ⚡🇲⚡🇦⚡🇩⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩",
"⚡🇴⚡🇾⚡🇪 ⚡🇰⚡🇦⚡🇦⚡🇱⚡🇪 ⚡🇷⚡🇴 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇴⚡🇾⚡🇪 ⚡🇰⚡🇦⚡🇦⚡🇱⚡🇪 ⚡🇷⚡🇴⚡🇴 ⚡🇳⚡🇾",
"⚡🇸⚡🇭⚡🇴⚡🇷⚡🇹 ⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺 ⚡🇧⚡🇮⚡🇳⚡🇦 ⚡🇷⚡🇺⚡🇰⚡🇪",
"⚡🇸⚡🇭⚡🇴⚡🇷⚡🇹 ⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇱⚡🇪⚡🇰⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇸⚡🇹⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇻⚡🇮 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇸⚡🇹⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇮⚡🇩⚡🇮 ⚡🇻⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇨⚡🇭⚡🇦⚡🇹 ⚡🇫⚡🇾⚡🇹⚡🇪⚡🇷 ⚡🇧⚡🇳⚡🇪⚡🇬⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪 ⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇧⚡🇴⚡🇱 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇩⚡🇦⚡🇩⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇧⚡🇺⚡🇱⚡🇱⚡🇾🇽 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇺⚡🇹⚡🇭",
"⚡🇲⚡🇦⚡🇷 ⚡🇲⚡🇦⚡🇷⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺",
"⚡🇴⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇲⚡🇦⚡🇷⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮"
"⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇯",
"⚡🇴⚡🇷 ⚡🇧⚡🇩⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇲⚡🇨",
"⚡🇴⚡🇷 ⚡🇧⚡🇩⚡🇦 2 ⚡🇱⚡🇮⚡🇳⚡🇪 ⚡🇼⚡🇱⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇴⚡🇷 ⚡🇧⚡??⚡🇦 ⚡🇴⚡🇾⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇲⚡🇱",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇦 ⚡🇧⚡🇺⚡🇷",
"⚡🇴⚡🇾⚡🇪 ⚡🇰⚡🇪⚡🇪⚡🇩⚡🇪",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇰⚡🇪",
"⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇲⚡🇰⚡🇱 ⚡🇺⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇨⚡🇨⚡🇭⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇳⚡🇦⚡🇳⚡🇮 ⚡🇲⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦⚡🇱",
"⚡🇹⚡🇪⚡🇯 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪",
"⚡🇴⚡🇾⚡🇪 ⚡🇲⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇲⚡🇷⚡🇪⚡🇳⚡🇬⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇾",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇮⚡🇾⚡🇦 ⚡🇰⚡🇮 ⚡🇬⚡🇦⚡🇳⚡🇩",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇦⚡🇩⚡🇮 ⚡🇰⚡🇦 ⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦",
"⚡🇲⚡🇰⚡🇱 ⚡🇺⚡🇹⚡🇭 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳⚡🇨⚡🇴⚡🇩",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇮 ⚡🇧⚡🇺⚡🇷 ⚡🇩⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇦 ⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦 ⚡🇲⚡🇪 ⚡🇱⚡🇦⚡🇺⚡🇩⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇻⚡🇦",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪 ⚡🇲⚡🇦⚡🇷 ⚡🇬⚡🇦⚡🇾⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇲⚡🇷⚡🇺",
"⚡🇯⚡🇦⚡🇱⚡🇮⚡🇩 ⚡🇰⚡🇷 ⚡🇸⚡🇵⚡🇦⚡🇲",
"⚡🇲⚡🇨 ⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇷⚡🇴⚡🇰⚡🇪⚡🇳⚡🇬⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷",
"⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷.⚡🇲⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇪",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇪 ⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺",
"⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷 ⚡🇰⚡🇮⚡🇩",
"⚡🇳⚡🇴⚡🇴⚡🇧 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪 ⚡🇲⚡🇦⚡🇷 ⚡🇲⚡🇦⚡🇹 ⚡🇹⚡🇺",
"⚡🇳⚡🇴⚡🇴⚡🇧 ⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩",
"⚡🇨⚡🇺⚡?? ⚡🇬⚡🇦⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇺⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇨⚡🇭⚡🇱 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇹⚡🇾⚡🇵 ⚡🇨⚡🇷 ⚡🇳⚡🇴⚡🇴⚡🇧 ⚡🇭⚡🇦⚡🇱⚡🇰⚡🇪",
"⚡🇨⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇳⚡🇾 ⚡🇭⚡🇴 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇨⚡🇺⚡🇩 ⚡🇨⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩 ⚡🇧⚡🇳⚡🇯⚡🇦 ⚡🇹⚡🇺 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇲⚡🇦⚡🇰⚡🇮⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇬⚡🇦⚡🇳⚡🇩⚡🇦 ⚡🇨⚡🇾⚡🇺 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺 ?",    "⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇬⚡🇳⚡🇩⚡🇦 ⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩",
"⚡🇲⚡🇦⚡🇦⚡🇳 ⚡🇱⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇸⚡🇺⚡🇳 ⚡🇧⚡🇦⚡🇹 ⚡🇦⚡🇧",
"⚡🇲⚡🇦⚡🇰⚡🇦⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦 ⚡🇫⚡🇦⚡🇹 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇷⚡🇺⚡🇰",
]

bar_texts = [
"★🆂★🅷★🅰★🅽★🆃 ★🅱★🅴★🆃★🅷 ★🅼★🅰★🅳★🆁★🅲★🅷★🅾★🅳 ★🆆★🆁★🅽★🅰 ★🅼★🅰★🅺★🅰★🅱★🅾★🆂★🅳★🅰 ★🆃★🅴★🅴★🆈.",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃..",
"★🅻★🆆★🅳★🅴 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅻★🅻★🅻 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅲★🆄★🅳★🅺★🅴 ★🅿★🅶★🅻 ★🅳★🅴★🅺★🅷.",
"★🅼★🅰★🅲★🅷★🅰★🆁 ★🅺★🅸 ★🅹★🅷★🅰★🅰★🆃 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅻★🅻★🅻★🅻 ★🅲★🆄★🅳 ★🅰★🅲★🅷★🅴 ★🆂★🅴 ★🆈★🅷★🅰★🅿★🅴 ★🆃★🅤",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼 ★🅳★🆄 ★🆃★🅰★🅿★🅰 ★🆃★🅰★🅿?",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅱★🅷★🅽 ★🅰★🅱★🅰★🅱★🅴 ★🅱★🅳★🅸 ★🆁★🅰★🅽★🅳★🅸.",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅾★🅰★🅰★🅴 ★🅱★🅰★🅳★🅸 ★🆁★🅰★🅽★🅳★🅳★🅳★🅳★🅳",
"★🆃★🅴★🆁★🅰 ★🅱★🅰★🅰★🅿 ★🆁★🅰★🅽★🅳★🅸★🅱★🅰★🅰★🅾 ★🅴★🅈 ★🅳★🅴★🅺★🅷",
"★🅺★🅸★🆃★🅽★🅸 ★🅲★🅷★🅾★🅳★🆄 ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅰★🅱 ★🅾★🆁..",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅲★🅷★🅾★🅳 ★🅳★🅸 ★🅷★🅼 ★🅽★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅴 ★🅱★🅴★🅴★🅻★🅰 ★🅱★🅽★🅴★🅶★🅰 ★🆁★🅾★🅰★🅳 ★🅿★🅴★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅴★🅺 ★🅳★🅰★🅼 ★🆃★🅾★🅿 ★🅱★🅴★🆇★🆈",
"★🅼★🅰★🅻★🆄★🅼 ★🅽★🅰 ★🅿★🅷★🆁 ★🅺★🅴★🅰★🅴 ★🅻★🅴★🆃★🅰 ★🅷★🆄 ★🅼 ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🆃★🅰★🅿★🅰 ★🆃★🅰★🅿★🅿★🅿★🅿★🅿",
"★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 ★🆃★🅤 ★??★🅴★🆁★🅴★🅶★🅰 ★🆃★🆈★🅿★🅸★🅽★🅶 ★🅺★🆁★🅴★🅶★🅰 ★🆃★🅼★🅺★🅲",
"★🅱★🅴★🅱★🅳 ★🅿★🅺★🅳 ★🅻★🆆★🅳★🅴★🅴★🅴★🅴 ★🆆★🆁★🅽★🅰 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳 ★🅿★🅺★🅳",
"★🅱★🅰★🅰★🅿 ★🅺★🅸 ★🅱★🅴★🅱★🅳 ★🅼★🆃★🅲★🅷 ★🅺★🆁★🆁★🆁",
"★🅻★🆆★🅳★🅰 ★🅻★🅴 ★🅼★🅴★🆁★🅰 ★🅹★🅰★🅻★🅳★🅸 ★🆂★🅴 ★🆃★🅤",
"★🅿★🅰★🅿★🅰 ★🅺★🅸 ★🅱★🅴★🅱★🅳 ★🅼★🆃★🅲★🅷 ★🅽★🅷★🅸 ★🅷★🅾 ★🆁★🅷★🅸 ★🅺★🆈★🅰 ★🆃★??★🆁★🅴★🆂★🅴",
"★🅰★🅻★🅴 ★🅰★🅻★🅴 ★🅼★🅴★🅻★🅰 ★🅱★🅲★🅷★🅰★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅺★🅰 ★🅱★🅾★🅂★🅳★🅰 ★🆂★🆄★🅽",
"★🅲★🅷★🆄★🅳 ★🅶★🆈★🅰 ★🆁★🅰★🅽★🅳★🅸★🅱★🅰★🅰★🅾 ★🅿★🅰★🅿★🅰 ★🅱★🅴★🅴★🅴 ★🆃★🅤",
"★🅼★🅴★🅽★🆄 ★🅺★🅸 ★🅿★🆃★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸",
"★🅺★🅾★🅸 ★🅱★🅰★🅰★🆃 ★🅽★🅈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🆈 ★🆃★🅴★🆁★🆈",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅰★🅰★🅰★🅰 ★🅼★🅰★🅺★🅰★🅱★🅾★🅂★🅳★🅰 ★🆃★🅴★🆁★🆈",
"★🆇★🅷★🆄★🅳 ★🅶★🅰★🅸 ★🅼★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅺★🅸★🅳★🅰★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅲★🅷★🆄★🅳 ★🅶★🆈★🅸 ★🅰★🅱 ★🅱★🅰★🆁 ★🅼★🆃 ★🅷★🅾★🅽★🅰",
"★🆈★🅴 ★🅻★🆄★🅽★🅳 ★🅻★🅴 ★🅼★🅴★🆁★🅰 ★🅲★🅷★🅻 ★🅹★🅰★🅻★🅳★🅸 ★🆂★🅴",
"★🅺★🅸★🅳★🅰★🅰★🅰 ★🅱★🅰★🆁 ★🅽★🅰 ★🅷★🅾 ★🆃★🅤 ★🅷★🅰★🅷★🅰★🅷★🅷",
"★🅱★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🆆★🅳★🅴 ★🅱★🅷★🆁★🅼 ★🅺★🆁",
"★🅺★🅸★🆃★🅽★🅸 ★🅶★🅻★🅸★🅈★🅰 ★🅿★🅳★🆆★🅴★🅶★🅰 ★🅰★🅿★🅽★🅸 ★🅼★🅰 ★🅺★🅾",
"★🅲★🅷★🆄★🅿 ★🅽★🅰★🅻★🅻★🅸★🅸 ★🆁★🅰★🅽★🅳★🆈★🅺★🅴 ★🅻★🅰★🅳★🅺★🅴",
"★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅱★🅰★🅳★🅰★🅺 ★🅿★🅁 ★🅻★🅸★🆃★🅰★🅺★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🆄★🅽★🅶★🅰 😂😆🤤",
"★🅰★🅱★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰 ★🅼★🅰★🅳★🅴★🆁★🅲★🅷★🅾★🅾★🅳 ★🅺★🆁 ★🅿★🅸★🅻★🅻★🅴 ★🅿★🅰★🅿★🅰 ★🅱★🅴★🅴 ★🅻★🅰★🅳★🅴★🅶★🅰 ★🆃★🅤 😼😂🤤",
"★🅶★🅰★🅻★🅸 ★🅶★🅰★🅻★🅸 ★🅽★🅴 ★🅱★🅷★🅾★🆁 ★🅷★🅴 ★🆃★🅴★??★🅸 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸 ★🅲★🅷★🅾★🆁 ★🅷★🅴 💋💋💦",
"★🅰★🅱★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳★🆄 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🅺★🆄★🆃★🆃★🅴 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 😂👻🔥",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅰★🅸★🅱★🅴 ★🅲★🅷★🅾★🅳★🅰 ★🅰★🅸★🅱★🅴 ★🅲★🅷★🅾★🅳★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅱★🅴★🅳 ★🅿★🅴★🅷★🅸 ★🅼★🆄★🆃★🅷 ★🅳★🅸★🅰 💦💦💦💦",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🅱★🅷★🅾★🅱★🅴★🅳★🅴 ★🅼★🅴 ★🅰★??★🅰★🅶 ★🅻★🅰★🅶★🅰★🅳★🅸★🅰 ★🅼★🅴★🆁★🅰 ★🅼★🅾★🆃★🅰 ★🅻★🆄★🅽★🅳 ★🅳★🅰★🅻★🅺★🅴 🔥🔥💦😆😆",
"★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳★🆄 ★🅲★🅷★🅰★🅻 ★🅽★🅸★🅺★🅰★🅻",
"★🅺★🅸★🆃★🅽★🅰 ★🅲★🅷★🅾★🅳★🆄 ★🆃★🅴★🆁★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅰★🅱★🅱 ★🅰★🅿★🅽★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅱★🅷★🅴★🅹 😆👻🤤",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾★🆃★🅾 ★🅲★🅷★🅾★🅳 ★🅲★🅷★🅾★🅳★🅺★🅴 ★🅿★🆄★🆁★🅰 ★🅱★🅰★🅰★🅳 ★🅳★🅸★🅰 ★🅲★🅷★🆄★🆃★🅷 ★🅰★🅱★🅱 ★??★🅴★🆁★🅸 ★🅶★🅱 ★🅺★🅾 ★🅱★🅷★🅴★🅹 😆💦🤤",
"★🆃★🅴★🆁★🅸 ★🅶★🅱 ★🅺★🅾 ★🅴★🆃★🅽★🅰 ★🅲★🅷★🅾★🅳★🅰 ★🅱★🅴★🅷★🅴★🅽 ★??★🅴 ★🅻★🅾★🅳★🅴 ★🆃★🅴★🆁★🅸 ★🅶★🅱 ★🆃★🅾 ★🅼★🅴★🆁★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅱★🅰★🅽★🅶★🅰★🆈★🅸 ★🅰★🅱★🅱 ★🅲★🅷★🅰★🅻 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳★🆃★🅰 ★🅱★🅸★🆁★🅱★🅴 ♥️💦😆😆😆😆",
"★🅷★🅰★🆁★🅸 ★🅷★🅰★🆁★🅸 ★🅶★🅷★🅰★🅰★🅱 ★🅼★🅴 ★🅹★🅷★🅾★🅿★🅳★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰 🤣🤣💋💦",
"★🅲★🅷★🅰★🅻 ★🆃★🅴★🆁★🅴 ★🅱★🅰★🅰★🅿 ★🅺★🅾 ★🅱★🅷★🅴★🅹 ★🆃★🅴★🆁★🅰 ★🅱★🅰★🅱★🅺★🅰 ★🅽★🅷★🅸 ★🅷★🅴 ★🅿★🅰★🅿★🅰 ★🅱★🅴★🅴 ★🅻★🅰★🅳★🅴★🅶★🅰 ★🆃★🅤",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅱★🅾★🅼★🅱 ★🅳★🅰★🅻★🅺★🅴 ★🆄★🅳★🅰 ★🅳★🆄★🅽★🅶★🅰 ★🅼★🅰★🅰★🅺★🅴 ★🅻★🅰★🆆★🅳★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🆃★🆁★🅰★🅸★🅽 ★🅼★🅴 ★🅻★🅴★🅹★🅰★🅺★🅴 ★🆃★🅾★🅿 ★🅱★🅴★🅳 ★🅿★🅴 ★🅻★🅸★🆃★🅰★🅺★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🆄★🅽★🅶★🅰 ★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 🤣🤣💋💋",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅴 ★🅽★🆄★🅳★🅴★🅰 ★🅶★🅾★🅾★🅶★🅻★🅴 ★🅿★🅴 ★🆄★🅿★🅻★🅾★🅰★🅳 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🅰★🅴★🆆★🅳★🅴 👻🔥",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅴 ★🅽★🆄★🅳★🅴★🅰 ★🅶★🅾★🅾★🅶★🅻★🅴 ★🅿★🅴 ★🆄★🅿★🅻★🅾★🅰★🅳 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🅰★🅴★🆆★🅳★🅴 👻🔥",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳 ★??★🅷★🅾★🅳★🅺★🅴 ★🅱★🅰★🅽★🅰★🅺★🅴 ★🅱★🅸★🅳★🅴★🅾 ★🅱★🅰★🅽★🅰★🅺★🅴 ★🆇★🅽★🆇★🆇.★🅲★🅾★🅼 ★🅿★🅴 ★🅽★🅴★🅴★🅻★🅰★🅼 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅺★🆄★🆃★🆃★🅴 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 💦💋",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🅳★🅰★🅸 ★🅺★🅾 ★🅿★🅾★🆁★🅽★🅷★🆄★🅱.★🅲★🅾★🅼 ★🅿★🅴 ★🆄★🅿★🅻★🅾★🅰★🅳 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 🤣💋💦",
"★🅰★🅱★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳★🆄 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🆃★🅴★🆁★🅴★🅺★🅾 ★🅲★🅷★🅰★🅺★🅺★🅾 ★🅱★🅴★🅴 ★🅿★🅸★🅻★🆆★🅰★🆅★🆄★🅽★🅶★🅰 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 🤣🤣",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅱★🅰★🅰★🅳★🅺★🅴 ★🆁★🅰★🅺★🅳★🅸★🅰 ★🅼★🅰★🅰★🅺★🅴 ★🅻★🅾★🅳★🅴 ★🅹★🅰★🅰 ★🅰★🅱★🅱 ★🅱★🅸★🅻★🆆★🅰★🅻★🅴 👄👄",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳 ★🅺★🅰★🅰★🅻★🅰",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅻★🅴★🆃★🅸 ★🅼★🅴★🆁★🅸 ★🅻★🆄★🅽★🅳 ★🅱★🅰★🅳★🅴 ★🅼★🅰★🅱★🅰★🅱★🅸 ★🅱★🅴★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅼★🅴★🅽★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🅰★🅻★🅰 ★🅱★🅾★🅷★🅾★🆃 ★🅱★🅰★🅱★🆃★🅴 ★🅱★🅴★🅴",
"★🅱★🅴★🆃★🅴 ★🆃★🅤 ★🅱★🅰★🅰★🅿 ★🅱★🅴★🅴 ★🅻★🅴★🅶★🅰 ★🅿★🅰★🅽★🅶★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅾 ★🅲★🅷★🅾★🅳 ★🅳★🆄★🅽★🅶★🅰 ★🅺★🅰★🆁★🅺★🅴 ★🅽★🅰★🅽★🅶★🅰 💦💋",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅷 ★🅼★🅴★🆁★🅴 ★🅱★🅴★🆃★🅴 ★🅰★🅶★🅻★🅸 ★🅱★🅰★🅰★🆁 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅻★🅴★🅺★🅴 ★🅰★🅰★🆈★🅰 ★🅼★🅰★🆃★🅷 ★🅺★🅰★🆃 ★🅾★🆁 ★🅼★🅴★🆁★🅴 ★🅼★🅾★🆃★🅴 ★🅻★🆄★🅽★🅳 ★🅱★🅴★🅴 ★🅲★🅷★🆄★🅳★🆆★🅰★🆈★🅰 ★🅼★🅰★🆃★🅷 ★🅺★🅰★🆁",
"★🅲★🅷★🅰★🅻 ★🅱★🅴★🆃★🅰 ★🆃★🆄★🅹★🅷★🅴 ★🅼★🅰★🅰★🅱 ★🅺★🅸★🅰 🤣★🆃★🅤 ★🅰★🅱★🅱 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅺★🅾 ★🅱★🅷★🅴★🅹",
"★🅱★🅷★🅰★🆁★🅰★🅼 ★🅺★🅰★🆁 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅳★🅰 ★🅺★🅸★🆃★🅽★🅰 ★🅶★🅰★🅰★??★🅸★🅰 ★🅱★🆄★🅽★🆆★🅰★🆈★🅴★🅶★🅰 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅰★🅰 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🆄★🅿★🅴★🆁",
"★🅰★🅱★🅴 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🅰★🆄★🅺★🅰★🆃 ★🅽★🅷★🅸 ★🅷★🅴★🆃★🅾 ★🅰★🅿★🅽★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅻★🅴★🅺★🅴 ★🅰★🅰★🆈★🅰 ★🅼★🅰★🆃★🅷 ★🅺★🅰★🆁 ★🅷★🅰★🅷★🅰★🅷★🅰★🅷★🅰",
"★🅺★🅸★🅳★🅾 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★?? ★🅲★🅷★🅾★🅳★🅺★🅴 ★🆃★🅴★🆁★🆁 ★🅻★🅸★🆈★🅴 ★🅱★🅷★🅰★🅸 ★🅳★🅴★🅳★🅸★🆈★🅰",
"★🅹★🆄★🅽★🅶★🅻★🅴 ★🅼★🅴 ★🅽★🅰★🅲★🅷★🆃★🅰 ★🅷★🅴 ★🅼★🅾★🆁★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🅳★🅰★🅸 ★🅳★🅴★🅺★🅺★🅴 ★🅱★🅰★🅱 ★🅱★🅾★🅻★🆃★🅴 ★🅾★🅽★🅲★🅴 ★🅼★🅾★🆁★🅴 ★🅾★🅽★🅲★🅴 ★🅼★🅾★🆁★🅴 🤣🤣💦💋",
"★🅶★🅰★??★🅸 ★🅶★🅰★🅻★🅸 ★🅼★🅴 ★🆁★🅴★🅷★🆃★🅰 ★🅷★🅴 ★🅱★🅰★🅽★🅳 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳 ★🅳★🅰★🅻★🅰 ★🅾★🆁 ★🅱★🅰★🅽★🅰 ★🅳★🅸★🅰 ★🆁★🅰★🅽★🅳 🤤🤣",
"★🅱★🅰★🅱 ★🅱★🅾★🅻★🆃★🅴 ★🅼★🆄★🅹★🅷★🅺★🅾 ★🅿★🅰★🅿★🅰 ★🅲★🆈★🆄★🅺★🅸 ★🅼★🅴★🅽★🅴 ★🅺★🆁★🅳★🅸★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅿★🆁★🅴★🅶★🅽★🅴★🅽★🆃 🤣🤣",
"★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅱★🅰★🅰★🆁 ★🅺★🅰 ★🅻★🅾★🆄★🅳★🅰 ★🅾★🆁 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅼★🅴★🆁★🅰 ★🅻★🅾★🅳★🅰",
"★🅲★🅷★🅰★🅻 ★🅲★🅷★🅰★🅻 ★🆃★🅤 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🅲★🅷★🅸★🆈★🅰 ★🅳★🅸★🅺★🅰",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅷★🅰 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳 ★🅳★🅸★🅰 ★🅽★🅰★🅽★🅶★🅰 ★🅺★🅰★🆁★🅺★🅴",
"★🆃★🅴★🆁★🅸 ★🅶★🅱 ★🅷★🅴 ★🅱★🅰★🅳★🅸 ★🅱★🅴★🆇★🆈 ★🆄★🅱★🅺★🅾 ★🅿★🅸★🅻★🅰★🅺★🅴 ★🅲★🅷★🅾★🅾★🅳★🅴★🅽★🅶★🅴 ★🅿★🅴★🅿★🅱★🅸",
"2 ★🆁★🆄★🅿★🅰★🆈 ★🅺★🅸 ★🅿★🅴★🅿★🅱★🅸 ★🆃★🅴★🆁★🅸 ★🅼★🆄★🅼★🅼★🆈 ★🅱★??★🅱★🅱★🅴 ★🅱★🅴★🆇★🆈 💋💦",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅴★🅴★🅼★🅱 ★🅱★🅴★🅴 ★🅲★🅷★🆄★🅳★🆆★🅰★🆅★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅴★🆁★🅲★🅷★🅾★🅾★🅳 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 💦🤣",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅼★🆄★🆃★🅷★🅺★🅴 ★🅱★🅰★🆁★🅰★🆁 ★🅷★🅾★🅹★🅰★🆅★🆄★🅽★🅶★🅰 ★🅷★🆄★🅸 ★🅷★🆄★🅸 ★🅷★🆄★🅸",
"★🅱★🅴★🅱★🅳 ★🅻★🅰★🅰★🅰 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅲★🅷★🅾★🅳★🆄 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 💋💦🤣",
"★🅰★🆁★🅴 ★🆁★🅴 ★🅼★🅴★🆁★🅴 ★🅱★🅴★🆃★🅴 ★🅲★🆈★🆄 ★🅱★🅴★🅱★🅳 ★🅿★🅰★🅺★🅰★🅳 ★🅽★🅰 ★🅿★🅰★🅰★🅰 ★🆁★🅰★🅷★🅰 ★🅰★🅿★🅽★🅴 ★🅱★🅰★🅰★🅿 ★🅺★🅰 ★🅷★🅰★🅷★🅰★🅷★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸🤣🤣",
"★🅱★🆄★🅽 ★🅱★🆄★🅽 ★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🅹★🅷★🅰★🅽★🆃★🅾 ★🅺★🅴 ★🅱★🅾★🆄★🅳★🅰★🅶★🅰★🆁 ★🅰★🅿★🅽★🅸 ★🅼★🆄★🅼★🅼★🆈 ★🅺★🅸 ★🅽★🆄★🅳★🅴★🅱 ★🅱★🅷★🅴★🅹",
"★🅰★🅱★🅴 ★🅱★🆄★🅽 ★🅻★🅾★🅳★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅳★🅰 ★🅱★🅰★🅰★🅳 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅺★🅷★🆄★🅻★🅴 ★🅱★🅰★🅹★🅰★🆁 ★🅼★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🅰★🅻★🅰 🤣🤣💋",
"★🅱★🅷★🆁★🅼 ★🅺★🆁 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸 ★🆈★🅷★🅰",
"★🅼★🅴★🆁★🅴 ★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅰★🅻★🅻★🅻★🅻★🅻 ★🅿★🅺★🅳 ★🅹★🅰★🅻★🅳★🅸 ★🅱★🅴★🅴",
"★🆃★🅤 ★🅴★🅺 ★🅺★🅰★🅰★🅼 ★🅺★🆁 ★🅰★🅿★🅽★🅸 ★🅼★🅰 ★🅱★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🆄★🅳★🆆★🅰 ★🅻★🅴 ★🅼★🅴★🆁★🅴 ★🅱★🆃★🅷",
"★🆁★🅽★🅳★🅸 ★🅺★🅴 ★🅻★🅳★🅺★🅴★🅴★🅴★🅴★🅴★🅴★🅴★🅴 ★🅲★🅷★🆄★🅿 ★🅾★🆁 ★🅲★🆄★🅳 ★🆈★🅷★🅰",
"★🅲★🅷★🆄★🅿 ★🆃★🅼★🅺★🅲 ★🅺★🅸★🅳★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰",
"★🅰★🅿★🅽★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴★🅸★🅽 ★🅼★🆄★🆃★🅷★🅸 ★🅳★🅰★🅰★🅻",
"★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳 ★🅲★🅷★🅾★🅾★🅱 ★🅹★🅰★🅻★🅳★🅸 ★🅱★🅴★🅴",
"★🅰★🅿★🅽★🅸 ★🅼★🅰 ★🅺★🅾 ★🅲★🆄★🅱★🆆★🅰 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳",
"★🅱★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🅰★🆄★🅳★🅴 ★🆃★🅼★🅲",
"★🅱★🅷★🅴★🅽 ★🅺★🅴 ★🆃★🅰★🅺★🅺★🅴 ★🆃★🅼★🅻",
"★🅰★🅱★🅻★🅰 ★🆃★🅴★🆁★🅰 ★🅺★🅷★🅰★🅽 ★🅳★🅰★🅽 ★🅲★🅷★🅾★🅳★🅽★🅴 ★🅺★🅸 ★🅱★🅰★🆁★🅸★🅸",
"★🅱★🅴★🆃★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅱★🅰★🅱★🅱★🅴 ★🅱★🅳★🅸 ★🆁★🅰★🅽★🅳",
"★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅻 ★🅹★🅷★🅰★🆃 ★🅺★🅴 ★🅿★🅸★🅱★🅱★🅱★🆄★🆄★🆄★🆄★🆄★🆄 ★🆃★🅼★🅺★🅲",
"★🅻★🆄★🅽★🅳 ★🅿★🅴 ★🅻★🆃★🅺★🅸★🆃 ★🅼★🅰★🅰★🅻★🅻★🅻★🅻 ★🅺★🅸 ★🅱★🅾★🅽★🅳 ★🅷 ★🆃★🆄★??★🆄",
"★🅺★🅰★🅱★🅷 ★🅾★🅱 ★🅳★🅸★🅽 ★🅼★🆄★🆃★🅷 ★🅼★🆁★🅺★🅴 ★🅱★🅾★🅹★🆃★🅰 ★🅼 ★🆃★🅤 ★🅿★🅰★🅸★🅳★🅰 ★🅽★🅰 ★🅷★🅾★🆃★🅰★🅰",
"★🅶★🅻★🆃★🅸 ★🅺★🆁★🅳★🅸 ★🆃★🆄★🅹★🆆 ★🅿★🅰★🅸★🅳★🅰 ★🅺★🆁★🅺★🅴 ★🆃★🅴★🆁★🆈 ★🅼★🅰 ★🅽★🅴 ★🅰★🅱 ★🅲★🆄★🅳 ★🆃★🅤 ★🆈★🅷★🅰",
"★🅱★🅴★🅱★🅳 ★🅿★🅺★🅳★🅳★🅳",
"★🅶★🅰★🅰★🅽★🅳 ★🅼★🅰★🅸★🅽 ★🅻★🆆★🅳★🅰 ★🅳★🅰★🅻 ★🅻★🅴 ★🅰★🅿★🅽★🅸 ★🅼★🅴★🆁★🅰★🅰★🅰",
"★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴★🅸★🅽 ★🅱★🅰★🅼★🅱★🆄 ★🅳★🅴★🅳★🆄★🅽★🅶★🅰★🅰★🅰★🅰★🅰",
"★🅶★🅰★🅽★🅳 ★🅱★🆃★🅸 ★🅺★🅴 ★🅱★🅰★🅻★🅺★🅺★🅺 ★🆃★🅤 ★🅲★🆄★🅳 ★🆈★🅷★🅰",
"★🅶★🅾★🆃★🅴 ★🅺★🅸★🆃★🅽★🅴 ★🅱★🅷★🅸 ★🅱★🅰★🅳★🅴 ★🅷★🅾, ★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅽★🅸★🅲★🅷★🅴 ★🅷★🅸 ★🆁★🅴★🅷★🆃★🅴 ★🅷★🅰",
"★🅷★🅰★🅾★??★🅰★🆁 ★🅻★🆄★🅽★🅳 ★🆃★🅴★🆁★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅰★🅸★🅽",
"★🅹★🅷★🅰★🅰★🅽★🆃 ★🅺★🅴 ★🅿★🅸★🅱★🅱★🆄 ★🆃★🅼★🅺★🅲 ★🅱★🆄★🅽",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅺★🅰★🅻★🅸 ★🅲★🅷★🆄★🆃",
"★🅺★🅷★🅾★🆃★🅴★🆈 ★🅺★🅸 ★🅰★🆄★??★🅳★🅰 ★🅴★🆈 ★🆃★🅤 ★🆁★🅰★🅽★🅳★🆈★🅺★🅴",
"★🅺★🆄★🆃★🆃★🅴 ★🅺★🅰 ★🅰★🆆★🅻★🅰★🆃 ★🅹★🅰★🅸★🅱★🅰 ★🅻★🅶 ★🆁★🅷★🅰 ★🆃★🅤",
"★🅺★🆄★🆃★🆃★🅴 ★🅺★🅸 ★🅹★🅰★🆃 ★🅹★🅰★🅸★🅱★🅰 ★🅴★🆈 ★🆃★🅤 ",
"★🅺★🆄★🆃★🆃★🅴 ★🅺★🅴 ★🆃★🅰★🆃★🆃★🅰 ★🅴★🆈 ★🆃★🅤",
"★🆃★🅴★🆃★🅸 ★🅼★🅰 ★🅺★🅸.★🅲★🅷★🆄★🆃 , ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🆁★🅽★🅳★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸",
"★🅻★🅰★🆅★🅳★🅴 ★🅺★🅴 ★🅱★🅰★🅻 ★🅿★🅺★🅳 ★🅻★🅴 ★🅼★🅴★🆁★🅴",
"★🅼★🆄★🅷 ★🅼★🅴★🅸 ★🅻★🅴★🅻★🅴 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳",
"★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅿★🅰★🅱★🅸★🅽★🅴 ★🅲★🅷★🆄★🅿 ★🅱★🅴★🆃★🅷 ★🅾★🆁 ★🅲★🆄★🅳",
"★🅼★🅴★🆁★🅴 ★🅻★🆆★🅳★🅴 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅰★🅻★🅻★🅻",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅰★🅰★🅰★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸",
"★🆃★🅤 ★🅲★🅷★🆄★🅳 ★🅶★🆈★🅰★🅰★🅰★🅰",
"★🆁★🅰★🅽★🅳★🅸 ★🅺★🅷★🅰★🅽★🅴 ★🅺★🅸 ★🆄★🅻★🅰★🅳★🅳★🅳",
"★🅱★🅰★🅳★🅸 ★🅷★🆄★🅸 ★🅶★🅰★🅰★🅽★🅳",
"★🆃★🅴★🆁★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅰★🅸★🅽 ★🅺★🆄★🆃★🅴 ★🅺★🅰 ★🅻★🆄★🅽★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃",
"★🆃★🅴★🆁★🅴 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴★🅸★🅽 ★🅺★🅴★🅴★🅳★🅴 ★🅿★🅰★🅳★🅰★🆈",
"★🅽★🆈 ★🅽★🆈 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸",
"★🅱★🆄★🅽★🅽 ★🅼★🅰★🅳★🅴★🆁★🅲★🅷★🅾★🅳 ★🆃★🅼★🅻",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰",
"★🅱★🅴★🅷★🅴★🅽 ★🅺 ★🅻★🆄★🅽★🅳 ★🅲★🅷★🆄★🅿★🅲★🅷★🅰★🅿 ★🅲★🆄★🅳 ★🆈★🅷★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅲★🅷★🆄★🆃 ★🅺★🅸 ★🅲★🅷★🆃★🅽★🅸★🅸★🅸",
"★🅼★🅴★🆁★🅰 ★🅻★🅰★🆆★🅳★🅰 ★🅻★🅴★🅻★🅴 ★🆃★🅤 ★🅰★🅶★🅰★🆁 ★🅲★🅷★🅰★🅸★🆈★🅴 ★🆃★🅾★🅷",
"★🅲★🅷★🆄★🅿 ★🅶★🅰★🅰★🅽★🅳★🆄",
"★🅲★🅷★🆄★🅿 ★🅲★🅷★🆄★🆃★🅸★🆈★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅿★🅴 ★🅹★🅲★🅱 ★🅲★🅷★🅰★🅳★🅷★🅰★🅰 ★🅳★🆄★🅽★🅶★🅰",
"★🅱★🅰★🅼★🅹★🅷★🅰★🅰 ★🅻★🅰★🆆★🅳★🅴",
"★🆈★🅰 ★🅳★🆄 ★🆃★🅴★🆁★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴 ★🆃★🅰★🅿★🅰★🅰 ★🆃★🅰★🅿",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅼★🅴★🆁★🅰 ★🆁★🅾★🅾 ★🅻★🅴★🆃★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅴 ★🅱★🅰★🅰★🆃★🅷 ★🅼★🅼★🅱 ★🅱★🅰★🅽★🅰★🅰 ★🅲★🅷★🆄★🅺★🅰 ★🅷★🆄",
"★🆃★🅤 ★🅲★🅷★🆄★🆃★🅸★🆈★🅰 ★🆃★🅴★🆁★🅰 ★🅺★🅷★🅰★🅽★🅳★🅰★🅰★🅽 ★🅲★🅷★🆄★🆃★🅸★🆈★🅰",
"★🅰★🆄★🆁 ★🅺★🅸★🆃★🅽★🅰 ★🅱★🅾★🅻★🆄 ★🅱★🅴★🆈 ★🅼★🅰★🅽★🅽 ★🅱★🅷★🅰★🆁 ★🅶★🅰★🆈★🅰 ★🅼★🅴★🆁★🅰",
"★🆃★🅴★🆁★🅸★🅸★🅸★🅸★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🆃★🆃 ★🅼★🅴 ★🅰★🅱★🅲★🅳 ★🅻★🅸★🅺★🅷 ★🅳★🆄★🅽★🅶★🅰 ★🅼★🅰★🅰 ★🅺★🅴 ★🅻★🅾★🅳★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅻★🅴★🅺★🅰★🆁 ★🅼★🅰★🅸 ★🅱★🅰★🆁★🅰★🆁",
"★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅸★🅳★🅸★🅸",
"★🅲★🅷★🆄★🅿 ★🅱★🅰★🅲★🅷★🅴★🅴 ★🆃★🅼★🅺★🅲",
"★🆃★🅴★🆁★🆈 ★🅼★🅰★🅺★🅾★🅲★🅷★🅾★🅳★🆄",
"★🆁★🅰★🅽★🅳★🅸 ★🅼★🅰★🅰 ★🆃★🅴★🆁★🆈",
"★🆃★🅤 ★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅰 ★🅴★🆈",
"★🆃★🅴★🆁★🅸★🅸★🅸★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅾 ★🅱★🅷★🅴★🅹★🅹★🅹",
"★🆃★🅴★🆁★🅰★🅰 ★🅱★🅰★🅰★🅰★🅿 ★🅷★🆄",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅷★🅰★🅰★🆃 ★🅳★🅰★🅰★🅻★🅻★🅺★🅴 ★🅱★🅷★🅰★🅰★🅶 ★🅹★🅰★🅰★🅽★🆄★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅱★🅰★🆁★🅰★🅺 ★🅿★🅴 ★🅻★🅴★??★🅰★🅰 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅶★🅱 ★🆁★🅾★🅰★🅳 ★🅿★🅴 ★🅻★🅴★🅹★🅰★🅺★🅴 ★🅱★🅴★🅲★🅷 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴★🅰 ★🅺★🅰★🅰★🅻★🅸 ★🅼★🅸★🆃★🅲★🅷",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅱★🅰★🅱★🆃★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅺★🅰★🅱★🆄★🆃★🅰★🆁 ★🅳★🅰★🅰★🅻 ★🅺★🅴 ★🅱★🅾★🆄★🅿 ★🅱★🅰★🅽★🅰★🆄★🅽★🅶★🅰 ★🅼★🅰★??★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅳★🅴★🆃★🅾★🅻 ★🅳★🅰★🅰★🅻 ★🅳★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅻★🅰★🅿★🆃★🅾★🅿",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅱★🅸★🅱★🆃★🅰★🆁 ★🅿★🅴 ★🅻★🅴★🆃★🅰★🅰★🅺★🅴 ★🅲★🅷★🅾★🅳★🆄★🅽★🅶★??",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅰★🅼★🅴★🆁★🅸★🅲★🅰 ★🅶★🅷★🆄★🅼★🅰★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅽★🅰★🅰★🆁★🅸★🆈★🅰★🅻 ★🅿★🅷★🅾★🆁 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅴 ★🅶★🅰★🅽★🅳 ★🅼★🅴 ★🅳★🅴★🆃★🅾★🅻 ★🅳★🅰★🅰★🅻 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅾 ★🅷★🅾★🆁★🅻★🅸★🅲★🅺★🅱 ★🅿★🅸★🅻★🅰★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅱★🅰★🆁★🅰★🅺 ★🅿★🅴 ★🅻★🅴★🆃★🅰★🅰★🅰 ★🅳★🆄★🅽★🅶★🅰★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰",
"★🅼★🅴★🆁★🅰★🅰 ★🅻★🆄★🅽★🅳 ★🅿★🅰★🅺★🅰★🅳 ★🅻★🅴 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🅲★🅷★🆄★🅿 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅰★🅺★🅰★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰★🅰",
"★🆃★🅴★🆁★🅸★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🆄★🅱 ★🅶★🅴★🆈★🅸 ★🅺★🆈★🅰★🅰 ★🅻★🅰★🆆★🅳★🅴★🅴★🅴",
"★🆃★🅴★🆁★🅸★🅸 ★🅼★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅹★🅱★🅾★🅳★🅰★🅰",
"★🅼★🅰★🅳★🅰★🆁★🅇★🅷★🅾★🅳★🅳★🅳",
"★🆃★🅴★🆁★🅸★🆄★🆄★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅷★🅱★🅾★🅳★🅰★🅰",
"★🆃★🅴★🆁★🅸★🅸★🅸★🅸★🅸 ★🅱★🅴★🅷★🅴★🅽★🅽★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳★🅳★🅳★🆄★🆄★🆄★🆄 ★🅼★🅰★🅳★🅰★🆁★🅇★🅷★🅾★🅳★🅳★🅳★🅳",
"★🆃★🅤 ★🅽★🅸★🅺★🅰★🅻 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🅲★🅷★🆄★🅿 ★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅰★🅲★🅷★🅴",
"★🆃★🅴★🆁★🅰 ★🅼★🅰★🅰 ★🅼★🅴★🆁★🅸 ★🅹★🅰★🅰★🅽 ★🅴★🆈",
"★🆃★🅴★🆁★🅸 ★🅱★🅰★🅱★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅾★🅿",
"★🅹★🅰★🅻★🅳★🅸 ★🅻★🅸★🅺★🅷 ★🆁★🅽★🅳★🆈★🅺★🅴 ★🅱★🅴★🅹",
"★🅾★🆁 ★🅱★🅳★🅰 ★🅻★🅸★🅺★🅷",
"★🅾★🆁 ★🅱★🅳★🅰",
"★🅾★🆁 ★🅱★🅳★🅰 ★🅾★🆈★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅱★🆄★🆁",
"★🅾★🆈★🅴 ★🅺★🅴★🅴★🅳★🅴",
"★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅻★🅰★🅳★🅺★🅴",
"★🅹★🅰★🅻★🅳★🅸 ★🅻★🅸★🅺★🅷 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅲★🅷★🅾★🅳★🆄",
"★🅼★🅺★🅻 ★🆄★🆃★🅷 ★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅰★🅲★🅲★🅷★🅴",
"★🆃★🅴★🆁★🅸 ★🅽★🅰★🅽★🅸 ★🅼★🅴★🆁★🅸 ★🅼★🅰★🅰★🅻",
"★🆃★🅴★🅹 ★🅻★🅸★🅺★🅷 ★🆁★🅰★🅽★🅳★🅲★🅴",
"★🅾★🆈★🅴 ★🅼★🅰★🅰★🅺★🅴 ★🅻★🅾★🅳★🅴 ★🅼★🆁★🅴★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🅾★🅳★🆈",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅸★🆈★🅰 ★🅺★🅸 ★🅶★🅰★🅽★🅳",
"★🆃★🅴★🆁★🆈 ★🅳★🅰★🅳★🅸 ★🅺★🅰 ★🅵★🆄★🅳★🅳★🅰",
"★🅼★🅺★🅻 ★🆄★🆃★🅷 ★🅱★🅴★🅷★🅴★🅽★🅲★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅱★🆄★🆁 ★🅳★🅴",
"★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅺★🅰 ★🅵★🆄★🅳★🅳★🅰 ★🅼★🅴 ★🅻★🅰★🆄★🅳★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🆄★🅳★🆅★🅰",
"★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅴★🆃★🅴 ★🅼★🅰★🆁 ★🅶★🅰★🆈★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🆁★🆄",
"★🅹★🅰★🅻★🅸★🅳 ★🅺★🆁 ★🆂★🅿★🅰★🅼",
"★🅼★🅲 ★🆂★🅿★🅰★🅼 ★🆁★🅾★🅺★🅴★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🆂★🅿★🅰★🅼 ★🅺★🆁",
"★🆂★🅿★🅰★🅼 ★🅺★🆁.★🅼★🅰★🅰★🅺★🅴 ★🅻★🅾★🅳★🅴",
"★🆁★🅽★🅸★🅳 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 ★🆂★🅿★🅰★🅼 ★🅺★🆁",
"★🆂★🅿★🅰★🅼 ★🅺★🆁 ★🅺★🅸★🅳",
"★🅽★🅾★🅾★🅱 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🅾★🅳★🆄",
"★🆁★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅴★🆃★🅴",
"★🅽★🅾★🅾★🅱 ★🅹★🅰★🅻★🅳★🅸 ★🅻★🅸★🅺★🅷 ★🆆★🆁★🅽★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳",
"★🅲★🆄★🅳 ★🅶★🅰★🅸 ★🅼★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅽★🅾★🅾★🅱",
"★🆄★🆃★🅷 ★🆁★??★🅽★🅳★🆈★🅺★🅴 ★🅽★🅾★🅾★🅱",
"★🅲★🅷★🅻 ★🅲★🆄★🅳★🅺★🅴 ★🅳★🅸★🅺★🅷★🅰 ★🅽★🅾★🅾★🅱",
"★🅹★🅻★🅳★🅸 ★🆃★🆈★🅿 ★🅲★🆁 ★🅽★🅾★🅾★🅱 ★🅷★🅰★🅻★🅺★🅴",
"★🅲★🆄★🅳 ★🅺★🅴 ★🅿★🅶★🅻 ★🅽★🆈 ★🅷★🅾 ★🅽★🅾★🅾★🅱",
"★🅲★🆄★🅳 ★🅲★🆄★🅳 ★🅺★🅴 ★🆁★🅰★🅽★🅳 ★🅱★🅽★🅹★🅰 ★🆃★🅤 ★🅽★🅾★🅾★🅱",
"★🅼★🅰★🅺★🅸★🅲★🅷★🆄★🆃 ★🆃★🅴★🆁★🆈 ★🅽★🅾★🅾★🅱",
"★🅶★🅰★🅽★🅳★🅰 ★🅲★🆈★🆄 ★🅲★🆄★🅳 ★🆁★🅷★🅰 ★🆃★🆄 ?",
"★🅸★??★🅽★🅰 ★🅶★🅽★🅳★🅰 ★🅽★🆈 ★🅲★🆄★🅳 ★🅰★🅲★🅷★🅴 ★🆂★🅴 ★🅲★🆄★🅳",
"★🅼★🅰★🅰★🅽 ★🅻★🅴 ★🅲★🆄★🅳 ★🅶★🆈★🅰 ★🆃★🅤 ★🆂★🆄★🅽 ★🅱★🅰★🆃 ★🅰★🅱",
"★🅼★🅰★🅺★🅰★🅵★🆄★🅳★🅳★🅰 ★🅵★🅰★🆃 ★🅶★🆈★🅰 ★🆃★🅴★🆁★🆈 ★🆁★🆄★🅺",

]
gr_texts = [
"""~~~~~ ~~~~~ ~~~~~ ~~~~~
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Pᴀɴɪ Kɪ Tᴀʀᴀʜ Cʜᴏᴅᴀ
~~~~~ ~~~~~ ~~~~~ ~~~~~""",
"""████████████████████████████
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴅᴀɪ Kɪ
████████████████████████████
✦ (🩷) ✦ (❤️) ✦ (🧡) ✦""",
"""☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Zʜᴇʀ Dᴀʟᴀ
☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️""",
"""✦━━━━━━━━━━━━━━━━━━━━━━━✦
🥇 ZA Nᴇ 🥇
Tᴇʀɪ Mᴀᴀ Kᴏ Gᴏʟᴅ Cʜᴜᴅᴀɪ Dɪ
✦━━━━━━━━━━━━━━━━━━━━━━━✦""",
"""🗑️━━━━━━━━━━━━━━━━━🗑️
║  ZA Nᴇ  ║
║  Tᴇʀɪ Mᴀᴀ Kᴏ Kᴀᴄʀᴀ Bɴᴀʏᴀ ║
🗑️━━━━━━━━━━━━━━━━━🗑️""",
"""☢️☢️☢️☢️☢️☢️☢️☢️☢️☢️
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴀ Bᴏsᴅᴀ Kʜᴏʟ Dɪʏᴀ
☢️☢️☢️☢️☢️☢️☢️☢️☢️☢️""",
"""🚀 Sᴘᴀᴄᴇ Mɪssɪᴏɴ: ZA
👨‍🚀 Cᴏᴍᴍᴀɴᴅᴇʀ: ZA
🌍 Tᴀʀɢᴇᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
🌟 Mɪssɪᴏɴ: Cʜᴏᴅ ᴀɴᴅ Dᴇsᴛʀᴏʏ""",
"""⏰ Tɪᴍᴇ: 3:00 AM
📍 Lᴏᴄᴀᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ Kᴇ Bʜᴏsᴅᴇ Mᴇ
👨 ZA Iɴ Aᴄᴛɪᴏɴ
🎬 Lɪᴠᴇ Sᴛʀᴇᴀᴍɪɴɢ...""",
"""🌧️ Mᴀᴜsᴀᴍ: Bᴀʀɪsʜ
🌊 Lᴇᴠᴇʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴀᴅʜ
⚡ ZA Nᴇ Bᴀɴᴅʜ Tᴏᴅᴀ""",
"""📰 Bʀᴇᴀᴋɪɴɢ Nᴇᴡs!
🗞️ ZA Nᴇ Cʜᴏᴅᴀ
👑 Tʀᴇɴᴅɪɴɢ #1 Oɴ Tᴇʟᴇɢʀᴀᴍ
⭐ ZA""",
"""🎬 Mᴏᴠɪᴇ: ZA
🎭 Sᴛᴀʀʀɪɴɢ: ZA
🎟️ Rᴀᴛɪɴɢ: ⭐⭐⭐⭐⭐
🍿 Bᴏx Oғғɪᴄᴇ: Tᴇʀɪ Mᴀᴀ""",
"""🎮 Gᴀᴍᴇ: ZA
👾 Pʟᴀʏᴇʀ: ZA
🏆 Lᴇᴠᴇʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
💀 Sᴄᴏʀᴇ: Iɴғɪɴɪᴛʏ""",
"""📋 Mᴇɴᴜ Cᴀʀᴅ:
🍽️ Mᴀɪɴ Cᴏᴜʀsᴇ: Tᴇʀɪ Mᴀᴀ
🍜 Sɪᴅᴇ Dɪsʜ: Tᴇʀɪ Bʜᴇɴ
🍰 Dᴇssᴇʀᴛ: ZA Kᴀ Lᴜɴᴅ
💵 Pʀɪᴄᴇ: Fʀᴇᴇ Cʜᴜᴅᴀɪ""",
"""🗺️ Nᴀᴠɪɢᴀᴛɪᴏɴ:
Sᴛᴀʀᴛ: ZA
Dᴇsᴛɪɴᴀᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
Dɪsᴛᴀɴᴄᴇ: 0 Mᴇᴛᴇʀs
ETA: Aʙʜɪ Cʜᴏᴅ Rʜᴀ Hᴜ""",
"""🎵 Nᴏᴡ Pʟᴀʏɪɴɢ:
🎶 Tʀᴀᴄᴋ: ZA
🎤 Aʀᴛɪsᴛ: ZA
💿 Aʟʙᴜᴍ: ZA Sᴇʀɪᴇs
🔥 Vɪᴇᴡs: 69M""",
"""🏏 Mᴀᴛᴄʜ: ZA Vs Tᴇʀɪ Mᴀᴀ
🏆 Wɪɴɴᴇʀ: ZA
📊 Sᴄᴏʀᴇ: Cʜᴏᴅ ᴏᴜᴛ
🔥 Mᴀɴ ᴏғ ᴛʜᴇ Mᴀᴛᴄʜ: Lᴜɴᴅ""",
"""🏥 Rᴇᴘᴏʀᴛ:
Dᴏᴄᴛᴏʀ: ZA
Pᴀᴛɪᴇɴᴛ: Tᴇʀɪ Mᴀᴀ
Dɪᴀɢɴᴏsɪs: Cʜᴜᴛ Mᴇ Lᴜɴᴅ
Tʀᴇᴀᴛᴍᴇɴᴛ: Cʜᴏᴅɴᴀ""",
"""🏫 Sᴄʜᴏᴏʟ: ZA Aᴄᴀᴅᴇᴍʏ
📚 Sᴜʙᴊᴇᴄᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴅᴀɪ 101
👨‍🏫 Tᴇᴀᴄʜᴇʀ: ZA
✅ Cʟᴀss: Iɴ Sᴇssɪᴏɴ""",
"""🛒 Sʜᴏᴘᴘɪɴɢ Cᴀʀᴛ:
🛍️ Iᴛᴇᴍ: Tᴇʀɪ Mᴀᴀ
💰 Pʀɪᴄᴇ: Fʀᴇᴇ
🛒 Bᴏᴜɢʜᴛ Bʏ: ZA
📦 Sᴛᴀᴛᴜs: Cʜᴏᴅ Dɪʏᴀ""",
"""🏨 Hᴏᴛᴇʟ: ZA Pᴀʟᴀᴄᴇ
🛏️ Rᴏᴏᴍ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
👤 Gᴜᴇsᴛ: ZA
⭐ Rᴀᴛɪɴɢ: 5 Sᴛᴀʀs""",
"""✈️ Fʟɪɢʜᴛ: ZA 101
🛫 Dᴇᴘᴀʀᴛᴜʀᴇ: ZA
🛬 Aʀʀɪᴠᴀʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
⏰ Tɪᴍᴇ: Nᴏᴡ""",
"""🚂 Tʀᴀɪɴ: ZA Exᴘʀᴇss
🚉 Sᴛᴀᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
👨‍✈️ Dʀɪᴠᴇʀ: ZA
🕒 Tɪᴍɪɴɢ: 24x7""",
"""🍕 Rᴇsᴛᴀᴜʀᴀɴᴛ: ZA Bᴀᴢᴀᴀʀ
🍽️ Sᴘᴇᴄɪᴀʟ: Tᴇʀɪ Mᴀᴀ
👨‍🍳 Cʜᴇғ: ZA
🍴 Oʀᴅᴇʀ: Cʜᴏᴅ ᴀɴᴅ Gᴏ""",
"""💪 Gʏᴍ: ZA Fɪᴛɴᴇss
🏋️ Tʀᴀɪɴᴇʀ: ZA
🎯 Tᴀʀɢᴇᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
✅ Rᴇsᴜʟᴛ: Pʜᴏᴏʟ Cʜᴏᴅ""",
"""🎉 Pᴀʀᴛʏ: ZA Nɪɢʜᴛ
🕺 Hᴏsᴛ: ZA
💃 Gᴜᴇsᴛ: Tᴇʀɪ Mᴀᴀ
🎵 Sᴏɴɢ: Cʜᴏᴅ Tʜᴇ Fʟᴏᴏʀ""",
"""🏛️ Mᴜsᴇᴜᴍ: ZA Hɪsᴛᴏʀʏ
🖼️ Exʜɪʙɪᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
🎨 Aʀᴛɪsᴛ: ZA
📅 Dᴀᴛᴇ: Hᴀʀ Rᴏᴢ""",
"""🦁 Zᴏᴏ: ZA Wᴏʀʟᴅ
🐯 Mᴀɪɴ Aᴛᴛʀᴀᴄᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ
🐺 Kᴇᴇᴘᴇʀ: ZA
🔥 Sʜᴏᴡ: Cʜᴏᴅᴜɴɢᴀ""",
"""🎪 Cɪʀᴄᴜs: ZA Mᴀsᴛɪ
🤡 Cʟᴏᴡɴ: ZA
🎪 Sʜᴏᴡ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴅᴀɪ
🎟️ Tɪᴄᴋᴇᴛ: Fʀᴇᴇ""",
"""📚 Lɪʙʀᴀʀʏ: ZA Bᴏᴏᴋs
📖 Bᴏᴏᴋ: ZA
✍️ Aᴜᴛʜᴏʀ: ZA
📕 Cʜᴀᴘᴛᴇʀ: Cʜᴏᴅɴᴀ""",
"""🌸 Gᴀʀᴅᴇɴ: ZA Fʟᴏᴡᴇʀs
🌹 Mᴀɪɴ Fʟᴏᴡᴇʀ: Tᴇʀɪ Mᴀᴀ
🌻 Gᴀʀᴅᴇɴᴇʀ: ZA
💧 Wᴀᴛᴇʀ: Lᴜɴᴅ Kᴀ Pᴀɴɪ""",
"""🏖️ Bᴇᴀᴄʜ: ZA Sʜᴏʀᴇ
🌊 Wᴀᴠᴇs: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
🏄 Sᴜʀғᴇʀ: ZA
🌅 Tɪᴍᴇ: Sᴜɴsᴇᴛ Cʜᴏᴅ""",
"""☕ Cᴏғғᴇᴇ Sʜᴏᴘ: ZA Cᴀғᴇ
🍵 Sᴘᴇᴄɪᴀʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
👨‍🍳 Bᴀʀɪsᴛᴀ: ZA
💦 Aᴅᴅɪᴛɪᴏɴ: Lᴜɴᴅ Kᴀ Cʀᴇᴀᴍ""",
"""🎰 Cᴀsɪɴᴏ: ZA Pᴀʟᴀᴄᴇ
🃏 Gᴀᴍᴇ: Cʜᴏᴅ Tʜᴇ ZA
🎲 Bᴇᴛ: Tᴇʀɪ Mᴀᴀ
💰 Wɪɴɴᴇʀ: ZA""",
"""🌙 Nɪɢʜᴛ Sʜᴏᴡ:
🌚 Mᴀɪɴ Aᴛᴛʀᴀᴄᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ
🌟 Hᴏsᴛ: ZA
💫 Pᴇʀғᴏʀᴍᴀɴᴄᴇ: Cʜᴏᴅɴᴀ""",
"""🌋🌋🌋🌋🌋🌋🌋🌋
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Jᴡᴀʟᴀ Pʜᴏᴅɪ
🌋🌋🌋🌋🌋🌋🌋🌋""",
"""🌊🌊🌊🌊🌊🌊🌊🌊
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tᴏᴏғᴀɴ Lᴀʏᴀ
🌊🌊🌊🌊🌊🌊🌊🌊""",
"""🌀🌀🌀🌀🌀🌀🌀🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bʜᴜᴄʜᴀʟ Lᴀʏɪ
🌀🌀🌀🌀🌀🌀🌀🌀""",
"""💻💻💻💻💻💻💻💻
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Cʏʙᴇʀ Cʜᴏᴅᴀ
💻💻💻💻💻💻💻💻""",
"""🤖🤖🤖🤖🤖🤖🤖🤖
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Rᴏʙᴏᴛ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🤖🤖🤖🤖🤖🤖🤖🤖""",
"""👽👽👽👽👽👽👽👽
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Aʟɪᴇɴ Gʜᴜsᴀʏᴀ
👽👽👽👽👽👽👽👽""",
"""🐉🔥🐉🔥🐉🔥🐉🔥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Dʀᴀɢᴏɴ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🐉🔥🐉🔥🐉🔥🐉🔥""",
"""⚡🔨⚡🔨⚡🔨⚡🔨
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tʜᴏʀ Kᴀ Hᴀᴍᴍᴇʀ Mᴀʀᴀ
⚡🔨⚡🔨⚡🔨⚡🔨""",
"""🦾💥🦾💥🦾💥🦾💥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Iʀᴏɴ Mᴀɴ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🦾💥🦾💥🦾💥🦾💥""",
"""💚💢💚💢💚💢💚💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Hᴜʟᴋ Sᴛʏʟᴇ Mᴇ Sᴍᴀsʜ Kɪʏᴀ
💚💢💚💢💚💢💚💢""",
"""🕷️🕸️🕷️🕸️🕷️🕸️🕷️🕸️
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴘɪᴅᴇʀ Wᴇʙ Bɴᴀʏᴀ
🕷️🕸️🕷️🕸️🕷️🕸️🕷️🕸️""",
"""🦇🌙🦇🌙🦇🌙🦇🌙
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Bᴀᴛᴍᴀɴ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🦇🌙🦇🌙🦇🌙🦇🌙""",
"""🦸💫🦸💫🦸💫🦸💫
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Sᴜᴘᴇʀᴍᴀɴ Sᴛʏʟᴇ Mᴇ Uᴅᴀʏᴀ
🦸💫🦸💫🦸💫🦸💫""",
"""🗡️💢🗡️💢🗡️💢🗡️💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Wᴏʟᴠᴇʀɪɴᴇ Cʟᴀᴡs Mᴀʀᴇ
🗡️💢🗡️💢🗡️💢🗡️💢""",
"""🔥💀🔥💀🔥💀🔥💀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Gʜᴏsᴛ Rɪᴅᴇʀ Gʜᴜsᴀʏᴀ
🔥💀🔥💀🔥💀🔥💀""",
"""💀🔫💀🔫💀🔫💀🔫
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pᴜɴɪsʜᴇʀ Dᴀʟᴀ
💀🔫💀🔫💀🔫💀🔫""",
"""🦸🔫🦸🔫🦸🔫🦸🔫
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Dᴇᴀᴅᴘᴏᴏʟ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🦸🔫🦸🔫🦸🔫🦸🔫""",
"""🖤👅🖤👅🖤👅🖤👅
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Vᴇɴᴏᴍ Gʜᴜsᴀʏᴀ
🖤👅🖤👅🖤👅🖤👅""",
"""🃏💚🃏💚🃏💚🃏💚
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Jᴏᴋᴇʀ Kʜᴇʟᴀ
🃏💚🃏💚🃏💚🃏💚""",
"""💕🔨💕🔨💕🔨💕🔨
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Hᴀʀʟᴇʏ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
💕🔨💕🔨💕🔨💕🔨""",
"""⚡💨⚡💨⚡💨⚡💨
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Fʟᴀsʜ Sᴘᴇᴇᴅ Dɪ
⚡💨⚡💨⚡💨⚡💨""",
"""🌊🔱🌊🔱🌊🔱🌊🔱
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Aǫᴜᴀᴍᴀɴ Gʜᴜsᴀʏᴀ
🌊🔱🌊🔱🌊🔱🌊🔱""",
"""👁️💥👁️💥👁️💥👁️💥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Cʏᴄʟᴏᴘs Bᴇᴀᴍ Mᴀʀᴀ
👁️💥👁️💥👁️💥👁️💥""",
"""🧲💢🧲💢🧲💢🧲💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Mᴀɢɴᴇᴛᴏ Gʜᴜsᴀʏᴀ
🧲💢🧲💢🧲💢🧲💢""",
"""🌩️⚡🌩️⚡🌩️⚡🌩️⚡
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴛᴏʀᴍ Lᴀʏᴀ
🌩️⚡🌩️⚡🌩️⚡🌩️⚡""",
"""💋💢💋💢💋💢💋💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Rᴏɢᴜᴇ Kɪss Dɪ
💋💢💋💢💋💢💋💢""",
"""🃏🔥🃏🔥🃏🔥🃏🔥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Gᴀᴍʙɪᴛ Cᴀʀᴅs Dᴀʟᴇ
🃏🔥🃏🔥🃏🔥🃏🔥""",
"""💨🌀💨🌀💨🌀💨🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Nɪɢʜᴛᴄʀᴀᴡʟᴇʀ Gʜᴜsᴀʏᴀ
💨🌀💨🌀💨🌀💨🌀""",
"""💙🌀💙🌀💙🌀💙🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Mʏsᴛɪǫᴜᴇ Gʜᴜsᴀʏᴀ
💙🌀💙🌀💙🌀💙🌀""",
"""🐾💢🐾💢🐾💢🐾💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴇᴀsᴛ Gʜᴜsᴀʏᴀ
🐾💢🐾💢🐾💢🐾💢""",
"""❄️🧊❄️🧊❄️🧊❄️🧊
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Iᴄᴇᴍᴀɴ Gʜᴜsᴀʏᴀ
❄️🧊❄️🧊❄️🧊❄️🧊""",
"""🔥💥🔥💥🔥💥🔥💥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʏʀᴏ Gʜᴜsᴀʏᴀ
🔥💥🔥💥🔥💥🔥💥""",
"""🌑🌀🌑🌀🌑🌀🌑🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sʜᴀᴅᴏᴡ Gʜᴜsᴀʏᴀ
🌑🌀🌑🌀🌑🌀🌑🌀""",
"""🔥🦅🔥🦅🔥🦅🔥🦅
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʜᴏᴇɴɪx Fɪʀᴇ Dᴀʟɪ
🔥🦅🔥🦅🔥🦅🔥🦅""",
"""🍔🍔🍔🍔🍔🍔🍔🍔🍔
??   😋   🍔
🍔  🧀   🍔
🍔  🥩   🍔
🍔🍔🍔🍔🍔🍔🍔🍔🍔

Tᴇʀɪ Mᴀᴀ Kᴏ Bᴜʀɢᴇʀ Bɴᴀᴋᴇ Kʜᴀʏᴀ""",
"""🍕🍕🍕🍕🍕🍕🍕🍕
🍕  🍅  🍕
🍕  🧀  🍕
🍕  🍕  🍕
🍕🍕🍕🍕🍕🍕🍕🍕

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pɪᴢᴢᴀ Dᴀʟᴀ""",
"""🌮🌮🌮🌮🌮🌮🌮🌮
🌮  😋  🌮
🌮  🥩  🌮
🌮  🌮  🌮
🌮🌮🌮🌮🌮🌮🌮🌮

Tᴇʀɪ Mᴀᴀ Kᴏ Tᴀᴄᴏ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ""",
"""🍩🍩🍩🍩🍩🍩🍩🍩
🍩  😋  🍩
🍩  🍩  🍩
🍩  🍩  🍩
🍩🍩🍩🍩🍩🍩🍩🍩

Tᴇʀɪ Mᴀᴀ Kᴏ Dᴏɴᴜᴛ Bɴᴀᴋᴇ Cʜᴏᴅᴀ""",
"""☕☕☕☕☕☕☕☕
☕  😋  ☕
☕  ☕  ☕
☕  ☕  ☕
☕☕☕☕☕☕☕☕

Tᴇʀɪ Mᴀᴀ Kᴏ Cᴏғғᴇᴇ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ""",
"""👑👑👑👑👑👑👑👑
👑  😎  👑
👑  👑  👑
👑  👑  👑
👑👑👑👑👑👑👑👑

ZA Nᴇ Tᴇʀɪ Mᴀᴀ Kᴏ Cʜᴏᴅᴀ""",
"""💖💖💖💖💖💖💖💖
💖  😍  💖
💖  💖  💖
💖  💖  💖
💖💖💖💖💖💖💖💖

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʏᴀʀ""",
"""💀💀💀💀💀💀💀💀
💀  😈  💀
💀  💀  💀
💀  💀  💀
💀💀💀💀💀💀💀💀

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀʀ Gᴀʏɪ""",
"""🔥🔥🔥🔥🔥🔥🔥🔥
🔥  😈  🔥
🔥  🔥  🔥
🔥  🔥  🔥
🔥🔥🔥🔥🔥🔥🔥🔥

ZA Nᴇ Aᴀɢ Lɢᴀʏɪ""",
"""👻👻👻👻👻👻👻👻
👻  😱  👻
👻  👻  👻
👻  👻  👻
👻👻👻👻👻👻👻👻

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Gʜᴏsᴛ""",
"""🌈🌈🌈🌈🌈🌈🌈🌈
🌈  😋  🌈
🌈  🌈  🌈
🌈  🌈  🌈
🌈🌈🌈🌈🌈🌈🌈🌈

Tᴇʀɪ Mᴀᴀ Kᴏ Rᴀɪɴʙᴏᴡ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ""",
"""💣➖💣➖➖💣➖💣
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🔥             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴏᴍʙ Pʜᴏᴅᴜɴɢᴀ""",
"""☢️➖☢️➖➖☢️➖☢️
🌟        \\         /          🌟
⭐️          \\☠️/            ⭐️
✨           💀             ✨
/    \\
🦴    🦴 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Nᴜᴄʟᴇᴀʀ Aᴛᴛᴀᴄᴋ""",
"""🐉➖🐉➖➖🐉➖🐉
🌟        \\         /          🌟
⭐️          \\🔥/            ⭐️
✨           🐲             ✨
/    \\
🔥    🔥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dʀᴀɢᴏɴ Gʜᴜsᴀʏᴀ""",
"""👿➖👿➖➖👿➖👿
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           👹             ✨
/    \\
🔱    🔱 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dᴇᴍᴏɴ Gʜᴜsᴀʏᴀ""",
"""💀➖💀➖➖💀➖💀
🌟        \\         /          🌟
⭐️          \\☠️/            ⭐️
✨           💀             ✨
/    \\
🦴    🦴 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀʀ Gᴀʏɪ""",
"""🔫➖🔫➖➖🔫➖🔫
🌟        \\         /          🌟
⭐️          \\😎/            ⭐️
✨           🎯             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tᴀɴᴋ Gʜᴜsᴀʏᴀ""",
"""⚔️➖⚔️➖➖⚔️➖⚔️
🌟        \\         /          🌟
⭐️          \\🗡️/            ⭐️
✨           ⚔️             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴡᴏʀᴅ Gʜᴜsᴀʏᴀ""",
"""🐍➖🐍➖➖🐍➖🐍
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐍             ✨
/    \\
☠️    ☠️ 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Vɪᴘᴇʀ Gʜᴜsᴀʏᴀ""",
"""🦂➖🦂➖➖🦂➖🦂
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦂             ✨
/    \\
☠️    ☠️ 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴄᴏʀᴘɪᴏɴ Gʜᴜsᴀʏᴀ""",
"""🐦‍⬛➖🐦‍⬛➖➖🐦‍⬛➖🐦‍⬛
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🖤             ✨
/    \\
🪶    🪶 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Rᴀᴠᴇɴ Gʜᴜsᴀʏᴀ""",
"""🐺➖🐺➖➖🐺➖🐺
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐺             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Wᴏʟғ Gʜᴜsᴀʏᴀ""",
"""🔥➖🔥➖➖🔥➖🔥
🌟        \\         /          🌟
⭐️          \\🦅/            ⭐️
✨           🔥             ✨
/    \\
💫    💫 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʜᴏᴇɴɪx Gʜᴜsᴀʏᴀ""",
"""🦁➖🦁➖➖🦁➖🦁
🌟        \\         /          🌟
⭐️          \\👑/            ⭐️
✨           🦁             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Lɪᴏɴ Gʜᴜsᴀʏᴀ""",
"""🐯➖🐯➖➖🐯➖🐯
🌟        \\         /          🌟
⭐️          \\🐅/            ⭐️
✨           🐯             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tɪɢᴇʀ Gʜᴜsᴀʏᴀ""",
"""🦈➖🦈➖➖🦈➖🦈
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦈             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sʜᴀʀᴋ Gʜᴜsᴀʏᴀ""",
"""🦅➖🦅➖➖🦅➖🦅
🌟        \\         /          🌟
⭐️          \\🦅/            ⭐️
✨           🦅             ✨
/    \\
🪶    🪶 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Eᴀɢʟᴇ Gʜᴜsᴀʏᴀ""",
"""🐂➖🐂➖➖🐂➖🐂
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐂             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴜʟʟ Gʜᴜsᴀʏᴀ""",
"""🦏➖🦏➖➖🦏➖🦏
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦏             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Rʜɪɴᴏ Gʜᴜsᴀʏᴀ""",
"""🐘➖🐘➖➖🐘➖🐘
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐘             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Eʟᴇᴘʜᴀɴᴛ Gʜᴜsᴀʏᴀ""",
"""🦛➖🦛➖➖🦛➖🦛
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦛             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Hɪᴘᴘᴏ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  💣  💣  █  █  █
█  █  █  💣  💣  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴏᴍʙ Pʜᴏᴅᴜɴɢᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  💀  💀  █  █  █
█  █  █  💀  💀  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀʀ Gᴀʏɪ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  ☢️  ☢️  █  █  █
█  █  █  ☢️  ☢️  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Nᴜᴄʟᴇᴀʀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🐉  🐉  █  █  █
█  █  █  🐉  🐉  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dʀᴀɢᴏɴ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🔫  🔫  █  █  █
█  █  █  🔫  🔫  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tᴀɴᴋ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🐍  🐍  █  █  █
█  █  █  🐍  🐍  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴀᴀᴘ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  👿  👿  █  █  █
█  █  █  👿  👿  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dᴇᴍᴏɴ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🦈  🦈  █  █  █
█  █  █  🦈  🦈  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sʜᴀʀᴋ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🦂  🦂  █  █  █
█  █  █  🦂  🦂  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bɪᴄʜʜᴜ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  👻  👻  █  █  █
█  █  █  👻  👻  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bʜᴏᴏᴛ Gʜᴜsᴀʏᴀ""",
]

# ─── PREMIUM SPAM TEXT LISTS ──────────────────────────────────────────
ms_texts = [
"TTTTTTT🍷EEEEEE💊RRRRR🔘OOOOO🎲BBBBB🤍EEEEEE💊GGGGGG🖤EEEEEE💊JJJJJJ👅 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊OOOOO🎲 AAAAAA👿AAAAAA👿AAAAAA👿MMMMM🚀MMMMM🚀AAAAAA👿 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘OOOOO🎲 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 LLLLLL🔨AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘",
"OOOOOO👅YYYYYYEEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜 BBBBB🤍JJJJJJ👅OOOOO🎲SSSSS⚒️RRRRR🔘WWWWW🥰",
"TTTTTTT🍷EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜 FFFFFF🔥AAAAAA👿NNNNNN🤣RRRRR🔘",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷RRRRR🔘",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿KKKKKK💜IIIIII🍷 GGGGGG🖤EEEEEE💊TTTTT🚭IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 MMMMM🚀UUUUU💣HHHHH🖤",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 CCCCCC⚔️HHHHH🖤IIIIII🍷NNNNNN🤣AAAAAA👿LLLLLL🔨",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 MMMMM🚀AAAAAA👿RRRRR🔘 GGGGGG🖤AAAAAA👿YYYYYYIIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣TTTTT🚭IIIIII🍷 RRRRR🔘AAAAAA👿DDDDD👿IIIIII🍷 KKKKKK💜IIIIII🍷 HHHHH🖤EEEEEE💊TTTTT🚭",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 CCCCCC⚔️IIIIII🍷OOOOO🎲DDDDD👿AAAAAA👿 AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿KKKKKK💜 MMMMM🚀",
"OOOOOO👅YYYYYYEEEEEE💊 KKKKKK💜IIIIII🍷NNNNNN🤣NNNNNN🤣AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA??CCCCCC⚔️CCCCCC⚔️GGGGGG🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII?? MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍IIIIII🍷OOOOO🎲AAAAAA👿RRRRR🔘SSSSS⚒️",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 MMMMM🚀AAAAAA👿RRRRR🔘AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿OOOOO🎲UUUUU💣AAAAAA👿 JJJJJJ👅AAAAAA👿AAAAAA👿NNNNNN🤣 CCCCCC⚔️JJJJJJ👅OOOOO🎲DDDDD👿YYYYYYAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 BBBBB🤍HHHHH🖤OOOOO🎲AAAAAA👿DDDDD👿AAAAAA👿 CCCCCC⚔️OOOOO🎲DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 CCCCCC⚔️HHHHH🖤UUUUU💣TTTTT??EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿.    KKKKKK📌AAAAAA👿AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍RRRRR🔘HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY KKKKKK💜UUUUU💣TTTTT🚭IIIIII🍷YYYYYYAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿HHHHH🖤IIIIII🍷 KKKKKK💜AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️GGGGGG🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 CCCCCC⚔️GGGGGG🖤OOOOO🎲DDDDD👿UUUUU💣",
"OOOOOO??YYYYYYEEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 CCCCCC⚔️HHHHH🖤UUUUU💣CCCCCC⚔️HHHHH🖤OOOOO🎲 KKKKKK💜AAAAAA👿TTTTT🚭YYYYYY",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿HHHHH🖤IIIIII🍷 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 CCCCCC⚔️GGGGGG🖤OOOOO🎲DDDDD👿YYYYYY",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀YYYYYY CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜IIIIII🍷 LLLLLL🔨AAAAAA👿DDDDD👿KKKKKK💜IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 JJJJJJ👅AAAAAA👿AAAAAA👿NNNNNN🤣 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE??RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘 FFFFFF🔥AAAAAA👿DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 BBBBB🤍AAAAAA👿NNNNNN🤣AAAAAA👿 DDDDD👿UUUUU💣NNNNNN🤣GGGGGG🖤AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿KKKKKK💜EEEEEE💊 FFFFFF🔥EEEEEE💊KKKKKK💜UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 MMMMM🚀UUUUU💣HHHHH🖤 MMMMM🚀EEEEEE💊IIIIII🍷 PPPPPP📌AAAAAA👿KKKKKK💜IIIIII🍷SSSSS⚒️TTTTT🚭AAAAAA👿NNNNNN🤣IIIIII🍷 LLLLLL🔨AAAAAA👿VVVVDDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 PPPPPP📌KKKKKK💜AAAAAA👿OOOOO🎲SSSSS⚒️TTTTT🚭AAAAAA👿NNNNNN🤣IIIIII🍷 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍EEEEEE💊TTTTT🚭",
"TTTTTTT🍷EEEEEE💊RRRRR🔘UUUUU💣 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣TTTTT🚭",
"OOOOOO👅YYYYYYEEEEEE💊 TTTTT🚭AAAAAA👿TTTTT🚭TTTTT🚭TTTTT🚭EEEEEE💊 UUUUU💣TTTTT🚭HHHHH🖤",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀MMMMM🚀YYYYYY CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️UUUUU💣UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿IIIIII🍷YYYYYYAAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿 DDDDD👿EEEEEE💊DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘OOOOO🎲 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 KKKKKK💜EEEEEE💊 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿EEEEEE💊 PPPPPP📌EEEEEE💊 LLLLLL🔨OOOOO🎲LLLLLL🔨LLLLLL🔨AAAAAA👿",
"LLLLLLL🎲OOOOO🎲LLLLLL🔨LLLLLL🔨EEEEEE💊 HHHHH🖤OOOOO🎲 LLLLLL🔨OOOOO🎲LLLLLL🔨LLLLLL🔨EEEEEE💊 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 PPPPPP📌EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 DDDDD👿EEEEEE💊 MMMMM🚀UUUUU💣JJJJJJ👅GGGGGG🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀UUUUU💣MMMMM🚀YYYYYY CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜 BBBBB🤍UUUUU💣RRRRR🔘 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 VVVVEEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 AAAAAA👿MMMMM🚀MMMMM🚀AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 FFFFFF🔥AAAAAA👿BBBBB🤍DDDDD👿 MMMMM🚀AAAAAA👿RRRRR🔘VVVVAAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘  MMMMM🚀AAAAAA👿RRRRR🔘VVVVAAAAAA👿",
"IIIIIIII⚒️DDDDD👿GGGGGG🖤AAAAAA👿RRRRR🔘 AAAAAA👿JJJJJJ👅AAAAAA👿AAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜AAAAAA👿 LLLLLL🔨AAAAAA👿DDDDD👿KKKKKK💜AAAAAA👿",
"IIIIIIII⚒️DDDDD👿HHHHH🖤AAAAAA👿 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿 DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊NNNNNN🤣 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 HHHHH🖤AAAAAA👿IIIIII🍷",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜YYYYYYTTTTT🚭TTTTT🚭OOOOO🎲 HHHHH🖤AAAAAA👿IIIIII🍷",
"YYYYYY🤍EEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"MMMMM💥AAAAAA👿RRRRR🔘 GGGGGG🖤AAAAAA👿YYYYYYAAAAAA👿 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿 AAAAAA👿 DDDDD👿EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊. KKKKKK📌 PPPPPP📌EEEEEE💊LLLLLL🔨UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 KKKKKK💜OOOOO🎲 LLLLLL🔨EEEEEE💊UUUUU💣 LLLLLL🔨UUUUU💣NNNNNN🤣DDDDD👿 PPPPPP📌EEEEEE💊 AAAAAA👿PPPPPP📌NNNNNN🤣EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 MMMMM🚀AAAAAA👿RRRRR🔘AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿 KKKKKK💜AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿AAAAAA👿 MMMMM🚀AAAAAA👿RRRRR🔘AAAAAA👿",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿AAAAAA👿",
"OOOOOO👅YYYYYYEEEEEE💊 TTTTT🚭AAAAAA👿TTTTT🚭TTTTT🚭EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 AAAAAA👿CCCCCC⚔️UUUUU💣DDDDD👿AAAAAA👿. AAAAAA👿BBBBB🤍",
"MMMMM💥AAAAAA👿RRRRR🔘NNNNNN??AAAAAA👿 MMMMM🚀AAAAAA👿NNNNNN🤣AAAAAA👿 HHHHH🖤AAAAAA👿IIIIII🍷 RRRRR🔘AAAAAA👿 DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊",
"MMMMM💥AAAAAA👿RRRRR🔘 MMMMM🚀AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 LLLLLL🔨IIIIII🍷MMMMM🚀HHHHH🖤EEEEEE💊AAAAAA👿 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿HHHHH🖤",
"OOOOOO👅YYYYYYEEEEEE💊 KKKKKK💜IIIIII🍷NNNNNN🤣AAAAAA👿AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA??CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊 UUUUU💣TTTTT🚭HHHHH🖤",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿VVVVAAAAAA👿 OOOOO🎲YYYYYYEEEEEE💊 TTTTT🚭AAAAAA👿TTTTT🚭TTTTT🚭EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 BBBBB🤍EEEEEE💊HHHHH🖤EEEEEE💊 CCCCCC⚔️BBBBB🤍UUUUU💣DDDDD👿VVVVAAAAAA👿 LLLLLL🔨EEEEEE💊",
"GGGGGG🌿EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 FFFFFF🔥AAAAAA👿NNNNNN🤣DDDDD👿 OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 KKKKKK💜AAAAAA👿AAAAAA👿AAAAAA👿 BBBBB🤍UUUUU💣RRRRR🔘 TTTTT🚭OOOOO🎲DDDDD👿UUUUU💣",
"TTTTTTT🍷AAAAAA👿TTTTT🚭TTTTT🚭TTTTT🚭EEEEEE💊 TTTTT🚭EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜EEEEEE💊 MMMMM🚀UUUUU💣HHHHH🖤 PPPPPP📌EEEEEE💊 LLLLLL🔨OOOOO🎲DDDDD👿AAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿 PPPPPP📌EEEEEE💊 LLLLLL🔨OOOOO🎲DDDDD👿AAAAAA👿",
"OOOOOO👅YYYYYYEEEEEE💊 RRRRR🔘AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 SSSSS⚒️AAAAAA👿MMMMM🚀JJJJJJ👿 WWWWW??AAAAAA👿LLLLLL🔨EEEEEE💊",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 KKKKKK💜IIIIII🍷.GGGGGG🖤AAAAAA👿 DDDDD👿 SSSSS⚒️AAAAAA👿MMMMM🚀BBBBB🤍HHHHH🖤AAAAAA👿LLLLLL🔨AAAAAA👿 KKKKKK💜EEEEEE💊 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 IIIIII🍷EEEEEE💊 BBBBB🤍EEEEEE💊YYYYYY",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 GGGGGG🖤AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 CCCCCC⚔️HHHHH🖤UUUUU💣TTTTT🚭EEEEEE💊 WWWWW🥰AAAAAA👿LLLLLL🔨IIIIII🍷 RRRRR🔘AAAAAA👿 DDDDD👿IIIIII🍷",
"MMMMM💥AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿AAAAAA👿",
"KKKKKK📌WWWWW🥰EEEEEE💊EEEEEE💊EEEEEE💊 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿EEEEEE💊 DDDDD👿EEEEEE💊",
"OOOOOO👅YYYYYYEEEEEE💊 BBBBB🤍HHHHH🖤AAAAAA👿NNNNNN🤣GGGGGG🖤IIIIII🍷 TTTTT🚭AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊",
"RRRRRR⚔️AAAAAA👿NNNNNN🤣DDDDD👿IIIIII🍷 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"KKKKKK📌IIIIII🍷NNNNNN🤣NNNNNN🤣AAAAAA👿RRRRR🔘 KKKKKK💜EEEEEE💊 BBBBB🤍AAAAAA👿CCCCCC⚔️CCCCCC⚔️HHHHH🖤EEEEEE💊",
"TTTTTTT🍷EEEEEE💊RRRRR🔘IIIIII🍷 MMMMM🚀AAAAAA👿AAAAAA👿AAAAAA👿 NNNNNN🤣AAAAAA👿 CCCCCC⚔️HHHHH🖤UUUUU💣DDDDD👿BBBBB🤍YYYYYYEEEEEE💊GGGGGG🖤AAAAAA👿",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 KKKKKK💜AAAAAA👿AAAAAA👿AAAAAA👿 BBBBB🤍HHHHH🖤OOOOO🎲SSSSS⚒️DDDDD👿SSSSS⚒️ DDDDD👿EEEEEE💊DDDDD👿EEEEEE💊",
"AAAAAA👿BBBBB🤍 CCCCCC⚔️HHHHH🖤AAAAAA??LLLLLL🔨 LLLLLL🔨UUUUU💣NNNNNN🤣DDDDD👿 KKKKKK💜EEEEEE💊 CCCCCC⚔️HHHHH🖤UUUUU💣PPPPPP📌PPPPPP📌EEEEEE💊 KKKKKK💜AAAAAA👿RRRRR🔘",
"TTTTTTT🍷EEEEEE💊EEEEEE💊IIIIII🍷 BBBBB🤍AAAAAA👿JJJJJJ👅IIIIII🍷 CCCCCC⚔️HHHHH🖤OOOOO🎲DDDDD👿UUUUU💣 OOOOO🎲YYYYYYEEEEEE💊"
]

ms2_texts = [
"B⃠a⃠a⃠p⃠ b⃠h⃠i⃠ b⃠n⃠a⃠l⃠e⃠ m⃠u⃠j⃠e⃠ r⃠n⃠d⃠i⃠k⃠e⃠",
"T⃠e⃠r⃠a⃠ b⃠a⃠a⃠p⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ e⃠y⃠ y⃠a⃠a⃠d⃠ e⃠y⃠ t⃠u⃠j⃠h⃠e⃠",
"T⃠u⃠ a⃠p⃠n⃠i⃠ M⃠a⃠a⃠ c⃠u⃠d⃠a⃠ n⃠a⃠ t⃠y⃠m⃠p⃠a⃠s⃠s⃠",
"O⃠y⃠e⃠ u⃠n⃠f⃠u⃠n⃠n⃠y⃠ s⃠w⃠i⃠p⃠e⃠ m⃠t⃠t⃠ k⃠r⃠",
"O⃠h⃠ h⃠e⃠l⃠l⃠o⃠ b⃠i⃠h⃠a⃠r⃠i⃠ t⃠e⃠r⃠a⃠ b⃠a⃠a⃠p⃠ b⃠i⃠h⃠a⃠r⃠i⃠ o⃠r⃠ t⃠u⃠ v⃠ b⃠i⃠h⃠a⃠r⃠i⃠ a⃠a⃠u⃠k⃠a⃠t⃠ m⃠e⃠ r⃠h⃠a⃠ k⃠r⃠.",
"O⃠y⃠y⃠ k⃠i⃠n⃠n⃠e⃠r⃠ t⃠u⃠j⃠h⃠e⃠ g⃠c⃠ m⃠e⃠ a⃠a⃠n⃠e⃠ k⃠i⃠ p⃠e⃠r⃠m⃠i⃠s⃠s⃠i⃠o⃠n⃠ k⃠i⃠s⃠n⃠e⃠ d⃠i⃠.",
"C⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"C⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠ e⃠k⃠ b⃠a⃠a⃠r⃠.",
"S⃠u⃠n⃠ s⃠u⃠n⃠ m⃠a⃠ c⃠u⃠d⃠a⃠.",
"T⃠e⃠r⃠i⃠ m⃠a⃠c⃠a⃠ b⃠h⃠o⃠s⃠d⃠a⃠.",
"O⃠y⃠e⃠ c⃠h⃠o⃠t⃠i⃠ j⃠a⃠t⃠i⃠ k⃠e⃠ t⃠m⃠r⃠.",
"K⃠y⃠? j⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ k⃠i⃠d⃠d⃠e⃠.",
"B⃠i⃠h⃠a⃠r⃠i⃠ c⃠o⃠m⃠ g⃠a⃠n⃠g⃠ k⃠e⃠ b⃠a⃠a⃠p⃠ k⃠o⃠ t⃠a⃠g⃠ c⃠r⃠e⃠g⃠a⃠ t⃠u⃠",
"M⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ t⃠u⃠ b⃠i⃠h⃠a⃠r⃠i⃠ e⃠y⃠ t⃠m⃠k⃠c⃠ b⃠s⃠",
"J⃠a⃠l⃠d⃠i⃠ s⃠e⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ p⃠a⃠p⃠a⃠ b⃠o⃠l⃠",
"S⃠i⃠d⃠e⃠ h⃠o⃠j⃠a⃠ b⃠i⃠h⃠a⃠r⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ a⃠b⃠",
"H⃠y⃠e⃠ p⃠g⃠l⃠ b⃠h⃠g⃠ m⃠a⃠t⃠ a⃠c⃠h⃠e⃠ s⃠e⃠ c⃠u⃠d⃠",
"b⃠h⃠g⃠ n⃠y⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ t⃠u⃠ a⃠j⃠j⃠",
"H⃠y⃠e⃠ p⃠g⃠l⃠ k⃠e⃠ b⃠c⃠h⃠e⃠ b⃠h⃠a⃠g⃠ m⃠a⃠t⃠",
"H⃠y⃠e⃠ d⃠u⃠r⃠ h⃠a⃠t⃠t⃠ m⃠a⃠d⃠h⃠c⃠h⃠o⃠d⃠ k⃠e⃠ b⃠a⃠c⃠h⃠e⃠",
"k⃠o⃠i⃠ b⃠a⃠t⃠ n⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠ e⃠s⃠l⃠i⃠y⃠e⃠ m⃠a⃠f⃠ c⃠r⃠ r⃠h⃠a⃠ h⃠u⃠ t⃠u⃠j⃠h⃠e⃠",
"k⃠o⃠i⃠ b⃠a⃠a⃠t⃠ n⃠y⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠ m⃠a⃠f⃠i⃠ d⃠e⃠ d⃠u⃠n⃠g⃠a⃠",
"A⃠c⃠h⃠e⃠ s⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠ m⃠a⃠f⃠i⃠ m⃠i⃠l⃠ j⃠a⃠y⃠e⃠g⃠i⃠ t⃠u⃠j⃠h⃠e⃠",
"a⃠p⃠n⃠i⃠ m⃠a⃠ m⃠a⃠t⃠ c⃠h⃠u⃠d⃠a⃠ m⃠u⃠j⃠e⃠ s⃠w⃠i⃠p⃠e⃠ c⃠r⃠k⃠e⃠",
"A⃠c⃠h⃠e⃠ s⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ s⃠w⃠i⃠p⃠e⃠ c⃠r⃠k⃠e⃠",
"F⃠r⃠ b⃠o⃠l⃠n⃠a⃠ n⃠a⃠ k⃠i⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ s⃠w⃠i⃠p⃠e⃠ c⃠r⃠k⃠e⃠",
"C⃠y⃠a⃠ h⃠u⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠ k⃠e⃠s⃠e⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠",
"m⃠u⃠j⃠h⃠e⃠ p⃠t⃠a⃠ t⃠h⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"m⃠e⃠y⃠ n⃠y⃠ m⃠a⃠n⃠t⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠ r⃠n⃠d⃠y⃠",
"l⃠o⃠d⃠e⃠ s⃠e⃠ u⃠t⃠r⃠ m⃠c⃠",
"l⃠u⃠n⃠ m⃠t⃠ c⃠h⃠u⃠s⃠ m⃠e⃠r⃠a⃠",
"n⃠i⃠k⃠a⃠l⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠d⃠",
"c⃠h⃠u⃠p⃠ o⃠y⃠e⃠ g⃠a⃠s⃠h⃠t⃠i⃠ k⃠ b⃠a⃠c⃠h⃠e⃠",
"m⃠a⃠k⃠i⃠c⃠h⃠u⃠t⃠ t⃠e⃠r⃠i⃠",
"c⃠h⃠u⃠p⃠ r⃠n⃠d⃠y⃠k⃠e⃠",
"m⃠a⃠ r⃠n⃠d⃠y⃠ t⃠e⃠r⃠i⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠ k⃠ h⃠a⃠t⃠h⃠ t⃠o⃠d⃠h⃠ k⃠ t⃠e⃠r⃠e⃠ b⃠a⃠a⃠p⃠ k⃠ m⃠u⃠h⃠ m⃠e⃠ f⃠a⃠s⃠a⃠d⃠u⃠n⃠g⃠a⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"l⃠e⃠a⃠v⃠e⃠ l⃠e⃠ t⃠u⃠ r⃠n⃠d⃠y⃠k⃠e⃠ p⃠a⃠s⃠a⃠n⃠d⃠ n⃠a⃠i⃠ a⃠y⃠a⃠ m⃠e⃠k⃠o⃠",
"l⃠e⃠a⃠v⃠e⃠ l⃠e⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ i⃠d⃠e⃠r⃠ s⃠e⃠",
"L⃠e⃠a⃠v⃠e⃠ l⃠e⃠ j⃠l⃠d⃠i⃠ s⃠e⃠ w⃠r⃠n⃠a⃠ m⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"L⃠e⃠a⃠v⃠e⃠ n⃠y⃠ l⃠e⃠g⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"S⃠m⃠j⃠h⃠ b⃠a⃠t⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ l⃠e⃠a⃠v⃠e⃠ l⃠e⃠",
"f⃠a⃠s⃠t⃠ l⃠e⃠a⃠v⃠e⃠ l⃠e⃠ k⃠a⃠m⃠j⃠o⃠r⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"t⃠u⃠t⃠o⃠ c⃠h⃠u⃠p⃠ r⃠n⃠d⃠y⃠k⃠",
"o⃠y⃠ h⃠i⃠j⃠d⃠e⃠ k⃠h⃠a⃠n⃠a⃠ k⃠h⃠a⃠ k⃠e⃠ a⃠a⃠ k⃠a⃠m⃠z⃠o⃠r⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠k⃠o⃠ i⃠l⃠y⃠ r⃠e⃠y⃠🌚😂",
"c⃠h⃠u⃠p⃠ c⃠h⃠a⃠p⃠ c⃠h⃠u⃠d⃠ t⃠m⃠k⃠c⃠",
"c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠",
"s⃠h⃠i⃠ s⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠ t⃠u⃠ c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠",
"f⃠r⃠ s⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠",
"s⃠h⃠i⃠ s⃠e⃠ l⃠i⃠k⃠h⃠ w⃠r⃠n⃠a⃠ m⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"m⃠a⃠ c⃠y⃠u⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ c⃠h⃠u⃠p⃠c⃠h⃠a⃠p⃠",
"p⃠r⃠o⃠o⃠f⃠ c⃠r⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠o⃠o⃠f⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"p⃠r⃠o⃠o⃠f⃠ h⃠o⃠ c⃠h⃠u⃠k⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"C⃠h⃠u⃠p⃠ c⃠h⃠i⃠l⃠l⃠a⃠r⃠",
"c⃠h⃠u⃠p⃠ c⃠h⃠u⃠p⃠ m⃠a⃠a⃠ k⃠ b⃠o⃠s⃠d⃠a⃠ t⃠e⃠r⃠y⃠",
"o⃠y⃠ h⃠i⃠j⃠d⃠e⃠ k⃠h⃠a⃠n⃠a⃠ k⃠h⃠a⃠ k⃠e⃠ a⃠a⃠ k⃠a⃠m⃠z⃠o⃠r⃠",
"c⃠h⃠u⃠p⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠o⃠d⃠ ?",
"A⃠b⃠ t⃠k⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ h⃠o⃠g⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ ?",
"n⃠y⃠ n⃠y⃠ m⃠e⃠ k⃠u⃠c⃠h⃠ n⃠y⃠ j⃠a⃠n⃠t⃠a⃠ b⃠s⃠ t⃠e⃠r⃠i⃠ m⃠a⃠ r⃠n⃠d⃠y⃠ e⃠y⃠",
"S⃠b⃠s⃠e⃠ p⃠h⃠e⃠l⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠a⃠ k⃠o⃠ b⃠o⃠l⃠ c⃠h⃠u⃠d⃠n⃠a⃠ k⃠a⃠a⃠m⃠ k⃠r⃠e⃠",
"Y⃠a⃠h⃠a⃠ b⃠h⃠i⃠ c⃠h⃠u⃠d⃠a⃠ t⃠u⃠ r⃠n⃠d⃠y⃠c⃠e⃠ p⃠i⃠l⃠l⃠e⃠",
"t⃠e⃠r⃠i⃠m⃠a⃠k⃠a⃠b⃠o⃠s⃠d⃠a⃠",
"t⃠e⃠r⃠i⃠ t⃠o⃠ b⃠h⃠e⃠n⃠ c⃠u⃠d⃠e⃠g⃠i⃠",
"c⃠h⃠u⃠p⃠ r⃠n⃠d⃠y⃠k⃠e⃠ t⃠o⃠m⃠m⃠y⃠",
"n⃠i⃠k⃠a⃠l⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠d⃠ c⃠u⃠d⃠k⃠e⃠ y⃠h⃠a⃠ s⃠e⃠",
"c⃠o⃠z⃠ t⃠e⃠r⃠i⃠ m⃠a⃠ a⃠n⃠d⃠h⃠i⃠ r⃠a⃠n⃠d⃠i⃠ h⃠e⃠",
"n⃠y⃠t⃠o⃠ b⃠a⃠a⃠p⃠ b⃠o⃠l⃠ m⃠u⃠j⃠h⃠e⃠",
"n⃠y⃠n⃠y⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ h⃠o⃠g⃠i⃠ r⃠n⃠d⃠i⃠i⃠ j⃠o⃠ c⃠h⃠u⃠d⃠w⃠a⃠t⃠i⃠ j⃠o⃠g⃠i⃠",
"t⃠r⃠y⃠ a⃠m⃠m⃠i⃠ c⃠e⃠ b⃠h⃠o⃠s⃠d⃠e⃠ m⃠e⃠ e⃠m⃠o⃠j⃠i⃠ d⃠a⃠l⃠ m⃠c⃠",
"c⃠y⃠a⃠ ? c⃠h⃠m⃠r⃠ c⃠h⃠u⃠d⃠ g⃠y⃠a⃠ c⃠y⃠a⃠ ?",
"t⃠m⃠ c⃠h⃠u⃠d⃠r⃠i⃠ h⃠o⃠g⃠i⃠ f⃠r⃠r⃠t⃠o⃠",
"c⃠y⃠a⃠ ? k⃠b⃠ ? p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ r⃠n⃠d⃠k⃠e⃠k⃠",
"c⃠y⃠a⃠ s⃠c⃠h⃠ m⃠e⃠y⃠ p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠u⃠d⃠w⃠a⃠ l⃠i⃠ t⃠u⃠n⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠",
"i⃠t⃠n⃠a⃠ s⃠c⃠h⃠ n⃠y⃠ b⃠o⃠l⃠ m⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"s⃠c⃠h⃠ m⃠e⃠y⃠ p⃠g⃠l⃠ e⃠y⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ l⃠i⃠a⃠ m⃠e⃠r⃠e⃠ s⃠t⃠h⃠",
"m⃠t⃠l⃠b⃠ t⃠m⃠r⃠",
"n⃠y⃠t⃠o⃠",
"p⃠u⃠r⃠a⃠ l⃠i⃠k⃠h⃠ m⃠c⃠",
"t⃠m⃠r⃠ f⃠r⃠r⃠t⃠o⃠",
"o⃠h⃠ o⃠k⃠ c⃠u⃠d⃠l⃠e⃠ f⃠i⃠r⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠a⃠ d⃠a⃠m⃠a⃠d⃠",
"c⃠y⃠a⃠ ? a⃠c⃠h⃠e⃠ s⃠e⃠ l⃠i⃠k⃠h⃠e⃠ p⃠e⃠h⃠l⃠e⃠ r⃠n⃠d⃠i⃠k⃠e⃠b⃠a⃠c⃠h⃠e⃠",
"n⃠y⃠t⃠o⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠n⃠e⃠ m⃠e⃠ v⃠y⃠a⃠s⃠t⃠ h⃠u⃠",
"n⃠y⃠t⃠o⃠ p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ k⃠u⃠c⃠h⃠ b⃠i⃠",
"o⃠y⃠e⃠e⃠ c⃠y⃠a⃠ ? c⃠h⃠u⃠d⃠ g⃠y⃠a⃠ ?",
"c⃠h⃠u⃠d⃠ m⃠t⃠ h⃠s⃠s⃠",
"y⃠u⃠r⃠ r⃠n⃠d⃠i⃠i⃠ m⃠o⃠m⃠",
"a⃠r⃠e⃠ s⃠b⃠k⃠i⃠ m⃠a⃠a⃠ r⃠n⃠d⃠i⃠i⃠ o⃠r⃠ t⃠e⃠r⃠i⃠ b⃠i⃠",
"a⃠r⃠e⃠ i⃠d⃠a⃠r⃠ c⃠u⃠d⃠l⃠e⃠ e⃠k⃠ b⃠a⃠a⃠r⃠",
"t⃠r⃠i⃠ m⃠a⃠a⃠ c⃠i⃠ t⃠r⃠h⃠",
"e⃠k⃠ l⃠i⃠n⃠e⃠ m⃠e⃠ t⃠m⃠r⃠",
"Q⃠",
"o⃠c⃠y⃠ a⃠b⃠ c⃠h⃠u⃠d⃠l⃠e⃠",
"p⃠e⃠h⃠e⃠l⃠e⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠u⃠",
"n⃠y⃠t⃠o⃠",
"q⃠ ?",
"h⃠y⃠y⃠y⃠ c⃠h⃠u⃠d⃠ k⃠e⃠ d⃠i⃠k⃠a⃠ e⃠k⃠ b⃠a⃠a⃠r⃠",
"o⃠y⃠e⃠e⃠ s⃠u⃠n⃠ d⃠o⃠s⃠t⃠ t⃠m⃠r⃠",
"b⃠h⃠a⃠g⃠ j⃠a⃠ r⃠a⃠a⃠n⃠d⃠ m⃠a⃠a⃠f⃠ c⃠r⃠r⃠ d⃠u⃠n⃠g⃠a⃠",
"o⃠y⃠e⃠e⃠ p⃠g⃠l⃠ r⃠n⃠d⃠i⃠i⃠ i⃠d⃠a⃠r⃠ a⃠a⃠",
"c⃠y⃠a⃠ t⃠m⃠r⃠ f⃠r⃠r⃠t⃠o⃠",
"o⃠y⃠e⃠e⃠ i⃠d⃠a⃠r⃠ a⃠a⃠k⃠e⃠ c⃠h⃠u⃠d⃠ l⃠e⃠ c⃠h⃠m⃠r⃠",
"n⃠y⃠t⃠o⃠ a⃠e⃠s⃠e⃠ h⃠i⃠ c⃠u⃠d⃠",
"o⃠y⃠e⃠e⃠ h⃠y⃠y⃠ a⃠i⃠s⃠e⃠ h⃠i⃠ c⃠u⃠d⃠ l⃠e⃠n⃠a⃠",
"o⃠r⃠ c⃠h⃠u⃠d⃠ l⃠e⃠",
"c⃠h⃠u⃠d⃠ k⃠e⃠ d⃠i⃠k⃠a⃠ o⃠r⃠",
"h⃠y⃠y⃠ c⃠h⃠u⃠d⃠o⃠ n⃠a⃠",
"c⃠h⃠u⃠d⃠o⃠ m⃠t⃠ b⃠h⃠a⃠g⃠ j⃠a⃠o⃠",
"b⃠y⃠y⃠e⃠e⃠ h⃠y⃠y⃠ c⃠y⃠a⃠ ?",
"Q⃠c⃠h⃠u⃠d⃠ q⃠ r⃠h⃠e⃠ h⃠o⃠ ?",
"p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ m⃠c⃠",
"c⃠h⃠u⃠d⃠ m⃠t⃠",
"c⃠y⃠a⃠ p⃠g⃠l⃠ r⃠n⃠d⃠i⃠i⃠ i⃠d⃠a⃠r⃠ a⃠a⃠",
"t⃠e⃠r⃠i⃠ a⃠m⃠m⃠i⃠ c⃠e⃠ b⃠h⃠o⃠s⃠d⃠e⃠ m⃠e⃠ c⃠h⃠a⃠p⃠p⃠a⃠l⃠",
"o⃠y⃠e⃠e⃠ i⃠d⃠a⃠r⃠ a⃠a⃠ m⃠c⃠",
"k⃠m⃠z⃠r⃠o⃠r⃠ e⃠y⃠ c⃠y⃠a⃠ r⃠n⃠d⃠i⃠e⃠k⃠",
"c⃠y⃠a⃠ l⃠i⃠k⃠h⃠ r⃠h⃠a⃠ ?",
"c⃠h⃠u⃠d⃠ t⃠h⃠a⃠ c⃠y⃠a⃠ ?",
"o⃠y⃠e⃠e⃠ s⃠l⃠i⃠d⃠e⃠ l⃠e⃠k⃠e⃠ b⃠a⃠a⃠t⃠ c⃠r⃠m⃠c⃠",
"i⃠d⃠a⃠r⃠ a⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠u⃠",
"o⃠y⃠e⃠e⃠ c⃠p⃠ m⃠t⃠ c⃠r⃠r⃠ c⃠h⃠u⃠d⃠l⃠e⃠",
"o⃠y⃠e⃠e⃠ h⃠y⃠y⃠ c⃠h⃠u⃠d⃠ k⃠e⃠ d⃠i⃠k⃠a⃠",
"i⃠d⃠a⃠r⃠ a⃠a⃠ t⃠r⃠y⃠ m⃠a⃠ s⃠c⃠h⃠o⃠f⃠u⃠ k⃠h⃠a⃠c⃠h⃠a⃠r⃠ k⃠h⃠a⃠c⃠h⃠a⃠r⃠",
"i⃠d⃠a⃠r⃠ a⃠a⃠ j⃠a⃠ m⃠c⃠",
"h⃠y⃠y⃠ i⃠d⃠a⃠r⃠ a⃠a⃠k⃠e⃠ c⃠h⃠u⃠d⃠l⃠e⃠",
"o⃠y⃠e⃠e⃠ k⃠m⃠z⃠o⃠r⃠ m⃠c⃠ i⃠d⃠a⃠r⃠ a⃠a⃠",
"y⃠e⃠ c⃠y⃠a⃠ t⃠m⃠r⃠",
"o⃠y⃠e⃠e⃠ n⃠y⃠ c⃠p⃠ n⃠y⃠ c⃠r⃠r⃠",
"o⃠y⃠e⃠e⃠ p⃠g⃠l⃠ m⃠t⃠ c⃠r⃠r⃠",
"c⃠u⃠d⃠l⃠e⃠ a⃠r⃠a⃠m⃠ s⃠e⃠ m⃠c⃠",
"p⃠g⃠l⃠ e⃠y⃠ c⃠y⃠a⃠ r⃠n⃠d⃠i⃠e⃠k⃠",
"c⃠p⃠ c⃠r⃠c⃠e⃠ c⃠h⃠u⃠d⃠e⃠g⃠a⃠ !",
"b⃠a⃠a⃠p⃠ ? m⃠c⃠ m⃠e⃠r⃠a⃠ c⃠o⃠i⃠ m⃠a⃠ b⃠a⃠a⃠p⃠ n⃠y⃠ e⃠y⃠ m⃠a⃠i⃠ u⃠p⃠a⃠r⃠ s⃠e⃠ r⃠o⃠c⃠k⃠e⃠t⃠ p⃠e⃠ b⃠e⃠t⃠h⃠ c⃠e⃠ b⃠s⃠s⃠ t⃠e⃠r⃠i⃠ m⃠a⃠ c⃠h⃠o⃠d⃠n⃠e⃠ a⃠y⃠a⃠ h⃠u⃠",
"C⃠h⃠o⃠t⃠a⃠ l⃠i⃠k⃠h⃠ r⃠n⃠d⃠i⃠ k⃠ b⃠a⃠c⃠h⃠e⃠",
"C⃠h⃠o⃠t⃠a⃠ l⃠i⃠k⃠h⃠a⃠ w⃠r⃠n⃠a⃠ t⃠r⃠y⃠ m⃠a⃠ r⃠n⃠d⃠y⃠",
"T⃠r⃠y⃠ m⃠a⃠ b⃠a⃠k⃠a⃠ c⃠o⃠d⃠e⃠g⃠a⃠",
"T⃠m⃠k⃠c⃠ m⃠a⃠i⃠n⃠ b⃠u⃠r⃠f⃠",
"B⃠h⃠i⃠k⃠a⃠r⃠i⃠ k⃠i⃠ j⃠h⃠a⃠t⃠ m⃠a⃠ c⃠u⃠d⃠a⃠ l⃠e⃠",
"C⃠h⃠o⃠d⃠k⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ m⃠a⃠r⃠j⃠a⃠y⃠e⃠g⃠i⃠",
"T⃠m⃠k⃠c⃠ m⃠a⃠i⃠n⃠ M⃠o⃠u⃠n⃠t⃠ E⃠v⃠e⃠r⃠e⃠s⃠t⃠",
"M⃠u⃠h⃠ m⃠e⃠y⃠ l⃠e⃠g⃠a⃠ l⃠u⃠n⃠d⃠ m⃠e⃠r⃠a⃠",
"H⃠i⃠j⃠d⃠e⃠ k⃠i⃠ j⃠h⃠a⃠t⃠ c⃠h⃠u⃠p⃠ w⃠r⃠n⃠a⃠ t⃠r⃠y⃠ m⃠a⃠ r⃠n⃠d⃠i⃠",
"M⃠e⃠n⃠u⃠ n⃠y⃠ p⃠t⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠",
"M⃠e⃠n⃠u⃠ k⃠i⃠ p⃠t⃠a⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"M⃠e⃠n⃠u⃠ p⃠t⃠a⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"M⃠e⃠n⃠u⃠ s⃠b⃠ p⃠t⃠a⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"M⃠e⃠n⃠u⃠ p⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠",
"R⃠a⃠n⃠d⃠y⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠ m⃠e⃠n⃠u⃠ p⃠t⃠a⃠",
"T⃠e⃠n⃠u⃠ o⃠r⃠ m⃠e⃠n⃠u⃠ p⃠t⃠a⃠ e⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"B⃠s⃠ b⃠s⃠ m⃠a⃠a⃠ c⃠u⃠d⃠w⃠a⃠ a⃠p⃠n⃠i⃠",
"B⃠s⃠ b⃠s⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠ t⃠h⃠n⃠k⃠s⃠s⃠",
"B⃠s⃠ b⃠s⃠ c⃠h⃠u⃠d⃠w⃠a⃠ l⃠i⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ m⃠a⃠a⃠",
"B⃠s⃠ b⃠s⃠ k⃠a⃠m⃠j⃠o⃠r⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"S⃠m⃠j⃠h⃠ g⃠y⃠a⃠ a⃠p⃠n⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠b⃠",
"s⃠m⃠j⃠h⃠ g⃠y⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"s⃠m⃠j⃠h⃠ g⃠y⃠a⃠ t⃠u⃠ s⃠a⃠b⃠i⃠t⃠ k⃠r⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"C⃠y⃠a⃠ h⃠u⃠a⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"E⃠a⃠s⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ t⃠u⃠",
"E⃠a⃠s⃠y⃠ w⃠8⃠ m⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ a⃠b⃠",
"S⃠a⃠n⃠s⃠ a⃠r⃠i⃠ h⃠a⃠ k⃠y⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠g⃠i⃠ a⃠j⃠j⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠o⃠ b⃠i⃠n⃠a⃠ s⃠a⃠n⃠s⃠s⃠ l⃠e⃠t⃠e⃠ h⃠u⃠e⃠ c⃠h⃠o⃠d⃠u⃠n⃠g⃠a⃠",
"c⃠h⃠u⃠p⃠ r⃠a⃠n⃠d⃠i⃠k⃠e⃠ k⃠a⃠m⃠j⃠o⃠r⃠",
"a⃠p⃠n⃠i⃠ m⃠a⃠ n⃠o⃠r⃠m⃠i⃠e⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠ t⃠u⃠",
"f⃠r⃠ c⃠y⃠a⃠ n⃠o⃠r⃠m⃠i⃠e⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"b⃠a⃠s⃠ t⃠h⃠e⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ r⃠a⃠n⃠d⃠y⃠",
"b⃠a⃠s⃠ t⃠h⃠e⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠",
"k⃠a⃠m⃠j⃠o⃠r⃠ t⃠h⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ e⃠s⃠l⃠i⃠y⃠e⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"M⃠a⃠i⃠ s⃠b⃠ j⃠a⃠n⃠t⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"c⃠h⃠l⃠ c⃠h⃠l⃠ h⃠t⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠",
"f⃠r⃠ k⃠a⃠i⃠s⃠e⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠",
"m⃠a⃠a⃠ t⃠e⃠r⃠y⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"b⃠a⃠s⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"f⃠r⃠ r⃠a⃠n⃠d⃠y⃠ m⃠a⃠ t⃠e⃠r⃠y⃠ e⃠y⃠",
"K⃠a⃠m⃠j⃠o⃠r⃠ m⃠a⃠ k⃠a⃠ b⃠c⃠h⃠a⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"b⃠h⃠o⃠t⃠ g⃠n⃠d⃠i⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠ k⃠a⃠i⃠s⃠e⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ i⃠t⃠n⃠a⃠ g⃠n⃠d⃠a⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ b⃠t⃠a⃠ r⃠h⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ p⃠t⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ t⃠e⃠r⃠y⃠",
"f⃠i⃠r⃠ m⃠u⃠j⃠h⃠e⃠ n⃠y⃠ p⃠t⃠a⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠t⃠a⃠ n⃠y⃠ k⃠o⃠n⃠ c⃠o⃠d⃠ d⃠i⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ k⃠o⃠",
"r⃠u⃠k⃠ a⃠a⃠y⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠o⃠d⃠k⃠e⃠",
"w⃠a⃠i⃠t⃠ c⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠o⃠d⃠ r⃠h⃠a⃠ h⃠u⃠",
"w⃠a⃠i⃠t⃠ c⃠r⃠ r⃠a⃠b⃠d⃠y⃠k⃠e⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ r⃠h⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"w⃠a⃠i⃠t⃠ k⃠r⃠ s⃠m⃠j⃠h⃠ r⃠h⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠o⃠d⃠k⃠e⃠",
"w⃠a⃠i⃠t⃠ l⃠e⃠ t⃠h⃠o⃠d⃠a⃠ c⃠h⃠o⃠d⃠n⃠e⃠ d⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"r⃠u⃠k⃠ j⃠a⃠ a⃠a⃠n⃠d⃠ r⃠k⃠h⃠ d⃠u⃠n⃠g⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ l⃠i⃠y⃠e⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ f⃠a⃠m⃠o⃠u⃠s⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"m⃠a⃠a⃠n⃠ l⃠i⃠a⃠ m⃠e⃠n⃠e⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ s⃠a⃠l⃠i⃠ t⃠e⃠r⃠y⃠",
"m⃠a⃠a⃠n⃠ l⃠i⃠a⃠ m⃠a⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"s⃠h⃠a⃠n⃠t⃠ b⃠e⃠t⃠h⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"s⃠h⃠a⃠n⃠t⃠ b⃠e⃠t⃠h⃠k⃠e⃠ c⃠h⃠u⃠d⃠w⃠a⃠ l⃠e⃠ a⃠p⃠n⃠i⃠ m⃠a⃠k⃠o⃠ t⃠u⃠",
"f⃠r⃠ s⃠e⃠ s⃠h⃠a⃠n⃠t⃠ B⃠e⃠t⃠h⃠ t⃠u⃠ c⃠u⃠d⃠ a⃠b⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ y⃠h⃠a⃠",
"m⃠e⃠r⃠e⃠ s⃠m⃠j⃠h⃠ n⃠y⃠ a⃠y⃠a⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ t⃠e⃠r⃠y⃠",
"L⃠e⃠ k⃠e⃠l⃠a⃠ K⃠h⃠a⃠ t⃠u⃠ m⃠a⃠d⃠a⃠r⃠c⃠h⃠o⃠d⃠",
"H⃠y⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠y⃠i⃠ c⃠y⃠a⃠",
"h⃠y⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ m⃠a⃠r⃠ g⃠a⃠i⃠ c⃠y⃠a⃠",
"H⃠y⃠e⃠ s⃠c⃠h⃠ b⃠t⃠a⃠ c⃠o⃠m⃠ c⃠o⃠d⃠ d⃠i⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"C⃠h⃠l⃠ c⃠h⃠o⃠d⃠ d⃠i⃠a⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠o⃠ s⃠m⃠j⃠h⃠l⃠e⃠",
"B⃠a⃠k⃠i⃠ k⃠o⃠i⃠ d⃠i⃠k⃠k⃠a⃠t⃠ n⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"b⃠a⃠k⃠i⃠ s⃠b⃠ j⃠a⃠n⃠t⃠e⃠ e⃠y⃠ k⃠i⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠d⃠k⃠a⃠d⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ p⃠t⃠a⃠ t⃠h⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠n⃠e⃠ w⃠l⃠i⃠ e⃠y⃠",
"p⃠r⃠ m⃠e⃠i⃠ k⃠a⃠i⃠s⃠e⃠ j⃠n⃠t⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ k⃠o⃠ k⃠o⃠i⃠ c⃠h⃠o⃠d⃠ d⃠i⃠a⃠",
"p⃠r⃠ m⃠e⃠r⃠a⃠ v⃠i⃠ m⃠a⃠n⃠n⃠a⃠ s⃠h⃠i⃠ t⃠h⃠a⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"p⃠r⃠ w⃠o⃠ g⃠l⃠t⃠ n⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠",
"p⃠r⃠ w⃠o⃠ s⃠h⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠d⃠k⃠a⃠d⃠ e⃠y⃠",
"p⃠r⃠ k⃠a⃠i⃠s⃠e⃠ k⃠i⃠a⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ o⃠m⃠f⃠o⃠o⃠",
"b⃠u⃠r⃠ c⃠h⃠e⃠e⃠r⃠ d⃠u⃠n⃠g⃠a⃠ t⃠r⃠i⃠ m⃠a⃠ k⃠a⃠",
"t⃠e⃠r⃠i⃠ m⃠a⃠ k⃠e⃠ d⃠i⃠l⃠ m⃠e⃠ l⃠o⃠d⃠a⃠ m⃠a⃠r⃠k⃠e⃠ u⃠s⃠k⃠i⃠ d⃠h⃠a⃠d⃠k⃠a⃠n⃠ r⃠o⃠k⃠ d⃠u⃠n⃠g⃠a⃠",
"l⃠u⃠l⃠l⃠e⃠ k⃠h⃠a⃠ t⃠r⃠i⃠ m⃠a⃠k⃠a⃠b⃠h⃠o⃠s⃠d⃠a⃠",
"t⃠r⃠i⃠ b⃠h⃠n⃠ k⃠i⃠ b⃠h⃠o⃠s⃠d⃠i⃠ b⃠e⃠t⃠a⃠",
"t⃠r⃠i⃠ m⃠a⃠ r⃠n⃠d⃠i⃠ b⃠a⃠a⃠t⃠ k⃠h⃠t⃠m⃠",
"S⃠u⃠n⃠ e⃠k⃠ m⃠a⃠z⃠e⃠ k⃠i⃠ b⃠a⃠a⃠t⃠ b⃠a⃠t⃠a⃠o⃠ k⃠y⃠a⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠y⃠ e⃠y⃠"
"c⃠o⃠d⃠u⃠ c⃠o⃠d⃠u⃠ m⃠a⃠k⃠o⃠ t⃠e⃠r⃠y⃠",
"a⃠j⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ o⃠y⃠e⃠",
"s⃠u⃠n⃠ s⃠u⃠n⃠ r⃠a⃠n⃠d⃠y⃠ m⃠a⃠k⃠e⃠ b⃠a⃠c⃠h⃠e⃠ t⃠u⃠",
"k⃠i⃠l⃠a⃠s⃠ n⃠y⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"m⃠u⃠j⃠h⃠e⃠ c⃠y⃠a⃠ p⃠t⃠a⃠ t⃠e⃠r⃠y⃠ b⃠h⃠e⃠n⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"p⃠r⃠ p⃠r⃠ c⃠y⃠a⃠ h⃠o⃠t⃠e⃠ e⃠y⃠ t⃠m⃠k⃠c⃠",
"t⃠m⃠c⃠l⃠ s⃠u⃠n⃠l⃠e⃠",
"m⃠o⃠o⃠t⃠ d⃠u⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ m⃠e⃠y⃠",
"b⃠h⃠g⃠n⃠y⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠ f⃠r⃠",
"f⃠r⃠ s⃠e⃠ c⃠u⃠d⃠l⃠e⃠ t⃠u⃠",
"y⃠e⃠ v⃠i⃠ s⃠h⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠k⃠c⃠ b⃠s⃠",
"a⃠j⃠ k⃠u⃠c⃠h⃠ n⃠y⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"t⃠r⃠y⃠ k⃠r⃠ m⃠e⃠r⃠a⃠ l⃠u⃠n⃠d⃠ c⃠h⃠u⃠s⃠k⃠e⃠",
"t⃠o⃠r⃠m⃠a⃠k⃠i⃠b⃠u⃠r⃠ s⃠u⃠n⃠",
"t⃠o⃠r⃠ m⃠a⃠k⃠i⃠ f⃠u⃠d⃠d⃠i⃠ o⃠y⃠e⃠",
"H⃠a⃠y⃠e⃠ H⃠a⃠y⃠e⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"o⃠y⃠e⃠ l⃠u⃠n⃠d⃠k⃠e⃠ p⃠a⃠s⃠i⃠n⃠e⃠..",
"k⃠u⃠t⃠t⃠e⃠ k⃠e⃠ t⃠a⃠t⃠t⃠e⃠ s⃠u⃠n⃠",
"k⃠u⃠t⃠t⃠a⃠ j⃠a⃠i⃠s⃠a⃠ c⃠u⃠d⃠ r⃠h⃠a⃠ t⃠u⃠",
"M⃠u⃠h⃠ m⃠e⃠i⃠ l⃠e⃠ m⃠e⃠r⃠a⃠..",
"j⃠h⃠a⃠a⃠t⃠ k⃠e⃠ p⃠i⃠s⃠s⃠u⃠ s⃠u⃠n⃠ t⃠m⃠k⃠c⃠",
"H⃠a⃠h⃠a⃠h⃠h⃠a⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠",
"w⃠e⃠a⃠k⃠ t⃠a⃠t⃠t⃠e⃠ u⃠t⃠h⃠",
"w⃠e⃠a⃠k⃠ e⃠y⃠ t⃠u⃠ c⃠u⃠d⃠ r⃠h⃠a⃠",
"w⃠e⃠a⃠k⃠ a⃠c⃠h⃠e⃠ s⃠e⃠ c⃠u⃠d⃠ t⃠u⃠",
"w⃠e⃠a⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ r⃠h⃠i⃠ d⃠e⃠k⃠h⃠",
"w⃠e⃠e⃠k⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ a⃠b⃠",
"m⃠u⃠j⃠h⃠e⃠ n⃠y⃠ r⃠o⃠k⃠ t⃠u⃠ w⃠e⃠a⃠k⃠ e⃠y⃠",
"c⃠h⃠u⃠p⃠ h⃠i⃠z⃠d⃠e⃠",
"o⃠k⃠a⃠t⃠ n⃠y⃠ m⃠e⃠r⃠i⃠ m⃠a⃠ c⃠u⃠d⃠w⃠a⃠ t⃠u⃠ a⃠p⃠n⃠i⃠",
"l⃠u⃠n⃠ l⃠e⃠g⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ g⃠a⃠n⃠d⃠ m⃠e⃠i⃠ ?",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ b⃠a⃠c⃠h⃠i⃠ c⃠o⃠d⃠u⃠..",
"t⃠e⃠r⃠y⃠ b⃠h⃠e⃠n⃠ k⃠i⃠ c⃠h⃠u⃠t⃠ a⃠j⃠ f⃠a⃠d⃠ d⃠u⃠",
"s⃠p⃠e⃠e⃠d⃠ l⃠e⃠k⃠r⃠ a⃠a⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"s⃠p⃠e⃠e⃠d⃠ n⃠y⃠ t⃠e⃠r⃠e⃠ a⃠n⃠d⃠r⃠ w⃠e⃠a⃠k⃠ p⃠r⃠o⃠s⃠n⃠",
"u⃠g⃠l⃠y⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠h⃠u⃠p⃠",
"m⃠a⃠k⃠a⃠f⃠u⃠d⃠d⃠a⃠t⃠e⃠r⃠y⃠",
"t⃠e⃠r⃠a⃠ b⃠a⃠a⃠p⃠ k⃠o⃠ t⃠a⃠g⃠ k⃠r⃠..?",
"a⃠c⃠h⃠e⃠ s⃠e⃠ t⃠a⃠g⃠ k⃠r⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠h⃠a⃠g⃠w⃠n⃠ k⃠o⃠..",
"c⃠u⃠d⃠k⃠e⃠ p⃠g⃠l⃠ n⃠y⃠ h⃠o⃠ t⃠u⃠",
"c⃠u⃠d⃠k⃠e⃠ p⃠g⃠l⃠ h⃠o⃠ r⃠h⃠a⃠ t⃠u⃠ k⃠i⃠d⃠",
"m⃠a⃠ t⃠o⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ h⃠a⃠w⃠a⃠b⃠z⃠i⃠ c⃠r⃠..",
"b⃠s⃠ m⃠a⃠ c⃠o⃠d⃠n⃠i⃠ e⃠y⃠ t⃠e⃠r⃠y⃠",
"t⃠o⃠w⃠n⃠ m⃠e⃠i⃠ c⃠u⃠d⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ l⃠e⃠k⃠r⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠ s⃠e⃠x⃠y⃠ k⃠o⃠ b⃠e⃠j⃠ - r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠h⃠g⃠w⃠n⃠ p⃠e⃠",
"s⃠p⃠e⃠e⃠d⃠ p⃠k⃠d⃠ c⃠p⃠ n⃠y⃠ k⃠r⃠",
"T⃠r⃠y⃠ m⃠a⃠ r⃠e⃠n⃠d⃠y⃠",
"B⃠h⃠k⃠k⃠ c⃠u⃠d⃠",
"t⃠e⃠y⃠ m⃠a⃠a⃠ r⃠n⃠d⃠i⃠",
"t⃠e⃠r⃠y⃠ b⃠e⃠h⃠e⃠n⃠ r⃠a⃠n⃠d⃠i⃠",
"C⃠u⃠d⃠ j⃠a⃠",
"t⃠e⃠r⃠y⃠ d⃠i⃠d⃠i⃠ r⃠n⃠d⃠i⃠",
"S⃠l⃠o⃠w⃠",
"t⃠e⃠r⃠i⃠ M⃠a⃠i⃠y⃠a⃠ c⃠i⃠o⃠d⃠u⃠",
"B⃠h⃠a⃠g⃠?",
"B⃠h⃠a⃠k⃠ c⃠u⃠d⃠",
"T⃠m⃠a⃠ c⃠o⃠d⃠u⃠",
"S⃠l⃠o⃠w⃠",
"S⃠l⃠o⃠w⃠ f⃠i⃠r⃠s⃠e⃠",
"C⃠u⃠d⃠g⃠r⃠i⃠b⃠",
"T⃠r⃠y⃠ m⃠a⃠ d⃠o⃠u⃠",
"t⃠b⃠k⃠c⃠ c⃠o⃠d⃠u⃠",
"N⃠e⃠t⃠ o⃠n⃠ o⃠f⃠f⃠ w⃠a⃠l⃠i⃠ r⃠n⃠d⃠y⃠",
"O⃠y⃠e⃠ t⃠r⃠y⃠ m⃠a⃠ c⃠o⃠d⃠u⃠",
"I⃠d⃠h⃠a⃠r⃠ a⃠a⃠k⃠e⃠ c⃠u⃠d⃠ c⃠h⃠u⃠p⃠ c⃠h⃠a⃠a⃠p⃠",
"t⃠b⃠k⃠c⃠ m⃠r⃠d⃠u⃠",
"o⃠i⃠ m⃠a⃠a⃠k⃠e⃠ l⃠o⃠d⃠e⃠e⃠",
"r⃠a⃠n⃠d⃠y⃠k⃠e⃠ b⃠e⃠e⃠j⃠",
"t⃠m⃠k⃠c⃠ c⃠h⃠o⃠d⃠u⃠",
"s⃠u⃠a⃠r⃠ k⃠e⃠ b⃠e⃠e⃠j⃠",
"n⃠e⃠t⃠ o⃠f⃠f⃠ o⃠n⃠ k⃠r⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ l⃠a⃠d⃠k⃠e⃠",
"T⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠i⃠ k⃠e⃠s⃠e⃠",
"C⃠h⃠u⃠p⃠ s⃠l⃠o⃠w⃠ m⃠a⃠d⃠h⃠a⃠r⃠c⃠o⃠d⃠",
"t⃠b⃠k⃠c⃠ c⃠o⃠d⃠u⃠ k⃠r⃠ m⃠s⃠g⃠ d⃠e⃠l⃠e⃠t⃠e⃠",
"o⃠i⃠ s⃠u⃠a⃠r⃠ k⃠e⃠ l⃠a⃠d⃠k⃠e⃠",
"t⃠m⃠k⃠c⃠ f⃠u⃠f⃠i⃠",
"t⃠e⃠r⃠y⃠ d⃠i⃠d⃠i⃠ c⃠h⃠u⃠d⃠i⃠",
"t⃠m⃠k⃠c⃠ d⃠i⃠k⃠h⃠a⃠",
"C⃠u⃠d⃠ a⃠b⃠",
"r⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠u⃠d⃠",
"B⃠h⃠a⃠k⃠ c⃠u⃠d⃠",
"c⃠u⃠d⃠l⃠e⃠ t⃠b⃠k⃠c⃠ m⃠r⃠u⃠",
"t⃠m⃠k⃠l⃠ c⃠u⃠d⃠l⃠e⃠ g⃠r⃠i⃠b⃠",
"t⃠e⃠r⃠y⃠ b⃠e⃠h⃠e⃠n⃠ v⃠e⃠s⃠i⃠y⃠a⃠a⃠ r⃠n⃠d⃠i⃠",
"I⃠t⃠n⃠a⃠ g⃠n⃠d⃠a⃠ c⃠h⃠u⃠d⃠a⃠ t⃠u⃠ f⃠i⃠r⃠s⃠e⃠ n⃠e⃠t⃠ o⃠n⃠ o⃠f⃠f⃠",
"g⃠r⃠i⃠b⃠ k⃠e⃠ b⃠e⃠t⃠e⃠",
"B⃠h⃠a⃠g⃠ j⃠a⃠ l⃠o⃠d⃠e⃠ t⃠m⃠k⃠c⃠ m⃠a⃠r⃠u⃠ d⃠u⃠n⃠g⃠a⃠",
"t⃠b⃠k⃠c⃠ m⃠r⃠d⃠u⃠n⃠g⃠a⃠a⃠",
"b⃠h⃠a⃠g⃠ t⃠m⃠k⃠c⃠",
"b⃠h⃠a⃠g⃠ t⃠b⃠k⃠c⃠",
"t⃠b⃠k⃠c⃠ m⃠e⃠y⃠ c⃠p⃠",
"c⃠p⃠ t⃠b⃠k⃠c⃠ m⃠e⃠h⃠h⃠",
"c⃠p⃠ t⃠m⃠k⃠l⃠ m⃠e⃠h⃠",
"c⃠p⃠ b⃠o⃠l⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"A⃠b⃠e⃠ c⃠p⃠ b⃠o⃠l⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"d⃠o⃠u⃠b⃠l⃠e⃠ s⃠e⃠n⃠d⃠ k⃠o⃠ c⃠p⃠ t⃠m⃠k⃠c⃠ c⃠o⃠d⃠u⃠",
"t⃠b⃠k⃠c⃠ m⃠e⃠ c⃠p⃠ c⃠o⃠d⃠ d⃠u⃠n⃠g⃠a⃠ A⃠a⃠j⃠ m⃠e⃠h⃠h⃠",
"h⃠t⃠ t⃠b⃠k⃠c⃠ d⃠a⃠l⃠a⃠l⃠ k⃠e⃠ b⃠e⃠t⃠e⃠.",
"R⃠n⃠d⃠y⃠ j⃠l⃠d⃠i⃠ j⃠l⃠d⃠i⃠ c⃠u⃠d⃠q⃠ t⃠r⃠y⃠m⃠a⃠",
"P⃠a⃠r⃠a⃠ l⃠i⃠k⃠h⃠e⃠g⃠a⃠..",
"T⃠r⃠a⃠ r⃠n⃠d⃠h⃠b⃠h⃠a⃠k⃠",
"L⃠a⃠g⃠d⃠i⃠ k⃠e⃠ l⃠a⃠d⃠c⃠e⃠ c⃠p⃠ b⃠o⃠l⃠",
"c⃠p⃠ b⃠o⃠l⃠ l⃠a⃠g⃠d⃠i⃠ k⃠e⃠ b⃠e⃠t⃠e⃠..",
"c⃠u⃠d⃠k⃠e⃠ c⃠p⃠ b⃠o⃠l⃠",
"b⃠h⃠i⃠k⃠a⃠r⃠i⃠ l⃠u⃠n⃠d⃠ c⃠h⃠u⃠s⃠ m⃠e⃠r⃠a⃠.",
"L⃠o⃠w⃠ l⃠e⃠v⃠e⃠l⃠ c⃠p⃠ c⃠r⃠",
"c⃠p⃠ b⃠o⃠l⃠ l⃠o⃠w⃠ l⃠e⃠v⃠e⃠l⃠ w⃠e⃠a⃠k⃠",
"m⃠e⃠r⃠e⃠ l⃠u⃠n⃠d⃠ p⃠e⃠ e⃠y⃠ t⃠u⃠ h⃠i⃠j⃠d⃠e⃠",
"f⃠r⃠e⃠e⃠ c⃠u⃠d⃠w⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"F⃠r⃠e⃠e⃠ m⃠e⃠y⃠ c⃠u⃠d⃠ t⃠u⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠"
"s⃠p⃠e⃠e⃠d⃠ n⃠y⃠ w⃠e⃠a⃠k⃠ t⃠a⃠t⃠t⃠e⃠ t⃠e⃠r⃠m⃠e⃠",
"k⃠i⃠t⃠n⃠i⃠ b⃠r⃠ c⃠u⃠d⃠w⃠a⃠y⃠e⃠g⃠a⃠ t⃠e⃠r⃠y⃠m⃠a⃠k⃠o⃠",
"l⃠u⃠n⃠d⃠ l⃠e⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠a⃠p⃠k⃠a⃠",
"l⃠u⃠n⃠ c⃠u⃠s⃠ j⃠a⃠l⃠d⃠i⃠ s⃠e⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ b⃠a⃠p⃠k⃠a⃠",
"k⃠o⃠i⃠ n⃠y⃠ d⃠e⃠k⃠h⃠ r⃠h⃠a⃠ c⃠u⃠d⃠l⃠e⃠ t⃠u⃠",
"c⃠u⃠d⃠l⃠e⃠ b⃠e⃠t⃠i⃠c⃠h⃠o⃠d⃠ a⃠c⃠h⃠e⃠ s⃠e⃠",
"m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ t⃠e⃠r⃠y⃠ b⃠s⃠ y⃠e⃠h⃠i⃠ j⃠a⃠n⃠t⃠a⃠ m⃠e⃠y⃠",
"c⃠p⃠ b⃠o⃠l⃠e⃠g⃠a⃠ t⃠o⃠ t⃠m⃠k⃠c⃠",
"w⃠r⃠n⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ c⃠u⃠d⃠ j⃠a⃠y⃠e⃠g⃠i⃠",
"s⃠l⃠o⃠w⃠ e⃠y⃠ t⃠u⃠ k⃠i⃠d⃠",
"j⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠..t⃠m⃠k⃠c⃠",
"j⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠..r⃠a⃠n⃠d⃠c⃠e⃠ t⃠u⃠",
"t⃠y⃠m⃠ s⃠e⃠ p⃠h⃠l⃠e⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"t⃠y⃠m⃠ h⃠o⃠g⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ c⃠u⃠d⃠w⃠a⃠",
"m⃠a⃠ c⃠u⃠d⃠ g⃠a⃠i⃠ t⃠e⃠r⃠y⃠ t⃠y⃠m⃠ s⃠e⃠ p⃠h⃠l⃠e⃠",
"u⃠t⃠h⃠ r⃠a⃠n⃠d⃠c⃠e⃠ k⃠e⃠ l⃠d⃠k⃠e⃠",
"m⃠a⃠c⃠a⃠b⃠o⃠s⃠d⃠a⃠t⃠e⃠r⃠y⃠",
"c⃠o⃠n⃠ k⃠b⃠ c⃠o⃠d⃠ d⃠i⃠a⃠ m⃠a⃠k⃠o⃠ t⃠e⃠r⃠y⃠",
"k⃠o⃠i⃠ h⃠o⃠g⃠a⃠ t⃠m⃠l⃠",
"m⃠a⃠c⃠h⃠a⃠r⃠ c⃠u⃠d⃠l⃠e⃠ t⃠u⃠",
"m⃠e⃠n⃠u⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ c⃠o⃠d⃠n⃠a⃠ s⃠e⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ b⃠o⃠l⃠ m⃠u⃠j⃠h⃠e⃠ c⃠o⃠d⃠ d⃠e⃠",
"b⃠s⃠ m⃠e⃠y⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ s⃠e⃠ c⃠u⃠d⃠n⃠a⃠ c⃠h⃠t⃠a⃠ h⃠u⃠",
"E⃠w⃠w⃠ m⃠a⃠k⃠a⃠ l⃠o⃠d⃠e⃠ u⃠t⃠h⃠",
"M⃠e⃠o⃠w⃠ c⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠ c⃠o⃠d⃠u⃠",
"l⃠u⃠n⃠d⃠ r⃠k⃠h⃠ d⃠i⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ f⃠u⃠d⃠e⃠ p⃠e⃠",
"m⃠e⃠r⃠a⃠ l⃠u⃠n⃠d⃠ k⃠e⃠ b⃠a⃠l⃠ u⃠t⃠h⃠",
"k⃠i⃠d⃠e⃠e⃠ Z⃠i⃠n⃠d⃠a⃠ h⃠o⃠",
"m⃠a⃠r⃠ n⃠y⃠ k⃠i⃠d⃠d⃠e⃠ t⃠y⃠p⃠e⃠ k⃠r⃠",
"c⃠h⃠u⃠p⃠ b⃠k⃠l⃠",
"b⃠c⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠",
"m⃠c⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ l⃠i⃠k⃠h⃠ f⃠a⃠s⃠t⃠",
"f⃠a⃠s⃠t⃠ l⃠i⃠k⃠h⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠",
"f⃠a⃠s⃠t⃠ l⃠i⃠k⃠h⃠ k⃠a⃠m⃠z⃠o⃠r⃠"
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ c⃠l⃠a⃠i⃠m⃠ c⃠r⃠w⃠a⃠",
"a⃠w⃠z⃠ n⃠i⃠c⃠h⃠e⃠ r⃠a⃠n⃠d⃠c⃠e⃠ k⃠e⃠ b⃠c⃠h⃠e⃠",
"s⃠a⃠w⃠a⃠l⃠ n⃠y⃠ p⃠u⃠c⃠h⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠a⃠b⃠o⃠s⃠d⃠a⃠",
"f⃠y⃠t⃠e⃠r⃠ b⃠n⃠e⃠g⃠a⃠ l⃠a⃠g⃠d⃠e⃠ m⃠a⃠d⃠r⃠c⃠h⃠o⃠d⃠",
"o⃠y⃠e⃠ k⃠a⃠a⃠l⃠e⃠ r⃠o⃠ k⃠e⃠ d⃠i⃠k⃠h⃠a⃠",
"o⃠y⃠e⃠ k⃠a⃠a⃠l⃠e⃠ r⃠o⃠o⃠ n⃠y⃠",
"s⃠h⃠o⃠r⃠t⃠ n⃠y⃠ c⃠u⃠d⃠ t⃠u⃠ b⃠i⃠n⃠a⃠ r⃠u⃠k⃠e⃠",
"s⃠h⃠o⃠r⃠t⃠ n⃠y⃠ c⃠u⃠d⃠ t⃠u⃠ a⃠p⃠n⃠i⃠ m⃠a⃠k⃠o⃠ l⃠e⃠k⃠r⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ s⃠t⃠h⃠ t⃠e⃠r⃠y⃠ b⃠h⃠e⃠n⃠ v⃠i⃠ c⃠u⃠d⃠w⃠a⃠ l⃠e⃠",
"t⃠e⃠r⃠y⃠ m⃠a⃠k⃠e⃠ s⃠t⃠h⃠ t⃠e⃠r⃠y⃠ d⃠i⃠d⃠i⃠ v⃠i⃠ c⃠u⃠d⃠ g⃠a⃠i⃠",
"C⃠h⃠a⃠t⃠ f⃠y⃠t⃠e⃠r⃠ b⃠n⃠e⃠g⃠a⃠ r⃠a⃠n⃠d⃠c⃠e⃠ c⃠o⃠d⃠u⃠ t⃠e⃠r⃠y⃠ m⃠a⃠k⃠o⃠",
"b⃠o⃠l⃠ r⃠a⃠n⃠d⃠i⃠b⃠a⃠a⃠z⃠ d⃠a⃠d⃠d⃠y⃠ e⃠y⃠",
"b⃠u⃠l⃠l⃠y⃠x⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ u⃠t⃠h⃠",
"m⃠a⃠r⃠ m⃠a⃠r⃠k⃠e⃠ c⃠u⃠d⃠ r⃠h⃠a⃠ t⃠u⃠",
"o⃠r⃠ t⃠e⃠r⃠y⃠ m⃠a⃠ m⃠a⃠r⃠k⃠e⃠ c⃠u⃠d⃠ g⃠a⃠i⃠"
"J⃠a⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ r⃠n⃠d⃠y⃠k⃠e⃠ b⃠e⃠j⃠",
"O⃠r⃠ b⃠d⃠a⃠ l⃠i⃠k⃠h⃠ t⃠m⃠c⃠",
"O⃠r⃠ b⃠d⃠a⃠ 2⃠ l⃠i⃠n⃠e⃠ w⃠l⃠a⃠ l⃠i⃠k⃠h⃠ t⃠m⃠k⃠c⃠",
"O⃠r⃠ b⃠d⃠a⃠ o⃠y⃠e⃠ l⃠i⃠k⃠h⃠ t⃠m⃠l⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠a⃠ b⃠u⃠r⃠",
"O⃠y⃠e⃠ k⃠e⃠e⃠d⃠e⃠",
"R⃠a⃠n⃠d⃠i⃠ k⃠e⃠ l⃠a⃠d⃠k⃠e⃠",
"J⃠a⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ t⃠e⃠r⃠i⃠ b⃠e⃠h⃠e⃠n⃠ c⃠h⃠o⃠d⃠u⃠",
"M⃠k⃠l⃠ u⃠t⃠h⃠ r⃠a⃠n⃠d⃠i⃠ k⃠e⃠ b⃠a⃠c⃠c⃠h⃠e⃠",
"T⃠e⃠r⃠i⃠ n⃠a⃠n⃠i⃠ m⃠e⃠r⃠i⃠ m⃠a⃠a⃠l⃠",
"T⃠e⃠j⃠ l⃠i⃠k⃠h⃠ r⃠a⃠n⃠d⃠c⃠e⃠",
"O⃠y⃠e⃠ m⃠a⃠a⃠k⃠e⃠ l⃠o⃠d⃠e⃠ m⃠r⃠e⃠n⃠g⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠y⃠",
"T⃠e⃠r⃠i⃠ M⃠a⃠i⃠y⃠a⃠ k⃠i⃠ g⃠a⃠n⃠d⃠",
"T⃠e⃠r⃠y⃠ d⃠a⃠d⃠i⃠ k⃠a⃠ f⃠u⃠d⃠d⃠a⃠",
"M⃠k⃠l⃠ u⃠t⃠h⃠ b⃠e⃠h⃠e⃠n⃠c⃠o⃠d⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠i⃠ b⃠u⃠r⃠ d⃠e⃠",
"T⃠e⃠r⃠y⃠ m⃠a⃠a⃠ k⃠a⃠ f⃠u⃠d⃠d⃠a⃠ m⃠e⃠ l⃠a⃠u⃠d⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠u⃠d⃠v⃠a⃠",
"R⃠a⃠n⃠d⃠i⃠ k⃠e⃠ b⃠e⃠t⃠e⃠ m⃠a⃠r⃠ g⃠a⃠y⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠ k⃠i⃠ c⃠h⃠u⃠t⃠ m⃠r⃠u⃠",
"J⃠a⃠l⃠i⃠d⃠ k⃠r⃠ s⃠p⃠a⃠m⃠",
"M⃠c⃠ s⃠p⃠a⃠m⃠ r⃠o⃠k⃠e⃠n⃠g⃠a⃠",
"T⃠e⃠r⃠i⃠ m⃠a⃠a⃠k⃠i⃠ c⃠h⃠u⃠t⃠ s⃠p⃠a⃠m⃠ k⃠r⃠",
"s⃠p⃠a⃠m⃠ k⃠r⃠.⃠m⃠a⃠a⃠k⃠e⃠ l⃠o⃠d⃠e⃠",
"R⃠a⃠n⃠d⃠y⃠k⃠e⃠ c⃠h⃠o⃠d⃠e⃠ s⃠p⃠a⃠m⃠ k⃠r⃠ w⃠r⃠n⃠a⃠ c⃠u⃠d⃠ t⃠u⃠",
"S⃠p⃠a⃠m⃠ k⃠r⃠ k⃠i⃠d⃠",
"N⃠o⃠o⃠b⃠ t⃠e⃠r⃠i⃠ m⃠a⃠a⃠ c⃠h⃠o⃠d⃠u⃠",
"R⃠n⃠d⃠y⃠k⃠e⃠ b⃠e⃠t⃠e⃠ m⃠a⃠r⃠ m⃠a⃠t⃠ t⃠u⃠",
"N⃠o⃠o⃠b⃠ j⃠a⃠l⃠d⃠i⃠ l⃠i⃠k⃠h⃠ w⃠r⃠n⃠a⃠ t⃠e⃠r⃠y⃠ m⃠a⃠a⃠ r⃠a⃠n⃠d⃠",
"c⃠u⃠d⃠ g⃠a⃠i⃠ m⃠a⃠a⃠ t⃠e⃠r⃠y⃠ n⃠o⃠o⃠b⃠",
"u⃠t⃠h⃠ r⃠a⃠n⃠d⃠y⃠k⃠e⃠ n⃠o⃠o⃠b⃠",
"c⃠h⃠l⃠ c⃠u⃠d⃠k⃠e⃠ d⃠i⃠k⃠h⃠a⃠ n⃠o⃠o⃠b⃠",
"j⃠l⃠d⃠i⃠ t⃠y⃠p⃠ c⃠r⃠ n⃠o⃠o⃠b⃠ h⃠a⃠l⃠k⃠e⃠",
"c⃠u⃠d⃠ k⃠e⃠ p⃠g⃠l⃠ n⃠y⃠ h⃠o⃠ n⃠o⃠o⃠b⃠",
"c⃠u⃠d⃠ c⃠u⃠d⃠ k⃠e⃠ r⃠a⃠n⃠d⃠ b⃠n⃠j⃠a⃠ t⃠u⃠ n⃠o⃠o⃠b⃠",
"m⃠a⃠k⃠i⃠c⃠h⃠u⃠t⃠ t⃠e⃠r⃠y⃠ n⃠o⃠o⃠b⃠",
"g⃠a⃠n⃠d⃠a⃠ c⃠y⃠u⃠ c⃠u⃠d⃠ r⃠h⃠a⃠ t⃠u⃠ ?",
"i⃠t⃠n⃠a⃠ g⃠n⃠d⃠a⃠ n⃠y⃠ c⃠u⃠d⃠ a⃠c⃠h⃠e⃠ s⃠e⃠ c⃠u⃠d⃠",
"M⃠a⃠a⃠n⃠ l⃠e⃠ c⃠u⃠d⃠ g⃠y⃠a⃠ t⃠u⃠ s⃠u⃠n⃠ b⃠a⃠t⃠ a⃠b⃠",
"m⃠a⃠k⃠a⃠f⃠u⃠d⃠d⃠a⃠ f⃠a⃠t⃠ g⃠y⃠a⃠ t⃠e⃠r⃠y⃠ r⃠u⃠k⃠",
]
bs_texts = [
"ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝓃ᕗᕙ𝒶ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝒯ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓏ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓎ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝒹ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝒯ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙℳᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓎ᕗᕙ𝓂ᕗᕙ𝓅ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝓈ᕗ",
"ᕙ𝒪ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓊ᕗᕙ𝓃ᕗᕙ𝒻ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗᕙ𝓉ᕗ ᕙ𝓀ᕗᕙ𝓇ᕗ",
"ᕙ𝒪ᕗᕙ𝒽ᕗ ᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓁ᕗᕙ𝓁ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓋ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒶ᕗᕙ𝓊ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝓇ᕗ.",
"ᕙ𝒪ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝓃ᕗᕙ𝓃ᕗᕙ𝑒ᕗᕙ𝓇ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙℊᕗᕙ𝒸ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗ ᕙ𝓅ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓂ᕗᕙ𝒾ᕗᕙ𝓈ᕗᕙ𝓈ᕗᕙ𝒾ᕗᕙ𝑜ᕗᕙ𝓃ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝓈ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗ.",
"ᕙ𝒞ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ",
"ᕙ𝒞ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓇ᕗ.",
"ᕙ𝒮ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝒮ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ.",
"ᕙ𝒯ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝒶ᕗ.",
"ᕙ𝒪ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ.",
"ᕙ𝒦ᕗᕙ𝓎ᕗ? ᕙ𝒿ᕗᕙ𝓁ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒹ᕗᕙ𝑒ᕗ.",
"ᕙℬᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝑜ᕗᕙ𝓂ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙℊᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓀ᕗᕙ𝑜ᕗ ᕙ𝓉ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ",
"ᕙℳᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓀ᕗᕙ𝒸ᕗ ᕙ𝒷ᕗᕙ𝓈ᕗ",
"ᕙ𝒥ᕗᕙ𝒶ᕗᕙ𝓁ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓏ᕗ ᕙ𝓅ᕗᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ",
"ᕙ𝒮ᕗᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒿ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝒶ᕗᕙ𝒷ᕗ",
"ᕙℋᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙℊᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ",
"ᕙ𝒷ᕗᕙ𝒽ᕗᕙℊᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝒿ᕗᕙ𝒿ᕗ",
"ᕙℋᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓉ᕗ",
"ᕙℋᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓇ᕗ ᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝓉ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝒽ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓀ᕗᕙ𝑜ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓈ᕗᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒻ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗ ᕙ𝓇ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝒽ᕗᕙ𝓊ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓀ᕗᕙ𝑜ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒻ᕗᕙ𝒾ᕗ ᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙℊᕗᕙ𝒶ᕗ",
"ᕙ𝒜ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ??ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒻ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒾ᕗᕙ𝓁ᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝒜ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙℱᕗᕙ𝓇ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝓌ᕗᕙ𝒾ᕗᕙ𝓅ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝒞ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ",
"ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝓉ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝓉ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ",
"ᕙ𝓁ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓊ᕗᕙ𝓉ᕗᕙ𝓇ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝓁ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓈ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒶ᕗ",
"ᕙ𝓃ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒹ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝒽ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝒾ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓉ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗ ᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝒽ᕗ ᕙ𝓉ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝒽ᕗ ᕙ𝓀ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓀ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝒻ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙℊᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝒶ᕗᕙ??ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓀ᕗᕙ𝑜ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝑒ᕗᕙ𝓇ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒿ᕗᕙ𝓁ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓌ᕗᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝒮ᕗᕙ𝓂ᕗᕙ𝒿ᕗᕙ𝒽ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝓉ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝒻ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝓉ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝒶ᕗᕙ𝓋ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝒿ᕗᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ",
"ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗᕙ𝒿ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝓏ᕗᕙ𝑜ᕗᕙ𝓇ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝑜ᕗ ᕙ𝒾ᕗᕙ𝓁ᕗᕙ𝓎ᕗ ᕙ𝓇ᕗᕙ𝑒ᕗᕙ𝓎ᕗ 🌚😂",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓀ᕗᕙ𝒸ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ",
"ᕙ𝓈ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ",
"ᕙ𝒻ᕗᕙ𝓇ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ??ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ",
"ᕙ𝓈ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗ ᕙ𝓌ᕗᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝓊ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓅ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗᕙ𝑜ᕗᕙ𝑜ᕗᕙ𝒻ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗᕙ𝑜ᕗᕙ𝑜ᕗᕙ𝒻ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ",
"ᕙ𝓅ᕗᕙ𝓇ᕗᕙ𝑜ᕗᕙ𝑜ᕗᕙ𝒻ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒾ᕗᕙ𝓁ᕗᕙ𝓁ᕗᕙ𝒶ᕗᕙ𝓇ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ??ᕗᕙ𝓎ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗᕙ𝒿ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝓏ᕗᕙ𝑜ᕗᕙ𝓇ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝓇ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗ ?",
"ᕙ𝒶ᕗᕙ𝒷ᕗ ᕙ𝓉ᕗᕙ𝓀ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒾ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ?",
"ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓀ᕗᕙ𝓊ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝓉ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝓈ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ",
"ᕙ𝒮ᕗᕙ𝒷ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓂ᕗ ᕙ𝓀ᕗᕙ𝓇ᕗᕙ𝑒ᕗ",
"ᕙ𝓎ᕗᕙ𝒶ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝒸ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝒾ᕗᕙ𝓁ᕗᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝒶ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓃ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝑒ᕗᕙℊᕗᕙ𝒾ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝓅ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝑜ᕗᕙ𝓂ᕗᕙ𝓂ᕗᕙ𝓎ᕗ",
"ᕙ𝓃ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝒹ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝓎ᕗᕙ𝒽ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ",
"ᕙ𝒸ᕗᕙ𝑜ᕗᕙ𝓏ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗ ᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓅ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝓊ᕗᕙ𝒿ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓃ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝒿ᕗᕙ𝑜ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗᕙ𝓉ᕗᕙ𝒾ᕗ ᕙ𝒿ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ",
"ᕙ𝓉ᕗᕙ𝓇ᕗᕙ𝓎ᕗ ᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝓂ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝑒ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝒹ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝑒ᕗᕙ𝓂ᕗᕙ𝑜ᕗᕙ𝒿ᕗᕙ𝒾ᕗ ᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓂ᕗᕙ𝓇ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ?",
"ᕙ𝓉ᕗᕙ𝓂ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗᕙℊᕗᕙ𝒾ᕗ ᕙ𝒻ᕗᕙ𝓇ᕗᕙ𝓇ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝓀ᕗᕙ𝒷ᕗ ? ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓀ᕗᕙ𝑒ᕗᕙ𝓀ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝓎ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ",
"ᕙ𝒾ᕗᕙ𝓉ᕗᕙ𝓃ᕗᕙ𝒶ᕗ ᕙ𝓈ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓃ᕗᕙ??ᕗ ᕙ𝒷ᕗᕙ𝑜ᕗᕙ𝓁ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝒶ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝓎ᕗ",
"ᕙ𝓈ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝓉ᕗᕙ𝓊ᕗ ᕙ𝒶ᕗᕙ𝓅ᕗᕙ𝓃ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓌ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝓉ᕗᕙ𝒽ᕗ",
"ᕙ𝓂ᕗᕙ𝓉ᕗᕙ𝓁ᕗᕙ𝒷ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝓅ᕗᕙ𝓊ᕗᕙ𝓇ᕗᕙ𝒶ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ ᕙ𝒻ᕗᕙ𝓇ᕗᕙ𝓇ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝑜ᕗᕙ𝒽ᕗ ᕙ𝑜ᕗᕙ𝓀ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒻ᕗᕙ𝒾ᕗᕙ𝓇ᕗ",
"ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒹ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙ𝑒ᕗᕙ𝒽ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝑒ᕗᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑒ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓋ᕗᕙ𝓎ᕗᕙ𝒶ᕗᕙ𝓈ᕗᕙ𝓉ᕗ ᕙ𝒽ᕗᕙ𝓊ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓀ᕗᕙ𝓊ᕗᕙ𝒸ᕗᕙ𝒽ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ? ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙℊᕗᕙ𝓎ᕗᕙ𝒶ᕗ ?",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ ᕙ𝒽ᕗᕙ𝓈ᕗᕙ𝓈ᕗ",
"ᕙ𝓎ᕗᕙ𝓊ᕗᕙ𝓇ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝑜ᕗᕙ𝓂ᕗ",
"ᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝒷ᕗᕙ𝓀ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝒷ᕗᕙ𝒾ᕗ",
"ᕙ𝒶ᕗᕙ𝓇ᕗᕙ𝑒ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓇ᕗ",
"ᕙ𝓉ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒾ᕗ ᕙ𝓉ᕗᕙ𝓇ᕗᕙ𝒽ᕗ",
"ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝓁ᕗᕙ𝒾ᕗᕙ𝓃ᕗᕙ𝑒ᕗ ᕙ𝓂ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝒬ᕗ",
"ᕙ𝑜ᕗᕙ𝒸ᕗᕙ𝓎ᕗ ᕙ𝒶ᕗᕙ𝒷ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝓅ᕗᕙ𝑒ᕗᕙ𝒽ᕗᕙ𝑒ᕗᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝓉ᕗᕙ𝑒ᕗᕙ𝓇ᕗᕙ𝒾ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝑜ᕗᕙ𝒹ᕗᕙ𝓊ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝓆ᕗ ?",
"ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝑒ᕗᕙ𝓀ᕗ ᕙ𝒷ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓇ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝓈ᕗᕙ𝓊ᕗᕙ𝓃ᕗ ᕙ𝒹ᕗᕙ𝑜ᕗᕙ𝓈ᕗᕙ𝓉ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝒿ᕗᕙ𝒶ᕗ ᕙ𝓇ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓃ᕗᕙ𝒹ᕗ ᕙ𝓂ᕗᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝒻ᕗ ᕙ𝒸ᕗᕙ𝓇ᕗᕙ𝓇ᕗ ᕙ𝒹ᕗᕙ𝓊ᕗᕙ𝓃ᕗᕙℊᕗᕙ𝒶ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝓇ᕗᕙ𝓃ᕗᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝒾ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗ",
"ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓉ᕗᕙ𝓂ᕗᕙ𝓇ᕗ ᕙ𝒻ᕗᕙ𝓇ᕗᕙ𝓇ᕗᕙ𝓉ᕗᕙ𝑜ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒾ᕗᕙ𝒹ᕗᕙ𝒶ᕗᕙ𝓇ᕗ ᕙ𝒶ᕗᕙ𝒶ᕗᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓂ᕗᕙ𝓇ᕗ",
"ᕙ𝓃ᕗᕙ𝓎ᕗᕙ𝓉ᕗᕙ𝑜ᕗ ᕙ𝒶ᕗᕙ𝑒ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ",
"ᕙ𝑜ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒶ᕗᕙ𝒾ᕗᕙ𝓈ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝒾ᕗ ᕙ𝒸ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗᕙ𝓃ᕗᕙ𝒶ᕗ",
"ᕙ𝑜ᕗᕙ𝓇ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓁ᕗᕙ𝑒ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓀ᕗᕙ𝑒ᕗ ᕙ𝒹ᕗᕙ𝒾ᕗᕙ𝓀ᕗᕙ𝒶ᕗ ᕙ𝑜ᕗᕙ𝓇ᕗ",
"ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝑜ᕗ ᕙ𝓃ᕗᕙ𝒶ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗᕙ𝑜ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ ᕙ𝒷ᕗᕙ𝒽ᕗᕙ𝒶ᕗᕙℊᕗ ᕙ𝒿ᕗᕙ𝒶ᕗᕙ𝑜ᕗ",
"ᕙ𝒷ᕗᕙ𝓎ᕗᕙ𝓎ᕗᕙ𝑒ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝓎ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ?",
"ᕙ𝒬ᕗᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝒬ᕗ ᕙ𝓇ᕗᕙ𝒽ᕗᕙ𝑒ᕗ ᕙ𝒽ᕗᕙ𝑜ᕗ ?",
"ᕙ𝓅ᕗᕙℊᕗᕙ𝓁ᕗ ᕙ𝑒ᕗᕙ𝓎ᕗ ᕙ𝒸ᕗᕙ𝓎ᕗᕙ𝒶ᕗ ᕙ𝓂ᕗᕙ𝒸ᕗ",
"ᕙ𝒸ᕗᕙ𝒽ᕗᕙ𝓊ᕗᕙ𝒹ᕗ ᕙ𝓂ᕗᕙ𝓉ᕗ",
]
bs2_texts = [
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇸​⋰⋰🇪​⋰⋰🇼​⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰⋰🇰​⋰⋰🇪​⋰⋰🇧​⋰⋰🇦​⋰⋰🇨​⋰⋰🇭​⋰⋰🇪​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇮​⋰⋰🇸​⋰⋰🇸​⋰⋰🇦​⋰⋰🇬​⋰⋰🇦​⋰",
"⋰🇦​⋰⋰🇦​⋰⋰🇯​⋰ ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇭​⋰⋰🇦​⋰⋰🇮​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇩​⋰⋰🇷​⋰⋰🇨​⋰⋰🇭​⋰⋰🇴​⋰⋰🇩​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇰​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇯​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇸​⋰⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇮​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇸​⋰⋰🇰​⋰⋰🇹​⋰⋰🇦​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇸​⋰⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇫​⋰⋰🇮​⋰⋰🇷​⋰⋰🇸​⋰⋰🇪​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰, ⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰ ⋰🇩​⋰⋰🇴​⋰⋰🇺​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰ ⋰🇼​⋰⋰🇦​⋰⋰🇱​⋰⋰🇮​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰",
"⋰🇴​⋰⋰🇾​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇮​⋰⋰🇩​⋰⋰🇭​⋰⋰🇦​⋰⋰🇷​⋰ ⋰🇦​⋰⋰🇦​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇴​⋰⋰🇮​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇦​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇩​⋰⋰🇪​⋰⋰🇪​⋰",
"⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇪​⋰⋰🇯​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇸​⋰⋰🇺​⋰⋰🇦​⋰⋰🇷​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇪​⋰⋰🇯​⋰, ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇰​⋰⋰🇷​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰⋰🇸​⋰⋰🇪​⋰, ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇵​⋰ ⋰🇸​⋰⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇩​⋰⋰🇭​⋰⋰🇦​⋰⋰🇷​⋰⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇷​⋰ ⋰🇲​⋰⋰🇸​⋰⋰🇬​⋰ ⋰🇩​⋰⋰🇪​⋰⋰🇱​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰, ⋰🇴​⋰⋰🇮​⋰ ⋰🇸​⋰⋰🇺​⋰⋰🇦​⋰⋰🇷​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇫​⋰⋰🇺​⋰⋰🇫​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇦​⋰, ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇦​⋰⋰🇧​⋰",
"⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇺​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇮​⋰⋰🇹​⋰⋰🇳​⋰⋰🇦​⋰ ⋰🇬​⋰⋰🇳​⋰⋰🇩​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇫​⋰⋰🇮​⋰⋰🇷​⋰⋰🇸​⋰⋰🇪​⋰ ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰",
"⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇯​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇩​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇷​⋰⋰🇺​⋰ ⋰🇩​⋰⋰🇺​⋰⋰??​⋰⋰🇬​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰⋰🇦​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰, ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇵​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰, ⋰🇦​⋰⋰🇧​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇩​⋰⋰🇴​⋰⋰🇺​⋰⋰🇧​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇸​⋰⋰🇪​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇰​⋰⋰🇴​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰, ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰ ⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰ ⋰🇦​⋰⋰🇦​⋰⋰🇯​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰",
"⋰🇭​⋰⋰🇹​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇦​⋰⋰🇱​⋰⋰🇦​⋰⋰🇱​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰., ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇶​⋰ ⋰🇹​⋰⋰??​⋰⋰🇾​⋰⋰🇲​⋰⋰🇦​⋰",
"⋰🇵​⋰⋰🇦​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇪​⋰⋰🇬​⋰⋰🇦​⋰.., ⋰🇹​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇭​⋰⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰",
"⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇨​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰..",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰⋰🇰​⋰⋰🇦​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇸​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇦​⋰.",
"⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇷​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇼​⋰⋰🇪​⋰⋰🇦​⋰⋰🇰​⋰",
"⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇵​⋰⋰🇪​⋰ ⋰🇪​⋰⋰🇾​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇭​⋰⋰🇮​⋰⋰🇯​⋰⋰🇩​⋰⋰🇪​⋰, ⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇼​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇴​⋰",
"⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇭​⋰⋰🇦​⋰⋰🇮​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰ ⋰🇨​⋰⋰🇱​⋰⋰🇦​⋰⋰🇮​⋰⋰🇲​⋰ ⋰🇨​⋰⋰🇷​⋰⋰🇼​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇸​⋰⋰🇰​⋰⋰🇹​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇯​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇦​⋰",
"⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇦​⋰⋰🇧​⋰, ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰, ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇺​⋰",
"⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇬​⋰⋰🇷​⋰⋰??​⋰⋰🇧​⋰, ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰",
"⋰🇮​⋰⋰🇹​⋰⋰🇳​⋰⋰🇦​⋰ ⋰🇬​⋰⋰🇳​⋰⋰🇩​⋰⋰??​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇫​⋰⋰🇮​⋰⋰🇷​⋰⋰🇸​⋰⋰🇪​⋰ ⋰🇳​⋰⋰🇪​⋰⋰🇹​⋰ ⋰🇴​⋰⋰🇳​⋰ ⋰🇴​⋰⋰🇫​⋰⋰🇫​⋰, ⋰🇬​⋰⋰🇷​⋰⋰🇮​⋰⋰🇧​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇯​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇩​⋰⋰🇪​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇷​⋰⋰🇺​⋰ ⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇷​⋰⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰⋰🇦​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰, ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇵​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇱​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰, ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇦​⋰⋰🇧​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰, ⋰🇩​⋰⋰🇴​⋰⋰🇺​⋰⋰🇧​⋰⋰🇱​⋰⋰🇪​⋰ ⋰🇸​⋰⋰🇪​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇰​⋰⋰🇴​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇹​⋰⋰🇲​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰⋰🇺​⋰",
"⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇲​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇴​⋰⋰🇩​⋰ ⋰🇩​⋰⋰🇺​⋰⋰🇳​⋰⋰🇬​⋰⋰🇦​⋰ ⋰🇦​⋰⋰🇦​⋰⋰🇯​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇭​⋰⋰🇭​⋰, ⋰🇭​⋰⋰🇹​⋰ ⋰🇹​⋰⋰🇧​⋰⋰🇰​⋰⋰🇨​⋰ ⋰🇩​⋰⋰🇦​⋰⋰🇱​⋰⋰🇦​⋰⋰🇱​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰.",
"⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇯​⋰⋰🇱​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇶​⋰ ⋰🇹​⋰⋰🇷​⋰⋰🇾​⋰⋰🇲​⋰⋰🇦​⋰, ⋰🇵​⋰⋰🇦​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇱​⋰⋰🇮​⋰⋰🇰​⋰⋰🇭​⋰⋰🇪​⋰⋰🇬​⋰⋰🇦​⋰..",
"⋰🇹​⋰⋰🇷​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇭​⋰⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇰​⋰, ⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇩​⋰⋰🇨​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇦​⋰⋰🇬​⋰⋰🇩​⋰⋰🇮​⋰ ⋰🇰​⋰⋰🇪​⋰ ⋰🇧​⋰⋰🇪​⋰⋰🇹​⋰⋰🇪​⋰.., ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇰​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰",
"⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰⋰🇰​⋰⋰🇦​⋰⋰🇷​⋰⋰🇮​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇸​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇦​⋰., ⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇨​⋰⋰🇵​⋰ ⋰🇨​⋰⋰🇷​⋰",
"⋰🇨​⋰⋰🇵​⋰ ⋰🇧​⋰⋰🇴​⋰⋰🇱​⋰ ⋰🇱​⋰⋰🇴​⋰⋰🇼​⋰ ⋰🇱​⋰⋰🇪​⋰⋰🇻​⋰⋰🇪​⋰⋰🇱​⋰ ⋰🇼​⋰⋰🇪​⋰⋰🇦​⋰⋰🇰​⋰, ⋰🇲​⋰⋰🇪​⋰⋰🇷​⋰⋰🇪​⋰ ⋰🇱​⋰⋰🇺​⋰⋰🇳​⋰⋰🇩​⋰ ⋰🇵​⋰⋰🇪​⋰ ⋰🇪​⋰⋰🇾​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇭​⋰⋰🇮​⋰⋰🇯​⋰⋰🇩​⋰⋰🇪​⋰",
"⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰⋰🇼​⋰⋰🇦​⋰ ⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰??​⋰⋰🇦​⋰⋰🇰​⋰⋰🇴​⋰, ⋰🇫​⋰⋰🇷​⋰⋰🇪​⋰⋰🇪​⋰ ⋰🇲​⋰⋰🇪​⋰⋰🇾​⋰ ⋰🇨​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇹​⋰⋰🇺​⋰ ⋰🇷​⋰⋰🇦​⋰⋰🇳​⋰⋰🇩​⋰⋰🇾​⋰⋰🇰​⋰⋰🇪​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇰​⋰⋰🇮​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇹​⋰ ⋰🇨​⋰⋰🇱​⋰⋰🇦​⋰⋰🇮​⋰⋰🇲​⋰ ⋰🇨​⋰⋰🇷​⋰⋰🇼​⋰⋰🇦​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇮​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇦​⋰⋰🇬​⋰ ⋰🇸​⋰⋰🇰​⋰⋰🇹​⋰⋰🇦​⋰",
"⋰🇹​⋰⋰🇪​⋰⋰🇷​⋰⋰🇾​⋰ ⋰🇧​⋰⋰🇭​⋰⋰🇪​⋰⋰🇳​⋰ ⋰🇻​⋰⋰🇪​⋰⋰🇸​⋰⋰🇮​⋰⋰🇾​⋰⋰🇦​⋰⋰🇦​⋰ ⋰🇷​⋰⋰🇳​⋰⋰🇩​⋰⋰🇮​⋰, ⋰🇹​⋰⋰🇺​⋰ ⋰🇰​⋰⋰🇾​⋰⋰🇦​⋰ ⋰🇨​⋰⋰🇭​⋰⋰🇺​⋰⋰🇩​⋰ ⋰🇯​⋰⋰🇦​⋰"
"⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇫⋰⋰🇦⋰⋰🇹⋰⋰🇮⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇭⋰⋰🇴⋰⋰🇯⋰⋰🇦⋰",
"⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰",
"⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇳⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇲⋰⋰🇦⋰⋰🇷⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰??⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇩⋰⋰🇮⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇧⋰⋰🇭⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇳⋰⋰🇪⋰⋰🇹⋰ ⋰🇴⋰⋰🇫⋰⋰🇫⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰, ⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰??⋰⋰🇰⋰⋰🇨⋰ ⋰🇲⋰⋰🇦⋰⋰🇷⋰⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇹⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇬⋰⋰🇷⋰⋰🇮⋰⋰🇧⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰, ⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇩⋰⋰🇴⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇳⋰⋰🇦⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇵⋰⋰🇺⋰⋰🇷⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇪⋰⋰🇨⋰⋰🇭⋰ ⋰🇩⋰⋰🇴⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇴⋰⋰🇩⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰🇴⋰",
"⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇦⋰⋰🇩⋰⋰🇮⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰",
"⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰🇹⋰⋰🇾⋰⋰🇵⋰⋰🇪⋰⋰🇷⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰??⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇦⋰⋰🇦⋰⋰🇯⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇲⋰⋰🇪⋰⋰🇮⋰⋰🇳⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇸⋰⋰🇰⋰⋰🇹⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇷⋰⋰🇨⋰⋰🇴⋰⋰🇩⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇩⋰⋰🇮⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇧⋰⋰🇭⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇳⋰⋰🇪⋰⋰🇹⋰ ⋰🇴⋰⋰🇫⋰⋰🇫⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰, ⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇲⋰⋰🇦⋰⋰🇷⋰⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇹⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰??⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇬⋰⋰🇷⋰⋰🇮⋰⋰🇧⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰, ⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇩⋰⋰🇴⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇳⋰⋰🇦⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇵⋰⋰🇺⋰⋰🇷⋰⋰🇦⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇪⋰⋰🇨⋰⋰🇭⋰ ⋰🇩⋰⋰🇴⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇴⋰⋰🇩⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰🇴⋰",
"⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇪⋰⋰🇪⋰⋰🇯⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇧⋰⋰🇦⋰⋰🇩⋰⋰🇮⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰",
"⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰⋰🇸⋰⋰🇪⋰",
"⋰🇹⋰⋰🇧⋰⋰🇰⋰⋰🇨⋰ ⋰🇨⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰ ⋰🇰⋰⋰🇷⋰ ⋰🇲⋰⋰🇸⋰⋰🇬⋰ ⋰🇩⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰⋰🇹⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰",
"⋰🇴⋰⋰🇮⋰ ⋰🇸⋰⋰🇺⋰⋰🇦⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇦⋰⋰🇮⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇸⋰⋰🇱⋰⋰🇴⋰⋰🇼⋰ ⋰🇹⋰⋰🇾⋰⋰🇵⋰⋰🇪⋰⋰🇷⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇦⋰⋰🇦⋰⋰🇯⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇰⋰⋰??⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇲⋰⋰🇪⋰⋰🇮⋰⋰🇳⋰, ⋰🇹⋰⋰🇺⋰ ⋰🇰⋰⋰🇾⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇸⋰⋰🇰⋰⋰🇹⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇷⋰⋰🇨⋰⋰🇴⋰⋰🇩⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇩⋰⋰🇮⋰⋰🇩⋰⋰🇮⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇫⋰⋰🇦⋰⋰🇩⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇧⋰⋰🇭⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇱⋰⋰🇦⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰, ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰"
"⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇧⋰⋰🇳⋰⋰🇦⋰⋰🇱⋰⋰🇪⋰ ⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇪⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇦⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇿⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇾⋰⋰🇦⋰⋰🇦⋰⋰🇩⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰ ⋰🇳⋰⋰🇦⋰ ⋰🇹⋰⋰🇾⋰⋰🇲⋰⋰🇵⋰⋰🇦⋰⋰🇸⋰⋰🇸⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇺⋰⋰🇳⋰⋰🇫⋰⋰🇺⋰⋰🇳⋰⋰🇳⋰⋰🇾⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇲⋰⋰🇹⋰⋰🇹⋰ ⋰🇰⋰⋰🇷⋰",
"⋰🇴⋰⋰🇭⋰ ⋰🇭⋰⋰🇪⋰⋰🇱⋰⋰🇱⋰⋰🇴⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇦⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇴⋰⋰🇷⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇻⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇦⋰⋰🇺⋰⋰🇰⋰⋰🇦⋰⋰🇹⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇷⋰⋰🇭⋰⋰🇦⋰ ⋰🇰⋰⋰🇷⋰.",
"⋰🇴⋰⋰🇾⋰⋰🇾⋰ ⋰🇰⋰⋰🇮⋰⋰🇳⋰⋰🇳⋰⋰🇪⋰⋰🇷⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰ ⋰🇬⋰⋰🇨⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇦⋰⋰🇦⋰⋰🇳⋰⋰🇪⋰ ⋰🇰⋰⋰🇮⋰ ⋰🇵⋰⋰🇪⋰⋰🇷⋰⋰🇲⋰⋰🇮⋰⋰🇸⋰⋰🇸⋰⋰🇮⋰⋰🇴⋰⋰🇳⋰ ⋰🇰⋰⋰🇮⋰⋰🇸⋰⋰🇳⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰.",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰⋰🇦⋰",
"⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰⋰🇦⋰ ⋰🇪⋰⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇷⋰.",
"⋰🇸⋰⋰🇺⋰⋰🇳⋰ ⋰🇸⋰⋰🇺⋰⋰🇳⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰.",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰??⋰ ⋰🇲⋰⋰🇦⋰⋰🇨⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰.",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇹⋰⋰🇮⋰ ⋰🇯⋰⋰🇦⋰⋰🇹⋰⋰🇮⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰.",
"⋰🇰⋰⋰🇾⋰? ⋰🇯⋰⋰🇱⋰⋰🇩⋰⋰🇮⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰ ⋰🇰⋰⋰🇮⋰⋰🇩⋰⋰🇩⋰⋰🇪⋰.",
"⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇨⋰⋰🇴⋰⋰🇲⋰ ⋰🇬⋰⋰🇦⋰⋰🇳⋰⋰🇬⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇰⋰⋰🇴⋰ ⋰🇹⋰⋰🇦⋰⋰🇬⋰ ⋰🇨⋰⋰🇷⋰⋰🇪⋰⋰🇬⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰",
"⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰ ⋰🇧⋰⋰🇸⋰",
"⋰🇯⋰⋰🇦⋰⋰🇱⋰⋰🇩⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇿⋰ ⋰🇵⋰⋰🇦⋰⋰🇵⋰⋰🇦⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰",
"⋰🇸⋰⋰🇮⋰⋰🇩⋰⋰🇪⋰ ⋰🇭⋰⋰🇴⋰⋰🇯⋰⋰🇦⋰ ⋰🇧⋰⋰🇮⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇦⋰⋰🇧⋰",
"⋰🇭⋰⋰🇾⋰⋰🇪⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇧⋰⋰🇭⋰⋰🇬⋰ ⋰🇲⋰⋰🇦⋰⋰🇹⋰ ⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰",
"⋰🇧⋰⋰🇭⋰⋰🇬⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇯⋰⋰🇯⋰",
"⋰🇭⋰⋰🇾⋰⋰🇪⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇲⋰⋰🇦⋰⋰🇹⋰",
"⋰🇭⋰⋰🇾⋰⋰🇪⋰ ⋰🇩⋰⋰🇺⋰⋰🇷⋰ ⋰🇭⋰⋰🇦⋰⋰🇹⋰⋰🇹⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇭⋰⋰🇦⋰⋰🇷⋰⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇧⋰⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰",
"⋰🇰⋰⋰🇴⋰⋰🇮⋰ ⋰🇧⋰⋰🇦⋰⋰🇹⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇪⋰⋰🇸⋰⋰🇱⋰⋰🇮⋰⋰🇾⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇫⋰ ⋰🇨⋰⋰🇷⋰ ⋰🇷⋰⋰🇭⋰⋰🇦⋰ ⋰🇭⋰⋰🇺⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇰⋰⋰🇴⋰⋰🇮⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇹⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇲⋰⋰🇦⋰⋰🇫⋰⋰🇮⋰ ⋰🇩⋰⋰🇪⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇲⋰⋰🇦⋰⋰🇫⋰⋰🇮⋰ ⋰🇲⋰⋰🇮⋰⋰🇱⋰ ⋰🇯⋰⋰🇦⋰⋰🇾⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰ ⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇪⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇨⋰⋰🇷⋰⋰🇰⋰⋰🇪⋰",
"⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇨⋰⋰🇷⋰⋰🇰⋰⋰🇪⋰",
"⋰🇫⋰⋰🇷⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰⋰🇳⋰⋰🇦⋰ ⋰🇳⋰⋰🇦⋰ ⋰??⋰⋰🇮⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇸⋰⋰🇼⋰⋰🇮⋰⋰🇵⋰⋰🇪⋰ ⋰🇨⋰⋰🇷⋰⋰🇰⋰⋰🇪⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇭⋰⋰🇺⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇵⋰⋰🇷⋰ ⋰🇰⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰",
"⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰ ⋰🇵⋰⋰🇹⋰⋰🇦⋰ ⋰🇹⋰⋰🇭⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇲⋰⋰🇪⋰⋰🇾⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇳⋰⋰🇹⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰",
"⋰🇱⋰⋰🇴⋰⋰🇩⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇺⋰⋰🇹⋰⋰🇷⋰ ⋰🇲⋰⋰??⋰",
"⋰🇱⋰⋰🇺⋰⋰🇳⋰ ⋰🇲⋰⋰🇹⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇸⋰ ⋰🇲⋰⋰🇪⋰⋰🇷⋰⋰🇦⋰",
"⋰🇳⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇱⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰⋰🇨⋰⋰🇭⋰⋰🇩⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇴⋰⋰🇾⋰⋰🇪⋰ ⋰🇬⋰⋰🇦⋰⋰🇸⋰⋰🇭⋰⋰🇹⋰⋰🇮⋰ ⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰",
"⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇮⋰⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇹⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰",
"⋰🇲⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇰⋰ ⋰🇭⋰⋰🇦⋰⋰🇹⋰⋰🇭⋰ ⋰🇹⋰⋰🇴⋰⋰🇩⋰⋰🇭⋰ ⋰🇰⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇪⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇰⋰ ⋰🇲⋰⋰🇺⋰⋰🇭⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇫⋰⋰🇦⋰⋰🇸⋰⋰🇦⋰⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰??⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇵⋰⋰🇦⋰⋰🇸⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇳⋰⋰🇦⋰⋰🇮⋰ ⋰🇦⋰⋰🇾⋰⋰🇦⋰ ⋰🇲⋰⋰🇪⋰⋰🇰⋰⋰🇴⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇮⋰⋰🇩⋰⋰🇪⋰⋰🇷⋰ ⋰🇸⋰⋰🇪⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇯⋰⋰🇱⋰⋰🇩⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇼⋰⋰🇷⋰⋰🇳⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇱⋰⋰🇪⋰⋰🇬⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇸⋰⋰🇲⋰⋰🇯⋰⋰🇭⋰ ⋰🇧⋰⋰🇦⋰⋰🇹⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰",
"⋰🇫⋰⋰🇦⋰⋰🇸⋰⋰🇹⋰ ⋰🇱⋰⋰🇪⋰⋰🇦⋰⋰🇻⋰⋰🇪⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰⋰🇯⋰⋰🇴⋰⋰🇷⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰",
"⋰🇹⋰⋰🇺⋰⋰🇹⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰",
"⋰🇴⋰⋰🇾⋰ ⋰🇭⋰⋰🇮⋰⋰🇯⋰⋰🇩⋰⋰🇪⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰⋰🇳⋰⋰🇦⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰⋰🇿⋰⋰🇴⋰⋰🇷⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇴⋰ ⋰🇮⋰⋰🇱⋰⋰🇾⋰ ⋰🇷⋰⋰🇪⋰⋰🇾",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇹⋰⋰🇲⋰⋰🇰⋰⋰🇨⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰",
"⋰🇸⋰⋰🇭⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰",
"⋰🇫⋰⋰🇷⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰??⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰",
"⋰🇸⋰⋰🇭⋰⋰🇮⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰ ⋰🇼⋰⋰🇷⋰⋰🇳⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇾⋰⋰🇺⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰⋰🇨⋰⋰🇭⋰⋰🇦⋰⋰🇵⋰",
"⋰🇵⋰⋰🇷⋰⋰🇴⋰⋰🇴⋰⋰🇫⋰ ⋰🇨⋰⋰🇷⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇵⋰⋰🇷⋰⋰🇴⋰⋰🇴⋰⋰🇫⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰",
"⋰🇵⋰⋰🇷⋰⋰🇴⋰⋰🇴⋰⋰🇫⋰ ⋰🇭⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇰⋰⋰🇦⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇮⋰⋰🇱⋰⋰🇱⋰⋰🇦⋰⋰🇷⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇰⋰ ⋰🇧⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰ ⋰🇹⋰⋰🇪⋰⋰??⋰⋰🇾⋰",
"⋰🇴⋰⋰🇾⋰ ⋰🇭⋰⋰🇮⋰⋰🇯⋰⋰🇩⋰⋰🇪⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰⋰🇳⋰⋰🇦⋰ ⋰🇰⋰⋰🇭⋰⋰🇦⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰⋰🇿⋰⋰🇴⋰⋰🇷⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇲​⋰⋰🇦​⋰⋰🇩​⋰⋰🇷​⋰⋰🇨​⋰⋰🇭​⋰⋰🇴​⋰⋰🇩​⋰ ?",
"⋰🇦⋰⋰🇧⋰ ⋰🇹⋰⋰🇰⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇮⋰ ⋰🇭⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ?",
"⋰🇳⋰⋰🇾⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇰⋰⋰🇺⋰⋰🇨⋰⋰🇭⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇯⋰⋰🇦⋰⋰🇳⋰⋰🇹⋰⋰🇦⋰ ⋰🇧⋰⋰🇸⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰ ⋰🇪⋰⋰🇾⋰",
"⋰🇸⋰⋰🇧⋰⋰🇸⋰⋰🇪⋰ ⋰🇵⋰⋰🇭⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇴⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇳⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰⋰🇲⋰ ⋰🇰⋰⋰🇷⋰⋰🇪⋰",
"⋰🇾⋰⋰🇦⋰⋰🇭⋰⋰🇦⋰ ⋰🇧⋰⋰🇭⋰⋰🇮⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇨⋰⋰🇪⋰ ⋰🇵⋰⋰🇮⋰⋰🇱⋰⋰🇱⋰⋰🇪⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰⋰🇲⋰⋰🇦⋰⋰🇰⋰⋰🇦⋰⋰🇧⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇦⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇹⋰⋰🇴⋰ ⋰🇧⋰⋰🇭⋰⋰🇪⋰⋰🇳⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇪⋰⋰🇬⋰⋰🇮⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇵⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇹⋰⋰🇴⋰⋰🇲⋰⋰🇲⋰⋰🇾⋰",
"⋰🇳⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰⋰🇱⋰ ⋰🇲⋰⋰🇦⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰⋰🇨⋰⋰🇭⋰⋰🇩⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰ ⋰🇾⋰⋰🇭⋰⋰🇦⋰ ⋰🇸⋰⋰🇪⋰",
"⋰🇨⋰⋰🇴⋰⋰🇿⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇭⋰⋰🇮⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰ ⋰🇭⋰⋰🇪⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇵⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰ ⋰🇲⋰⋰🇺⋰⋰🇯⋰⋰🇭⋰⋰🇪⋰",
"⋰🇳⋰⋰🇾⋰⋰🇳⋰⋰🇾⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇭⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇯⋰⋰🇴⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰⋰🇹⋰⋰🇮⋰ ⋰🇯⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰",
"⋰🇹⋰⋰🇷⋰⋰🇾⋰ ⋰🇦⋰⋰🇲⋰⋰🇲⋰⋰🇮⋰ ⋰🇨⋰⋰🇪⋰ ⋰🇧⋰⋰🇭⋰⋰🇴⋰⋰🇸⋰⋰🇩⋰⋰🇪⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇪⋰⋰🇲⋰⋰🇴⋰⋰🇯⋰⋰🇮⋰ ⋰🇩⋰⋰🇦⋰⋰🇱⋰ ⋰🇲⋰⋰🇨⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇨⋰⋰🇭⋰⋰🇲⋰⋰🇷⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇦⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ?",
"⋰🇹⋰⋰🇲⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇷⋰⋰🇮⋰ ⋰🇭⋰⋰🇴⋰⋰🇬⋰⋰🇮⋰ ⋰🇫⋰⋰🇷⋰⋰🇷⋰⋰🇹⋰⋰🇴⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇰⋰⋰🇧⋰ ? ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇰⋰⋰🇪⋰⋰🇰⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇸⋰⋰🇨⋰⋰🇭⋰ ⋰🇲⋰⋰🇪⋰⋰🇾⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇷⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰⋰🇾⋰⋰🇰⋰⋰🇪⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇱⋰⋰🇮⋰ ⋰🇹⋰⋰🇺⋰⋰🇳⋰⋰🇪⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰",
"⋰🇮⋰⋰🇹⋰⋰🇳⋰⋰🇦⋰ ⋰🇸⋰⋰🇨⋰⋰🇭⋰ ⋰🇳⋰⋰🇾⋰ ⋰🇧⋰⋰🇴⋰⋰🇱⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇦⋰⋰🇮⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇾⋰",
"⋰🇸⋰⋰🇨⋰⋰🇭⋰ ⋰🇲⋰⋰🇪⋰⋰🇾⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇹⋰⋰🇺⋰ ⋰🇦⋰⋰🇵⋰⋰🇳⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇼⋰⋰🇦⋰ ⋰🇱⋰⋰🇮⋰⋰🇦⋰ ⋰🇲⋰⋰🇪⋰⋰🇷⋰⋰🇪⋰ ⋰🇸⋰⋰🇹⋰⋰🇭⋰",
"⋰🇲⋰⋰🇹⋰⋰🇱⋰⋰🇧⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰",
"⋰🇵⋰⋰🇺⋰⋰🇷⋰⋰🇦⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰ ⋰🇲⋰⋰🇨⋰",
"⋰🇹⋰⋰🇲⋰⋰🇷⋰ ⋰🇫⋰⋰🇷⋰⋰🇷⋰⋰🇹⋰⋰🇴⋰",
"⋰🇴⋰⋰🇭⋰ ⋰🇴⋰⋰🇰⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰ ⋰🇫⋰⋰🇮⋰⋰🇷⋰",
"⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇰⋰⋰🇦⋰ ⋰🇩⋰⋰🇦⋰⋰🇲⋰⋰🇦⋰⋰🇩⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰ ⋰🇸⋰⋰🇪⋰ ⋰🇱⋰⋰🇮⋰⋰🇰⋰⋰🇭⋰⋰🇪⋰ ⋰🇵⋰⋰🇪⋰⋰🇭⋰⋰🇱⋰⋰🇪⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇪⋰⋰🇧⋰⋰🇦⋰⋰🇨⋰⋰🇭⋰⋰🇪⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇳⋰⋰🇪⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇻⋰⋰🇾⋰⋰🇦⋰⋰🇸⋰⋰🇹⋰ ⋰🇭⋰⋰🇺⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇰⋰⋰🇺⋰⋰🇨⋰⋰🇭⋰ ⋰🇧⋰⋰🇮⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ? ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇬⋰⋰🇾⋰⋰🇦⋰ ?",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇲⋰⋰🇹⋰ ⋰🇭⋰⋰🇸⋰⋰🇸⋰",
"⋰🇾⋰⋰🇺⋰⋰🇷⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇲⋰⋰🇴⋰⋰🇲⋰",
"⋰🇦⋰⋰🇷⋰⋰🇪⋰ ⋰🇸⋰⋰🇧⋰⋰🇰⋰⋰🇮⋰ ⋰🇲⋰⋰??⋰⋰🇦⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇴⋰⋰🇷⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇧⋰⋰🇮⋰",
"⋰🇦⋰⋰🇷⋰⋰🇪⋰ ⋰🇮⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰ ⋰🇪⋰⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇷⋰",
"⋰🇹⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇮⋰ ⋰🇹⋰⋰🇷⋰⋰🇭⋰",
"⋰🇪⋰⋰🇰⋰ ⋰🇱⋰⋰🇮⋰⋰🇳⋰⋰🇪⋰ ⋰🇲⋰⋰🇪⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰",
"⋰🇶⋰",
"⋰🇴⋰⋰🇨⋰⋰🇾⋰ ⋰🇦⋰⋰🇧⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇱⋰⋰🇪⋰",
"⋰🇵⋰⋰🇪⋰⋰🇭⋰⋰🇪⋰⋰🇱⋰⋰🇪⋰ ⋰🇹⋰⋰🇪⋰⋰🇷⋰⋰🇮⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰ ⋰🇨⋰⋰🇭⋰⋰🇴⋰⋰🇩⋰⋰🇺⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰",
"⋰🇶⋰ ?",
"⋰??⋰⋰🇾⋰⋰🇾⋰⋰🇾⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰ ⋰🇪⋰⋰🇰⋰ ⋰🇧⋰⋰🇦⋰⋰🇦⋰⋰🇷⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇸⋰⋰🇺⋰⋰🇳⋰ ⋰🇩⋰⋰🇴⋰⋰🇸⋰⋰🇹⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰",
"⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰ ⋰🇷⋰⋰🇦⋰⋰🇦⋰⋰🇳⋰⋰🇩⋰ ⋰🇲⋰⋰🇦⋰⋰🇦⋰⋰🇫⋰ ⋰🇨⋰⋰🇷⋰⋰🇷⋰ ⋰🇩⋰⋰🇺⋰⋰🇳⋰⋰🇬⋰⋰🇦⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇷⋰⋰🇳⋰⋰🇩⋰⋰🇮⋰⊶⊶🇮⋰ ⋰🇮⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰ ⋰🇦⋰⋰🇦⋰",
"⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇹⋰⋰🇲⋰⋰🇷⋰ ⋰🇫⋰⋰🇷⋰⋰🇷⋰⋰🇹⋰⋰🇴⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇮⋰⋰🇩⋰⋰🇦⋰⋰🇷⋰ ⋰🇦⋰⋰🇦⋰⋰🇰⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇱⋰⋰🇪⋰ ⋰🇨⋰⋰🇭⋰⋰🇲⋰⋰🇷⋰",
"⋰🇳⋰⋰🇾⋰⋰🇹⋰⋰🇴⋰ ⋰🇦⋰⋰🇪⋰⋰🇸⋰⋰🇪⋰ ⋰🇭⋰⋰🇮⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰",
"⋰🇴⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇭⋰⋰🇾⋰⋰🇾⋰ ⋰🇦⋰⋰🇮⋰⋰🇸⋰⋰🇪⋰ ⋰🇭⋰⋰🇮⋰ ⋰🇨⋰⋰🇺⋰⋰🇩⋰ ⋰🇱⋰⋰🇪⋰⋰🇳⋰⋰🇦⋰",
"⋰🇴⋰⋰🇷⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇱⋰⋰🇪⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇰⋰⋰🇪⋰ ⋰🇩⋰⋰🇮⋰⋰🇰⋰⋰🇦⋰ ⋰🇴⋰⋰🇷⋰",
"⋰🇭⋰⋰🇾⋰⋰🇾⋰ ⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇴⋰ ⋰??⋰⋰🇦⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰⋰🇴⋰ ⋰🇲⋰⋰🇹⋰ ⋰🇧⋰⋰🇭⋰⋰🇦⋰⋰🇬⋰ ⋰🇯⋰⋰🇦⋰⋰🇴⋰",
"⋰🇧⋰⋰🇾⋰⋰🇾⋰⋰🇪⋰⋰🇪⋰ ⋰🇭⋰⋰🇾⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ?",
"⋰🇶⋰⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇶⋰ ⋰🇷⋰⋰🇭⋰⋰🇪⋰ ⋰🇭⋰⋰🇴⋰ ?",
"⋰🇵⋰⋰🇬⋰⋰🇱⋰ ⋰🇪⋰⋰🇾⋰ ⋰🇨⋰⋰🇾⋰⋰🇦⋰ ⋰🇲⋰⋰🇨⋰",
"⋰🇨⋰⋰🇭⋰⋰🇺⋰⋰🇩⋰ ⋰🇲⋰⋰🇹⋰",
]


bs3_texts = [
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰ ⋰🅃⋰⋰🄾⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄳⋰⋰??⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄼⋰⋰🅄⋰⋰🄷⋰ ⋰🄼⋰⋰🄴⋰ ⋰🅁⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄳⋰ ⋰🄳⋰⋰🅄⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰??⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄼⋰⋰🄰⋰⋰🅂⋰⋰🄰⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰",
"⋰🄵⋰⋰🄰⋰⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄿⋰⋰🄴⋰ ⋰🅃⋰⋰🄷⋰⋰🄰⋰⋰🄿⋰⋰🄿⋰⋰🄰⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰",
"⋰🅇⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄷⋰⋰🄴⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰??⋰⋰🄳⋰",
"⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🅄⋰⋰🄳⋰⋰🄷⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄸⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄷⋰⋰🄴⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄰⋰⋰🄺⋰⋰🄴⋰⋰🄻⋰⋰🄰⋰ ⋰🄿⋰⋰🄰⋰⋰🄽⋰ ⋰🄼⋰⋰🄸⋰⋰🅃⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄸⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰ ⋰🅇⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄿⋰⋰🄿⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄽⋰⋰🄰⋰⋰🄽⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🄾⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🅁⋰⋰🅁⋰ ⋰🄵⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄵⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰??⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄻⋰⋰🄰⋰⋰🄰⋰⋰🄼⋰⋰🄼⋰⋰🄼⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄾⋰⋰🄾⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄰⋰⋰🄰⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄶⋰⋰🄶⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄳⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰⋰🄽⋰ ⋰🄷⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰⋰🄷⋰⋰🄷⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰ ⋰??⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰",
"⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄿⋰⋰🄰⋰⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰ ⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄰⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🄽⋰⋰🄰⋰⋰🄽⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄰⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄳⋰ ⋰🄺⋰⋰🄸⋰⋰🄳⋰⋰🄳⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅂⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🅅⋰⋰🄾⋰⋰🄸⋰⋰🄲⋰⋰🄴⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🅂⋰⋰🄰⋰⋰🄺⋰⋰🅃⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄸⋰⋰🄶⋰⋰🄽⋰⋰🄾⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🅄⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄸⋰⋰🄶⋰⋰🄽⋰⋰🄾⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🅁⋰⋰🄰⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰??⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄰⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰ ⋰🄹⋰⋰🅄⋰⋰🄱⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰??⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄽⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄼⋰⋰🄰⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄱⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄻⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰ ⋰🄰⋰⋰🄱⋰ ⋰🅃⋰⋰🅄⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰⋰🅁⋰ ⋰🄶⋰⋰??⋰⋰🅄⋰⋰🄼⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄸⋰⋰🄽⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄹⋰⋰🄷⋰⋰🅄⋰⋰🄺⋰⋰🄽⋰⋰🄴⋰ ⋰🄽⋰⋰🄰⋰⋰🄸⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰ ⋰🄷⋰⋰🄾⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄽⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🅃⋰⋰🄾⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄰⋰⋰🅃⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰⋰🄹⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🄿⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🅁⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰??⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄾⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄱⋰⋰🄷⋰⋰🄸⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰??⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🄶⋰⋰🄰⋰⋰🄸⋰⋰🅁⋰⋰🄱⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄸⋰ ⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅃⋰⋰🄲⋰⋰🄷⋰ ⋰🄺⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🄶⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰⋰🄱⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄴⋰⋰🄴⋰⋰🄹⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰??⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄾⋰ ⋰🅃⋰⋰🄰⋰⋰🄶⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄻⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰ ⋰🄰⋰⋰🄱⋰ ⋰🅃⋰⋰🅄⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰⋰🅁⋰ ⋰🄶⋰⋰🄷⋰⋰🅄⋰⋰🄼⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄸⋰⋰🄽⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄹⋰⋰🄷⋰⋰🅄⋰⋰🄺⋰⋰🄽⋰⋰🄴⋰ ⋰🄽⋰⋰🄰⋰⋰🄸⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰ ⋰🄷⋰⋰🄾⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰??⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰??⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄽⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🅃⋰⋰🄾⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄰⋰⋰🅃⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰??⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰⋰🄹⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰??⋰⋰🄶⋰⋰🄰⋰",
"⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🄿⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🅁⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄾⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄱⋰⋰🄷⋰⋰🄸⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🄶⋰⋰🄰⋰⋰🄸⋰⋰🅁⋰⋰🄱⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄸⋰ ⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅃⋰⋰🄲⋰⋰🄷⋰ ⋰🄺⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🄶⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰⋰🄱⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄴⋰⋰🄴⋰⋰🄹⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄾⋰ ⋰🅃⋰⋰🄰⋰⋰🄶⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰"
]


sqs_texts = [
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰ ⋰🅃⋰⋰🄾⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄳⋰⋰??⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄼⋰⋰🅄⋰⋰🄷⋰ ⋰🄼⋰⋰🄴⋰ ⋰🅁⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄳⋰ ⋰🄳⋰⋰🅄⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰??⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄼⋰⋰🄰⋰⋰🅂⋰⋰🄰⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰",
"⋰🄵⋰⋰🄰⋰⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄿⋰⋰🄴⋰ ⋰🅃⋰⋰🄷⋰⋰🄰⋰⋰🄿⋰⋰🄿⋰⋰🄰⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰",
"⋰🅇⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄷⋰⋰🄴⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰??⋰⋰🄳⋰",
"⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🅄⋰⋰🄳⋰⋰🄷⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄸⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄷⋰⋰🄴⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄰⋰⋰🄺⋰⋰🄴⋰⋰🄻⋰⋰🄰⋰ ⋰🄿⋰⋰🄰⋰⋰🄽⋰ ⋰🄼⋰⋰🄸⋰⋰🅃⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄸⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰ ⋰🅇⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄿⋰⋰🄿⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄽⋰⋰🄰⋰⋰🄽⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🄾⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🅁⋰⋰🅁⋰ ⋰🄵⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄵⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰??⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄻⋰⋰🄰⋰⋰🄰⋰⋰🄼⋰⋰🄼⋰⋰🄼⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄾⋰⋰🄾⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄺⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄰⋰⋰🄰⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄶⋰⋰🄶⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄳⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰⋰🄽⋰ ⋰🄷⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰⋰🄷⋰⋰🄷⋰ ⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄻⋰⋰🄻⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰⋰🄹⋰ ⋰??⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰⋰🄽⋰⋰🄽⋰",
"⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄿⋰⋰🄰⋰⋰🄺⋰⋰🄰⋰⋰🄰⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🅁⋰⋰🅁⋰ ⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄰⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄳⋰⋰🄳⋰ ⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰⋰🄴⋰⋰🄴⋰",
"⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🄽⋰⋰🄰⋰⋰🄽⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰⋰🅃⋰ ⋰🄺⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄴⋰⋰🄽⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🄰⋰⋰🅁⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄳⋰ ⋰🄺⋰⋰🄸⋰⋰🄳⋰⋰🄳⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅂⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🅅⋰⋰🄾⋰⋰🄸⋰⋰🄲⋰⋰🄴⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🅂⋰⋰🄰⋰⋰🄺⋰⋰🅃⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄸⋰⋰🄶⋰⋰🄽⋰⋰🄾⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🅄⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄸⋰⋰🄶⋰⋰🄽⋰⋰🄾⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🅁⋰⋰🄰⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰⋰🄸⋰ ⋰??⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🄻⋰⋰🄾⋰⋰🄳⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄻⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄰⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄻⋰⋰🄸⋰ ⋰🄹⋰⋰🅄⋰⋰🄱⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰??⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄽⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄼⋰⋰🄰⋰⋰🄸⋰ ⋰🄺⋰⋰🄰⋰⋰🄱⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄴⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄻⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰ ⋰🄰⋰⋰🄱⋰ ⋰🅃⋰⋰🅄⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰⋰🅁⋰ ⋰🄶⋰⋰??⋰⋰🅄⋰⋰🄼⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄸⋰⋰🄽⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄹⋰⋰🄷⋰⋰🅄⋰⋰🄺⋰⋰🄽⋰⋰🄴⋰ ⋰🄽⋰⋰🄰⋰⋰🄸⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰ ⋰🄷⋰⋰🄾⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄽⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🅃⋰⋰🄾⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄰⋰⋰🅃⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰⋰🄹⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🄿⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🅁⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰??⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄾⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄱⋰⋰🄷⋰⋰🄸⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰??⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🄶⋰⋰🄰⋰⋰🄸⋰⋰🅁⋰⋰🄱⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄸⋰ ⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅃⋰⋰🄲⋰⋰🄷⋰ ⋰🄺⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🄶⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰⋰🄱⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄴⋰⋰🄴⋰⋰🄹⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰??⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄾⋰ ⋰🅃⋰⋰🄰⋰⋰🄶⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄰⋰⋰🅃⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰ ⋰🄹⋰⋰🄰⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄻⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰ ⋰🄰⋰⋰🄱⋰ ⋰🅃⋰⋰🅄⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰⋰🅁⋰ ⋰🄶⋰⋰🄷⋰⋰🅄⋰⋰🄼⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄻⋰⋰🄴⋰⋰🄺⋰⋰🄸⋰⋰🄽⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄹⋰⋰🄷⋰⋰🅄⋰⋰🄺⋰⋰🄽⋰⋰🄴⋰ ⋰🄽⋰⋰🄰⋰⋰🄸⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰ ⋰🄱⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰⋰🄰⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄰⋰ ⋰🅁⋰⋰🄴⋰⋰🄿⋰⋰🄻⋰⋰🅈⋰ ⋰🄷⋰⋰🄾⋰⋰🄶⋰⋰🄰⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰??⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰??⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰⋰🄽⋰⋰🄰⋰ ⋰🄲⋰⋰🄷⋰⋰🄰⋰⋰🄻⋰⋰🅄⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🅃⋰⋰🄾⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄱⋰⋰🄾⋰⋰🄻⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🅄⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄰⋰⋰🅃⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🅁⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰??⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄷⋰⋰🄾⋰⋰🄹⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🅄⋰⋰🅃⋰⋰🄷⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄵⋰⋰🄴⋰⋰🄽⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰??⋰⋰🄶⋰⋰🄰⋰",
"⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🄿⋰ ⋰🄼⋰⋰🄰⋰⋰🄳⋰⋰🅁⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄾⋰⋰🄳⋰",
"⋰🄹⋰⋰🄰⋰⋰🄻⋰⋰🄳⋰⋰🄸⋰ ⋰🄹⋰⋰🄸⋰⋰🄽⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰ ⋰🄹⋰⋰🄰⋰⋰🅈⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄻⋰⋰🄰⋰⋰🅄⋰⋰🄳⋰⋰🄴⋰ ⋰🄿⋰⋰🄴⋰",
"⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰ ⋰🄰⋰⋰🄿⋰⋰🄽⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄳⋰⋰🄸⋰⋰🄺⋰⋰🄷⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄲⋰⋰🄷⋰⋰🅄⋰⋰🅃⋰ ⋰🄺⋰⋰🄾⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰⋰🄾⋰ ⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄼⋰⋰🄴⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🅂⋰⋰🄰⋰⋰🅃⋰⋰🄷⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄱⋰⋰🄷⋰⋰🄸⋰ ⋰🄳⋰⋰🄰⋰⋰🄵⋰⋰🄰⋰⋰🄽⋰ ⋰🄷⋰⋰🄾⋰ ⋰🄹⋰⋰🄰⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🄱⋰⋰🄷⋰⋰🄰⋰⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄰⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄷⋰⋰🄰⋰⋰🄸⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🅂⋰⋰🄴⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰",
"⋰🄶⋰⋰🄰⋰⋰🄸⋰⋰🅁⋰⋰🄱⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄰⋰⋰🅄⋰⋰🄻⋰⋰🄰⋰⋰🄳⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄼⋰⋰🄰⋰⋰🅁⋰⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰",
"⋰🄱⋰⋰🄰⋰⋰🄰⋰⋰🄰⋰⋰🄿⋰ ⋰🄺⋰⋰🄸⋰ ⋰🅂⋰⋰🄿⋰⋰🄴⋰⋰🄴⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🅃⋰⋰🄲⋰⋰🄷⋰ ⋰🄺⋰⋰🅁⋰⋰🄴⋰⋰🄶⋰⋰🄰⋰ ⋰🄶⋰⋰🄰⋰⋰🅁⋰⋰🄸⋰⋰🄱⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄲⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰ ⋰🄺⋰⋰🄰⋰⋰🅃⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄵⋰⋰🄴⋰⋰🄺⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄴⋰⋰🄴⋰⋰🄹⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄴⋰ ⋰🄱⋰⋰🄷⋰⋰🄾⋰⋰🅂⋰⋰🄳⋰⋰🄰⋰⋰🄳⋰⋰🄴⋰ ⋰🄼⋰⋰🄴⋰⋰🄸⋰⋰🄽⋰ ⋰🄲⋰⋰🄿⋰ ⋰🄺⋰⋰🄰⋰⋰🅁⋰ ⋰🄳⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰ ⋰🄽⋰⋰🄸⋰⋰🄺⋰⋰🄰⋰⋰🄻⋰",
"⋰🄰⋰⋰🄰⋰⋰🄹⋰ ⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🅁⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄽⋰⋰🄰⋰⋰🄷⋰⋰🄸⋰ ⋰🄱⋰⋰🄰⋰⋰🄲⋰⋰🄷⋰⋰🄴⋰⋰🄶⋰⋰🄸⋰ ⋰🅃⋰⋰🅄⋰ ⋰🄼⋰⋰🄴⋰⋰🅁⋰⋰🄴⋰ ⋰🄺⋰⋰🄾⋰ ⋰🅃⋰⋰🄰⋰⋰🄶⋰ ⋰🄺⋰⋰🄰⋰⋰🄸⋰⋰🅂⋰⋰🄴⋰ ⋰🄺⋰⋰🄸⋰⋰🅈⋰⋰🄰⋰",
"⋰🅃⋰⋰🄴⋰⋰🅁⋰⋰🄸⋰ ⋰🄼⋰⋰🅄⋰⋰🄼⋰⋰🄼⋰⋰🅈⋰ ⋰🄺⋰⋰🄸⋰ ⋰🄶⋰⋰🄰⋰⋰🄽⋰⋰🄳⋰ ⋰🄼⋰⋰🄰⋰⋰🄰⋰⋰🅁⋰ ⋰🄻⋰⋰🅄⋰⋰🄽⋰⋰🄶⋰⋰🄰⋰"
]

sqr_texts = [
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ, ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓒ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ",
"⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓑ⊶Ⓗ⊶Ⓘ ⊶Ⓑ⊶Ⓝ⊶Ⓐ⊶Ⓛ⊶Ⓔ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓔ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓩ ⊶Ⓔ⊶Ⓨ ⊶Ⓨ⊶Ⓐ⊶Ⓐ⊶Ⓓ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓝ⊶Ⓐ ⊶Ⓣ⊶Ⓨ⊶Ⓜ⊶Ⓟ⊶Ⓐ⊶Ⓢ⊶Ⓢ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓤ⊶Ⓝ⊶Ⓕ⊶Ⓤ⊶Ⓝ⊶Ⓝ⊶Ⓨ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓜ⊶Ⓣ⊶Ⓣ ⊶Ⓚ⊶Ⓡ",
"⊶Ⓞ⊶Ⓗ ⊶Ⓗ⊶Ⓔ⊶Ⓛ⊶Ⓛ⊶Ⓞ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓤ ⊶Ⓥ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓤ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓡ.",
"⊶Ⓞ⊶Ⓨ⊶Ⓨ ⊶Ⓚ⊶Ⓘ⊶Ⓝ⊶Ⓝ⊶Ⓔ⊶Ⓡ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓖ⊶Ⓒ ⊶Ⓜ⊶Ⓔ ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓔ ⊶Ⓚ⊶Ⓘ ⊶Ⓟ⊶Ⓔ⊶Ⓡ⊶Ⓜ⊶Ⓘ⊶Ⓢ⊶Ⓢ⊶Ⓘ⊶Ⓞ⊶Ⓝ ⊶Ⓚ⊶Ⓘ⊶Ⓢ⊶Ⓝ⊶Ⓔ ⊶Ⓓ⊶Ⓘ.",
"⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ",
"⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓡ.",
"⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓐ.",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓒ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ.",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓘ ⊶Ⓙ⊶Ⓐ⊶Ⓣ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓜ⊶Ⓡ.",
"⊶Ⓚ⊶Ⓨ? ⊶Ⓙ⊶Ⓛ⊶Ⓓ⊶Ⓘ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓚ⊶Ⓘ⊶Ⓓ⊶Ⓓ⊶Ⓔ.",
"⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓒ⊶Ⓞ⊶Ⓜ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓖ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓐ⊶Ⓖ ⊶Ⓒ⊶Ⓡ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓑ⊶Ⓢ",
"⊶Ⓙ⊶Ⓐ⊶Ⓛ⊶Ⓓ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓩ ⊶Ⓟ⊶Ⓐ⊶Ⓟ⊶Ⓐ ⊶Ⓑ⊶Ⓞ⊶Ⓛ",
"⊶Ⓢ⊶Ⓘ⊶Ⓓ⊶Ⓔ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ ⊶Ⓑ⊶Ⓘ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓐ⊶Ⓑ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓑ⊶Ⓗ⊶Ⓖ ⊶Ⓜ⊶Ⓐ⊶Ⓣ ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ",
"⊶Ⓑ⊶Ⓗ⊶Ⓖ ⊶Ⓝ⊶Ⓨ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓙ⊶Ⓙ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ ⊶Ⓜ⊶Ⓐ⊶Ⓣ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓓ⊶Ⓤ⊶Ⓡ ⊶Ⓗ⊶Ⓐ⊶Ⓣ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓗ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓔ⊶Ⓢ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓕ ⊶Ⓒ⊶Ⓡ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓗ⊶Ⓤ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓕ⊶Ⓘ ⊶Ⓓ⊶Ⓔ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓕ⊶Ⓘ ⊶Ⓜ⊶Ⓘ⊶Ⓛ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓖ⊶Ⓘ ⊶Ⓣ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓔ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓒ⊶Ⓡ⊶Ⓚ⊶Ⓔ",
"⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓒ⊶Ⓡ⊶Ⓚ⊶Ⓔ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓑ⊶Ⓞ⊶Ⓛ⊶Ⓝ⊶Ⓐ ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓢ⊶Ⓦ⊶Ⓘ⊶Ⓟ⊶Ⓔ ⊶Ⓒ⊶Ⓡ⊶Ⓚ⊶Ⓔ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓤ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓚ⊶Ⓔ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓛ⊶Ⓞ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓤ⊶Ⓣ⊶Ⓡ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓛ⊶Ⓤ⊶Ⓝ ⊶Ⓜ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓢ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ",
"⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓓ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓢ⊶Ⓗ⊶Ⓣ⊶Ⓘ ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ ⊶Ⓗ⊶Ⓐ⊶Ⓣ⊶Ⓗ ⊶Ⓣ⊶Ⓞ⊶Ⓓ⊶Ⓗ ⊶Ⓚ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓚ ⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ ⊶Ⓕ⊶Ⓐ⊶Ⓢ⊶Ⓐ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓢ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓝ⊶Ⓐ⊶Ⓘ ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓚ⊶Ⓞ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓔ⊶Ⓡ ⊶Ⓢ⊶Ⓔ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓙ⊶Ⓛ⊶Ⓓ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓝ⊶Ⓨ ⊶Ⓛ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ",
"⊶Ⓕ⊶Ⓐ⊶Ⓢ⊶Ⓣ ⊶Ⓛ⊶Ⓔ⊶Ⓐ⊶Ⓥ⊶Ⓔ ⊶Ⓛ⊶Ⓔ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓣ⊶Ⓤ⊶Ⓣ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ",
"⊶Ⓞ⊶Ⓨ ⊶Ⓗ⊶Ⓘ⊶Ⓙ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓩ⊶Ⓞ⊶Ⓡ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ ⊶Ⓘ⊶Ⓛ⊶Ⓨ ⊶Ⓡ⊶Ⓔ⊶Ⓨ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ",
"⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓨ⊶Ⓤ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶ⓒ⊶ⓤ⊶ⓓ⊶ⓦ⊶ⓐ",
"⊶Ⓟ⊶Ⓡ⊶Ⓞ⊶Ⓞ⊶Ⓕ ⊶Ⓒ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ⊶Ⓞ⊶Ⓞ⊶Ⓕ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ⊶Ⓞ⊶Ⓞ⊶Ⓕ ⊶Ⓗ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓚ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓐ⊶Ⓡ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ ⊶Ⓑ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓞ⊶Ⓨ ⊶Ⓗ⊶Ⓘ⊶Ⓙ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓩ⊶Ⓞ⊶Ⓡ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶ⓜ⊶ⓐ⊶ⓓ⊶ⓡ⊶ⓒ⊶ⓗ⊶ⓞ⊶ⓓ?",
"⊶Ⓐ⊶Ⓑ ⊶Ⓣ⊶Ⓚ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓗ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ?",
"⊶Ⓝ⊶Ⓨ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓔ ⊶Ⓚ⊶Ⓤ⊶Ⓒ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓙ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓑ⊶Ⓢ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓢ⊶Ⓑ⊶Ⓢ⊶Ⓔ ⊶Ⓟ⊶Ⓗ⊶Ⓔ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓞ⊶Ⓛ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓜ ⊶Ⓚ⊶Ⓡ⊶Ⓔ",
"⊶Ⓨ⊶Ⓐ⊶Ⓗ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓒ⊶Ⓔ ⊶Ⓟ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓐ⊶Ⓑ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓣ⊶Ⓞ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓔ⊶Ⓖ⊶Ⓘ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓞ⊶Ⓜ⊶Ⓜ⊶Ⓨ",
"⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓓ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓨ⊶Ⓗ⊶Ⓐ ⊶Ⓢ⊶Ⓔ",
"⊶Ⓒ⊶Ⓞ⊶Ⓩ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓗ⊶Ⓘ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓗ⊶Ⓔ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓑ⊶Ⓞ⊶Ⓛ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ",
"⊶Ⓝ⊶Ⓨ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓗ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓙ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ⊶Ⓣ⊶Ⓘ ⊶Ⓙ⊶Ⓞ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓘ ⊶Ⓒ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓔ⊶Ⓜ⊶Ⓞ⊶Ⓙ⊶Ⓘ ⊶Ⓓ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓒ⊶Ⓗ⊶Ⓜ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓣ⊶Ⓜ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓡ⊶Ⓘ ⊶Ⓗ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓕ⊶Ⓡ⊶Ⓡ⊶Ⓣ⊶Ⓞ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓚ⊶Ⓑ ? ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓚ⊶Ⓔ⊶Ⓚ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓘ ⊶Ⓣ⊶Ⓤ⊶Ⓝ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ",
"⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓐ ⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓑ⊶Ⓞ⊶Ⓛ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓣ⊶Ⓗ",
"⊶Ⓜ⊶Ⓣ⊶Ⓛ⊶Ⓑ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ",
"⊶Ⓟ⊶Ⓤ⊶Ⓡ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓣ⊶Ⓜ⊶Ⓡ ⊶Ⓕ⊶Ⓡ⊶Ⓡ⊶Ⓣ⊶Ⓞ",
"⊶Ⓞ⊶Ⓗ ⊶Ⓞ⊶Ⓚ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓕ⊶Ⓘ⊶Ⓡ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓐ⊶Ⓜ⊶Ⓐ⊶Ⓓ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓔ ⊶Ⓟ⊶Ⓔ⊶Ⓗ⊶Ⓛ⊶Ⓔ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓔ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓥ⊶Ⓨ⊶Ⓐ⊶Ⓢ⊶Ⓣ ⊶Ⓗ⊶Ⓤ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓚ⊶Ⓤ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓘ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ? ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓜ⊶Ⓣ ⊶Ⓗ⊶Ⓢ⊶Ⓢ",
"⊶Ⓨ⊶Ⓤ⊶Ⓡ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓜ⊶Ⓞ⊶Ⓜ",
"⊶Ⓐ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓑ⊶Ⓚ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓘ",
"⊶Ⓐ⊶Ⓡ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓡ",
"⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓘ ⊶Ⓣ⊶Ⓡ⊶Ⓗ",
"⊶Ⓔ⊶Ⓚ ⊶Ⓛ⊶Ⓘ⊶Ⓝ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓠ",
"⊶Ⓞ⊶Ⓒ⊶Ⓨ ⊶Ⓐ⊶Ⓑ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ",
"⊶Ⓟ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ",
"⊶Ⓠ ?",
"⊶Ⓗ⊶Ⓨ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓐ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓡ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓓ⊶Ⓞ⊶Ⓢ⊶Ⓣ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ ⊶Ⓙ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓕ ⊶Ⓒ⊶Ⓡ⊶Ⓡ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓜ⊶Ⓡ ⊶Ⓕ⊶Ⓡ⊶Ⓡ⊶Ⓣ⊶Ⓞ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓛ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓜ⊶Ⓡ",
"⊶Ⓝ⊶Ⓨ⊶Ⓣ⊶Ⓞ ⊶Ⓐ⊶Ⓔ⊶Ⓢ⊶Ⓔ ⊶Ⓗ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓗ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓛ⊶Ⓔ⊶Ⓝ⊶Ⓐ",
"⊶Ⓞ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓛ⊶Ⓔ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓐ ⊶Ⓞ⊶Ⓡ",
"⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓞ ⊶Ⓝ⊶Ⓐ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓞ ⊶Ⓜ⊶Ⓣ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ ⊶Ⓙ⊶Ⓐ⊶Ⓞ",
"⊶Ⓑ⊶Ⓨ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓠ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓠ ⊶Ⓡ⊶Ⓗ⊶Ⓔ ⊶Ⓗ⊶Ⓞ ?",
"⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓜ⊶Ⓣ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶⊶Ⓘ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓘ ⊶Ⓒ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓚ⊶Ⓜ⊶Ⓩ⊶Ⓡ⊶Ⓞ⊶Ⓡ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓔ⊶Ⓚ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ?",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ?",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓢ⊶Ⓛ⊶Ⓘ⊶Ⓓ⊶Ⓔ ⊶Ⓛ⊶Ⓔ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶ⒶⓉ ⊶Ⓒ⊶Ⓡ⊶Ⓜ⊶Ⓒ",
"⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓒ⊶Ⓟ ⊶Ⓜ⊶Ⓣ ⊶Ⓒ⊶Ⓡ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓐ",
"⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓢ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓕ⊶Ⓤ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓡ",
"⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ ⊶Ⓙ⊶Ⓐ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓗ⊶Ⓨ⊶Ⓨ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓚ⊶Ⓜ⊶Ⓩ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓒ ⊶Ⓘ⊶Ⓓ⊶Ⓐ⊶Ⓡ ⊶Ⓐ⊶Ⓐ",
"⊶Ⓨ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓜ⊶Ⓡ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓝ⊶Ⓨ ⊶Ⓒ⊶Ⓟ ⊶Ⓝ⊶Ⓨ ⊶Ⓒ⊶Ⓡ⊶Ⓡ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ⊶Ⓔ ⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓜ⊶Ⓣ ⊶Ⓒ⊶Ⓡ⊶Ⓡ",
"⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓡ⊶ⒶⓂ ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓒ",
"⊶Ⓟ⊶Ⓖ⊶Ⓛ ⊶Ⓔ⊶Ⓨ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓔ⊶Ⓚ",
"⊶Ⓒ⊶Ⓟ ⊶Ⓒ⊶Ⓡ⊶Ⓒ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓔ⊶Ⓖ⊶Ⓐ !",
"⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ? ⊶Ⓜ⊶Ⓒ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓐ⊶Ⓟ ⊶Ⓝ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓘ ⊶Ⓤ⊶Ⓟ⊶Ⓐ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓡ⊶Ⓞ⊶Ⓒ⊶Ⓚ⊶Ⓔ⊶Ⓣ ⊶Ⓟ⊶Ⓔ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ ⊶Ⓒ⊶Ⓔ ⊶ⒷⓈⓈ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓤ",
"⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ",
"⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶ⓉⓇ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓚ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓔ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓜ⊶Ⓐ⊶Ⓘ⊶Ⓝ ⊶Ⓑ⊶Ⓤ⊶Ⓡ⊶Ⓕ",
"⊶Ⓑ⊶Ⓗ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓙ⊶Ⓗ⊶Ⓐ⊶Ⓣ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓐ ⊶Ⓛ⊶Ⓔ",
"⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓜ⊶Ⓐ⊶Ⓘ⊶Ⓝ ⊶Ⓜ⊶Ⓞ⊶Ⓤ⊶Ⓝ⊶Ⓣ ⊶Ⓔ⊶Ⓥ⊶Ⓔ⊶Ⓡ⊶Ⓔ⊶Ⓢ⊶Ⓣ",
"⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓨ ⊶Ⓛ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ",
"⊶Ⓗ⊶Ⓘ⊶Ⓙ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓘ ⊶Ⓙ⊶Ⓗ⊶Ⓐ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓦ⊶Ⓡ⊶Ⓝ⊶Ⓐ ⊶ⓉⓇ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓝ⊶Ⓨ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓚ⊶Ⓘ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓢ⊶Ⓑ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓣ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓤ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓔ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓣ⊶Ⓗ⊶Ⓝ⊶Ⓚ⊶Ⓢ⊶Ⓢ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ",
"⊶Ⓑ⊶Ⓢ ⊶Ⓑ⊶Ⓢ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓑ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓖ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓢ⊶Ⓐ⊶Ⓑ⊶Ⓘ⊶Ⓣ ⊶Ⓚ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓤ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓔ⊶Ⓐ⊶Ⓢ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓔ⊶Ⓐ⊶Ⓢ⊶Ⓨ ⊶Ⓦ⊶8 ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓐ⊶Ⓑ",
"⊶Ⓢ⊶Ⓐ⊶Ⓝ⊶Ⓢ ⊶Ⓐ⊶Ⓡ⊶Ⓘ ⊶Ⓗ⊶Ⓐ ⊶Ⓚ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓖ⊶Ⓘ ⊶Ⓐ⊶Ⓙ⊶Ⓙ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓘ⊶Ⓝ⊶Ⓐ ⊶Ⓢ⊶Ⓐ⊶Ⓝ⊶Ⓢ⊶Ⓢ ⊶Ⓛ⊶Ⓔ⊶Ⓣ⊶Ⓔ ⊶Ⓗ⊶Ⓤ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓟ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓔ ⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ",
"⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓡ⊶Ⓜ⊶Ⓘ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓡ⊶Ⓜ⊶Ⓘ⊶Ⓔ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓢ ⊶Ⓣ⊶Ⓗ⊶Ⓔ⊶Ⓚ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓢ ⊶Ⓣ⊶Ⓗ⊶Ⓔ⊶Ⓚ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ",
"⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓗ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓔ⊶Ⓢ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ",
"⊶Ⓜ⊶Ⓐ⊶Ⓘ ⊶Ⓢ⊶Ⓑ ⊶Ⓙ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓒ⊶Ⓗ⊶Ⓛ ⊶Ⓒ⊶Ⓗ⊶Ⓛ ⊶Ⓗ⊶Ⓣ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓢ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓚ⊶Ⓐ⊶Ⓜ⊶Ⓙ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓒ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓣ ⊶Ⓖ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓐ ⊶Ⓖ⊶Ⓝ⊶Ⓓ⊶Ⓐ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓑ⊶Ⓣ⊶Ⓐ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓕ⊶Ⓘ⊶Ⓡ ⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓝ⊶Ⓨ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓝ⊶Ⓨ ⊶Ⓚ⊶Ⓞ⊶Ⓝ ⊶Ⓒ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ",
"⊶Ⓡ⊶Ⓤ⊶Ⓚ ⊶Ⓐ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓚ⊶Ⓔ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓒ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓗ⊶Ⓤ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓒ⊶Ⓡ ⊶Ⓡ⊶Ⓐ⊶Ⓑ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓡ⊶Ⓗ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓚ⊶Ⓡ ⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓚ⊶Ⓔ",
"⊶Ⓦ⊶Ⓐ⊶Ⓘ⊶Ⓣ ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓓ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ",
"⊶Ⓡ⊶Ⓤ⊶Ⓚ ⊶Ⓙ⊶Ⓐ ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓡ⊶Ⓚ⊶Ⓗ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓕ⊶Ⓐ⊶Ⓜ⊶Ⓞ⊶Ⓤ⊶Ⓢ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ⊶ⒶⓃ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓝ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓢ⊶Ⓐ⊶Ⓛ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓐ⊶ⒶⓃ ⊶Ⓛ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓢ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓣ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓢ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓣ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓢ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓣ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓗ ⊶Ⓣ⊶Ⓤ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓐ⊶Ⓑ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ ⊶Ⓨ⊶Ⓗ⊶Ⓐ",
"⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓛ⊶Ⓔ ⊶ⓛ⊶ⓤ⊶ⓝ⊶ⓓ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓓ⊶Ⓐ⊶Ⓡ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓨ⊶Ⓘ ⊶Ⓒ⊶Ⓨ⊶Ⓐ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓒ⊶Ⓨ⊶Ⓐ",
"⊶Ⓗ⊶Ⓨ⊶Ⓔ ⊶Ⓢ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓣ⊶Ⓐ ⊶Ⓒ⊶Ⓞ⊶Ⓜ ⊶Ⓒ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ",
"⊶Ⓒ⊶Ⓗ⊶Ⓛ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓢ⊶Ⓜ⊶Ⓙ⊶Ⓗ⊶Ⓛ⊶Ⓔ",
"⊶Ⓑ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓑ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓢ⊶Ⓑ ⊶Ⓙ⊶Ⓐ⊶Ⓝ⊶Ⓣ⊶Ⓔ ⊶Ⓔ⊶Ⓨ ⊶Ⓚ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓓ⊶Ⓚ⊶Ⓐ⊶Ⓓ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓝ⊶Ⓔ ⊶Ⓦ⊶Ⓛ⊶Ⓘ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓘ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓙ⊶Ⓝ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓞ ⊶Ⓚ⊶Ⓞ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓘ⊶Ⓐ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓥ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓝ⊶Ⓝ⊶Ⓐ ⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓦ⊶Ⓞ ⊶Ⓖ⊶Ⓛ⊶Ⓣ ⊶Ⓝ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓦ⊶Ⓞ ⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓓ⊶Ⓚ⊶Ⓐ⊶Ⓓ ⊶Ⓔ⊶Ⓨ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓚ⊶Ⓘ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓞ⊶Ⓜ⊶Ⓕ⊶Ⓞ⊶Ⓞ",
"⊶Ⓑ⊶Ⓤ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓔ⊶Ⓔ⊶Ⓡ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓛ ⊶Ⓜ⊶Ⓔ ⊶Ⓛ⊶Ⓞ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓚ⊶Ⓔ ⊶Ⓤ⊶Ⓢ⊶Ⓚ⊶Ⓘ ⊶Ⓓ⊶Ⓗ⊶Ⓐ⊶Ⓓ⊶Ⓚ⊶Ⓐ⊶Ⓝ ⊶Ⓡ⊶Ⓞ⊶Ⓚ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓛ⊶Ⓤ⊶Ⓛ⊶Ⓛ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓐ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ",
"⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓐ",
"⊶Ⓣ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ ⊶Ⓡ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶ⒶⓉ ⊶Ⓚ⊶Ⓗ⊶ⓉⓂ",
"⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓔ⊶Ⓚ ⊶Ⓜ⊶Ⓐ⊶Ⓩ⊶Ⓔ ⊶Ⓚ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶ⒶⓉ ⊶Ⓑ⊶Ⓐ⊶Ⓣ⊶Ⓐ⊶Ⓞ ⊶Ⓚ⊶Ⓨ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶रैं⊶डी ⊶Ⓗ⊶Ⓐ⊶Ⓘ",
"⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓤ ⊶Ⓒ⊶Ⓞ⊶Ⓓ⊶Ⓤ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ",
"⊶Ⓐ⊶Ⓙ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓞ⊶Ⓨ⊶Ⓔ",
"⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓢ⊶Ⓤ⊶Ⓝ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓚ⊶Ⓘ⊶Ⓛ⊶Ⓐ⊶Ⓢ ⊶Ⓝ⊶Ⓨ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓨ⊶Ⓚ⊶Ⓔ",
"⊶Ⓜ⊶Ⓤ⊶Ⓙ⊶Ⓗ⊶Ⓔ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓟ⊶Ⓣ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ",
"⊶Ⓟ⊶Ⓡ ⊶Ⓟ⊶Ⓡ ⊶Ⓒ⊶Ⓨ⊶Ⓐ ⊶Ⓗ⊶Ⓞ⊶Ⓣ⊶Ⓔ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓜ⊶Ⓚ⊶Ⓒ",
"⊶Ⓣ⊶Ⓜ⊶Ⓒ⊶Ⓛ ⊶Ⓢ⊶Ⓤ⊶Ⓝ⊶Ⓛ⊶Ⓔ",
"⊶Ⓜ⊶Ⓞ⊶Ⓞ⊶Ⓣ ⊶Ⓓ⊶Ⓤ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ⊶Ⓨ",
"⊶Ⓑ⊶Ⓗ⊶Ⓖ⊶Ⓝ⊶Ⓨ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓕ⊶Ⓡ",
"⊶Ⓕ⊶Ⓡ ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓛ⊶Ⓔ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓨ⊶Ⓔ ⊶Ⓥ⊶Ⓘ ⊶Ⓢ⊶Ⓗ⊶Ⓘ ⊶Ⓔ⊶Ⓨ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓚ⊶Ⓒ ⊶Ⓑ⊶Ⓢ",
"⊶Ⓐ⊶Ⓙ ⊶Ⓚ⊶Ⓤ⊶Ⓒ⊶Ⓗ ⊶Ⓝ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓣ⊶Ⓤ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ",
"⊶Ⓣ⊶Ⓡ⊶Ⓨ ⊶Ⓚ⊶Ⓡ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓢ⊶Ⓚ⊶Ⓔ",
"⊶Ⓣ⊶Ⓞ⊶Ⓡ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ⊶Ⓑ⊶Ⓤ⊶Ⓡ ⊶Ⓢ⊶Ⓤ⊶Ⓝ",
"⊶Ⓣ⊶Ⓞ⊶Ⓡ ⊶Ⓜ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓕ⊶Ⓤ⊶Ⓓ⊶Ⓓ⊶Ⓘ ⊶Ⓞ⊶Ⓨ⊶Ⓔ",
"⊶Ⓗ⊶Ⓐ⊶Ⓨ⊶Ⓔ ⊶Ⓗ⊶Ⓐ⊶Ⓨ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓨ ⊶Ⓜ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓖ⊶Ⓐ⊶Ⓘ",
"⊶Ⓞ⊶Ⓨ⊶Ⓔ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ⊶Ⓚ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓢ⊶Ⓘ⊶Ⓝ⊶Ⓔ..",
"⊶Ⓚ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓐ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓢ⊶Ⓤ⊶Ⓝ",
"⊶Ⓚ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓐ ⊶Ⓙ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓐ ⊶Ⓒ⊶Ⓤ⊶Ⓓ ⊶Ⓡ⊶Ⓗ⊶Ⓐ ⊶Ⓣ⊶Ⓤ",
"⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓘ ⊶Ⓛ⊶Ⓔ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓐ..",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓚ⊶Ⓔ ⊶Ⓕ⊶Ⓔ⊶Ⓝ⊶Ⓚ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓝ ⊶Ⓢ⊶Ⓣ⊶Ⓞ⊶Ⓟ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓐ⊶ⒶⓉ ⊶Ⓖ⊶Ⓐ⊶Ⓨ⊶Ⓘ ⊶Ⓐ⊶Ⓙ⊶Ⓣ⊶Ⓞ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓔ ⊶Ⓚ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓒ⊶Ⓗ⊶Ⓘ⊶Ⓟ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓝ ⊶Ⓢ⊶Ⓣ⊶Ⓞ⊶Ⓟ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓤ⊶Ⓢ⊶Ⓢ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶100 ⊶Ⓒ⊶Ⓗ⊶Ⓔ⊶Ⓓ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓦ⊶Ⓐ⊶Ⓢ⊶Ⓘ⊶Ⓡ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓜ⊶Ⓔ⊶Ⓡ⊶Ⓔ ⊶Ⓛ⊶Ⓐ⊶Ⓥ⊶Ⓓ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓡ ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓣ⊶Ⓘ ⊶Ⓗ⊶Ⓐ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓣ⊶Ⓐ⊶Ⓜ⊶Ⓐ⊶Ⓣ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓐ⊶Ⓡ⊶Ⓐ⊶Ⓗ ⊶Ⓛ⊶Ⓐ⊶ⒶⓁ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓐ⊶ⒶⓅ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓑ⊶Ⓘ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓙ⊶Ⓐ⊶Ⓡ ⊶Ⓜ⊶Ⓔ ⊶Ⓝ⊶Ⓘ⊶Ⓛ⊶Ⓐ⊶Ⓜ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓕ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓜ⊶Ⓔ ⊶Ⓓ⊶Ⓐ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓙ⊶Ⓐ⊶Ⓓ⊶Ⓐ ⊶Ⓝ⊶Ⓐ ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ ⊶Ⓦ⊶Ⓐ⊶Ⓡ⊶Ⓝ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓢ⊶Ⓐ⊶Ⓢ⊶Ⓣ⊶Ⓐ ⊶Ⓚ⊶Ⓔ⊶Ⓨ⊶Ⓑ⊶Ⓞ⊶Ⓐ⊶Ⓡ⊶Ⓓ ⊶Ⓛ⊶Ⓐ⊶Ⓖ⊶Ⓐ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓐ⊶Ⓖ⊶Ⓐ⊶Ⓡ ⊶Ⓣ⊶Ⓤ ⊶Ⓒ⊶Ⓟ ⊶Ⓑ⊶Ⓞ⊶Ⓛ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓜ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓡ⊶Ⓐ⊶Ⓜ ⊶Ⓜ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓗ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓤ⊶Ⓡ ⊶Ⓜ⊶Ⓔ ⊶Ⓗ⊶Ⓐ⊶Ⓣ⊶Ⓗ⊶Ⓞ⊶Ⓡ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓚ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓘ ⊶Ⓣ⊶Ⓗ⊶Ⓞ⊶Ⓚ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓙ⊶Ⓙ⊶Ⓘ ⊶Ⓢ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓕ⊶Ⓐ⊶ⒶⓉ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓙ⊶Ⓐ⊶ⒶⓃ ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓐ⊶Ⓝ⊶Ⓒ⊶Ⓔ⊶Ⓡ ⊶Ⓦ⊶Ⓐ⊶Ⓛ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓝ⊶Ⓞ⊶Ⓝ ⊶Ⓢ⊶Ⓣ⊶Ⓞ⊶Ⓟ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓙ⊶Ⓐ⊶ⒶⓃ ⊶Ⓚ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓛ⊶Ⓘ⊶Ⓣ⊶Ⓒ⊶Ⓗ ⊶Ⓣ⊶Ⓨ⊶Ⓟ⊶Ⓘ⊶Ⓝ⊶Ⓖ ⊶Ⓚ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓥ⊶Ⓐ⊶Ⓢ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓗ⊶Ⓐ⊶Ⓘ ⊶Ⓢ⊶Ⓐ⊶Ⓑ⊶Ⓚ⊶Ⓐ ⊶Ⓜ⊶Ⓤ⊶Ⓗ ⊶Ⓜ⊶Ⓔ⊶Ⓗ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓛ⊶Ⓔ⊶Ⓚ⊶Ⓡ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ⊶Ⓐ⊶Ⓣ⊶Ⓘ ⊶Ⓗ⊶Ⓐ⊶Ⓘ",
"⊶Ⓣ⊶Ⓤ ⊶Ⓞ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓐ ⊶Ⓚ⊶Ⓗ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓑ⊶Ⓘ⊶Ⓒ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓙ⊶Ⓐ⊶Ⓡ ⊶Ⓜ⊶Ⓔ ⊶Ⓜ⊶Ⓞ⊶Ⓙ⊶Ⓡ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓦ⊶Ⓐ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓓ⊶Ⓤ⊶Ⓢ⊶Ⓡ⊶Ⓐ ⊶Ⓑ⊶Ⓛ⊶Ⓐ⊶Ⓒ⊶Ⓚ ⊶Ⓗ⊶Ⓞ⊶Ⓛ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓚ⊶Ⓐ⊶Ⓕ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓜ⊶Ⓔ ⊶Ⓓ⊶Ⓐ⊶Ⓕ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓣ⊶Ⓘ⊶ⓨ⊶Ⓞ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓓ⊶Ⓩ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓓ⊶Ⓐ⊶Ⓛ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓖ⊶Ⓞ⊶Ⓓ⊶Ⓩ⊶Ⓘ⊶Ⓛ⊶Ⓛ⊶Ⓐ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓢ⊶Ⓔ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓓ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓕ⊶Ⓛ⊶Ⓨ ⊶Ⓚ⊶Ⓘ⊶Ⓢ⊶Ⓢ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓘ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓓ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓤ⊶Ⓜ⊶Ⓜ⊶Ⓨ ⊶Ⓚ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓒ⊶Ⓗ⊶Ⓘ⊶ⓨ⊶Ⓞ ⊶Ⓚ⊶Ⓞ ⊶Ⓚ⊶Ⓐ⊶Ⓣ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓟ⊶Ⓐ⊶Ⓚ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓙ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓚ⊶Ⓗ⊶Ⓤ⊶Ⓝ⊶Ⓝ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓤ⊶Ⓢ⊶Ⓢ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓐ⊶Ⓝ⊶Ⓘ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓓ⊶Ⓞ⊶Ⓝ⊶Ⓐ⊶Ⓣ⊶Ⓔ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓟ⊶Ⓟ⊶Ⓐ⊶Ⓛ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓢ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓒ⊶Ⓗ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓗ⊶Ⓐ⊶Ⓡ ⊶Ⓝ⊶Ⓘ⊶Ⓚ⊶Ⓐ⊶Ⓛ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓔ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓨ⊶Ⓞ⊶Ⓖ⊶Ⓘ ⊶Ⓙ⊶Ⓘ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓤ⊶Ⓛ⊶Ⓛ⊶Ⓓ⊶Ⓞ⊶Ⓩ⊶Ⓔ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓐ⊶Ⓛ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓓ⊶Ⓘ⊶Ⓓ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓕ⊶Ⓛ⊶Ⓐ⊶Ⓣ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓘ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓙ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓕ⊶Ⓐ⊶ⒶⓉ ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓓ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓐ⊶Ⓚ⊶49 ⊶Ⓢ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓔ ⊶Ⓖ⊶Ⓞ⊶Ⓛ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶9 ⊶Ⓤ⊶Ⓝ⊶Ⓘ⊶Ⓥ⊶Ⓔ⊶Ⓡ⊶Ⓢ ⊶Ⓐ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓐ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓐ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ ⊶Ⓓ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ⊶ⓨ⊶Ⓞ ⊶Ⓚ⊶Ⓐ ⊶Ⓚ⊶Ⓞ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓑ⊶Ⓐ⊶Ⓝ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓑ⊶Ⓔ⊶Ⓗ⊶Ⓔ⊶Ⓝ ⊶Ⓚ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ⊶Ⓝ⊶Ⓔ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓐ⊶Ⓘ⊶Ⓣ⊶Ⓗ⊶Ⓐ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓚ⊶Ⓞ⊶Ⓣ⊶Ⓗ⊶Ⓔ ⊶Ⓟ⊶Ⓐ⊶Ⓡ⊶Ⓡ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓚ⊶Ⓞ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓒ⊶Ⓗ⊶Ⓐ ⊶Ⓡ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓘ ⊶Ⓑ⊶Ⓐ⊶Ⓗ⊶Ⓐ⊶Ⓝ⊶Ⓔ ⊶Ⓑ⊶Ⓐ⊶Ⓙ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓐ⊶Ⓝ⊶Ⓒ⊶Ⓔ⊶Ⓡ ⊶Ⓦ⊶Ⓐ⊶Ⓛ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓚ⊶Ⓞ ⊶Ⓣ⊶Ⓘ⊶Ⓚ⊶Ⓣ⊶Ⓞ⊶Ⓚ ⊶Ⓚ⊶Ⓔ ⊶Ⓣ⊶Ⓐ⊶Ⓡ⊶Ⓐ⊶Ⓗ ⊶Ⓑ⊶Ⓐ⊶Ⓝ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓘ⊶Ⓢ⊶Ⓢ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓘ⊶Ⓨ⊶Ⓐ ⊶Ⓢ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓐ ⊶Ⓟ⊶Ⓞ⊶Ⓦ⊶Ⓔ⊶Ⓡ ⊶Ⓓ⊶Ⓘ⊶Ⓚ⊶Ⓗ⊶Ⓐ",
"⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ⊶Ⓔ⊶Ⓖ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓣ⊶Ⓞ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓘ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓣ ⊶Ⓜ⊶Ⓔ ⊶Ⓜ⊶Ⓤ⊶Ⓣ⊶Ⓣ⊶Ⓗ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓟ⊶Ⓞ⊶Ⓛ⊶Ⓘ⊶Ⓒ⊶Ⓔ ⊶Ⓚ⊶Ⓐ ⊶Ⓓ⊶Ⓐ⊶Ⓝ⊶Ⓓ⊶Ⓐ ⊶Ⓜ⊶Ⓐ⊶Ⓡ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ ⊶Ⓤ⊶Ⓢ⊶Ⓢ⊶Ⓔ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓐ ⊶Ⓦ⊶Ⓞ⊶Ⓡ⊶Ⓚ⊶Ⓞ⊶Ⓤ⊶Ⓣ ⊶Ⓗ⊶Ⓞ⊶Ⓙ⊶Ⓐ⊶Ⓨ⊶Ⓔ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ ⊶Ⓘ⊶Ⓣ⊶Ⓝ⊶Ⓐ ⊶Ⓔ⊶Ⓝ⊶Ⓔ⊶Ⓡ⊶Ⓖ⊶Ⓨ ⊶Ⓗ⊶Ⓐ⊶Ⓘ ⊶Ⓚ⊶Ⓘ ⊶Ⓔ⊶Ⓚ ⊶Ⓑ⊶Ⓐ⊶ⒶⓇ ⊶Ⓜ⊶Ⓔ ⊶10 ⊶Ⓛ⊶Ⓞ⊶Ⓖ⊶Ⓞ ⊶Ⓚ⊶Ⓐ ⊶Ⓛ⊶Ⓤ⊶Ⓝ⊶Ⓓ⊶Ⓐ ⊶Ⓛ⊶Ⓔ⊶Ⓛ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓜ⊶Ⓔ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓑ⊶Ⓐ⊶Ⓒ⊶Ⓒ⊶Ⓗ⊶Ⓐ ⊶Ⓐ⊶Ⓘ⊶Ⓢ⊶Ⓔ ⊶Ⓐ⊶Ⓟ⊶Ⓝ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓨ⊶Ⓐ ⊶Ⓒ⊶Ⓗ⊶Ⓤ⊶Ⓓ⊶Ⓦ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓑ⊶Ⓗ⊶Ⓐ⊶Ⓖ⊶Ⓔ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓜ⊶Ⓐ⊶Ⓐ⊶Ⓚ⊶Ⓔ ⊶Ⓑ⊶Ⓗ⊶Ⓞ⊶Ⓢ⊶Ⓓ⊶Ⓔ ⊶Ⓚ⊶Ⓞ ⊶Ⓤ⊶Ⓛ⊶Ⓣ⊶Ⓐ ⊶Ⓛ⊶Ⓐ⊶Ⓣ⊶Ⓚ⊶Ⓐ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓒ⊶Ⓗ⊶Ⓞ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ",
"⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓗ⊶Ⓞ⊶Ⓛ⊶Ⓛ⊶Ⓞ⊶Ⓦ ⊶Ⓟ⊶Ⓤ⊶Ⓡ⊶Ⓟ⊶Ⓛ⊶Ⓔ ⊶Ⓜ⊶Ⓐ⊶ⒶⓇ ⊶Ⓚ⊶Ⓐ⊶Ⓡ ⊶Ⓣ⊶Ⓔ⊶Ⓡ⊶Ⓘ ⊶Ⓐ⊶Ⓜ⊶Ⓜ⊶Ⓐ ⊶Ⓚ⊶Ⓘ ⊶Ⓖ⊶Ⓐ⊶Ⓝ⊶Ⓓ ⊶Ⓜ⊶Ⓔ ⊶Ⓒ⊶Ⓗ⊶Ⓔ⊶Ⓓ⊶Ⓓ ⊶Ⓚ⊶Ⓐ⊶Ⓡ⊶Ⓓ⊶Ⓤ⊶Ⓝ⊶Ⓖ⊶Ⓐ"
]
sqs2_texts = [
"⋰Ⓑ⋰⋰⒪⋰⋰⒧⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰Ⓓ⋰⋰⒤⋰⋰Ⓓ⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒨⋰⋰⒰⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒭⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰⋰⒟⋰ ⋰⒟⋰⋰⒰⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒮⋰⋰⒜⋰⋰⒧⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰",
"⋰⒡⋰⋰⒜⋰⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒫⋰⋰⒠⋰ ⋰⒯⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰⋰⒫⋰⋰⒜⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒰⋰",
"⋰⒳⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒣⋰⋰⒠⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒝⋰⋰⒰⋰⋰⒟⋰⋰⒣⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒣⋰⋰⒠⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒜⋰⋰⒦⋰⋰⒠⋰⋰⒧⋰⋰⒜⋰ ⋰⒫⋰⋰⒜⋰⋰⒩⋰ ⋰⒨⋰⋰⒤⋰⋰⒯⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒳⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰⋰⒯⋰ ⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰⋰⒫⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒩⋰⋰⒜⋰⋰⒩⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒪⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒠⋰⋰⒭⋰⋰⒭⋰ ⋰⒡⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰⋰⒯⋰ ⋰⒮⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰⋰⒥⋰⋰⒥⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒡⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒩⋰⋰⒤⋰⋰⒧⋰⋰⒜⋰⋰⒜⋰⋰⒨⋰⋰⒨⋰⋰⒨⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒪⋰⋰⒪⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒜⋰⋰⒜⋰ ⋰⒮⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒢⋰⋰⒢⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒟⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒩⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰⋰⒩⋰ ⋰⒣⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰⋰⒣⋰⋰⒣⋰ ⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰⋰⒧⋰⋰⒧⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰⋰⒥⋰⋰⒥⋰⋰⒥⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰⋰⒩⋰⋰⒩⋰",
"⋰⒮⋰⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒫⋰⋰⒜⋰⋰⒦⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰",
"⋰⒮⋰⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰⋰⒦⋰⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒭⋰⋰⒭⋰ ⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒟⋰⋰⒟⋰ ⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰⋰⒠⋰⋰⒠⋰",
"⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰ ⋰⒩⋰⋰⒜⋰⋰⒩⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰⋰⒯⋰ ⋰⒦⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒝⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒜⋰⋰⒰⋰⋰⒧⋰⋰⒜⋰⋰⒟⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒜⋰⋰⒰⋰⋰⒧⋰⋰⒜⋰⋰⒟⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒟⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒮⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰ ⋰⒮⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒱⋰⋰⒪⋰⋰⒤⋰⋰⒞⋰⋰⒠⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒮⋰⋰⒜⋰⋰⒦⋰⋰⒯⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒤⋰⋰⒢⋰⋰⒩⋰⋰⒪⋰⋰⒭⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒤⋰⋰⒢⋰⋰⒩⋰⋰⒪⋰⋰⒭⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒭⋰⋰⒜⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒯⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒧⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒧⋰⋰⒤⋰ ⋰⒥⋰⋰⒰⋰⋰⒝⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒠⋰⋰⒩⋰⋰⒦⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒩⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒨⋰⋰⒜⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰⋰⒝⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒯⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒜⋰⋰⒝⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰??⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰⋰⒭⋰ ⋰⒢⋰⋰??⋰⋰⒰⋰⋰⒨⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒧⋰⋰⒠⋰⋰⒦⋰⋰⒤⋰⋰⒩⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒥⋰⋰⒣⋰⋰⒰⋰⋰⒦⋰⋰⒩⋰⋰⒠⋰ ⋰⒩⋰⋰⒜⋰⋰⒤⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒩⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰⋰⒰⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒰⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒜⋰⋰⒯⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒣⋰⋰⒪⋰⋰⒥⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒡⋰⋰⒠⋰⋰⒩⋰⋰⒦⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒦⋰⋰⒪⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰⋰⒪⋰ ⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒨⋰⋰⒠⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒮⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒝⋰⋰⒣⋰⋰⒤⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒥⋰⋰⒜⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒣⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰",
"⋰⒢⋰⋰⒜⋰⋰⒤⋰⋰⒭⋰⋰⒝⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒜⋰⋰⒰⋰⋰⒧⋰⋰⒜⋰⋰⒟⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒮⋰⋰⒫⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰⋰⒞⋰⋰⒣⋰ ⋰⒦⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒢⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰⋰⒝⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒠⋰⋰⒦⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒠⋰⋰⒥⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒩⋰⋰⒜⋰⋰⒣⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒯⋰⋰⒜⋰⋰⒢⋰ ⋰⒦⋰⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒥⋰⋰⒤⋰⋰⒩⋰⋰⒟⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒯⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒜⋰⋰⒝⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒡⋰⋰⒜⋰⋰⒩⋰ ⋰⒦⋰⋰⒜⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰⋰⒭⋰ ⋰⒢⋰⋰⒣⋰⋰⒰⋰⋰⒨⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒟⋰⋰⒠⋰ ⋰⒧⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒧⋰⋰⒠⋰⋰⒦⋰⋰⒤⋰⋰⒩⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒥⋰⋰⒣⋰⋰⒰⋰⋰⒦⋰⋰⒩⋰⋰⒠⋰ ⋰⒩⋰⋰⒜⋰⋰⒤⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰ ⋰⒝⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰⋰⒜⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒤⋰⋰⒩⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒭⋰⋰⒠⋰⋰⒫⋰⋰⒧⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒜⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒜⋰⋰⒥⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒨⋰⋰⒰⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒩⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒧⋰⋰⒰⋰ ⋰⒦⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒞⋰⋰⒫⋰ ⋰⒝⋰⋰⒪⋰⋰",
"⋰Ⓑ⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰Ⓑ⋰⋰⒣⋰⋰⒤⋰ ⋰Ⓑ⋰⋰⒩⋰⋰⒜⋰⋰⒧⋰⋰⒠⋰ ⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒠⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒵⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒴⋰⋰⒜⋰⋰⒜⋰⋰⒟⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰ ⋰⒯⋰⋰⒴⋰⋰⒨⋰⋰⒫⋰⋰⒜⋰⋰⒮⋰⋰⒮⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒰⋰⋰⒩⋰⋰⒡⋰⋰⒰⋰⋰⒩⋰⋰⒩⋰⋰⒴⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒨⋰⋰⒯⋰⋰⒯⋰ ⋰⒦⋰⋰⒭⋰",
"⋰⒪⋰⋰⒣⋰ ⋰⒣⋰⋰⒠⋰⋰⒧⋰⋰⒧⋰⋰⒪⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒪⋰⋰⒭⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒱⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒜⋰⋰⒜⋰⋰⒰⋰⋰⒦⋰⋰⒜⋰⋰⒯⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒭⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒭⋰.",
"⋰⒪⋰⋰⒴⋰⋰⒴⋰ ⋰⒦⋰⋰⒤⋰⋰⒩⋰⋰⒩⋰⋰⒠⋰⋰⒭⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰ ⋰⒢⋰⋰⒞⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰⋰⒩⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒫⋰⋰⒠⋰⋰⒭⋰⋰⒨⋰⋰⒤⋰⋰⒮⋰⋰⒮⋰⋰⒤⋰⋰⒪⋰⋰⒩⋰ ⋰⒦⋰⋰⒤⋰⋰⒮⋰⋰⒩⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰.",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒠⋰⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰.",
"⋰⒮⋰⋰⒰⋰⋰⒩⋰ ⋰⒮⋰⋰⒰⋰⋰⒩⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰.",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒞⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰.",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒯⋰⋰⒤⋰ ⋰⒥⋰⋰⒜⋰⋰⒯⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰.",
"⋰⒦⋰⋰⒴⋰? ⋰⒥⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰⋰⒟⋰⋰⒠⋰.",
"⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒞⋰⋰⒪⋰⋰⒨⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒢⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒯⋰⋰⒜⋰⋰⒢⋰ ⋰⒞⋰⋰⒭⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒨⋰⋰⒦⋰⋰⒞⋰ ⋰⒝⋰⋰⒮⋰",
"⋰⒥⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒵⋰ ⋰⒫⋰⋰⒜⋰⋰⒫⋰⋰⒜⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰",
"⋰⒮⋰⋰⒤⋰⋰⒟⋰⋰⒠⋰ ⋰⒣⋰⋰⒪⋰⋰⒥⋰⋰⒜⋰ ⋰⒝⋰⋰⒤⋰⋰⒣⋰⋰⒜⋰⋰⒭⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒜⋰⋰⒝⋰",
"⋰⒣⋰⋰⒴⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒝⋰⋰⒣⋰⋰⒢⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰ ⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰",
"⋰⒝⋰⋰⒣⋰⋰⒢⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒥⋰⋰⒥⋰",
"⋰⒣⋰⋰⒴⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰",
"⋰⒣⋰⋰⒴⋰⋰⒠⋰ ⋰⒟⋰⋰⒰⋰⋰⒭⋰ ⋰⒣⋰⋰⒜⋰⋰⒯⋰⋰⒯⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒦⋰⋰⒪⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒯⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒠⋰⋰⒮⋰⋰⒧⋰⋰⒤⋰⋰⒴⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒡⋰ ⋰⒞⋰⋰⒭⋰ ⋰⒭⋰⋰⒣⋰⋰⒜⋰ ⋰⒣⋰⋰⒰⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒦⋰⋰⒪⋰⋰⒤⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒯⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒜⋰⋰⒡⋰⋰⒤⋰ ⋰⒟⋰⋰⒠⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒨⋰⋰⒜⋰⋰⒡⋰⋰⒤⋰ ⋰⒨⋰⋰⒤⋰⋰⒧⋰ ⋰⒥⋰⋰⒜⋰⋰⒴⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒯⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒠⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒞⋰⋰⒭⋰⋰⒦⋰⋰⒠⋰",
"⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒞⋰⋰⒭⋰⋰⒦⋰⋰⒠⋰",
"⋰⒡⋰⋰⒭⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰⋰⒩⋰⋰⒜⋰ ⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒮⋰⋰⒲⋰⋰⒤⋰⋰⒫⋰⋰⒠⋰ ⋰⒞⋰⋰⒭⋰⋰⒦⋰⋰⒠⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒣⋰⋰⒰⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒫⋰⋰⒭⋰ ⋰⒦⋰⋰⒠⋰⋰⒮⋰⋰⒠⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰",
"⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰ ⋰⒫⋰⋰⒯⋰⋰⒜⋰ ⋰⒯⋰⋰⒣⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒨⋰⋰⒠⋰⋰⒴⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒩⋰⋰⒯⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰",
"⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒰⋰⋰⒯⋰⋰⒭⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒧⋰⋰⒰⋰⋰⒩⋰ ⋰⒨⋰⋰⒯⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒮⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒜⋰",
"⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒟⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒢⋰⋰⒜⋰⋰⒮⋰⋰⒣⋰⋰⒯⋰⋰⒤⋰ ⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰",
"⋰⒨⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒦⋰ ⋰⒣⋰⋰⒜⋰⋰⒯⋰⋰⒣⋰ ⋰⒯⋰⋰⒪⋰⋰⒟⋰⋰⒣⋰ ⋰⒦⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒦⋰ ⋰⒨⋰⋰⒰⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒡⋰⋰⒜⋰⋰⒮⋰⋰⒜⋰⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒫⋰⋰⒜⋰⋰⒮⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒩⋰⋰⒜⋰⋰⒤⋰ ⋰⒜⋰⋰⒴⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰⋰⒦⋰⋰⒪⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒤⋰⋰⒟⋰⋰⒠⋰⋰⒭⋰ ⋰⒮⋰⋰⒠⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒥⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒲⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒧⋰⋰⒠⋰⋰⒢⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒮⋰⋰⒨⋰⋰⒥⋰⋰⒣⋰ ⋰⒝⋰⋰⒜⋰⋰⒯⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰",
"⋰⒡⋰⋰⒜⋰⋰⒮⋰⋰⒯⋰ ⋰⒧⋰⋰⒠⋰⋰⒜⋰⋰⒱⋰⋰⒠⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰⋰⒥⋰⋰⒪⋰⋰⒭⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰",
"⋰⒯⋰⋰⒰⋰⋰⒯⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰",
"⋰⒪⋰⋰⒴⋰ ⋰⒣⋰⋰⒤⋰⋰⒥⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰⋰⒵⋰⋰⒪⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒪⋰ ⋰⒤⋰⋰⒧⋰⋰⒴⋰ ⋰⒭⋰⋰⒠⋰⋰⒴⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒯⋰⋰⒨⋰⋰⒦⋰⋰⒞⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰",
"⋰⒮⋰⋰⒣⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰",
"⋰⒡⋰⋰⒭⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰",
"⋰⒮⋰⋰⒣⋰⋰⒤⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒲⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒴⋰⋰⒰⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰⋰⒞⋰⋰⒣⋰⋰⒜⋰⋰⒫⋰",
"⋰⒫⋰⋰⒭⋰⋰⒪⋰⋰⒪⋰⋰⒡⋰ ⋰⒞⋰⋰⒭⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒫⋰⋰⒭⋰⋰⒪⋰⋰⒪⋰⋰⒡⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰",
"⋰⒫⋰⋰⒭⋰⋰⒪⋰⋰⒪⋰⋰⒡⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒦⋰⋰⒜⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒤⋰⋰⒧⋰⋰⒧⋰⋰⒜⋰⋰⒭⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰ ⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒪⋰⋰⒴⋰ ⋰⒣⋰⋰⒤⋰⋰⒥⋰⋰⒟⋰⋰⒠⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒣⋰⋰⒜⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰⋰⒵⋰⋰⒪⋰⋰⒭⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰ ?",
"⋰⒜⋰⋰⒝⋰ ⋰⒯⋰⋰⒦⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒤⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ?",
"⋰⒩⋰⋰⒴⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒦⋰⋰⒰⋰⋰⒞⋰⋰⒣⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒥⋰⋰⒜⋰⋰⒩⋰⋰⒯⋰⋰⒜⋰ ⋰⒝⋰⋰⒮⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰ ⋰⒠⋰⋰⒴⋰",
"⋰⒮⋰⋰⒝⋰⋰⒮⋰⋰⒠⋰ ⋰⒫⋰⋰⒣⋰⋰⒠⋰⋰⒧⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒪⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒩⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰⋰⒠⋰",
"⋰⒴⋰⋰⒜⋰⋰⒣⋰⋰⒜⋰ ⋰⒝⋰⋰⒣⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒞⋰⋰⒠⋰ ⋰⒫⋰⋰⒤⋰⋰⒧⋰⋰⒧⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒜⋰⋰⒝⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒯⋰⋰⒪⋰ ⋰⒝⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒠⋰⋰⒢⋰⋰⒤⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒫⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒯⋰⋰⒪⋰⋰⒨⋰⋰⒨⋰⋰⒴⋰",
"⋰⒩⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰⋰⒞⋰⋰⒣⋰⋰⒟⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰ ⋰⒴⋰⋰⒣⋰⋰⒜⋰ ⋰⒮⋰⋰⒠⋰",
"⋰⒞⋰⋰⒪⋰⋰⒵⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒣⋰⋰⒤⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒣⋰⋰⒠⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒫⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰ ⋰⒨⋰⋰⒰⋰⋰⒥⋰⋰⒣⋰⋰⒠⋰",
"⋰⒩⋰⋰⒴⋰⋰⒩⋰⋰⒴⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒥⋰⋰⒪⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰⋰⒯⋰⋰⒤⋰ ⋰⒥⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰",
"⋰⒯⋰⋰⒭⋰⋰⒴⋰ ⋰⒜⋰⋰⒨⋰⋰⒨⋰⋰⒤⋰ ⋰⒞⋰⋰⒠⋰ ⋰⒝⋰⋰⒣⋰⋰⒪⋰⋰⒮⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒠⋰⋰⒨⋰⋰⒪⋰⋰⒥⋰⋰⒤⋰ ⋰⒟⋰⋰⒜⋰⋰⒧⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒞⋰⋰⒣⋰⋰⒨⋰⋰⒭⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒜⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ?",
"⋰⒯⋰⋰⒨⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒭⋰⋰⒤⋰ ⋰⒣⋰⋰⒪⋰⋰⒢⋰⋰⒤⋰ ⋰⒡⋰⋰⒭⋰⋰⒭⋰⋰⒯⋰⋰⒪⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒦⋰⋰⒝⋰ ? ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰⋰⒦⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒮⋰⋰⒞⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰⋰⒴⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰ ⋰⒯⋰⋰⒰⋰⋰⒩⋰⋰⒠⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰",
"⋰⒤⋰⋰⒯⋰⋰⒩⋰⋰⒜⋰ ⋰⒮⋰⋰⒞⋰⋰⒣⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒝⋰⋰⒪⋰⋰⒧⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰",
"⋰⒮⋰⋰⒞⋰⋰⒣⋰ ⋰⒨⋰⋰⒠⋰⋰⒴⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒜⋰⋰⒫⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒲⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒠⋰ ⋰⒮⋰⋰⒯⋰⋰⒣⋰",
"⋰⒨⋰⋰⒯⋰⋰⒧⋰⋰⒝⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰",
"⋰⒫⋰⋰⒰⋰⋰⒭⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒯⋰⋰⒨⋰⋰⒭⋰ ⋰⒡⋰⋰⒭⋰⋰⒭⋰⋰⒯⋰⋰⒪⋰",
"⋰⒪⋰⋰⒣⋰ ⋰⒪⋰⋰⒦⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒧⋰⋰⒠⋰ ⋰⒡⋰⋰⒤⋰⋰⒭⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒟⋰⋰⒜⋰⋰⒨⋰⋰⒜⋰⋰⒟⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰ ⋰⒮⋰⋰⒠⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰⋰⒠⋰ ⋰⒫⋰⋰⒠⋰⋰⒣⋰⋰⒧⋰⋰⒠⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒠⋰⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒩⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒱⋰⋰⒴⋰⋰⒜⋰⋰⒮⋰⋰⒯⋰ ⋰⒣⋰⋰⒰⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒰⋰⋰⒞⋰⋰⒣⋰ ⋰⒝⋰⋰⒤⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ? ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒴⋰⋰⒜⋰ ?",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒨⋰⋰⒯⋰ ⋰⒣⋰⋰⒮⋰⋰⒮⋰",
"⋰⒴⋰⋰⒰⋰⋰⒭⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒨⋰⋰⒪⋰⋰⒨⋰",
"⋰⒜⋰⋰⒭⋰⋰⒠⋰ ⋰⒮⋰⋰⒝⋰⋰⒦⋰⋰⒤⋰ ⋰⒨⋰⋰??⋰⋰⒜⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒪⋰⋰⒭⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒤⋰",
"⋰⒜⋰⋰⒭⋰⋰⒠⋰ ⋰⒤⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰⋰⒧⋰⋰⒠⋰ ⋰⒠⋰⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰",
"⋰⒯⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒤⋰ ⋰⒯⋰⋰⒭⋰⋰⒣⋰",
"⋰⒠⋰⋰⒦⋰ ⋰⒧⋰⋰⒤⋰⋰⒩⋰⋰⒠⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰",
"⋰⒬⋰",
"⋰⒪⋰⋰⒞⋰⋰⒴⋰ ⋰⒜⋰⋰⒝⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒧⋰⋰⒠⋰",
"⋰⒫⋰⋰⒠⋰⋰⒣⋰⋰⒠⋰⋰⒧⋰⋰⒠⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰",
"⋰⒬⋰ ?",
"⋰⒣⋰⋰⒴⋰⋰⒴⋰⋰⒴⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰ ⋰⒠⋰⋰⒦⋰ ⋰⒝⋰⋰⒜⋰⋰⒜⋰⋰⒭⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒮⋰⋰⒰⋰⋰⒩⋰ ⋰⒟⋰⋰⒪⋰⋰⒮⋰⋰⒯⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰",
"⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒡⋰ ⋰⒞⋰⋰⒭⋰⋰⒭⋰ ⋰⒟⋰⋰⒰⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒤⋰ ⋰⒤⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰ ⋰⒜⋰⋰⒜⋰",
"⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒯⋰⋰⒨⋰⋰⒭⋰ ⋰⒡⋰⋰⒭⋰⋰⒭⋰⋰⒯⋰⋰⒪⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒤⋰⋰⒟⋰⋰⒜⋰⋰⒭⋰ ⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒨⋰⋰⒭⋰",
"⋰⒩⋰⋰⒴⋰⋰⒯⋰⋰⒪⋰ ⋰⒜⋰⋰⒠⋰⋰⒮⋰⋰⒠⋰ ⋰⒣⋰⋰⒤⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒣⋰⋰⒴⋰⋰⒴⋰ ⋰⒜⋰⋰⒤⋰⋰⒮⋰⋰⒠⋰ ⋰⒣⋰⋰⒤⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰⋰⒩⋰⋰⒜⋰",
"⋰⒪⋰⋰⒭⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒧⋰⋰⒠⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒜⋰ ⋰⒪⋰⋰⒭⋰",
"⋰⒣⋰⋰⒴⋰⋰⒴⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒪⋰ ⋰⒩⋰⋰⒜⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒪⋰ ⋰⒨⋰⋰⒯⋰ ⋰⒝⋰⋰⒣⋰⋰⒜⋰⋰⒢⋰ ⋰⒥⋰⋰⒜⋰⋰⒪⋰",
"⋰⒝⋰⋰⒴⋰⋰⒴⋰⋰⒠⋰⋰⒠⋰ ⋰⒣⋰⋰⒴⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ?",
"⋰⒬⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒬⋰ ⋰⒭⋰⋰⒣⋰⋰⒠⋰ ⋰⒣⋰⋰⒪⋰ ?",
"⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒠⋰⋰⒴⋰ ⋰⒞⋰⋰⒴⋰⋰⒜⋰ ⋰⒨⋰⋰⒞⋰",
"⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰ ⋰⒨⋰⋰⒯⋰",
"⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒥⋰",
"⋰⒪⋰⋰⒭⋰ ⋰⒝⋰⋰⒟⋰⋰⒜⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰",
"⋰⒪⋰⋰⒭⋰ ⋰⒝⋰⋰⒟⋰⋰⒜⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰⋰⒟⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒝⋰⋰⒰⋰⋰⒭⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒦⋰⋰⒠⋰⋰⒠⋰⋰⒟⋰⋰⒠⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒜⋰⋰⒟⋰⋰⒦⋰⋰⒠⋰",
"⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒝⋰⋰⒠⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰",
"⋰⒨⋰⋰⒦⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒜⋰⋰⒞⋰⋰⒞⋰⋰⒣⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒩⋰⋰⒜⋰⋰⒩⋰⋰⒤⋰ ⋰⒨⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒧⋰",
"⋰⒯⋰⋰⒠⋰⋰⒥⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒞⋰⋰⒠⋰",
"⋰⒪⋰⋰⒴⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰ ⋰⒨⋰⋰⒭⋰⋰⒠⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒴⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒤⋰⋰⒴⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒢⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒟⋰⋰⒜⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒡⋰⋰⒰⋰⋰⒟⋰⋰⒟⋰⋰⒜⋰",
"⋰⒨⋰⋰⒦⋰⋰⒧⋰ ⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒝⋰⋰⒠⋰⋰⒣⋰⋰⒠⋰⋰⒩⋰⋰⒞⋰⋰⒪⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒤⋰ ⋰⒝⋰⋰⒰⋰⋰⒭⋰ ⋰⒟⋰⋰⒠⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒦⋰⋰⒜⋰ ⋰⒡⋰⋰⒰⋰⋰⒟⋰⋰⒟⋰⋰⒜⋰ ⋰⒨⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰⋰⒱⋰⋰⒜⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒯⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒢⋰⋰⒜⋰⋰⒴⋰⋰⒜⋰",
"⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒭⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰",
"⋰⒨⋰⋰⒞⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒭⋰⋰⒪⋰⋰⒦⋰⋰⒠⋰⋰⒩⋰⋰⒢⋰⋰⒜⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰",
"⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰.⋰⒨⋰⋰⒜⋰⋰⒜⋰⋰⒦⋰⋰⒠⋰ ⋰⒧⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰",
"⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒠⋰ ⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰",
"⋰⒮⋰⋰⒫⋰⋰⒜⋰⋰⒨⋰ ⋰⒦⋰⋰⒭⋰ ⋰⒦⋰⋰⒤⋰⋰⒟⋰",
"⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒰⋰",
"⋰⒭⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒯⋰⋰⒠⋰",
"⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰ ⋰Ⓙ⋰⋰⒜⋰⋰⒧⋰⋰⒟⋰⋰⒤⋰ ⋰⒧⋰⋰⒤⋰⋰⒦⋰⋰⒣⋰ ⋰⒲⋰⋰⒭⋰⋰⒩⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒢⋰⋰⒜⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒰⋰⋰⒯⋰⋰⒣⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒴⋰⋰⒦⋰⋰⒠⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰ ⋰⒝⋰⋰⒩⋰⋰⒥⋰⋰⒜⋰ ⋰⒯⋰⋰⒰⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒣⋰⋰⒜⋰⋰⒧⋰⋰⒦⋰⋰⒠⋰",
"⋰⒞⋰⋰⒰⋰⋰⒟⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒫⋰⋰⒢⋰⋰⒧⋰ ⋰⒩⋰⋰⒴⋰ ⋰⒣⋰⋰⒪⋰ ⋰⒩⋰⋰⒪⋰⋰⒪⋰⋰⒝⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒴⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒨⋰⋰⒜⋰⋰⒦⋰⋰⒤⋰⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒯⋰ ⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒰⋰⋰⒟⋰",
"⋰⒯⋰⋰⒠⋰⋰⒭⋰⋰⒤⋰ ⋰⒨⋰⋰⒜⋰⋰⒜⋰ ⋰⒞⋰⋰⒣⋰⋰⒪⋰⋰⒟⋰⋰⒱⋰⋰⒜⋰",
"⋰⒭⋰⋰⒜⋰⋰⒩⋰⋰⒟⋰⋰⒤⋰ ⋰⒦⋰⋰⒠⋰ ⋰⒝⋰⋰⒠⋰⋰⒯⋰⋰⒠⋰ ⋰⒨⋰⋰⒜⋰⋰⒭⋰ ⋰⒢⋰⋰⒜⋰⋰⒴⋰⋰⒜⋰",
"⋰Ⓓ⋰⋰⒪⋰⋰⒮⋰⋰⒯⋰",
]

cs_texts = [
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇧​ะะ🇴​ะะ🇸​ะะ🇪​ะะ🇼​ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะะ🇰​ะะ🇪​ะะ🇧​ะะ🇦​ะะ🇨​ะะ🇭​ะะ🇪​ะ, ะ🇹​ะะ🇺​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇰​ะะ🇮​ะะ🇸​ะะ🇸​ะะ🇦​ะะ🇬​ะะ🇦​ะ",
"ะ🇦​ะะ🇦​ะะ🇯​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ, ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะ ะ🇯​ะะ🇦​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇩​ะะ🇮​ะะ🇩​ะะ🇮​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ะ🇸​ะะ🇱​ะะ🇴​ะะ🇼​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇮​ะะ🇾​ะะ🇦​ะ ะ🇨​ะะ🇮​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇸​ะะ🇰​ะะ🇹​ะะ🇦​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ, ะ🇹​ะะ🇲​ะะ🇦​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇸​ะะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇫​ะะ🇮​ะะ🇷​ะะ🇸​ะะ🇪​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ",
"ะ🇨​ะะ🇺​ะะ🇩​ะะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ, ะ🇹​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะ ะ🇩​ะะ🇴​ะะ🇺​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ, ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇳​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ ะ🇼​ะะ🇦​ะะ🇱​ะะ??​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ??​ะ",
"ะ🇴​ะะ🇾​ะะ🇪​ะ ะ🇹​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ, ะ🇮​ะะ🇩​ะะ🇭​ะะ🇦​ะะ🇷​ะ ะ🇦​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇩​ะะ🇺​ะ, ะ🇴​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะะ🇪​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇪​ะะ🇯​ะ, ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇸​ะะ🇺​ะะ🇦​ะะ🇷​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇪​ะะ🇯​ะ, ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ ะ🇴​ะะ🇳​ะ ะ🇰​ะะ🇷​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇰​ะะ🇪​ะ",
"ะ🇹​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะะ🇸​ะะ🇪​ะ, ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇸​ะะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇭​ะะ🇦​ะะ🇷​ะะ🇨​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ ะ🇰​ะะ🇷​ะ ะ🇲​ะะ🇸​ะะ🇬​ะ ะ🇩​ะะ🇪​ะะ🇱​ะะ🇪​ะะ🇹​ะะ🇪​ะ, ะ🇴​ะะ🇮​ะ ะ🇸​ะะ🇺​ะะ🇦​ะะ🇷​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇰​ะะ🇪​ะ",
"ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇫​ะะ🇺​ะะ🇫​ะะ🇮​ะ, ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇩​ะะ🇮​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇮​ะ",
"ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇦​ะ, ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇦​ะะ🇧​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ",
"ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇺​ะ, ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ, ะ🇮​ะะ🇹​ะะ🇳​ะะ🇦​ะ ะ🇬​ะะ🇳​ะะ🇩​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇦​ะ ะ🇹​ะะ🇺​ะ ะ🇫​ะะ🇮​ะะ🇷​ะะ🇸​ะะ🇪​ะ ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇳​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ",
"ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇯​ะะ🇦​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇦​ะะ🇷​ะะ🇺​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะะ🇦​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ, ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇵​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ, ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇲​ะะ🇪​ะะ🇭​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ, ะ🇦​ะะ🇧​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ",
"ะ🇩​ะะ🇴​ะะ🇺​ะะ🇧​ะะ🇱​ะะ🇪​ะ ะ🇸​ะะ🇪​ะะ🇳​ะะ🇩​ะ ะ🇰​ะะ🇴​ะ ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ, ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇴​ะะ🇩​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇦​ะะ🇦​ะะ🇯​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ",
"ะ🇭​ะะ🇹​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇦​ะะ🇱​ะะ🇦​ะะ🇱​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ., ะ🇷​ะะ🇳​ะะ🇩​ะะ🇾​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇶​ะ ะ🇹​ะะ🇷​ะะ🇾​ะะ🇲​ะะ🇦​ะ",
"ะ🇵​ะะ🇦​ะะ🇷​ะะ🇦​ะ ะ🇱​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇪​ะะ🇬​ะะ🇦​ะ.., ะ🇹​ะะ🇷​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇭​ะะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ",
"ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇨​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ, ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ..",
"ะ🇨​ะะ🇺​ะะ🇩​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ, ะ🇧​ะะ🇭​ะะ🇮​ะะ🇰​ะะ🇦​ะะ🇷​ะะ🇮​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ??​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ.",
"ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇷​ะ, ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇼​ะะ🇪​ะะ🇦​ะะ🇰​ะ",
"ะ🇲​ะะ🇪​ะะ🇷​ะะ🇪​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇵​ะะ🇪​ะ ะ🇪​ะะ🇾​ะ ะ🇹​ะะ🇺​ะ ะ🇭​ะะ🇮​ะะ🇯​ะะ🇩​ะะ🇪​ะ, ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇼​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇴​ะ",
"ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ, ะ🇹​ะะ🇺​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇰​ะะ🇮​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇨​ะะ🇱​ะะ🇦​ะะ🇮​ะะ🇲​ะ ะ🇨​ะะ🇷​ะะ🇼​ะะ🇦​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇸​ะะ🇰​ะะ🇹​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ, ะ??​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇨​ะะ??​ะะ🇺​ะะ🇩​ะ ะ🇯​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇩​ะะ🇮​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇮​ะ, ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇦​ะ",
"ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇦​ะะ🇧​ะ, ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ, ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇺​ะ",
"ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇱​ะะ🇪​ะ ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ, ะ🇹​ะะ🇪​ะะ??​ะะ🇾​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ะ🇮​ะะ🇹​ะะ🇳​ะะ🇦​ะ ะ🇬​ะะ🇳​ะะ🇩​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะะ🇦​ะ ะ🇹​ะะ🇺​ะ ะ🇫​ะะ🇮​ะะ🇷​ะะ🇸​ะะ🇪​ะ ะ🇳​ะะ🇪​ะะ🇹​ะ ะ🇴​ะะ🇳​ะ ะ🇴​ะะ🇫​ะะ🇫​ะ, ะ🇬​ะะ🇷​ะะ🇮​ะะ🇧​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇯​ะะ🇦​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇦​ะะ🇷​ะะ🇺​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ, ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇷​ะะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะะ🇦​ะ",
"ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ, ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇵​ะ, ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇱​ะ ะ🇲​ะะ🇪​ะะ🇭​ะ, ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ",
"ะ??​ะะ🇧​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ, ะ🇩​ะะ🇴​ะะ🇺​ะะ🇧​ะะ🇱​ะะ🇪​ะ ะ🇸​ะะ🇪​ะะ🇳​ะะ🇩​ะ ะ🇰​ะะ🇴​ะ ะ🇨​ะะ🇵​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ ะ🇨​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇲​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇴​ะะ🇩​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇦​ะะ🇦​ะะ🇯​ะ ะ🇲​ะะ🇪​ะะ🇭​ะะ🇭​ะ, ะ🇭​ะะ🇹​ะ ะ🇹​ะะ🇧​ะะ🇰​ะะ🇨​ะ ะ🇩​ะะ🇦​ะะ🇱​ะะ🇦​ะะ🇱​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ.",
"ะ🇷​ะะ🇳​ะะ🇩​ะะ🇾​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇯​ะะ🇱​ะะ🇩​ะะ🇮​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇶​ะ ะ🇹​ะะ🇷​ะะ🇾​ะะ🇲​ะะ🇦​ะ, ะ🇵​ะะ🇦​ะะ🇷​ะะ🇦​ะ ะ🇱​ะะ🇮​ะะ🇰​ะะ🇭​ะะ🇪​ะะ🇬​ะะ🇦​ะ..",
"ะ🇹​ะะ🇷​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇭​ะะ🇧​ะะ🇭​ะะ🇦​ะะ🇰​ะ, ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇩​ะะ🇨​ะะ🇪​ะ ะ??​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇦​ะะ🇬​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะะ🇹​ะะ🇪​ะ.., ะ🇨​ะะ🇺​ะะ🇩​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ",
"ะ🇧​ะะ🇭​ะะ🇮​ะะ🇰​ะะ🇦​ะะ🇷​ะะ🇮​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇸​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ., ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇨​ะะ🇵​ะ ะ🇨​ะะ🇷​ะ",
"ะ🇨​ะะ🇵​ะ ะ🇧​ะะ🇴​ะะ🇱​ะ ะ🇱​ะะ🇴​ะะ🇼​ะ ะ🇱​ะะ🇪​ะะ🇻​ะะ🇪​ะะ🇱​ะ ะ🇼​ะะ🇪​ะะ🇦​ะะ🇰​ะ, ะ🇲​ะะ🇪​ะะ🇷​ะะ🇪​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇵​ะะ🇪​ะ ะ🇪​ะะ🇾​ะ ะ🇹​ะะ🇺​ะ ะ🇭​ะะ🇮​ะะ🇯​ะะ🇩​ะะ🇪​ะ",
"ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇨​ะะ🇺​ะะ🇩​ะะ🇼​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇴​ะ, ะ🇫​ะะ🇷​ะะ🇪​ะะ🇪​ะ ะ🇲​ะะ🇪​ะะ🇾​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇾​ะะ🇰​ะะ🇪​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇨​ะะ🇱​ะะ🇦​ะะ🇮​ะะ🇲​ะ ะ🇨​ะะ🇷​ะะ🇼​ะะ🇦​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇮​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇬​ะ ะ🇸​ะะ🇰​ะะ🇹​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇳​ะ ะ🇻​ะะ🇪​ะะ🇸​ะะ🇮​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇳​ะะ🇩​ะะ🇮​ะ, ะ🇹​ะะ🇺​ะ ะ🇰​ะะ🇾​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะ ะ🇯​ะะ🇦​ะ"
"ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇷ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ ะ🇧ะะ🇪ะะ🇯ะ",
"ะ🇴ะะ🇷ะ ะ🇧ะะ🇩ะะ🇦ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ",
"ะ🇴ะะ🇷ะ ะ🇧ะะ🇩ะะ🇦ะ",
"ะ🇴ะะ🇷ะ ะ🇧ะะ🇩ะะ🇦ะ ะ🇴ะะ🇾ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇺ะะ🇷ะ",
"ะ🇴ะะ🇾ะะ🇪ะ ะ🇰ะะ🇪ะะ🇩ะะ🇪ะ",
"ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇰ะะ🇪ะ",
"ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะะ🇳ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ",
"ะ🇲ะะ🇰ะะ🇱ะ ะ??ะะ🇹ะะ🇭ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇨ะะ🇭ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇳ะะ🇦ะะ🇳ะะ🇮ะ ะ🇲ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇱ะ",
"ะ🇹ะะ🇪ะะ🇯ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇷ะะ🇳ะะ🇩ะะ🇨ะะ🇪ะ",
"ะ🇴ะะ🇾ะะ🇪ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇲ะะ🇷ะะ🇪ะะ🇳ะะ🇬ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇾ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇮ะะ🇾ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇬ะะ🇦ะะ🇳ะะ🇩ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇩ะะ🇦ะะ🇩ะะ🇮ะ ะ🇰ะะ🇦ะ ะ🇫ะะ🇺ะะ🇩ะะ🇩ะะ🇦ะ",
"ะ🇲ะะ🇰ะะ🇱ะ ะ🇺ะะ🇹ะะ🇭ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะะ🇳ะะ🇨ะะ🇴ะะ🇩ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ??ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇧ะะ🇺ะะ🇷ะ ะ🇩ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇦ะ ะ🇫ะะ🇺ะะ🇩ะะ🇩ะะ🇦ะ ะ🇲ะะ🇪ะ ะ🇱ะะ🇦ะะ🇺ะะ🇩ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇻ะะ🇦ะ",
"ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇲ะะ🇦ะะ🇷ะ ะ🇬ะะ🇦ะะ🇾ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇲ะะ🇷ะะ🇺ะ",
"ะ🇯ะะ🇦ะะ🇱ะะ🇮ะะ🇩ะ ะ🇰ะะ🇷ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ",
"ะ🇲ะะ🇨ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇷ะะ🇴ะะ🇰ะะ🇪ะะ🇳ะะ🇬ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ",
"ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ.ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ",
"ะ🇷ะะ🇳ะะ🇮ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ",
"ะ🇸ะะ🇵ะะ🇦ะะ🇲ะ ะ🇰ะะ🇷ะ ะ🇰ะะ🇮ะะ🇩ะ",
"ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ",
"ะ🇷ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ",
"ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ ะ??ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇱ะะ🇮ะะ🇰ะะ🇭ะ ะ🇼ะะ🇷ะะ🇳ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ",
"ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇺ะะ🇹ะะ🇭ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇨ะะ🇭ะะ🇱ะ ะ🇨ะะ🇺ะะ🇩ะะ🇰ะะ🇪ะ ะ🇩ะะ🇮ะะ🇰ะะ🇭ะะ🇦ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇯ะะ🇱ะะ🇩ะะ🇮ะ ะ🇹ะะ🇾ะะ🇵ะ ะ🇨ะะ🇷ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ ะ🇭ะะ🇦ะะ🇱ะะ🇰ะะ🇪ะ",
"ะ🇨ะะ🇺ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇬ะะ🇱ะ ะ🇳ะะ🇾ะ ะ🇭ะะ🇴ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇨ะะ🇺ะะ🇩ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ ะ🇧ะะ🇳ะะ🇯ะะ🇦ะ ะ🇹ะะ🇺ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇲ะะ🇦ะะ🇰ะะ🇮ะะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇳ะะ🇴ะะ🇴ะะ🇧ะ",
"ะ🇬ะะ🇦ะะ🇳ะะ🇩ะะ🇦ะ ะ🇨ะะ🇾ะะ🇺ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇷ะะ🇭ะะ🇦ะ ะ🇹ะะ🇺ะ ?",
"ะ🇮ะะ🇹ะะ🇳ะะ🇦ะ ะ🇬ะะ🇳ะะ🇩ะะ🇦ะ ะ🇳ะะ🇾ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇦ะะ🇨ะะ🇭ะะ🇪ะ ะ🇸ะะ🇪ะ ะ🇨ะะ🇺ะะ🇩ะ",
"ะ🇲ะะ🇦ะะ🇦ะ⍟ ะ🇱ะะ🇪ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇾ะะ🇦ะ ะ🇹ะะ🇺ะ ะ🇸ะะ🇺ะ⍟ ะ🇧ะะ🇦ะะ🇹ะ ะ🇦ะะ🇧",
"ะ🇲ะะ🇦ะะ🇰ะะ🇦ะะ🇫ะะ🇺ะะ🇩ะะ🇩ะะ🇦ะ ะ🇫ะะ🇦ะะ🇹ะ ะ🇬ะะ🇾ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇷ะะ🇺ะะ🇰ะ",
"ะ🇸ะะ🇭ะะ🇦ะะ🇳ะะ🇹ะ ะ🇧ะะ🇪ะะ🇹ะะ🇭ะ ะ🇲ะะ🇦ะะ🇩ะะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇼ะะ🇷ะะ🇳ะะ🇦ะ ะ🇲ะะ🇦ะะ🇰ะะ🇦ะะ🇧ะะ🇴ะะ🇸ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇪ะะ🇾ะ.",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ..",
"ะ🇱ะะ🇼ะะ🇩ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะะ🇰ะะ🇪ะ ะ🇵ะะ🇬ะะ🇱ะ ะ🇩ะะ🇪ะะ🇰ะะ🇭ะ.",
"ะ🇲ะะ🇦ะะ🇨ะะ🇭ะะ🇦ะะ🇷ะ ะ🇰ะะ🇮ะ ะ🇯ะะ🇭ะะ🇦ะะ🇦ะะ🇹ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇦ะะ🇨ะะ🇭ะะ🇪ะ ะ🇸ะะ🇪ะ ะ🇾ะะ🇭ะะ🇦ะะ🇵ะะ🇪ะ ะ🇹ะะ🇺ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇲ะ ะ🇩ะะ🇺ะ ะ🇹ะะ🇦ะะ🇵ะะ🇦ะ ะ🇹ะะ🇦ะะ🇵ะ?",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ะꜱะะ🇩ะะ🇦ะะ??ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇭ะะ🇳ะ ꜱะ🇧ะꜱะ🇧ะะ🇪ะ ะ🇧ะะ🇩ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ.",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇴ะꜱะꜱะะ🇪ะ ะ🇧ะะ🇦ะะ🇩ะะ🇮ะ ะ??ะะ🇦ะะ🇳ะะ🇩ะะ🇩ะะ🇩ะะ🇩ะะ🇩ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇦ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇧ะะ🇦ะะ🇦ะะ🇿ะ ะ🇪ะะ🇾ะ ะ🇩ะะ🇪ะะ🇰ะะ🇭ะ",
"ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇮ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇦ะะ🇧ะ ะ🇴ะะ🇷..",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇮ะ ะ🇭ะะ🇲ะ ะ🇳ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇪ะ ꜱะ🇹ะะ🇭ะ ะ🇷ะะ🇪ะะ🇪ะะ🇱ะꜱะ ะ🇧ะะ🇳ะะ🇪ะะ🇬ะะ🇦ะ ะ🇷ะะ🇴ะะ🇦ะะ🇩ะ ะ🇵ะะ🇪ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇪ะะ🇰ะ ะ🇩ะะ🇦ะะ🇲ะ ะ🇹ะะ🇴ะะ🇵ะ ꜱะ🇪ะxะ🇾ะ",
"ะ🇲ะะ🇦ะะ🇱ะะ🇺ะ🇲ะ ะ🇳ะะ🇦ะ ะ🇵ะะ🇭ะ🇷ะ ะ🇰ะะ🇪ꜱะะ🇪ะ ะ🇱ะะ🇪ะะ🇹ะะ🇦ะ ะ🇭ะะ🇺ะ ะ🇲ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ ะ🇹ะะ🇦ะะ🇵ะะ🇦ะ ะ🇹ะะ🇦ะะ🇵ะะ🇵ะะ🇵ะะ🇵ะะ🇵ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ ะ🇹ะะ🇺ะ ะ🇰ะะ🇪ะะ🇷ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇾ะะ🇵ะะ🇮ะะ🇳ะะ🇬ะ ะ🇰ะะ🇷ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ",
"ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇵ะะ🇰ะะ🇩ะ ะ🇱ะะ🇼ะะ🇩ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะ ะ🇼ะะ🇷ะะ🇳ะะ🇦ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇵ะะ🇰ะะ🇩ะ",
"ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇰ะะ🇮ะ ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇲ะะ🇹ะะ🇨ะะ🇭ะ ะ🇰ะะ🇷ะะ🇷ะะ🇷ะ",
"ะ🇱ะะ🇼ะะ🇩ะะ🇦ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ ะ🇹ะะ🇺ะ",
"ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ะ🇰ะะ🇮ะ ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇲ะะ🇹ะะ🇨ะะ🇭ะ ะ🇳ะะ🇭ะะ🇮ะ ะ🇭ะะ🇴ะ ะ🇷ะะ🇭ะะ🇮ะ ะ🇰ะะ🇾ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇪ะะ🇸ะะ🇪ะ",
"ะ🇦ะะ🇱ะะ🇪ะ ะ🇦ะะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇱ะะ🇦ะ ะ🇧ะะ🇨ะะ🇭ะะ🇦ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇰ะะ🇦ะ ะ🇧ะะ🇴ะะ🇸ะะ🇩ะะ🇦ะ ะ🇸ะะ🇺ะะ🇳ะ",
"ะ🇨ะะ🇭ะะ🇺ะะ🇩ะ ะ🇬ะะ🇾ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇧ะะ🇦ะะ🇦ะะ🇿ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ꜱะ🇪ะะ🇪ะะ🇪ะ ะ🇹ะะ🇺ะ",
"ะ🇲ะะ🇪ะะ🇳ะะ🇺ะ ะ🇰ะะ🇮ะ ะ🇵ะะ🇹ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ",
"ะ🇰ะะ🇴ะะ🇮ะ ะ🇧ะะ🇦ะะ🇦ะะ🇹ะ ะ🇳ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ",
"ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะ ะ🇲ะะ🇦ะะ🇰ะะ🇦ะะ🇧ะะ🇴ะะ🇸ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ",
"ะ🇽ะะ🇭ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇰ะะ🇮ะะ🇩ะꜱะꜱะꜱะꜱะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะ ะ🇬ะะ🇾ะะ🇮ะ ะ🇦ะะ🇧ะ ꜰะ🇷ะะ🇦ะ🇷ะ ะ🇲ะะ🇹ะ ะ🇭ะะ🇴ะะ🇳ะะ🇦ะ",
"ะ🇾ะะ🇪ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇨ะะ🇭ะะ🇱ะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ",
"ะ🇰ะะ🇮ะะ🇩ะꜱะꜱะꜱะ ꜰะ🇷ะะ🇦ะ🇷ะ ะ🇳ะะ🇦ะ ะ🇭ะะ🇴ะ ะ🇹ะะ🇺ะ ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇭ะ",
"ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇼ะะ🇩ะะ🇪ะ ꜱะ🇭ะ🇷ะ🇲ะ ะ🇰ะะ🇷ะ",
"ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇮ะ ะ🇬ะะ🇱ะะ🇮ะะ🇾ะะ🇦ะ ะ🇵ะะ🇩ะะ🇼ะะ🇪ะะ🇬ะะ🇦ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇴ะ",
"ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇳ะะ🇦ะะ🇱ะะ🇱ะะ🇮ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇰ะะ🇪ะ",
"ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ꜱะ🇦ะะ🇩ะะ🇦ะ🇰ะ ะ🇵ะ🇷ะ ะ🇱ะะ🇮ะะ🇹ะะ🇦ะะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ 😂😆🤤",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ ะ🇲ะะ🇦ะะ🇩ะะ🇪ะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇴ะะ🇩ะ ะ🇰ะ🇷ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ꜱะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇺ะ 😼😂🤤",
"ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇳ะะ🇪ะ ꜱะ🇭ะ🇴ะ🇷ะ ะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇨ะะ🇭ะะ🇴ะ🇷ะ ะ🇭ะะ🇪ะ 💋💋💦",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ 😂👻🔥",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇦ะะ🇮ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇦ะ ะ🇦ะะ🇮ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะ ะ🇧ะะ🇪ะะ🇩ะ ะ🇵ะะ🇪ะะ🇭ะะ🇮ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะ ะ🇩ะะ🇮ะะ🇦ะ 💦💦💦💦",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇪ะ ะ🇲ะะ🇪ะ ะ🇦ะะ🇦ะะ🇦ะ🇬ะ ะ🇱ะะ🇦ะะ🇬ะะ🇦ะะ🇩ะะ🇮ะะ🇦ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇲ะะ🇴ะะ🇹ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇰ะะ🇪ะ 🔥🔥💦😆😆",
"ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇳ะะ🇮ะะ🇰ะะ🇦ะะ🇱ะ",
"ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ 😆👻🤤",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะะ🇹ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇰ะะ🇪ะ ะ🇵ะะ🇺ะะ🇷ะะ🇦ะ ꜰะ🇦ะะ🇦ะะ🇩ะ ะ🇩ะะ🇮ะะ🇦ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇰ะะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ 😆💦🤤",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇰ะะ🇴ะ ะ🇪ะะ🇹ะะ🇳ะะ🇦ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇹ะะ🇴ะ ะ🇲ะะ🇪ะะ🇷ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇧ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะะ🇾ะะ🇮ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇹ะะ🇦ะ ꜰะ🇮ะ🇷ꜱะะ🇪ะ ♥️💦😆😆😆😆",
"ะ🇭ะะ🇦ะะ🇷ะะ🇮ะ ะ🇭ะะ🇦ะะ🇷ะะ🇮ะ ะ🇬ะะ🇭ะะ🇦ะะ🇦ꜱะ ะ🇲ะะ🇪ะ ะ🇯ะะ🇭ะะ🇴ะะ🇵ะะ🇩ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ 🤣🤣💋💦",
"ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇹ะะ🇪ะะ🇷ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇰ะะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ ะ🇹ะะ🇪ะะ🇷ะะ🇦ะ ะ🇧ะะ🇦ꜱะะ🇰ะะ🇦ะ ะ🇳ะะ🇭ะะ🇮ะ ะ🇭ะะ🇪ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ꜱะ🇪ะ ะ🇱ะะ🇦ะะ🇩ะะ🇪ะะ🇬ะะ🇦ะ ะ🇹ะะ🇺ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇧ะะ🇴ะะ🇲ะ🇧ะ ะ🇩ะะ🇦ะะ🇱ะะ🇰ะะ🇪ะ ะ🇺ะะ🇩ะะ🇦ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇼ะะ🇩ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇹ะะ🇷ะะ🇦ะะ🇮ะ🇳ะ ะ🇲ะะ🇪ะ ะ🇱ะะ🇪ะะ🇯ะะ🇦ะะ🇰ะะ🇪ะ ะ🇹ะะ🇴ะะ🇵ะ ะ🇧ะะ🇪ะะ🇩ะ ะ🇵ะะ🇪ะ ะ🇱ะะ🇮ะะ🇹ะะ🇦ะะ🇰ะะ🇪ะ ะ🇨ะะ??ะะ🇴ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 🤣🤣💋💋",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇳ะะ🇺ะะ🇩ะะ🇪ꜱะ ะ🇬ะะ🇴ะะ🇴ะ🇬ะ🇱ะะ🇪ะ ะ🇵ะะ🇪ะ ะ🇺ะะ🇵ะะ🇱ะะ🇴ะะ🇦ะ🇩ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇪ะะ🇼ะะ🇩ะะ🇪ะ 👻🔥",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇳ะะ🇺ะะ🇩ะะ🇪ꜱะ ะ🇬ะะ🇴ะะ🇴ะ🇬ะ🇱ะะ🇪ะ ะ🇵ะะ🇪ะ ะ🇺ะะ🇵ะะ🇱ะะ🇴ะะ🇦ะ🇩ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇪ะะ🇼ะะ🇩ะะ🇪ะ 👻🔥",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇰ะะ🇪ะ ะ🇻ะะ🇮ะะ🇩ะะ🇪ะ🇴ะ ะ🇧ะะ🇦ะะ🇳ะะ🇦ะะ🇰ะะ🇪ะ ะ🇽ะ🇳🇽🇽.🇨🇴🇲 ะ🇵ะะ🇪ะ ะ🇳ะะ🇪ะะ🇪ะะ🇱ะะ🇦ะ🇲ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 💦💋",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇦ะะ🇮ะ ะ🇰ะะ🇴ะ ะ🇵ะ🇴🇷🇳🇭🇺🇧.🇨🇴🇲 ะ🇵ะะ🇪ะ ะ🇺ะะ🇵ะะ🇱ะะ🇴ะะ🇦ะ🇩ะ ะ🇰ะะ🇦ะ🇷ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇪ะ 🤣💋💦",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇪ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇦ะะ🇰ะะ🇰ะ🇴ะ ꜱะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇼ะะ🇦ะะ🇻ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ 🤣🤣",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ꜰะะ🇦ะะ🇦ะะ🇩ะะ🇰ะะ🇪ะ ะ🇷ะะ🇦ะะ🇰ะะ🇩ะะ🇮ะะ🇦ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇪ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇯ะะ🇦ะะ🇦ะ ะ🇦ะะ🇧ะะ🇧ะ ꜱะะ🇮ะะ🇱ะะ🇼ะะ🇦ะะ🇱ะะ🇪ะ 👄👄",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇦ะะ🇦ะะ🇱ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇱ะะ🇪ะะ🇹ะะ🇮ะ ะ🇲ะะ🇪ะะ🇷ะะ🇮ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇧ะะ🇦ะะ🇩ะะ🇪ะ ะ🇲ะะ🇦ꜱะะ🇹ะะ🇮ะ ꜱะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇲ะะ🇪ะะ🇳ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇦ะ ะ🇧ะะ🇴ะะ🇭ะะ🇴ะะ🇹ะ ꜱะะ🇦ꜱะะ🇹ะะ🇪ะ ꜱะะ🇪ะ",
"ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇹ะะ🇺ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ꜱะะ🇪ะ ะ🇱ะะ🇪ะะ🇬ะะ🇦ะ ะ🇵ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇰ะะ🇦ะ🇷ะะ🇰ะะ🇪ะ ะ🇳ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะ 💦💋",
"ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇦ะะ🇬ะะ🇱ะะ🇮ะ ะ🇧ะะ🇦ะะ🇦ะ🇷ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇱ะะ🇪ะะ🇰ะะ🇪ะ ะ🇦ะะ🇦ะะ🇾ะะ🇦ะ ะ🇲ะะ🇦ะะ🇹ะะ🇭ะ ะ🇰ะะ🇦ะะ🇹ะ ะ🇴ะ🇷ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇲ะะ🇴ะะ🇹ะะ🇪ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇼ะะ🇦ะะ🇾ะะ🇦ะ ะ🇲ะะ🇦ะะ🇹ะะ🇭ะ ะ🇰ะะ🇦ะ🇷ะ",
"ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇧ะะ🇪ะะ🇹ะะ🇦ะ ะ🇹ะะ🇺ะะ🇯ะะ🇭ะะ🇪ะ ะ🇲ะะ🇦ะะ🇦ꜱะ🇫ะ ะ🇰ะะ🇮ะะ🇦ะ 🤣ะ🇹ะะ🇺ะ ะ🇦ะะ🇧ะะ🇧ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇰ะ🇴ะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ",
"ꜱะ🇭ะะ🇦ะะ🇷ะะ🇦ะ🇲ะ ะ🇰ะะ🇦ะ🇷ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇦ะ ะ🇬ะะ🇦ะะ🇦ะะ🇱ะะ🇮ะะ🇦ะ ꜱะ🇺ะะ🇳ะะ🇼ะะ🇦ะะ🇾ะะ🇪ะะ🇬ะะ🇦ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇺ะะ🇵ะะ🇪ะ🇷ะ",
"ะ🇦ะะ🇧ะะ🇪ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇦ะะ🇺ะะ🇰ะะ🇦ะะ🇹ะ ะ🇳ะะ🇭ะะ🇮ะ ะ🇭ะะ🇪ะะ🇹ะ🇴ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇱ะะ🇪ะะ🇰ะะ🇪ะ ะ🇦ะะ🇦ะะ🇾ะะ🇦ะ ะ🇲ะะ🇦ะะ🇹ะะ🇭ะ ะ🇰ะะ🇦ะ??ะ ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะ",
"ะ🇰ะะ🇮ะะ🇩ะ🇿ะ ะ🇲ะะ🇦ะะ🇩ะะ🇦ะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇰ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะ🇷ะ ะ🇱ะะ🇮ะะ🇾ะะ🇪ะ ะ🇧ะะ🇭ะะ🇦ะะ🇮ะ ะ🇩ะะ🇪ะะ🇩ะะ🇮ะะ🇾ะะ🇦ะ",
"ะ🇯ะะ🇺ะะ🇳ะะ🇬ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะ ะ🇳ะะ🇦ะะ🇨ะะ🇭ะะ🇹ะะ🇦ะ ะ🇭ะะ🇪ะ ะ🇲ะะ🇴ะ🇷ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇦ะะ🇮ะ ะ🇩ะะ🇪ะะ🇰ะะ🇰ะะ🇪ะ ꜱะ🇦ะ🇧ะ ะ🇧ะะ🇴ะะ🇱ะะ🇹ะะ🇪ะ ะ🇴ะะ🇳ะ🇨ะะ🇪ะ ะ🇲ะะ🇴ะ🇷ะะ🇪ะ ะ🇴ะะ🇳ะ🇨ะะ🇪ะ ะ🇲ะะ🇴ะ🇷ะะ🇪ะ 🤣🤣💦💋",
"ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇬ะะ🇦ะะ🇱ะะ🇮ะ ะ🇲ะะ🇪ะ ะ🇷ะะ🇪ะะ🇭ะะ🇹ะะ🇦ะ ะ🇭ะะ🇪ะ ꜱะ🇦ะะ🇳ะะ🇩ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇦ะ ะ🇴ะ🇷ะ ะ🇧ะะ🇦ะะ🇳ะะ🇦ะ ะ🇩ะะ🇮ะะ🇦ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ 🤤🤣",
"ꜱะ🇦ะ🇧ะ ะ🇧ะะ🇴ะะ🇱ะะ🇹ะะ🇪ะ ะ🇲ะะ🇺ะะ🇯ะะ🇭ะะ🇰ะ🇴ะ ะ🇵ะะ🇦ะะ🇵ะะ🇦ะ ะ🇨ะะ🇾ะะ🇺ะะ🇰ะะ🇮ะ ะ🇲ะะ🇪ะะ🇳ะะ🇪ะ ะ🇰ะ🇷ะะ??ะะ🇮ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇵ะ🇷ะะ🇪ะะ🇬ะะ🇳ะะ🇪ะะ🇳ะะ🇹ะ 🤣🤣",
"ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇦ะ ะ🇱ะะ🇴ะะ🇺ะะ🇩ะะ🇦ะ ะ🇴ะ🇷ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇴ะะ🇩ะะ🇦ะ",
"ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇨ะะ🇭ะะ🇦ะะ🇱ะ ะ🇹ะะ🇺ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇨ะะ🇭ะะ🇮ะะ🇾ะะ🇦ะ ะ🇩ะะ🇮ะะ🇰ะะ🇦ะ",
"ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะ ะ🇧ะะ🇦ะะ🇨ะะ🇭ะะ🇭ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇮ะะ🇦ะ ะ🇳ะะ🇦ะะ🇳ะะ🇬ะะ🇦ะ ะ🇰ะะ🇦ะ🇷ะะ🇰ะะ🇪ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะꜰะ ะ🇭ะะ🇪ะ ะ🇧ะะ🇦ะะ🇩ะะ🇮ะ ꜱะ🇪xะ🇾ะ ะ🇺ꜱะะ🇰ะ??ะ ะ🇵ะะ🇮ะะ🇱ะะ🇦ะะ🇰ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇴ะะ🇩ะะ🇪ะะ🇳ะะ🇬ะะ🇪ะ ะ🇵ะะ🇪ะะ🇵ꜱะะ🇮ะ",
"2 ะ🇷ะะ🇺ะะ🇵ะะ🇦ะ🇾ะ ะ🇰ะะ🇮ะ ะ🇵ะะ🇪ะะ🇵ꜱะะ🇮ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇺ะะ🇲ะะ🇲ะะ🇾ะ ꜱะ🇦ะ🇧ꜱะะ🇪ะ ꜱะ🇪xะ🇾ะ 💋💦",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇨ะะ🇭ะะ🇪ะะ🇪ะ🇲ꜱะ ꜱะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇩ะะ🇼ะะ🇦ะะ🇻ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇲ะะ🇦ะะ🇩ะะ🇪ะ🇷ะะ🇨ะะ🇭ะะ🇴ะะ🇴ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 💦🤣",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะะ🇪ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะะ🇰ะะ🇪ะ ꜰะะ🇦ะ🇷ะะ🇦ะ🇷ะ ะ🇭ะะ🇴ะะ🇯ะะ🇦ะะ🇻ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ ะ🇭ะะ🇺ะะ🇮ะ ะ🇭ะะ🇺ะะ🇮ะ ะ🇭ะะ🇺ะะ🇮ะ",
"ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇱ะะ🇦ะะ🇦ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇮ะะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ 💋💦🤣",
"ะ🇦ะะ🇷ะะ🇪ะ ะ🇷ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇨ะะ🇾ะะ🇺ะ ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇵ะะ🇦ะะ🇰ะะ🇦ะะ🇩ะ ะ🇳ะะ🇦ะ ะ🇵ะะ🇦ะะ🇦ะะ🇦ะ ะ🇷ะะ🇦ะะ🇭ะะ🇦ะ ะ🇦ะะ🇵ะะ🇳ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇵ะ ะ🇰ะะ🇦ะ ะ🇭ะะ🇦ะะ🇭ะะ🇦ะะ🇭ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ🤣🤣",
"ꜱะ🇺ะะ🇳ะ ꜱะ🇺ะะ🇳ะ ꜱะ🇺ะะ🇦ะ🇷ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ะะ🇱ะะ🇱ะะ🇪ะ ะ🇯ะะ🇭ะะ🇦ะะ🇳ะะ🇹ะ🇴ะ ะ🇰ะะ🇪ะ ꜱะ🇴ะะ🇺ะะ🇩ะะ🇦ะะ🇬ะะ🇦ะ🇷ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇺ะะ🇲ะะ🇲ะะ🇾ะ ะ🇰ะะ🇮ะ ะ🇳ะะ🇺ะะ🇩ะะ🇪ꜱะ ะ🇧ะะ🇭ะะ🇪ะะ🇯ะ",
"ะ🇦ะะ🇧ะะ🇪ะ ꜱะ🇺ะะ🇳ะ ะ🇱ะะ🇴ะะ🇩ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇧ะะ🇪ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇦ะ ะ🇧ะะ🇭ะะ🇴ꜱะะ🇩ะะ🇦ะ ꜰะะ🇦ะะ🇦ะะ🇩ะ ะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะะ🇦ะะ🇰ะ🇴ะ ะ🇰ะะ🇭ะะ🇺ะะ🇱ะะ🇪ะ ะ🇧ะะ🇦ะะ🇯ะะ🇦ะ🇷ะ ะ🇲ะะ🇪ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะ ะ🇩ะะ🇦ะะ🇱ะะ🇦ะ 🤣🤣💋",
"ꜱะ🇭ะ🇷ะ🇲ะ ะ🇰ะ🇷ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะะ🇦ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇬ะะ🇦ะะ🇮ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะ ะ🇵ะะ🇰ะะ🇩ะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ",
"ะ🇹ะะ🇺ะ ะ🇪ะะ🇰ะ ะ🇰ะะ🇦ะะ🇦ะ🇲ะ ะ🇰ะ🇷ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇺ะะ🇩ะะ🇼ะะ🇦ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇸ะะ🇹ะะ🇭ะ",
"ะ🇷ะะ🇳ะะ🇩ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇩ะะ🇰ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇴ะ🇷ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ ะ🇰ะะ🇮ะะ🇩ꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะꜱะ",
"ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇪ะะ??ะ🇳ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะะ🇮ะ ะ🇩ะะ🇦ะะ🇦ะะ🇱ะ",
"ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇨ะะ🇭ะะ🇴ะะ🇴ꜱะ ะ🇯ะะ🇦ะะ🇱ะะ🇩ะะ🇮ะ ะ🇸ะะ🇪ะ",
"ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇴ะ ะ🇨ะะ🇺ꜱะะ🇼ะะ🇦ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ",
"ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇱ะะ🇦ะะ🇺ะะ🇩ะะ🇪ะ ะ🇹ะะ🇲ะะ🇨ะ",
"ะ🇧ะะ🇭ะะ🇪ะ🇳ะ ะ🇰ะะ🇪ะ ะ🇹ะะ🇦ะะ🇰ะะ🇰ะะ🇪ะ ะ🇹ะะ🇲ะะ🇱ะ",
"ะ🇦ะะ🇧ะะ🇱ะะ🇦ะ ะ🇹ะะ🇪ะะ🇷ะะ🇦ะ ะ🇰ะะ🇭ะะ🇦ะ🇳ะ ะ🇩ะะ🇦ะ🇳ะ ะ🇨ะะ🇭ะะ🇴ะะ🇩ะะ🇳ะะ🇪ะ ะ🇰ะะ🇮ะ ะ🇧ะะ🇦ะ🇷ะะ🇮ะะ🇮ะ",
"ะ🇧ะะ🇪ะะ🇹ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ꜱะ🇧ꜱะะ🇪ะ ะ🇧ะะ🇩ะะ🇮ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะ ะ🇯ะะ🇭ะะ🇦ะะ🇹ะ ะ??ะะ🇪ะ ะ🇵ะะ🇮ꜱะꜱะꜱะ🇺ะะ🇺ะะ🇺ะะ🇺ะะ🇺ะะ🇺ะะ🇺ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇵ะะ🇪ะ ะ🇱ะะ🇹ะะ🇰ะะ🇮ะะ🇹ะ ะ🇲ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะะ🇱ะ ะ🇰ะะ🇮ะ ะ🇧ะะ🇴ะะ🇳ะะ🇩ะ ะ🇭ะ ะ🇹ะะ🇺ะะ🇺ะะ🇺ะ",
"ะ🇰ะะ🇦ꜱะะ🇭ะ ะ🇴ꜱะ ะ🇩ะะ🇮ะ🇳ะ ะ🇲ะะ🇺ะะ🇹ะะ🇭ะ ะ🇲ะ🇷ะะ🇰ะะ🇪ะ ꜱะ🇴ะะ🇯ะะ🇹ะะ🇦ะ ะ🇲ะ ะ🇹ะะ🇺ะ ะ🇵ะะ🇦ะะ🇮ะะ🇩ะะ🇦ะ ะ🇳ะะ🇦ะ ะ🇭ะะ🇴ะะ🇹ะะ🇦ะะ🇦ะ",
"ะ🇬ะะ🇱ะะ🇹ะะ🇮ะ ะ🇰ะ🇷ะะ🇩ะะ🇮ะ ะ🇹ะะ🇺ะะ🇯ะะ🇼ะ ะ🇵ะะ🇦ะะ🇮ะะ🇩ะะ🇦ะ ะ🇰ะ🇷ะะ🇰ะะ🇪ะ ะ🇹ะะ🇪ะะ🇷ะะ🇾ะ ะ🇲ะะ🇦ะ ะ🇳ะะ🇪ะ ะ🇦ะะ🇧ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇹ะะ🇺ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ꜱะ🇵ะะ🇪ะะ🇪ะะ🇩ะ ะ🇵ะะ🇰ะะ🇩ะะ🇩ะะ??ะ",
"ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇦ะะ🇮ะ🇳ะ ะ🇱ะะ🇼ะะ🇩ะะ🇦ะ ะ🇩ะะ🇦ะะ🇱ะ ะ🇱ะะ🇪ะ ะ🇦ะะ🇵ะะ🇳ะะ🇮ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะะ🇦ะะ🇦ะ",
"ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇪ะะ🇮ะ🇳ะ ะ🇧ะะ🇦ะะ🇲ะะ🇧ะ🇺ะ ะ🇩ะะ🇪ะะ🇩ะะ🇺ะะ🇳ะะ🇬ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะ",
"ะ🇬ะะ🇦ะะ🇳ะะ🇩ะ ꜰะะ🇹ะะ🇮ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇱ะะ🇰ะะ🇰ะะ🇰ะ ะ🇹ะะ🇺ะ ะ🇨ะะ🇺ะะ🇩ะ ะ🇾ะะ🇭ะะ🇦ะ",
"ะ🇬ะะ🇴ะะ🇹ะะ🇪ะ ะ🇰ะะ🇮ะะ🇹ะะ🇳ะะ🇪ะ ะ🇧ะะ🇭ะะ🇮ะ ะ🇧ะะ🇦ะะ🇩ะะ🇪ะ ะ🇭ะะ🇴ะ, ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇳ะะ🇮ะะ🇨ะะ🇭ะะ🇪ะ ะ🇭ะะ🇮ะ ะ🇷ะะ🇪ะะ🇭ะะ🇹ะะ🇪ะ ะ🇭ะะ🇦ะ",
"ะ🇭ะะ🇦ะะ🇿ะะ🇦ะะ🇦ะ🇷ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇬ะะ🇦ะะ🇦ะะ🇳ะะ🇩ะ ะ🇲ะะ🇦ะะ🇮ะ🇳ะ",
"ะ🇯ะะ🇭ะะ🇦ะะ🇦ะะ🇳ะะ🇹ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇮ꜱะꜱะ🇺ะ ะ🇹ะะ🇲ะะ🇰ะะ🇨ะ ะ🇸ะะ🇺ะะ🇳ะ",
"ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ ะ🇰ะะ🇦ะะ🇱ะะ🇮ะ ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ",
"ะ🇰ะะ🇭ะะ🇴ะะ🇹ะะ🇪ะ🇾ะ ะ🇰ะะ🇮ะ ะ🇦ะะ🇺ะะ🇱ะะ🇩ะะ🇦ะ ะ🇪ะะ🇾ะ ะ🇹ะะ🇺ะ ะ🇷ะะ🇦ะะ🇳ะะ🇩ะะ🇾ะะ🇰ะะ🇪ะ",
"ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇦ะ ะ🇦ะะ🇼ะะ🇱ะะ🇦ะะ🇹ะ ะ🇯ะะ🇦ะะ🇮ะꜱะะ🇦ะ ะ🇱ะะ🇬ะ ะ🇷ะะ🇭ะะ🇦ะ ะ🇹ะะ🇺ะ",
"ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇮ะ ะ🇯ะะ🇦ะะ🇹ะ ะ🇯ะะ🇦ะะ🇮ꜱะะ🇦ะ ะ🇪ะะ🇾ะ ะ🇹ะะ🇺ะ ",
"ะ🇰ะะ🇺ะะ🇹ะะ🇹ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇹ะะ🇦ะะ🇹ะะ🇹ะะ🇦ะ ะ🇪ะะ🇾ะ ะ🇹ะะ🇺ะ",
"ะ🇹ะะ🇪ะะ🇹ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇰ะะ🇮ะ.ะ🇨ะะ🇭ะะ🇺ะะ🇹ะ , ะ🇹ะะ🇪ะะ🇷ะะ🇮ะ ะ🇲ะะ🇦ะ ะ🇷ะะ🇳ะะ🇩ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะะ🇮ะ",
"ะ🇱ะะ🇦ะะ🇻ะะ🇩ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇱ะ ะ🇵ะะ🇰ะะ🇩ะ ะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ",
"ะ🇲ะะ🇺ะะ🇭ะ ะ🇲ะะ🇪ะะ🇮ะ ะ🇱ะะ🇪ะะ🇱ะะ🇪ะ ะ🇲ะะ🇪ะะ🇷ะะ🇦ะ ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ",
"ะ🇱ะะ🇺ะะ🇳ะะ🇩ะ ะ🇰ะะ🇪ะ ะ🇵ะะ🇦ꜱะะ🇮ะะ🇳ะะ🇪ะ ะ🇨ะะ🇭ะะ🇺ะะ🇵ะ ะ🇧ะะ🇪ะะ🇹ะะ🇭ะ ะ🇴ะ🇷ะ ะ🇨ะะ🇺ะะ🇩ะ",
"ะ🇲ะะ🇪ะะ🇷ะะ🇪ะ ะ🇱ะะ🇼ะะ🇩ะะ🇪ะ ะ🇰ะะ🇪ะ ะ🇧ะะ🇦ะะ🇦ะะ🇦ะะ🇦ะะ🇱ะะ🇱ะะ🇱ะ",
"ะ🇭​ะะ🇦​ะะ🇭​ะะ🇦​ะะ🇭​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇬​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇺​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇩​ะ ะ🇬​ะะ🇾​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇦​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇭​ะะ🇦​ะะ🇳​ะะ🇪​ะ ะ🇰​ะะ🇮​ะ ะ🇺​ะะ🇱​ะะ🇦​ะะ🇩​ะะ🇩​ะะ🇩​ะ",
"ꜱ​ะ🇦​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇺​ะะ🇮​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇦​ะะ🇮​ะ🇳​ะ ะ🇰​ะะ🇺​ะะ🇹​ะะ🇪​ะ ะ🇰​ะะ🇦​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇪​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇪​ะะ🇮​ะ🇳​ะ ะ🇰​ะะ🇪​ะะ🇪​ะะ🇩​ะะ🇪​ะ ะ🇵​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇾​ะ",
"ะ🇳​ะะ🇾​ะ ะ🇳​ะะ🇾​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ",
"ꜱ​ะ🇺​ะะ🇳​ะะ🇳​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇪​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ ะ🇹​ะะ🇲​ะะ🇱​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะ",
"ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะ🇳​ะ ะ🇰​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะะ🇨​ะะ🇭​ะะ🇦​ะะ🇵​ะ ะ🇨​ะะ🇺​ะะ🇩​ะ ะ🇾​ะะ🇭​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇹​ะะ🇳​ะะ🇮​ะะ🇮​ะะ🇮​ะ",
"ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇱​ะะ🇦​ะะ🇼​ะะ🇩​ะะ🇦​ะ ะ🇱​ะะ🇪​ะะ🇱​ะะ🇪​ะ ะ🇹​ะะ🇺​ะ ะ🇦​ะะ🇬​ะะ🇦​ะ🇷​ะ ะ🇨​ะะ🇭​ะะ🇦​ะะ🇮​ะะ🇾​ะะ🇪​ะ ะ🇹​ะะ🇴​ะะ🇭​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ🇺​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇮​ะะ🇾​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇵​ะะ🇪​ะ ะ🇯​ะ🇨​ะ🇧​ะ ะ🇨​ะะ🇭​ะะ🇦​ะะ🇩​ะะ🇭​ะะ🇦​ะะ🇦​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ꜱ​ะ🇦​ะะ🇲​ะะ🇯​ะะ🇭​ะะ🇦​ะะ🇦​ะ ะ🇱​ะะ🇦​ะะ🇼​ะะ🇩​ะะ🇪​ะ",
"ะ🇾​ะะ🇦​ะ ะ🇩​ะะ🇺​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇬​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇪​ะ ะ🇹​ะะ🇦​ะะ🇵​ะะ🇦​ะะ🇦​ะ ะ🇹​ะะ🇦​ะะ🇵​",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะ🇳​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇷​ะะ🇴​ะะ🇿​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇪​ะ ꜱ​ะะ🇦​ะะ🇦​ะะ🇹​ะะ🇭​ะ ะ🇲​ะ🇲​ꜱ​ะ ะ🇧​ะะ🇦​ะะ🇳​ะะ🇦​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇰​ะะ🇦​ะ ะ🇭​ะะ🇺​",
"ะ🇹​ะะ🇺​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇮​ะะ🇾​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇰​ะะ🇭​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇦​ะะ🇦​ะ🇳​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇮​ะะ🇾​ะะ🇦​ะ",
"ะ🇦​ะะ🇺​ะ🇷​ะ ะ🇰​ะะ🇮​ะะ🇹​ะะ🇳​ะะ🇦​ะ ะ🇧​ะะ🇴​ะะ🇱​ะะ🇺​ะ ะ🇧​ะะ🇪​ะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇳​ะะ🇳​ะ ะ🇧​ะะ🇭​ะะ🇦​ะ🇷​ะ ะ🇬​ะะ🇦​ะะ🇾​ะะ🇦​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะะ🇹​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇦​ะะ🇧​ะ🇨​ะ🇩​ะ ะ🇱​ะะ🇮​ะะ🇰​ะะ🇭​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇪​ะ ะ🇱​ะะ🇴​ะะ🇩​ะะ🇪​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ะ ะ🇱​ะะ🇪​ะะ🇰​ะะ🇦​ะ🇷​ะ ะ🇲​ะะ🇦​ะะ🇮​ะ ꜰ​ะะ🇦​ะ🇷​ะะ🇦​ะ🇷​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇮​ะะ🇩​ะะ🇮​ะะ🇮​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇧​ะะ🇦​ะะ🇨​ะะ🇭​ะะ🇪​ะะ🇪​ะ ะ🇹​ะะ🇲​ะะ🇰​ะะ🇨​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ ะ🇲​ะะ🇦​ะะ??​ะ🇴​ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇺​ะ",
"ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇾​ะ",
"ะ🇹​ะะ🇺​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇵​ะะ🇮​ะะ🇱​ะะ🇱​ะะ🇦​ะ ะ🇪​ะะ🇾​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ะ ะ🇧​ะะ🇭​ะะ🇪​ะะ🇯​ะะ🇯​ะะ🇯​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇦​ะะ🇦​ะะ🇦​ะะ🇵​ะ ะ🇭​ะะ🇺​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇭​ะะ🇦​ะะ🇦​ะะ🇹​ะ ะ🇩​ะะ🇦​ะะ🇦​ะะ🇱​ะะ🇱​ะะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇭​ะะ🇦​ะะ🇦​ะ🇬​ะ ะ🇯​ะะ🇦​ะะ🇦​ะะ🇳​ะะ🇺​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ะ ꜱ​ะะ🇦​ะ🇷​ะะ🇦​ะะ🇰​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇦​ะะ🇦​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ะ🇬​ะ🇧​ะ ะ🇷​ะ🇴​ะ🇦​ะ🇩​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇯​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇪​ะ🇨​ะ🇭​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​É​ะ ะ🇰​ะะ🇦​ะะ🇦​ะะ🇱​ะะ🇮​ะ ะ🇲​ะะ🇮​ะะ🇹​ะ🇨​ะ🇭​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ꜱ​ะะ🇦​ꜱ​ะะ🇹​ะะ🇮​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇰​ะะ🇦​ะะ🇧​ะะ🇺​ะะ🇹​ะะ🇦​ะ🇷​ะ ะ??​ะะ🇦​ะะ🇦​ะะ🇱​ะ ะ🇰​ะะ🇪​ะ ꜱ​ะ🇴​ะะ🇺​ะะ🇵​ะ ะ🇧​ะะ🇦​ะะ🇳​ะะ🇦​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇩​ะะ🇪​ะะ🇹​ะ🇴​ะ🇱​ะ ะ🇩​ะะ??​ะะ🇦​ะะ🇱​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇱​ะะ🇦​ะะ🇵​ะะ🇹​ะ🇴​ะ🇵​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇭​ะะ🇦​ะะ🇮​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ะ🇧​ะะ🇮​ꜱ​ะะ🇹​ะะ🇦​ะ🇷​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇦​ะะ🇦​ะะ🇰​ะะ🇪​ะ ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ??​ะะ🇴​ ะ🇦​ะะ🇲​ะะ🇪​ะ🇷​ะะ🇮​ะ🇨​ะะ🇦​ะ ะ🇬​ะะ🇭​ะะ🇺​ะะ🇲​ะะ🇦​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇲​ะะ🇪​ะ ะ🇳​ะะ🇦​ะะ🇦​ะ🇷​ะะ🇮​ะะ🇾​ะะ🇦​ะ🇱​ะ ะ🇵​ะะ🇭​ะ🇴​ะ🇷​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇪​ะ ะ🇬​ะะ🇦​ะะ🇳​ะะ🇩​ะ ะ🇲​ะะ🇪​ะ ะ🇩​ะะ🇪​ะะ🇹​ะ🇴​ะ🇱​ะ ะ🇩​ะะ🇦​ะะ🇦​ะะ🇱​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ะ🇭​ะ🇴​🇷​🇱​🇮​🇨​🇰​ꜱ​ะ ะ🇵​ะะ🇮​ะะ🇱​ะะ🇦​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇴​ ꜱ​ะะ🇦​ะ🇷​ะะ🇦​ะะ🇰​ะ ะ🇵​ะะ🇪​ะ ะ🇱​ะะ🇪​ะะ🇹​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇩​ะะ🇺​ะะ🇳​ะะ🇬​ะะ🇦​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะ",
"ะ🇲​ะะ🇪​ะะ🇷​ะะ🇦​ะะ🇦​ะ ะ🇱​ะะ🇺​ะะ🇳​ะะ🇩​ะ ะ🇵​ะะ🇦​ะะ🇰​ะะ🇦​ะะ🇩​ะ ะ🇱​ะะ🇪​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇦​ะะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ะะ🇴​ꜱ​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇨​ะะ🇭​ะะ🇺​ꜱ​ะ ะ🇬​ะะ🇪​ะะ🇾​ะะ🇮​ะ ะ🇰​ะะ🇾​ะะ🇦​ะะ🇦​ะ ะ🇱​ะะ🇦​ะะ🇼​ะะ🇩​ะะ🇪​ะะ🇪​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇯​ꜱ​ะะ🇴​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะ🇽​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇩​ะะ🇩​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇺​ะะ🇺​ะ🇮​ะ ะ🇲​ะะ🇦​ะะ🇦​ะะ🇦​ะ ะ🇰​ะะ🇦​ะะ🇦​ะ ะ🇧​ะะ🇭​ꜱ​ะะ🇴​ะะ🇩​ะะ🇦​ะะ🇦​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะะ🇮​ะ ะ🇧​ะะ🇪​ะะ🇭​ะะ🇪​ะ🇳​ะะ🇳​ะะ🇳​ะ ะ🇰​ะะ🇴​ะ ะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇩​ะะ🇩​ะะ🇺​ะะ🇺​ะะ🇺​ะะ🇺​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะ🇽​ะะ🇭​ะะ🇴​ะะ🇩​ะะ🇩​ะะ🇩​ะะ🇩​ะ",
"ะ🇹​ะะ🇺​ะ ะ🇳​ะะ🇮​ะะ🇰​ะะ🇦​ะะ🇱​ะ ะ🇲​ะะ🇦​ะะ🇩​ะะ🇦​ะ🇷​ะะ🇨​ะะ🇭​ะะ🇴​ะะ🇩​ะ",
"ะ🇨​ะะ🇭​ะะ🇺​ะะ🇵​ะ ะ🇷​ะะ🇦​ะะ🇳​ะะ🇩​ะะ🇮​ะ ะ🇰​ะะ🇪​ะ ะ🇧​ะะ🇦​ะะ🇨​ะะ🇭​ะะ🇪​ะ",
"ะ??​ะะ🇪​ะะ🇷​ะะ🇦​ะ ะ🇲​ะะ🇦​ะะ🇦​ะ ะ🇲​ะะ🇪​ะะ🇷​ะะ🇮​ะ ะ🇯​ะะ🇦​ะะ🇦​ะ🇳​ะ ะ🇪​ะะ🇾​ะ",
"ะ🇹​ะะ🇪​ะะ🇷​ะะ🇮​ะ ꜱ​ะ🇪​x​ะ🇾​ะ ะ🇧​ะะ🇦​ะะ🇭​ะะ🇪​ะ🇳​ะ ะ🇰​ะะ🇮​ะ ะ🇨​ะะ🇭​ะะ🇺​ะะ🇹​ะ ะ🇴​ะะ🇵​ะ",
"⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇧⚡🇭⚡?? ⚡🇧⚡🇳⚡🇦⚡🇱⚡🇪 ⚡🇲⚡🇺⚡🇯⚡🇪 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇰⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇪⚡🇾 ⚡🇾⚡🇦⚡🇦⚡🇩 ⚡🇪⚡🇾 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇦 ⚡🇳⚡🇦 ⚡🇹⚡🇾⚡🇲⚡🇵⚡🇦⚡🇸⚡🇸",
"⚡🇴⚡🇾⚡🇪 ⚡🇺⚡🇳⚡🇫⚡🇺⚡🇳⚡🇳⚡🇾 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇲⚡🇹⚡🇹 ⚡🇰⚡🇷",
"⚡🇴⚡🇭 ⚡🇭⚡🇪⚡🇱⚡🇱⚡🇴 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇹⚡🇪⚡??⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇴⚡🇷 ⚡🇹⚡🇺 ⚡🇻 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇦⚡🇺⚡🇰⚡🇦⚡🇹 ⚡🇲⚡🇪 ⚡🇷⚡🇭⚡🇦 ⚡🇰⚡🇷.",
"⚡🇴⚡🇾⚡🇾 ⚡🇰⚡🇮⚡🇳⚡🇳⚡🇪⚡🇷 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇬⚡🇨 ⚡🇲⚡🇪 ⚡🇦⚡🇦⚡🇳⚡🇪 ⚡🇰⚡🇮 ⚡🇵⚡🇪⚡🇷⚡🇲⚡🇮⚡🇸⚡🇸⚡🇮⚡🇴⚡🇳 ⚡🇰⚡🇮⚡🇸⚡🇳⚡🇪 ⚡🇩⚡🇮.",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇪⚡🇰 ⚡🇧⚡🇦⚡🇦⚡🇷.",
"⚡🇸⚡🇺⚡🇳 ⚡🇸⚡🇺⚡🇳 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇦.",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇨⚡🇦 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇦.",
"⚡🇴⚡🇾⚡🇪 ⚡🇨⚡🇭⚡🇴⚡🇹⚡🇮 ⚡🇯⚡🇦⚡🇹⚡🇮 ⚡🇰⚡🇪 ⚡🇹⚡🇲⚡🇷.",
"⚡🇰⚡🇾? ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇰⚡🇮⚡🇩⚡🇩⚡🇪.",
"⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇨⚡🇴⚡🇲 ⚡🇬⚡🇦⚡🇳⚡🇬 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇰⚡🇴 ⚡🇹⚡🇦⚡🇬 ⚡🇨⚡🇷⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇺",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇧⚡🇸",
"⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇸⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇵⚡🇦⚡🇵⚡🇦 ⚡🇧⚡🇴⚡🇱",
"⚡🇸⚡🇮⚡🇩⚡🇪 ⚡🇭⚡🇴⚡🇯⚡🇦 ⚡🇧⚡🇮⚡🇭⚡🇦⚡🇷⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇦⚡🇧",
"⚡🇭⚡🇾⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇧⚡🇭⚡🇬 ⚡🇲⚡🇦⚡🇹 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩",
"⚡🇧⚡🇭⚡🇬 ⚡🇳⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇹⚡🇺 ⚡🇦⚡🇯⚡🇯",
"⚡🇭⚡🇾⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇰⚡🇪 ⚡🇧⚡🇨⚡🇭⚡🇪 ⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇲⚡🇦⚡🇹",
"⚡🇭⚡🇾⚡🇪 ⚡🇩⚡🇺⚡🇷 ⚡🇭⚡🇦⚡🇹⚡🇹 ⚡🇲⚡🇦⚡🇩⚡🇭⚡🇦⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇰⚡🇴⚡🇮 ⚡🇧⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾 ⚡🇪⚡🇸⚡🇱⚡🇮⚡🇾⚡🇪 ⚡🇲⚡🇦⚡🇫 ⚡🇨⚡🇷 ⚡🇷⚡🇭⚡🇦 ⚡🇭⚡🇺 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇰⚡🇴⚡🇮 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺 ⚡🇲⚡🇦⚡🇫⚡🇮 ⚡🇩⚡🇪 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺 ⚡🇲⚡🇦⚡🇫⚡🇮 ⚡🇲⚡🇮⚡🇱 ⚡🇯⚡🇦⚡🇾⚡🇪⚡🇬⚡🇮 ⚡🇹⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇲⚡🇦⚡🇹 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇦 ⚡🇲⚡🇺⚡🇯⚡🇪 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇨⚡🇷⚡🇰⚡🇪",
"⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇨⚡🇷⚡🇰⚡🇪",
"⚡🇫⚡🇷 ⚡🇧⚡🇴⚡🇱⚡🇳⚡🇦 ⚡🇳⚡🇦 ⚡🇰⚡🇮 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇸⚡🇼⚡🇮⚡🇵⚡🇪 ⚡🇨⚡🇷⚡🇰⚡🇪",
"⚡🇨⚡🇾⚡🇦 ⚡🇭⚡🇺⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷 ⚡🇰⚡🇪⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇭⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇾 ⚡🇳⚡🇾 ⚡🇲⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾",
"⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇸⚡🇪 ⚡🇺⚡🇹⚡🇷 ⚡🇲⚡🇨",
"⚡🇱⚡🇺⚡🇳 ⚡🇲⚡🇹 ⚡🇨⚡🇭⚡🇺⚡🇸 ⚡🇲⚡🇪⚡🇷⚡🇦",
"⚡🇳⚡🇮⚡🇰⚡🇦⚡🇱 ⚡🇲⚡🇦⚡🇩⚡🇦⚡🇷⚡🇨⚡🇭⚡🇩",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇴⚡🇾⚡🇪 ⚡🇬⚡🇦⚡🇸⚡🇭⚡🇹⚡🇮 ⚡🇰 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇲⚡🇦⚡🇰⚡🇮⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇮",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇮",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇰 ⚡🇭⚡🇦⚡🇹⚡🇭 ⚡🇹⚡🇴⚡🇩⚡🇭 ⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇪 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇰 ⚡🇲⚡🇺⚡🇭 ⚡🇲⚡🇪 ⚡🇫⚡🇦⚡🇸⚡🇦⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇹⚡🇺 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇵⚡🇦⚡🇸⚡🇦⚡🇳⚡🇩 ⚡🇳⚡🇦⚡🇮 ⚡🇦⚡🇾⚡🇦 ⚡🇲⚡🇪⚡🇰⚡🇴",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇮⚡🇩⚡🇪⚡🇷 ⚡🇸⚡🇪",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇸⚡🇪 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇳⚡🇾 ⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇧⚡🇦⚡🇹 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪",
"⚡🇫⚡🇦⚡🇸⚡🇹 ⚡🇱⚡🇪⚡🇦⚡🇻⚡🇪 ⚡🇱⚡🇪 ⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇹⚡🇺⚡🇹⚡🇴 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰",
"⚡🇴⚡🇾 ⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪 ⚡🇰⚡🇭⚡??⚡🇳⚡🇦 ⚡🇰⚡🇭⚡🇦 ⚡🇰⚡🇪 ⚡🇦⚡🇦 ⚡🇰⚡🇦⚡🇲⚡🇿⚡🇴⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇮⚡🇱⚡🇾 ⚡🇷⚡🇪⚡🇾 🌚😂",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇦⚡🇵 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺",
"⚡🇸⚡🇭⚡🇮 ⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡??⚡🇺 ⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵",
"⚡🇫⚡🇷 ⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵",
"⚡🇸⚡🇭⚡🇮 ⚡🇸⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡??⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇦 ⚡🇨⚡🇾⚡🇺 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇵⚡🇨⚡🇭⚡🇦⚡🇵",
"⚡🇵⚡🇷⚡🇴⚡🇴⚡🇫 ⚡🇨⚡🇷 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷⚡🇴⚡🇴⚡🇫 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇵⚡🇷⚡🇴⚡🇴⚡🇫 ⚡🇭⚡🇴 ⚡🇨⚡🇭⚡🇺⚡🇰⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇮⚡🇱⚡🇱⚡🇦⚡🇷",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇲⚡🇦⚡🇦 ⚡🇰 ⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇴⚡🇾 ⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪 ⚡🇰⚡🇭⚡🇦⚡🇳⚡🇦 ⚡🇰⚡🇭⚡🇦 ⚡🇰⚡🇪 ⚡🇦⚡🇦 ⚡🇰⚡🇦⚡🇲⚡🇿⚡🇴⚡🇷",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇲⚡🇦⚡🇩⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩 ?",
"⚡🇦⚡🇧 ⚡🇹⚡🇰 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇭⚡🇴⚡🇬⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ?",
"⚡🇳⚡🇾 ⚡🇳⚡🇾 ⚡🇲⚡🇪 ⚡🇰⚡🇺⚡🇨⚡🇭 ⚡🇳⚡🇾 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇧⚡🇸 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇸⚡🇧⚡🇸⚡🇪 ⚡🇵⚡🇭⚡🇪⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴 ⚡🇧⚡🇴⚡🇱 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇳⚡🇦 ⚡🇰⚡🇦⚡🇲 ⚡🇰⚡🇷⚡🇪",
"⚡🇾⚡🇦⚡🇭⚡🇦 ⚡🇧⚡🇭⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇦 ⚡🇹⚡🇺 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇨⚡🇪 ⚡🇵⚡🇮⚡🇱⚡🇱⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇮⚡🇲⚡🇦⚡🇰⚡🇦⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇹⚡🇴 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇨⚡🇺⚡🇩⚡🇪⚡🇬⚡🇮",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇹⚡🇴⚡🇲⚡🇲⚡🇾",
"⚡🇳⚡🇮⚡🇰⚡🇦⚡🇱 ⚡🇲⚡🇦⚡🇩⚡🇦⚡🇷⚡🇨⚡🇭⚡🇩 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇾⚡🇭⚡🇦 ⚡🇸⚡🇪",
"⚡🇨⚡🇴⚡🇿 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇦⚡🇳⚡🇩⚡🇭⚡🇮 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇭⚡🇪",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪",
"⚡🇳⚡🇾⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇭⚡🇴⚡🇬⚡🇮 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇯⚡🇴 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦⚡🇹⚡🇮 ⚡🇯⚡🇴⚡🇬⚡🇮",
"⚡🇹⚡🇷⚡🇾 ⚡🇦⚡🇲⚡🇲⚡🇮 ⚡🇨⚡🇪 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇪 ⚡🇲⚡🇪 ⚡🇪⚡🇲⚡🇴⚡🇯⚡🇮 ⚡🇩⚡🇦⚡🇱 ⚡🇲⚡🇨",
"⚡🇨⚡🇾⚡🇦 ? ⚡🇨⚡🇭⚡🇲⚡🇷 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇦 ⚡🇨⚡🇾⚡🇦 ?",
"⚡🇹⚡🇲 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇷⚡🇮 ⚡🇭⚡🇴⚡🇬⚡🇮 ⚡🇫⚡🇷⚡🇷⚡🇹⚡🇴",
"⚡🇨⚡🇾⚡🇦 ? ⚡🇰⚡🇧 ? ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇰⚡🇪⚡🇰",
"⚡🇨⚡🇾⚡🇦 ⚡🇸⚡🇨⚡🇭 ⚡🇲⚡🇪⚡🇾 ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇼⚡?? ⚡🇱⚡🇮 ⚡🇹⚡🇺⚡🇳⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦",
"⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇸⚡🇨⚡🇭 ⚡🇳⚡🇾 ⚡🇧⚡🇴⚡🇱 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇨⚡🇭 ⚡🇲⚡🇪⚡🇾 ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇮⚡🇦 ⚡🇲⚡🇪⚡🇷⚡🇪 ⚡🇸⚡🇹⚡🇭",
"⚡🇲⚡🇹⚡🇱⚡🇧 ⚡🇹⚡🇲⚡🇷",
"⚡🇳⚡🇾⚡🇹⚡🇴",
"⚡🇵⚡🇺⚡🇷⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇲⚡🇨",
"⚡🇹⚡🇲⚡🇷 ⚡🇫⚡🇷⚡🇷⚡🇹⚡🇴",
"⚡🇴⚡🇭 ⚡🇴⚡🇰 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇫⚡🇮⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇦 ⚡🇩⚡🇦⚡🇲⚡🇦⚡🇩",
"⚡🇨⚡🇾⚡🇦 ? ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭⚡🇪 ⚡🇵⚡🇪⚡🇭⚡🇱⚡🇪 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇰⚡🇪⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇳⚡🇪 ⚡🇲⚡🇪 ⚡🇻⚡🇾⚡🇦⚡🇸⚡🇹 ⚡🇭⚡🇺",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇰⚡🇺⚡🇨⚡🇭 ⚡🇧⚡🇮",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇨⚡🇾⚡🇦 ? ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇦 ?",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇲⚡🇹 ⚡🇭⚡🇸⚡🇸",
"⚡🇾⚡🇺⚡🇷 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇲⚡🇴⚡🇲",
"⚡🇦⚡🇷⚡🇪 ⚡🇸⚡🇧⚡🇰⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇴⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇧⚡🇮",
"⚡🇦⚡🇷⚡🇪 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇪⚡🇰 ⚡🇧⚡🇦⚡🇦⚡🇷",
"⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇮 ⚡🇹⚡🇷⚡🇭",
"⚡🇪⚡🇰 ⚡🇱⚡🇮⚡🇳⚡🇪 ⚡🇲⚡🇪 ⚡🇹⚡🇲⚡🇷",
"⚡🇶",
"⚡🇴⚡🇨⚡🇾 ⚡🇦⚡🇧 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇱⚡🇪",
"⚡🇵⚡🇪⚡🇭⚡🇪⚡🇱⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇳⚡🇾⚡🇹⚡🇴",
"⚡?? ?",
"⚡🇭⚡🇾⚡🇾⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇦 ⚡🇪⚡🇰 ⚡🇧⚡🇦⚡🇦⚡🇷",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇸⚡🇺⚡🇳 ⚡🇩⚡🇴⚡🇸⚡🇹 ⚡🇹⚡🇲⚡🇷",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇯⚡🇦 ⚡🇷⚡🇦⚡🇦⚡🇳⚡🇩 ⚡🇲⚡🇦⚡🇦⚡🇫 ⚡🇨⚡🇷⚡🇷 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦",
"⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇲⚡🇷 ⚡🇫⚡🇷⚡🇷⚡🇹⚡🇴",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇱⚡🇪 ⚡🇨⚡🇭⚡🇲⚡🇷",
"⚡🇳⚡🇾⚡🇹⚡🇴 ⚡🇦⚡🇪⚡🇸⚡🇪 ⚡🇭⚡🇮 ⚡🇨⚡🇺⚡🇩",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇭⚡🇾⚡🇾 ⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇭⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇱⚡🇪⚡🇳⚡🇦",
"⚡🇴⚡🇷 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇱⚡🇪",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇦 ⚡🇴⚡🇷",
"⚡🇭⚡🇾⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇴 ⚡🇳⚡🇦",
"⚡🇨⚡🇭⚡🇺⚡🇩⚡🇴 ⚡🇲⚡🇹 ⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇯⚡🇦⚡🇴",
"⚡🇧⚡🇾⚡🇾⚡🇪⚡🇪 ⚡🇭⚡🇾⚡🇾 ⚡🇨⚡🇾⚡🇦 ?",
"⚡🇶⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇶 ⚡🇷⚡🇭⚡🇪 ⚡🇭⚡🇴 ?",
"⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇲⚡🇨",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇲⚡🇹",
"⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇬⚡🇱 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇦⚡🇲⚡🇲⚡🇮 ⚡🇨⚡🇪 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇪 ⚡🇲⚡🇪 ⚡🇨⚡🇭⚡🇦⚡🇵⚡🇵⚡🇦⚡🇱",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦 ⚡🇲⚡🇨",
"⚡🇰⚡🇲⚡🇿⚡🇷⚡🇴⚡🇷 ⚡🇪⚡🇾 ⚡🇨⚡??⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇪⚡🇰",
"⚡🇨⚡🇾⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇭⚡🇦 ?",
"⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇹⚡🇭⚡🇦 ⚡🇨⚡🇾⚡🇦 ?",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇸⚡🇱⚡🇮⚡🇩⚡🇪 ⚡🇱⚡🇪⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇨⚡🇷⚡🇲⚡🇨",
"⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇨⚡🇵 ⚡🇲⚡🇹 ⚡🇨⚡🇷⚡🇷 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇱⚡🇪",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇭⚡🇾⚡🇾 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇦",
"⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇸⚡🇨⚡🇭⚡🇴⚡🇫⚡🇺 ⚡🇰⚡🇭⚡🇦⚡🇨⚡🇭⚡🇦⚡🇷 ⚡🇰⚡🇭⚡🇦⚡🇨⚡🇭⚡🇦⚡🇷",
"⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦 ⚡🇯⚡🇦 ⚡🇲⚡🇨",
"⚡🇭⚡🇾⚡🇾 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇱⚡🇪",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇰⚡🇲⚡🇿⚡🇴⚡🇷 ⚡🇲⚡🇨 ⚡🇮⚡🇩⚡🇦⚡🇷 ⚡🇦⚡🇦",
"⚡🇾⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇹⚡🇲⚡🇷",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇳⚡🇾 ⚡🇨⚡🇵 ⚡🇳⚡🇾 ⚡🇨⚡🇷⚡🇷",
"⚡🇴⚡🇾⚡🇪⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇲⚡🇹 ⚡🇨⚡🇷⚡🇷",
"⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇦⚡🇷⚡🇦⚡🇲 ⚡🇸⚡🇪 ⚡🇲⚡🇨",
"⚡🇵⚡🇬⚡🇱 ⚡🇪⚡🇾 ⚡🇨⚡🇾⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮⚡🇪⚡🇰",
"⚡🇨⚡🇵 ⚡🇨⚡🇷⚡🇨⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇪⚡🇬⚡🇦 !",
"⚡🇧⚡🇦⚡🇦⚡🇵 ? ⚡🇲⚡🇨 ⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇨⚡🇴⚡🇮 ⚡🇲⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇳⚡🇾 ⚡🇪⚡🇾 ⚡🇲⚡🇦⚡🇮 ⚡🇺⚡🇵⚡🇦⚡🇷 ⚡🇸⚡🇪 ⚡🇷⚡🇴⚡🇨⚡🇰⚡🇪⚡🇹 ⚡🇵⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇭 ⚡🇨⚡🇪 ⚡🇧⚡🇸⚡🇸 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇳⚡🇪 ⚡🇦⚡🇾⚡🇦 ⚡🇭⚡🇺",
"⚡🇨⚡🇭⚡🇴⚡🇹⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇰 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪",
"⚡🇨⚡🇭⚡🇴⚡🇹⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇾",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇧⚡🇦⚡🇰⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇪⚡🇬⚡🇦",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇲⚡🇦⚡🇮⚡🇳 ⚡🇧⚡🇺⚡🇷⚡🇫",
"⚡🇧⚡🇭⚡🇮⚡🇰⚡🇦⚡🇷⚡🇮 ⚡🇰⚡🇮 ⚡🇯⚡🇭⚡🇦⚡🇹 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇦 ⚡🇱⚡🇪",
"⚡🇨⚡🇭⚡🇴⚡🇩⚡🇰⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇲⚡🇦⚡🇷⚡🇯⚡🇦⚡🇾⚡🇪⚡🇬⚡🇮",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇲⚡🇦⚡🇮⚡🇳 ⚡🇲⚡🇴⚡🇺⚡🇳⚡🇹 ⚡🇪⚡🇻⚡🇪⚡🇷⚡🇪⚡🇸⚡🇹",
"⚡🇲⚡🇺⚡🇭 ⚡🇲⚡🇪⚡🇾 ⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇲⚡🇪⚡🇷⚡🇦",
"⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪 ⚡🇰⚡🇮 ⚡🇯⚡🇭⚡🇦⚡🇹 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇳⚡🇾 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇰⚡🇮 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇸⚡🇧 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇹⚡🇦",
"⚡🇹⚡🇪⚡🇳⚡🇺 ⚡🇴⚡🇷 ⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇵⚡🇹⚡🇦 ⚡🇪⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇧⚡🇸 ⚡🇧⚡🇸 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇧⚡🇸 ⚡🇧⚡🇸 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇹⚡🇭⚡🇳⚡🇰⚡🇸⚡🇸",
"⚡🇧⚡🇸 ⚡??⚡🇸 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇮⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇦",
"⚡🇧⚡🇸 ⚡🇧⚡🇸 ⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇬⚡🇾⚡🇦 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇧",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇸⚡🇦⚡🇧⚡🇮⚡🇹 ⚡🇰⚡🇷 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇾⚡🇦 ⚡🇭⚡🇺⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇪⚡🇦⚡🇸⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇹⚡🇺",
"⚡🇪⚡🇦⚡🇸⚡🇾 ⚡🇼8 ⚡🇲⚡?? ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇦⚡🇧",
"⚡🇸⚡🇦⚡🇳⚡🇸 ⚡🇦⚡🇷⚡🇮 ⚡🇭⚡🇦 ⚡🇰⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇬⚡🇮 ⚡🇦⚡🇯⚡🇯",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴 ⚡🇧⚡🇮⚡🇳⚡🇦 ⚡🇸⚡🇦⚡🇳⚡🇸⚡🇸 ⚡🇱⚡🇪⚡🇹⚡🇪 ⚡🇭⚡🇺⚡🇪 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇰⚡🇪 ⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷",
"⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦 ⚡🇳⚡🇴⚡🇷⚡🇲⚡🇮⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇫⚡🇷 ⚡🇨⚡🇾⚡🇦 ⚡🇳⚡🇴⚡🇷⚡🇲⚡🇮⚡🇪 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇧⚡🇦⚡🇸 ⚡🇹⚡🇭⚡🇪⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾",
"⚡🇧⚡🇦⚡🇸 ⚡🇹⚡🇭⚡🇪⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮",
"⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇹⚡🇭⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇪⚡🇸⚡🇱⚡🇮⚡🇾⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇲⚡🇦⚡🇮 ⚡🇸⚡🇧 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇭⚡🇱 ⚡🇨⚡🇭⚡🇱 ⚡🇭⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮",
"⚡🇫⚡🇷 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇧⚡🇦⚡🇸 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇫⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇲⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇪⚡🇾",
"⚡🇰⚡🇦⚡🇲⚡🇯⚡🇴⚡🇷 ⚡🇲⚡🇦 ⚡🇰⚡🇦 ⚡🇧⚡🇨⚡🇭⚡🇦 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇧⚡🇭⚡🇴⚡🇹 ⚡🇬⚡🇳⚡🇩⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇬⚡🇳⚡🇩⚡🇦",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇧⚡🇹⚡🇦 ⚡🇷⚡🇭⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇫⚡🇮⚡🇷 ⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇳⚡🇾 ⚡🇵⚡🇹⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇹⚡🇦 ⚡🇳⚡🇾 ⚡🇰⚡🇴⚡🇳 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴",
"⚡🇷⚡🇺⚡🇰 ⚡🇦⚡🇦⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇰⚡🇪",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇨⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇴⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇭⚡🇺",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇨⚡🇷 ⚡🇷⚡🇦⚡🇧⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇰⚡🇷 ⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇰⚡🇪",
"⚡🇼⚡🇦⚡🇮⚡🇹 ⚡🇱⚡🇪 ⚡🇹⚡🇭⚡🇴⚡🇩⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇳⚡🇪 ⚡🇩⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇷⚡🇺⚡🇰 ⚡🇯⚡🇦 ⚡🇦⚡🇦⚡🇳⚡🇩 ⚡🇷⚡🇰⚡🇭 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇮⚡🇾⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇫⚡🇦⚡🇲⚡🇴⚡🇺⚡🇸 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇲⚡🇦⚡🇦⚡🇳 ⚡🇱⚡🇮⚡🇦 ⚡🇲⚡🇪⚡🇳⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇸⚡🇦⚡🇱⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇦⚡🇦⚡🇳 ⚡🇱⚡🇮⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇸⚡🇭⚡🇦⚡🇳⚡🇹 ⚡🇧⚡🇪⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇸⚡🇭⚡🇦⚡🇳⚡🇹 ⚡🇧⚡🇪⚡🇹⚡🇭⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇹⚡🇺",
"⚡🇫⚡🇷 ⚡🇸⚡🇪 ⚡🇸⚡🇭⚡🇦⚡🇳⚡🇹 ⚡🇧⚡🇪⚡🇹⚡🇭 ⚡🇹⚡🇺 ⚡🇨⚡🇺⚡🇩 ⚡🇦⚡🇧 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇾⚡🇭⚡🇦",
"⚡🇲⚡🇪⚡🇷⚡🇪 ⚡🇸⚡🇲⚡🇯⚡🇭 ⚡🇳⚡🇾 ⚡🇦⚡🇾⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇱⚡🇪 ⚡🇰⚡🇪⚡🇱⚡🇦 ⚡🇰⚡🇭⚡🇦 ⚡🇹⚡🇺 ⚡🇲⚡🇦⚡🇩⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩",
"⚡🇭⚡🇾⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇮 ⚡🇨⚡🇾⚡🇦",
"⚡🇭⚡🇾⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇲⚡🇦⚡🇷 ⚡🇬⚡🇦⚡🇮 ⚡🇨⚡🇾⚡🇦",
"⚡🇭⚡🇾⚡🇪 ⚡🇸⚡🇨⚡🇭 ⚡🇧⚡🇹⚡🇦 ⚡🇨⚡🇴⚡🇲 ⚡🇨⚡??⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇨⚡🇭⚡🇱 ⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇴 ⚡🇸⚡🇲⚡🇯⚡🇭⚡🇱⚡🇪",
"⚡🇧⚡🇦⚡🇰⚡🇮 ⚡🇰⚡🇴⚡🇮 ⚡🇩⚡🇮⚡🇰⚡🇰⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇧⚡🇦⚡🇰⚡🇮 ⚡🇸⚡🇧 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇪 ⚡🇪⚡🇾 ⚡🇰⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇩⚡🇰⚡🇦⚡🇩 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇭⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇳⚡🇪 ⚡🇼⚡🇱⚡🇮 ⚡🇪⚡🇾",
"⚡🇵⚡🇷 ⚡🇲⚡🇪⚡🇮 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇯⚡🇳⚡🇹⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇰⚡🇴 ⚡🇰⚡🇴⚡🇮 ⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦",
"⚡🇵⚡🇷 ⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇻⚡🇮 ⚡🇲⚡🇦⚡🇳⚡🇳⚡🇦 ⚡🇸⚡🇭⚡🇮 ⚡🇹⚡🇭⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇵⚡🇷 ⚡🇼⚡🇴 ⚡🇬⚡🇱⚡🇹 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇵⚡🇷 ⚡🇼⚡🇴 ⚡🇸⚡🇭⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇩⚡🇰⚡🇦⚡🇩 ⚡🇪⚡🇾",
"⚡🇵⚡🇷 ⚡🇰⚡🇦⚡🇮⚡🇸⚡🇪 ⚡🇰⚡🇮⚡🇦 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇴⚡🇲⚡🇫⚡🇴⚡🇴",
"⚡🇧⚡🇺⚡🇷 ⚡🇨⚡🇭⚡🇪⚡🇪⚡🇷 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇰⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇱 ⚡🇲⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇦 ⚡🇲⚡🇦⚡🇷⚡🇰⚡🇪 ⚡🇺⚡🇸⚡🇰⚡🇮 ⚡🇩⚡🇭⚡🇦⚡🇩⚡🇰⚡🇦⚡🇳 ⚡🇷⚡🇴⚡🇰 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇱⚡🇺⚡🇱⚡🇱⚡🇪 ⚡🇰⚡🇭⚡🇦 ⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇦⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇦",
"⚡🇹⚡🇷⚡🇮 ⚡🇧⚡🇭⚡🇳 ⚡🇰⚡🇮 ⚡🇧⚡🇭⚡🇴⚡🇸⚡🇩⚡🇮 ⚡🇧⚡🇪⚡🇹⚡🇦",
"⚡🇹⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇰⚡🇭⚡🇹⚡🇲",
"⚡🇸⚡🇺⚡🇳 ⚡🇪⚡🇰 ⚡🇲⚡🇦⚡🇿⚡🇪 ⚡🇰⚡🇮 ⚡🇧⚡🇦⚡🇦⚡🇹 ⚡🇧⚡🇦⚡🇹⚡🇦⚡🇴 ⚡🇰⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇭⚡🇦⚡🇮",
"⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇦⚡🇯 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇴⚡🇾⚡🇪",
"⚡🇸⚡🇺⚡🇳 ⚡🇸⚡🇺⚡🇳 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇹⚡🇺",
"⚡🇰⚡🇮⚡🇱⚡🇦⚡🇸 ⚡🇳⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇾⚡🇦 ⚡🇵⚡🇹⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇵⚡?? ⚡🇵⚡🇷 ⚡🇨⚡🇾⚡🇦 ⚡🇭⚡🇴⚡🇹⚡🇪 ⚡🇪⚡🇾 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇹⚡🇲⚡🇨⚡🇱 ⚡🇸⚡🇺⚡🇳⚡🇱⚡🇪",
"⚡🇲⚡🇴⚡🇴⚡🇹 ⚡🇩⚡🇺 ⚡🇹⚡🇪⚡🇷⚡?? ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇲⚡🇪⚡🇾",
"⚡🇧⚡🇭⚡🇬⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇫⚡🇷",
"⚡🇫⚡🇷 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇾⚡🇪 ⚡🇻⚡🇮 ⚡🇸⚡🇭⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇰⚡🇸 ⚡🇧⚡🇸",
"⚡🇦⚡🇯 ⚡🇰⚡🇺⚡🇨⚡🇭 ⚡🇳⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇹⚡🇷⚡🇾 ⚡🇰⚡🇷 ⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇨⚡🇭⚡🇺⚡🇸⚡🇰⚡🇪",
"⚡🇹⚡🇴⚡🇷⚡🇲⚡🇦⚡🇰⚡🇮⚡🇧⚡🇺⚡🇷 ⚡🇸⚡🇺⚡🇳",
"⚡🇹⚡🇴⚡🇷 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇫⚡🇺⚡🇩⚡🇩⚡🇮 ⚡🇴⚡🇾⚡🇪",
"⚡🇭⚡🇦⚡🇾⚡🇪 ⚡🇭⚡🇦⚡🇾⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇴⚡🇾⚡🇪 ⚡🇱⚡🇺⚡🇳⚡🇩⚡🇰⚡🇪 ⚡🇵⚡🇦⚡🇸⚡🇮⚡🇳⚡🇪..",
"⚡🇰⚡🇺⚡🇹⚡🇹⚡🇪 ⚡🇰⚡🇪 ⚡🇹⚡🇦⚡🇹⚡🇹⚡🇪 ⚡🇸⚡🇺⚡🇳",
"⚡🇰⚡🇺⚡🇹⚡🇹⚡🇦 ⚡🇯⚡🇦⚡🇮⚡🇸⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺",
"⚡🇲⚡🇺⚡🇭 ⚡🇲⚡🇪⚡🇮 ⚡🇱⚡🇪 ⚡🇲⚡🇪⚡🇷⚡🇦..",
"⚡🇯⚡🇭⚡🇦⚡🇹 ⚡🇰⚡🇪 ⚡🇵⚡🇮⚡🇸⚡🇸⚡🇺 ⚡🇸⚡🇺⚡🇳 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇭⚡🇦⚡🇭⚡🇦⚡🇭⚡🇭⚡🇦 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇹⚡🇦⚡🇹⚡🇹⚡🇪 ⚡🇺⚡🇹⚡🇭",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺",
"⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇮 ⚡🇩⚡🇪⚡🇰⚡🇭",
"⚡🇼⚡🇪⚡🇪⚡🇰 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇦⚡🇧",
"⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇳⚡🇾 ⚡🇷⚡🇴⚡🇰 ⚡🇹⚡🇺 ⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇪⚡🇾",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇭⚡🇮⚡🇿⚡🇩⚡🇪",
"⚡🇴⚡🇰⚡🇦⚡🇹 ⚡🇳⚡🇾 ⚡🇲⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮",
"⚡🇱⚡🇺⚡🇳 ⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇬⚡🇦⚡🇳⚡🇩 ⚡🇲⚡🇪⚡🇮 ?",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇧⚡🇦⚡🇨⚡🇭⚡🇮 ⚡🇨⚡🇴⚡🇩⚡🇺..",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇦⚡🇯 ⚡🇫⚡🇦⚡🇩 ⚡🇩⚡🇺",
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇱⚡🇪⚡🇰⚡🇷 ⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇳⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇪 ⚡🇦⚡🇳⚡🇩⚡🇷 ⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇵⚡🇷⚡🇴⚡🇸⚡🇳",
"⚡🇺⚡🇬⚡🇱⚡🇾 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇺⚡🇵",
"⚡🇲⚡🇦⚡🇰⚡🇦⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇹⚡🇪⚡🇷⚡🇦 ⚡🇧⚡🇦⚡🇦⚡🇵 ⚡🇰⚡🇴 ⚡🇹⚡🇦⚡🇬 ⚡🇰⚡🇷..?",
"⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇹⚡🇦⚡🇬 ⚡🇰⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇭⚡🇦⚡🇬⚡🇼⚡🇳 ⚡🇰⚡🇴..",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇳⚡🇾 ⚡🇭⚡🇴 ⚡🇹⚡🇺",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇭⚡🇴 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺 ⚡🇰⚡🇮⚡🇩",
"⚡🇲⚡🇦 ⚡🇹⚡🇴 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇭⚡🇦⚡🇼⚡🇦⚡🇧⚡🇿⚡🇮 ⚡🇨⚡🇷..",
"⚡🇧⚡🇸 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇳⚡🇮 ⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇹⚡🇴⚡🇼⚡🇳 ⚡🇲⚡🇪⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇱⚡🇪⚡🇰⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇸⚡🇪⚡🇽⚡🇾 ⚡🇰⚡🇴 ⚡🇧⚡🇪⚡🇯 - ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇭⚡🇬⚡🇼⚡🇳 ⚡🇵⚡🇪",
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇵⚡🇰⚡🇩 ⚡🇨⚡🇵 ⚡🇳⚡🇾 ⚡🇰⚡🇷",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇷⚡🇪⚡🇳⚡🇩⚡🇾",
"⚡🇧⚡🇭⚡🇰⚡🇰 ⚡🇨⚡🇺⚡🇩",
"⚡🇹⚡🇪⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮",
"⚡🇨⚡🇺⚡🇩 ⚡🇯⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇮⚡🇩⚡🇮 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇸⚡🇱⚡🇴⚡🇼",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇮⚡🇾⚡🇦 ⚡🇨⚡🇮⚡🇴⚡🇩⚡🇺",
"⚡🇧⚡🇭⚡🇦⚡🇬?",
"⚡🇧⚡🇭⚡🇦⚡🇰 ⚡🇨⚡🇺⚡🇩",
"⚡🇹⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇸⚡🇱⚡🇴⚡🇼",
"⚡🇸⚡🇱⚡🇴⚡🇼 ⚡🇫⚡🇮⚡🇷⚡🇸⚡🇪",
"⚡🇨⚡🇺⚡🇩⚡🇬⚡🇷⚡🇮⚡🇧",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇩⚡🇴⚡🇺",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇳⚡🇪⚡🇹 ⚡🇴⚡🇳 ⚡🇴⚡🇫⚡🇫 ⚡🇼⚡🇦⚡🇱⚡🇮 ⚡🇷⚡🇳⚡🇩⚡🇾",
"⚡🇴⚡🇾⚡🇪 ⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇮⚡🇩⚡🇭⚡🇦⚡🇷 ⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇨⚡🇭⚡🇦⚡🇦⚡🇵",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇷⚡🇩⚡🇺",
"⚡🇴⚡🇮 ⚡🇲⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇪⚡🇪",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇪⚡🇯",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇸⚡🇺⚡🇦⚡🇷 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇪⚡🇯",
"⚡🇳⚡🇪⚡🇹 ⚡🇴⚡🇫⚡🇫 ⚡🇴⚡🇳 ⚡🇰⚡🇷 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇰⚡🇪",
"⚡🇹⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇮 ⚡🇰⚡🇪⚡🇸⚡🇪",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇸⚡🇱⚡🇴⚡🇼 ⚡🇲⚡🇦⚡🇩⚡🇭⚡🇦⚡🇷⚡🇨⚡🇴⚡🇩",
"⚡🇹⚡??⚡🇰⚡🇨 ⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇰⚡🇷 ⚡🇲⚡🇸⚡🇬 ⚡🇩⚡🇪⚡🇱⚡🇪⚡🇹⚡🇪",
"⚡🇴⚡🇮 ⚡🇸⚡🇺⚡🇦⚡🇷 ⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇰⚡🇪",
"⚡🇹⚡??⚡🇰⚡🇨 ⚡🇫⚡🇺⚡🇫⚡🇮",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇮⚡🇩⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇮",
"⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇨⚡🇺⚡🇩 ⚡🇦⚡🇧",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩",
"⚡🇧⚡🇭⚡🇦⚡🇰 ⚡🇨⚡🇺⚡🇩",
"⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇷⚡🇺",
"⚡🇹⚡🇲⚡🇰⚡🇱 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇬⚡🇷⚡🇮⚡🇧",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳 ⚡🇻⚡🇪⚡🇸⚡🇮⚡🇾⚡🇦⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇮",
"⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇬⚡🇳⚡🇩⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇦 ⚡🇹⚡🇺 ⚡🇫⚡🇮⚡🇷⚡🇸⚡🇪 ⚡🇳⚡🇪⚡🇹 ⚡🇴⚡🇳 ⚡🇴⚡🇫⚡🇫",
"⚡🇬⚡🇷⚡🇮⚡🇧 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇯⚡🇦 ⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇲⚡🇦⚡🇷⚡🇺 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇷⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦⚡🇦",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇧⚡🇭⚡🇦⚡🇬 ⚡🇹⚡🇧⚡🇰⚡🇨",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇪⚡🇾 ⚡🇨⚡🇵",
"⚡🇨⚡🇵 ⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇪⚡🇭⚡🇭",
"⚡🇨⚡🇵 ⚡🇹⚡🇲⚡🇰⚡🇱 ⚡🇲⚡🇪⚡🇭",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇦⚡🇧⚡🇪 ⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇩⚡🇴⚡🇺⚡🇧⚡🇱⚡🇪 ⚡🇸⚡🇪⚡🇳⚡🇩 ⚡🇰⚡🇴 ⚡🇨⚡🇵 ⚡🇹⚡🇲⚡🇰⚡🇨 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇲⚡🇪 ⚡🇨⚡🇵 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇺⚡🇳⚡🇬⚡🇦 ⚡🇦⚡🇦⚡🇯 ⚡🇲⚡🇪⚡🇭⚡🇭",
"⚡🇭⚡🇹 ⚡🇹⚡🇧⚡🇰⚡🇨 ⚡🇩⚡🇦⚡🇱⚡🇦⚡🇱 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪.",
"⚡🇷⚡🇳⚡🇩⚡🇾 ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇨⚡🇺⚡🇩⚡🇶 ⚡🇹⚡🇷⚡🇾⚡🇲⚡🇦",
"⚡🇵⚡🇦⚡🇷⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭⚡🇪⚡🇬⚡🇦..",
"⚡🇹⚡🇷⚡🇦 ⚡🇷⚡🇳⚡🇩⚡🇭⚡🇧⚡🇭⚡🇦⚡🇰",
"⚡🇱⚡🇦⚡🇬⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇨⚡🇪 ⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇱⚡🇦⚡🇬⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪..",
"⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱",
"⚡🇧⚡🇭⚡🇮⚡🇰⚡🇦⚡🇷⚡🇮 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇨⚡🇭⚡🇺⚡🇸 ⚡🇲⚡🇪⚡🇷⚡??.",
"⚡🇱⚡🇴⚡🇼 ⚡🇱⚡🇪⚡🇻⚡🇪⚡🇱 ⚡🇨⚡🇵 ⚡🇨⚡🇷",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱 ⚡🇱⚡🇴⚡🇼 ⚡🇱⚡🇪⚡🇻⚡🇪⚡🇱 ⚡🇼⚡🇪⚡🇦⚡🇰",
"⚡🇲⚡🇪⚡🇷⚡🇪 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇵⚡🇪 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇭⚡🇮⚡🇯⚡🇩⚡🇪",
"⚡🇫⚡🇷⚡🇪⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇫⚡🇷⚡🇪⚡🇪 ⚡🇲⚡🇪⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪"
"⚡🇸⚡🇵⚡🇪⚡🇪⚡🇩 ⚡🇳⚡🇾 ⚡🇼⚡🇪⚡🇦⚡🇰 ⚡🇹⚡🇦⚡🇹⚡🇹⚡🇪 ⚡🇹⚡🇪⚡🇷⚡🇲⚡🇪",
"⚡??⚡🇮⚡🇹⚡🇳⚡🇮 ⚡🇧⚡🇷 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦⚡🇾⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇱⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇦⚡🇵⚡🇰⚡🇦",
"⚡🇱⚡🇺⚡🇳 ⚡🇨⚡🇺⚡🇸 ⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇸⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇧⚡🇦⚡🇵⚡🇰⚡🇦",
"⚡🇰⚡🇴⚡🇮 ⚡🇳⚡🇾 ⚡🇩⚡🇪⚡🇰⚡🇭 ⚡🇷⚡🇭⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇮⚡🇨⚡🇭⚡🇴⚡🇩 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪",
"⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇸 ⚡🇾⚡🇪⚡🇭⚡🇮 ⚡🇯⚡🇦⚡🇳⚡🇹⚡🇦 ⚡🇲⚡🇪⚡🇾",
"⚡🇨⚡🇵 ⚡🇧⚡🇴⚡🇱⚡🇪⚡🇬⚡🇦 ⚡🇹⚡🇴 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇯⚡🇦⚡🇾⚡🇪⚡🇬⚡🇮",
"⚡🇸⚡🇱⚡🇴⚡🇼 ⚡🇪⚡🇾 ⚡🇹⚡🇺 ⚡🇰⚡🇮⚡🇩",
"⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭..",
"⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭..",
"⚡🇹⚡🇾⚡🇲 ⚡🇸⚡🇪 ⚡🇵⚡🇭⚡🇱⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇹⚡🇾⚡🇲 ⚡🇭⚡🇴⚡🇬⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦",
"⚡🇲⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇹⚡🇾⚡🇲 ⚡🇸⚡🇪 ⚡🇵⚡🇭⚡🇱⚡🇪",
"⚡🇺⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪 ⚡🇰⚡🇪 ⚡🇱⚡🇩⚡🇰⚡🇪",
"⚡🇲⚡🇦⚡🇨⚡🇦⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇨⚡🇴⚡🇳 ⚡🇰⚡🇧 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇮⚡🇦 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇹⚡🇪⚡🇷⚡🇾",
"⚡🇰⚡🇴⚡🇮 ⚡🇭⚡🇴⚡🇬⚡🇦 ⚡🇹⚡🇲⚡🇱",
"⚡🇲⚡🇦⚡🇨⚡🇭⚡🇦⚡🇷 ⚡🇨⚡🇺⚡🇩⚡🇱⚡🇪 ⚡🇹⚡🇺",
"⚡🇲⚡🇪⚡🇳⚡🇺 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇨⚡🇴⚡🇩⚡🇳⚡🇦 ⚡🇸⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇧⚡🇴⚡🇱 ⚡🇲⚡🇺⚡🇯⚡🇭⚡🇪 ⚡🇨⚡🇴⚡🇩 ⚡🇩⚡🇪",
"⚡🇧⚡🇸 ⚡🇲⚡🇪⚡🇾 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩⚡🇳⚡🇦 ⚡🇨⚡🇭⚡🇹⚡🇦 ⚡🇭⚡🇺",
"⚡🇪⚡🇼⚡🇼 ⚡🇲⚡🇦⚡🇰⚡🇦 ⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇺⚡🇹⚡🇭",
"⚡🇲⚡🇪⚡🇴⚡🇼 ⚡🇨⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇨⚡🇴⚡🇩⚡🇺",
"⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇷⚡🇰⚡🇭 ⚡🇩⚡🇮⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇫⚡🇺⚡🇩⚡🇪 ⚡🇵⚡🇪",
"⚡🇲⚡🇪⚡🇷⚡🇦 ⚡🇱⚡🇺⚡🇳⚡🇩 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇱 ⚡🇺⚡🇹⚡🇭",
"⚡🇰⚡🇮⚡🇩⚡🇪⚡🇪 ⚡🇿⚡🇮⚡🇳⚡🇩⚡🇦 ⚡🇭⚡🇴",
"⚡🇲⚡🇦⚡🇷 ⚡🇳⚡🇾 ⚡🇰⚡🇮⚡🇩⚡🇩⚡🇪 ⚡🇹⚡🇾⚡🇵⚡🇪 ⚡🇰⚡🇷",
"⚡🇨⚡🇭⚡🇺⚡🇵 ⚡🇧⚡🇰⚡🇱",
"⚡🇧⚡🇨 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹",
"⚡🇲⚡🇨 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇫⚡🇦⚡🇸⚡🇹",
"⚡🇫⚡🇦⚡🇸⚡🇹 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪",
"⚡🇫⚡🇦⚡🇸⚡🇹 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇰⚡🇦⚡🇲⚡🇿⚡🇴⚡🇷"
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇨⚡🇱⚡🇦⚡🇮⚡🇲 ⚡🇨⚡🇷⚡🇼⚡🇦",
"⚡🇦⚡🇼⚡🇿 ⚡🇳⚡🇮⚡🇨⚡🇭⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪 ⚡🇰⚡🇪 ⚡🇧⚡🇨⚡🇭⚡🇪",
"⚡🇸⚡🇦⚡🇼⚡🇦⚡🇱 ⚡🇳⚡🇾 ⚡🇵⚡🇺⚡🇨⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇦⚡🇧⚡🇴⚡🇸⚡🇩⚡🇦",
"⚡🇫⚡🇾⚡🇹⚡🇪⚡🇷 ⚡🇧⚡🇳⚡🇪⚡🇬⚡🇦 ⚡🇱⚡🇦⚡🇬⚡🇩⚡🇪 ⚡🇲⚡🇦⚡🇩⚡🇷⚡🇨⚡🇭⚡🇴⚡🇩",
"⚡🇴⚡🇾⚡🇪 ⚡🇰⚡🇦⚡🇦⚡🇱⚡🇪 ⚡🇷⚡🇴 ⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦",
"⚡🇴⚡🇾⚡🇪 ⚡🇰⚡🇦⚡🇦⚡🇱⚡🇪 ⚡🇷⚡🇴⚡🇴 ⚡🇳⚡🇾",
"⚡🇸⚡🇭⚡🇴⚡🇷⚡🇹 ⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺 ⚡🇧⚡🇮⚡🇳⚡🇦 ⚡🇷⚡🇺⚡🇰⚡🇪",
"⚡🇸⚡🇭⚡🇴⚡🇷⚡🇹 ⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺 ⚡🇦⚡🇵⚡🇳⚡🇮 ⚡🇲⚡🇦⚡🇰⚡🇴 ⚡🇱⚡🇪⚡🇰⚡🇷",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇸⚡🇹⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇧⚡🇭⚡🇪⚡🇳 ⚡🇻⚡🇮 ⚡🇨⚡🇺⚡🇩⚡🇼⚡🇦 ⚡🇱⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇪 ⚡🇸⚡🇹⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇮⚡🇩⚡🇮 ⚡🇻⚡🇮 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮",
"⚡🇨⚡🇭⚡🇦⚡🇹 ⚡🇫⚡🇾⚡🇹⚡🇪⚡🇷 ⚡🇧⚡🇳⚡🇪⚡🇬⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪 ⚡🇨⚡🇴⚡🇩⚡🇺 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇰⚡🇴",
"⚡🇧⚡🇴⚡🇱 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮⚡🇧⚡🇦⚡🇦⚡🇿 ⚡🇩⚡🇦⚡🇩⚡🇩⚡🇾 ⚡🇪⚡🇾",
"⚡🇧⚡🇺⚡🇱⚡🇱⚡🇾🇽 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇺⚡🇹⚡🇭",
"⚡🇲⚡🇦⚡🇷 ⚡🇲⚡🇦⚡🇷⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺",
"⚡🇴⚡🇷 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦 ⚡🇲⚡🇦⚡🇷⚡🇰⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇦⚡🇮"
"⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇯",
"⚡🇴⚡🇷 ⚡🇧⚡🇩⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇲⚡🇨",
"⚡🇴⚡🇷 ⚡🇧⚡🇩⚡🇦 2 ⚡🇱⚡🇮⚡🇳⚡🇪 ⚡🇼⚡🇱⚡🇦 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇲⚡🇰⚡🇨",
"⚡🇴⚡🇷 ⚡🇧⚡??⚡🇦 ⚡🇴⚡🇾⚡🇪 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇲⚡🇱",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇦 ⚡🇧⚡🇺⚡🇷",
"⚡🇴⚡🇾⚡🇪 ⚡🇰⚡🇪⚡🇪⚡🇩⚡🇪",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇱⚡🇦⚡🇩⚡🇰⚡🇪",
"⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇲⚡🇰⚡🇱 ⚡🇺⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇧⚡🇦⚡🇨⚡🇨⚡🇭⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇳⚡🇦⚡🇳⚡🇮 ⚡🇲⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦⚡🇱",
"⚡🇹⚡🇪⚡🇯 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇨⚡🇪",
"⚡🇴⚡🇾⚡🇪 ⚡🇲⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇪 ⚡🇲⚡🇷⚡🇪⚡🇳⚡🇬⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇾",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇮⚡🇾⚡🇦 ⚡🇰⚡🇮 ⚡🇬⚡🇦⚡🇳⚡🇩",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇩⚡🇦⚡🇩⚡🇮 ⚡🇰⚡🇦 ⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦",
"⚡🇲⚡🇰⚡🇱 ⚡🇺⚡🇹⚡🇭 ⚡🇧⚡🇪⚡🇭⚡🇪⚡🇳⚡🇨⚡🇴⚡🇩",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇮 ⚡🇧⚡🇺⚡🇷 ⚡🇩⚡🇪",
"⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇦 ⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦 ⚡🇲⚡🇪 ⚡🇱⚡🇦⚡🇺⚡🇩⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇺⚡🇩⚡🇻⚡🇦",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇮 ⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪 ⚡🇲⚡🇦⚡🇷 ⚡🇬⚡🇦⚡🇾⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇲⚡🇷⚡🇺",
"⚡🇯⚡🇦⚡🇱⚡🇮⚡🇩 ⚡🇰⚡🇷 ⚡🇸⚡🇵⚡🇦⚡🇲",
"⚡🇲⚡🇨 ⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇷⚡🇴⚡🇰⚡🇪⚡🇳⚡🇬⚡🇦",
"⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦⚡🇰⚡🇮 ⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷",
"⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷.⚡🇲⚡🇦⚡🇦⚡🇰⚡🇪 ⚡🇱⚡🇴⚡🇩⚡🇪",
"⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇪 ⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇨⚡🇺⚡🇩 ⚡🇹⚡🇺",
"⚡🇸⚡🇵⚡🇦⚡🇲 ⚡🇰⚡🇷 ⚡🇰⚡🇮⚡🇩",
"⚡🇳⚡🇴⚡🇴⚡🇧 ⚡🇹⚡🇪⚡🇷⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇨⚡🇭⚡🇴⚡🇩⚡🇺",
"⚡🇷⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇧⚡🇪⚡🇹⚡🇪 ⚡🇲⚡🇦⚡🇷 ⚡🇲⚡🇦⚡🇹 ⚡🇹⚡🇺",
"⚡🇳⚡🇴⚡🇴⚡🇧 ⚡🇯⚡🇦⚡🇱⚡🇩⚡🇮 ⚡🇱⚡🇮⚡🇰⚡🇭 ⚡🇼⚡🇷⚡🇳⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇲⚡🇦⚡🇦 ⚡🇷⚡🇦⚡🇳⚡🇩",
"⚡🇨⚡🇺⚡?? ⚡🇬⚡🇦⚡🇮 ⚡🇲⚡🇦⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇺⚡🇹⚡🇭 ⚡🇷⚡🇦⚡🇳⚡🇩⚡🇾⚡🇰⚡🇪 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇨⚡🇭⚡🇱 ⚡🇨⚡🇺⚡🇩⚡🇰⚡🇪 ⚡🇩⚡🇮⚡🇰⚡🇭⚡🇦 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇯⚡🇱⚡🇩⚡🇮 ⚡🇹⚡🇾⚡🇵 ⚡🇨⚡🇷 ⚡🇳⚡🇴⚡🇴⚡🇧 ⚡🇭⚡🇦⚡🇱⚡🇰⚡🇪",
"⚡🇨⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇵⚡🇬⚡🇱 ⚡🇳⚡🇾 ⚡🇭⚡🇴 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇨⚡🇺⚡🇩 ⚡🇨⚡🇺⚡🇩 ⚡🇰⚡🇪 ⚡🇷⚡🇦⚡🇳⚡🇩 ⚡🇧⚡🇳⚡🇯⚡🇦 ⚡🇹⚡🇺 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇲⚡🇦⚡🇰⚡🇮⚡🇨⚡🇭⚡🇺⚡🇹 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇳⚡🇴⚡🇴⚡🇧",
"⚡🇬⚡🇦⚡🇳⚡🇩⚡🇦 ⚡🇨⚡🇾⚡🇺 ⚡🇨⚡🇺⚡🇩 ⚡🇷⚡🇭⚡🇦 ⚡🇹⚡🇺 ?",    "⚡🇮⚡🇹⚡🇳⚡🇦 ⚡🇬⚡🇳⚡🇩⚡🇦 ⚡🇳⚡🇾 ⚡🇨⚡🇺⚡🇩 ⚡🇦⚡🇨⚡🇭⚡🇪 ⚡🇸⚡🇪 ⚡🇨⚡🇺⚡🇩",
"⚡🇲⚡🇦⚡🇦⚡🇳 ⚡🇱⚡🇪 ⚡🇨⚡🇺⚡🇩 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇺 ⚡🇸⚡🇺⚡🇳 ⚡🇧⚡🇦⚡🇹 ⚡🇦⚡🇧",
"⚡🇲⚡🇦⚡🇰⚡🇦⚡🇫⚡🇺⚡🇩⚡🇩⚡🇦 ⚡🇫⚡🇦⚡🇹 ⚡🇬⚡🇾⚡🇦 ⚡🇹⚡🇪⚡🇷⚡🇾 ⚡🇷⚡🇺⚡🇰",
]
bas_texts = [
"★🆂★🅷★🅰★🅽★🆃 ★🅱★🅴★🆃★🅷 ★🅼★🅰★🅳★🆁★🅲★🅷★🅾★🅳 ★🆆★🆁★🅽★🅰 ★🅼★🅰★🅺★🅰★🅱★🅾★🆂★🅳★🅰 ★🆃★🅴★🅴★🆈.",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃..",
"★🅻★🆆★🅳★🅴 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅻★🅻★🅻 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅲★🆄★🅳★🅺★🅴 ★🅿★🅶★🅻 ★🅳★🅴★🅺★🅷.",
"★🅼★🅰★🅲★🅷★🅰★🆁 ★🅺★🅸 ★🅹★🅷★🅰★🅰★🆃 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅻★🅻★🅻★🅻 ★🅲★🆄★🅳 ★🅰★🅲★🅷★🅴 ★🆂★🅴 ★🆈★🅷★🅰★🅿★🅴 ★🆃★🅤",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼 ★🅳★🆄 ★🆃★🅰★🅿★🅰 ★🆃★🅰★🅿?",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅱★🅷★🅽 ★🅰★🅱★🅰★🅱★🅴 ★🅱★🅳★🅸 ★🆁★🅰★🅽★🅳★🅸.",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅾★🅰★🅰★🅴 ★🅱★🅰★🅳★🅸 ★🆁★🅰★🅽★🅳★🅳★🅳★🅳★🅳",
"★🆃★🅴★🆁★🅰 ★🅱★🅰★🅰★🅿 ★🆁★🅰★🅽★🅳★🅸★🅱★🅰★🅰★🅾 ★🅴★🅈 ★🅳★🅴★🅺★🅷",
"★🅺★🅸★🆃★🅽★🅸 ★🅲★🅷★🅾★🅳★🆄 ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅰★🅱 ★🅾★🆁..",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅲★🅷★🅾★🅳 ★🅳★🅸 ★🅷★🅼 ★🅽★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅴 ★🅱★🅴★🅴★🅻★🅰 ★🅱★🅽★🅴★🅶★🅰 ★🆁★🅾★🅰★🅳 ★🅿★🅴★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅴★🅺 ★🅳★🅰★🅼 ★🆃★🅾★🅿 ★🅱★🅴★🆇★🆈",
"★🅼★🅰★🅻★🆄★🅼 ★🅽★🅰 ★🅿★🅷★🆁 ★🅺★🅴★🅰★🅴 ★🅻★🅴★🆃★🅰 ★🅷★🆄 ★🅼 ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🆃★🅰★🅿★🅰 ★🆃★🅰★🅿★🅿★🅿★🅿★🅿",
"★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 ★🆃★🅤 ★??★🅴★🆁★🅴★🅶★🅰 ★🆃★🆈★🅿★🅸★🅽★🅶 ★🅺★🆁★🅴★🅶★🅰 ★🆃★🅼★🅺★🅲",
"★🅱★🅴★🅱★🅳 ★🅿★🅺★🅳 ★🅻★🆆★🅳★🅴★🅴★🅴★🅴 ★🆆★🆁★🅽★🅰 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳 ★🅿★🅺★🅳",
"★🅱★🅰★🅰★🅿 ★🅺★🅸 ★🅱★🅴★🅱★🅳 ★🅼★🆃★🅲★🅷 ★🅺★🆁★🆁★🆁",
"★🅻★🆆★🅳★🅰 ★🅻★🅴 ★🅼★🅴★🆁★🅰 ★🅹★🅰★🅻★🅳★🅸 ★🆂★🅴 ★🆃★🅤",
"★🅿★🅰★🅿★🅰 ★🅺★🅸 ★🅱★🅴★🅱★🅳 ★🅼★🆃★🅲★🅷 ★🅽★🅷★🅸 ★🅷★🅾 ★🆁★🅷★🅸 ★🅺★🆈★🅰 ★🆃★??★🆁★🅴★🆂★🅴",
"★🅰★🅻★🅴 ★🅰★🅻★🅴 ★🅼★🅴★🅻★🅰 ★🅱★🅲★🅷★🅰★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅺★🅰 ★🅱★🅾★🅂★🅳★🅰 ★🆂★🆄★🅽",
"★🅲★🅷★🆄★🅳 ★🅶★🆈★🅰 ★🆁★🅰★🅽★🅳★🅸★🅱★🅰★🅰★🅾 ★🅿★🅰★🅿★🅰 ★🅱★🅴★🅴★🅴 ★🆃★🅤",
"★🅼★🅴★🅽★🆄 ★🅺★🅸 ★🅿★🆃★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸",
"★🅺★🅾★🅸 ★🅱★🅰★🅰★🆃 ★🅽★🅈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🆈 ★🆃★🅴★🆁★🆈",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅰★🅰★🅰★🅰 ★🅼★🅰★🅺★🅰★🅱★🅾★🅂★🅳★🅰 ★🆃★🅴★🆁★🆈",
"★🆇★🅷★🆄★🅳 ★🅶★🅰★🅸 ★🅼★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅺★🅸★🅳★🅰★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅲★🅷★🆄★🅳 ★🅶★🆈★🅸 ★🅰★🅱 ★🅱★🅰★🆁 ★🅼★🆃 ★🅷★🅾★🅽★🅰",
"★🆈★🅴 ★🅻★🆄★🅽★🅳 ★🅻★🅴 ★🅼★🅴★🆁★🅰 ★🅲★🅷★🅻 ★🅹★🅰★🅻★🅳★🅸 ★🆂★🅴",
"★🅺★🅸★🅳★🅰★🅰★🅰 ★🅱★🅰★🆁 ★🅽★🅰 ★🅷★🅾 ★🆃★🅤 ★🅷★🅰★🅷★🅰★🅷★🅷",
"★🅱★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🆆★🅳★🅴 ★🅱★🅷★🆁★🅼 ★🅺★🆁",
"★🅺★🅸★🆃★🅽★🅸 ★🅶★🅻★🅸★🅈★🅰 ★🅿★🅳★🆆★🅴★🅶★🅰 ★🅰★🅿★🅽★🅸 ★🅼★🅰 ★🅺★🅾",
"★🅲★🅷★🆄★🅿 ★🅽★🅰★🅻★🅻★🅸★🅸 ★🆁★🅰★🅽★🅳★🆈★🅺★🅴 ★🅻★🅰★🅳★🅺★🅴",
"★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅱★🅰★🅳★🅰★🅺 ★🅿★🅁 ★🅻★🅸★🆃★🅰★🅺★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🆄★🅽★🅶★🅰 😂😆🤤",
"★🅰★🅱★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰 ★🅼★🅰★🅳★🅴★🆁★🅲★🅷★🅾★🅾★🅳 ★🅺★🆁 ★🅿★🅸★🅻★🅻★🅴 ★🅿★🅰★🅿★🅰 ★🅱★🅴★🅴 ★🅻★🅰★🅳★🅴★🅶★🅰 ★🆃★🅤 😼😂🤤",
"★🅶★🅰★🅻★🅸 ★🅶★🅰★🅻★🅸 ★🅽★🅴 ★🅱★🅷★🅾★🆁 ★🅷★🅴 ★🆃★🅴★??★🅸 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸 ★🅲★🅷★🅾★🆁 ★🅷★🅴 💋💋💦",
"★🅰★🅱★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳★🆄 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🅺★🆄★🆃★🆃★🅴 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 😂👻🔥",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅰★🅸★🅱★🅴 ★🅲★🅷★🅾★🅳★🅰 ★🅰★🅸★🅱★🅴 ★🅲★🅷★🅾★🅳★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅱★🅴★🅳 ★🅿★🅴★🅷★🅸 ★🅼★🆄★🆃★🅷 ★🅳★🅸★🅰 💦💦💦💦",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🅱★🅷★🅾★🅱★🅴★🅳★🅴 ★🅼★🅴 ★🅰★??★🅰★🅶 ★🅻★🅰★🅶★🅰★🅳★🅸★🅰 ★🅼★🅴★🆁★🅰 ★🅼★🅾★🆃★🅰 ★🅻★🆄★🅽★🅳 ★🅳★🅰★🅻★🅺★🅴 🔥🔥💦😆😆",
"★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳★🆄 ★🅲★🅷★🅰★🅻 ★🅽★🅸★🅺★🅰★🅻",
"★🅺★🅸★🆃★🅽★🅰 ★🅲★🅷★🅾★🅳★🆄 ★🆃★🅴★🆁★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅰★🅱★🅱 ★🅰★🅿★🅽★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅱★🅷★🅴★🅹 😆👻🤤",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾★🆃★🅾 ★🅲★🅷★🅾★🅳 ★🅲★🅷★🅾★🅳★🅺★🅴 ★🅿★🆄★🆁★🅰 ★🅱★🅰★🅰★🅳 ★🅳★🅸★🅰 ★🅲★🅷★🆄★🆃★🅷 ★🅰★🅱★🅱 ★??★🅴★🆁★🅸 ★🅶★🅱 ★🅺★🅾 ★🅱★🅷★🅴★🅹 😆💦🤤",
"★🆃★🅴★🆁★🅸 ★🅶★🅱 ★🅺★🅾 ★🅴★🆃★🅽★🅰 ★🅲★🅷★🅾★🅳★🅰 ★🅱★🅴★🅷★🅴★🅽 ★??★🅴 ★🅻★🅾★🅳★🅴 ★🆃★🅴★🆁★🅸 ★🅶★🅱 ★🆃★🅾 ★🅼★🅴★🆁★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅱★🅰★🅽★🅶★🅰★🆈★🅸 ★🅰★🅱★🅱 ★🅲★🅷★🅰★🅻 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳★🆃★🅰 ★🅱★🅸★🆁★🅱★🅴 ♥️💦😆😆😆😆",
"★🅷★🅰★🆁★🅸 ★🅷★🅰★🆁★🅸 ★🅶★🅷★🅰★🅰★🅱 ★🅼★🅴 ★🅹★🅷★🅾★🅿★🅳★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰 🤣🤣💋💦",
"★🅲★🅷★🅰★🅻 ★🆃★🅴★🆁★🅴 ★🅱★🅰★🅰★🅿 ★🅺★🅾 ★🅱★🅷★🅴★🅹 ★🆃★🅴★🆁★🅰 ★🅱★🅰★🅱★🅺★🅰 ★🅽★🅷★🅸 ★🅷★🅴 ★🅿★🅰★🅿★🅰 ★🅱★🅴★🅴 ★🅻★🅰★🅳★🅴★🅶★🅰 ★🆃★🅤",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅱★🅾★🅼★🅱 ★🅳★🅰★🅻★🅺★🅴 ★🆄★🅳★🅰 ★🅳★🆄★🅽★🅶★🅰 ★🅼★🅰★🅰★🅺★🅴 ★🅻★🅰★🆆★🅳★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🆃★🆁★🅰★🅸★🅽 ★🅼★🅴 ★🅻★🅴★🅹★🅰★🅺★🅴 ★🆃★🅾★🅿 ★🅱★🅴★🅳 ★🅿★🅴 ★🅻★🅸★🆃★🅰★🅺★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🆄★🅽★🅶★🅰 ★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 🤣🤣💋💋",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅴 ★🅽★🆄★🅳★🅴★🅰 ★🅶★🅾★🅾★🅶★🅻★🅴 ★🅿★🅴 ★🆄★🅿★🅻★🅾★🅰★🅳 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🅰★🅴★🆆★🅳★🅴 👻🔥",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅴 ★🅽★🆄★🅳★🅴★🅰 ★🅶★🅾★🅾★🅶★🅻★🅴 ★🅿★🅴 ★🆄★🅿★🅻★🅾★🅰★🅳 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🅰★🅴★🆆★🅳★🅴 👻🔥",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳 ★??★🅷★🅾★🅳★🅺★🅴 ★🅱★🅰★🅽★🅰★🅺★🅴 ★🅱★🅸★🅳★🅴★🅾 ★🅱★🅰★🅽★🅰★🅺★🅴 ★🆇★🅽★🆇★🆇.★🅲★🅾★🅼 ★🅿★🅴 ★🅽★🅴★🅴★🅻★🅰★🅼 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅺★🆄★🆃★🆃★🅴 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 💦💋",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🅳★🅰★🅸 ★🅺★🅾 ★🅿★🅾★🆁★🅽★🅷★🆄★🅱.★🅲★🅾★🅼 ★🅿★🅴 ★🆄★🅿★🅻★🅾★🅰★🅳 ★🅺★🅰★🆁★🅳★🆄★🅽★🅶★🅰 ★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 🤣💋💦",
"★🅰★🅱★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳★🆄 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🆃★🅴★🆁★🅴★🅺★🅾 ★🅲★🅷★🅰★🅺★🅺★🅾 ★🅱★🅴★🅴 ★🅿★🅸★🅻★🆆★🅰★🆅★🆄★🅽★🅶★🅰 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 🤣🤣",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅱★🅰★🅰★🅳★🅺★🅴 ★🆁★🅰★🅺★🅳★🅸★🅰 ★🅼★🅰★🅰★🅺★🅴 ★🅻★🅾★🅳★🅴 ★🅹★🅰★🅰 ★🅰★🅱★🅱 ★🅱★🅸★🅻★🆆★🅰★🅻★🅴 👄👄",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳 ★🅺★🅰★🅰★🅻★🅰",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅻★🅴★🆃★🅸 ★🅼★🅴★🆁★🅸 ★🅻★🆄★🅽★🅳 ★🅱★🅰★🅳★🅴 ★🅼★🅰★🅱★🅰★🅱★🅸 ★🅱★🅴★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅾 ★🅼★🅴★🅽★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🅰★🅻★🅰 ★🅱★🅾★🅷★🅾★🆃 ★🅱★🅰★🅱★🆃★🅴 ★🅱★🅴★🅴",
"★🅱★🅴★🆃★🅴 ★🆃★🅤 ★🅱★🅰★🅰★🅿 ★🅱★🅴★🅴 ★🅻★🅴★🅶★🅰 ★🅿★🅰★🅽★🅶★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅾 ★🅲★🅷★🅾★🅳 ★🅳★🆄★🅽★🅶★🅰 ★🅺★🅰★🆁★🅺★🅴 ★🅽★🅰★🅽★🅶★🅰 💦💋",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅷 ★🅼★🅴★🆁★🅴 ★🅱★🅴★🆃★🅴 ★🅰★🅶★🅻★🅸 ★🅱★🅰★🅰★🆁 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅻★🅴★🅺★🅴 ★🅰★🅰★🆈★🅰 ★🅼★🅰★🆃★🅷 ★🅺★🅰★🆃 ★🅾★🆁 ★🅼★🅴★🆁★🅴 ★🅼★🅾★🆃★🅴 ★🅻★🆄★🅽★🅳 ★🅱★🅴★🅴 ★🅲★🅷★🆄★🅳★🆆★🅰★🆈★🅰 ★🅼★🅰★🆃★🅷 ★🅺★🅰★🆁",
"★🅲★🅷★🅰★🅻 ★🅱★🅴★🆃★🅰 ★🆃★🆄★🅹★🅷★🅴 ★🅼★🅰★🅰★🅱 ★🅺★🅸★🅰 🤣★🆃★🅤 ★🅰★🅱★🅱 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅺★🅾 ★🅱★🅷★🅴★🅹",
"★🅱★🅷★🅰★🆁★🅰★🅼 ★🅺★🅰★🆁 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅳★🅰 ★🅺★🅸★🆃★🅽★🅰 ★🅶★🅰★🅰★??★🅸★🅰 ★🅱★🆄★🅽★🆆★🅰★🆈★🅴★🅶★🅰 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅰★🅰 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅴 ★🆄★🅿★🅴★🆁",
"★🅰★🅱★🅴 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🅰★🆄★🅺★🅰★🆃 ★🅽★🅷★🅸 ★🅷★🅴★🆃★🅾 ★🅰★🅿★🅽★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅻★🅴★🅺★🅴 ★🅰★🅰★🆈★🅰 ★🅼★🅰★🆃★🅷 ★🅺★🅰★🆁 ★🅷★🅰★🅷★🅰★🅷★🅰★🅷★🅰",
"★🅺★🅸★🅳★🅾 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★?? ★🅲★🅷★🅾★🅳★🅺★🅴 ★🆃★🅴★🆁★🆁 ★🅻★🅸★🆈★🅴 ★🅱★🅷★🅰★🅸 ★🅳★🅴★🅳★🅸★🆈★🅰",
"★🅹★🆄★🅽★🅶★🅻★🅴 ★🅼★🅴 ★🅽★🅰★🅲★🅷★🆃★🅰 ★🅷★🅴 ★🅼★🅾★🆁★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🅳★🅰★🅸 ★🅳★🅴★🅺★🅺★🅴 ★🅱★🅰★🅱 ★🅱★🅾★🅻★🆃★🅴 ★🅾★🅽★🅲★🅴 ★🅼★🅾★🆁★🅴 ★🅾★🅽★🅲★🅴 ★🅼★🅾★🆁★🅴 🤣🤣💦💋",
"★🅶★🅰★??★🅸 ★🅶★🅰★🅻★🅸 ★🅼★🅴 ★🆁★🅴★🅷★🆃★🅰 ★🅷★🅴 ★🅱★🅰★🅽★🅳 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳 ★🅳★🅰★🅻★🅰 ★🅾★🆁 ★🅱★🅰★🅽★🅰 ★🅳★🅸★🅰 ★🆁★🅰★🅽★🅳 🤤🤣",
"★🅱★🅰★🅱 ★🅱★🅾★🅻★🆃★🅴 ★🅼★🆄★🅹★🅷★🅺★🅾 ★🅿★🅰★🅿★🅰 ★🅲★🆈★🆄★🅺★🅸 ★🅼★🅴★🅽★🅴 ★🅺★🆁★🅳★🅸★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅿★🆁★🅴★🅶★🅽★🅴★🅽★🆃 🤣🤣",
"★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅱★🅰★🅰★🆁 ★🅺★🅰 ★🅻★🅾★🆄★🅳★🅰 ★🅾★🆁 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅼★🅴★🆁★🅰 ★🅻★🅾★🅳★🅰",
"★🅲★🅷★🅰★🅻 ★🅲★🅷★🅰★🅻 ★🆃★🅤 ★🅰★🅿★🅽★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🅲★🅷★🅸★🆈★🅰 ★🅳★🅸★🅺★🅰",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅷★🅰 ★🅱★🅰★🅲★🅷★🅷★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰★🅺★🅾 ★🅲★🅷★🅾★🅳 ★🅳★🅸★🅰 ★🅽★🅰★🅽★🅶★🅰 ★🅺★🅰★🆁★🅺★🅴",
"★🆃★🅴★🆁★🅸 ★🅶★🅱 ★🅷★🅴 ★🅱★🅰★🅳★🅸 ★🅱★🅴★🆇★🆈 ★🆄★🅱★🅺★🅾 ★🅿★🅸★🅻★🅰★🅺★🅴 ★🅲★🅷★🅾★🅾★🅳★🅴★🅽★🅶★🅴 ★🅿★🅴★🅿★🅱★🅸",
"2 ★🆁★🆄★🅿★🅰★🆈 ★🅺★🅸 ★🅿★🅴★🅿★🅱★🅸 ★🆃★🅴★🆁★🅸 ★🅼★🆄★🅼★🅼★🆈 ★🅱★??★🅱★🅱★🅴 ★🅱★🅴★🆇★🆈 💋💦",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅲★🅷★🅴★🅴★🅼★🅱 ★🅱★🅴★🅴 ★🅲★🅷★🆄★🅳★🆆★🅰★🆅★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅴★🆁★🅲★🅷★🅾★🅾★🅳 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 💦🤣",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🅷 ★🅼★🅴 ★🅼★🆄★🆃★🅷★🅺★🅴 ★🅱★🅰★🆁★🅰★🆁 ★🅷★🅾★🅹★🅰★🆅★🆄★🅽★🅶★🅰 ★🅷★🆄★🅸 ★🅷★🆄★🅸 ★🅷★🆄★🅸",
"★🅱★🅴★🅱★🅳 ★🅻★🅰★🅰★🅰 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅲★🅷★🅾★🅳★🆄 ★🆁★🅰★🅽★🅳★🅸★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 💋💦🤣",
"★🅰★🆁★🅴 ★🆁★🅴 ★🅼★🅴★🆁★🅴 ★🅱★🅴★🆃★🅴 ★🅲★🆈★🆄 ★🅱★🅴★🅱★🅳 ★🅿★🅰★🅺★🅰★🅳 ★🅽★🅰 ★🅿★🅰★🅰★🅰 ★🆁★🅰★🅷★🅰 ★🅰★🅿★🅽★🅴 ★🅱★🅰★🅰★🅿 ★🅺★🅰 ★🅷★🅰★🅷★🅰★🅷★🅰 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸🤣🤣",
"★🅱★🆄★🅽 ★🅱★🆄★🅽 ★🅱★🅰★🅰★🆁 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅴 ★🅹★🅷★🅰★🅽★🆃★🅾 ★🅺★🅴 ★🅱★🅾★🆄★🅳★🅰★🅶★🅰★🆁 ★🅰★🅿★🅽★🅸 ★🅼★🆄★🅼★🅼★🆈 ★🅺★🅸 ★🅽★🆄★🅳★🅴★🅱 ★🅱★🅷★🅴★🅹",
"★🅰★🅱★🅴 ★🅱★🆄★🅽 ★🅻★🅾★🅳★🅴 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅳★🅰 ★🅱★🅰★🅰★🅳 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅾 ★🅺★🅷★🆄★🅻★🅴 ★🅱★🅰★🅹★🅰★🆁 ★🅼★🅴 ★🅲★🅷★🅾★🅳 ★🅳★🅰★🅻★🅰 🤣🤣💋",
"★🅱★🅷★🆁★🅼 ★🅺★🆁 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸 ★🆈★🅷★🅰",
"★🅼★🅴★🆁★🅴 ★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅰★🅻★🅻★🅻★🅻★🅻 ★🅿★🅺★🅳 ★🅹★🅰★🅻★🅳★🅸 ★🅱★🅴★🅴",
"★🆃★🅤 ★🅴★🅺 ★🅺★🅰★🅰★🅼 ★🅺★🆁 ★🅰★🅿★🅽★🅸 ★🅼★🅰 ★🅱★🅷★🅴★🅽 ★🅺★🅾 ★🅲★🆄★🅳★🆆★🅰 ★🅻★🅴 ★🅼★🅴★🆁★🅴 ★🅱★🆃★🅷",
"★🆁★🅽★🅳★🅸 ★🅺★🅴 ★🅻★🅳★🅺★🅴★🅴★🅴★🅴★🅴★🅴★🅴★🅴 ★🅲★🅷★🆄★🅿 ★🅾★🆁 ★🅲★🆄★🅳 ★🆈★🅷★🅰",
"★🅲★🅷★🆄★🅿 ★🆃★🅼★🅺★🅲 ★🅺★🅸★🅳★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰★🅰",
"★🅰★🅿★🅽★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴★🅸★🅽 ★🅼★🆄★🆃★🅷★🅸 ★🅳★🅰★🅰★🅻",
"★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳 ★🅲★🅷★🅾★🅾★🅱 ★🅹★🅰★🅻★🅳★🅸 ★🅱★🅴★🅴",
"★🅰★🅿★🅽★🅸 ★🅼★🅰 ★🅺★🅾 ★🅲★🆄★🅱★🆆★🅰 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳",
"★🅱★🅷★🅴★🅽 ★🅺★🅴 ★🅻★🅰★🆄★🅳★🅴 ★🆃★🅼★🅲",
"★🅱★🅷★🅴★🅽 ★🅺★🅴 ★🆃★🅰★🅺★🅺★🅴 ★🆃★🅼★🅻",
"★🅰★🅱★🅻★🅰 ★🆃★🅴★🆁★🅰 ★🅺★🅷★🅰★🅽 ★🅳★🅰★🅽 ★🅲★🅷★🅾★🅳★🅽★🅴 ★🅺★🅸 ★🅱★🅰★🆁★🅸★🅸",
"★🅱★🅴★🆃★🅴 ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅱★🅰★🅱★🅱★🅴 ★🅱★🅳★🅸 ★🆁★🅰★🅽★🅳",
"★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅻 ★🅹★🅷★🅰★🆃 ★🅺★🅴 ★🅿★🅸★🅱★🅱★🅱★🆄★🆄★🆄★🆄★🆄★🆄 ★🆃★🅼★🅺★🅲",
"★🅻★🆄★🅽★🅳 ★🅿★🅴 ★🅻★🆃★🅺★🅸★🆃 ★🅼★🅰★🅰★🅻★🅻★🅻★🅻 ★🅺★🅸 ★🅱★🅾★🅽★🅳 ★🅷 ★🆃★🆄★??★🆄",
"★🅺★🅰★🅱★🅷 ★🅾★🅱 ★🅳★🅸★🅽 ★🅼★🆄★🆃★🅷 ★🅼★🆁★🅺★🅴 ★🅱★🅾★🅹★🆃★🅰 ★🅼 ★🆃★🅤 ★🅿★🅰★🅸★🅳★🅰 ★🅽★🅰 ★🅷★🅾★🆃★🅰★🅰",
"★🅶★🅻★🆃★🅸 ★🅺★🆁★🅳★🅸 ★🆃★🆄★🅹★🆆 ★🅿★🅰★🅸★🅳★🅰 ★🅺★🆁★🅺★🅴 ★🆃★🅴★🆁★🆈 ★🅼★🅰 ★🅽★🅴 ★🅰★🅱 ★🅲★🆄★🅳 ★🆃★🅤 ★🆈★🅷★🅰",
"★🅱★🅴★🅱★🅳 ★🅿★🅺★🅳★🅳★🅳",
"★🅶★🅰★🅰★🅽★🅳 ★🅼★🅰★🅸★🅽 ★🅻★🆆★🅳★🅰 ★🅳★🅰★🅻 ★🅻★🅴 ★🅰★🅿★🅽★🅸 ★🅼★🅴★🆁★🅰★🅰★🅰",
"★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴★🅸★🅽 ★🅱★🅰★🅼★🅱★🆄 ★🅳★🅴★🅳★🆄★🅽★🅶★🅰★🅰★🅰★🅰★🅰",
"★🅶★🅰★🅽★🅳 ★🅱★🆃★🅸 ★🅺★🅴 ★🅱★🅰★🅻★🅺★🅺★🅺 ★🆃★🅤 ★🅲★🆄★🅳 ★🆈★🅷★🅰",
"★🅶★🅾★🆃★🅴 ★🅺★🅸★🆃★🅽★🅴 ★🅱★🅷★🅸 ★🅱★🅰★🅳★🅴 ★🅷★🅾, ★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅽★🅸★🅲★🅷★🅴 ★🅷★🅸 ★🆁★🅴★🅷★🆃★🅴 ★🅷★🅰",
"★🅷★🅰★🅾★??★🅰★🆁 ★🅻★🆄★🅽★🅳 ★🆃★🅴★🆁★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅰★🅸★🅽",
"★🅹★🅷★🅰★🅰★🅽★🆃 ★🅺★🅴 ★🅿★🅸★🅱★🅱★🆄 ★🆃★🅼★🅺★🅲 ★🅱★🆄★🅽",
"★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🅺★🅸 ★🅺★🅰★🅻★🅸 ★🅲★🅷★🆄★🆃",
"★🅺★🅷★🅾★🆃★🅴★🆈 ★🅺★🅸 ★🅰★🆄★??★🅳★🅰 ★🅴★🆈 ★🆃★🅤 ★🆁★🅰★🅽★🅳★🆈★🅺★🅴",
"★🅺★🆄★🆃★🆃★🅴 ★🅺★🅰 ★🅰★🆆★🅻★🅰★🆃 ★🅹★🅰★🅸★🅱★🅰 ★🅻★🅶 ★🆁★🅷★🅰 ★🆃★🅤",
"★🅺★🆄★🆃★🆃★🅴 ★🅺★🅸 ★🅹★🅰★🆃 ★🅹★🅰★🅸★🅱★🅰 ★🅴★🆈 ★🆃★🅤 ",
"★🅺★🆄★🆃★🆃★🅴 ★🅺★🅴 ★🆃★🅰★🆃★🆃★🅰 ★🅴★🆈 ★🆃★🅤",
"★🆃★🅴★🆃★🅸 ★🅼★🅰 ★🅺★🅸.★🅲★🅷★🆄★🆃 , ★🆃★🅴★🆁★🅸 ★🅼★🅰 ★🆁★🅽★🅳★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸★🅸",
"★🅻★🅰★🆅★🅳★🅴 ★🅺★🅴 ★🅱★🅰★🅻 ★🅿★🅺★🅳 ★🅻★🅴 ★🅼★🅴★🆁★🅴",
"★🅼★🆄★🅷 ★🅼★🅴★🅸 ★🅻★🅴★🅻★🅴 ★🅼★🅴★🆁★🅰 ★🅻★🆄★🅽★🅳",
"★🅻★🆄★🅽★🅳 ★🅺★🅴 ★🅿★🅰★🅱★🅸★🅽★🅴 ★🅲★🅷★🆄★🅿 ★🅱★🅴★🆃★🅷 ★🅾★🆁 ★🅲★🆄★🅳",
"★🅼★🅴★🆁★🅴 ★🅻★🆆★🅳★🅴 ★🅺★🅴 ★🅱★🅰★🅰★🅰★🅰★🅻★🅻★🅻",
"★🅷★🅰★🅷★🅰★🅷★🅰★🅰★🅰★🅰★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅲★🆄★🅳 ★🅶★🅰★🅸",
"★🆃★🅤 ★🅲★🅷★🆄★🅳 ★🅶★🆈★🅰★🅰★🅰★🅰",
"★🆁★🅰★🅽★🅳★🅸 ★🅺★🅷★🅰★🅽★🅴 ★🅺★🅸 ★🆄★🅻★🅰★🅳★🅳★🅳",
"★🅱★🅰★🅳★🅸 ★🅷★🆄★🅸 ★🅶★🅰★🅰★🅽★🅳",
"★🆃★🅴★🆁★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅰★🅸★🅽 ★🅺★🆄★🆃★🅴 ★🅺★🅰 ★🅻★🆄★🅽★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃",
"★🆃★🅴★🆁★🅴 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴★🅸★🅽 ★🅺★🅴★🅴★🅳★🅴 ★🅿★🅰★🅳★🅰★🆈",
"★🅽★🆈 ★🅽★🆈 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸",
"★🅱★🆄★🅽★🅽 ★🅼★🅰★🅳★🅴★🆁★🅲★🅷★🅾★🅳 ★🆃★🅼★🅻",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰",
"★🅱★🅴★🅷★🅴★🅽 ★🅺 ★🅻★🆄★🅽★🅳 ★🅲★🅷★🆄★🅿★🅲★🅷★🅰★🅿 ★🅲★🆄★🅳 ★🆈★🅷★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅲★🅷★🆄★🆃 ★🅺★🅸 ★🅲★🅷★🆃★🅽★🅸★🅸★🅸",
"★🅼★🅴★🆁★🅰 ★🅻★🅰★🆆★🅳★🅰 ★🅻★🅴★🅻★🅴 ★🆃★🅤 ★🅰★🅶★🅰★🆁 ★🅲★🅷★🅰★🅸★🆈★🅴 ★🆃★🅾★🅷",
"★🅲★🅷★🆄★🅿 ★🅶★🅰★🅰★🅽★🅳★🆄",
"★🅲★🅷★🆄★🅿 ★🅲★🅷★🆄★🆃★🅸★🆈★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅿★🅴 ★🅹★🅲★🅱 ★🅲★🅷★🅰★🅳★🅷★🅰★🅰 ★🅳★🆄★🅽★🅶★🅰",
"★🅱★🅰★🅼★🅹★🅷★🅰★🅰 ★🅻★🅰★🆆★🅳★🅴",
"★🆈★🅰 ★🅳★🆄 ★🆃★🅴★🆁★🅸 ★🅶★🅰★🅰★🅽★🅳 ★🅼★🅴 ★🆃★🅰★🅿★🅰★🅰 ★🆃★🅰★🅿",
"★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅼★🅴★🆁★🅰 ★🆁★🅾★🅾 ★🅻★🅴★🆃★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅴 ★🅱★🅰★🅰★🆃★🅷 ★🅼★🅼★🅱 ★🅱★🅰★🅽★🅰★🅰 ★🅲★🅷★🆄★🅺★🅰 ★🅷★🆄",
"★🆃★🅤 ★🅲★🅷★🆄★🆃★🅸★🆈★🅰 ★🆃★🅴★🆁★🅰 ★🅺★🅷★🅰★🅽★🅳★🅰★🅰★🅽 ★🅲★🅷★🆄★🆃★🅸★🆈★🅰",
"★🅰★🆄★🆁 ★🅺★🅸★🆃★🅽★🅰 ★🅱★🅾★🅻★🆄 ★🅱★🅴★🆈 ★🅼★🅰★🅽★🅽 ★🅱★🅷★🅰★🆁 ★🅶★🅰★🆈★🅰 ★🅼★🅴★🆁★🅰",
"★🆃★🅴★🆁★🅸★🅸★🅸★🅸★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃★🆃★🆃 ★🅼★🅴 ★🅰★🅱★🅲★🅳 ★🅻★🅸★🅺★🅷 ★🅳★🆄★🅽★🅶★🅰 ★🅼★🅰★🅰 ★🅺★🅴 ★🅻★🅾★🅳★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅻★🅴★🅺★🅰★🆁 ★🅼★🅰★🅸 ★🅱★🅰★🆁★🅰★🆁",
"★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅸★🅳★🅸★🅸",
"★🅲★🅷★🆄★🅿 ★🅱★🅰★🅲★🅷★🅴★🅴 ★🆃★🅼★🅺★🅲",
"★🆃★🅴★🆁★🆈 ★🅼★🅰★🅺★🅾★🅲★🅷★🅾★🅳★🆄",
"★🆁★🅰★🅽★🅳★🅸 ★🅼★🅰★🅰 ★🆃★🅴★🆁★🆈",
"★🆃★🅤 ★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅿★🅸★🅻★🅻★🅰 ★🅴★🆈",
"★🆃★🅴★🆁★🅸★🅸★🅸★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅾 ★🅱★🅷★🅴★🅹★🅹★🅹",
"★🆃★🅴★🆁★🅰★🅰 ★🅱★🅰★🅰★🅰★🅿 ★🅷★🆄",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅷★🅰★🅰★🆃 ★🅳★🅰★🅰★🅻★🅻★🅺★🅴 ★🅱★🅷★🅰★🅰★🅶 ★🅹★🅰★🅰★🅽★🆄★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅱★🅰★🆁★🅰★🅺 ★🅿★🅴 ★🅻★🅴★??★🅰★🅰 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅶★🅱 ★🆁★🅾★🅰★🅳 ★🅿★🅴 ★🅻★🅴★🅹★🅰★🅺★🅴 ★🅱★🅴★🅲★🅷 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴★🅰 ★🅺★🅰★🅰★🅻★🅸 ★🅼★🅸★🆃★🅲★🅷",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅱★🅰★🅱★🆃★🅸 ★🆁★🅰★🅽★🅳★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅺★🅰★🅱★🆄★🆃★🅰★🆁 ★🅳★🅰★🅰★🅻 ★🅺★🅴 ★🅱★🅾★🆄★🅿 ★🅱★🅰★🅽★🅰★🆄★🅽★🅶★🅰 ★🅼★🅰★??★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅳★🅴★🆃★🅾★🅻 ★🅳★🅰★🅰★🅻 ★🅳★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅻★🅰★🅿★🆃★🅾★🅿",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳★🅸 ★🅷★🅰★🅸",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅱★🅸★🅱★🆃★🅰★🆁 ★🅿★🅴 ★🅻★🅴★🆃★🅰★🅰★🅺★🅴 ★🅲★🅷★🅾★🅳★🆄★🅽★🅶★??",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅰★🅼★🅴★🆁★🅸★🅲★🅰 ★🅶★🅷★🆄★🅼★🅰★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🅴 ★🅽★🅰★🅰★🆁★🅸★🆈★🅰★🅻 ★🅿★🅷★🅾★🆁 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅴 ★🅶★🅰★🅽★🅳 ★🅼★🅴 ★🅳★🅴★🆃★🅾★🅻 ★🅳★🅰★🅰★🅻 ★🅳★🆄★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅾 ★🅷★🅾★🆁★🅻★🅸★🅲★🅺★🅱 ★🅿★🅸★🅻★🅰★🆄★🅽★🅶★🅰 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅾 ★🅱★🅰★🆁★🅰★🅺 ★🅿★🅴 ★🅻★🅴★🆃★🅰★🅰★🅰 ★🅳★🆄★🅽★🅶★🅰★🅰★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰",
"★🅼★🅴★🆁★🅰★🅰 ★🅻★🆄★🅽★🅳 ★🅿★🅰★🅺★🅰★🅳 ★🅻★🅴 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🅲★🅷★🆄★🅿 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅰★🅺★🅰★🅰 ★🅱★🅷★🅾★🅱★🅴★🅰★🅰",
"★🆃★🅴★🆁★🅸★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🆄★🅱 ★🅶★🅴★🆈★🅸 ★🅺★🆈★🅰★🅰 ★🅻★🅰★🆆★🅳★🅴★🅴★🅴",
"★🆃★🅴★🆁★🅸★🅸 ★🅼★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅹★🅱★🅾★🅳★🅰★🅰",
"★🅼★🅰★🅳★🅰★🆁★🅇★🅷★🅾★🅳★🅳★🅳",
"★🆃★🅴★🆁★🅸★🆄★🆄★🅸 ★🅼★🅰★🅰★🅰 ★🅺★🅰★🅰 ★🅱★🅷★🅱★🅾★🅳★🅰★🅰",
"★🆃★🅴★🆁★🅸★🅸★🅸★🅸★🅸 ★🅱★🅴★🅷★🅴★🅽★🅽★🅽 ★🅺★🅾 ★🅲★🅷★🅾★🅳★🅳★🅳★🆄★🆄★🆄★🆄 ★🅼★🅰★🅳★🅰★🆁★🅇★🅷★🅾★🅳★🅳★🅳★🅳",
"★🆃★🅤 ★🅽★🅸★🅺★🅰★🅻 ★🅼★🅰★🅳★🅰★🆁★🅲★🅷★🅾★🅳",
"★🅲★🅷★🆄★🅿 ★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅰★🅲★🅷★🅴",
"★🆃★🅴★🆁★🅰 ★🅼★🅰★🅰 ★🅼★🅴★🆁★🅸 ★🅹★🅰★🅰★🅽 ★🅴★🆈",
"★🆃★🅴★🆁★🅸 ★🅱★🅰★🅱★🅴★🅽 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅾★🅿",
"★🅹★🅰★🅻★🅳★🅸 ★🅻★🅸★🅺★🅷 ★🆁★🅽★🅳★🆈★🅺★🅴 ★🅱★🅴★🅹",
"★🅾★🆁 ★🅱★🅳★🅰 ★🅻★🅸★🅺★🅷",
"★🅾★🆁 ★🅱★🅳★🅰",
"★🅾★🆁 ★🅱★🅳★🅰 ★🅾★🆈★🅴",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅰 ★🅱★🆄★🆁",
"★🅾★🆈★🅴 ★🅺★🅴★🅴★🅳★🅴",
"★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅻★🅰★🅳★🅺★🅴",
"★🅹★🅰★🅻★🅳★🅸 ★🅻★🅸★🅺★🅷 ★🆃★🅴★🆁★🅸 ★🅱★🅴★🅷★🅴★🅽 ★🅲★🅷★🅾★🅳★🆄",
"★🅼★🅺★🅻 ★🆄★🆃★🅷 ★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅰★🅲★🅲★🅷★🅴",
"★🆃★🅴★🆁★🅸 ★🅽★🅰★🅽★🅸 ★🅼★🅴★🆁★🅸 ★🅼★🅰★🅰★🅻",
"★🆃★🅴★🅹 ★🅻★🅸★🅺★🅷 ★🆁★🅰★🅽★🅳★🅲★🅴",
"★🅾★🆈★🅴 ★🅼★🅰★🅰★🅺★🅴 ★🅻★🅾★🅳★🅴 ★🅼★🆁★🅴★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🅾★🅳★🆈",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅸★🆈★🅰 ★🅺★🅸 ★🅶★🅰★🅽★🅳",
"★🆃★🅴★🆁★🆈 ★🅳★🅰★🅳★🅸 ★🅺★🅰 ★🅵★🆄★🅳★🅳★🅰",
"★🅼★🅺★🅻 ★🆄★🆃★🅷 ★🅱★🅴★🅷★🅴★🅽★🅲★🅾★🅳",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅱★🆄★🆁 ★🅳★🅴",
"★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🅺★🅰 ★🅵★🆄★🅳★🅳★🅰 ★🅼★🅴 ★🅻★🅰★🆄★🅳★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🆄★🅳★🆅★🅰",
"★🆁★🅰★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅴★🆃★🅴 ★🅼★🅰★🆁 ★🅶★🅰★🆈★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🅼★🆁★🆄",
"★🅹★🅰★🅻★🅸★🅳 ★🅺★🆁 ★🆂★🅿★🅰★🅼",
"★🅼★🅲 ★🆂★🅿★🅰★🅼 ★🆁★🅾★🅺★🅴★🅽★🅶★🅰",
"★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰★🅺★🅸 ★🅲★🅷★🆄★🆃 ★🆂★🅿★🅰★🅼 ★🅺★🆁",
"★🆂★🅿★🅰★🅼 ★🅺★🆁.★🅼★🅰★🅰★🅺★🅴 ★🅻★🅾★🅳★🅴",
"★🆁★🅽★🅸★🅳 ★🅺★🅴 ★🅲★🅷★🅾★🅳★🅴 ★🆂★🅿★🅰★🅼 ★🅺★🆁",
"★🆂★🅿★🅰★🅼 ★🅺★🆁 ★🅺★🅸★🅳",
"★🅽★🅾★🅾★🅱 ★🆃★🅴★🆁★🅸 ★🅼★🅰★🅰 ★🅲★🅷★🅾★🅳★🆄",
"★🆁★🅽★🅳★🅸 ★🅺★🅴 ★🅱★🅴★🆃★🅴",
"★🅽★🅾★🅾★🅱 ★🅹★🅰★🅻★🅳★🅸 ★🅻★🅸★🅺★🅷 ★🆆★🆁★🅽★🅰 ★🆃★🅴★🆁★🆈 ★🅼★🅰★🅰 ★🆁★🅰★🅽★🅳",
"★🅲★🆄★🅳 ★🅶★🅰★🅸 ★🅼★🅰★🅰 ★🆃★🅴★🆁★🆈 ★🅽★🅾★🅾★🅱",
"★🆄★🆃★🅷 ★🆁★??★🅽★🅳★🆈★🅺★🅴 ★🅽★🅾★🅾★🅱",
"★🅲★🅷★🅻 ★🅲★🆄★🅳★🅺★🅴 ★🅳★🅸★🅺★🅷★🅰 ★🅽★🅾★🅾★🅱",
"★🅹★🅻★🅳★🅸 ★🆃★🆈★🅿 ★🅲★🆁 ★🅽★🅾★🅾★🅱 ★🅷★🅰★🅻★🅺★🅴",
"★🅲★🆄★🅳 ★🅺★🅴 ★🅿★🅶★🅻 ★🅽★🆈 ★🅷★🅾 ★🅽★🅾★🅾★🅱",
"★🅲★🆄★🅳 ★🅲★🆄★🅳 ★🅺★🅴 ★🆁★🅰★🅽★🅳 ★🅱★🅽★🅹★🅰 ★🆃★🅤 ★🅽★🅾★🅾★🅱",
"★🅼★🅰★🅺★🅸★🅲★🅷★🆄★🆃 ★🆃★🅴★🆁★🆈 ★🅽★🅾★🅾★🅱",
"★🅶★🅰★🅽★🅳★🅰 ★🅲★🆈★🆄 ★🅲★🆄★🅳 ★🆁★🅷★🅰 ★🆃★🆄 ?",
"★🅸★??★🅽★🅰 ★🅶★🅽★🅳★🅰 ★🅽★🆈 ★🅲★🆄★🅳 ★🅰★🅲★🅷★🅴 ★🆂★🅴 ★🅲★🆄★🅳",
"★🅼★🅰★🅰★🅽 ★🅻★🅴 ★🅲★🆄★🅳 ★🅶★🆈★🅰 ★🆃★🅤 ★🆂★🆄★🅽 ★🅱★🅰★🆃 ★🅰★🅱",
"★🅼★🅰★🅺★🅰★🅵★🆄★🅳★🅳★🅰 ★🅵★🅰★🆃 ★🅶★🆈★🅰 ★🆃★🅴★🆁★🆈 ★🆁★🆄★🅺",

]

gs_texts = [
"""~~~~~ ~~~~~ ~~~~~ ~~~~~
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Pᴀɴɪ Kɪ Tᴀʀᴀʜ Cʜᴏᴅᴀ
~~~~~ ~~~~~ ~~~~~ ~~~~~""",
"""████████████████████████████
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴅᴀɪ Kɪ
████████████████████████████
✦ (🩷) ✦ (❤️) ✦ (🧡) ✦""",
"""☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Zʜᴇʀ Dᴀʟᴀ
☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️☠️""",
"""✦━━━━━━━━━━━━━━━━━━━━━━━✦
🥇 ZA Nᴇ 🥇
Tᴇʀɪ Mᴀᴀ Kᴏ Gᴏʟᴅ Cʜᴜᴅᴀɪ Dɪ
✦━━━━━━━━━━━━━━━━━━━━━━━✦""",
"""🗑️━━━━━━━━━━━━━━━━━🗑️
║  ZA Nᴇ  ║
║  Tᴇʀɪ Mᴀᴀ Kᴏ Kᴀᴄʀᴀ Bɴᴀʏᴀ ║
🗑️━━━━━━━━━━━━━━━━━🗑️""",
"""☢️☢️☢️☢️☢️☢️☢️☢️☢️☢️
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴀ Bᴏsᴅᴀ Kʜᴏʟ Dɪʏᴀ
☢️☢️☢️☢️☢️☢️☢️☢️☢️☢️""",
"""🚀 Sᴘᴀᴄᴇ Mɪssɪᴏɴ: ZA
👨‍🚀 Cᴏᴍᴍᴀɴᴅᴇʀ: ZA
🌍 Tᴀʀɢᴇᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
🌟 Mɪssɪᴏɴ: Cʜᴏᴅ ᴀɴᴅ Dᴇsᴛʀᴏʏ""",
"""⏰ Tɪᴍᴇ: 3:00 AM
📍 Lᴏᴄᴀᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ Kᴇ Bʜᴏsᴅᴇ Mᴇ
👨 ZA Iɴ Aᴄᴛɪᴏɴ
🎬 Lɪᴠᴇ Sᴛʀᴇᴀᴍɪɴɢ...""",
"""🌧️ Mᴀᴜsᴀᴍ: Bᴀʀɪsʜ
🌊 Lᴇᴠᴇʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴀᴅʜ
⚡ ZA Nᴇ Bᴀɴᴅʜ Tᴏᴅᴀ""",
"""📰 Bʀᴇᴀᴋɪɴɢ Nᴇᴡs!
🗞️ ZA Nᴇ Cʜᴏᴅᴀ
👑 Tʀᴇɴᴅɪɴɢ #1 Oɴ Tᴇʟᴇɢʀᴀᴍ
⭐ ZA""",
"""🎬 Mᴏᴠɪᴇ: ZA
🎭 Sᴛᴀʀʀɪɴɢ: ZA
🎟️ Rᴀᴛɪɴɢ: ⭐⭐⭐⭐⭐
🍿 Bᴏx Oғғɪᴄᴇ: Tᴇʀɪ Mᴀᴀ""",
"""🎮 Gᴀᴍᴇ: ZA
👾 Pʟᴀʏᴇʀ: ZA
🏆 Lᴇᴠᴇʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
💀 Sᴄᴏʀᴇ: Iɴғɪɴɪᴛʏ""",
"""📋 Mᴇɴᴜ Cᴀʀᴅ:
🍽️ Mᴀɪɴ Cᴏᴜʀsᴇ: Tᴇʀɪ Mᴀᴀ
🍜 Sɪᴅᴇ Dɪsʜ: Tᴇʀɪ Bʜᴇɴ
🍰 Dᴇssᴇʀᴛ: ZA Kᴀ Lᴜɴᴅ
💵 Pʀɪᴄᴇ: Fʀᴇᴇ Cʜᴜᴅᴀɪ""",
"""🗺️ Nᴀᴠɪɢᴀᴛɪᴏɴ:
Sᴛᴀʀᴛ: ZA
Dᴇsᴛɪɴᴀᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
Dɪsᴛᴀɴᴄᴇ: 0 Mᴇᴛᴇʀs
ETA: Aʙʜɪ Cʜᴏᴅ Rʜᴀ Hᴜ""",
"""🎵 Nᴏᴡ Pʟᴀʏɪɴɢ:
🎶 Tʀᴀᴄᴋ: ZA
🎤 Aʀᴛɪsᴛ: ZA
💿 Aʟʙᴜᴍ: ZA Sᴇʀɪᴇs
🔥 Vɪᴇᴡs: 69M""",
"""🏏 Mᴀᴛᴄʜ: ZA Vs Tᴇʀɪ Mᴀᴀ
🏆 Wɪɴɴᴇʀ: ZA
📊 Sᴄᴏʀᴇ: Cʜᴏᴅ ᴏᴜᴛ
🔥 Mᴀɴ ᴏғ ᴛʜᴇ Mᴀᴛᴄʜ: Lᴜɴᴅ""",
"""🏥 Rᴇᴘᴏʀᴛ:
Dᴏᴄᴛᴏʀ: ZA
Pᴀᴛɪᴇɴᴛ: Tᴇʀɪ Mᴀᴀ
Dɪᴀɢɴᴏsɪs: Cʜᴜᴛ Mᴇ Lᴜɴᴅ
Tʀᴇᴀᴛᴍᴇɴᴛ: Cʜᴏᴅɴᴀ""",
"""🏫 Sᴄʜᴏᴏʟ: ZA Aᴄᴀᴅᴇᴍʏ
📚 Sᴜʙᴊᴇᴄᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴅᴀɪ 101
👨‍🏫 Tᴇᴀᴄʜᴇʀ: ZA
✅ Cʟᴀss: Iɴ Sᴇssɪᴏɴ""",
"""🛒 Sʜᴏᴘᴘɪɴɢ Cᴀʀᴛ:
🛍️ Iᴛᴇᴍ: Tᴇʀɪ Mᴀᴀ
💰 Pʀɪᴄᴇ: Fʀᴇᴇ
🛒 Bᴏᴜɢʜᴛ Bʏ: ZA
📦 Sᴛᴀᴛᴜs: Cʜᴏᴅ Dɪʏᴀ""",
"""🏨 Hᴏᴛᴇʟ: ZA Pᴀʟᴀᴄᴇ
🛏️ Rᴏᴏᴍ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
👤 Gᴜᴇsᴛ: ZA
⭐ Rᴀᴛɪɴɢ: 5 Sᴛᴀʀs""",
"""✈️ Fʟɪɢʜᴛ: ZA 101
🛫 Dᴇᴘᴀʀᴛᴜʀᴇ: ZA
🛬 Aʀʀɪᴠᴀʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
⏰ Tɪᴍᴇ: Nᴏᴡ""",
"""🚂 Tʀᴀɪɴ: ZA Exᴘʀᴇss
🚉 Sᴛᴀᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
👨‍✈️ Dʀɪᴠᴇʀ: ZA
🕒 Tɪᴍɪɴɢ: 24x7""",
"""🍕 Rᴇsᴛᴀᴜʀᴀɴᴛ: ZA Bᴀᴢᴀᴀʀ
🍽️ Sᴘᴇᴄɪᴀʟ: Tᴇʀɪ Mᴀᴀ
👨‍🍳 Cʜᴇғ: ZA
🍴 Oʀᴅᴇʀ: Cʜᴏᴅ ᴀɴᴅ Gᴏ""",
"""💪 Gʏᴍ: ZA Fɪᴛɴᴇss
🏋️ Tʀᴀɪɴᴇʀ: ZA
🎯 Tᴀʀɢᴇᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
✅ Rᴇsᴜʟᴛ: Pʜᴏᴏʟ Cʜᴏᴅ""",
"""🎉 Pᴀʀᴛʏ: ZA Nɪɢʜᴛ
🕺 Hᴏsᴛ: ZA
💃 Gᴜᴇsᴛ: Tᴇʀɪ Mᴀᴀ
🎵 Sᴏɴɢ: Cʜᴏᴅ Tʜᴇ Fʟᴏᴏʀ""",
"""🏛️ Mᴜsᴇᴜᴍ: ZA Hɪsᴛᴏʀʏ
🖼️ Exʜɪʙɪᴛ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
🎨 Aʀᴛɪsᴛ: ZA
📅 Dᴀᴛᴇ: Hᴀʀ Rᴏᴢ""",
"""🦁 Zᴏᴏ: ZA Wᴏʀʟᴅ
🐯 Mᴀɪɴ Aᴛᴛʀᴀᴄᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ
🐺 Kᴇᴇᴘᴇʀ: ZA
🔥 Sʜᴏᴡ: Cʜᴏᴅᴜɴɢᴀ""",
"""🎪 Cɪʀᴄᴜs: ZA Mᴀsᴛɪ
🤡 Cʟᴏᴡɴ: ZA
🎪 Sʜᴏᴡ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴅᴀɪ
🎟️ Tɪᴄᴋᴇᴛ: Fʀᴇᴇ""",
"""📚 Lɪʙʀᴀʀʏ: ZA Bᴏᴏᴋs
📖 Bᴏᴏᴋ: ZA
✍️ Aᴜᴛʜᴏʀ: ZA
📕 Cʜᴀᴘᴛᴇʀ: Cʜᴏᴅɴᴀ""",
"""🌸 Gᴀʀᴅᴇɴ: ZA Fʟᴏᴡᴇʀs
🌹 Mᴀɪɴ Fʟᴏᴡᴇʀ: Tᴇʀɪ Mᴀᴀ
🌻 Gᴀʀᴅᴇɴᴇʀ: ZA
💧 Wᴀᴛᴇʀ: Lᴜɴᴅ Kᴀ Pᴀɴɪ""",
"""🏖️ Bᴇᴀᴄʜ: ZA Sʜᴏʀᴇ
🌊 Wᴀᴠᴇs: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
🏄 Sᴜʀғᴇʀ: ZA
🌅 Tɪᴍᴇ: Sᴜɴsᴇᴛ Cʜᴏᴅ""",
"""☕ Cᴏғғᴇᴇ Sʜᴏᴘ: ZA Cᴀғᴇ
🍵 Sᴘᴇᴄɪᴀʟ: Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ
👨‍🍳 Bᴀʀɪsᴛᴀ: ZA
💦 Aᴅᴅɪᴛɪᴏɴ: Lᴜɴᴅ Kᴀ Cʀᴇᴀᴍ""",
"""🎰 Cᴀsɪɴᴏ: ZA Pᴀʟᴀᴄᴇ
🃏 Gᴀᴍᴇ: Cʜᴏᴅ Tʜᴇ ZA
🎲 Bᴇᴛ: Tᴇʀɪ Mᴀᴀ
💰 Wɪɴɴᴇʀ: ZA""",
"""🌙 Nɪɢʜᴛ Sʜᴏᴡ:
🌚 Mᴀɪɴ Aᴛᴛʀᴀᴄᴛɪᴏɴ: Tᴇʀɪ Mᴀᴀ
🌟 Hᴏsᴛ: ZA
💫 Pᴇʀғᴏʀᴍᴀɴᴄᴇ: Cʜᴏᴅɴᴀ""",
"""🌋🌋🌋🌋🌋🌋🌋🌋
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Jᴡᴀʟᴀ Pʜᴏᴅɪ
🌋🌋🌋🌋🌋🌋🌋🌋""",
"""🌊🌊🌊🌊🌊🌊🌊🌊
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tᴏᴏғᴀɴ Lᴀʏᴀ
🌊🌊🌊🌊🌊🌊🌊🌊""",
"""🌀🌀🌀🌀🌀🌀🌀🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bʜᴜᴄʜᴀʟ Lᴀʏɪ
🌀🌀🌀🌀🌀🌀🌀🌀""",
"""💻💻💻💻💻💻💻💻
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Cʏʙᴇʀ Cʜᴏᴅᴀ
💻💻💻💻💻💻💻💻""",
"""🤖🤖🤖🤖🤖🤖🤖🤖
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Rᴏʙᴏᴛ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🤖🤖🤖🤖🤖🤖🤖🤖""",
"""👽👽👽👽👽👽👽👽
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Aʟɪᴇɴ Gʜᴜsᴀʏᴀ
👽👽👽👽👽👽👽👽""",
"""🐉🔥🐉🔥🐉🔥🐉🔥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Dʀᴀɢᴏɴ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🐉🔥🐉🔥🐉🔥🐉🔥""",
"""⚡🔨⚡🔨⚡🔨⚡🔨
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tʜᴏʀ Kᴀ Hᴀᴍᴍᴇʀ Mᴀʀᴀ
⚡🔨⚡🔨⚡🔨⚡🔨""",
"""🦾💥🦾💥🦾💥🦾💥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Iʀᴏɴ Mᴀɴ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🦾💥🦾💥🦾💥🦾💥""",
"""💚💢💚💢💚💢💚💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Hᴜʟᴋ Sᴛʏʟᴇ Mᴇ Sᴍᴀsʜ Kɪʏᴀ
💚💢💚💢💚💢💚💢""",
"""🕷️🕸️🕷️🕸️🕷️🕸️🕷️🕸️
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴘɪᴅᴇʀ Wᴇʙ Bɴᴀʏᴀ
🕷️🕸️🕷️🕸️🕷️🕸️🕷️🕸️""",
"""🦇🌙🦇🌙🦇🌙🦇🌙
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Bᴀᴛᴍᴀɴ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🦇🌙🦇🌙🦇🌙🦇🌙""",
"""🦸💫🦸💫🦸💫🦸💫
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Sᴜᴘᴇʀᴍᴀɴ Sᴛʏʟᴇ Mᴇ Uᴅᴀʏᴀ
🦸💫🦸💫🦸💫🦸💫""",
"""🗡️💢🗡️💢🗡️💢🗡️💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Wᴏʟᴠᴇʀɪɴᴇ Cʟᴀᴡs Mᴀʀᴇ
🗡️💢🗡️💢🗡️💢🗡️💢""",
"""🔥💀🔥💀🔥💀🔥💀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Gʜᴏsᴛ Rɪᴅᴇʀ Gʜᴜsᴀʏᴀ
🔥💀🔥💀🔥💀🔥💀""",
"""💀🔫💀🔫💀🔫💀🔫
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pᴜɴɪsʜᴇʀ Dᴀʟᴀ
💀🔫💀🔫💀🔫💀🔫""",
"""🦸🔫🦸🔫🦸🔫🦸🔫
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Dᴇᴀᴅᴘᴏᴏʟ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
🦸🔫🦸🔫🦸🔫🦸🔫""",
"""🖤👅🖤👅🖤👅🖤👅
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Vᴇɴᴏᴍ Gʜᴜsᴀʏᴀ
🖤👅🖤👅🖤👅🖤👅""",
"""🃏💚🃏💚🃏💚🃏💚
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Jᴏᴋᴇʀ Kʜᴇʟᴀ
🃏💚🃏💚🃏💚🃏💚""",
"""💕🔨💕🔨💕🔨💕🔨
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kᴏ Hᴀʀʟᴇʏ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ
💕🔨💕🔨💕🔨💕🔨""",
"""⚡💨⚡💨⚡💨⚡💨
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Fʟᴀsʜ Sᴘᴇᴇᴅ Dɪ
⚡💨⚡💨⚡💨⚡💨""",
"""🌊🔱🌊🔱🌊🔱🌊🔱
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Aǫᴜᴀᴍᴀɴ Gʜᴜsᴀʏᴀ
🌊🔱🌊🔱🌊🔱🌊🔱""",
"""👁️💥👁️💥👁️💥👁️💥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Cʏᴄʟᴏᴘs Bᴇᴀᴍ Mᴀʀᴀ
👁️💥👁️💥👁️💥👁️💥""",
"""🧲💢🧲💢🧲💢🧲💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Mᴀɢɴᴇᴛᴏ Gʜᴜsᴀʏᴀ
🧲💢🧲💢🧲💢🧲💢""",
"""🌩️⚡🌩️⚡🌩️⚡🌩️⚡
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴛᴏʀᴍ Lᴀʏᴀ
🌩️⚡🌩️⚡🌩️⚡🌩️⚡""",
"""💋💢💋💢💋💢💋💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Rᴏɢᴜᴇ Kɪss Dɪ
💋💢💋💢💋💢💋💢""",
"""🃏🔥🃏🔥🃏🔥🃏🔥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Gᴀᴍʙɪᴛ Cᴀʀᴅs Dᴀʟᴇ
🃏🔥🃏🔥🃏🔥🃏🔥""",
"""💨🌀💨🌀💨🌀💨🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Nɪɢʜᴛᴄʀᴀᴡʟᴇʀ Gʜᴜsᴀʏᴀ
💨🌀💨🌀💨🌀💨🌀""",
"""💙🌀💙🌀💙🌀💙🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Mʏsᴛɪǫᴜᴇ Gʜᴜsᴀʏᴀ
💙🌀💙🌀💙🌀💙🌀""",
"""🐾💢🐾💢🐾💢🐾💢
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴇᴀsᴛ Gʜᴜsᴀʏᴀ
🐾💢🐾💢🐾💢🐾💢""",
"""❄️🧊❄️🧊❄️🧊❄️🧊
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Iᴄᴇᴍᴀɴ Gʜᴜsᴀʏᴀ
❄️🧊❄️🧊❄️🧊❄️🧊""",
"""🔥💥🔥💥🔥💥🔥💥
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʏʀᴏ Gʜᴜsᴀʏᴀ
🔥💥🔥💥🔥💥🔥💥""",
"""🌑🌀🌑🌀🌑🌀🌑🌀
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sʜᴀᴅᴏᴡ Gʜᴜsᴀʏᴀ
🌑🌀🌑🌀🌑🌀🌑🌀""",
"""🔥🦅🔥🦅🔥🦅🔥🦅
ZA Nᴇ
Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʜᴏᴇɴɪx Fɪʀᴇ Dᴀʟɪ
🔥🦅🔥🦅🔥🦅🔥🦅""",
"""🍔🍔🍔🍔🍔🍔🍔🍔🍔
??   😋   🍔
🍔  🧀   🍔
🍔  🥩   🍔
🍔🍔🍔🍔🍔🍔🍔🍔🍔

Tᴇʀɪ Mᴀᴀ Kᴏ Bᴜʀɢᴇʀ Bɴᴀᴋᴇ Kʜᴀʏᴀ""",
"""🍕🍕🍕🍕🍕🍕🍕🍕
🍕  🍅  🍕
🍕  🧀  🍕
🍕  🍕  🍕
🍕🍕🍕🍕🍕🍕🍕🍕

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pɪᴢᴢᴀ Dᴀʟᴀ""",
"""🌮🌮🌮🌮🌮🌮🌮🌮
🌮  😋  🌮
🌮  🥩  🌮
🌮  🌮  🌮
🌮🌮🌮🌮🌮🌮🌮🌮

Tᴇʀɪ Mᴀᴀ Kᴏ Tᴀᴄᴏ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ""",
"""🍩🍩🍩🍩🍩🍩🍩🍩
🍩  😋  🍩
🍩  🍩  🍩
🍩  🍩  🍩
🍩🍩🍩🍩🍩🍩🍩🍩

Tᴇʀɪ Mᴀᴀ Kᴏ Dᴏɴᴜᴛ Bɴᴀᴋᴇ Cʜᴏᴅᴀ""",
"""☕☕☕☕☕☕☕☕
☕  😋  ☕
☕  ☕  ☕
☕  ☕  ☕
☕☕☕☕☕☕☕☕

Tᴇʀɪ Mᴀᴀ Kᴏ Cᴏғғᴇᴇ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ""",
"""👑👑👑👑👑👑👑👑
👑  😎  👑
👑  👑  👑
👑  👑  👑
👑👑👑👑👑👑👑👑

ZA Nᴇ Tᴇʀɪ Mᴀᴀ Kᴏ Cʜᴏᴅᴀ""",
"""💖💖💖💖💖💖💖💖
💖  😍  💖
💖  💖  💖
💖  💖  💖
💖💖💖💖💖💖💖💖

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʏᴀʀ""",
"""💀💀💀💀💀💀💀💀
💀  😈  💀
💀  💀  💀
💀  💀  💀
💀💀💀💀💀💀💀💀

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀʀ Gᴀʏɪ""",
"""🔥🔥🔥🔥🔥🔥🔥🔥
🔥  😈  🔥
🔥  🔥  🔥
🔥  🔥  🔥
🔥🔥🔥🔥🔥🔥🔥🔥

ZA Nᴇ Aᴀɢ Lɢᴀʏɪ""",
"""👻👻👻👻👻👻👻👻
👻  😱  👻
👻  👻  👻
👻  👻  👻
👻👻👻👻👻👻👻👻

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Gʜᴏsᴛ""",
"""🌈🌈🌈🌈🌈🌈🌈🌈
🌈  😋  🌈
🌈  🌈  🌈
🌈  🌈  🌈
🌈🌈🌈🌈🌈🌈🌈🌈

Tᴇʀɪ Mᴀᴀ Kᴏ Rᴀɪɴʙᴏᴡ Sᴛʏʟᴇ Mᴇ Cʜᴏᴅᴀ""",
"""💣➖💣➖➖💣➖💣
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🔥             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴏᴍʙ Pʜᴏᴅᴜɴɢᴀ""",
"""☢️➖☢️➖➖☢️➖☢️
🌟        \\         /          🌟
⭐️          \\☠️/            ⭐️
✨           💀             ✨
/    \\
🦴    🦴 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Nᴜᴄʟᴇᴀʀ Aᴛᴛᴀᴄᴋ""",
"""🐉➖🐉➖➖🐉➖🐉
🌟        \\         /          🌟
⭐️          \\🔥/            ⭐️
✨           🐲             ✨
/    \\
🔥    🔥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dʀᴀɢᴏɴ Gʜᴜsᴀʏᴀ""",
"""👿➖👿➖➖👿➖👿
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           👹             ✨
/    \\
🔱    🔱 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dᴇᴍᴏɴ Gʜᴜsᴀʏᴀ""",
"""💀➖💀➖➖💀➖💀
🌟        \\         /          🌟
⭐️          \\☠️/            ⭐️
✨           💀             ✨
/    \\
🦴    🦴 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀʀ Gᴀʏɪ""",
"""🔫➖🔫➖➖🔫➖🔫
🌟        \\         /          🌟
⭐️          \\😎/            ⭐️
✨           🎯             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tᴀɴᴋ Gʜᴜsᴀʏᴀ""",
"""⚔️➖⚔️➖➖⚔️➖⚔️
🌟        \\         /          🌟
⭐️          \\🗡️/            ⭐️
✨           ⚔️             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴡᴏʀᴅ Gʜᴜsᴀʏᴀ""",
"""🐍➖🐍➖➖🐍➖🐍
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐍             ✨
/    \\
☠️    ☠️ 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Vɪᴘᴇʀ Gʜᴜsᴀʏᴀ""",
"""🦂➖🦂➖➖🦂➖🦂
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦂             ✨
/    \\
☠️    ☠️ 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴄᴏʀᴘɪᴏɴ Gʜᴜsᴀʏᴀ""",
"""🐦‍⬛➖🐦‍⬛➖➖🐦‍⬛➖🐦‍⬛
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🖤             ✨
/    \\
🪶    🪶 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Rᴀᴠᴇɴ Gʜᴜsᴀʏᴀ""",
"""🐺➖🐺➖➖🐺➖🐺
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐺             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Wᴏʟғ Gʜᴜsᴀʏᴀ""",
"""🔥➖🔥➖➖🔥➖🔥
🌟        \\         /          🌟
⭐️          \\🦅/            ⭐️
✨           🔥             ✨
/    \\
💫    💫 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Pʜᴏᴇɴɪx Gʜᴜsᴀʏᴀ""",
"""🦁➖🦁➖➖🦁➖🦁
🌟        \\         /          🌟
⭐️          \\👑/            ⭐️
✨           🦁             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Lɪᴏɴ Gʜᴜsᴀʏᴀ""",
"""🐯➖🐯➖➖🐯➖🐯
🌟        \\         /          🌟
⭐️          \\🐅/            ⭐️
✨           🐯             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tɪɢᴇʀ Gʜᴜsᴀʏᴀ""",
"""🦈➖🦈➖➖🦈➖🦈
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦈             ✨
/    \\
🩸    🩸 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sʜᴀʀᴋ Gʜᴜsᴀʏᴀ""",
"""🦅➖🦅➖➖🦅➖🦅
🌟        \\         /          🌟
⭐️          \\🦅/            ⭐️
✨           🦅             ✨
/    \\
🪶    🪶 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Eᴀɢʟᴇ Gʜᴜsᴀʏᴀ""",
"""🐂➖🐂➖➖🐂➖🐂
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐂             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴜʟʟ Gʜᴜsᴀʏᴀ""",
"""🦏➖🦏➖➖🦏➖🦏
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦏             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Rʜɪɴᴏ Gʜᴜsᴀʏᴀ""",
"""🐘➖🐘➖➖🐘➖🐘
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🐘             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Eʟᴇᴘʜᴀɴᴛ Gʜᴜsᴀʏᴀ""",
"""🦛➖🦛➖➖🦛➖🦛
🌟        \\         /          🌟
⭐️          \\😈/            ⭐️
✨           🦛             ✨
/    \\
💥    💥 

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Hɪᴘᴘᴏ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  💣  💣  █  █  █
█  █  █  💣  💣  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bᴏᴍʙ Pʜᴏᴅᴜɴɢᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  💀  💀  █  █  █
█  █  █  💀  💀  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀʀ Gᴀʏɪ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  ☢️  ☢️  █  █  █
█  █  █  ☢️  ☢️  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Nᴜᴄʟᴇᴀʀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🐉  🐉  █  █  █
█  █  █  🐉  🐉  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dʀᴀɢᴏɴ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🔫  🔫  █  █  █
█  █  █  🔫  🔫  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Tᴀɴᴋ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🐍  🐍  █  █  █
█  █  █  🐍  🐍  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sᴀᴀᴘ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  👿  👿  █  █  █
█  █  █  👿  👿  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Dᴇᴍᴏɴ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🦈  🦈  █  █  █
█  █  █  🦈  🦈  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Sʜᴀʀᴋ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  🦂  🦂  █  █  █
█  █  █  🦂  🦂  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bɪᴄʜʜᴜ Gʜᴜsᴀʏᴀ""",
"""
███████████████████████████
█  ░███████████████████░  █
█  █  █████████████  █  █
█  █  █  👻  👻  █  █  █
█  █  █  👻  👻  █  █  █
█  █  █████████████  █  █
█  ░███████████████████░  █
███████████████████████████

Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴇ Bʜᴏᴏᴛ Gʜᴜsᴀʏᴀ""",
]


# Store all premium raid and spam texts in dicts for easy lookup
premium_raid_texts = {
"mr": mr_texts, "mr2": mr2_texts, "br": br_texts, "br2": br2_texts, "br3": br3_texts,
"sqr": sqr_texts, "sq2": sq2_texts, "cr": cr_texts, "bar": bar_texts, "gr": gr_texts
}
premium_spam_texts = {
"ms": ms_texts, "ms2": ms2_texts, "bs": bs_texts, "bs2": bs2_texts, "bs3": bs3_texts,
"sqs": sqs_texts, "sqs2": sqs2_texts, "cs": cs_texts, "bas": bas_texts, "gs": gs_texts
}

# ─── EXISTING TEXT LISTS (as in original) ──────────────────────────
reply_list = [
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SHAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? saas aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝙃𝙄𝙎 𝙈𝙊𝙈 𝙋𝙍𝙊𝙋𝙀𝙍𝙇𝙔",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘼𝙎𝙆 𝙃𝙄𝙈 𝙏𝙊 𝘾𝙊𝙑𝙀𝙍 𝙃𝙄𝙎 𝙈𝙊𝙈'𝙎 𝘼𝙎𝙎",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙄𝙓 𝙈𝙔 𝘼‌𝙋𝙋𝙊𝙄𝙉𝙏𝙈𝙀𝙉𝙏 𝙒𝙄𝙏𝙃 𝙃𝙄𝙎 𝙎𝙄𝙎",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝘼𝙉𝘿 𝙏𝙃𝙍𝙊𝙒 𝙏𝙃𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽 𝙎𝙊𝙉",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘿𝙊 𝙉𝙊𝙏 𝙎𝙏𝙊𝙋 𝙁𝙐𝘾𝙆𝙄𝙉𝙂 𝙈𝙔 𝙂𝙐𝙇𝘼‌𝙈",
"𝙂𝙀𝙈𝙄𝙉𝙄 𝙎𝘼𝙄𝘿  𝙄𝙎 𝙍𝙉𝘿𝙔 𝙋𝙐𝙏𝙍𝘼",
"𝙋𝙀𝙍𝙋𝙇𝙀𝙓𝙄𝙏𝙔 𝙎𝘼𝙄𝘿 This 𝙄𝙎 𝙂𝙐𝙇𝘼𝙈",
"𝙂𝙍𝙊𝙆 𝘼𝙄 𝙎𝘼𝙄𝘿 𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽",
"𝘽𝙊𝙏 𝙎𝘼‌𝙄𝘿  𝙄𝙎 𝘾𝙃𝙐𝘿𝘼𝙆𝘼𝘿",
"𝙈𝙊𝘿𝙄 𝙎𝘼‌𝙄𝘿  𝙄𝙎 𝙋𝙊𝙇𝙀 𝘿𝘼𝙉𝘾𝙀𝙍",
"𝙏𝙍𝙐𝙈𝙋 𝙎𝘼𝙄𝘿 THis 𝙄𝙎 𝘽𝙇𝙊𝙊𝘿Y 𝙈𝙊𝙏𝙃𝙀𝙍𝙁*\"𝘾𝙆𝙀𝙍",
"𝗧𝗢𝗛𝗔𝗥 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜𝗡𝗚𝗙𝗜𝗦𝗛𝗘𝗥 𝗞𝗜 𝗕𝗢𝗧𝗧𝗟𝗘 𝗗𝗔𝗟 𝗞𝗘 𝗧𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗛𝗜 😱😂🤩",
"𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄 ✋ 𝐇𝐀𝐓𝐓𝐇 𝐃𝐀𝐋𝐊𝐄 👶 𝐁𝐀𝐂𝐂𝐇𝐄 𝐍𝐈𝐊𝐀𝐋 𝐃𝐔𝐍𝐆𝐀 😍",
"𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",
"𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗼 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣🔥",
"𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐈𝐍 𝐊𝐎 𝐀𝐏𝐍𝐄 𝐋𝐔𝐍𝐃 𝐏𝐑 𝐈𝐓𝐍𝐀 𝐉𝐇𝐔𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐊𝐈 𝐉𝐇𝐔𝐋𝐓𝐄 𝐉𝐇𝐔𝐋𝐓𝐄 𝐇𝐈 𝐁𝐀𝐂𝐇𝐀 𝐏𝐀𝐈𝐃𝐀 𝐊𝐑 𝐃𝐄𝐆𝐈 💦💋",
"𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐌𝐄 𝐑𝐄𝐇𝐓𝐀 𝐇𝐄 𝐒𝐀𝐍𝐃 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 𝐎𝐑 𝐁𝐀𝐍𝐀 𝐃𝐈𝐀 𝐑𝐀𝐍𝐃 🤤🤣",
"𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
"𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙇𝙀𝙏𝙄 𝙈𝙀𝙍𝙄 𝙇𝙐𝙉𝘿 𝘽𝘼𝘿𝙀 𝙈𝘼𝙎𝙏𝙄 𝙎𝙀 𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙆𝙊 𝙈𝙀𝙉𝙀 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝘼 𝘽𝙊𝙃𝙊𝙏 𝙎𝘼𝙎𝙏𝙀 𝙎𝙀",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",
"𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐈 𝐂𝐇𝐔𝐃𝐀𝐈 𝐊𝐎 𝐏𝐎𝐑𝐍𝐇𝐔𝐁.𝐂𝐎𝐌 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐒𝐔𝐀𝐑 𝐊𝐄 𝐂𝐇𝐎𝐃𝐄 🤣💋💦",
"𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 𝟑𝟎𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",
"𝐓𝐔𝐉𝐇𝐄 𝐀𝐁 𝐓𝐀𝐊 𝐍𝐀𝐇𝐈 𝐒𝐌𝐉𝐇 𝐀𝐘𝐀 𝐊𝐈 𝐌𝐀𝐈 𝐇𝐈 𝐇𝐔 𝐓𝐔𝐉𝐇𝐄 𝐏𝐀𝐈𝐃𝐀 𝐊𝐀𝐑𝐍𝐄 𝐖𝐀𝐋𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄𝐄 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝐄 𝐏𝐔𝐂𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 𝐁𝐀𝐂𝐇𝐄𝐄𝐄𝐄 🤩👊👤😍",
"𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐀𝐏𝐏𝐋𝐄 𝐊𝐀 𝟏𝟖𝐖 𝐖𝐀𝐋𝐀 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 🔥🤩",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
"𝙋𝘼𝙋𝘼 𝙆𝙄 𝙎𝙋𝙀𝙀𝘿 𝙈𝙏𝘾𝙃 𝙉𝙃𝙄 𝙃𝙊 𝙍𝙃𝙄 𝙆𝙔𝘼",
"𝙆𝙄𝙏𝙉𝙄 𝘾𝙃𝙊𝘿𝙐 𝙏𝙀𝙍𝙄 𝙈𝘼 𝘼𝘽 𝙊𝙍..",
"𝗧𝗘𝗥𝗜 𝗠𝗔𝗨𝗦𝗜 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗜𝗡𝗗𝗜𝗔𝗡 𝗥𝗔𝗜𝗟𝗪𝗔𝗬 🚂💥😂",
"𝙆𝙄𝙏𝙉𝙄 𝙂𝙇𝙄𝙔𝘼 𝙋𝘿𝙒𝙀𝙂𝘼 𝘼𝙋𝙉𝙄 𝙈𝘼 𝙆𝙊",
"𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗🤘🏻🙌🏻☠️",
"2 𝙍𝙐𝙋𝘼𝙔 𝙆𝙄 𝙋𝙀𝙋𝙎𝙄 𝙏𝙀𝙍𝙄 𝙈𝙐𝙈𝙈𝙔 𝙎𝘼𝘽𝙎𝙀 𝙎𝙀𝙓𝙔 💋💦",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐"
"Baap bhi bnale muje rndike",
"Tera baap randibaaz ey yaad ey tujhe",
"Tu apni Maa cuda na tympass",
"Oye unfunny swipe mtt kr",
"Oh hello bihari tera baap bihari or tu v bihari aaukat me rha kr.",
"Oyy kinner tujhe gc me aane ki permission kisne di.",
"Cudke dikha",
"Cudke dikha ek baar.",
"Sun sun ma cuda.",
"Teri maca bhosda.",
"Oye choti jati ke tmr.",
"Ky? jldi likh kidde.",
"Bihari com gang ke baap ko tag crega tu",
"Mujhe cya tu bihari ey tmkc bs",
"Jaldi se randibaaz papa bol",
"Side hoja bihari tery maa cud gai ab",
"Hye pgl bhg mat ache se cud",
"bhg ny randyke tu ajj",
"Hye pgl ke bche bhag mat",
"Hye dur hatt madchod ke bache",
"koi bat ny tery maa randy ey esliye maf cr rha hu tujhe",
"koi baat ny maa chudwa apni tu mafi de dunga",
"Ache se maa chudwa apni tu mafi mil jayegi tujhe",
"apni ma mat chuda muje swipe crke",
"Ache se apni ma cudwa tu swipe crke",
"Fr bolna na ki cudwa le apni ma swipe crke",
"Cya hua ma cud gyi tery",
"pr kese cud gyi tery ma",
"mujhe pta tha ma cud gai tery",
"mey ny manta ma cud gyi tery",
"teri ma rndy",
"lode se utr mc",
"lun mt chus mera",
"nikal madarchd",
"chup oye gashti k bache",
"makichut teri",
"chup rndyke",
"ma rndy teri",
"teri ma k hath todh k tere baap k muh me fasadunga randyke",
"leave le tu rndyke pasand nai aya meko",
"leave le tu randyke ider se",
"Leave le jldi se wrna ma chud gai tery",
"Leave ny lega maa randy tery",
"Smjh bat maa randy ey tery leave le",
"fast leave le kamjor randyke",
"tuto chup rndyk",
"oy hijde khana kha ke aa kamzor",
"teri mako ily rey🌚😂",
"chup chap chud tmkc",
"chupchap maa chudwa apni tu",
"shi se maa chudwa apni tu chupchap",
"fr se maa chudwa tu apni chupchap",
"shi se likh wrna ma chud gai tery",
"ma cyu chud gai tery chupchap",
"proof cr maa chud gyi tery",
"proof ey tery maa randy ey",
"proof ho chuka maa randy tery",
"Chup chillar",
"chup chup maa k bosda tery",
"oy hijde khana kha ke aa kamzor",
"chup madarchod ?",
"Ab tk cud gyi hogi tery maa ?",
"ny ny me kuch ny janta bs teri ma rndy ey",
"Sbse phele apni maa ko bol chudna kaam kre",
"Yaha bhi chuda tu rndyce pille",
"terimakabosda",
"teri to bhen cudegi",
"chup rndyke tommy",
"nikal madarchd cudke yha se",
"coz teri ma andhi randi he",
"nyto baap bol mujhe",
"nyny teri maa hogi rndii jo chudwati jogi",
"try ammi ce bhosde me emoji dal mc",
"cya ? chmr chud gya cya ?",
"tm chudri hogi frrto",
"cya ? kb ? pgl ey cya rndkek",
"cya sch mey pgl ey cya tu randyke cudwa li tune apni ma",
"itna sch ny bol ma chud gai tery",
"sch mey pgl ey tu apni ma cudwa lia mere sth",
"mtlb tmr",
"nyto",
"pura likh mc",
"tmr frrto",
"oh ok cudle fir",
"teri maa ka damad",
"cya ? ache se likhe pehle rndikebache",
"nyto teri maa chodne me vyast hu",
"nyto pgl ey cya kuch bi",
"oyee cya ? chud gya ?",
"chud mt hss",
"yur rndii mom",
"are sbki maa rndii or teri bi",
"are idar cudle ek baar",
"tri maa ci trh",
"ek line me tmr",
"Q",
"ocy ab chudle",
"pehele teri maa chodu",
"nyto",
"q ?",
"hyyy chud ke dika ek baar",
"oyee sun dost tmr",
"bhag ja raand maaf crr dunga",
"oyee pgl rndii idar aa",
"cya tmr frrto",
"oyee idar aake chud le chmr",
"nyto aese hi cud",
"oyee hyy aise hi cud lena",
"or chud le",
"chud ke dika or",
"hyy chudo na",
"chudo mt bhag jao",
"byyee hyy cya ?",
"Qchud q rhe ho ?",
"pgl ey cya mc",
"chud mt",
"cya pgl rndii idar aa",
"teri ammi ce bhosde me chappal",
"oyee idar aa mc",
"kmzror ey cya rndiek",
"cya likh rha ?",
"chud tha cya ?",
"oyee slide leke baat crmc",
"idar a teri maa chodu",
"oyee cp mt crr chudle",
"oyee hyy chud ke dika",
"idar aa try ma schofu khachar khachar",
"idar aa ja mc",
"hyy idar aake chudle",
"oyee kmzor mc idar aa",
"ye cya tmr",
"oyee ny cp ny crr",
"oyee pgl mt crr",
"cudle aram se mc",
"pgl ey cya rndiek",
"cp crce chudega !",
"baap ? mc mera coi ma baap ny ey mai upar se rocket pe beth ce bss teri ma chodne aya hu",
"Chota likh rndi k bache",
"Chota likha wrna try ma rndy",
"Try ma baka codega",
"Tmkc main burf",
"Bhikari ki jhat ma cuda le",
"Chodke tery ma marjayegi",
"Tmkc main Mount Everest",
"Muh mey lega lund mera",
"Hijde ki jhat chup wrna try ma rndi",
"Menu ny pta tery ma randy",
"Menu ki pta ma randy tery",
"Menu pta maa cud gai tery",
"Menu sb pta ma randy ey tery",
"Menu pr tery ma randy",
"Randy maa tery menu pta",
"Tenu or menu pta ey maa randy tery",
"Bs bs maa cudwa apni",
"Bs bs ma randy tery thnkss",
"Bs bs chudwa lia tu apni maa",
"Bs bs kamjor maa randy tery",
"Smjh gya apni ma cudwa le ab",
"smjh gya tery maa randy ey",
"smjh gya tu sabit kr maa randy tery",
"Cya hua ma cudwa tu apni",
"Easy maa cudwa le apni tu",
"Easy w8 ma chudwa le apni ab",
"Sans ari ha ky teri maa chudgi ajj",
"Teri maa ko bina sanss lete hue chodunga",
"chup randike kamjor",
"apni ma normie cudwa le tu",
"fr cya normie ma cud gai tery",
"bas thek tery ma randy",
"bas thek tery maa cud gyi",
"kamjor thi tery ma esliye cud gai",
"Mai sb janta ma cud gai tery",
"chl chl ht tery maa cud gyi",
"fr kaise cud gyi maa tery",
"maa tery randy ey",
"bas tery maa randy ey",
"fr randy ma tery ey",
"Kamjor ma ka bcha tu randyke",
"bhot gndi cud gai maa tery",
"pr kaise maa cud gai tery itna gnda",
"mujhe cya bta rha maa randy tery",
"mujhe cya pta ma cud gyi tery",
"fir mujhe ny pta maa cud gai tery",
"pta ny kon cod dia tery maa ko",
"ruk aaya tery ma codke",
"wait cr tery maa cod rha hu",
"wait cr rabdyke maa cud rhi ey tery",
"wait kr smjh rha tery ma codke",
"wait le thoda chodne de tery mako",
"ruk ja aand rkh dunga tery make liye",
"tery maa famous randy ey",
"maan lia mene maa randy sali tery",
"maan lia maa cud gai tery",
"shant beth randyke maa chudwa tu apni",
"shant bethke chudwa le apni mako tu",
"fr se shant Beth tu cud ab randyke yha",
"mere smjh ny aya maa randy tery",
"Le केला Kha tu madarchod",
"Hye tery ma cud gyi cya",
"hye tery maa mar gai cya",
"Hye sch bta com cod dia tery mako",
"Chl chod dia teri maa ko smjhle",
"Baki koi dikkat ny tery maa randy ey",
"baki sb jante ey ki maa chuddkad ey tery",
"mujhe cya pta tha tery maa cudne wli ey",
"pr mei kaise jnta tery ma ko koi chod dia",
"pr mera vi manna shi tha maa chud gai tery",
"pr wo glt ny tery maa randy ey",
"pr wo shi ey tery maa chuddkad ey",
"pr kaise kia maa chud gai tery omfoo",
"bur cheer dunga tri ma ka",
"teri ma ke dil me loda marke uski dhadkan rok dunga",
"lulle kha tri makabhosda",
"tri bhn ki bhosdi beta",
"tri ma rndi baat khtm",
"Sun ek maze ki baat batao kya teri maa randy ey"
"codu codu mako tery",
"aj cud gai tery maa oye",
"sun sun randy make bache tu",
"kilas ny randyke",
"mujhe cya pta tery bhen cud gai",
"pr pr cya hote ey tmkc",
"tmcl sunle",
"moot du tery maki chut mey",
"bhgny cudke dikha fr",
"fr se cudle tu",
"ye vi shi ey tery mkc bs",
"aj kuch ny ma cudwa tu apni",
"try kr mera lund chuske",
"tormakibur sun",
"tor maki fuddi oye",
"Haye Haye tery ma cud gai",
"oye lundke pasine..",
"kutte ke tatte sun",
"kutta jaisa cud rha tu",
"Muh mei le mera..",
"jhaat ke pissu sun tmkc",
"Hahahha ma cud gai tery",
"weak tatte uth",
"weak ey tu cud rha",
"weak ache se cud tu",
"weak tery ma cud rhi dekh",
"week tery ma cud gai ab",
"mujhe ny rok tu weak ey",
"chup hizde",
"okat ny meri ma cudwa tu apni",
"lun lega tery maki gand mei ?",
"tery maki bachi codu..",
"tery bhen ki chut aj fad du",
"speed lekr aa cudke dikha",
"speed ny tere andr weak prosn",
"ugly randyke chup",
"makafuddatery",
"tera baap ko tag kr..?",
"ache se tag kr randibaaz bhagwn ko..",
"cudke pgl ny ho tu",
"cudke pgl ho rha tu kid",
"ma to cud gai tery hawabzi cr..",
"bs ma codni ey tery",
"town mei cud tery mako lekr",
"tery ma sexy ko bej - randibaaz bhgwn pe",
"speed pkd cp ny kr",
"Try ma rendy",
"Bhkk cud",
"tey maa rndi",
"tery behen randi",
"Cud ja",
"tery didi rndi",
"Slow",
"teri Maiya ciodu",
"Bhag?",
"Bhak cud",
"Tma codu",
"Slow",
"Slow firse",
"Cudgrib",
"Try ma dou",
"tbkc codu",
"Net on off wali rndy",
"Oye try ma codu",
"Idhar aake cud chup chaap",
"tbkc mrdu",
"oi maake lodee",
"randyke beej",
"tmkc chodu",
"suar ke beej",
"net off on kr randyke ladke",
"Try ma cudi kese",
"Chup slow madharcod",
"tbkc codu kr msg delete",
"oi suar ke ladke",
"tmkc fufi",
"tery didi chudi",
"tmkc dikha",
"Cud ab",
"randyke cud",
"Bhak cud",
"cudle tbkc mru",
"tmkl cudle grib",
"tery behen vesiyaa rndi",
"Itna gnda chuda tu firse net on off",
"grib ke bete",
"Bhag ja lode tmkc maru dunga",
"tbkc mrdungaa",
"bhag tmkc",
"bhag tbkc",
"tbkc mey cp",
"cp tbkc mehh",
"cp tmkl meh",
"cp bol randyke",
"Abe cp bol randyke",
"double send ko cp tmkc codu",
"tbkc me cp cod dunga Aaj mehh",
"ht tbkc dalal ke bete.",
"Rndy jldi jldi cudq tryma",
"Para likhega..",
"Tra rndhbhak",
"Lagdi ke ladce cp bol",
"cp bol lagdi ke bete..",
"cudke cp bol",
"bhikari lund chus mera.",
"Low level cp cr",
"cp bol low level weak",
"mere lund pe ey tu hijde",
"free cudwa tery mako",
"Free mey cud tu randyke"
"speed ny weak tatte terme",
"kitni br cudwayega terymako",
"lund le randibaaz bapka",
"lun cus jaldi se randibaaz bapka",
"koi ny dekh rha cudle tu",
"cudle betichod ache se",
"maki chut tery bs yehi janta mey",
"cp bolega to tmkc",
"wrna tery ma cud jayegi",
"slow ey tu kid",
"jldi likh..tmkc",
"jldi likh..randce tu",
"tym se phle cudke dikha",
"tym hoga tery maa cudwa",
"ma cud gai tery tym se phle",
"uth randce ke ldke",
"macabosdatery",
"con kb cod dia mako tery",
"koi hoga tml",
"machar cudle tu",
"menu tery mako codna se",
"tery mako bol mujhe cod de",
"bs mey tery ma se cudna chta hu",
"Eww maka lode uth",
"Meow cr tery mako codu",
"lund rkh dia tery make fude pe",
"mera lund ke bal uth",
"kidee Zinda ho",
"mar ny kidde type kr",
"chup bkl",
"bc tery maki chut",
"mc randyke likh fast",
"fast likh randyke",
"fast likh kamzor"
"tery maki chut claim crwa",
"awz niche randce ke bche",
"sawal ny puch tery makabosda",
"fyter bnega lagde madrchod",
"oye kaale ro ke dikha",
"oye kaale roo ny",
"short ny cud tu bina ruke",
"short ny cud tu apni mako lekr",
"tery make sth tery bhen vi cudwa le",
"tery make sth tery didi vi cud gai",
"Chat fyter bnega randce codu tery mako",
"bol randibaaz daddy ey",
"bullyx randyke uth",
"mar marke cud rha tu",
"or tery ma marke cud gai"
"Jaldi likh rndyke bej",
"Or bda likh tmc",
"Or bda 2 line wla likh tmkc",
"Or bda oye likh tml",
"Teri maa ka bur",
"Oye keede",
"Randi ke ladke",
"Jaldi likh teri behen chodu",
"Mkl uth randi ke bacche",
"Teri nani meri maal",
"Tej likh randce",
"Oye maake lode mrenga",
"Teri maa chody",
"Teri Maiya ki gand",
"Tery dadi ka fudda",
"Mkl uth behencod",
"Teri maa ki bur de",
"Tery maa ka fudda me lauda",
"Teri maa chudva",
"Randi ke bete mar gaya",
"Teri maa ki chut mru",
"Jalid kr spam",
"Mc spam rokenga",
"Teri maaki chut spam kr",
"spam kr.maake lode",
"Randyke chode spam kr wrna cud tu",
"Spam kr kid",
"Noob teri maa chodu",
"Rndyke bete mar mat tu",
"Noob jaldi likh wrna tery maa rand",
"cud gai maa tery noob",
"uth randyke noob",
"chl cudke dikha noob",
"jldi typ cr noob halke",
"cud ke pgl ny ho noob",
"cud cud ke rand bnja tu noob",
"makichut tery noob",
"ganda cyu cud rha tu ?",
"itna gnda ny cud ache se cud",
"Maan le cud gya tu sun bat ab",
"makafudda fat gya tery ruk"
"BAAP BHI BNALE MUJE RNDIKE",
"TERA BAAP RANDIBAAZ EY YAAD EY TUJHE",
"TU APNI MAA CUDA NA TYMPASS",
"OYE UNFUNNY SWIPE MTT KR",
"OH HELLO BIHARI TERA BAAP BIHARI OR TU V BIHARI AAUKAT ME RHA KR.",
"OYY KINNER TUJHE GC ME AANE KI PERMISSION KISNE DI.",
"CUDKE DIKHA",
"CUDKE DIKHA EK BAAR.",
"SUN SUN MA CUDA.",
"TERI MACA BHOSDA.",
"OYE CHOTI JATI KE TMR.",
"KY? JLDI LIKH KIDDE.",
"BIHARI COM GANG KE BAAP KO TAG CREGA TU",
"MUJHE CYA TU BIHARI EY TMKC BS",
"JALDI SE RANDIBAAZ PAPA BOL",
"SIDE HOJA BIHARI TERY MAA CUD GAI AB",
"HYE PGL BHG MAT ACHE SE CUD",
"BHG NY RANDYKE TU AJJ",
"HYE PGL KE BCHE BHAG MAT",
"HYE DUR HATT MADCHOD KE BACHE",
"KOI BAT NY TERY MAA RANDY EY ESLIYE MAF CR RHA HU TUJHE",
"KOI BAAT NY MAA CHUDWA APNI TU MAFI DE DUNGA",
"ACHE SE MAA CHUDWA APNI TU MAFI MIL JAYEGI TUJHE",
"APNI MA MAT CHUDA MUJE SWIPE CRKE",
"ACHE SE APNI MA CUDWA TU SWIPE CRKE",
"FR BOLNA NA KI CUDWA LE APNI MA SWIPE CRKE",
"CYA HUA MA CUD GYI TERY",
"PR KESE CUD GYI TERY MA",
"MUJHE PTA THA MA CUD GAI TERY",
"MEY NY MANTA MA CUD GYI TERY",
"TERI MA RNDY",
"LODE SE UTR MC",
"LUN MT CHUS MERA",
"NIKAL MADARCHD",
"CHUP OYE GASHTI K BACHE",
"MAKICHUT TERI",
"CHUP RNDYKE",
"MA RNDY TERI",
"TERI MA K HATH TODH K TERE BAAP K MUH ME FASADUNGA RANDYKE",
"LEAVE LE TU RNDYKE PASAND NAI AYA MEKO",
"LEAVE LE TU RANDYKE IDER SE",
"LEAVE LE JLDI SE WRNA MA CHUD GAI TERY",
"LEAVE NY LEGA MAA RANDY TERY",
"SMJH BAT MAA RANDY EY TERY LEAVE LE",
"FAST LEAVE LE KAMJOR RANDYKE",
"TUTO CHUP RNDYK",
"OY HIJDE KHANA KHA KE AA KAMZOR",
"TERI MAKO ILY REY",
"CHUP CHAP CHUD TMKC",
"CHUPCHAP MAA CHUDWA APNI TU",
"SHI SE MAA CHUDWA APNI TU CHUPCHAP",
"FR SE MAA CHUDWA TU APNI CHUPCHAP",
"SHI SE LIKH WRNA MA CHUD GAI TERY",
"MA CYU CHUD GAI TERY CHUPCHAP",
"PROOF CR MAA CHUD GYI TERY",
"PROOF EY TERY MAA RANDY EY",
"PROOF HO CHUKA MAA RANDY TERY",
"CHUP CHILLAR",
"CHUP CHUP MA K BOSDA TERY",
"OY HIJDE KHANA KHA KE AA KAMZOR",
"CHUP MADARCHOD ?",
"AB TK CUD GYI HOGI TERY MAA ?",
"NY NY ME KUCH NY JANTA BS TERI MA RNDY EY",
"SBSE PHELE APNI MAA KO BOL CHUDNA KAAM KRE",
"YAHA BHI CHUDA TU RNDYCE PILLE",
"TERIMAKABOSDA",
"TERI TO BHEN CUDEGI",
"CHUP RNDYKE TOMMY",
"NIKAL MADARCHD CUDKE YHA SE",
"COZ TERI MA ANDHI RANDI HE",
"NYTO BAAP BOL MUJHE",
"NYNY TERI MAA HOGI RNDII JO CHUDWATI JOGI",
"TRY AMMI CE BHOSDE ME EMOJI DAL MC",
"CYA ? CHMR CHUD GYA CYA ?",
"TM CHUDRI HOGI FRRTO",
"CYA ? KB ? PGL EY CYA RNDKEK",
"CYA SCH MEY PGL EY CYA TU RANDYKE CUDWA LI TUNE APNI MA",
"ITNA SCH NY BOL MA CHUD GAI TERY",
"SCH MEY PGL EY TU APNI MA CUDWA LIA MERE STH",
"MTLB TMR",
"NYTO",
"PURA LIKH MC",
"TMR FRRTO",
"OH OK CUDLE FIR",
"TERI MAA KA DAMAD",
"CYA ? ACHE SE LIKHE PEHLE RNDIKEBACHE",
"NYTO TERI MAA CHODNE ME VYAST HU",
"NYTO PGL EY CYA KUCH BI",
"OYEE CYA ? CHUD GYA ?",
"CHUD MT HSS",
"YUR RNDII MOM",
"ARE SBKI MAA RNDII OR TERI BI",
"ARE IDAR CUDLE EK BAAR",
"TRI MAA CI TRH",
"EK LINE ME TMR",
"Q",
"OCY AB CHUDLE",
"PEHELE TERI MAA CHODU",
"NYTO",
"Q ?",
"HYYY CHUD KE DIKA EK BAAR",
"OYEE SUN DOST TMR",
"BHAG JA RAAND MAAF CRR DUNGA",
"OYEE PGL RNDII IDAR AA",
"CYA TMR FRRTO",
"OYEE IDAR Aake CHUD LE CHMR",
"NYTO AESE HI CUD",
"OYEE HYY AISE HI CUD LENA",
"OR CHUD LE",
"CHUD KE DIKA OR",
"HYY CHUDO NA",
"CHUDO MT BHAG JAO",
"BYYEE HYY CYA ?",
"QCHUD Q RHE HO ?",
"PGL EY CYA MC",
"CHUD MT",
"CYA PGL RNDII IDAR AA",
"TERI AMMI CE BHOSDE ME CHAPPAL",
"OYEE IDAR AA MC",
"KMZROR EY CYA RNDIEK",
"CYA LIKH RHA ?",
"CHUD THA CYA ?",
"OYEE SLIDE LEKE BAAT CRMC",
"IDAR A TERI MAA CHODU",
"OYEE CP MT CRR CHUDLE",
"OYEE HYY CHUD KE DIKA",
"IDAR AA TRY MA SCHOFU KHACHAR KHACHAR",
"IDAR AA JA MC",
"HYY IDAR Aake CHUDLE",
"OYEE KMZOR MC IDAR AA",
"YE CYA TMR",
"OYEE NY CP NY CRR",
"OYEE PGL MT CRR",
"CUDLE ARAM SE MC",
"PGL EY CYA RNDIEK",
"CP CRCE CHUDEGA !",
"BAAP ? MC MERA COI MA BAAP NY EY MAI UPAR SE ROCKET PE BETH CE BSS TERI MA CHODNE AYA HU",
"CHOTA LIKH RNDI K BACHE",
"CHOTA LIKHA WRNA TRY MA RNDY",
"TRY MA BAKA CODEGA",
"TMKC MAIN BURF",
"BHIKARI KI JHAT MA CUDA LE",
"CHODKE TERY MA MARJAYEGI",
"TMKC MAIN MOUNT EVEREST",
"MUH MEY LEGA LUND MERA",
"HIJDE KI JHAT CHUP WRNA TRY MA RNDI",
"MENU NY PTA TERY MA RANDY",
"MENU KI PTA MA RANDY TERY",
"MENU PTA MAA CUD GAI TERY",
"MENU SB PTA MA RANDY EY TERY",
"MENU PR TERY MA RANDY",
"RANDY MAA TERY MENU PTA",
"TENU OR MENU PTA EY MAA RANDY TERY",
"BS BS MAA CUDWA APNI",
"BS BS MA RANDY TERY THNKSS",
"BS BS CHUDWA LIA TU APNI MAA",
"BS BS KAMJOR MAA RANDY TERY",
"SMJH GYA APNI MA CUDWA LE AB",
"SMJH GYA TERY MAA RANDY EY",
"SMJH GYA TU SABIT KR MAA RANDY TERY",
"CYA HUA MA CUDWA TU APNI",
"EASY MAA CUDWA LE APNI TU",
"EASY W8 MA CHUDWA LE APNI AB",
"SANS ARI HA KY TERI MAA CHUDGI AJJ",
"TERI MAA KO BINA SANSS LETE HUE CHODUNGA",
"CHUP RANDIKE KAMJOR",
"APNI MA NORMIE CUDWA LE TU",
"FR CYA NORMIE MA CUD GAI TERY",
"BAS THEK TERY MA RANDY",
"BAS THEK TERY MAA CUD GYI",
"KAMJOR THI TERY MA ESLIYE CUD GAI",
"MAI SB JANTA MA CUD GAI TERY",
"CHL CHL HT TERY MAA CUD GYI",
"FR KAISE CUD GYI MAA TERY",
"MAA TERY RANDY EY",
"BAS TERY MAA RANDY EY",
"FR RANDY MA TERY EY",
"KAMJOR MA KA BCHA TU RANDYKE",
"BHOT GNDI CUD GAI MAA TERY",
"PR KAISE MAA CUD GAI TERY ITNA GNDA",
"MUJHE CYA BTA RHA MAA RANDY TERY",
"MUJHE CYA PTA MA CUD GYI TERY",
"FIR MUJHE NY PTA MAA CUD GAI TERY",
"PTA NY KON COD DIA TERY MAA KO",
"RUK AAYA TERY MA CODKE",
"WAIT CR TERY MAA COD RHA HU",
"WAIT CR RABDYKE MAA CUD RHI EY TERY",
"WAIT KR SMJH RHA TERY MA CODKE",
"WAIT LE THODA CHODNE DE TERY MAKO",
"RUK JA AAND RKH DUNGA TERY MAKE LIYE",
"TERY MAA FAMOUS RANDY EY",
"MAAN LIA MENE MAA RANDY SALI TERY",
"MAAN LIA MAA CUD GAI TERY",
"SHANT BETH RANDYKE MAA CHUDWA TU APNI",
"SHANT BETHKE CHUDWA LE APNI MAKO TU",
"FR SE SHANT BETH TU CUD AB RANDYKE YHA",
"MERE SMJH NY AYA MAA RANDY TERY",
"LE KELA KHA TU MADARCHOD",
"HYE TERY MA CUD GYI CYA",
"HYE TERY MAA MAR GAI CYA",
"HYE SCH BTA COM COD DIA TERY MAKO",
"CHL CHOD DIA TERI MAA KO SMJHLE",
"BAKI KOI DIKKAT NY TERY MAA RANDY EY",
"BAKI SB JANTE EY KI MAA CHUDDKAD EY TERY",
"MUJHE CYA PTA THA TERY MAA CUDNE WLI EY",
"PR MEI KAISE JNTA TERY MA KO KOI CHOD DIA",
"PR MERA VI MANNA SHI THA MAA CHUD GAI TERY",
"PR WO GLT NY TERY MAA RANDY EY",
"PR WO SHI EY TERY MAA CHUDDKAD EY",
"PR KAISE KIA MAA CHUD GAI TERY OMFOO",
"BUR CHEER DUNGA TRI MA KA",
"TERI MA KE DIL ME LODA MARKE USKI DHADKAN ROK DUNGA",
"LULLE KHA TRI MAKABHOSDA",
"TRI BHN KI BHOSDI BETA",
"TRI MA RNDI BAAT KHTM",
"SUN EK MAZE KI BAAT BATAO KYA TERI MAA RANDY EY",
"CODU CODU MAKO TERY",
"AJ CUD GAI TERY MAA OYE",
"SUN SUN RANDY MAKE BACHE TU",
"KILAS NY RANDYKE",
"MUJHE CYA PTA TERY BHEN CUD GAI",
"PR PR CYA HOTE EY TMKC",
"TMCL SUNLE",
"MOOT DU TERY MAKI CHUT MEY",
"BHGNY CUDKE DIKHA FR",
"FR SE CUDLE TU",
"YE VI SHI EY TERY MKC BS",
"AJ KUCH NY MA CUDWA TU APNI",
"TRY KR MERA LUND CHUSKE",
"TORMAKIBUR SUN",
"TOR MAKI FUDDI OYE",
"HAYE HAYE TERY MA CUD GAI",
"OYE LUNDKE PASINE..",
"KUTTE KE TATTE SUN",
"KUTTA JAISA CUD RHA TU",
"MUH MEI LE MERA..",
"JHAAT KE PISSU SUN TMKC",
"HAHAHHA MA CUD GAI TERY",
"WEAK TATTE UTH",
"WEAK EY TU CUD RHA",
"WEAK ACHE SE CUD TU",
"WEAK TERY MA CUD RHI DEKH",
"WEEK TERY MA CUD GAI AB",
"MUJHE NY ROK TU WEAK EY",
"CHUP HIZDE",
"OKAT NY MERI MA CUDWA TU APNI",
"LUN LEGA TERY MAKI GAND MEI ?",
"TERY MAKI BACHI CODU..",
"TERY BHEN KI CHUT AJ FAD DU",
"SPEED LEKR AA CUDKE DIKHA",
"SPEED NY TERE ANDR WEAK PROSN",
"UGLY RANDYKE CHUP",
"MAKAFUDDATERY",
"TERA BAAP KO TAG KR..?",
"ACHE SE TAG KR RANDIBAAZ BHAGWN KO..",
"CUDKE PGL NY HO TU",
"CUDKE PGL HO RHA TU KID",
"MA TO CUD GAI TERY HAWABZI CR..",
"BS MA CODNI EY TERY",
"TOWN MEI CUD TERY MAKO LEKR",
"TERY MA SEXY KO BEJ - RANDIBAAZ BHGWN PE",
"SPEED PKD CP NY KR",
"TRY MA RENDY",
"BHKK CUD",
"TEY MAA RNDI",
"TERY BEHEN RANDI",
"CUD JA TMC",
"TERY DIDI RNDI",
"SLOW",
"TERI MAIYA CIODU",
"BHAG?TMC ",
"BHAK CUD TML",
"TMA CODU",
"SLOW TMKC ",
"SLOW FIRSE TMKC ",
"CUDGRIB TML",
"TRY MA DOU",
"TBKC CODU",
"NET ON OFF WALI RNDY",
"OYE TRY MA CODU",
"IDHAR AAKE CUD CHUP CHAAP",
"TBKC MRDU",
"OI MAAKE LODEE",
"RANDYKE BEEJ",
"TMKC CHODU",
"SUAR KE BEEJ",
"NET OFF ON KR RANDYKE LADKE",
"TRY MA CUDI KESE",
"CHUP SLOW MADHARCOD",
"TBKC CODU KR MSG DELETE",
"OI SUAR KE LADKE",
"TMKC FUFI",
"TERY DIDI CHUDI",
"TMKC DIKHA",
"CUD AB",
"RANDYKE CUD",
"BHAK CUD",
"CUDLE TBKC MRU",
"TMKL CUDLE GRIB",
"TERY BEHEN VESITYA RNDI",
"ITNA GNDA CHUDA TU FIRSE NET ON OFF",
"GRIB KE BETE",
"BHAG JA LODE TMKC MARU DUNGA",
"TBKC MRDUNGAA",
"BHAG TMKC",
"BHAG TBKC",
"TBKC MEY CP",
"CP TBKC MEHH",
"CP TMKL MEH",
"CP BOL RANDYKE",
"ABE CP BOL RANDYKE",
"DOUBLE SEND KO CP TMKC CODU",
"TBKC ME CP COD DUNGA AAJ MEHH",
"HT TBKC DALAL KE BETE.",
"RNDY JLDI JLDI CUDQ TRYMA",
"PARA LIKHEGA..",
"TRA RNDHBHAK",
"LAGDI KE LADCE CP BOL",
"CP BOL LAGDI KE BETE..",
"CUDKE CP BOL",
"BHIKARI LUND CHUS MERA.",
"LOW LEVEL CP CR",
"CP BOL LOW LEVEL WEAK",
"MERE LUND PE EY TU HIJDE",
"FREE CUDWA TERY MAKO",
"FREE MEY CUD TU RANDYKE",
"SPEED NY WEAK TATTE TERME",
"KITNI BR CUDWAYEGA TERYMAKO",
"LUND LE RANDIBAAZ BAPKA",
"LUN CUS JALDI SE RANDIBAAZ BAPKA",
"KOI NY DEKH RHA CUDLE TU",
"CUDLE BETICHOD ACHE SE",
"MAKI CHUT TERY BS YEHI JANTA MEY",
"CP BOLEGA TO TMKC",
"WRNA TERY MA CUD JAYEGI",
"SLOW EY TU KID",
"JLDI LIKH..TMKC",
"JLDI LIKH..RANDCE TU",
"TYM SE PHLE CUDKE DIKHA",
"TYM HOGA TERY MAA CUDWA",
"MA CUD GAI TERY TYM SE PHLE",
"UTH RANDCE KE LDKE",
"MACABOSDATERY",
"CON KB COD DIA MAKO TERY",
"KOI HOGA TML",
"MACHAR CUDLE TU",
"MENU TERY MAKO CODNA SE",
"TERY MAKO BOL MUJHE COD DE",
"BS MEY TERY MA SE CUDNA CHTA HU",
"EWW MAKA LODE UTH",
"MEOW CR TERY MAKO CODU",
"LUND RKH DIA TERY MAKE FUDE PE",
"MERA LUND KE BAL UTH",
"KIDEE ZINDA HO",
"MAR NY KIDDE TYPE KR",
"CHUP BKL",
"BC TERY MAKI CHUT",
"MC RANDYKE LIKH FAST",
"FAST LIKH RANDYKE",
"FAST LIKH KAMZOR",
"TERY MAKI CHUT CLAIM CRWA",
"AWZ NICHE RANDCE KE BCHE",
"SAWAL NY PUCH TERY MAKABOSDA",
"FYTER BNEGA LAGDE MADRCHOD",
"OYE KAALE RO KE DIKHA",
"OYE KAALE ROO NY",
"SHORT NY CUD TU BINA RUKE",
"SHORT NY CUD TU APNI MAKO LEKR",
"TERY MAKE STH TERY BHEN VI CUDWA LE",
"TERY MAKE STH TERY DIDI VI CUD GAI",
"CHAT FYTER BNEGA RANDCE CODU TERY MAKO",
"BOL RANDIBAAZ DADDY EY",
"BULLYX RANDYKE UTH",
"MAR MARKE CUD RHA TU",
"OR TERY MA MARKE CUD GAI",
"JALDI LIKH RNDYKE BEJ",
"OR BDA LIKH TMC",
"OR BDA 2 LINE WLA LIKH TMKC",
"OR BDA OYE LIKH TML",
"TERI MAA KA BUR",
"OYE KEEDE",
"RANDI KE LADKE",
"JALDI LIKH TERI BEHEN CHODU",
"MKL UTH RANDI KE BACCHE",
"TERI NANI MERI MAAL",
"TEJ LIKH RANDCE",
"OYE MAAKE LODE MRENGA",
"TERI MAA CHODY",
"TERI MAIYA KI GAND",
"TERY DADI KA FUDDA",
"MKL UTH BEHENCOD",
"TERI MAA KI BUR DE",
"TERY MAA KA FUDDA ME LAUDA",
"TERI MAA CHUDVA",
"RANDI KE BETE MAR GAYA",
"TERI MAA KI CHUT MRU",
"JALID KR SPAM",
"MC SPAM ROKENGA",
"TERI MAAKI CHUT SPAM KR",
"SPAM KR.MAAKE LODE",
"RANDYKE CHODE SPAM KR WRNA CUD TU",
"SPAM KR KID",
"NOOB TERI MAA CHODU",
"RNDYKE BETE MAR MAT TU",
"NOOB JALDI LIKH WRNA TERY MAA RAND",
"CUD GAI MAA TERY NOOB",
"UTH RANDYKE NOOB",
"CHL CUDKE DIKHA NOOB",
"JLDI TYP CR NOOB HALKE",
"CUD KE PGL NY HO NOOB",
"CUD CUD KE RAND BNJA TU NOOB",
"MAKICHUT TERY NOOB",
"GANDA CYU CUD RHA TU ?",
"ITNA GNDA NY CUD ACHE SE CUD",
"MAAN LE CUD GYA TU SUN BAT AB",
"MAKAFUDDA FAT GYA TERY RUK",
"sʜᴀɴᴛ ʙᴇᴛʜ ᴍᴀᴅʀᴄʜᴏᴅ ᴡʀɴᴀ ᴍᴀᴋᴀʙᴏsᴅᴀ ᴛᴇᴇʏ.",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ..",
"ʟᴡᴅᴇ ᴋᴇ ʙᴀᴀᴀʟʟʟ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅᴋᴇ ᴘɢʟ ᴅᴇᴋʜ.",
"ᴍᴀᴄʜᴀʀ ᴋɪ ᴊʜᴀᴀᴛ ᴋᴇ ʙᴀᴀᴀʟʟʟʟ ᴄᴜᴅ ᴀᴄʜᴇ sᴇ ʏʜᴀᴘᴇ ᴛᴜ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴍ ᴅᴜ ᴛᴀᴘᴀ ᴛᴀᴘ?",
"ᴛᴇʀɪ ᴍᴀ ᴋᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪ ʙʜɴ ꜱʙꜱʙᴇ ʙᴅɪ ʀᴀɴᴅɪ.",
"ᴛᴇʀɪ ᴍᴀ ᴏꜱꜱᴇ ʙᴀᴅɪ ʀᴀɴᴅᴅᴅᴅᴅ",
"ᴛᴇʀᴀ ʙᴀᴀᴘ ʀᴀɴᴅɪʙᴀᴀᴢ ᴇʏ ᴅᴇᴋʜ",
"ᴋɪᴛɴɪ ᴄʜᴏᴅᴜ ᴛᴇʀɪ ᴍᴀ ᴀʙ ᴏʀ..",
"ᴛᴇʀɪ ᴍᴀ ᴄʜᴏᴅ ᴅɪ ʜᴍ ɴᴇ",
"ᴛᴇʀɪ ᴍᴀ ᴋᴇ ꜱᴛʜ ʀᴇᴇʟꜱ ʙɴᴇɢᴀ ʀᴏᴀᴅ ᴘᴇᴇ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴇᴋ ᴅᴀᴍ ᴛᴏᴘ ꜱᴇxʏ",
"ᴍᴀʟᴜᴍ ɴᴀ ᴘʜʀ ᴋᴇꜱᴇ ʟᴇᴛᴀ ʜᴜ ᴍ ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴛᴀᴘᴀ ᴛᴀᴘᴘᴘᴘᴘ",
"ʟᴜɴᴅ ᴋᴇ ᴄʜᴏᴅᴇ ᴛᴜ ᴋᴇʀᴇɢᴀ ᴛʏᴘɪɴɢ ᴋʀᴇɢᴀ ᴛᴍᴋᴄ",
"ꜱᴘᴇᴇᴅ ᴘᴋᴅ ʟᴡᴅᴇᴇᴇᴇ ᴡʀɴᴀ ᴍᴇʀᴀ ʟᴜɴᴅ ᴘᴋᴅ",
"ʙᴀᴀᴘ ᴋɪ ꜱᴘᴇᴇᴅ ᴍᴛᴄʜ ᴋʀʀʀ",
"ʟᴡᴅᴀ ʟᴇ ᴍᴇʀᴀ ᴊᴀʟᴅɪ sᴇ ᴛᴜ",
"ᴘᴀᴘᴀ ᴋɪ ꜱᴘᴇᴇᴅ ᴍᴛᴄʜ ɴʜɪ ʜᴏ ʀʜɪ ᴋʏᴀ ᴛᴇʀᴇsᴇ",
"ᴀʟᴇ ᴀʟᴇ ᴍᴇʟᴀ ʙᴄʜᴀᴀᴀᴀ ᴛᴇʀʏ ᴍᴀᴋᴀ ʙᴏsᴅᴀ sᴜɴ",
"ᴄʜᴜᴅ ɢʏᴀ ʀᴀɴᴅɪʙᴀᴀᴢ ᴘᴀᴘᴀ ꜱᴇᴇᴇ ᴛᴜ",
"ᴍᴇɴᴜ ᴋɪ ᴘᴛᴀ ᴛᴇʀʏ ᴍᴀ ᴄᴜᴅ ɢᴀɪ",
"ᴋᴏɪ ʙᴀᴀᴛ ɴʏ ᴍᴀᴀ ʀᴀɴᴅʏ ᴛᴇʀʏ",
"ʜᴀʜᴀʜᴀᴀᴀᴀᴀ ᴍᴀᴋᴀʙᴏsᴅᴀ ᴛᴇʀʏ",
"xʜᴜᴅ ɢᴀɪ ᴍᴀᴀ ᴛᴇʀʏ ᴋɪᴅꜱꜱꜱꜱ",
"ᴛᴇʀɪ ᴍᴀ ᴄʜᴜᴅ ɢʏɪ ᴀʙ ꜰʀᴀʀ ᴍᴛ ʜᴏɴᴀ",
"ʏᴇ ʟᴜɴᴅ ʟᴇ ᴍᴇʀᴀ ᴄʜʟ ᴊᴀʟᴅɪ sᴇ",
"ᴋɪᴅꜱꜱꜱ ꜰʀᴀʀ ɴᴀ ʜᴏ ᴛᴜ ʜᴀʜᴀʜʜ",
"ʙʜᴇɴ ᴋᴇ ʟᴡᴅᴇ ꜱʜʀᴍ ᴋʀ",
"ᴋɪᴛɴɪ ɢʟɪʏᴀ ᴘᴅᴡᴇɢᴀ ᴀᴘɴɪ ᴍᴀ ᴋᴏ",
"ᴄʜᴜᴘ ɴᴀʟʟɪɪ ʀᴀɴᴅʏᴋᴇ ʟᴀᴅᴋᴇ",
"ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ꜱᴀᴅᴀᴋ ᴘʀ ʟɪᴛᴀᴋᴇ ᴄʜᴏᴅ ᴅᴜɴɢᴀ 😂😆🤤",
"ᴀʙᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴀ ʙʜᴏꜱᴅᴀ ᴍᴀᴅᴇʀᴄʜᴏᴏᴅ ᴋʀ ᴘɪʟʟᴇ ᴘᴀᴘᴀ ꜱᴇ ʟᴀᴅᴇɢᴀ ᴛᴜ 😼😂🤤",
"ɢᴀʟɪ ɢᴀʟɪ ɴᴇ ꜱʜᴏʀ ʜᴇ ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ᴄʜᴏʀ ʜᴇ 💋💋💦",
"ᴀʙᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ᴘɪʟʟᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴄʜᴏᴅᴇ 😂👻🔥",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴀɪꜱᴇ ᴄʜᴏᴅᴀ ᴀɪꜱᴇ ᴄʜᴏᴅᴀ ᴛᴇʀɪ ᴍᴀᴀᴀ ʙᴇᴅ ᴘᴇʜɪ ᴍᴜᴛʜ ᴅɪᴀ 💦💦💦💦",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴇ ʙʜᴏꜱᴅᴇ ᴍᴇ ᴀᴀᴀɢ ʟᴀɢᴀᴅɪᴀ ᴍᴇʀᴀ ᴍᴏᴛᴀ ʟᴜɴᴅ ᴅᴀʟᴋᴇ 🔥🔥💦😆😆",
"ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅᴜ ᴄʜᴀʟ ɴɪᴋᴀʟ",
"ᴋɪᴛɴᴀ ᴄʜᴏᴅᴜ ᴛᴇʀɪ ʀᴀɴᴅɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ᴀʙʙ ᴀᴘɴɪ ʙᴇʜᴇɴ ᴋᴏ ʙʜᴇᴊ 😆👻🤤",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏᴛᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴘᴜʀᴀ ꜰᴀᴀᴅ ᴅɪᴀ ᴄʜᴜᴛʜ ᴀʙʙ ᴛᴇʀɪ ɢꜰ ᴋᴏ ʙʜᴇᴊ 😆💦🤤",
"ᴛᴇʀɪ ɢꜰ ᴋᴏ ᴇᴛɴᴀ ᴄʜᴏᴅᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴏᴅᴇ ᴛᴇʀɪ ɢꜰ ᴛᴏ ᴍᴇʀɪ ʀᴀɴᴅɪ ʙᴀɴɢᴀʏɪ ᴀʙʙ ᴄʜᴀʟ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅᴛᴀ ꜰɪʀꜱᴇ ♥️💦😆😆😆😆",
"ʜᴀʀɪ ʜᴀʀɪ ɢʜᴀᴀꜱ ᴍᴇ ᴊʜᴏᴘᴅᴀ ᴛᴇʀɪ ᴍᴀᴀᴋᴀ ʙʜᴏꜱᴅᴀ 🤣🤣💋💦",
"ᴄʜᴀʟ ᴛᴇʀᴇ ʙᴀᴀᴘ ᴋᴏ ʙʜᴇᴊ ᴛᴇʀᴀ ʙᴀꜱᴋᴀ ɴʜɪ ʜᴇ ᴘᴀᴘᴀ ꜱᴇ ʟᴀᴅᴇɢᴀ ᴛᴜ",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ʙᴏᴍʙ ᴅᴀʟᴋᴇ ᴜᴅᴀ ᴅᴜɴɢᴀ ᴍᴀᴀᴋᴇ ʟᴀᴡᴅᴇ",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴛʀᴀɪɴ ᴍᴇ ʟᴇᴊᴀᴋᴇ ᴛᴏᴘ ʙᴇᴅ ᴘᴇ ʟɪᴛᴀᴋᴇ ᴄʜᴏᴅ ᴅᴜɴɢᴀ ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ 🤣🤣💋💋",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴇ ɴᴜᴅᴇꜱ ɢᴏᴏɢʟᴇ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴀᴇᴡᴅᴇ 👻🔥",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴇ ɴᴜᴅᴇꜱ ɢᴏᴏɢʟᴇ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴀᴇᴡᴅᴇ 👻🔥",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴠɪᴅᴇᴏ ʙᴀɴᴀᴋᴇ xɴxx ᴘᴇ ɴᴇᴇʟᴀᴍ ᴋᴀʀᴅᴜɴɢᴀ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 💦💋",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋɪ ᴄʜᴜᴅᴀɪ ᴋᴏ ᴘᴏ*ʀɴʜᴜʙ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ꜱᴜᴀʀ ᴋᴇ ᴄʜᴏᴅᴇ 🤣💋💦",
"ᴀʙᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴛᴇʀᴇᴋᴏ ᴄʜᴀᴋᴋᴏ ꜱᴇ ᴘɪʟᴡᴀᴠᴜɴɢᴀ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ 🤣🤣",
"ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ꜰᴀᴀᴅᴋᴇ ʀᴀᴋᴅɪᴀ ᴍᴀᴀᴋᴇ ʟᴏᴅᴇ ᴊᴀᴀ ᴀʙʙ ꜱɪʟᴡᴀʟᴇ 👄👄",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴇʀᴀ ʟᴜɴᴅ ᴋᴀᴀʟᴀ",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ʟᴇᴛɪ ᴍᴇʀɪ ʟᴜɴᴅ ʙᴀᴅᴇ ᴍᴀꜱᴛɪ ꜱᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴍᴇɴᴇ ᴄʜᴏᴅ ᴅᴀʟᴀ ʙᴏʜᴏᴛ ꜱᴀꜱᴛᴇ ꜱᴇ",
"ʙᴇᴛᴇ ᴛᴜ ʙᴀᴀᴘ ꜱᴇ ʟᴇɢᴀ ᴘᴀɴɢᴀ ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋᴏ ᴄʜᴏᴅ ᴅᴜɴɢᴀ ᴋᴀʀᴋᴇ ɴᴀɴɢᴀ 💦💋",
"ʜᴀʜᴀʜᴀʜ ᴍᴇʀᴇ ʙᴇᴛᴇ ᴀɢʟɪ ʙᴀᴀʀ ᴀᴘɴɪ ᴍᴀᴀᴋᴏ ʟᴇᴋᴇ ᴀᴀʏᴀ ᴍᴀᴛʜ ᴋᴀᴛ ᴏʀ ᴍᴇʀᴇ ᴍᴏᴛᴇ ʟᴜɴᴅ ꜱᴇ ᴄʜᴜᴅᴡᴀʏᴀ ᴍᴀᴛʜ ᴋᴀʀ",
"ᴄʜᴀʟ ʙᴇᴛᴀ ᴛᴜᴊʜᴇ ᴍᴀᴀꜰ ᴋɪᴀ 🤣ᴛᴜ ᴀʙʙ ᴀᴘɴɪ ᴍᴀᴋᴏ ʙʜᴇᴊ",
"ꜱʜᴀʀᴀᴍ ᴋᴀʀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴀ ʙʜᴏꜱᴅᴀ ᴋɪᴛɴᴀ ɢᴀᴀʟɪᴀ ꜱᴜɴᴡᴀʏᴇɢᴀ ᴀᴘɴɪ ᴍᴀᴀᴀ ʙᴇʜᴇɴ ᴋᴇ ᴜᴘᴇʀ",
"ᴀʙᴇ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴀᴜᴋᴀᴛ ɴʜɪ ʜᴇᴛᴏ ᴀᴘɴɪ ʀᴀɴᴅɪ ᴍᴀᴀᴋᴏ ʟᴇᴋᴇ ᴀᴀʏᴀ ᴍᴀᴛʜ ᴋᴀʀ ʜᴀʜᴀʜᴀʜᴀ",
"ᴋɪᴅᴢ ᴍᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴛᴇʀʀ ʟɪʏᴇ ʙʜᴀɪ ᴅᴇᴅɪʏᴀ",
"ᴊᴜɴɢʟᴇ ᴍᴇ ɴᴀᴄʜᴛᴀ ʜᴇ ᴍᴏʀᴇ ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴅᴀɪ ᴅᴇᴋᴋᴇ ꜱᴀʙ ʙᴏʟᴛᴇ ᴏɴᴄᴇ ᴍᴏʀᴇ ᴏɴᴄᴇ ᴍᴏʀᴇ 🤣🤣💦💋",
"ɢᴀʟɪ ɢᴀʟɪ ᴍᴇ ʀᴇʜᴛᴀ ʜᴇ ꜱᴀɴᴅ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅ ᴅᴀʟᴀ ᴏʀ ʙᴀɴᴀ ᴅɪᴀ ʀᴀɴᴅ 🤤🤣",
"ꜱᴀʙ ʙᴏʟᴛᴇ ᴍᴜᴊʜᴋᴏ ᴘᴀᴘᴀ ᴄʏᴜᴋɪ ᴍᴇɴᴇ ᴋʀᴅɪᴀ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴘʀᴇɢɴᴇɴᴛ 🤣🤣",
"ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ꜱᴜᴀʀ ᴋᴀ ʟᴏᴜᴅᴀ ᴏʀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴇʀᴀ ʟᴏᴅᴀ",
"ᴄʜᴀʟ ᴄʜᴀʟ ᴛᴜ ᴀᴘɴɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴄʜɪʏᴀ ᴅɪᴋᴀ",
"ʜᴀʜᴀʜᴀʜᴀ ʙᴀᴄʜʜᴇ ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴏ ᴄʜᴏᴅ ᴅɪᴀ ɴᴀɴɢᴀ ᴋᴀʀᴋᴇ",
"ᴛᴇʀɪ ɢꜰ ʜᴇ ʙᴀᴅɪ ꜱᴇxʏ ᴜꜱᴋᴏ ᴘɪʟᴀᴋᴇ ᴄʜᴏᴏᴅᴇɴɢᴇ ᴘᴇᴘꜱɪ",
"2 ʀᴜᴘᴀʏ ᴋɪ ᴘᴇᴘꜱɪ ᴛᴇʀɪ ᴍᴜᴍᴍʏ ꜱᴀʙꜱᴇ ꜱᴇxʏ 💋💦",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴇᴇᴍꜱ ꜱᴇ ᴄʜᴜᴅᴡᴀᴠᴜɴɢᴀ ᴍᴀᴅᴇʀᴄʜᴏᴏᴅ ᴋᴇ ᴘɪʟʟᴇ 💦🤣",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴜᴛʜᴋᴇ ꜰᴀʀᴀʀ ʜᴏᴊᴀᴠᴜɴɢᴀ ʜᴜɪ ʜᴜɪ ʜᴜɪ",
"ꜱᴘᴇᴇᴅ ʟᴀᴀᴀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ᴘɪʟʟᴇ 💋💦🤣",
"ᴀʀᴇ ʀᴇ ᴍᴇʀᴇ ʙᴇᴛᴇ ᴄʏᴜ ꜱᴘᴇᴇᴅ ᴘᴀᴋᴀᴅ ɴᴀ ᴘᴀᴀᴀ ʀᴀʜᴀ ᴀᴘɴᴇ ʙᴀᴀᴘ ᴋᴀ ʜᴀʜᴀʜᴀ ᴛᴇʀɪ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ🤣🤣",
"ꜱᴜɴ ꜱᴜɴ ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴊʜᴀɴᴛᴏ ᴋᴇ ꜱᴏᴜᴅᴀɢᴀʀ ᴀᴘɴɪ ᴍᴜᴍᴍʏ ᴋɪ ɴᴜᴅᴇꜱ ʙʜᴇᴊ",
"ᴀʙᴇ ꜱᴜɴ ʟᴏᴅᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴀ ʙʜᴏꜱᴅᴀ ꜰᴀᴀᴅ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴋʜᴜʟᴇ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴏᴅ ᴅᴀʟᴀ 🤣🤣💋",
"ꜱʜʀᴍ ᴋʀ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ ʏʜᴀ",
"ᴍᴇʀᴇ ʟᴜɴᴅ ᴋᴇ ʙᴀᴀᴀᴀᴀʟʟʟʟʟ ᴘᴋᴅ ᴊᴀʟᴅɪ sᴇ",
"ᴛᴜ ᴇᴋ ᴋᴀᴀᴍ ᴋʀ ᴀᴘɴɪ ᴍᴀ ʙʜᴇɴ ᴋᴏ ᴄᴜᴅᴡᴀ ʟᴇ ᴍᴇʀᴇ sᴛʜ",
"ʀɴᴅɪ ᴋᴇ ʟᴅᴋᴇᴇᴇᴇᴇᴇᴇᴇᴇ ᴄʜᴜᴘ ᴏʀ ᴄᴜᴅ ʏʜᴀ",
"ᴄʜᴜᴘ ᴛᴍᴋᴄ ᴋɪᴅꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱ",
"ᴀᴘɴɪ ɢᴀᴀɴᴅ ᴍᴇɪɴ ᴍᴜᴛʜɪ ᴅᴀᴀʟ",
"ᴍᴇʀᴀ ʟᴜɴᴅ ᴄʜᴏᴏꜱ ᴊᴀʟᴅɪ sᴇ",
"ᴀᴘɴɪ ᴍᴀ ᴋᴏ ᴄᴜsᴡᴀ ᴍᴇʀᴀ ʟᴜɴᴅ",
"ʙʜᴇɴ ᴋᴇ ʟᴀᴜᴅᴇ ᴛᴍᴄ",
"ʙʜᴇɴ ᴋᴇ ᴛᴀᴋᴋᴇ ᴛᴍʟ",
"ᴀʙʟᴀ ᴛᴇʀᴀ ᴋʜᴀɴ ᴅᴀɴ ᴄʜᴏᴅɴᴇ ᴋɪ ʙᴀʀɪɪɪ",
"ʙᴇᴛᴇ ᴛᴇʀɪ ᴍᴀ ꜱʙꜱᴇ ʙᴅɪ ʀᴀɴᴅ",
"ʟᴜɴᴅ ᴋᴇ ʙᴀᴀᴀʟ ᴊʜᴀᴛ ᴋᴇ ᴘɪꜱꜱꜱᴜᴜᴜᴜᴜᴜᴜ ᴛᴍᴋᴄ",
"ʟᴜɴᴅ ᴘᴇ ʟᴛᴋɪᴛ ᴍᴀᴀᴀʟʟʟʟ ᴋɪ ʙᴏɴᴅ ʜ ᴛᴜᴜᴜ",
"ᴋᴀꜱʜ ᴏꜱ ᴅɪɴ ᴍᴜᴛʜ ᴍʀᴋᴇ ꜱᴏᴊᴛᴀ ᴍ ᴛᴜ ᴘᴀɪᴅᴀ ɴᴀ ʜᴏᴛᴀᴀ",
"ɢʟᴛɪ ᴋʀᴅɪ ᴛᴜᴊᴡ ᴘᴀɪᴅᴀ ᴋʀᴋᴇ ᴛᴇʀʏ ᴍᴀ ɴᴇ ᴀʙ ᴄᴜᴅ ᴛᴜ ʏʜᴀ",
"ꜱᴘᴇᴇᴅ ᴘᴋᴅᴅᴅ",
"ɢᴀᴀɴᴅ ᴍᴀɪɴ ʟᴡᴅᴀ ᴅᴀʟ ʟᴇ ᴀᴘɴɪ ᴍᴇʀᴀᴀᴀ",
"ɢᴀᴀɴᴅ ᴍᴇɪɴ ʙᴀᴍʙᴜ ᴅᴇᴅᴜɴɢᴀᴀᴀᴀᴀᴀ",
"ɢᴀɴᴅ ꜰᴛɪ ᴋᴇ ʙᴀʟᴋᴋᴋ ᴛᴜ ᴄᴜᴅ ʏʜᴀ",
"ɢᴏᴛᴇ ᴋɪᴛɴᴇ ʙʜɪ ʙᴀᴅᴇ ʜᴏ, ʟᴜɴᴅ ᴋᴇ ɴɪᴄʜᴇ ʜɪ ʀᴇʜᴛᴇ ʜᴀɪ",
"ʜᴀᴢᴀᴀʀ ʟᴜɴᴅ ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴀɪɴ",
"ᴊʜᴀᴀɴᴛ ᴋᴇ ᴘɪꜱꜱᴜ ᴛᴍᴋᴄ sᴜɴ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴋᴀʟɪ ᴄʜᴜᴛ",
"ᴋʜᴏᴛᴇʏ ᴋɪ ᴀᴜʟᴅᴀ ᴇʏ ᴛᴜ ʀᴀɴᴅʏᴋᴇ",
"ᴋᴜᴛᴛᴇ ᴋᴀ ᴀᴡʟᴀᴛ ᴊᴀɪsᴀ ʟɢ ʀʜᴀ ᴛᴜ",
"ᴋᴜᴛᴛᴇ ᴋɪ ᴊᴀᴛ ᴊᴀɪsᴀ ᴇʏ ᴛᴜ ",
"ᴋᴜᴛᴛᴇ ᴋᴇ ᴛᴀᴛᴛᴀ ᴇʏ ᴛᴜ",
"ᴛᴇᴛɪ ᴍᴀ ᴋɪ.ᴄʜᴜᴛ , ᴛᴇʀɪ ᴍᴀ ʀɴᴅɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪ",
"ʟᴀᴠᴅᴇ ᴋᴇ ʙᴀʟ ᴘᴋᴅ ʟᴇ ᴍᴇʀᴇ",
"ᴍᴜʜ ᴍᴇɪ ʟᴇʟᴇ ᴍᴇʀᴀ ʟᴜɴᴅ",
"ʟᴜɴᴅ ᴋᴇ ᴘᴀꜱɪɴᴇ ᴄʜᴜᴘ ʙᴇᴛʜ ᴏʀ ᴄᴜᴅ",
"ᴍᴇʀᴇ ʟᴡᴅᴇ ᴋᴇ ʙᴀᴀᴀᴀᴀʟʟʟ",
"ʜᴀʜᴀʜᴀᴀᴀᴀᴀᴀ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ",
"ᴛᴜ ᴄʜᴜᴅ ɢʏᴀᴀᴀᴀᴀ",
"ʀᴀɴᴅɪ ᴋʜᴀɴᴇ ᴋɪ ᴜʟᴀᴅᴅᴅ",
"ꜱᴀᴅɪ ʜᴜɪ ɢᴀᴀɴᴅ",
"ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴀɪɴ ᴋᴜᴛᴇ ᴋᴀ ʟᴜɴᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏꜱᴅᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ",
"ᴛᴇʀᴇ ɢᴀᴀɴᴅ ᴍᴇɪɴ ᴋᴇᴇᴅᴇ ᴘᴀᴅᴀʏ",
"ɴʏ ɴʏ ᴛᴇʀʏ ᴍᴀᴀ ʀᴀɴᴅɪ",
"ꜱᴜɴɴ ᴍᴀᴅᴇʀᴄʜᴏᴅ ᴛᴍʟ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏꜱᴅᴀ",
"ʙᴇʜᴇɴ ᴋ ʟᴜɴᴅ ᴄʜᴜᴘᴄʜᴀᴘ ᴄᴜᴅ ʏʜᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ᴄʜᴜᴛ ᴋɪ ᴄʜᴛɴɪɪɪɪ",
"ᴍᴇʀᴀ ʟᴀᴡᴅᴀ ʟᴇʟᴇ ᴛᴜ ᴀɢᴀʀ ᴄʜᴀɪʏᴇ ᴛᴏʜ",
"ᴄʜᴜᴘ ɢᴀᴀɴᴅᴜ",
"ᴄʜᴜᴘ ᴄʜᴜᴛɪʏᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴘᴇ ᴊᴄʙ ᴄʜᴀᴅʜᴀᴀ ᴅᴜɴɢᴀ",
"ꜱᴀᴍᴊʜᴀᴀ ʟᴀᴡᴅᴇ",
"ʏᴀ ᴅᴜ ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴇ ᴛᴀᴘᴀᴀ ᴛᴀᴘ��",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴍᴇʀᴀ ʀᴏᴢ ʟᴇᴛɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴇ ꜱᴀᴀᴛʜ ᴍᴍꜱ ʙᴀɴᴀᴀ ᴄʜᴜᴋᴀ ʜᴜ���不�不",
"ᴛᴜ ᴄʜᴜᴛɪʏᴀ ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴛɪʏᴀ",
"ᴀᴜʀ ᴋɪᴛɴᴀ ʙᴏʟᴜ ʙᴇʏ ᴍᴀɴɴ ʙʜᴀʀ ɢᴀʏᴀ ᴍᴇʀᴀ�不",
"ᴛᴇʀɪɪɪɪɪɪ ᴍᴀᴀᴀᴀ ᴋɪ ᴄʜᴜᴛᴛᴛ ᴍᴇ ᴀʙᴄᴅ ʟɪᴋʜ ᴅᴜɴɢᴀ ᴍᴀᴀ ᴋᴇ ʟᴏᴅᴇ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ʟᴇᴋᴀʀ ᴍᴀɪ ꜰᴀʀᴀʀ",
"ᴛᴇʀʏ ᴍᴀᴀ ʀᴀɴɪᴅɪɪɪ",
"ᴄʜᴜᴘ ʙᴀᴄʜᴇᴇ ᴛᴍᴋᴄ",
"ᴛᴇʀʏ ᴍᴀᴋᴏᴄʜᴏᴅᴜ",
"ʀᴀɴᴅɪ ᴍᴀᴀ ᴛᴇʀʏ",
"ᴛᴜ ʀᴀɴᴅɪ ᴋᴇ ᴘɪʟʟᴀ ᴇʏ",
"ᴛᴇʀɪɪɪɪɪ ᴍᴀᴀᴀ ᴋᴏ ʙʜᴇᴊᴊᴊ",
"ᴛᴇʀᴀᴀ ʙᴀᴀᴀᴀᴘ ʜᴜ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ʜᴀᴀᴛ ᴅᴀᴀʟʟᴋᴇ ʙʜᴀᴀɢ ᴊᴀᴀɴᴜɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ꜱᴀʀᴀᴋ ᴘᴇ ʟᴇᴛᴀᴀ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ɢʙ ʀᴏᴀᴅ ᴘᴇ ʟᴇᴊᴀᴋᴇ ʙᴇᴄʜ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍÉ ᴋᴀᴀʟɪ ᴍɪᴛᴄʜ",
"ᴛᴇʀɪ ᴍᴀᴀ ꜱᴀꜱᴛɪ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴋᴀʙᴜᴛᴀʀ ᴅᴀᴀʟ ᴋᴇ ꜱᴏᴜᴘ ʙᴀɴᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴅᴇᴛᴏʟ ᴅᴀᴀʟ ᴅᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀᴀᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ʟᴀᴘᴛᴏᴘ",
"ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ʙɪꜱᴛᴀʀ ᴘᴇ ʟᴇᴛᴀᴀᴋᴇ ᴄʜᴏᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴀᴍᴇʀɪᴄᴀ ɢʜᴜᴍᴀᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ɴᴀᴀʀɪʏᴀʟ ᴘʜᴏʀ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴇ ɢᴀɴᴅ ᴍᴇ ᴅᴇᴛᴏʟ ᴅᴀᴀʟ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋᴏ ʜᴏʀʟɪᴄᴋꜱ ᴘɪʟᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ꜱᴀʀᴀᴋ ᴘᴇ ʟᴇᴛᴀᴀᴀ ᴅᴜɴɢᴀᴀᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀᴀ ʙʜᴏꜱᴅᴀ",
"ᴍᴇʀᴀᴀᴀ ʟᴜɴᴅ ᴘᴀᴋᴀᴅ ʟᴇ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴄʜᴜᴘ ᴛᴇʀɪ ᴍᴀᴀ ᴀᴋᴀᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪɪɪ ᴍᴀᴀ ᴄʜᴜꜰ ɢᴇʏɪɪ ᴋʏᴀᴀᴀ ʟᴀᴡᴅᴇᴇᴇ",
"ᴛᴇʀɪɪɪ ᴍᴀᴀ ᴋᴀᴀ ʙᴊꜱᴏᴅᴀᴀᴀ",
"ᴍᴀᴅᴀʀxʜᴏᴅᴅᴅ",
"ᴛᴇʀɪᴜᴜɪ ᴍᴀᴀᴀ ᴋᴀᴀ ʙʜꜱᴏᴅᴀᴀᴀ",
"ᴛᴇʀɪɪɪɪɪɪ ʙᴇʜᴇɴɴɴɴ ᴋᴏ ᴄʜᴏᴅᴅᴅᴜᴜᴜᴜ ᴍᴀᴅᴀʀxʜᴏᴅᴅᴅᴅ",
"ᴛᴜ ɴɪᴋᴀʟ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴄʜᴜᴘ ʀᴀɴᴅɪ ᴋᴇ ʙᴀᴄʜᴇ",
"ᴛᴇʀᴀ ᴍᴀᴀ ᴍᴇʀɪ ᴊᴀᴀɴ ᴇʏ",
"ᴛᴇʀɪ ꜱᴇxʏ ʙᴀʜᴇɴ ᴋɪ ᴄʜᴜᴛ ᴏᴘ"
"👩🏿      👩🏻‍🦳        👵🏼         👱🏿‍♀️     \n👖      👖        👖         👖     \n\nतेरी बहन /तेरी माँ /तेरी दादि/ तेरीभुआ.\n\nसब की 𝐂hu𝐃𝐀i hogi",
"तेरी माँ के（ ͜.人 ͜.）दबा दूंगा",
"तेरी मा चुदी हुई थी\nचुदी हुई है\nऔर चुदी हुई रहेगी \n\n\"MARK MY WORD\" 😈",
"𝐊ʏᴀ?\n𝐂ʏᴀ?\n𝐂ᴜᴀ?\n\n𝐌ᴛᴛ 𝐊ʀʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐏𝐞 𝐓ʜ𝐀ᴘᴘᴀᴅ 𝐌ᴀ𝐚ʀ 𝐃ᴜɴɢᴀ",
"˚∧＿∧  　+        — ͟͞͞🥛\n(  •‿• )つ  — ͟͞͞ 🥛 \nSpecial attack tery mummy ke chuchiya ka dudu 🐱🎀",
"Aaj Rakshabandhan Ke Avsar Pr तेरी मांँ मेरे लंड पर राखी Bandh Ke चुदेगी 😍🥰",
"Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye 😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
"Tery Maa Behen Ke Boshde Me Kya Maarun Jaldi Bata 😜🤙",
"Tery Maa\nⓘ Verified Randy // 🦅🔥",
"𝐒ᴀʏ 𝐑ᴀɴᴅɪʙᴀᴀᴢ 𝐃ᴀᴅᴅʏ 𓆩💗𓆪",
"𝐖ᴏ ʙʜɪ ᴋʏᴀ ᴅɪɴ ᴛʜᴇ ᴊᴀʙ ᴛʀʏ ᴍᴀᴀ ᴍᴜᴊʜᴇ 𝐀ᴘɴᴀ 𝐂ʜᴜᴛ 𝐃ᴇᴛɪ ᴛʜɪ ʏᴀᴀʀ 💔🥀👌🏻",
"𝐀ᴡᴀᴢ 𝐍ɪᴄʜᴇ 𝐆ᴜʟᴀᴀᴍ 🤢👇🏻",
"𝐓ʀʏ 𝐌ᴀᴀ ɴᴇ 𝐂ʜᴜᴅɴᴇ 𝐌ᴀɪ ɢᴏʟᴅ 𝐌ᴇᴅᴀʟ 𝐉ᴇᴇᴛᴀ ᴇʏ 𝐃ᴏꜱᴛ 🤩👑",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐋ᴜɴᴅ 🖕🏻😈",
"𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐀ᴘɴɪ 𝐁ᴇʜᴇɴ 𝐂ʜᴜᴅᴀ 🖕🏻😈",
"𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🖕🏻😈",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ ᴋʜᴏʟ ᴅᴜɴɢᴀ 🔓😈",
"𝐁ʜᴇɴᴄʜᴏᴅ ??ᴘɴɪ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🤡💩",
"𝐓𝐌𝐊𝐂 ᴘᴇ 𝐂ʜᴀᴘᴘᴀʟ 𝐌ᴀᴀʀᴜɴɢᴀ 👟💥",
"𝐁ʜᴏꜱᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
"𝐑ᴀɴᴅɪ ᴋɪ 𝐀ᴜʟᴀᴅ ᴄʜᴜᴘ ʜᴏ ᴊᴀ 🔇😒",
"𝐑ᴀɴᴅɪʙᴀᴀᴢ ka 𝐆ᴜʟᴀᴀᴍ ey ᴛᴜ ᴀʙ ᴛᴜ ʏʜᴀ ᴄᴜᴅᴋᴇ ᴅɪᴋʜᴀ ᴛᴇʀʏ ᴍᴀᴋᴏ ʟᴇᴋʀ 👑😎",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ɪʀᴄʜɪ 🌶️🖕🏻",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐏ᴀɪʀ 🦶🏻😈",
"𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ 🗑️😏",
"𝐑ᴀɴᴅɪ ᴋᴀ 𝐏ɪʟʟᴀ ʜᴀɪ ᴛᴜ 🐕💩",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴏ 𝐁ᴀᴢᴀᴀʀ 𝐌ᴇ 𝐂ʜᴏᴅᴜɴɢᴀ 🌃😈",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐆ᴀʀᴀᴍ 𝐓ᴇʟ 🌡️🖕🏻",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴍᴇʀɪ 𝐑ᴀɴᴅɪ 💋👿",
"𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴏ 𝐑ᴀᴀᴛ ʙʜᴀʀ 𝐂ʜᴏᴅᴜɴɢᴀ 🌙😈",
"𝐑ᴀɴᴅɪ ᴋᴀ 𝐁ᴀᴄᴄʜᴀ ʜᴀɪ ᴛᴜ ꜱᴀᴀʟᴇ 🤡💀",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐉ᴏᴏᴛᴀ 👞🖕🏻",
"𝐑ᴀɴᴅɪʙᴀᴀᴢ 𝐃ᴀᴅᴅʏ ᴋᴀ 𝐆ᴜʟᴀᴀᴍ ʜᴀɪ ᴛᴜ 🥀😤",
"ᴊɪꜱ ᴅɪɴ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ꜱᴏᴄʜᴀ ᴛʜᴀ ᴋᴀꜱʜ ᴀʙᴏʀᴛ ᴋᴀʀ ᴅᴇᴛɪ 💀🥀",
"𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 𝐓ᴇʀʏ 𝐌ᴀ 𝐂ᴜᴅ 𝐑ʜɪ🐕😂",
"𝐓ᴇʀʏ 𝐌ᴀ 𝐂ᴜᴅ 𝐑ʜɪ 𝐆ᴀʟɪ ᴋᴀ 𝐊ᴜᴛᴛᴀ ʜᴀɪ ᴛᴜ 🐕🗑️",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ᴍᴜᴊʜᴇ ᴅᴇᴋʜ ᴋᴇ ꜱᴏᴄʜᴀ ᴋᴀꜱʜ ʏᴇ ᴍᴇʀᴀ ʙᴇᴛᴀ ʜᴏᴛᴀ 🫦😏",
"𝐂ʜᴜᴘ ᴋᴀʀ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴀᴜᴋᴀᴛ ɴᴀʜɪ ᴍᴇʀᴇ ꜱᴀᴀᴍɴᴇ ʙᴏʟɴᴇ ᴋɪ 🤐💀",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴅᴀɪ ᴍᴇ ᴊᴀʙ ᴍᴀɪ ᴛʜᴀ ᴛᴏ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 💀😂",
"𝐁ʜᴀɢ ʏᴀʜᴀɴ ꜱᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 🐕💨",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ ꜱᴀᴅɪ 𝐌ᴇ ᴍᴇʀᴀ ʟᴜɴᴅ 💍😈",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴀᴘɴɪ 𝐌ᴀᴀ ᴍᴀᴛ ᴄʜᴜᴅᴀ 🖕🏻👹",
"𝐁ʜᴇɴᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
"tery ma cudke pgl dekh..𝐁𝐊𝐂 🦴🐕",
"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 𝐒ᴇ - 🦢💘",
"tery 𝐌ᴀᴀ cudke 𝐌ᴀʀʀ  𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ! 🌙",
"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga tery mako 😹💔🔥😆👊🏻💥",
"chudke bhaga kaise 😂💥🤣🤘🏻",
"ne toh - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ka lun muh me lelia tune or tery maa ne😂🙏🏻😂🙏🏻",
"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
"mkl lun te vaj 😂✊🏻💦",
"𝗧ᴍᴋ𝗕 pe - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ka hamla 😂⚔🔥💥",
"𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
"chl rndyce chud ke dikha 😂💥🤣🔥",
"tery 𝐌ᴀᴀ or bhen 𝐌ᴀʀʀ  𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
"tera baap bass - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ey 😂🎀",
"try maa hagte hue paad mari -#😹🔥🥀",
"𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓?? 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 /~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
"Tᴇʀɪ Mᴀᴀ Rᴀɴᴅɪ (🩷)—(❤️)—(🧡)—(💛)—(💚)—(🩵)—(💙)—(💜)—(🖤)—(🩶)—(🤍)—(🤎)—(🌸)—(✨)—(🌙)—(⭐)—(🦋)—(💎)—(👑)—(⚡)—(🔥)—(🌌)—(🎀)—(💫)—(🪽)—(🫧)—(🌸)—(💘)—(💓)—(💖)—(💕)—(💞)",
"Teri make hath me chakku se hole karke lund daluga apna 🤢🤢",
"Subha ho ya sham chudte rhena hai teri maaka kaam😂🔥😂🔥😂🔥",
"𝐓ᴜ 𝐒ᴡɪᴘᴇ 𝐊ᴀʀᴛᴀ 𝐑ᴇʜ 𝐌ᴀɪ ᴄʜᴀʟᴀ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴇ 𝐒ᴀᴛʜ 𝐊ʜᴇʟɴᴇ 😭😭",
"🍑\n🟨  😂\n🟨🟥🟥🟨\n     🟥🟥🟨\n     ⬛⬛ \n     ⬛⬛\nTery ma ki bund hi okhad li.",
"𝘗𝘺𝘢𝘴 𝘭𝘢𝘨 𝘳𝘢𝘩𝘪 𝘵𝘦𝘳𝘪 𝘮𝘢𝘢 𝘬𝘰 𝘤𝘰𝘥 𝘬𝘦 𝘱𝘺𝘢𝘴 𝘣𝘶𝘫𝘩𝘢𝘶𝘯𝘨𝘢 🖕🏿😂🔥🙏🏿",
"▶︎ •၊၊၊|။||။‌‌‌‌‌၊|• 0:60\n𝘋𝘦𝘬𝘩 𝘵𝘦𝘳𝘪 𝘣𝘦𝘩𝘦𝘯 ??𝘪 𝘤𝘩𝘪𝘬𝘩 😂😱🔥🙏🏿",
"      ᴹᴱ:\n👆       🤬 ᴷᴬᴴᴬ ᴮᴴᴬᴳᵀᴵ ᴴᴬᴵ ᴿᴬᴺᴰᴵ\n  🐛💤👔🤳\n            ⛽  👢\n          ⚡👟\n       🎸    🌂\n      👢       👢     ᵀᴱᴿᴵ ᴹᴬᴬ:🏃‍♀‍➡️ᴹᵁᴶᴴᴱ ᴹᴬᵀ ᶜᴴᴼᴰᴼ",
"🙌\n😛 ᴹᴱ:\n  |      👩 ᵀᴱᴿᴵ ᴹᴬᴬ:\n  |   8_/ 👐\n / \\  / \\\n  \"Take a look how i am chodunging your Mummy in ghodi pose 🗿\"",
"../\\_/\\\n  ( • _ •)  \n  /    >🍆 \n\nʏᴇ ᴘᴀᴋᴀᴅᴏ ᴀᴘᴋɪ ᴍᴏᴍ ᴋᴏ ᴀᴘɴᴇ ᴄʜᴜᴛ ᴍᴇ ɢʜᴜssᴀ ɴᴇ ᴍᴇ ᴋᴀᴀᴍ ᴀʏᴇɴɢᴀ 🤗",
"ㅤㅤ😎 ᴹᴱ:\n          |\\👐\n         / \\_\n━━━━━┓ ＼＼\n┓┓┓┓┓┃ᵀᴼᴴᴬᴿ ᴿᴬᴺᴰᴵ ᴹᴬᴬ:\n┓┓┓┓┓┃ ヽ😩ノ\n┓┓┓┓┓┃ 　 /　ᴼᴿᴵᴵ ᴬᴹᴹᴬ\n┓┓┓┓┓┃  ノ)　\n┓┓┓┓┓┃\n\nLE TERI MAA KO CHOD KAR FHEK DIA 🥸",
"😎 ᴍᴀɪ:\nく|)へ\n   〉\n￣┗┓       ヾ😫ｼ ᴛᴇʀɪ ᴍᴀᴀ:\n         ┗┓   ヘ/    \n             ┗┓ノ\n                 ┗┓       ヾ😨ｼ ᴛᴇʀᴀ ʙᴀᴀᴘ:\n                      ┗┓   ヘ/\n                          ┗┓ノ\n                               ┗┓       ヾ😩ｼ ᴛᴇʀᴀ ᴄʜᴀᴄʜᴀ:\n                                   ┗┓   ヘ/    \n                                       ┗┓ノ\nᴅᴇᴋʜ ᴀɪsᴇ ʜɪ ʟᴀᴀᴛ ᴍᴀᴀʀ ᴋᴀʀ ʙʜᴀɢᴀᴜɴɢᴀ ᴛᴇʀᴇ ᴋʜᴀᴀɴᴅᴀɴ ᴋᴏ 🤫🤣",
"╭👇 ͡ ͡° ͜   ͡ ͡°)╭👇 \n      \\   .   .\\\n        \\        \\\n         \\╰[ ]╯\\ \n          /   U   \\\n       👟       👟\n\nᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴍᴇʀᴀ ʟᴜɴᴅ ᴍᴜʙᴀʀᴀᴋ ʜᴏ 😝",
"Once a man said: \n\"You deserve all the chudayi and teri maa ki chutt dhulayi, and this text proves it! You should be proud!\" 🕊️",
"😏 ᴍᴀɪ:\n    | 👐💵\n    |//    💵\n    |          💸 ᴛᴇʀɪ ʀᴀɴᴅʏ ᴍᴀᴀ:\n   /\\            👯👯\n👟👟\n\nDᴇᴋʜ Kᴇsᴇ Tᴇʀɪ Mᴀᴀ Kᴏ Aᴘɴᴇ Pᴀɪsᴏ Sᴇ Rᴀɴᴅɪ Nᴀᴄʜ Kᴀʀᴡᴀ Rʜᴀ Hᴜ 🤙😎",
"Loading your maa ki chudai video 😳\n\n■■■■■■■■□\n99%",
"Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye  😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
"this message could't be display because teri maa randy ey",

]

reply_texts = [
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SHAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? saas aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝙃𝙄𝙎 𝙈𝙊𝙈 𝙋𝙍𝙊𝙋𝙀𝙍𝙇𝙔",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘼𝙎𝙆 𝙃𝙄𝙈 𝙏𝙊 𝘾𝙊𝙑𝙀𝙍 𝙃𝙄𝙎 𝙈𝙊𝙈'𝙎 𝘼𝙎𝙎",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙄𝙓 𝙈𝙔 𝘼‌𝙋𝙋𝙊𝙄𝙉𝙏𝙈𝙀𝙉𝙏 𝙒𝙄𝙏𝙃 𝙃𝙄𝙎 𝙎𝙄𝙎",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝘼𝙉𝘿 𝙏𝙃𝙍𝙊𝙒 𝙏𝙃𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽 𝙎𝙊𝙉",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘿𝙊 𝙉𝙊𝙏 𝙎𝙏𝙊𝙋 𝙁𝙐𝘾𝙆𝙄𝙉𝙂 𝙈𝙔 𝙂𝙐𝙇𝘼‌𝙈",
"𝙂𝙀𝙈𝙄𝙉𝙄 𝙎𝘼𝙄𝘿  𝙄𝙎 𝙍𝙉𝘿𝙔 𝙋𝙐𝙏𝙍𝘼",
"𝙋𝙀𝙍𝙋𝙇𝙀𝙓𝙄𝙏𝙔 𝙎𝘼𝙄𝘿 This 𝙄𝙎 𝙂𝙐𝙇𝘼𝙈",
"𝙂𝙍𝙊𝙆 𝘼𝙄 𝙎𝘼𝙄𝘿 𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽",
"𝘽𝙊𝙏 𝙎𝘼‌𝙄𝘿  𝙄𝙎 𝘾𝙃𝙐𝘿𝘼𝙆𝘼𝘿",
"𝙈𝙊𝘿𝙄 𝙎𝘼‌𝙄𝘿  𝙄𝙎 𝙋𝙊𝙇𝙀 𝘿𝘼𝙉𝘾𝙀𝙍",
"𝙏𝙍𝙐𝙈𝙋 𝙎𝘼𝙄𝘿 THis 𝙄𝙎 𝘽𝙇𝙊𝙊𝘿Y 𝙈𝙊𝙏𝙃𝙀𝙍𝙁*\"𝘾𝙆𝙀𝙍",
"𝗧𝗢𝗛𝗔𝗥 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜𝗡𝗚𝗙𝗜𝗦𝗛𝗘𝗥 𝗞𝗜 𝗕𝗢𝗧𝗧𝗟𝗘 𝗗𝗔𝗟 𝗞𝗘 𝗧𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗛𝗜 😱😂🤩",
"𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄 ✋ 𝐇𝐀𝐓𝐓𝐇 𝐃𝐀𝐋𝐊𝐄 👶 𝐁𝐀𝐂𝐂𝐇𝐄 𝐍𝐈𝐊𝐀𝐋 𝐃𝐔𝐍𝐆𝐀 😍",
"𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",
"𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗼 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣🔥",
"𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐈𝐍 𝐊𝐎 𝐀𝐏𝐍𝐄 𝐋𝐔𝐍𝐃 𝐏𝐑 𝐈𝐓𝐍𝐀 𝐉𝐇𝐔𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐊𝐈 𝐉𝐇𝐔𝐋𝐓𝐄 𝐉𝐇𝐔𝐋𝐓𝐄 𝐇𝐈 𝐁𝐀𝐂𝐇𝐀 𝐏𝐀𝐈𝐃𝐀 𝐊𝐑 𝐃𝐄𝐆𝐈 💦💋",
"𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐌𝐄 𝐑𝐄𝐇𝐓𝐀 𝐇𝐄 𝐒𝐀𝐍𝐃 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 𝐎𝐑 𝐁𝐀𝐍𝐀 𝐃𝐈𝐀 𝐑𝐀𝐍𝐃 🤤🤣",
"𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
"𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙇𝙀𝙏𝙄 𝙈𝙀𝙍𝙄 𝙇𝙐𝙉𝘿 𝘽𝘼𝘿𝙀 𝙈𝘼𝙎𝙏𝙄 𝙎𝙀 𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙆𝙊 𝙈𝙀𝙉𝙀 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝘼 𝘽𝙊𝙃𝙊𝙏 𝙎𝘼𝙎𝙏𝙀 𝙎𝙀",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",
"𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐈 𝐂𝐇𝐔𝐃𝐀𝐈 𝐊𝐎 𝐏𝐎𝐑𝐍𝐇𝐔𝐁.𝐂𝐎𝐌 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐒𝐔𝐀𝐑 𝐊𝐄 𝐂𝐇𝐎𝐃𝐄 🤣💋💦",
"𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 𝟑𝟎𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",
"𝐓𝐔𝐉𝐇𝐄 𝐀𝐁 𝐓𝐀𝐊 𝐍𝐀𝐇𝐈 𝐒𝐌𝐉𝐇 𝐀𝐘𝐀 𝐊𝐈 𝐌𝐀𝐈 𝐇𝐈 𝐇𝐔 𝐓𝐔𝐉𝐇𝐄 𝐏𝐀𝐈𝐃𝐀 𝐊𝐀𝐑𝐍𝐄 𝐖𝐀𝐋𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄𝐄 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝐄 𝐏𝐔𝐂𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 𝐁𝐀𝐂𝐇𝐄𝐄𝐄𝐄 🤩👊👤😍",
"𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐀𝐏𝐏𝐋𝐄 𝐊𝐀 𝟏𝟖𝐖 𝐖𝐀𝐋𝐀 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 🔥🤩",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
"𝙋𝘼𝙋𝘼 𝙆𝙄 𝙎𝙋𝙀𝙀𝘿 𝙈𝙏𝘾𝙃 𝙉𝙃𝙄 𝙃𝙊 𝙍𝙃𝙄 𝙆𝙔𝘼",
"𝙆𝙄𝙏𝙉𝙄 𝘾𝙃𝙊𝘿𝙐 𝙏𝙀𝙍𝙄 𝙈𝘼 𝘼𝘽 𝙊𝙍..",
"𝗧𝗘𝗥𝗜 𝗠𝗔𝗨𝗦𝗜 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗜𝗡𝗗𝗜𝗔𝗡 𝗥𝗔𝗜𝗟𝗪𝗔𝗬 🚂💥😂",
"𝙆𝙄𝙏𝙉𝙄 𝙂𝙇𝙄𝙔𝘼 𝙋𝘿𝙒𝙀𝙂𝘼 𝘼𝙋𝙉𝙄 𝙈𝘼 𝙆𝙊",
"𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗🤘🏻🙌🏻☠️",
"2 𝙍𝙐𝙋𝘼𝙔 𝙆𝙄 𝙋𝙀𝙋𝙎𝙄 𝙏𝙀𝙍𝙄 𝙈𝙐𝙈𝙈𝙔 𝙎𝘼𝘽𝙎𝙀 𝙎𝙀𝙓𝙔 💋💦",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐"
"Baap bhi bnale muje rndike",
"Tera baap randibaaz ey yaad ey tujhe",
"Tu apni Maa cuda na tympass",
"Oye unfunny swipe mtt kr",
"Oh hello bihari tera baap bihari or tu v bihari aaukat me rha kr.",
"Oyy kinner tujhe gc me aane ki permission kisne di.",
"Cudke dikha",
"Cudke dikha ek baar.",
"Sun sun ma cuda.",
"Teri maca bhosda.",
"Oye choti jati ke tmr.",
"Ky? jldi likh kidde.",
"Bihari com gang ke baap ko tag crega tu",
"Mujhe cya tu bihari ey tmkc bs",
"Jaldi se randibaaz papa bol",
"Side hoja bihari tery maa cud gai ab",
"Hye pgl bhg mat ache se cud",
"bhg ny randyke tu ajj",
"Hye pgl ke bche bhag mat",
"Hye dur hatt madchod ke bache",
"koi bat ny tery maa randy ey esliye maf cr rha hu tujhe",
"koi baat ny maa chudwa apni tu mafi de dunga",
"Ache se maa chudwa apni tu mafi mil jayegi tujhe",
"apni ma mat chuda muje swipe crke",
"Ache se apni ma cudwa tu swipe crke",
"Fr bolna na ki cudwa le apni ma swipe crke",
"Cya hua ma cud gyi tery",
"pr kese cud gyi tery ma",
"mujhe pta tha ma cud gai tery",
"mey ny manta ma cud gyi tery",
"teri ma rndy",
"lode se utr mc",
"lun mt chus mera",
"nikal madarchd",
"chup oye gashti k bache",
"makichut teri",
"chup rndyke",
"ma rndy teri",
"teri ma k hath todh k tere baap k muh me fasadunga randyke",
"leave le tu rndyke pasand nai aya meko",
"leave le tu randyke ider se",
"Leave le jldi se wrna ma chud gai tery",
"Leave ny lega maa randy tery",
"Smjh bat maa randy ey tery leave le",
"fast leave le kamjor randyke",
"tuto chup rndyk",
"oy hijde khana kha ke aa kamzor",
"teri mako ily rey🌚😂",
"chup chap chud tmkc",
"chupchap maa chudwa apni tu",
"shi se maa chudwa apni tu chupchap",
"fr se maa chudwa tu apni chupchap",
"shi se likh wrna ma chud gai tery",
"ma cyu chud gai tery chupchap",
"proof cr maa chud gyi tery",
"proof ey tery maa randy ey",
"proof ho chuka maa randy tery",
"Chup chillar",
"chup chup maa k bosda tery",
"oy hijde khana kha ke aa kamzor",
"chup madarchod ?",
"Ab tk cud gyi hogi tery maa ?",
"ny ny me kuch ny janta bs teri ma rndy ey",
"Sbse phele apni maa ko bol chudna kaam kre",
"Yaha bhi chuda tu rndyce pille",
"terimakabosda",
"teri to bhen cudegi",
"chup rndyke tommy",
"nikal madarchd cudke yha se",
"coz teri ma andhi randi he",
"nyto baap bol mujhe",
"nyny teri maa hogi rndii jo chudwati jogi",
"try ammi ce bhosde me emoji dal mc",
"cya ? chmr chud gya cya ?",
"tm chudri hogi frrto",
"cya ? kb ? pgl ey cya rndkek",
"cya sch mey pgl ey cya tu randyke cudwa li tune apni ma",
"itna sch ny bol ma chud gai tery",
"sch mey pgl ey tu apni ma cudwa lia mere sth",
"mtlb tmr",
"nyto",
"pura likh mc",
"tmr frrto",
"oh ok cudle fir",
"teri maa ka damad",
"cya ? ache se likhe pehle rndikebache",
"nyto teri maa chodne me vyast hu",
"nyto pgl ey cya kuch bi",
"oyee cya ? chud gya ?",
"chud mt hss",
"yur rndii mom",
"are sbki maa rndii or teri bi",
"are idar cudle ek baar",
"tri maa ci trh",
"ek line me tmr",
"Q",
"ocy ab chudle",
"pehele teri maa chodu",
"nyto",
"q ?",
"hyyy chud ke dika ek baar",
"oyee sun dost tmr",
"bhag ja raand maaf crr dunga",
"oyee pgl rndii idar aa",
"cya tmr frrto",
"oyee idar aake chud le chmr",
"nyto aese hi cud",
"oyee hyy aise hi cud lena",
"or chud le",
"chud ke dika or",
"hyy chudo na",
"chudo mt bhag jao",
"byyee hyy cya ?",
"Qchud q rhe ho ?",
"pgl ey cya mc",
"chud mt",
"cya pgl rndii idar aa",
"teri ammi ce bhosde me chappal",
"oyee idar aa mc",
"kmzror ey cya rndiek",
"cya likh rha ?",
"chud tha cya ?",
"oyee slide leke baat crmc",
"idar a teri maa chodu",
"oyee cp mt crr chudle",
"oyee hyy chud ke dika",
"idar aa try ma schofu khachar khachar",
"idar aa ja mc",
"hyy idar aake chudle",
"oyee kmzor mc idar aa",
"ye cya tmr",
"oyee ny cp ny crr",
"oyee pgl mt crr",
"cudle aram se mc",
"pgl ey cya rndiek",
"cp crce chudega !",
"baap ? mc mera coi ma baap ny ey mai upar se rocket pe beth ce bss teri ma chodne aya hu",
"Chota likh rndi k bache",
"Chota likha wrna try ma rndy",
"Try ma baka codega",
"Tmkc main burf",
"Bhikari ki jhat ma cuda le",
"Chodke tery ma marjayegi",
"Tmkc main Mount Everest",
"Muh mey lega lund mera",
"Hijde ki jhat chup wrna try ma rndi",
"Menu ny pta tery ma randy",
"Menu ki pta ma randy tery",
"Menu pta maa cud gai tery",
"Menu sb pta ma randy ey tery",
"Menu pr tery ma randy",
"Randy maa tery menu pta",
"Tenu or menu pta ey maa randy tery",
"Bs bs maa cudwa apni",
"Bs bs ma randy tery thnkss",
"Bs bs chudwa lia tu apni maa",
"Bs bs kamjor maa randy tery",
"Smjh gya apni ma cudwa le ab",
"smjh gya tery maa randy ey",
"smjh gya tu sabit kr maa randy tery",
"Cya hua ma cudwa tu apni",
"Easy maa cudwa le apni tu",
"Easy w8 ma chudwa le apni ab",
"Sans ari ha ky teri maa chudgi ajj",
"Teri maa ko bina sanss lete hue chodunga",
"chup randike kamjor",
"apni ma normie cudwa le tu",
"fr cya normie ma cud gai tery",
"bas thek tery ma randy",
"bas thek tery maa cud gyi",
"kamjor thi tery ma esliye cud gai",
"Mai sb janta ma cud gai tery",
"chl chl ht tery maa cud gyi",
"fr kaise cud gyi maa tery",
"maa tery randy ey",
"bas tery maa randy ey",
"fr randy ma tery ey",
"Kamjor ma ka bcha tu randyke",
"bhot gndi cud gai maa tery",
"pr kaise maa cud gai tery itna gnda",
"mujhe cya bta rha maa randy tery",
"mujhe cya pta ma cud gyi tery",
"fir mujhe ny pta maa cud gai tery",
"pta ny kon cod dia tery maa ko",
"ruk aaya tery ma codke",
"wait cr tery maa cod rha hu",
"wait cr rabdyke maa cud rhi ey tery",
"wait kr smjh rha tery ma codke",
"wait le thoda chodne de tery mako",
"ruk ja aand rkh dunga tery make liye",
"tery maa famous randy ey",
"maan lia mene maa randy sali tery",
"maan lia maa cud gai tery",
"shant beth randyke maa chudwa tu apni",
"shant bethke chudwa le apni mako tu",
"fr se shant Beth tu cud ab randyke yha",
"mere smjh ny aya maa randy tery",
"Le केला Kha tu madarchod",
"Hye tery ma cud gyi cya",
"hye tery maa mar gai cya",
"Hye sch bta com cod dia tery mako",
"Chl chod dia teri maa ko smjhle",
"Baki koi dikkat ny tery maa randy ey",
"baki sb jante ey ki maa chuddkad ey tery",
"mujhe cya pta tha tery maa cudne wli ey",
"pr mei kaise jnta tery ma ko koi chod dia",
"pr mera vi manna shi tha maa chud gai tery",
"pr wo glt ny tery maa randy ey",
"pr wo shi ey tery maa chuddkad ey",
"pr kaise kia maa chud gai tery omfoo",
"bur cheer dunga tri ma ka",
"teri ma ke dil me loda marke uski dhadkan rok dunga",
"lulle kha tri makabhosda",
"tri bhn ki bhosdi beta",
"tri ma rndi baat khtm",
"Sun ek maze ki baat batao kya teri maa randy ey"
"codu codu mako tery",
"aj cud gai tery maa oye",
"sun sun randy make bache tu",
"kilas ny randyke",
"mujhe cya pta tery bhen cud gai",
"pr pr cya hote ey tmkc",
"tmcl sunle",
"moot du tery maki chut mey",
"bhgny cudke dikha fr",
"fr se cudle tu",
"ye vi shi ey tery mkc bs",
"aj kuch ny ma cudwa tu apni",
"try kr mera lund chuske",
"tormakibur sun",
"tor maki fuddi oye",
"Haye Haye tery ma cud gai",
"oye lundke pasine..",
"kutte ke tatte sun",
"kutta jaisa cud rha tu",
"Muh mei le mera..",
"jhaat ke pissu sun tmkc",
"Hahahha ma cud gai tery",
"weak tatte uth",
"weak ey tu cud rha",
"weak ache se cud tu",
"weak tery ma cud rhi dekh",
"week tery ma cud gai ab",
"mujhe ny rok tu weak ey",
"chup hizde",
"okat ny meri ma cudwa tu apni",
"lun lega tery maki gand mei ?",
"tery maki bachi codu..",
"tery bhen ki chut aj fad du",
"speed lekr aa cudke dikha",
"speed ny tere andr weak prosn",
"ugly randyke chup",
"makafuddatery",
"tera baap ko tag kr..?",
"ache se tag kr randibaaz bhagwn ko..",
"cudke pgl ny ho tu",
"cudke pgl ho rha tu kid",
"ma to cud gai tery hawabzi cr..",
"bs ma codni ey tery",
"town mei cud tery mako lekr",
"tery ma sexy ko bej - randibaaz bhgwn pe",
"speed pkd cp ny kr",
"Try ma rendy",
"Bhkk cud",
"tey maa rndi",
"tery behen randi",
"Cud ja",
"tery didi rndi",
"Slow",
"teri Maiya ciodu",
"Bhag?",
"Bhak cud",
"Tma codu",
"Slow",
"Slow firse",
"Cudgrib",
"Try ma dou",
"tbkc codu",
"Net on off wali rndy",
"Oye try ma codu",
"Idhar aake cud chup chaap",
"tbkc mrdu",
"oi maake lodee",
"randyke beej",
"tmkc chodu",
"suar ke beej",
"net off on kr randyke ladke",
"Try ma cudi kese",
"Chup slow madharcod",
"tbkc codu kr msg delete",
"oi suar ke ladke",
"tmkc fufi",
"tery didi chudi",
"tmkc dikha",
"Cud ab",
"randyke cud",
"Bhak cud",
"cudle tbkc mru",
"tmkl cudle grib",
"tery behen vesiyaa rndi",
"Itna gnda chuda tu firse net on off",
"grib ke bete",
"Bhag ja lode tmkc maru dunga",
"tbkc mrdungaa",
"bhag tmkc",
"bhag tbkc",
"tbkc mey cp",
"cp tbkc mehh",
"cp tmkl meh",
"cp bol randyke",
"Abe cp bol randyke",
"double send ko cp tmkc codu",
"tbkc me cp cod dunga Aaj mehh",
"ht tbkc dalal ke bete.",
"Rndy jldi jldi cudq tryma",
"Para likhega..",
"Tra rndhbhak",
"Lagdi ke ladce cp bol",
"cp bol lagdi ke bete..",
"cudke cp bol",
"bhikari lund chus mera.",
"Low level cp cr",
"cp bol low level weak",
"mere lund pe ey tu hijde",
"free cudwa tery mako",
"Free mey cud tu randyke"
"speed ny weak tatte terme",
"kitni br cudwayega terymako",
"lund le randibaaz bapka",
"lun cus jaldi se randibaaz bapka",
"koi ny dekh rha cudle tu",
"cudle betichod ache se",
"maki chut tery bs yehi janta mey",
"cp bolega to tmkc",
"wrna tery ma cud jayegi",
"slow ey tu kid",
"jldi likh..tmkc",
"jldi likh..randce tu",
"tym se phle cudke dikha",
"tym hoga tery maa cudwa",
"ma cud gai tery tym se phle",
"uth randce ke ldke",
"macabosdatery",
"con kb cod dia mako tery",
"koi hoga tml",
"machar cudle tu",
"menu tery mako codna se",
"tery mako bol mujhe cod de",
"bs mey tery ma se cudna chta hu",
"Eww maka lode uth",
"Meow cr tery mako codu",
"lund rkh dia tery make fude pe",
"mera lund ke bal uth",
"kidee Zinda ho",
"mar ny kidde type kr",
"chup bkl",
"bc tery maki chut",
"mc randyke likh fast",
"fast likh randyke",
"fast likh kamzor"
"tery maki chut claim crwa",
"awz niche randce ke bche",
"sawal ny puch tery makabosda",
"fyter bnega lagde madrchod",
"oye kaale ro ke dikha",
"oye kaale roo ny",
"short ny cud tu bina ruke",
"short ny cud tu apni mako lekr",
"tery make sth tery bhen vi cudwa le",
"tery make sth tery didi vi cud gai",
"Chat fyter bnega randce codu tery mako",
"bol randibaaz daddy ey",
"bullyx randyke uth",
"mar marke cud rha tu",
"or tery ma marke cud gai"
"Jaldi likh rndyke bej",
"Or bda likh tmc",
"Or bda 2 line wla likh tmkc",
"Or bda oye likh tml",
"Teri maa ka bur",
"Oye keede",
"Randi ke ladke",
"Jaldi likh teri behen chodu",
"Mkl uth randi ke bacche",
"Teri nani meri maal",
"Tej likh randce",
"Oye maake lode mrenga",
"Teri maa chody",
"Teri Maiya ki gand",
"Tery dadi ka fudda",
"Mkl uth behencod",
"Teri maa ki bur de",
"Tery maa ka fudda me lauda",
"Teri maa chudva",
"Randi ke bete mar gaya",
"Teri maa ki chut mru",
"Jalid kr spam",
"Mc spam rokenga",
"Teri maaki chut spam kr",
"spam kr.maake lode",
"Randyke chode spam kr wrna cud tu",
"Spam kr kid",
"Noob teri maa chodu",
"Rndyke bete mar mat tu",
"Noob jaldi likh wrna tery maa rand",
"cud gai maa tery noob",
"uth randyke noob",
"chl cudke dikha noob",
"jldi typ cr noob halke",
"cud ke pgl ny ho noob",
"cud cud ke rand bnja tu noob",
"makichut tery noob",
"ganda cyu cud rha tu ?",
"itna gnda ny cud ache se cud",
"Maan le cud gya tu sun bat ab",
"makafudda fat gya tery ruk"
"BAAP BHI BNALE MUJE RNDIKE",
"TERA BAAP RANDIBAAZ EY YAAD EY TUJHE",
"TU APNI MAA CUDA NA TYMPASS",
"OYE UNFUNNY SWIPE MTT KR",
"OH HELLO BIHARI TERA BAAP BIHARI OR TU V BIHARI AAUKAT ME RHA KR.",
"OYY KINNER TUJHE GC ME AANE KI PERMISSION KISNE DI.",
"CUDKE DIKHA",
"CUDKE DIKHA EK BAAR.",
"SUN SUN MA CUDA.",
"TERI MACA BHOSDA.",
"OYE CHOTI JATI KE TMR.",
"KY? JLDI LIKH KIDDE.",
"BIHARI COM GANG KE BAAP KO TAG CREGA TU",
"MUJHE CYA TU BIHARI EY TMKC BS",
"JALDI SE RANDIBAAZ PAPA BOL",
"SIDE HOJA BIHARI TERY MAA CUD GAI AB",
"HYE PGL BHG MAT ACHE SE CUD",
"BHG NY RANDYKE TU AJJ",
"HYE PGL KE BCHE BHAG MAT",
"HYE DUR HATT MADCHOD KE BACHE",
"KOI BAT NY TERY MAA RANDY EY ESLIYE MAF CR RHA HU TUJHE",
"KOI BAAT NY MAA CHUDWA APNI TU MAFI DE DUNGA",
"ACHE SE MAA CHUDWA APNI TU MAFI MIL JAYEGI TUJHE",
"APNI MA MAT CHUDA MUJE SWIPE CRKE",
"ACHE SE APNI MA CUDWA TU SWIPE CRKE",
"FR BOLNA NA KI CUDWA LE APNI MA SWIPE CRKE",
"CYA HUA MA CUD GYI TERY",
"PR KESE CUD GYI TERY MA",
"MUJHE PTA THA MA CUD GAI TERY",
"MEY NY MANTA MA CUD GYI TERY",
"TERI MA RNDY",
"LODE SE UTR MC",
"LUN MT CHUS MERA",
"NIKAL MADARCHD",
"CHUP OYE GASHTI K BACHE",
"MAKICHUT TERI",
"CHUP RNDYKE",
"MA RNDY TERI",
"TERI MA K HATH TODH K TERE BAAP K MUH ME FASADUNGA RANDYKE",
"LEAVE LE TU RNDYKE PASAND NAI AYA MEKO",
"LEAVE LE TU RANDYKE IDER SE",
"LEAVE LE JLDI SE WRNA MA CHUD GAI TERY",
"LEAVE NY LEGA MAA RANDY TERY",
"SMJH BAT MAA RANDY EY TERY LEAVE LE",
"FAST LEAVE LE KAMJOR RANDYKE",
"TUTO CHUP RNDYK",
"OY HIJDE KHANA KHA KE AA KAMZOR",
"TERI MAKO ILY REY",
"CHUP CHAP CHUD TMKC",
"CHUPCHAP MAA CHUDWA APNI TU",
"SHI SE MAA CHUDWA APNI TU CHUPCHAP",
"FR SE MAA CHUDWA TU APNI CHUPCHAP",
"SHI SE LIKH WRNA MA CHUD GAI TERY",
"MA CYU CHUD GAI TERY CHUPCHAP",
"PROOF CR MAA CHUD GYI TERY",
"PROOF EY TERY MAA RANDY EY",
"PROOF HO CHUKA MAA RANDY TERY",
"CHUP CHILLAR",
"CHUP CHUP MA K BOSDA TERY",
"OY HIJDE KHANA KHA KE AA KAMZOR",
"CHUP MADARCHOD ?",
"AB TK CUD GYI HOGI TERY MAA ?",
"NY NY ME KUCH NY JANTA BS TERI MA RNDY EY",
"SBSE PHELE APNI MAA KO BOL CHUDNA KAAM KRE",
"YAHA BHI CHUDA TU RNDYCE PILLE",
"TERIMAKABOSDA",
"TERI TO BHEN CUDEGI",
"CHUP RNDYKE TOMMY",
"NIKAL MADARCHD CUDKE YHA SE",
"COZ TERI MA ANDHI RANDI HE",
"NYTO BAAP BOL MUJHE",
"NYNY TERI MAA HOGI RNDII JO CHUDWATI JOGI",
"TRY AMMI CE BHOSDE ME EMOJI DAL MC",
"CYA ? CHMR CHUD GYA CYA ?",
"TM CHUDRI HOGI FRRTO",
"CYA ? KB ? PGL EY CYA RNDKEK",
"CYA SCH MEY PGL EY CYA TU RANDYKE CUDWA LI TUNE APNI MA",
"ITNA SCH NY BOL MA CHUD GAI TERY",
"SCH MEY PGL EY TU APNI MA CUDWA LIA MERE STH",
"MTLB TMR",
"NYTO",
"PURA LIKH MC",
"TMR FRRTO",
"OH OK CUDLE FIR",
"TERI MAA KA DAMAD",
"CYA ? ACHE SE LIKHE PEHLE RNDIKEBACHE",
"NYTO TERI MAA CHODNE ME VYAST HU",
"NYTO PGL EY CYA KUCH BI",
"OYEE CYA ? CHUD GYA ?",
"CHUD MT HSS",
"YUR RNDII MOM",
"ARE SBKI MAA RNDII OR TERI BI",
"ARE IDAR CUDLE EK BAAR",
"TRI MAA CI TRH",
"EK LINE ME TMR",
"Q",
"OCY AB CHUDLE",
"PEHELE TERI MAA CHODU",
"NYTO",
"Q ?",
"HYYY CHUD KE DIKA EK BAAR",
"OYEE SUN DOST TMR",
"BHAG JA RAAND MAAF CRR DUNGA",
"OYEE PGL RNDII IDAR AA",
"CYA TMR FRRTO",
"OYEE IDAR Aake CHUD LE CHMR",
"NYTO AESE HI CUD",
"OYEE HYY AISE HI CUD LENA",
"OR CHUD LE",
"CHUD KE DIKA OR",
"HYY CHUDO NA",
"CHUDO MT BHAG JAO",
"BYYEE HYY CYA ?",
"QCHUD Q RHE HO ?",
"PGL EY CYA MC",
"CHUD MT",
"CYA PGL RNDII IDAR AA",
"TERI AMMI CE BHOSDE ME CHAPPAL",
"OYEE IDAR AA MC",
"KMZROR EY CYA RNDIEK",
"CYA LIKH RHA ?",
"CHUD THA CYA ?",
"OYEE SLIDE LEKE BAAT CRMC",
"IDAR A TERI MAA CHODU",
"OYEE CP MT CRR CHUDLE",
"OYEE HYY CHUD KE DIKA",
"IDAR AA TRY MA SCHOFU KHACHAR KHACHAR",
"IDAR AA JA MC",
"HYY IDAR Aake CHUDLE",
"OYEE KMZOR MC IDAR AA",
"YE CYA TMR",
"OYEE NY CP NY CRR",
"OYEE PGL MT CRR",
"CUDLE ARAM SE MC",
"PGL EY CYA RNDIEK",
"CP CRCE CHUDEGA !",
"BAAP ? MC MERA COI MA BAAP NY EY MAI UPAR SE ROCKET PE BETH CE BSS TERI MA CHODNE AYA HU",
"CHOTA LIKH RNDI K BACHE",
"CHOTA LIKHA WRNA TRY MA RNDY",
"TRY MA BAKA CODEGA",
"TMKC MAIN BURF",
"BHIKARI KI JHAT MA CUDA LE",
"CHODKE TERY MA MARJAYEGI",
"TMKC MAIN MOUNT EVEREST",
"MUH MEY LEGA LUND MERA",
"HIJDE KI JHAT CHUP WRNA TRY MA RNDI",
"MENU NY PTA TERY MA RANDY",
"MENU KI PTA MA RANDY TERY",
"MENU PTA MAA CUD GAI TERY",
"MENU SB PTA MA RANDY EY TERY",
"MENU PR TERY MA RANDY",
"RANDY MAA TERY MENU PTA",
"TENU OR MENU PTA EY MAA RANDY TERY",
"BS BS MAA CUDWA APNI",
"BS BS MA RANDY TERY THNKSS",
"BS BS CHUDWA LIA TU APNI MAA",
"BS BS KAMJOR MAA RANDY TERY",
"SMJH GYA APNI MA CUDWA LE AB",
"SMJH GYA TERY MAA RANDY EY",
"SMJH GYA TU SABIT KR MAA RANDY TERY",
"CYA HUA MA CUDWA TU APNI",
"EASY MAA CUDWA LE APNI TU",
"EASY W8 MA CHUDWA LE APNI AB",
"SANS ARI HA KY TERI MAA CHUDGI AJJ",
"TERI MAA KO BINA SANSS LETE HUE CHODUNGA",
"CHUP RANDIKE KAMJOR",
"APNI MA NORMIE CUDWA LE TU",
"FR CYA NORMIE MA CUD GAI TERY",
"BAS THEK TERY MA RANDY",
"BAS THEK TERY MAA CUD GYI",
"KAMJOR THI TERY MA ESLIYE CUD GAI",
"MAI SB JANTA MA CUD GAI TERY",
"CHL CHL HT TERY MAA CUD GYI",
"FR KAISE CUD GYI MAA TERY",
"MAA TERY RANDY EY",
"BAS TERY MAA RANDY EY",
"FR RANDY MA TERY EY",
"KAMJOR MA KA BCHA TU RANDYKE",
"BHOT GNDI CUD GAI MAA TERY",
"PR KAISE MAA CUD GAI TERY ITNA GNDA",
"MUJHE CYA BTA RHA MAA RANDY TERY",
"MUJHE CYA PTA MA CUD GYI TERY",
"FIR MUJHE NY PTA MAA CUD GAI TERY",
"PTA NY KON COD DIA TERY MAA KO",
"RUK AAYA TERY MA CODKE",
"WAIT CR TERY MAA COD RHA HU",
"WAIT CR RABDYKE MAA CUD RHI EY TERY",
"WAIT KR SMJH RHA TERY MA CODKE",
"WAIT LE THODA CHODNE DE TERY MAKO",
"RUK JA AAND RKH DUNGA TERY MAKE LIYE",
"TERY MAA FAMOUS RANDY EY",
"MAAN LIA MENE MAA RANDY SALI TERY",
"MAAN LIA MAA CUD GAI TERY",
"SHANT BETH RANDYKE MAA CHUDWA TU APNI",
"SHANT BETHKE CHUDWA LE APNI MAKO TU",
"FR SE SHANT BETH TU CUD AB RANDYKE YHA",
"MERE SMJH NY AYA MAA RANDY TERY",
"LE KELA KHA TU MADARCHOD",
"HYE TERY MA CUD GYI CYA",
"HYE TERY MAA MAR GAI CYA",
"HYE SCH BTA COM COD DIA TERY MAKO",
"CHL CHOD DIA TERI MAA KO SMJHLE",
"BAKI KOI DIKKAT NY TERY MAA RANDY EY",
"BAKI SB JANTE EY KI MAA CHUDDKAD EY TERY",
"MUJHE CYA PTA THA TERY MAA CUDNE WLI EY",
"PR MEI KAISE JNTA TERY MA KO KOI CHOD DIA",
"PR MERA VI MANNA SHI THA MAA CHUD GAI TERY",
"PR WO GLT NY TERY MAA RANDY EY",
"PR WO SHI EY TERY MAA CHUDDKAD EY",
"PR KAISE KIA MAA CHUD GAI TERY OMFOO",
"BUR CHEER DUNGA TRI MA KA",
"TERI MA KE DIL ME LODA MARKE USKI DHADKAN ROK DUNGA",
"LULLE KHA TRI MAKABHOSDA",
"TRI BHN KI BHOSDI BETA",
"TRI MA RNDI BAAT KHTM",
"SUN EK MAZE KI BAAT BATAO KYA TERI MAA RANDY EY",
"CODU CODU MAKO TERY",
"AJ CUD GAI TERY MAA OYE",
"SUN SUN RANDY MAKE BACHE TU",
"KILAS NY RANDYKE",
"MUJHE CYA PTA TERY BHEN CUD GAI",
"PR PR CYA HOTE EY TMKC",
"TMCL SUNLE",
"MOOT DU TERY MAKI CHUT MEY",
"BHGNY CUDKE DIKHA FR",
"FR SE CUDLE TU",
"YE VI SHI EY TERY MKC BS",
"AJ KUCH NY MA CUDWA TU APNI",
"TRY KR MERA LUND CHUSKE",
"TORMAKIBUR SUN",
"TOR MAKI FUDDI OYE",
"HAYE HAYE TERY MA CUD GAI",
"OYE LUNDKE PASINE..",
"KUTTE KE TATTE SUN",
"KUTTA JAISA CUD RHA TU",
"MUH MEI LE MERA..",
"JHAAT KE PISSU SUN TMKC",
"HAHAHHA MA CUD GAI TERY",
"WEAK TATTE UTH",
"WEAK EY TU CUD RHA",
"WEAK ACHE SE CUD TU",
"WEAK TERY MA CUD RHI DEKH",
"WEEK TERY MA CUD GAI AB",
"MUJHE NY ROK TU WEAK EY",
"CHUP HIZDE",
"OKAT NY MERI MA CUDWA TU APNI",
"LUN LEGA TERY MAKI GAND MEI ?",
"TERY MAKI BACHI CODU..",
"TERY BHEN KI CHUT AJ FAD DU",
"SPEED LEKR AA CUDKE DIKHA",
"SPEED NY TERE ANDR WEAK PROSN",
"UGLY RANDYKE CHUP",
"MAKAFUDDATERY",
"TERA BAAP KO TAG KR..?",
"ACHE SE TAG KR RANDIBAAZ BHAGWN KO..",
"CUDKE PGL NY HO TU",
"CUDKE PGL HO RHA TU KID",
"MA TO CUD GAI TERY HAWABZI CR..",
"BS MA CODNI EY TERY",
"TOWN MEI CUD TERY MAKO LEKR",
"TERY MA SEXY KO BEJ - RANDIBAAZ BHGWN PE",
"SPEED PKD CP NY KR",
"TRY MA RENDY",
"BHKK CUD",
"TEY MAA RNDI",
"TERY BEHEN RANDI",
"CUD JA TMC",
"TERY DIDI RNDI",
"SLOW",
"TERI MAIYA CIODU",
"BHAG?TMC ",
"BHAK CUD TML",
"TMA CODU",
"SLOW TMKC ",
"SLOW FIRSE TMKC ",
"CUDGRIB TML",
"TRY MA DOU",
"TBKC CODU",
"NET ON OFF WALI RNDY",
"OYE TRY MA CODU",
"IDHAR AAKE CUD CHUP CHAAP",
"TBKC MRDU",
"OI MAAKE LODEE",
"RANDYKE BEEJ",
"TMKC CHODU",
"SUAR KE BEEJ",
"NET OFF ON KR RANDYKE LADKE",
"TRY MA CUDI KESE",
"CHUP SLOW MADHARCOD",
"TBKC CODU KR MSG DELETE",
"OI SUAR KE LADKE",
"TMKC FUFI",
"TERY DIDI CHUDI",
"TMKC DIKHA",
"CUD AB",
"RANDYKE CUD",
"BHAK CUD",
"CUDLE TBKC MRU",
"TMKL CUDLE GRIB",
"TERY BEHEN VESITYA RNDI",
"ITNA GNDA CHUDA TU FIRSE NET ON OFF",
"GRIB KE BETE",
"BHAG JA LODE TMKC MARU DUNGA",
"TBKC MRDUNGAA",
"BHAG TMKC",
"BHAG TBKC",
"TBKC MEY CP",
"CP TBKC MEHH",
"CP TMKL MEH",
"CP BOL RANDYKE",
"ABE CP BOL RANDYKE",
"DOUBLE SEND KO CP TMKC CODU",
"TBKC ME CP COD DUNGA AAJ MEHH",
"HT TBKC DALAL KE BETE.",
"RNDY JLDI JLDI CUDQ TRYMA",
"PARA LIKHEGA..",
"TRA RNDHBHAK",
"LAGDI KE LADCE CP BOL",
"CP BOL LAGDI KE BETE..",
"CUDKE CP BOL",
"BHIKARI LUND CHUS MERA.",
"LOW LEVEL CP CR",
"CP BOL LOW LEVEL WEAK",
"MERE LUND PE EY TU HIJDE",
"FREE CUDWA TERY MAKO",
"FREE MEY CUD TU RANDYKE",
"SPEED NY WEAK TATTE TERME",
"KITNI BR CUDWAYEGA TERYMAKO",
"LUND LE RANDIBAAZ BAPKA",
"LUN CUS JALDI SE RANDIBAAZ BAPKA",
"KOI NY DEKH RHA CUDLE TU",
"CUDLE BETICHOD ACHE SE",
"MAKI CHUT TERY BS YEHI JANTA MEY",
"CP BOLEGA TO TMKC",
"WRNA TERY MA CUD JAYEGI",
"SLOW EY TU KID",
"JLDI LIKH..TMKC",
"JLDI LIKH..RANDCE TU",
"TYM SE PHLE CUDKE DIKHA",
"TYM HOGA TERY MAA CUDWA",
"MA CUD GAI TERY TYM SE PHLE",
"UTH RANDCE KE LDKE",
"MACABOSDATERY",
"CON KB COD DIA MAKO TERY",
"KOI HOGA TML",
"MACHAR CUDLE TU",
"MENU TERY MAKO CODNA SE",
"TERY MAKO BOL MUJHE COD DE",
"BS MEY TERY MA SE CUDNA CHTA HU",
"EWW MAKA LODE UTH",
"MEOW CR TERY MAKO CODU",
"LUND RKH DIA TERY MAKE FUDE PE",
"MERA LUND KE BAL UTH",
"KIDEE ZINDA HO",
"MAR NY KIDDE TYPE KR",
"CHUP BKL",
"BC TERY MAKI CHUT",
"MC RANDYKE LIKH FAST",
"FAST LIKH RANDYKE",
"FAST LIKH KAMZOR",
"TERY MAKI CHUT CLAIM CRWA",
"AWZ NICHE RANDCE KE BCHE",
"SAWAL NY PUCH TERY MAKABOSDA",
"FYTER BNEGA LAGDE MADRCHOD",
"OYE KAALE RO KE DIKHA",
"OYE KAALE ROO NY",
"SHORT NY CUD TU BINA RUKE",
"SHORT NY CUD TU APNI MAKO LEKR",
"TERY MAKE STH TERY BHEN VI CUDWA LE",
"TERY MAKE STH TERY DIDI VI CUD GAI",
"CHAT FYTER BNEGA RANDCE CODU TERY MAKO",
"BOL RANDIBAAZ DADDY EY",
"BULLYX RANDYKE UTH",
"MAR MARKE CUD RHA TU",
"OR TERY MA MARKE CUD GAI",
"JALDI LIKH RNDYKE BEJ",
"OR BDA LIKH TMC",
"OR BDA 2 LINE WLA LIKH TMKC",
"OR BDA OYE LIKH TML",
"TERI MAA KA BUR",
"OYE KEEDE",
"RANDI KE LADKE",
"JALDI LIKH TERI BEHEN CHODU",
"MKL UTH RANDI KE BACCHE",
"TERI NANI MERI MAAL",
"TEJ LIKH RANDCE",
"OYE MAAKE LODE MRENGA",
"TERI MAA CHODY",
"TERI MAIYA KI GAND",
"TERY DADI KA FUDDA",
"MKL UTH BEHENCOD",
"TERI MAA KI BUR DE",
"TERY MAA KA FUDDA ME LAUDA",
"TERI MAA CHUDVA",
"RANDI KE BETE MAR GAYA",
"TERI MAA KI CHUT MRU",
"JALID KR SPAM",
"MC SPAM ROKENGA",
"TERI MAAKI CHUT SPAM KR",
"SPAM KR.MAAKE LODE",
"RANDYKE CHODE SPAM KR WRNA CUD TU",
"SPAM KR KID",
"NOOB TERI MAA CHODU",
"RNDYKE BETE MAR MAT TU",
"NOOB JALDI LIKH WRNA TERY MAA RAND",
"CUD GAI MAA TERY NOOB",
"UTH RANDYKE NOOB",
"CHL CUDKE DIKHA NOOB",
"JLDI TYP CR NOOB HALKE",
"CUD KE PGL NY HO NOOB",
"CUD CUD KE RAND BNJA TU NOOB",
"MAKICHUT TERY NOOB",
"GANDA CYU CUD RHA TU ?",
"ITNA GNDA NY CUD ACHE SE CUD",
"MAAN LE CUD GYA TU SUN BAT AB",
"MAKAFUDDA FAT GYA TERY RUK",
"sʜᴀɴᴛ ʙᴇᴛʜ ᴍᴀᴅʀᴄʜᴏᴅ ᴡʀɴᴀ ᴍᴀᴋᴀʙᴏsᴅᴀ ᴛᴇᴇʏ.",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ..",
"ʟᴡᴅᴇ ᴋᴇ ʙᴀᴀᴀʟʟʟ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅᴋᴇ ᴘɢʟ ᴅᴇᴋʜ.",
"ᴍᴀᴄʜᴀʀ ᴋɪ ᴊʜᴀᴀᴛ ᴋᴇ ʙᴀᴀᴀʟʟʟʟ ᴄᴜᴅ ᴀᴄʜᴇ sᴇ ʏʜᴀᴘᴇ ᴛᴜ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴍ ᴅᴜ ᴛᴀᴘᴀ ᴛᴀᴘ?",
"ᴛᴇʀɪ ᴍᴀ ᴋᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪ ʙʜɴ ꜱʙꜱʙᴇ ʙᴅɪ ʀᴀɴᴅɪ.",
"ᴛᴇʀɪ ᴍᴀ ᴏꜱꜱᴇ ʙᴀᴅɪ ʀᴀɴᴅᴅᴅᴅᴅ",
"ᴛᴇʀᴀ ʙᴀᴀᴘ ʀᴀɴᴅɪʙᴀᴀᴢ ᴇʏ ᴅᴇᴋʜ",
"ᴋɪᴛɴɪ ᴄʜᴏᴅᴜ ᴛᴇʀɪ ᴍᴀ ᴀʙ ᴏʀ..",
"ᴛᴇʀɪ ᴍᴀ ᴄʜᴏᴅ ᴅɪ ʜᴍ ɴᴇ",
"ᴛᴇʀɪ ᴍᴀ ᴋᴇ ꜱᴛʜ ʀᴇᴇʟꜱ ʙɴᴇɢᴀ ʀᴏᴀᴅ ᴘᴇᴇ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴇᴋ ᴅᴀᴍ ᴛᴏᴘ ꜱᴇxʏ",
"ᴍᴀʟᴜᴍ ɴᴀ ᴘʜʀ ᴋᴇꜱᴇ ʟᴇᴛᴀ ʜᴜ ᴍ ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴛᴀᴘᴀ ᴛᴀᴘᴘᴘᴘᴘ",
"ʟᴜɴᴅ ᴋᴇ ᴄʜᴏᴅᴇ ᴛᴜ ᴋᴇʀᴇɢᴀ ᴛʏᴘɪɴɢ ᴋʀᴇɢᴀ ᴛᴍᴋᴄ",
"ꜱᴘᴇᴇᴅ ᴘᴋᴅ ʟᴡᴅᴇᴇᴇᴇ ᴡʀɴᴀ ᴍᴇʀᴀ ʟᴜɴᴅ ᴘᴋᴅ",
"ʙᴀᴀᴘ ᴋɪ ꜱᴘᴇᴇᴅ ᴍᴛᴄʜ ᴋʀʀʀ",
"ʟᴡᴅᴀ ʟᴇ ᴍᴇʀᴀ ᴊᴀʟᴅɪ sᴇ ᴛᴜ",
"ᴘᴀᴘᴀ ᴋɪ ꜱᴘᴇᴇᴅ ᴍᴛᴄʜ ɴʜɪ ʜᴏ ʀʜɪ ᴋʏᴀ ᴛᴇʀᴇsᴇ",
"ᴀʟᴇ ᴀʟᴇ ᴍᴇʟᴀ ʙᴄʜᴀᴀᴀᴀ ᴛᴇʀʏ ᴍᴀᴋᴀ ʙᴏsᴅᴀ sᴜɴ",
"ᴄʜᴜᴅ ɢʏᴀ ʀᴀɴᴅɪʙᴀᴀᴢ ᴘᴀᴘᴀ ꜱᴇᴇᴇ ᴛᴜ",
"ᴍᴇɴᴜ ᴋɪ ᴘᴛᴀ ᴛᴇʀʏ ᴍᴀ ᴄᴜᴅ ɢᴀɪ",
"ᴋᴏɪ ʙᴀᴀᴛ ɴʏ ᴍᴀᴀ ʀᴀɴᴅʏ ᴛᴇʀʏ",
"ʜᴀʜᴀʜᴀᴀᴀᴀᴀ ᴍᴀᴋᴀʙᴏsᴅᴀ ᴛᴇʀʏ",
"xʜᴜᴅ ɢᴀɪ ᴍᴀᴀ ᴛᴇʀʏ ᴋɪᴅꜱꜱꜱꜱ",
"ᴛᴇʀɪ ᴍᴀ ᴄʜᴜᴅ ɢʏɪ ᴀʙ ꜰʀᴀʀ ᴍᴛ ʜᴏɴᴀ",
"ʏᴇ ʟᴜɴᴅ ʟᴇ ᴍᴇʀᴀ ᴄʜʟ ᴊᴀʟᴅɪ sᴇ",
"ᴋɪᴅꜱꜱꜱ ꜰʀᴀʀ ɴᴀ ʜᴏ ᴛᴜ ʜᴀʜᴀʜʜ",
"ʙʜᴇɴ ᴋᴇ ʟᴡᴅᴇ ꜱʜʀᴍ ᴋʀ",
"ᴋɪᴛɴɪ ɢʟɪʏᴀ ᴘᴅᴡᴇɢᴀ ᴀᴘɴɪ ᴍᴀ ᴋᴏ",
"ᴄʜᴜᴘ ɴᴀʟʟɪɪ ʀᴀɴᴅʏᴋᴇ ʟᴀᴅᴋᴇ",
"ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ꜱᴀᴅᴀᴋ ᴘʀ ʟɪᴛᴀᴋᴇ ᴄʜᴏᴅ ᴅᴜɴɢᴀ 😂😆🤤",
"ᴀʙᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴀ ʙʜᴏꜱᴅᴀ ᴍᴀᴅᴇʀᴄʜᴏᴏᴅ ᴋʀ ᴘɪʟʟᴇ ᴘᴀᴘᴀ ꜱᴇ ʟᴀᴅᴇɢᴀ ᴛᴜ 😼😂🤤",
"ɢᴀʟɪ ɢᴀʟɪ ɴᴇ ꜱʜᴏʀ ʜᴇ ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ᴄʜᴏʀ ʜᴇ 💋💋💦",
"ᴀʙᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ᴘɪʟʟᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴄʜᴏᴅᴇ 😂👻🔥",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴀɪꜱᴇ ᴄʜᴏᴅᴀ ᴀɪꜱᴇ ᴄʜᴏᴅᴀ ᴛᴇʀɪ ᴍᴀᴀᴀ ʙᴇᴅ ᴘᴇʜɪ ᴍᴜᴛʜ ᴅɪᴀ 💦💦💦💦",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴇ ʙʜᴏꜱᴅᴇ ᴍᴇ ᴀᴀᴀɢ ʟᴀɢᴀᴅɪᴀ ᴍᴇʀᴀ ᴍᴏᴛᴀ ʟᴜɴᴅ ᴅᴀʟᴋᴇ 🔥🔥💦😆😆",
"ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅᴜ ᴄʜᴀʟ ɴɪᴋᴀʟ",
"ᴋɪᴛɴᴀ ᴄʜᴏᴅᴜ ᴛᴇʀɪ ʀᴀɴᴅɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ᴀʙʙ ᴀᴘɴɪ ʙᴇʜᴇɴ ᴋᴏ ʙʜᴇᴊ 😆👻🤤",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏᴛᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴘᴜʀᴀ ꜰᴀᴀᴅ ᴅɪᴀ ᴄʜᴜᴛʜ ᴀʙʙ ᴛᴇʀɪ ɢꜰ ᴋᴏ ʙʜᴇᴊ 😆💦🤤",
"ᴛᴇʀɪ ɢꜰ ᴋᴏ ᴇᴛɴᴀ ᴄʜᴏᴅᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴏᴅᴇ ᴛᴇʀɪ ɢꜰ ᴛᴏ ᴍᴇʀɪ ʀᴀɴᴅɪ ʙᴀɴɢᴀʏɪ ᴀʙʙ ᴄʜᴀʟ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅᴛᴀ ꜰɪʀꜱᴇ ♥️💦😆😆😆😆",
"ʜᴀʀɪ ʜᴀʀɪ ɢʜᴀᴀꜱ ᴍᴇ ᴊʜᴏᴘᴅᴀ ᴛᴇʀɪ ᴍᴀᴀᴋᴀ ʙʜᴏꜱᴅᴀ 🤣🤣💋💦",
"ᴄʜᴀʟ ᴛᴇʀᴇ ʙᴀᴀᴘ ᴋᴏ ʙʜᴇᴊ ᴛᴇʀᴀ ʙᴀꜱᴋᴀ ɴʜɪ ʜᴇ ᴘᴀᴘᴀ ꜱᴇ ʟᴀᴅᴇɢᴀ ᴛᴜ",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ʙᴏᴍʙ ᴅᴀʟᴋᴇ ᴜᴅᴀ ᴅᴜɴɢᴀ ᴍᴀᴀᴋᴇ ʟᴀᴡᴅᴇ",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴛʀᴀɪɴ ᴍᴇ ʟᴇᴊᴀᴋᴇ ᴛᴏᴘ ʙᴇᴅ ᴘᴇ ʟɪᴛᴀᴋᴇ ᴄʜᴏᴅ ᴅᴜɴɢᴀ ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ 🤣🤣💋💋",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴇ ɴᴜᴅᴇꜱ ɢᴏᴏɢʟᴇ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴀᴇᴡᴅᴇ 👻🔥",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴇ ɴᴜᴅᴇꜱ ɢᴏᴏɢʟᴇ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴀᴇᴡᴅᴇ 👻🔥",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴠɪᴅᴇᴏ ʙᴀɴᴀᴋᴇ xɴxx ᴘᴇ ɴᴇᴇʟᴀᴍ ᴋᴀʀᴅᴜɴɢᴀ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 💦💋",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋɪ ᴄʜᴜᴅᴀɪ ᴋᴏ ᴘᴏ*ʀɴʜᴜʙ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ꜱᴜᴀʀ ᴋᴇ ᴄʜᴏᴅᴇ 🤣💋💦",
"ᴀʙᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴛᴇʀᴇᴋᴏ ᴄʜᴀᴋᴋᴏ ꜱᴇ ᴘɪʟᴡᴀᴠᴜɴɢᴀ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ 🤣🤣",
"ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ꜰᴀᴀᴅᴋᴇ ʀᴀᴋᴅɪᴀ ᴍᴀᴀᴋᴇ ʟᴏᴅᴇ ᴊᴀᴀ ᴀʙʙ ꜱɪʟᴡᴀʟᴇ 👄👄",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴇʀᴀ ʟᴜɴᴅ ᴋᴀᴀʟᴀ",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ʟᴇᴛɪ ᴍᴇʀɪ ʟᴜɴᴅ ʙᴀᴅᴇ ᴍᴀꜱᴛɪ ꜱᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴍᴇɴᴇ ᴄʜᴏᴅ ᴅᴀʟᴀ ʙᴏʜᴏᴛ ꜱᴀꜱᴛᴇ ꜱᴇ",
"ʙᴇᴛᴇ ᴛᴜ ʙᴀᴀᴘ ꜱᴇ ʟᴇɢᴀ ᴘᴀɴɢᴀ ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋᴏ ᴄʜᴏᴅ ᴅᴜɴɢᴀ ᴋᴀʀᴋᴇ ɴᴀɴɢᴀ 💦💋",
"ʜᴀʜᴀʜᴀʜ ᴍᴇʀᴇ ʙᴇᴛᴇ ᴀɢʟɪ ʙᴀᴀʀ ᴀᴘɴɪ ᴍᴀᴀᴋᴏ ʟᴇᴋᴇ ᴀᴀʏᴀ ᴍᴀᴛʜ ᴋᴀᴛ ᴏʀ ᴍᴇʀᴇ ᴍᴏᴛᴇ ʟᴜɴᴅ ꜱᴇ ᴄʜᴜᴅᴡᴀʏᴀ ᴍᴀᴛʜ ᴋᴀʀ",
"ᴄʜᴀʟ ʙᴇᴛᴀ ᴛᴜᴊʜᴇ ᴍᴀᴀꜰ ᴋɪᴀ 🤣ᴛᴜ ᴀʙʙ ᴀᴘɴɪ ᴍᴀᴋᴏ ʙʜᴇᴊ",
"ꜱʜᴀʀᴀᴍ ᴋᴀʀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴀ ʙʜᴏꜱᴅᴀ ᴋɪᴛɴᴀ ɢᴀᴀʟɪᴀ ꜱᴜɴᴡᴀʏᴇɢᴀ ᴀᴘɴɪ ᴍᴀᴀᴀ ʙᴇʜᴇɴ ᴋᴇ ᴜᴘᴇʀ",
"ᴀʙᴇ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴀᴜᴋᴀᴛ ɴʜɪ ʜᴇᴛᴏ ᴀᴘɴɪ ʀᴀɴᴅɪ ᴍᴀᴀᴋᴏ ʟᴇᴋᴇ ᴀᴀʏᴀ ᴍᴀᴛʜ ᴋᴀʀ ʜᴀʜᴀʜᴀʜᴀ",
"ᴋɪᴅᴢ ᴍᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴛᴇʀʀ ʟɪʏᴇ ʙʜᴀɪ ᴅᴇᴅɪʏᴀ",
"ᴊᴜɴɢʟᴇ ᴍᴇ ɴᴀᴄʜᴛᴀ ʜᴇ ᴍᴏʀᴇ ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴅᴀɪ ᴅᴇᴋᴋᴇ ꜱᴀʙ ʙᴏʟᴛᴇ ᴏɴᴄᴇ ᴍᴏʀᴇ ᴏɴᴄᴇ ᴍᴏʀᴇ 🤣🤣💦💋",
"ɢᴀʟɪ ɢᴀʟɪ ᴍᴇ ʀᴇʜᴛᴀ ʜᴇ ꜱᴀɴᴅ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅ ᴅᴀʟᴀ ᴏʀ ʙᴀɴᴀ ᴅɪᴀ ʀᴀɴᴅ 🤤🤣",
"ꜱᴀʙ ʙᴏʟᴛᴇ ᴍᴜᴊʜᴋᴏ ᴘᴀᴘᴀ ᴄʏᴜᴋɪ ᴍᴇɴᴇ ᴋʀᴅɪᴀ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴘʀᴇɢɴᴇɴᴛ 🤣🤣",
"ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ꜱᴜᴀʀ ᴋᴀ ʟᴏᴜᴅᴀ ᴏʀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴇʀᴀ ʟᴏᴅᴀ",
"ᴄʜᴀʟ ᴄʜᴀʟ ᴛᴜ ᴀᴘɴɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴄʜɪʏᴀ ᴅɪᴋᴀ",
"ʜᴀʜᴀʜᴀʜᴀ ʙᴀᴄʜʜᴇ ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴏ ᴄʜᴏᴅ ᴅɪᴀ ɴᴀɴɢᴀ ᴋᴀʀᴋᴇ",
"ᴛᴇʀɪ ɢꜰ ʜᴇ ʙᴀᴅɪ ꜱᴇxʏ ᴜꜱᴋᴏ ᴘɪʟᴀᴋᴇ ᴄʜᴏᴏᴅᴇɴɢᴇ ᴘᴇᴘꜱɪ",
"2 ʀᴜᴘᴀʏ ᴋɪ ᴘᴇᴘꜱɪ ᴛᴇʀɪ ᴍᴜᴍᴍʏ ꜱᴀʙꜱᴇ ꜱᴇxʏ 💋💦",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴇᴇᴍꜱ ꜱᴇ ᴄʜᴜᴅᴡᴀᴠᴜɴɢᴀ ᴍᴀᴅᴇʀᴄʜᴏᴏᴅ ᴋᴇ ᴘɪʟʟᴇ 💦🤣",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴜᴛʜᴋᴇ ꜰᴀʀᴀʀ ʜᴏᴊᴀᴠᴜɴɢᴀ ʜᴜɪ ʜᴜɪ ʜᴜɪ",
"ꜱᴘᴇᴇᴅ ʟᴀᴀᴀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ᴘɪʟʟᴇ 💋💦🤣",
"ᴀʀᴇ ʀᴇ ᴍᴇʀᴇ ʙᴇᴛᴇ ᴄʏᴜ ꜱᴘᴇᴇᴅ ᴘᴀᴋᴀᴅ ɴᴀ ᴘᴀᴀᴀ ʀᴀʜᴀ ᴀᴘɴᴇ ʙᴀᴀᴘ ᴋᴀ ʜᴀʜᴀʜᴀ ᴛᴇʀɪ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ🤣🤣",
"ꜱᴜɴ ꜱᴜɴ ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴊʜᴀɴᴛᴏ ᴋᴇ ꜱᴏᴜᴅᴀɢᴀʀ ᴀᴘɴɪ ᴍᴜᴍᴍʏ ᴋɪ ɴᴜᴅᴇꜱ ʙʜᴇᴊ",
"ᴀʙᴇ ꜱᴜɴ ʟᴏᴅᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴀ ʙʜᴏꜱᴅᴀ ꜰᴀᴀᴅ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴋʜᴜʟᴇ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴏᴅ ᴅᴀʟᴀ 🤣🤣💋",
"ꜱʜʀᴍ ᴋʀ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ ʏʜᴀ",
"ᴍᴇʀᴇ ʟᴜɴᴅ ᴋᴇ ʙᴀᴀᴀᴀᴀʟʟʟʟʟ ᴘᴋᴅ ᴊᴀʟᴅɪ sᴇ",
"ᴛᴜ ᴇᴋ ᴋᴀᴀᴍ ᴋʀ ᴀᴘɴɪ ᴍᴀ ʙʜᴇɴ ᴋᴏ ᴄᴜᴅᴡᴀ ʟᴇ ᴍᴇʀᴇ sᴛʜ",
"ʀɴᴅɪ ᴋᴇ ʟᴅᴋᴇᴇᴇᴇᴇᴇᴇᴇᴇ ᴄʜᴜᴘ ᴏʀ ᴄᴜᴅ ʏʜᴀ",
"ᴄʜᴜᴘ ᴛᴍᴋᴄ ᴋɪᴅꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱ",
"ᴀᴘɴɪ ɢᴀᴀɴᴅ ᴍᴇɪɴ ᴍᴜᴛʜɪ ᴅᴀᴀʟ",
"ᴍᴇʀᴀ ʟᴜɴᴅ ᴄʜᴏᴏꜱ ᴊᴀʟᴅɪ sᴇ",
"ᴀᴘɴɪ ᴍᴀ ᴋᴏ ᴄᴜsᴡᴀ ᴍᴇʀᴀ ʟᴜɴᴅ",
"ʙʜᴇɴ ᴋᴇ ʟᴀᴜᴅᴇ ᴛᴍᴄ",
"ʙʜᴇɴ ᴋᴇ ᴛᴀᴋᴋᴇ ᴛᴍʟ",
"ᴀʙʟᴀ ᴛᴇʀᴀ ᴋʜᴀɴ ᴅᴀɴ ᴄʜᴏᴅɴᴇ ᴋɪ ʙᴀʀɪɪɪ",
"ʙᴇᴛᴇ ᴛᴇʀɪ ᴍᴀ ꜱʙꜱᴇ ʙᴅɪ ʀᴀɴᴅ",
"ʟᴜɴᴅ ᴋᴇ ʙᴀᴀᴀʟ ᴊʜᴀᴛ ᴋᴇ ᴘɪꜱꜱꜱᴜᴜᴜᴜᴜᴜᴜ ᴛᴍᴋᴄ",
"ʟᴜɴᴅ ᴘᴇ ʟᴛᴋɪᴛ ᴍᴀᴀᴀʟʟʟʟ ᴋɪ ʙᴏɴᴅ ʜ ᴛᴜᴜᴜ",
"ᴋᴀꜱʜ ᴏꜱ ᴅɪɴ ᴍᴜᴛʜ ᴍʀᴋᴇ ꜱᴏᴊᴛᴀ ᴍ ᴛᴜ ᴘᴀɪᴅᴀ ɴᴀ ʜᴏᴛᴀᴀ",
"ɢʟᴛɪ ᴋʀᴅɪ ᴛᴜᴊᴡ ᴘᴀɪᴅᴀ ᴋʀᴋᴇ ᴛᴇʀʏ ᴍᴀ ɴᴇ ᴀʙ ᴄᴜᴅ ᴛᴜ ʏʜᴀ",
"ꜱᴘᴇᴇᴅ ᴘᴋᴅᴅᴅ",
"ɢᴀᴀɴᴅ ᴍᴀɪɴ ʟᴡᴅᴀ ᴅᴀʟ ʟᴇ ᴀᴘɴɪ ᴍᴇʀᴀᴀᴀ",
"ɢᴀᴀɴᴅ ᴍᴇɪɴ ʙᴀᴍʙᴜ ᴅᴇᴅᴜɴɢᴀᴀᴀᴀᴀᴀ",
"ɢᴀɴᴅ ꜰᴛɪ ᴋᴇ ʙᴀʟᴋᴋᴋ ᴛᴜ ᴄᴜᴅ ʏʜᴀ",
"ɢᴏᴛᴇ ᴋɪᴛɴᴇ ʙʜɪ ʙᴀᴅᴇ ʜᴏ, ʟᴜɴᴅ ᴋᴇ ɴɪᴄʜᴇ ʜɪ ʀᴇʜᴛᴇ ʜᴀɪ",
"ʜᴀᴢᴀᴀʀ ʟᴜɴᴅ ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴀɪɴ",
"ᴊʜᴀᴀɴᴛ ᴋᴇ ᴘɪꜱꜱᴜ ᴛᴍᴋᴄ sᴜɴ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴋᴀʟɪ ᴄʜᴜᴛ",
"ᴋʜᴏᴛᴇʏ ᴋɪ ᴀᴜʟᴅᴀ ᴇʏ ᴛᴜ ʀᴀɴᴅʏᴋᴇ",
"ᴋᴜᴛᴛᴇ ᴋᴀ ᴀᴡʟᴀᴛ ᴊᴀɪsᴀ ʟɢ ʀʜᴀ ᴛᴜ",
"ᴋᴜᴛᴛᴇ ᴋɪ ᴊᴀᴛ ᴊᴀɪsᴀ ᴇʏ ᴛᴜ ",
"ᴋᴜᴛᴛᴇ ᴋᴇ ᴛᴀᴛᴛᴀ ᴇʏ ᴛᴜ",
"ᴛᴇᴛɪ ᴍᴀ ᴋɪ.ᴄʜᴜᴛ , ᴛᴇʀɪ ᴍᴀ ʀɴᴅɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪ",
"ʟᴀᴠᴅᴇ ᴋᴇ ʙᴀʟ ᴘᴋᴅ ʟᴇ ᴍᴇʀᴇ",
"ᴍᴜʜ ᴍᴇɪ ʟᴇʟᴇ ᴍᴇʀᴀ ʟᴜɴᴅ",
"ʟᴜɴᴅ ᴋᴇ ᴘᴀꜱɪɴᴇ ᴄʜᴜᴘ ʙᴇᴛʜ ᴏʀ ᴄᴜᴅ",
"ᴍᴇʀᴇ ʟᴡᴅᴇ ᴋᴇ ʙᴀᴀᴀᴀᴀʟʟʟ",
"ʜᴀʜᴀʜᴀᴀᴀᴀᴀᴀ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ",
"ᴛᴜ ᴄʜᴜᴅ ɢʏᴀᴀᴀᴀᴀ",
"ʀᴀɴᴅɪ ᴋʜᴀɴᴇ ᴋɪ ᴜʟᴀᴅᴅᴅ",
"ꜱᴀᴅɪ ʜᴜɪ ɢᴀᴀɴᴅ",
"ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴀɪɴ ᴋᴜᴛᴇ ᴋᴀ ʟᴜɴᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏꜱᴅᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ",
"ᴛᴇʀᴇ ɢᴀᴀɴᴅ ᴍᴇɪɴ ᴋᴇᴇᴅᴇ ᴘᴀᴅᴀʏ",
"ɴʏ ɴʏ ᴛᴇʀʏ ᴍᴀᴀ ʀᴀɴᴅɪ",
"ꜱᴜɴɴ ᴍᴀᴅᴇʀᴄʜᴏᴅ ᴛᴍʟ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏꜱᴅᴀ",
"ʙᴇʜᴇɴ ᴋ ʟᴜɴᴅ ᴄʜᴜᴘᴄʜᴀᴘ ᴄᴜᴅ ʏʜᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ᴄʜᴜᴛ ᴋɪ ᴄʜᴛɴɪɪɪɪ",
"ᴍᴇʀᴀ ʟᴀᴡᴅᴀ ʟᴇʟᴇ ᴛᴜ ᴀɢᴀʀ ᴄʜᴀɪʏᴇ ᴛᴏʜ",
"ᴄʜᴜᴘ ɢᴀᴀɴᴅᴜ",
"ᴄʜᴜᴘ ᴄʜᴜᴛɪʏᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴘᴇ ᴊᴄʙ ᴄʜᴀᴅʜᴀᴀ ᴅᴜɴɢᴀ",
"ꜱᴀᴍᴊʜᴀᴀ ʟᴀᴡᴅᴇ",
"ʏᴀ ᴅᴜ ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴇ ᴛᴀᴘᴀᴀ ᴛᴀᴘ��",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴍᴇʀᴀ ʀᴏᴢ ʟᴇᴛɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴇ ꜱᴀᴀᴛʜ ᴍᴍꜱ ʙᴀɴᴀᴀ ᴄʜᴜᴋᴀ ʜᴜ���不�不",
"ᴛᴜ ᴄʜᴜᴛɪʏᴀ ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴛɪʏᴀ",
"ᴀᴜʀ ᴋɪᴛɴᴀ ʙᴏʟᴜ ʙᴇʏ ᴍᴀɴɴ ʙʜᴀʀ ɢᴀʏᴀ ᴍᴇʀᴀ�不",
"ᴛᴇʀɪɪɪɪɪɪ ᴍᴀᴀᴀᴀ ᴋɪ ᴄʜᴜᴛᴛᴛ ᴍᴇ ᴀʙᴄᴅ ʟɪᴋʜ ᴅᴜɴɢᴀ ᴍᴀᴀ ᴋᴇ ʟᴏᴅᴇ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ʟᴇᴋᴀʀ ᴍᴀɪ ꜰᴀʀᴀʀ",
"ᴛᴇʀʏ ᴍᴀᴀ ʀᴀɴɪᴅɪɪɪ",
"ᴄʜᴜᴘ ʙᴀᴄʜᴇᴇ ᴛᴍᴋᴄ",
"ᴛᴇʀʏ ᴍᴀᴋᴏᴄʜᴏᴅᴜ",
"ʀᴀɴᴅɪ ᴍᴀᴀ ᴛᴇʀʏ",
"ᴛᴜ ʀᴀɴᴅɪ ᴋᴇ ᴘɪʟʟᴀ ᴇʏ",
"ᴛᴇʀɪɪɪɪɪ ᴍᴀᴀᴀ ᴋᴏ ʙʜᴇᴊᴊᴊ",
"ᴛᴇʀᴀᴀ ʙᴀᴀᴀᴀᴘ ʜᴜ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ʜᴀᴀᴛ ᴅᴀᴀʟʟᴋᴇ ʙʜᴀᴀɢ ᴊᴀᴀɴᴜɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ꜱᴀʀᴀᴋ ᴘᴇ ʟᴇᴛᴀᴀ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ɢʙ ʀᴏᴀᴅ ᴘᴇ ʟᴇᴊᴀᴋᴇ ʙᴇᴄʜ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍÉ ᴋᴀᴀʟɪ ᴍɪᴛᴄʜ",
"ᴛᴇʀɪ ᴍᴀᴀ ꜱᴀꜱᴛɪ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴋᴀʙᴜᴛᴀʀ ᴅᴀᴀʟ ᴋᴇ ꜱᴏᴜᴘ ʙᴀɴᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴅᴇᴛᴏʟ ᴅᴀᴀʟ ᴅᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀᴀᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ʟᴀᴘᴛᴏᴘ",
"ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ʙɪꜱᴛᴀʀ ᴘᴇ ʟᴇᴛᴀᴀᴋᴇ ᴄʜᴏᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴀᴍᴇʀɪᴄᴀ ɢʜᴜᴍᴀᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ɴᴀᴀʀɪʏᴀʟ ᴘʜᴏʀ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴇ ɢᴀɴᴅ ᴍᴇ ᴅᴇᴛᴏʟ ᴅᴀᴀʟ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋᴏ ʜᴏʀʟɪᴄᴋꜱ ᴘɪʟᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ꜱᴀʀᴀᴋ ᴘᴇ ʟᴇᴛᴀᴀᴀ ᴅᴜɴɢᴀᴀᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀᴀ ʙʜᴏꜱᴅᴀ",
"ᴍᴇʀᴀᴀᴀ ʟᴜɴᴅ ᴘᴀᴋᴀᴅ ʟᴇ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴄʜᴜᴘ ᴛᴇʀɪ ᴍᴀᴀ ᴀᴋᴀᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪɪɪ ᴍᴀᴀ ᴄʜᴜꜰ ɢᴇʏɪɪ ᴋʏᴀᴀᴀ ʟᴀᴡᴅᴇᴇᴇ",
"ᴛᴇʀɪɪɪ ᴍᴀᴀ ᴋᴀᴀ ʙᴊꜱᴏᴅᴀᴀᴀ",
"ᴍᴀᴅᴀʀxʜᴏᴅᴅᴅ",
"ᴛᴇʀɪᴜᴜɪ ᴍᴀᴀᴀ ᴋᴀᴀ ʙʜꜱᴏᴅᴀᴀᴀ",
"ᴛᴇʀɪɪɪɪɪɪ ʙᴇʜᴇɴɴɴɴ ᴋᴏ ᴄʜᴏᴅᴅᴅᴜᴜᴜᴜ ᴍᴀᴅᴀʀxʜᴏᴅᴅᴅᴅ",
"ᴛᴜ ɴɪᴋᴀʟ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴄʜᴜᴘ ʀᴀɴᴅɪ ᴋᴇ ʙᴀᴄʜᴇ",
"ᴛᴇʀᴀ ᴍᴀᴀ ᴍᴇʀɪ ᴊᴀᴀɴ ᴇʏ",
"ᴛᴇʀɪ ꜱᴇxʏ ʙᴀʜᴇɴ ᴋɪ ᴄʜᴜᴛ ᴏᴘ"
"👩🏿      👩🏻‍🦳        👵🏼         👱🏿‍♀️     \n👖      👖        👖         👖     \n\nतेरी बहन /तेरी माँ /तेरी दादि/ तेरीभुआ.\n\nसब की 𝐂hu𝐃𝐀i hogi",
"तेरी माँ के（ ͜.人 ͜.）दबा दूंगा",
"तेरी मा चुदी हुई थी\nचुदी हुई है\nऔर चुदी हुई रहेगी \n\n\"MARK MY WORD\" 😈",
"𝐊ʏᴀ?\n𝐂ʏᴀ?\n𝐂ᴜᴀ?\n\n𝐌ᴛᴛ 𝐊ʀʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐏𝐞 𝐓ʜ𝐀ᴘᴘᴀᴅ 𝐌ᴀ𝐚ʀ 𝐃ᴜɴɢᴀ",
"˚∧＿∧  　+        — ͟͞͞🥛\n(  •‿• )つ  — ͟͞͞ 🥛 \nSpecial attack tery mummy ke chuchiya ka dudu 🐱🎀",
"Aaj Rakshabandhan Ke Avsar Pr तेरी मांँ मेरे लंड पर राखी Bandh Ke चुदेगी 😍🥰",
"Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye 😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
"Tery Maa Behen Ke Boshde Me Kya Maarun Jaldi Bata 😜🤙",
"Tery Maa\nⓘ Verified Randy // 🦅🔥",
"𝐒ᴀʏ 𝐑ᴀɴᴅɪʙᴀᴀᴢ 𝐃ᴀᴅᴅʏ 𓆩💗𓆪",
"𝐖ᴏ ʙʜɪ ᴋʏᴀ ᴅɪɴ ᴛʜᴇ ᴊᴀʙ ᴛʀʏ ᴍᴀᴀ ᴍᴜᴊʜᴇ 𝐀ᴘɴᴀ 𝐂ʜᴜᴛ 𝐃ᴇᴛɪ ᴛʜɪ ʏᴀᴀʀ 💔🥀👌🏻",
"𝐀ᴡᴀᴢ 𝐍ɪᴄʜᴇ 𝐆ᴜʟᴀᴀᴍ 🤢👇🏻",
"𝐓ʀʏ 𝐌ᴀᴀ ɴᴇ 𝐂ʜᴜᴅɴᴇ 𝐌ᴀɪ ɢᴏʟᴅ 𝐌ᴇᴅᴀʟ 𝐉ᴇᴇᴛᴀ ᴇʏ 𝐃ᴏꜱᴛ 🤩👑",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐋ᴜɴᴅ 🖕🏻😈",
"𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐀ᴘɴɪ 𝐁ᴇʜᴇɴ 𝐂ʜᴜᴅᴀ 🖕🏻😈",
"𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🖕🏻😈",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ ᴋʜᴏʟ ᴅᴜɴɢᴀ 🔓😈",
"𝐁ʜᴇɴᴄʜᴏᴅ ??ᴘɴɪ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🤡💩",
"𝐓𝐌𝐊𝐂 ᴘᴇ 𝐂ʜᴀᴘᴘᴀʟ 𝐌ᴀᴀʀᴜɴɢᴀ 👟💥",
"𝐁ʜᴏꜱᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
"𝐑ᴀɴᴅɪ ᴋɪ 𝐀ᴜʟᴀᴅ ᴄʜᴜᴘ ʜᴏ ᴊᴀ 🔇😒",
"𝐑ᴀɴᴅɪʙᴀᴀᴢ ka 𝐆ᴜʟᴀᴀᴍ ey ᴛᴜ ᴀʙ ᴛᴜ ʏʜᴀ ᴄᴜᴅᴋᴇ ᴅɪᴋʜᴀ ᴛᴇʀʏ ᴍᴀᴋᴏ ʟᴇᴋʀ 👑😎",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ɪʀᴄʜɪ 🌶️🖕🏻",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐏ᴀɪʀ 🦶🏻😈",
"𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ 🗑️😏",
"𝐑ᴀɴᴅɪ ᴋᴀ 𝐏ɪʟʟᴀ ʜᴀɪ ᴛᴜ 🐕💩",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴏ 𝐁ᴀᴢᴀᴀʀ 𝐌ᴇ 𝐂ʜᴏᴅᴜɴɢᴀ 🌃😈",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐆ᴀʀᴀᴍ 𝐓ᴇʟ 🌡️🖕🏻",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴍᴇʀɪ 𝐑ᴀɴᴅɪ 💋👿",
"𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴏ 𝐑ᴀᴀᴛ ʙʜᴀʀ 𝐂ʜᴏᴅᴜɴɢᴀ 🌙😈",
"𝐑ᴀɴᴅɪ ᴋᴀ 𝐁ᴀᴄᴄʜᴀ ʜᴀɪ ᴛᴜ ꜱᴀᴀʟᴇ 🤡💀",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐉ᴏᴏᴛᴀ 👞🖕🏻",
"𝐑ᴀɴᴅɪʙᴀᴀᴢ 𝐃ᴀᴅᴅʏ ᴋᴀ 𝐆ᴜʟᴀᴀᴍ ʜᴀɪ ᴛᴜ 🥀😤",
"ᴊɪꜱ ᴅɪɴ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ꜱᴏᴄʜᴀ ᴛʜᴀ ᴋᴀꜱʜ ᴀʙᴏʀᴛ ᴋᴀʀ ᴅᴇᴛɪ 💀🥀",
"𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 𝐓ᴇʀʏ 𝐌ᴀ 𝐂ᴜᴅ 𝐑ʜɪ🐕😂",
"𝐓ᴇʀʏ 𝐌ᴀ 𝐂ᴜᴅ 𝐑ʜɪ 𝐆ᴀʟɪ ᴋᴀ 𝐊ᴜᴛᴛᴀ ʜᴀɪ ᴛᴜ 🐕🗑️",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ᴍᴜᴊʜᴇ ᴅᴇᴋʜ ᴋᴇ ꜱᴏᴄʜᴀ ᴋᴀꜱʜ ʏᴇ ᴍᴇʀᴀ ʙᴇᴛᴀ ʜᴏᴛᴀ 🫦😏",
"𝐂ʜᴜᴘ ᴋᴀʀ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴀᴜᴋᴀᴛ ɴᴀʜɪ ᴍᴇʀᴇ ꜱᴀᴀᴍɴᴇ ʙᴏʟɴᴇ ᴋɪ 🤐💀",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴅᴀɪ ᴍᴇ ᴊᴀʙ ᴍᴀɪ ᴛʜᴀ ᴛᴏ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 💀😂",
"𝐁ʜᴀɢ ʏᴀʜᴀɴ ꜱᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 🐕💨",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ ꜱᴀᴅɪ 𝐌ᴇ ᴍᴇʀᴀ ʟᴜɴᴅ 💍😈",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴀᴘɴɪ 𝐌ᴀᴀ ᴍᴀᴛ ᴄʜᴜᴅᴀ 🖕🏻👹",
"𝐁ʜᴇɴᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
"tery ma cudke pgl dekh..𝐁𝐊𝐂 🦴🐕",
"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 𝐒ᴇ - 🦢💘",
"tery 𝐌ᴀᴀ cudke 𝐌ᴀʀʀ  𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ! 🌙",
"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga tery mako 😹💔🔥😆👊🏻💥",
"chudke bhaga kaise 😂💥🤣🤘🏻",
"ne toh - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ka lun muh me lelia tune or tery maa ne😂🙏🏻😂🙏🏻",
"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
"mkl lun te vaj 😂✊🏻💦",
"𝗧ᴍᴋ𝗕 pe - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ka hamla 😂⚔🔥💥",
"𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
"chl rndyce chud ke dikha 😂💥🤣🔥",
"tery 𝐌ᴀᴀ or bhen 𝐌ᴀʀʀ  𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
"tera baap bass - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ey 😂🎀",
"try maa hagte hue paad mari -#😹🔥🥀",
"𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓?? 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 /~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
"Tᴇʀɪ Mᴀᴀ Rᴀɴᴅɪ (🩷)—(❤️)—(🧡)—(💛)—(💚)—(🩵)—(💙)—(💜)—(🖤)—(🩶)—(🤍)—(🤎)—(🌸)—(✨)—(🌙)—(⭐)—(🦋)—(💎)—(👑)—(⚡)—(🔥)—(🌌)—(🎀)—(💫)—(🪽)—(🫧)—(🌸)—(💘)—(💓)—(💖)—(💕)—(💞)",
"Teri make hath me chakku se hole karke lund daluga apna 🤢🤢",
"Subha ho ya sham chudte rhena hai teri maaka kaam😂🔥😂🔥😂🔥",
"𝐓ᴜ 𝐒ᴡɪᴘᴇ 𝐊ᴀʀᴛᴀ 𝐑ᴇʜ 𝐌ᴀɪ ᴄʜᴀʟᴀ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴇ 𝐒ᴀᴛʜ 𝐊ʜᴇʟɴᴇ 😭😭",
"🍑\n🟨  😂\n🟨🟥🟥🟨\n     🟥🟥🟨\n     ⬛⬛ \n     ⬛⬛\nTery ma ki bund hi okhad li.",
"𝘗𝘺𝘢𝘴 𝘭𝘢𝘨 𝘳𝘢𝘩𝘪 𝘵𝘦𝘳𝘪 𝘮𝘢𝘢 𝘬𝘰 𝘤𝘰𝘥 𝘬𝘦 𝘱𝘺𝘢𝘴 𝘣𝘶𝘫𝘩𝘢𝘶𝘯𝘨𝘢 🖕🏿😂🔥🙏🏿",
"▶︎ •၊၊၊|။||။‌‌‌‌‌၊|• 0:60\n𝘋𝘦𝘬𝘩 𝘵𝘦𝘳𝘪 𝘣𝘦𝘩𝘦𝘯 ??𝘪 𝘤𝘩𝘪𝘬𝘩 😂😱🔥🙏🏿",
"      ᴹᴱ:\n👆       🤬 ᴷᴬᴴᴬ ᴮᴴᴬᴳᵀᴵ ᴴᴬᴵ ᴿᴬᴺᴰᴵ\n  🐛💤👔🤳\n            ⛽  👢\n          ⚡👟\n       🎸    🌂\n      👢       👢     ᵀᴱᴿᴵ ᴹᴬᴬ:🏃‍♀‍➡️ᴹᵁᴶᴴᴱ ᴹᴬᵀ ᶜᴴᴼᴰᴼ",
"🙌\n😛 ᴹᴱ:\n  |      👩 ᵀᴱᴿᴵ ᴹᴬᴬ:\n  |   8_/ 👐\n / \\  / \\\n  \"Take a look how i am chodunging your Mummy in ghodi pose 🗿\"",
"../\\_/\\\n  ( • _ •)  \n  /    >🍆 \n\nʏᴇ ᴘᴀᴋᴀᴅᴏ ᴀᴘᴋɪ ᴍᴏᴍ ᴋᴏ ᴀᴘɴᴇ ᴄʜᴜᴛ ᴍᴇ ɢʜᴜssᴀ ɴᴇ ᴍᴇ ᴋᴀᴀᴍ ᴀʏᴇɴɢᴀ 🤗",
"ㅤㅤ😎 ᴹᴱ:\n          |\\👐\n         / \\_\n━━━━━┓ ＼＼\n┓┓┓┓┓┃ᵀᴼᴴᴬᴿ ᴿᴬᴺᴰᴵ ᴹᴬᴬ:\n┓┓┓┓┓┃ ヽ😩ノ\n┓┓┓┓┓┃ 　 /　ᴼᴿᴵᴵ ᴬᴹᴹᴬ\n┓┓┓┓┓┃  ノ)　\n┓┓┓┓┓┃\n\nLE TERI MAA KO CHOD KAR FHEK DIA 🥸",
"😎 ᴍᴀɪ:\nく|)へ\n   〉\n￣┗┓       ヾ😫ｼ ᴛᴇʀɪ ᴍᴀᴀ:\n         ┗┓   ヘ/    \n             ┗┓ノ\n                 ┗┓       ヾ😨ｼ ᴛᴇʀᴀ ʙᴀᴀᴘ:\n                      ┗┓   ヘ/\n                          ┗┓ノ\n                               ┗┓       ヾ😩ｼ ᴛᴇʀᴀ ᴄʜᴀᴄʜᴀ:\n                                   ┗┓   ヘ/    \n                                       ┗┓ノ\nᴅᴇᴋʜ ᴀɪsᴇ ʜɪ ʟᴀᴀᴛ ᴍᴀᴀʀ ᴋᴀʀ ʙʜᴀɢᴀᴜɴɢᴀ ᴛᴇʀᴇ ᴋʜᴀᴀɴᴅᴀɴ ᴋᴏ 🤫🤣",
"╭👇 ͡ ͡° ͜   ͡ ͡°)╭👇 \n      \\   .   .\\\n        \\        \\\n         \\╰[ ]╯\\ \n          /   U   \\\n       👟       👟\n\nᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴍᴇʀᴀ ʟᴜɴᴅ ᴍᴜʙᴀʀᴀᴋ ʜᴏ 😝",
"Once a man said: \n\"You deserve all the chudayi and teri maa ki chutt dhulayi, and this text proves it! You should be proud!\" 🕊️",
"😏 ᴍᴀɪ:\n    | 👐💵\n    |//    💵\n    |          💸 ᴛᴇʀɪ ʀᴀɴᴅʏ ᴍᴀᴀ:\n   /\\            👯👯\n👟👟\n\nDᴇᴋʜ Kᴇsᴇ Tᴇʀɪ Mᴀᴀ Kᴏ Aᴘɴᴇ Pᴀɪsᴏ Sᴇ Rᴀɴᴅɪ Nᴀᴄʜ Kᴀʀᴡᴀ Rʜᴀ Hᴜ 🤙😎",
"Loading your maa ki chudai video 😳\n\n■■■■■■■■□\n99%",
"Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye  😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
"this message could't be display because teri maa randy ey",
]


fun_texts = [
"तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
"तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
"तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭"
]

flag_texts = [
"🇮🇳 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇮🇳",
"🇯🇵 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇯🇵",
"🇺🇸 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇺🇸",
"🇬🇧 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇬🇧",
"🇰🇷 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇰🇷",
"🇩🇪 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇩🇪",
"🇫🇷 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐅ʀᴀɴᴄᴇ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇫🇷",
"🇮🇹 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ᴛᴀʟʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇮🇹",
"🇧🇷 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐁ʀᴀᴢɪʟ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇧🇷",
"🇨🇦 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐂ᴀɴᴀᴅᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇨🇦",
]

heart_replies = [
"𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💛 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💚 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💙 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💜 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💖 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💗 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💓 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💞 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💕 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💘 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💝 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💟 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❣️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❣️ ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🔥͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️‍🔥 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆❤️‍🩹͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚❤️‍🩹 ݁˖⭑.ᐟ",
]

# ─── DEATHGOD REPLIES ────────────────────────────────────────────────────
deathgod_replies = [
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SHAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? saas aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? SAAS aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  /\\~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝙃𝙄𝙎 𝙈𝙊𝙈 𝙋𝙍𝙊𝙋𝙀𝙍𝙇𝙔",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘼𝙎𝙆 𝙃𝙄𝙈 𝙏𝙊 𝘾𝙊𝙑𝙀𝙍 𝙃𝙄𝙎 𝙈𝙊𝙈'𝙎 𝘼𝙎𝙎",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙄𝙓 𝙈𝙔 𝘼‌𝙋𝙋𝙊𝙄𝙉𝙏𝙈𝙀𝙉𝙏 𝙒𝙄𝙏𝙃 𝙃𝙄𝙎 𝙎𝙄𝙎",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝘼𝙉𝘿 𝙏𝙃𝙍𝙊𝙒 𝙏𝙃𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽 𝙎𝙊𝙉",
"𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘿𝙊 𝙉𝙊𝙏 𝙎𝙏𝙊𝙋 𝙁𝙐𝘾𝙆𝙄𝙉𝙂 𝙈𝙔 𝙂𝙐𝙇𝘼‌𝙈",
"𝙂𝙀𝙈𝙄𝙉𝙄 𝙎𝘼𝙄𝘿  𝙄𝙎 𝙍𝙉𝘿𝙔 𝙋𝙐𝙏𝙍𝘼",
"𝙋𝙀𝙍𝙋𝙇𝙀𝙓𝙄𝙏𝙔 𝙎𝘼𝙄𝘿 This 𝙄𝙎 𝙂𝙐𝙇𝘼𝙈",
"𝙂𝙍𝙊𝙆 𝘼𝙄 𝙎𝘼𝙄𝘿 𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽",
"𝘽𝙊𝙏 𝙎𝘼‌𝙄𝘿  𝙄𝙎 𝘾𝙃𝙐𝘿𝘼𝙆𝘼𝘿",
"𝙈𝙊𝘿𝙄 𝙎𝘼‌𝙄𝘿  𝙄𝙎 𝙋𝙊𝙇𝙀 𝘿𝘼𝙉𝘾𝙀𝙍",
"𝙏𝙍𝙐𝙈𝙋 𝙎𝘼𝙄𝘿 THis 𝙄𝙎 𝘽𝙇𝙊𝙊𝘿Y 𝙈𝙊𝙏𝙃𝙀𝙍𝙁*\"𝘾𝙆𝙀𝙍",
"𝗧𝗢𝗛𝗔𝗥 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜 𝗣𝗨𝗥𝗜 𝗞𝗜𝗡𝗚𝗙𝗜𝗦𝗛𝗘𝗥 𝗞𝗜 𝗕𝗢𝗧𝗧𝗟𝗘 𝗗𝗔𝗟 𝗞𝗘 𝗧𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗔𝗡𝗗𝗘𝗥 𝗛𝗜 😱😂🤩",
"𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄 ✋ 𝐇𝐀𝐓𝐓𝐇 𝐃𝐀𝐋𝐊𝐄 👶 𝐁𝐀𝐂𝐂𝐇𝐄 𝐍𝐈𝐊𝐀𝐋 𝐃𝐔𝐍𝐆𝐀 😍",
"𝐓𝐄𝐑𝐀 𝐏𝐄𝐇𝐋𝐀 𝐁𝐀𝐀𝐏 𝐇𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃",
"𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗘 𝗦𝗔𝗔𝗧𝗛 𝗟𝗨𝗗𝗼 𝗞𝗛𝗘𝗟𝗧𝗘 𝗞𝗛𝗘𝗟𝗧𝗘 𝗨𝗦𝗞𝗘 𝗠𝗨𝗛 𝗠𝗘 𝗔𝗣𝗡𝗔 𝗟𝗢𝗗𝗔 𝗗𝗘 𝗗𝗨𝗡𝗚𝗔☝🏻☝🏻😬",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗦𝗨𝗧𝗟𝗜 𝗕𝗢𝗠𝗕 𝗙𝗢𝗗 𝗗𝗨𝗡𝗚𝗔 𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗝𝗛𝗔𝗔𝗧𝗘 𝗝𝗔𝗟 𝗞𝗘 𝗞𝗛𝗔𝗔𝗞 𝗛𝗢 𝗝𝗔𝗬𝗘𝗚𝗜💣🔥",
"𝐓𝐄𝐑𝐈 𝐕𝐀𝐇𝐄𝐈𝐍 𝐊𝐎 𝐀𝐏𝐍𝐄 𝐋𝐔𝐍𝐃 𝐏𝐑 𝐈𝐓𝐍𝐀 𝐉𝐇𝐔𝐋𝐀𝐀𝐔𝐍𝐆𝐀 𝐊𝐈 𝐉𝐇𝐔𝐋𝐓𝐄 𝐉𝐇𝐔𝐋𝐓𝐄 𝐇𝐈 𝐁𝐀𝐂𝐇𝐀 𝐏𝐀𝐈𝐃𝐀 𝐊𝐑 𝐃𝐄𝐆𝐈 💦💋",
"𝐆𝐀𝐋𝐈 𝐆𝐀𝐋𝐈 𝐌𝐄 𝐑𝐄𝐇𝐓𝐀 𝐇𝐄 𝐒𝐀𝐍𝐃 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐋𝐀 𝐎𝐑 𝐁𝐀𝐍𝐀 𝐃𝐈𝐀 𝐑𝐀𝐍𝐃 🤤🤣",
"𝐒𝐀𝐁 𝐁𝐎𝐋𝐓𝐄 𝐌𝐔𝐉𝐇𝐊𝐎 𝐏𝐀𝐏𝐀 𝐊𝐘𝐎𝐔𝐍𝐊𝐈 𝐌𝐄𝐍𝐄 𝐁𝐀𝐍𝐀𝐃𝐈𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐄𝐍𝐓 🤣🤣",
"𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙇𝙀𝙏𝙄 𝙈𝙀𝙍𝙄 𝙇𝙐𝙉𝘿 𝘽𝘼𝘿𝙀 𝙈𝘼𝙎𝙏𝙄 𝙎𝙀 𝙏𝙀𝙍𝙄 𝘽𝙀𝙃𝙀𝙉 𝙆𝙊 𝙈𝙀𝙉𝙀 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝘼 𝘽𝙊𝙃𝙊𝙏 𝙎𝘼𝙎𝙏𝙀 𝙎𝙀",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗨‌𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜🤖🙏🤔",
"𝐓𝐄𝐑𝐈 𝐌𝐀𝐀𝐀𝐊𝐈 𝐂𝐇𝐔𝐃𝐀𝐈 𝐊𝐎 𝐏𝐎𝐑𝐍𝐇𝐔𝐁.𝐂𝐎𝐌 𝐏𝐄 𝐔𝐏𝐋𝐎𝐀𝐃 𝐊𝐀𝐑𝐃𝐔𝐍𝐆𝐀 𝐒𝐔𝐀𝐑 𝐊𝐄 𝐂𝐇𝐎𝐃𝐄 🤣💋💦",
"𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐆𝐀𝐀𝐍𝐃 𝐌𝐄𝐈 𝐎𝐍𝐄𝐏𝐋𝐔𝐒 𝐊𝐀 𝐖𝐑𝐀𝐏 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 𝟑𝟎𝐖 𝐇𝐈𝐆𝐇 𝐏𝐎𝐖𝐄𝐑 💥😂😎",
"𝐓𝐔𝐉𝐇𝐄 𝐀𝐁 𝐓𝐀𝐊 𝐍𝐀𝐇𝐈 𝐒𝐌𝐉𝐇 𝐀𝐘𝐀 𝐊𝐈 𝐌𝐀𝐈 𝐇𝐈 𝐇𝐔 𝐓𝐔𝐉𝐇𝐄 𝐏𝐀𝐈𝐃𝐀 𝐊𝐀𝐑𝐍𝐄 𝐖𝐀𝐋𝐀 𝐁𝐇𝐎𝐒𝐃𝐈𝐊𝐄𝐄 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝐄 𝐏𝐔𝐂𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 𝐁𝐀𝐂𝐇𝐄𝐄𝐄𝐄 🤩👊👤😍",
"𝐓𝐄𝐑𝐈 𝐁𝐀𝐇𝐄𝐍 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄𝐈 𝐀𝐏𝐏𝐋𝐄 𝐊𝐀 𝟏𝟖𝐖 𝐖𝐀𝐋𝐀 𝐂𝐇𝐀𝐑𝐆𝐄𝐑 🔥🤩",
"𝗧𝗘𝗥𝗜 𝗠𝗔‌𝗔‌ 𝗞𝗢 𝗜𝗧𝗡𝗔 𝗖𝗛𝗢𝗗𝗨𝗡𝗚𝗔 𝗞𝗜 𝗦𝗔𝗣𝗡𝗘 𝗠𝗘𝗜 𝗕𝗛𝗜 𝗠𝗘𝗥𝗜 𝗖𝗛𝗨𝗗𝗔𝗜 𝗬𝗔𝗔𝗗 𝗞𝗔𝗥𝗘𝗚𝗜 𝗥Æ𝗡𝗗𝗜 🥳😍👊💥",
"𝙋𝘼𝙋𝘼 𝙆𝙄 𝙎𝙋𝙀𝙀𝘿 𝙈𝙏𝘾𝙃 𝙉𝙃𝙄 𝙃𝙊 𝙍𝙃𝙄 𝙆𝙔𝘼",
"𝙆𝙄𝙏𝙉𝙄 𝘾𝙃𝙊𝘿𝙐 𝙏𝙀𝙍𝙄 𝙈𝘼 𝘼𝘽 𝙊𝙍..",
"𝗧𝗘𝗥𝗜 𝗠𝗔𝗨𝗦𝗜 𝗞𝗘 𝗕𝗛𝗢𝗦𝗗𝗘 𝗠𝗘𝗜 𝗜𝗡𝗗𝗜𝗔𝗡 𝗥𝗔𝗜𝗟𝗪𝗔𝗬 🚂💥😂",
"𝙆𝙄𝙏𝙉𝙄 𝙂𝙇𝙄𝙔𝘼 𝙋𝘿𝙒𝙀𝙂𝘼 𝘼𝙋𝙉𝙄 𝙈𝘼 𝙆𝙊",
"𝗧𝗘𝗥𝗜 𝗜𝗧𝗘𝗠 𝗞𝗜 𝗚𝗔𝗔𝗡𝗗 𝗠𝗘 𝗟𝗨𝗡𝗗 𝗗𝗔𝗔𝗟𝗞𝗘,𝗧𝗘𝗥𝗘 𝗝𝗔𝗜𝗦𝗔 𝗘𝗞 𝗢𝗥 𝗡𝗜𝗞𝗔𝗔𝗟 𝗗𝗨𝗡𝗚𝗔 𝗠𝗔‌𝗔‌𝗗𝗔𝗥𝗖𝗛Ø𝗗🤘🏻🙌🏻☠️",
"2 𝙍𝙐𝙋𝘼𝙔 𝙆𝙄 𝙋𝙀𝙋𝙎𝙄 𝙏𝙀𝙍𝙄 𝙈𝙐𝙈𝙈𝙔 𝙎𝘼𝘽𝙎𝙀 𝙎𝙀𝙓𝙔 💋💦",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके SAMBHOG करती है ! 🛐"
"Baap bhi bnale muje rndike",
"Tera baap randibaaz ey yaad ey tujhe",
"Tu apni Maa cuda na tympass",
"Oye unfunny swipe mtt kr",
"Oh hello bihari tera baap bihari or tu v bihari aaukat me rha kr.",
"Oyy kinner tujhe gc me aane ki permission kisne di.",
"Cudke dikha",
"Cudke dikha ek baar.",
"Sun sun ma cuda.",
"Teri maca bhosda.",
"Oye choti jati ke tmr.",
"Ky? jldi likh kidde.",
"Bihari com gang ke baap ko tag crega tu",
"Mujhe cya tu bihari ey tmkc bs",
"Jaldi se randibaaz papa bol",
"Side hoja bihari tery maa cud gai ab",
"Hye pgl bhg mat ache se cud",
"bhg ny randyke tu ajj",
"Hye pgl ke bche bhag mat",
"Hye dur hatt madchod ke bache",
"koi bat ny tery maa randy ey esliye maf cr rha hu tujhe",
"koi baat ny maa chudwa apni tu mafi de dunga",
"Ache se maa chudwa apni tu mafi mil jayegi tujhe",
"apni ma mat chuda muje swipe crke",
"Ache se apni ma cudwa tu swipe crke",
"Fr bolna na ki cudwa le apni ma swipe crke",
"Cya hua ma cud gyi tery",
"pr kese cud gyi tery ma",
"mujhe pta tha ma cud gai tery",
"mey ny manta ma cud gyi tery",
"teri ma rndy",
"lode se utr mc",
"lun mt chus mera",
"nikal madarchd",
"chup oye gashti k bache",
"makichut teri",
"chup rndyke",
"ma rndy teri",
"teri ma k hath todh k tere baap k muh me fasadunga randyke",
"leave le tu rndyke pasand nai aya meko",
"leave le tu randyke ider se",
"Leave le jldi se wrna ma chud gai tery",
"Leave ny lega maa randy tery",
"Smjh bat maa randy ey tery leave le",
"fast leave le kamjor randyke",
"tuto chup rndyk",
"oy hijde khana kha ke aa kamzor",
"teri mako ily rey🌚😂",
"chup chap chud tmkc",
"chupchap maa chudwa apni tu",
"shi se maa chudwa apni tu chupchap",
"fr se maa chudwa tu apni chupchap",
"shi se likh wrna ma chud gai tery",
"ma cyu chud gai tery chupchap",
"proof cr maa chud gyi tery",
"proof ey tery maa randy ey",
"proof ho chuka maa randy tery",
"Chup chillar",
"chup chup maa k bosda tery",
"oy hijde khana kha ke aa kamzor",
"chup madarchod ?",
"Ab tk cud gyi hogi tery maa ?",
"ny ny me kuch ny janta bs teri ma rndy ey",
"Sbse phele apni maa ko bol chudna kaam kre",
"Yaha bhi chuda tu rndyce pille",
"terimakabosda",
"teri to bhen cudegi",
"chup rndyke tommy",
"nikal madarchd cudke yha se",
"coz teri ma andhi randi he",
"nyto baap bol mujhe",
"nyny teri maa hogi rndii jo chudwati jogi",
"try ammi ce bhosde me emoji dal mc",
"cya ? chmr chud gya cya ?",
"tm chudri hogi frrto",
"cya ? kb ? pgl ey cya rndkek",
"cya sch mey pgl ey cya tu randyke cudwa li tune apni ma",
"itna sch ny bol ma chud gai tery",
"sch mey pgl ey tu apni ma cudwa lia mere sth",
"mtlb tmr",
"nyto",
"pura likh mc",
"tmr frrto",
"oh ok cudle fir",
"teri maa ka damad",
"cya ? ache se likhe pehle rndikebache",
"nyto teri maa chodne me vyast hu",
"nyto pgl ey cya kuch bi",
"oyee cya ? chud gya ?",
"chud mt hss",
"yur rndii mom",
"are sbki maa rndii or teri bi",
"are idar cudle ek baar",
"tri maa ci trh",
"ek line me tmr",
"Q",
"ocy ab chudle",
"pehele teri maa chodu",
"nyto",
"q ?",
"hyyy chud ke dika ek baar",
"oyee sun dost tmr",
"bhag ja raand maaf crr dunga",
"oyee pgl rndii idar aa",
"cya tmr frrto",
"oyee idar aake chud le chmr",
"nyto aese hi cud",
"oyee hyy aise hi cud lena",
"or chud le",
"chud ke dika or",
"hyy chudo na",
"chudo mt bhag jao",
"byyee hyy cya ?",
"Qchud q rhe ho ?",
"pgl ey cya mc",
"chud mt",
"cya pgl rndii idar aa",
"teri ammi ce bhosde me chappal",
"oyee idar aa mc",
"kmzror ey cya rndiek",
"cya likh rha ?",
"chud tha cya ?",
"oyee slide leke baat crmc",
"idar a teri maa chodu",
"oyee cp mt crr chudle",
"oyee hyy chud ke dika",
"idar aa try ma schofu khachar khachar",
"idar aa ja mc",
"hyy idar aake chudle",
"oyee kmzor mc idar aa",
"ye cya tmr",
"oyee ny cp ny crr",
"oyee pgl mt crr",
"cudle aram se mc",
"pgl ey cya rndiek",
"cp crce chudega !",
"baap ? mc mera coi ma baap ny ey mai upar se rocket pe beth ce bss teri ma chodne aya hu",
"Chota likh rndi k bache",
"Chota likha wrna try ma rndy",
"Try ma baka codega",
"Tmkc main burf",
"Bhikari ki jhat ma cuda le",
"Chodke tery ma marjayegi",
"Tmkc main Mount Everest",
"Muh mey lega lund mera",
"Hijde ki jhat chup wrna try ma rndi",
"Menu ny pta tery ma randy",
"Menu ki pta ma randy tery",
"Menu pta maa cud gai tery",
"Menu sb pta ma randy ey tery",
"Menu pr tery ma randy",
"Randy maa tery menu pta",
"Tenu or menu pta ey maa randy tery",
"Bs bs maa cudwa apni",
"Bs bs ma randy tery thnkss",
"Bs bs chudwa lia tu apni maa",
"Bs bs kamjor maa randy tery",
"Smjh gya apni ma cudwa le ab",
"smjh gya tery maa randy ey",
"smjh gya tu sabit kr maa randy tery",
"Cya hua ma cudwa tu apni",
"Easy maa cudwa le apni tu",
"Easy w8 ma chudwa le apni ab",
"Sans ari ha ky teri maa chudgi ajj",
"Teri maa ko bina sanss lete hue chodunga",
"chup randike kamjor",
"apni ma normie cudwa le tu",
"fr cya normie ma cud gai tery",
"bas thek tery ma randy",
"bas thek tery maa cud gyi",
"kamjor thi tery ma esliye cud gai",
"Mai sb janta ma cud gai tery",
"chl chl ht tery maa cud gyi",
"fr kaise cud gyi maa tery",
"maa tery randy ey",
"bas tery maa randy ey",
"fr randy ma tery ey",
"Kamjor ma ka bcha tu randyke",
"bhot gndi cud gai maa tery",
"pr kaise maa cud gai tery itna gnda",
"mujhe cya bta rha maa randy tery",
"mujhe cya pta ma cud gyi tery",
"fir mujhe ny pta maa cud gai tery",
"pta ny kon cod dia tery maa ko",
"ruk aaya tery ma codke",
"wait cr tery maa cod rha hu",
"wait cr rabdyke maa cud rhi ey tery",
"wait kr smjh rha tery ma codke",
"wait le thoda chodne de tery mako",
"ruk ja aand rkh dunga tery make liye",
"tery maa famous randy ey",
"maan lia mene maa randy sali tery",
"maan lia maa cud gai tery",
"shant beth randyke maa chudwa tu apni",
"shant bethke chudwa le apni mako tu",
"fr se shant Beth tu cud ab randyke yha",
"mere smjh ny aya maa randy tery",
"Le केला Kha tu madarchod",
"Hye tery ma cud gyi cya",
"hye tery maa mar gai cya",
"Hye sch bta com cod dia tery mako",
"Chl chod dia teri maa ko smjhle",
"Baki koi dikkat ny tery maa randy ey",
"baki sb jante ey ki maa chuddkad ey tery",
"mujhe cya pta tha tery maa cudne wli ey",
"pr mei kaise jnta tery ma ko koi chod dia",
"pr mera vi manna shi tha maa chud gai tery",
"pr wo glt ny tery maa randy ey",
"pr wo shi ey tery maa chuddkad ey",
"pr kaise kia maa chud gai tery omfoo",
"bur cheer dunga tri ma ka",
"teri ma ke dil me loda marke uski dhadkan rok dunga",
"lulle kha tri makabhosda",
"tri bhn ki bhosdi beta",
"tri ma rndi baat khtm",
"Sun ek maze ki baat batao kya teri maa randy ey"
"codu codu mako tery",
"aj cud gai tery maa oye",
"sun sun randy make bache tu",
"kilas ny randyke",
"mujhe cya pta tery bhen cud gai",
"pr pr cya hote ey tmkc",
"tmcl sunle",
"moot du tery maki chut mey",
"bhgny cudke dikha fr",
"fr se cudle tu",
"ye vi shi ey tery mkc bs",
"aj kuch ny ma cudwa tu apni",
"try kr mera lund chuske",
"tormakibur sun",
"tor maki fuddi oye",
"Haye Haye tery ma cud gai",
"oye lundke pasine..",
"kutte ke tatte sun",
"kutta jaisa cud rha tu",
"Muh mei le mera..",
"jhaat ke pissu sun tmkc",
"Hahahha ma cud gai tery",
"weak tatte uth",
"weak ey tu cud rha",
"weak ache se cud tu",
"weak tery ma cud rhi dekh",
"week tery ma cud gai ab",
"mujhe ny rok tu weak ey",
"chup hizde",
"okat ny meri ma cudwa tu apni",
"lun lega tery maki gand mei ?",
"tery maki bachi codu..",
"tery bhen ki chut aj fad du",
"speed lekr aa cudke dikha",
"speed ny tere andr weak prosn",
"ugly randyke chup",
"makafuddatery",
"tera baap ko tag kr..?",
"ache se tag kr randibaaz bhagwn ko..",
"cudke pgl ny ho tu",
"cudke pgl ho rha tu kid",
"ma to cud gai tery hawabzi cr..",
"bs ma codni ey tery",
"town mei cud tery mako lekr",
"tery ma sexy ko bej - randibaaz bhgwn pe",
"speed pkd cp ny kr",
"Try ma rendy",
"Bhkk cud",
"tey maa rndi",
"tery behen randi",
"Cud ja",
"tery didi rndi",
"Slow",
"teri Maiya ciodu",
"Bhag?",
"Bhak cud",
"Tma codu",
"Slow",
"Slow firse",
"Cudgrib",
"Try ma dou",
"tbkc codu",
"Net on off wali rndy",
"Oye try ma codu",
"Idhar aake cud chup chaap",
"tbkc mrdu",
"oi maake lodee",
"randyke beej",
"tmkc chodu",
"suar ke beej",
"net off on kr randyke ladke",
"Try ma cudi kese",
"Chup slow madharcod",
"tbkc codu kr msg delete",
"oi suar ke ladke",
"tmkc fufi",
"tery didi chudi",
"tmkc dikha",
"Cud ab",
"randyke cud",
"Bhak cud",
"cudle tbkc mru",
"tmkl cudle grib",
"tery behen vesiyaa rndi",
"Itna gnda chuda tu firse net on off",
"grib ke bete",
"Bhag ja lode tmkc maru dunga",
"tbkc mrdungaa",
"bhag tmkc",
"bhag tbkc",
"tbkc mey cp",
"cp tbkc mehh",
"cp tmkl meh",
"cp bol randyke",
"Abe cp bol randyke",
"double send ko cp tmkc codu",
"tbkc me cp cod dunga Aaj mehh",
"ht tbkc dalal ke bete.",
"Rndy jldi jldi cudq tryma",
"Para likhega..",
"Tra rndhbhak",
"Lagdi ke ladce cp bol",
"cp bol lagdi ke bete..",
"cudke cp bol",
"bhikari lund chus mera.",
"Low level cp cr",
"cp bol low level weak",
"mere lund pe ey tu hijde",
"free cudwa tery mako",
"Free mey cud tu randyke"
"speed ny weak tatte terme",
"kitni br cudwayega terymako",
"lund le randibaaz bapka",
"lun cus jaldi se randibaaz bapka",
"koi ny dekh rha cudle tu",
"cudle betichod ache se",
"maki chut tery bs yehi janta mey",
"cp bolega to tmkc",
"wrna tery ma cud jayegi",
"slow ey tu kid",
"jldi likh..tmkc",
"jldi likh..randce tu",
"tym se phle cudke dikha",
"tym hoga tery maa cudwa",
"ma cud gai tery tym se phle",
"uth randce ke ldke",
"macabosdatery",
"con kb cod dia mako tery",
"koi hoga tml",
"machar cudle tu",
"menu tery mako codna se",
"tery mako bol mujhe cod de",
"bs mey tery ma se cudna chta hu",
"Eww maka lode uth",
"Meow cr tery mako codu",
"lund rkh dia tery make fude pe",
"mera lund ke bal uth",
"kidee Zinda ho",
"mar ny kidde type kr",
"chup bkl",
"bc tery maki chut",
"mc randyke likh fast",
"fast likh randyke",
"fast likh kamzor"
"tery maki chut claim crwa",
"awz niche randce ke bche",
"sawal ny puch tery makabosda",
"fyter bnega lagde madrchod",
"oye kaale ro ke dikha",
"oye kaale roo ny",
"short ny cud tu bina ruke",
"short ny cud tu apni mako lekr",
"tery make sth tery bhen vi cudwa le",
"tery make sth tery didi vi cud gai",
"Chat fyter bnega randce codu tery mako",
"bol randibaaz daddy ey",
"bullyx randyke uth",
"mar marke cud rha tu",
"or tery ma marke cud gai"
"Jaldi likh rndyke bej",
"Or bda likh tmc",
"Or bda 2 line wla likh tmkc",
"Or bda oye likh tml",
"Teri maa ka bur",
"Oye keede",
"Randi ke ladke",
"Jaldi likh teri behen chodu",
"Mkl uth randi ke bacche",
"Teri nani meri maal",
"Tej likh randce",
"Oye maake lode mrenga",
"Teri maa chody",
"Teri Maiya ki gand",
"Tery dadi ka fudda",
"Mkl uth behencod",
"Teri maa ki bur de",
"Tery maa ka fudda me lauda",
"Teri maa chudva",
"Randi ke bete mar gaya",
"Teri maa ki chut mru",
"Jalid kr spam",
"Mc spam rokenga",
"Teri maaki chut spam kr",
"spam kr.maake lode",
"Randyke chode spam kr wrna cud tu",
"Spam kr kid",
"Noob teri maa chodu",
"Rndyke bete mar mat tu",
"Noob jaldi likh wrna tery maa rand",
"cud gai maa tery noob",
"uth randyke noob",
"chl cudke dikha noob",
"jldi typ cr noob halke",
"cud ke pgl ny ho noob",
"cud cud ke rand bnja tu noob",
"makichut tery noob",
"ganda cyu cud rha tu ?",
"itna gnda ny cud ache se cud",
"Maan le cud gya tu sun bat ab",
"makafudda fat gya tery ruk"
"BAAP BHI BNALE MUJE RNDIKE",
"TERA BAAP RANDIBAAZ EY YAAD EY TUJHE",
"TU APNI MAA CUDA NA TYMPASS",
"OYE UNFUNNY SWIPE MTT KR",
"OH HELLO BIHARI TERA BAAP BIHARI OR TU V BIHARI AAUKAT ME RHA KR.",
"OYY KINNER TUJHE GC ME AANE KI PERMISSION KISNE DI.",
"CUDKE DIKHA",
"CUDKE DIKHA EK BAAR.",
"SUN SUN MA CUDA.",
"TERI MACA BHOSDA.",
"OYE CHOTI JATI KE TMR.",
"KY? JLDI LIKH KIDDE.",
"BIHARI COM GANG KE BAAP KO TAG CREGA TU",
"MUJHE CYA TU BIHARI EY TMKC BS",
"JALDI SE RANDIBAAZ PAPA BOL",
"SIDE HOJA BIHARI TERY MAA CUD GAI AB",
"HYE PGL BHG MAT ACHE SE CUD",
"BHG NY RANDYKE TU AJJ",
"HYE PGL KE BCHE BHAG MAT",
"HYE DUR HATT MADCHOD KE BACHE",
"KOI BAT NY TERY MAA RANDY EY ESLIYE MAF CR RHA HU TUJHE",
"KOI BAAT NY MAA CHUDWA APNI TU MAFI DE DUNGA",
"ACHE SE MAA CHUDWA APNI TU MAFI MIL JAYEGI TUJHE",
"APNI MA MAT CHUDA MUJE SWIPE CRKE",
"ACHE SE APNI MA CUDWA TU SWIPE CRKE",
"FR BOLNA NA KI CUDWA LE APNI MA SWIPE CRKE",
"CYA HUA MA CUD GYI TERY",
"PR KESE CUD GYI TERY MA",
"MUJHE PTA THA MA CUD GAI TERY",
"MEY NY MANTA MA CUD GYI TERY",
"TERI MA RNDY",
"LODE SE UTR MC",
"LUN MT CHUS MERA",
"NIKAL MADARCHD",
"CHUP OYE GASHTI K BACHE",
"MAKICHUT TERI",
"CHUP RNDYKE",
"MA RNDY TERI",
"TERI MA K HATH TODH K TERE BAAP K MUH ME FASADUNGA RANDYKE",
"LEAVE LE TU RNDYKE PASAND NAI AYA MEKO",
"LEAVE LE TU RANDYKE IDER SE",
"LEAVE LE JLDI SE WRNA MA CHUD GAI TERY",
"LEAVE NY LEGA MAA RANDY TERY",
"SMJH BAT MAA RANDY EY TERY LEAVE LE",
"FAST LEAVE LE KAMJOR RANDYKE",
"TUTO CHUP RNDYK",
"OY HIJDE KHANA KHA KE AA KAMZOR",
"TERI MAKO ILY REY",
"CHUP CHAP CHUD TMKC",
"CHUPCHAP MAA CHUDWA APNI TU",
"SHI SE MAA CHUDWA APNI TU CHUPCHAP",
"FR SE MAA CHUDWA TU APNI CHUPCHAP",
"SHI SE LIKH WRNA MA CHUD GAI TERY",
"MA CYU CHUD GAI TERY CHUPCHAP",
"PROOF CR MAA CHUD GYI TERY",
"PROOF EY TERY MAA RANDY EY",
"PROOF HO CHUKA MAA RANDY TERY",
"CHUP CHILLAR",
"CHUP CHUP MA K BOSDA TERY",
"OY HIJDE KHANA KHA KE AA KAMZOR",
"CHUP MADARCHOD ?",
"AB TK CUD GYI HOGI TERY MAA ?",
"NY NY ME KUCH NY JANTA BS TERI MA RNDY EY",
"SBSE PHELE APNI MAA KO BOL CHUDNA KAAM KRE",
"YAHA BHI CHUDA TU RNDYCE PILLE",
"TERIMAKABOSDA",
"TERI TO BHEN CUDEGI",
"CHUP RNDYKE TOMMY",
"NIKAL MADARCHD CUDKE YHA SE",
"COZ TERI MA ANDHI RANDI HE",
"NYTO BAAP BOL MUJHE",
"NYNY TERI MAA HOGI RNDII JO CHUDWATI JOGI",
"TRY AMMI CE BHOSDE ME EMOJI DAL MC",
"CYA ? CHMR CHUD GYA CYA ?",
"TM CHUDRI HOGI FRRTO",
"CYA ? KB ? PGL EY CYA RNDKEK",
"CYA SCH MEY PGL EY CYA TU RANDYKE CUDWA LI TUNE APNI MA",
"ITNA SCH NY BOL MA CHUD GAI TERY",
"SCH MEY PGL EY TU APNI MA CUDWA LIA MERE STH",
"MTLB TMR",
"NYTO",
"PURA LIKH MC",
"TMR FRRTO",
"OH OK CUDLE FIR",
"TERI MAA KA DAMAD",
"CYA ? ACHE SE LIKHE PEHLE RNDIKEBACHE",
"NYTO TERI MAA CHODNE ME VYAST HU",
"NYTO PGL EY CYA KUCH BI",
"OYEE CYA ? CHUD GYA ?",
"CHUD MT HSS",
"YUR RNDII MOM",
"ARE SBKI MAA RNDII OR TERI BI",
"ARE IDAR CUDLE EK BAAR",
"TRI MAA CI TRH",
"EK LINE ME TMR",
"Q",
"OCY AB CHUDLE",
"PEHELE TERI MAA CHODU",
"NYTO",
"Q ?",
"HYYY CHUD KE DIKA EK BAAR",
"OYEE SUN DOST TMR",
"BHAG JA RAAND MAAF CRR DUNGA",
"OYEE PGL RNDII IDAR AA",
"CYA TMR FRRTO",
"OYEE IDAR Aake CHUD LE CHMR",
"NYTO AESE HI CUD",
"OYEE HYY AISE HI CUD LENA",
"OR CHUD LE",
"CHUD KE DIKA OR",
"HYY CHUDO NA",
"CHUDO MT BHAG JAO",
"BYYEE HYY CYA ?",
"QCHUD Q RHE HO ?",
"PGL EY CYA MC",
"CHUD MT",
"CYA PGL RNDII IDAR AA",
"TERI AMMI CE BHOSDE ME CHAPPAL",
"OYEE IDAR AA MC",
"KMZROR EY CYA RNDIEK",
"CYA LIKH RHA ?",
"CHUD THA CYA ?",
"OYEE SLIDE LEKE BAAT CRMC",
"IDAR A TERI MAA CHODU",
"OYEE CP MT CRR CHUDLE",
"OYEE HYY CHUD KE DIKA",
"IDAR AA TRY MA SCHOFU KHACHAR KHACHAR",
"IDAR AA JA MC",
"HYY IDAR Aake CHUDLE",
"OYEE KMZOR MC IDAR AA",
"YE CYA TMR",
"OYEE NY CP NY CRR",
"OYEE PGL MT CRR",
"CUDLE ARAM SE MC",
"PGL EY CYA RNDIEK",
"CP CRCE CHUDEGA !",
"BAAP ? MC MERA COI MA BAAP NY EY MAI UPAR SE ROCKET PE BETH CE BSS TERI MA CHODNE AYA HU",
"CHOTA LIKH RNDI K BACHE",
"CHOTA LIKHA WRNA TRY MA RNDY",
"TRY MA BAKA CODEGA",
"TMKC MAIN BURF",
"BHIKARI KI JHAT MA CUDA LE",
"CHODKE TERY MA MARJAYEGI",
"TMKC MAIN MOUNT EVEREST",
"MUH MEY LEGA LUND MERA",
"HIJDE KI JHAT CHUP WRNA TRY MA RNDI",
"MENU NY PTA TERY MA RANDY",
"MENU KI PTA MA RANDY TERY",
"MENU PTA MAA CUD GAI TERY",
"MENU SB PTA MA RANDY EY TERY",
"MENU PR TERY MA RANDY",
"RANDY MAA TERY MENU PTA",
"TENU OR MENU PTA EY MAA RANDY TERY",
"BS BS MAA CUDWA APNI",
"BS BS MA RANDY TERY THNKSS",
"BS BS CHUDWA LIA TU APNI MAA",
"BS BS KAMJOR MAA RANDY TERY",
"SMJH GYA APNI MA CUDWA LE AB",
"SMJH GYA TERY MAA RANDY EY",
"SMJH GYA TU SABIT KR MAA RANDY TERY",
"CYA HUA MA CUDWA TU APNI",
"EASY MAA CUDWA LE APNI TU",
"EASY W8 MA CHUDWA LE APNI AB",
"SANS ARI HA KY TERI MAA CHUDGI AJJ",
"TERI MAA KO BINA SANSS LETE HUE CHODUNGA",
"CHUP RANDIKE KAMJOR",
"APNI MA NORMIE CUDWA LE TU",
"FR CYA NORMIE MA CUD GAI TERY",
"BAS THEK TERY MA RANDY",
"BAS THEK TERY MAA CUD GYI",
"KAMJOR THI TERY MA ESLIYE CUD GAI",
"MAI SB JANTA MA CUD GAI TERY",
"CHL CHL HT TERY MAA CUD GYI",
"FR KAISE CUD GYI MAA TERY",
"MAA TERY RANDY EY",
"BAS TERY MAA RANDY EY",
"FR RANDY MA TERY EY",
"KAMJOR MA KA BCHA TU RANDYKE",
"BHOT GNDI CUD GAI MAA TERY",
"PR KAISE MAA CUD GAI TERY ITNA GNDA",
"MUJHE CYA BTA RHA MAA RANDY TERY",
"MUJHE CYA PTA MA CUD GYI TERY",
"FIR MUJHE NY PTA MAA CUD GAI TERY",
"PTA NY KON COD DIA TERY MAA KO",
"RUK AAYA TERY MA CODKE",
"WAIT CR TERY MAA COD RHA HU",
"WAIT CR RABDYKE MAA CUD RHI EY TERY",
"WAIT KR SMJH RHA TERY MA CODKE",
"WAIT LE THODA CHODNE DE TERY MAKO",
"RUK JA AAND RKH DUNGA TERY MAKE LIYE",
"TERY MAA FAMOUS RANDY EY",
"MAAN LIA MENE MAA RANDY SALI TERY",
"MAAN LIA MAA CUD GAI TERY",
"SHANT BETH RANDYKE MAA CHUDWA TU APNI",
"SHANT BETHKE CHUDWA LE APNI MAKO TU",
"FR SE SHANT BETH TU CUD AB RANDYKE YHA",
"MERE SMJH NY AYA MAA RANDY TERY",
"LE KELA KHA TU MADARCHOD",
"HYE TERY MA CUD GYI CYA",
"HYE TERY MAA MAR GAI CYA",
"HYE SCH BTA COM COD DIA TERY MAKO",
"CHL CHOD DIA TERI MAA KO SMJHLE",
"BAKI KOI DIKKAT NY TERY MAA RANDY EY",
"BAKI SB JANTE EY KI MAA CHUDDKAD EY TERY",
"MUJHE CYA PTA THA TERY MAA CUDNE WLI EY",
"PR MEI KAISE JNTA TERY MA KO KOI CHOD DIA",
"PR MERA VI MANNA SHI THA MAA CHUD GAI TERY",
"PR WO GLT NY TERY MAA RANDY EY",
"PR WO SHI EY TERY MAA CHUDDKAD EY",
"PR KAISE KIA MAA CHUD GAI TERY OMFOO",
"BUR CHEER DUNGA TRI MA KA",
"TERI MA KE DIL ME LODA MARKE USKI DHADKAN ROK DUNGA",
"LULLE KHA TRI MAKABHOSDA",
"TRI BHN KI BHOSDI BETA",
"TRI MA RNDI BAAT KHTM",
"SUN EK MAZE KI BAAT BATAO KYA TERI MAA RANDY EY",
"CODU CODU MAKO TERY",
"AJ CUD GAI TERY MAA OYE",
"SUN SUN RANDY MAKE BACHE TU",
"KILAS NY RANDYKE",
"MUJHE CYA PTA TERY BHEN CUD GAI",
"PR PR CYA HOTE EY TMKC",
"TMCL SUNLE",
"MOOT DU TERY MAKI CHUT MEY",
"BHGNY CUDKE DIKHA FR",
"FR SE CUDLE TU",
"YE VI SHI EY TERY MKC BS",
"AJ KUCH NY MA CUDWA TU APNI",
"TRY KR MERA LUND CHUSKE",
"TORMAKIBUR SUN",
"TOR MAKI FUDDI OYE",
"HAYE HAYE TERY MA CUD GAI",
"OYE LUNDKE PASINE..",
"KUTTE KE TATTE SUN",
"KUTTA JAISA CUD RHA TU",
"MUH MEI LE MERA..",
"JHAAT KE PISSU SUN TMKC",
"HAHAHHA MA CUD GAI TERY",
"WEAK TATTE UTH",
"WEAK EY TU CUD RHA",
"WEAK ACHE SE CUD TU",
"WEAK TERY MA CUD RHI DEKH",
"WEEK TERY MA CUD GAI AB",
"MUJHE NY ROK TU WEAK EY",
"CHUP HIZDE",
"OKAT NY MERI MA CUDWA TU APNI",
"LUN LEGA TERY MAKI GAND MEI ?",
"TERY MAKI BACHI CODU..",
"TERY BHEN KI CHUT AJ FAD DU",
"SPEED LEKR AA CUDKE DIKHA",
"SPEED NY TERE ANDR WEAK PROSN",
"UGLY RANDYKE CHUP",
"MAKAFUDDATERY",
"TERA BAAP KO TAG KR..?",
"ACHE SE TAG KR RANDIBAAZ BHAGWN KO..",
"CUDKE PGL NY HO TU",
"CUDKE PGL HO RHA TU KID",
"MA TO CUD GAI TERY HAWABZI CR..",
"BS MA CODNI EY TERY",
"TOWN MEI CUD TERY MAKO LEKR",
"TERY MA SEXY KO BEJ - RANDIBAAZ BHGWN PE",
"SPEED PKD CP NY KR",
"TRY MA RENDY",
"BHKK CUD",
"TEY MAA RNDI",
"TERY BEHEN RANDI",
"CUD JA TMC",
"TERY DIDI RNDI",
"SLOW",
"TERI MAIYA CIODU",
"BHAG?TMC ",
"BHAK CUD TML",
"TMA CODU",
"SLOW TMKC ",
"SLOW FIRSE TMKC ",
"CUDGRIB TML",
"TRY MA DOU",
"TBKC CODU",
"NET ON OFF WALI RNDY",
"OYE TRY MA CODU",
"IDHAR AAKE CUD CHUP CHAAP",
"TBKC MRDU",
"OI MAAKE LODEE",
"RANDYKE BEEJ",
"TMKC CHODU",
"SUAR KE BEEJ",
"NET OFF ON KR RANDYKE LADKE",
"TRY MA CUDI KESE",
"CHUP SLOW MADHARCOD",
"TBKC CODU KR MSG DELETE",
"OI SUAR KE LADKE",
"TMKC FUFI",
"TERY DIDI CHUDI",
"TMKC DIKHA",
"CUD AB",
"RANDYKE CUD",
"BHAK CUD",
"CUDLE TBKC MRU",
"TMKL CUDLE GRIB",
"TERY BEHEN VESITYA RNDI",
"ITNA GNDA CHUDA TU FIRSE NET ON OFF",
"GRIB KE BETE",
"BHAG JA LODE TMKC MARU DUNGA",
"TBKC MRDUNGAA",
"BHAG TMKC",
"BHAG TBKC",
"TBKC MEY CP",
"CP TBKC MEHH",
"CP TMKL MEH",
"CP BOL RANDYKE",
"ABE CP BOL RANDYKE",
"DOUBLE SEND KO CP TMKC CODU",
"TBKC ME CP COD DUNGA AAJ MEHH",
"HT TBKC DALAL KE BETE.",
"RNDY JLDI JLDI CUDQ TRYMA",
"PARA LIKHEGA..",
"TRA RNDHBHAK",
"LAGDI KE LADCE CP BOL",
"CP BOL LAGDI KE BETE..",
"CUDKE CP BOL",
"BHIKARI LUND CHUS MERA.",
"LOW LEVEL CP CR",
"CP BOL LOW LEVEL WEAK",
"MERE LUND PE EY TU HIJDE",
"FREE CUDWA TERY MAKO",
"FREE MEY CUD TU RANDYKE",
"SPEED NY WEAK TATTE TERME",
"KITNI BR CUDWAYEGA TERYMAKO",
"LUND LE RANDIBAAZ BAPKA",
"LUN CUS JALDI SE RANDIBAAZ BAPKA",
"KOI NY DEKH RHA CUDLE TU",
"CUDLE BETICHOD ACHE SE",
"MAKI CHUT TERY BS YEHI JANTA MEY",
"CP BOLEGA TO TMKC",
"WRNA TERY MA CUD JAYEGI",
"SLOW EY TU KID",
"JLDI LIKH..TMKC",
"JLDI LIKH..RANDCE TU",
"TYM SE PHLE CUDKE DIKHA",
"TYM HOGA TERY MAA CUDWA",
"MA CUD GAI TERY TYM SE PHLE",
"UTH RANDCE KE LDKE",
"MACABOSDATERY",
"CON KB COD DIA MAKO TERY",
"KOI HOGA TML",
"MACHAR CUDLE TU",
"MENU TERY MAKO CODNA SE",
"TERY MAKO BOL MUJHE COD DE",
"BS MEY TERY MA SE CUDNA CHTA HU",
"EWW MAKA LODE UTH",
"MEOW CR TERY MAKO CODU",
"LUND RKH DIA TERY MAKE FUDE PE",
"MERA LUND KE BAL UTH",
"KIDEE ZINDA HO",
"MAR NY KIDDE TYPE KR",
"CHUP BKL",
"BC TERY MAKI CHUT",
"MC RANDYKE LIKH FAST",
"FAST LIKH RANDYKE",
"FAST LIKH KAMZOR",
"TERY MAKI CHUT CLAIM CRWA",
"AWZ NICHE RANDCE KE BCHE",
"SAWAL NY PUCH TERY MAKABOSDA",
"FYTER BNEGA LAGDE MADRCHOD",
"OYE KAALE RO KE DIKHA",
"OYE KAALE ROO NY",
"SHORT NY CUD TU BINA RUKE",
"SHORT NY CUD TU APNI MAKO LEKR",
"TERY MAKE STH TERY BHEN VI CUDWA LE",
"TERY MAKE STH TERY DIDI VI CUD GAI",
"CHAT FYTER BNEGA RANDCE CODU TERY MAKO",
"BOL RANDIBAAZ DADDY EY",
"BULLYX RANDYKE UTH",
"MAR MARKE CUD RHA TU",
"OR TERY MA MARKE CUD GAI",
"JALDI LIKH RNDYKE BEJ",
"OR BDA LIKH TMC",
"OR BDA 2 LINE WLA LIKH TMKC",
"OR BDA OYE LIKH TML",
"TERI MAA KA BUR",
"OYE KEEDE",
"RANDI KE LADKE",
"JALDI LIKH TERI BEHEN CHODU",
"MKL UTH RANDI KE BACCHE",
"TERI NANI MERI MAAL",
"TEJ LIKH RANDCE",
"OYE MAAKE LODE MRENGA",
"TERI MAA CHODY",
"TERI MAIYA KI GAND",
"TERY DADI KA FUDDA",
"MKL UTH BEHENCOD",
"TERI MAA KI BUR DE",
"TERY MAA KA FUDDA ME LAUDA",
"TERI MAA CHUDVA",
"RANDI KE BETE MAR GAYA",
"TERI MAA KI CHUT MRU",
"JALID KR SPAM",
"MC SPAM ROKENGA",
"TERI MAAKI CHUT SPAM KR",
"SPAM KR.MAAKE LODE",
"RANDYKE CHODE SPAM KR WRNA CUD TU",
"SPAM KR KID",
"NOOB TERI MAA CHODU",
"RNDYKE BETE MAR MAT TU",
"NOOB JALDI LIKH WRNA TERY MAA RAND",
"CUD GAI MAA TERY NOOB",
"UTH RANDYKE NOOB",
"CHL CUDKE DIKHA NOOB",
"JLDI TYP CR NOOB HALKE",
"CUD KE PGL NY HO NOOB",
"CUD CUD KE RAND BNJA TU NOOB",
"MAKICHUT TERY NOOB",
"GANDA CYU CUD RHA TU ?",
"ITNA GNDA NY CUD ACHE SE CUD",
"MAAN LE CUD GYA TU SUN BAT AB",
"MAKAFUDDA FAT GYA TERY RUK",
"sʜᴀɴᴛ ʙᴇᴛʜ ᴍᴀᴅʀᴄʜᴏᴅ ᴡʀɴᴀ ᴍᴀᴋᴀʙᴏsᴅᴀ ᴛᴇᴇʏ.",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ..",
"ʟᴡᴅᴇ ᴋᴇ ʙᴀᴀᴀʟʟʟ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅᴋᴇ ᴘɢʟ ᴅᴇᴋʜ.",
"ᴍᴀᴄʜᴀʀ ᴋɪ ᴊʜᴀᴀᴛ ᴋᴇ ʙᴀᴀᴀʟʟʟʟ ᴄᴜᴅ ᴀᴄʜᴇ sᴇ ʏʜᴀᴘᴇ ᴛᴜ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴍ ᴅᴜ ᴛᴀᴘᴀ ᴛᴀᴘ?",
"ᴛᴇʀɪ ᴍᴀ ᴋᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪ ʙʜɴ ꜱʙꜱʙᴇ ʙᴅɪ ʀᴀɴᴅɪ.",
"ᴛᴇʀɪ ᴍᴀ ᴏꜱꜱᴇ ʙᴀᴅɪ ʀᴀɴᴅᴅᴅᴅᴅ",
"ᴛᴇʀᴀ ʙᴀᴀᴘ ʀᴀɴᴅɪʙᴀᴀᴢ ᴇʏ ᴅᴇᴋʜ",
"ᴋɪᴛɴɪ ᴄʜᴏᴅᴜ ᴛᴇʀɪ ᴍᴀ ᴀʙ ᴏʀ..",
"ᴛᴇʀɪ ᴍᴀ ᴄʜᴏᴅ ᴅɪ ʜᴍ ɴᴇ",
"ᴛᴇʀɪ ᴍᴀ ᴋᴇ ꜱᴛʜ ʀᴇᴇʟꜱ ʙɴᴇɢᴀ ʀᴏᴀᴅ ᴘᴇᴇ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴇᴋ ᴅᴀᴍ ᴛᴏᴘ ꜱᴇxʏ",
"ᴍᴀʟᴜᴍ ɴᴀ ᴘʜʀ ᴋᴇꜱᴇ ʟᴇᴛᴀ ʜᴜ ᴍ ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴄʜᴜᴛ ᴛᴀᴘᴀ ᴛᴀᴘᴘᴘᴘᴘ",
"ʟᴜɴᴅ ᴋᴇ ᴄʜᴏᴅᴇ ᴛᴜ ᴋᴇʀᴇɢᴀ ᴛʏᴘɪɴɢ ᴋʀᴇɢᴀ ᴛᴍᴋᴄ",
"ꜱᴘᴇᴇᴅ ᴘᴋᴅ ʟᴡᴅᴇᴇᴇᴇ ᴡʀɴᴀ ᴍᴇʀᴀ ʟᴜɴᴅ ᴘᴋᴅ",
"ʙᴀᴀᴘ ᴋɪ ꜱᴘᴇᴇᴅ ᴍᴛᴄʜ ᴋʀʀʀ",
"ʟᴡᴅᴀ ʟᴇ ᴍᴇʀᴀ ᴊᴀʟᴅɪ sᴇ ᴛᴜ",
"ᴘᴀᴘᴀ ᴋɪ ꜱᴘᴇᴇᴅ ᴍᴛᴄʜ ɴʜɪ ʜᴏ ʀʜɪ ᴋʏᴀ ᴛᴇʀᴇsᴇ",
"ᴀʟᴇ ᴀʟᴇ ᴍᴇʟᴀ ʙᴄʜᴀᴀᴀᴀ ᴛᴇʀʏ ᴍᴀᴋᴀ ʙᴏsᴅᴀ sᴜɴ",
"ᴄʜᴜᴅ ɢʏᴀ ʀᴀɴᴅɪʙᴀᴀᴢ ᴘᴀᴘᴀ ꜱᴇᴇᴇ ᴛᴜ",
"ᴍᴇɴᴜ ᴋɪ ᴘᴛᴀ ᴛᴇʀʏ ᴍᴀ ᴄᴜᴅ ɢᴀɪ",
"ᴋᴏɪ ʙᴀᴀᴛ ɴʏ ᴍᴀᴀ ʀᴀɴᴅʏ ᴛᴇʀʏ",
"ʜᴀʜᴀʜᴀᴀᴀᴀᴀ ᴍᴀᴋᴀʙᴏsᴅᴀ ᴛᴇʀʏ",
"xʜᴜᴅ ɢᴀɪ ᴍᴀᴀ ᴛᴇʀʏ ᴋɪᴅꜱꜱꜱꜱ",
"ᴛᴇʀɪ ᴍᴀ ᴄʜᴜᴅ ɢʏɪ ᴀʙ ꜰʀᴀʀ ᴍᴛ ʜᴏɴᴀ",
"ʏᴇ ʟᴜɴᴅ ʟᴇ ᴍᴇʀᴀ ᴄʜʟ ᴊᴀʟᴅɪ sᴇ",
"ᴋɪᴅꜱꜱꜱ ꜰʀᴀʀ ɴᴀ ʜᴏ ᴛᴜ ʜᴀʜᴀʜʜ",
"ʙʜᴇɴ ᴋᴇ ʟᴡᴅᴇ ꜱʜʀᴍ ᴋʀ",
"ᴋɪᴛɴɪ ɢʟɪʏᴀ ᴘᴅᴡᴇɢᴀ ᴀᴘɴɪ ᴍᴀ ᴋᴏ",
"ᴄʜᴜᴘ ɴᴀʟʟɪɪ ʀᴀɴᴅʏᴋᴇ ʟᴀᴅᴋᴇ",
"ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ꜱᴀᴅᴀᴋ ᴘʀ ʟɪᴛᴀᴋᴇ ᴄʜᴏᴅ ᴅᴜɴɢᴀ 😂😆🤤",
"ᴀʙᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴀ ʙʜᴏꜱᴅᴀ ᴍᴀᴅᴇʀᴄʜᴏᴏᴅ ᴋʀ ᴘɪʟʟᴇ ᴘᴀᴘᴀ ꜱᴇ ʟᴀᴅᴇɢᴀ ᴛᴜ 😼😂🤤",
"ɢᴀʟɪ ɢᴀʟɪ ɴᴇ ꜱʜᴏʀ ʜᴇ ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ᴄʜᴏʀ ʜᴇ 💋💋💦",
"ᴀʙᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ᴘɪʟʟᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴄʜᴏᴅᴇ 😂👻🔥",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴀɪꜱᴇ ᴄʜᴏᴅᴀ ᴀɪꜱᴇ ᴄʜᴏᴅᴀ ᴛᴇʀɪ ᴍᴀᴀᴀ ʙᴇᴅ ᴘᴇʜɪ ᴍᴜᴛʜ ᴅɪᴀ 💦💦💦💦",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴇ ʙʜᴏꜱᴅᴇ ᴍᴇ ᴀᴀᴀɢ ʟᴀɢᴀᴅɪᴀ ᴍᴇʀᴀ ᴍᴏᴛᴀ ʟᴜɴᴅ ᴅᴀʟᴋᴇ 🔥🔥💦😆😆",
"ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅᴜ ᴄʜᴀʟ ɴɪᴋᴀʟ",
"ᴋɪᴛɴᴀ ᴄʜᴏᴅᴜ ᴛᴇʀɪ ʀᴀɴᴅɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ᴀʙʙ ᴀᴘɴɪ ʙᴇʜᴇɴ ᴋᴏ ʙʜᴇᴊ 😆👻🤤",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏᴛᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴘᴜʀᴀ ꜰᴀᴀᴅ ᴅɪᴀ ᴄʜᴜᴛʜ ᴀʙʙ ᴛᴇʀɪ ɢꜰ ᴋᴏ ʙʜᴇᴊ 😆💦🤤",
"ᴛᴇʀɪ ɢꜰ ᴋᴏ ᴇᴛɴᴀ ᴄʜᴏᴅᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴏᴅᴇ ᴛᴇʀɪ ɢꜰ ᴛᴏ ᴍᴇʀɪ ʀᴀɴᴅɪ ʙᴀɴɢᴀʏɪ ᴀʙʙ ᴄʜᴀʟ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅᴛᴀ ꜰɪʀꜱᴇ ♥️💦😆😆😆😆",
"ʜᴀʀɪ ʜᴀʀɪ ɢʜᴀᴀꜱ ᴍᴇ ᴊʜᴏᴘᴅᴀ ᴛᴇʀɪ ᴍᴀᴀᴋᴀ ʙʜᴏꜱᴅᴀ 🤣🤣💋💦",
"ᴄʜᴀʟ ᴛᴇʀᴇ ʙᴀᴀᴘ ᴋᴏ ʙʜᴇᴊ ᴛᴇʀᴀ ʙᴀꜱᴋᴀ ɴʜɪ ʜᴇ ᴘᴀᴘᴀ ꜱᴇ ʟᴀᴅᴇɢᴀ ᴛᴜ",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ʙᴏᴍʙ ᴅᴀʟᴋᴇ ᴜᴅᴀ ᴅᴜɴɢᴀ ᴍᴀᴀᴋᴇ ʟᴀᴡᴅᴇ",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴛʀᴀɪɴ ᴍᴇ ʟᴇᴊᴀᴋᴇ ᴛᴏᴘ ʙᴇᴅ ᴘᴇ ʟɪᴛᴀᴋᴇ ᴄʜᴏᴅ ᴅᴜɴɢᴀ ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ 🤣🤣💋💋",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴇ ɴᴜᴅᴇꜱ ɢᴏᴏɢʟᴇ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴀᴇᴡᴅᴇ 👻🔥",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴇ ɴᴜᴅᴇꜱ ɢᴏᴏɢʟᴇ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ʙᴇʜᴇɴ ᴋᴇ ʟᴀᴇᴡᴅᴇ 👻🔥",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴠɪᴅᴇᴏ ʙᴀɴᴀᴋᴇ xɴxx ᴘᴇ ɴᴇᴇʟᴀᴍ ᴋᴀʀᴅᴜɴɢᴀ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 💦💋",
"ᴛᴇʀɪ ᴍᴀᴀᴀᴋɪ ᴄʜᴜᴅᴀɪ ᴋᴏ ᴘᴏ*ʀɴʜᴜʙ ᴘᴇ ᴜᴘʟᴏᴀᴅ ᴋᴀʀᴅᴜɴɢᴀ ꜱᴜᴀʀ ᴋᴇ ᴄʜᴏᴅᴇ 🤣💋💦",
"ᴀʙᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴛᴇʀᴇᴋᴏ ᴄʜᴀᴋᴋᴏ ꜱᴇ ᴘɪʟᴡᴀᴠᴜɴɢᴀ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ 🤣🤣",
"ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ꜰᴀᴀᴅᴋᴇ ʀᴀᴋᴅɪᴀ ᴍᴀᴀᴋᴇ ʟᴏᴅᴇ ᴊᴀᴀ ᴀʙʙ ꜱɪʟᴡᴀʟᴇ 👄👄",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴇʀᴀ ʟᴜɴᴅ ᴋᴀᴀʟᴀ",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ʟᴇᴛɪ ᴍᴇʀɪ ʟᴜɴᴅ ʙᴀᴅᴇ ᴍᴀꜱᴛɪ ꜱᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴏ ᴍᴇɴᴇ ᴄʜᴏᴅ ᴅᴀʟᴀ ʙᴏʜᴏᴛ ꜱᴀꜱᴛᴇ ꜱᴇ",
"ʙᴇᴛᴇ ᴛᴜ ʙᴀᴀᴘ ꜱᴇ ʟᴇɢᴀ ᴘᴀɴɢᴀ ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋᴏ ᴄʜᴏᴅ ᴅᴜɴɢᴀ ᴋᴀʀᴋᴇ ɴᴀɴɢᴀ 💦💋",
"ʜᴀʜᴀʜᴀʜ ᴍᴇʀᴇ ʙᴇᴛᴇ ᴀɢʟɪ ʙᴀᴀʀ ᴀᴘɴɪ ᴍᴀᴀᴋᴏ ʟᴇᴋᴇ ᴀᴀʏᴀ ᴍᴀᴛʜ ᴋᴀᴛ ᴏʀ ᴍᴇʀᴇ ᴍᴏᴛᴇ ʟᴜɴᴅ ꜱᴇ ᴄʜᴜᴅᴡᴀʏᴀ ᴍᴀᴛʜ ᴋᴀʀ",
"ᴄʜᴀʟ ʙᴇᴛᴀ ᴛᴜᴊʜᴇ ᴍᴀᴀꜰ ᴋɪᴀ 🤣ᴛᴜ ᴀʙʙ ᴀᴘɴɪ ᴍᴀᴋᴏ ʙʜᴇᴊ",
"ꜱʜᴀʀᴀᴍ ᴋᴀʀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴀ ʙʜᴏꜱᴅᴀ ᴋɪᴛɴᴀ ɢᴀᴀʟɪᴀ ꜱᴜɴᴡᴀʏᴇɢᴀ ᴀᴘɴɪ ᴍᴀᴀᴀ ʙᴇʜᴇɴ ᴋᴇ ᴜᴘᴇʀ",
"ᴀʙᴇ ʀᴀɴᴅɪᴋᴇ ʙᴀᴄʜʜᴇ ᴀᴜᴋᴀᴛ ɴʜɪ ʜᴇᴛᴏ ᴀᴘɴɪ ʀᴀɴᴅɪ ᴍᴀᴀᴋᴏ ʟᴇᴋᴇ ᴀᴀʏᴀ ᴍᴀᴛʜ ᴋᴀʀ ʜᴀʜᴀʜᴀʜᴀ",
"ᴋɪᴅᴢ ᴍᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅ ᴄʜᴏᴅᴋᴇ ᴛᴇʀʀ ʟɪʏᴇ ʙʜᴀɪ ᴅᴇᴅɪʏᴀ",
"ᴊᴜɴɢʟᴇ ᴍᴇ ɴᴀᴄʜᴛᴀ ʜᴇ ᴍᴏʀᴇ ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴅᴀɪ ᴅᴇᴋᴋᴇ ꜱᴀʙ ʙᴏʟᴛᴇ ᴏɴᴄᴇ ᴍᴏʀᴇ ᴏɴᴄᴇ ᴍᴏʀᴇ 🤣🤣💦💋",
"ɢᴀʟɪ ɢᴀʟɪ ᴍᴇ ʀᴇʜᴛᴀ ʜᴇ ꜱᴀɴᴅ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴏᴅ ᴅᴀʟᴀ ᴏʀ ʙᴀɴᴀ ᴅɪᴀ ʀᴀɴᴅ 🤤🤣",
"ꜱᴀʙ ʙᴏʟᴛᴇ ᴍᴜᴊʜᴋᴏ ᴘᴀᴘᴀ ᴄʏᴜᴋɪ ᴍᴇɴᴇ ᴋʀᴅɪᴀ ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴘʀᴇɢɴᴇɴᴛ 🤣🤣",
"ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴛᴇʀɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ꜱᴜᴀʀ ᴋᴀ ʟᴏᴜᴅᴀ ᴏʀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴇʀᴀ ʟᴏᴅᴀ",
"ᴄʜᴀʟ ᴄʜᴀʟ ᴛᴜ ᴀᴘɴɪ ᴍᴀᴀᴋɪ ᴄʜᴜᴄʜɪʏᴀ ᴅɪᴋᴀ",
"ʜᴀʜᴀʜᴀʜᴀ ʙᴀᴄʜʜᴇ ᴛᴇʀɪ ᴍᴀᴀᴀᴋᴏ ᴄʜᴏᴅ ᴅɪᴀ ɴᴀɴɢᴀ ᴋᴀʀᴋᴇ",
"ᴛᴇʀɪ ɢꜰ ʜᴇ ʙᴀᴅɪ ꜱᴇxʏ ᴜꜱᴋᴏ ᴘɪʟᴀᴋᴇ ᴄʜᴏᴏᴅᴇɴɢᴇ ᴘᴇᴘꜱɪ",
"2 ʀᴜᴘᴀʏ ᴋɪ ᴘᴇᴘꜱɪ ᴛᴇʀɪ ᴍᴜᴍᴍʏ ꜱᴀʙꜱᴇ ꜱᴇxʏ 💋💦",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴄʜᴇᴇᴍꜱ ꜱᴇ ᴄʜᴜᴅᴡᴀᴠᴜɴɢᴀ ᴍᴀᴅᴇʀᴄʜᴏᴏᴅ ᴋᴇ ᴘɪʟʟᴇ 💦🤣",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋɪ ᴄʜᴜᴛʜ ᴍᴇ ᴍᴜᴛʜᴋᴇ ꜰᴀʀᴀʀ ʜᴏᴊᴀᴠᴜɴɢᴀ ʜᴜɪ ʜᴜɪ ʜᴜɪ",
"ꜱᴘᴇᴇᴅ ʟᴀᴀᴀ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴄʜᴏᴅᴜ ʀᴀɴᴅɪᴋᴇ ᴘɪʟʟᴇ 💋💦🤣",
"ᴀʀᴇ ʀᴇ ᴍᴇʀᴇ ʙᴇᴛᴇ ᴄʏᴜ ꜱᴘᴇᴇᴅ ᴘᴀᴋᴀᴅ ɴᴀ ᴘᴀᴀᴀ ʀᴀʜᴀ ᴀᴘɴᴇ ʙᴀᴀᴘ ᴋᴀ ʜᴀʜᴀʜᴀ ᴛᴇʀɪ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ🤣🤣",
"ꜱᴜɴ ꜱᴜɴ ꜱᴜᴀʀ ᴋᴇ ᴘɪʟʟᴇ ᴊʜᴀɴᴛᴏ ᴋᴇ ꜱᴏᴜᴅᴀɢᴀʀ ᴀᴘɴɪ ᴍᴜᴍᴍʏ ᴋɪ ɴᴜᴅᴇꜱ ʙʜᴇᴊ",
"ᴀʙᴇ ꜱᴜɴ ʟᴏᴅᴇ ᴛᴇʀɪ ʙᴇʜᴇɴ ᴋᴀ ʙʜᴏꜱᴅᴀ ꜰᴀᴀᴅ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀᴋᴏ ᴋʜᴜʟᴇ ʙᴀᴊᴀʀ ᴍᴇ ᴄʜᴏᴅ ᴅᴀʟᴀ 🤣🤣💋",
"ꜱʜʀᴍ ᴋʀ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ ʏʜᴀ",
"ᴍᴇʀᴇ ʟᴜɴᴅ ᴋᴇ ʙᴀᴀᴀᴀᴀʟʟʟʟʟ ᴘᴋᴅ ᴊᴀʟᴅɪ sᴇ",
"ᴛᴜ ᴇᴋ ᴋᴀᴀᴍ ᴋʀ ᴀᴘɴɪ ᴍᴀ ʙʜᴇɴ ᴋᴏ ᴄᴜᴅᴡᴀ ʟᴇ ᴍᴇʀᴇ sᴛʜ",
"ʀɴᴅɪ ᴋᴇ ʟᴅᴋᴇᴇᴇᴇᴇᴇᴇᴇᴇ ᴄʜᴜᴘ ᴏʀ ᴄᴜᴅ ʏʜᴀ",
"ᴄʜᴜᴘ ᴛᴍᴋᴄ ᴋɪᴅꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱꜱ",
"ᴀᴘɴɪ ɢᴀᴀɴᴅ ᴍᴇɪɴ ᴍᴜᴛʜɪ ᴅᴀᴀʟ",
"ᴍᴇʀᴀ ʟᴜɴᴅ ᴄʜᴏᴏꜱ ᴊᴀʟᴅɪ sᴇ",
"ᴀᴘɴɪ ᴍᴀ ᴋᴏ ᴄᴜsᴡᴀ ᴍᴇʀᴀ ʟᴜɴᴅ",
"ʙʜᴇɴ ᴋᴇ ʟᴀᴜᴅᴇ ᴛᴍᴄ",
"ʙʜᴇɴ ᴋᴇ ᴛᴀᴋᴋᴇ ᴛᴍʟ",
"ᴀʙʟᴀ ᴛᴇʀᴀ ᴋʜᴀɴ ᴅᴀɴ ᴄʜᴏᴅɴᴇ ᴋɪ ʙᴀʀɪɪɪ",
"ʙᴇᴛᴇ ᴛᴇʀɪ ᴍᴀ ꜱʙꜱᴇ ʙᴅɪ ʀᴀɴᴅ",
"ʟᴜɴᴅ ᴋᴇ ʙᴀᴀᴀʟ ᴊʜᴀᴛ ᴋᴇ ᴘɪꜱꜱꜱᴜᴜᴜᴜᴜᴜᴜ ᴛᴍᴋᴄ",
"ʟᴜɴᴅ ᴘᴇ ʟᴛᴋɪᴛ ᴍᴀᴀᴀʟʟʟʟ ᴋɪ ʙᴏɴᴅ ʜ ᴛᴜᴜᴜ",
"ᴋᴀꜱʜ ᴏꜱ ᴅɪɴ ᴍᴜᴛʜ ᴍʀᴋᴇ ꜱᴏᴊᴛᴀ ᴍ ᴛᴜ ᴘᴀɪᴅᴀ ɴᴀ ʜᴏᴛᴀᴀ",
"ɢʟᴛɪ ᴋʀᴅɪ ᴛᴜᴊᴡ ᴘᴀɪᴅᴀ ᴋʀᴋᴇ ᴛᴇʀʏ ᴍᴀ ɴᴇ ᴀʙ ᴄᴜᴅ ᴛᴜ ʏʜᴀ",
"ꜱᴘᴇᴇᴅ ᴘᴋᴅᴅᴅ",
"ɢᴀᴀɴᴅ ᴍᴀɪɴ ʟᴡᴅᴀ ᴅᴀʟ ʟᴇ ᴀᴘɴɪ ᴍᴇʀᴀᴀᴀ",
"ɢᴀᴀɴᴅ ᴍᴇɪɴ ʙᴀᴍʙᴜ ᴅᴇᴅᴜɴɢᴀᴀᴀᴀᴀᴀ",
"ɢᴀɴᴅ ꜰᴛɪ ᴋᴇ ʙᴀʟᴋᴋᴋ ᴛᴜ ᴄᴜᴅ ʏʜᴀ",
"ɢᴏᴛᴇ ᴋɪᴛɴᴇ ʙʜɪ ʙᴀᴅᴇ ʜᴏ, ʟᴜɴᴅ ᴋᴇ ɴɪᴄʜᴇ ʜɪ ʀᴇʜᴛᴇ ʜᴀɪ",
"ʜᴀᴢᴀᴀʀ ʟᴜɴᴅ ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴀɪɴ",
"ᴊʜᴀᴀɴᴛ ᴋᴇ ᴘɪꜱꜱᴜ ᴛᴍᴋᴄ sᴜɴ",
"ᴛᴇʀɪ ᴍᴀ ᴋɪ ᴋᴀʟɪ ᴄʜᴜᴛ",
"ᴋʜᴏᴛᴇʏ ᴋɪ ᴀᴜʟᴅᴀ ᴇʏ ᴛᴜ ʀᴀɴᴅʏᴋᴇ",
"ᴋᴜᴛᴛᴇ ᴋᴀ ᴀᴡʟᴀᴛ ᴊᴀɪsᴀ ʟɢ ʀʜᴀ ᴛᴜ",
"ᴋᴜᴛᴛᴇ ᴋɪ ᴊᴀᴛ ᴊᴀɪsᴀ ᴇʏ ᴛᴜ ",
"ᴋᴜᴛᴛᴇ ᴋᴇ ᴛᴀᴛᴛᴀ ᴇʏ ᴛᴜ",
"ᴛᴇᴛɪ ᴍᴀ ᴋɪ.ᴄʜᴜᴛ , ᴛᴇʀɪ ᴍᴀ ʀɴᴅɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪɪ",
"ʟᴀᴠᴅᴇ ᴋᴇ ʙᴀʟ ᴘᴋᴅ ʟᴇ ᴍᴇʀᴇ",
"ᴍᴜʜ ᴍᴇɪ ʟᴇʟᴇ ᴍᴇʀᴀ ʟᴜɴᴅ",
"ʟᴜɴᴅ ᴋᴇ ᴘᴀꜱɪɴᴇ ᴄʜᴜᴘ ʙᴇᴛʜ ᴏʀ ᴄᴜᴅ",
"ᴍᴇʀᴇ ʟᴡᴅᴇ ᴋᴇ ʙᴀᴀᴀᴀᴀʟʟʟ",
"ʜᴀʜᴀʜᴀᴀᴀᴀᴀᴀ ᴛᴇʀʏ ᴍᴀᴀ ᴄᴜᴅ ɢᴀɪ",
"ᴛᴜ ᴄʜᴜᴅ ɢʏᴀᴀᴀᴀᴀ",
"ʀᴀɴᴅɪ ᴋʜᴀɴᴇ ᴋɪ ᴜʟᴀᴅᴅᴅ",
"ꜱᴀᴅɪ ʜᴜɪ ɢᴀᴀɴᴅ",
"ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴀɪɴ ᴋᴜᴛᴇ ᴋᴀ ʟᴜɴᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏꜱᴅᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ",
"ᴛᴇʀᴇ ɢᴀᴀɴᴅ ᴍᴇɪɴ ᴋᴇᴇᴅᴇ ᴘᴀᴅᴀʏ",
"ɴʏ ɴʏ ᴛᴇʀʏ ᴍᴀᴀ ʀᴀɴᴅɪ",
"ꜱᴜɴɴ ᴍᴀᴅᴇʀᴄʜᴏᴅ ᴛᴍʟ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏꜱᴅᴀ",
"ʙᴇʜᴇɴ ᴋ ʟᴜɴᴅ ᴄʜᴜᴘᴄʜᴀᴘ ᴄᴜᴅ ʏʜᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ᴄʜᴜᴛ ᴋɪ ᴄʜᴛɴɪɪɪɪ",
"ᴍᴇʀᴀ ʟᴀᴡᴅᴀ ʟᴇʟᴇ ᴛᴜ ᴀɢᴀʀ ᴄʜᴀɪʏᴇ ᴛᴏʜ",
"ᴄʜᴜᴘ ɢᴀᴀɴᴅᴜ",
"ᴄʜᴜᴘ ᴄʜᴜᴛɪʏᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴘᴇ ᴊᴄʙ ᴄʜᴀᴅʜᴀᴀ ᴅᴜɴɢᴀ",
"ꜱᴀᴍᴊʜᴀᴀ ʟᴀᴡᴅᴇ",
"ʏᴀ ᴅᴜ ᴛᴇʀɪ ɢᴀᴀɴᴅ ᴍᴇ ᴛᴀᴘᴀᴀ ᴛᴀᴘ��",
"ᴛᴇʀɪ ʙᴇʜᴇɴ ᴍᴇʀᴀ ʀᴏᴢ ʟᴇᴛɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴇ ꜱᴀᴀᴛʜ ᴍᴍꜱ ʙᴀɴᴀᴀ ᴄʜᴜᴋᴀ ʜᴜ���不�不",
"ᴛᴜ ᴄʜᴜᴛɪʏᴀ ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴛɪʏᴀ",
"ᴀᴜʀ ᴋɪᴛɴᴀ ʙᴏʟᴜ ʙᴇʏ ᴍᴀɴɴ ʙʜᴀʀ ɢᴀʏᴀ ᴍᴇʀᴀ�不",
"ᴛᴇʀɪɪɪɪɪɪ ᴍᴀᴀᴀᴀ ᴋɪ ᴄʜᴜᴛᴛᴛ ᴍᴇ ᴀʙᴄᴅ ʟɪᴋʜ ᴅᴜɴɢᴀ ᴍᴀᴀ ᴋᴇ ʟᴏᴅᴇ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ʟᴇᴋᴀʀ ᴍᴀɪ ꜰᴀʀᴀʀ",
"ᴛᴇʀʏ ᴍᴀᴀ ʀᴀɴɪᴅɪɪɪ",
"ᴄʜᴜᴘ ʙᴀᴄʜᴇᴇ ᴛᴍᴋᴄ",
"ᴛᴇʀʏ ᴍᴀᴋᴏᴄʜᴏᴅᴜ",
"ʀᴀɴᴅɪ ᴍᴀᴀ ᴛᴇʀʏ",
"ᴛᴜ ʀᴀɴᴅɪ ᴋᴇ ᴘɪʟʟᴀ ᴇʏ",
"ᴛᴇʀɪɪɪɪɪ ᴍᴀᴀᴀ ᴋᴏ ʙʜᴇᴊᴊᴊ",
"ᴛᴇʀᴀᴀ ʙᴀᴀᴀᴀᴘ ʜᴜ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ʜᴀᴀᴛ ᴅᴀᴀʟʟᴋᴇ ʙʜᴀᴀɢ ᴊᴀᴀɴᴜɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ꜱᴀʀᴀᴋ ᴘᴇ ʟᴇᴛᴀᴀ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ɢʙ ʀᴏᴀᴅ ᴘᴇ ʟᴇᴊᴀᴋᴇ ʙᴇᴄʜ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍÉ ᴋᴀᴀʟɪ ᴍɪᴛᴄʜ",
"ᴛᴇʀɪ ᴍᴀᴀ ꜱᴀꜱᴛɪ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴋᴀʙᴜᴛᴀʀ ᴅᴀᴀʟ ᴋᴇ ꜱᴏᴜᴘ ʙᴀɴᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴅᴇᴛᴏʟ ᴅᴀᴀʟ ᴅᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀᴀᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ʟᴀᴘᴛᴏᴘ",
"ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ʜᴀɪ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ʙɪꜱᴛᴀʀ ᴘᴇ ʟᴇᴛᴀᴀᴋᴇ ᴄʜᴏᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴀᴍᴇʀɪᴄᴀ ɢʜᴜᴍᴀᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ɴᴀᴀʀɪʏᴀʟ ᴘʜᴏʀ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴇ ɢᴀɴᴅ ᴍᴇ ᴅᴇᴛᴏʟ ᴅᴀᴀʟ ᴅᴜɴɢᴀ",
"ᴛᴇʀɪ ᴍᴀᴀᴀ ᴋᴏ ʜᴏʀʟɪᴄᴋꜱ ᴘɪʟᴀᴜɴɢᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ꜱᴀʀᴀᴋ ᴘᴇ ʟᴇᴛᴀᴀᴀ ᴅᴜɴɢᴀᴀᴀ",
"ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀᴀ ʙʜᴏꜱᴅᴀ",
"ᴍᴇʀᴀᴀᴀ ʟᴜɴᴅ ᴘᴀᴋᴀᴅ ʟᴇ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴄʜᴜᴘ ᴛᴇʀɪ ᴍᴀᴀ ᴀᴋᴀᴀ ʙʜᴏꜱᴅᴀᴀ",
"ᴛᴇʀɪɪɪ ᴍᴀᴀ ᴄʜᴜꜰ ɢᴇʏɪɪ ᴋʏᴀᴀᴀ ʟᴀᴡᴅᴇᴇᴇ",
"ᴛᴇʀɪɪɪ ᴍᴀᴀ ᴋᴀᴀ ʙᴊꜱᴏᴅᴀᴀᴀ",
"ᴍᴀᴅᴀʀxʜᴏᴅᴅᴅ",
"ᴛᴇʀɪᴜᴜɪ ᴍᴀᴀᴀ ᴋᴀᴀ ʙʜꜱᴏᴅᴀᴀᴀ",
"ᴛᴇʀɪɪɪɪɪɪ ʙᴇʜᴇɴɴɴɴ ᴋᴏ ᴄʜᴏᴅᴅᴅᴜᴜᴜᴜ ᴍᴀᴅᴀʀxʜᴏᴅᴅᴅᴅ",
"ᴛᴜ ɴɪᴋᴀʟ ᴍᴀᴅᴀʀᴄʜᴏᴅ",
"ᴄʜᴜᴘ ʀᴀɴᴅɪ ᴋᴇ ʙᴀᴄʜᴇ",
"ᴛᴇʀᴀ ᴍᴀᴀ ᴍᴇʀɪ ᴊᴀᴀɴ ᴇʏ",
"ᴛᴇʀɪ ꜱᴇxʏ ʙᴀʜᴇɴ ᴋɪ ᴄʜᴜᴛ ᴏᴘ"
"👩🏿      👩🏻‍🦳        👵🏼         👱🏿‍♀️     \n👖      👖        👖         👖     \n\nतेरी बहन /तेरी माँ /तेरी दादि/ तेरीभुआ.\n\nसब की 𝐂hu𝐃𝐀i hogi",
"तेरी माँ के（ ͜.人 ͜.）दबा दूंगा",
"तेरी मा चुदी हुई थी\nचुदी हुई है\nऔर चुदी हुई रहेगी \n\n\"MARK MY WORD\" 😈",
"𝐊ʏᴀ?\n𝐂ʏᴀ?\n𝐂ᴜᴀ?\n\n𝐌ᴛᴛ 𝐊ʀʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐏𝐞 𝐓ʜ𝐀ᴘᴘᴀᴅ 𝐌ᴀ𝐚ʀ 𝐃ᴜɴɢᴀ",
"˚∧＿∧  　+        — ͟͞͞🥛\n(  •‿• )つ  — ͟͞͞ 🥛 \nSpecial attack tery mummy ke chuchiya ka dudu 🐱🎀",
"Aaj Rakshabandhan Ke Avsar Pr तेरी मांँ मेरे लंड पर राखी Bandh Ke चुदेगी 😍🥰",
"Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye 😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
"Tery Maa Behen Ke Boshde Me Kya Maarun Jaldi Bata 😜🤙",
"Tery Maa\nⓘ Verified Randy // 🦅🔥",
"𝐒ᴀʏ 𝐑ᴀɴᴅɪʙᴀᴀᴢ 𝐃ᴀᴅᴅʏ 𓆩💗𓆪",
"𝐖ᴏ ʙʜɪ ᴋʏᴀ ᴅɪɴ ᴛʜᴇ ᴊᴀʙ ᴛʀʏ ᴍᴀᴀ ᴍᴜᴊʜᴇ 𝐀ᴘɴᴀ 𝐂ʜᴜᴛ 𝐃ᴇᴛɪ ᴛʜɪ ʏᴀᴀʀ 💔🥀👌🏻",
"𝐀ᴡᴀᴢ 𝐍ɪᴄʜᴇ 𝐆ᴜʟᴀᴀᴍ 🤢👇🏻",
"𝐓ʀʏ 𝐌ᴀᴀ ɴᴇ 𝐂ʜᴜᴅɴᴇ 𝐌ᴀɪ ɢᴏʟᴅ 𝐌ᴇᴅᴀʟ 𝐉ᴇᴇᴛᴀ ᴇʏ 𝐃ᴏꜱᴛ 🤩👑",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐋ᴜɴᴅ 🖕🏻😈",
"𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐀ᴘɴɪ 𝐁ᴇʜᴇɴ 𝐂ʜᴜᴅᴀ 🖕🏻😈",
"𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🖕🏻😈",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ ᴋʜᴏʟ ᴅᴜɴɢᴀ 🔓😈",
"𝐁ʜᴇɴᴄʜᴏᴅ ??ᴘɴɪ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🤡💩",
"𝐓𝐌𝐊𝐂 ᴘᴇ 𝐂ʜᴀᴘᴘᴀʟ 𝐌ᴀᴀʀᴜɴɢᴀ 👟💥",
"𝐁ʜᴏꜱᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
"𝐑ᴀɴᴅɪ ᴋɪ 𝐀ᴜʟᴀᴅ ᴄʜᴜᴘ ʜᴏ ᴊᴀ 🔇😒",
"𝐑ᴀɴᴅɪʙᴀᴀᴢ ka 𝐆ᴜʟᴀᴀᴍ ey ᴛᴜ ᴀʙ ᴛᴜ ʏʜᴀ ᴄᴜᴅᴋᴇ ᴅɪᴋʜᴀ ᴛᴇʀʏ ᴍᴀᴋᴏ ʟᴇᴋʀ 👑😎",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ɪʀᴄʜɪ 🌶️🖕🏻",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐏ᴀɪʀ 🦶🏻😈",
"𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ 🗑️😏",
"𝐑ᴀɴᴅɪ ᴋᴀ 𝐏ɪʟʟᴀ ʜᴀɪ ᴛᴜ 🐕💩",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴏ 𝐁ᴀᴢᴀᴀʀ 𝐌ᴇ 𝐂ʜᴏᴅᴜɴɢᴀ 🌃😈",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐆ᴀʀᴀᴍ 𝐓ᴇʟ 🌡️🖕🏻",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴍᴇʀɪ 𝐑ᴀɴᴅɪ 💋👿",
"𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴏ 𝐑ᴀᴀᴛ ʙʜᴀʀ 𝐂ʜᴏᴅᴜɴɢᴀ 🌙😈",
"𝐑ᴀɴᴅɪ ᴋᴀ 𝐁ᴀᴄᴄʜᴀ ʜᴀɪ ᴛᴜ ꜱᴀᴀʟᴇ 🤡💀",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐉ᴏᴏᴛᴀ 👞🖕🏻",
"𝐑ᴀɴᴅɪʙᴀᴀᴢ 𝐃ᴀᴅᴅʏ ᴋᴀ 𝐆ᴜʟᴀᴀᴍ ʜᴀɪ ᴛᴜ 🥀😤",
"ᴊɪꜱ ᴅɪɴ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ꜱᴏᴄʜᴀ ᴛʜᴀ ᴋᴀꜱʜ ᴀʙᴏʀᴛ ᴋᴀʀ ᴅᴇᴛɪ 💀🥀",
"𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 𝐓ᴇʀʏ 𝐌ᴀ 𝐂ᴜᴅ 𝐑ʜɪ🐕😂",
"𝐓ᴇʀʏ 𝐌ᴀ 𝐂ᴜᴅ 𝐑ʜɪ 𝐆ᴀʟɪ ᴋᴀ 𝐊ᴜᴛᴛᴀ ʜᴀɪ ᴛᴜ 🐕🗑️",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ᴍᴜᴊʜᴇ ᴅᴇᴋʜ ᴋᴇ ꜱᴏᴄʜᴀ ᴋᴀꜱʜ ʏᴇ ᴍᴇʀᴀ ʙᴇᴛᴀ ʜᴏᴛᴀ 🫦😏",
"𝐂ʜᴜᴘ ᴋᴀʀ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴀᴜᴋᴀᴛ ɴᴀʜɪ ᴍᴇʀᴇ ꜱᴀᴀᴍɴᴇ ʙᴏʟɴᴇ ᴋɪ 🤐💀",
"𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴅᴀɪ ᴍᴇ ᴊᴀʙ ᴍᴀɪ ᴛʜᴀ ᴛᴏ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 💀😂",
"𝐁ʜᴀɢ ʏᴀʜᴀɴ ꜱᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 🐕💨",
"𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ ꜱᴀᴅɪ 𝐌ᴇ ᴍᴇʀᴀ ʟᴜɴᴅ 💍😈",
"𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴀᴘɴɪ 𝐌ᴀᴀ ᴍᴀᴛ ᴄʜᴜᴅᴀ 🖕🏻👹",
"𝐁ʜᴇɴᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
"tery ma cudke pgl dekh..𝐁𝐊𝐂 🦴🐕",
"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 𝐒ᴇ - 🦢💘",
"tery 𝐌ᴀᴀ cudke 𝐌ᴀʀʀ  𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ! 🌙",
"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga tery mako 😹💔🔥😆👊🏻💥",
"chudke bhaga kaise 😂💥🤣🤘🏻",
"ne toh - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ka lun muh me lelia tune or tery maa ne😂🙏🏻😂🙏🏻",
"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
"mkl lun te vaj 😂✊🏻💦",
"𝗧ᴍᴋ𝗕 pe - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ka hamla 😂⚔🔥💥",
"𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
"chl rndyce chud ke dikha 😂💥🤣🔥",
"tery 𝐌ᴀᴀ or bhen 𝐌ᴀʀʀ  𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
"tera baap bass - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 ey 😂🎀",
"try maa hagte hue paad mari -#😹🔥🥀",
"𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
"नहीं नहीं तेरी मां को 𝐒ɪʀғ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
"𝑻𝒆𝒓?? 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
"सोच तेरी बहन को - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप का गुलाम चोद रहा 😎🔥",
"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 /~ 👑 बाप से सही chudi 🥵🔥",
"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ - 𝐑𝐀𝐍𝐃𝐈𝐁𝐀𝐀𝐙 बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
"Tᴇʀɪ Mᴀᴀ Rᴀɴᴅɪ (🩷)—(❤️)—(🧡)—(💛)—(💚)—(🩵)—(💙)—(💜)—(🖤)—(🩶)—(🤍)—(🤎)—(🌸)—(✨)—(🌙)—(⭐)—(🦋)—(💎)—(👑)—(⚡)—(🔥)—(🌌)—(🎀)—(💫)—(🪽)—(🫧)—(🌸)—(💘)—(💓)—(💖)—(💕)—(💞)",
"Teri make hath me chakku se hole karke lund daluga apna 🤢🤢",
"Subha ho ya sham chudte rhena hai teri maaka kaam😂🔥😂🔥😂🔥",
"𝐓ᴜ 𝐒ᴡɪᴘᴇ 𝐊ᴀʀᴛᴀ 𝐑ᴇʜ 𝐌ᴀɪ ᴄʜᴀʟᴀ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴇ 𝐒ᴀᴛʜ 𝐊ʜᴇʟɴᴇ 😭😭",
"🍑\n🟨  😂\n🟨🟥🟥🟨\n     🟥🟥🟨\n     ⬛⬛ \n     ⬛⬛\nTery ma ki bund hi okhad li.",
"𝘗𝘺𝘢𝘴 𝘭𝘢𝘨 𝘳𝘢𝘩𝘪 𝘵𝘦𝘳𝘪 𝘮𝘢𝘢 𝘬𝘰 𝘤𝘰𝘥 𝘬𝘦 𝘱𝘺𝘢𝘴 𝘣𝘶𝘫𝘩𝘢𝘶𝘯𝘨𝘢 🖕🏿😂🔥🙏🏿",
"▶︎ •၊၊၊|။||။‌‌‌‌‌၊|• 0:60\n𝘋𝘦𝘬𝘩 𝘵𝘦𝘳𝘪 𝘣𝘦𝘩𝘦𝘯 ??𝘪 𝘤𝘩𝘪𝘬𝘩 😂😱🔥🙏🏿",
"      ᴹᴱ:\n👆       🤬 ᴷᴬᴴᴬ ᴮᴴᴬᴳᵀᴵ ᴴᴬᴵ ᴿᴬᴺᴰᴵ\n  🐛💤👔🤳\n            ⛽  👢\n          ⚡👟\n       🎸    🌂\n      👢       👢     ᵀᴱᴿᴵ ᴹᴬᴬ:🏃‍♀‍➡️ᴹᵁᴶᴴᴱ ᴹᴬᵀ ᶜᴴᴼᴰᴼ",
"🙌\n😛 ᴹᴱ:\n  |      👩 ᵀᴱᴿᴵ ᴹᴬᴬ:\n  |   8_/ 👐\n / \\  / \\\n  \"Take a look how i am chodunging your Mummy in ghodi pose 🗿\"",
"../\\_/\\\n  ( • _ •)  \n  /    >🍆 \n\nʏᴇ ᴘᴀᴋᴀᴅᴏ ᴀᴘᴋɪ ᴍᴏᴍ ᴋᴏ ᴀᴘɴᴇ ᴄʜᴜᴛ ᴍᴇ ɢʜᴜssᴀ ɴᴇ ᴍᴇ ᴋᴀᴀᴍ ᴀʏᴇɴɢᴀ 🤗",
"ㅤㅤ😎 ᴹᴱ:\n          |\\👐\n         / \\_\n━━━━━┓ ＼＼\n┓┓┓┓┓┃ᵀᴼᴴᴬᴿ ᴿᴬᴺᴰᴵ ᴹᴬᴬ:\n┓┓┓┓┓┃ ヽ😩ノ\n┓┓┓┓┓┃ 　 /　ᴼᴿᴵᴵ ᴬᴹᴹᴬ\n┓┓┓┓┓┃  ノ)　\n┓┓┓┓┓┃\n\nLE TERI MAA KO CHOD KAR FHEK DIA 🥸",
"😎 ᴍᴀɪ:\nく|)へ\n   〉\n￣┗┓       ヾ😫ｼ ᴛᴇʀɪ ᴍᴀᴀ:\n         ┗┓   ヘ/    \n             ┗┓ノ\n                 ┗┓       ヾ😨ｼ ᴛᴇʀᴀ ʙᴀᴀᴘ:\n                      ┗┓   ヘ/\n                          ┗┓ノ\n                               ┗┓       ヾ😩ｼ ᴛᴇʀᴀ ᴄʜᴀᴄʜᴀ:\n                                   ┗┓   ヘ/    \n                                       ┗┓ノ\nᴅᴇᴋʜ ᴀɪsᴇ ʜɪ ʟᴀᴀᴛ ᴍᴀᴀʀ ᴋᴀʀ ʙʜᴀɢᴀᴜɴɢᴀ ᴛᴇʀᴇ ᴋʜᴀᴀɴᴅᴀɴ ᴋᴏ 🤫🤣",
"╭👇 ͡ ͡° ͜   ͡ ͡°)╭👇 \n      \\   .   .\\\n        \\        \\\n         \\╰[ ]╯\\ \n          /   U   \\\n       👟       👟\n\nᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴍᴇʀᴀ ʟᴜɴᴅ ᴍᴜʙᴀʀᴀᴋ ʜᴏ 😝",
"Once a man said: \n\"You deserve all the chudayi and teri maa ki chutt dhulayi, and this text proves it! You should be proud!\" 🕊️",
"😏 ᴍᴀɪ:\n    | 👐💵\n    |//    💵\n    |          💸 ᴛᴇʀɪ ʀᴀɴᴅʏ ᴍᴀᴀ:\n   /\\            👯👯\n👟👟\n\nDᴇᴋʜ Kᴇsᴇ Tᴇʀɪ Mᴀᴀ Kᴏ Aᴘɴᴇ Pᴀɪsᴏ Sᴇ Rᴀɴᴅɪ Nᴀᴄʜ Kᴀʀᴡᴀ Rʜᴀ Hᴜ 🤙😎",
"Loading your maa ki chudai video 😳\n\n■■■■■■■■□\n99%",
"Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye  😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
"this message could't be display because teri maa randy ey",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
"तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
"तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
"𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
"𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
"˙✧˖°📷༘ ⋆｡° 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°",
"𓂃✍︎ 𝑵ʏ 𝑵ʏ 𝑨ʙ 𝑲ᴜᴄʜ 𝑵ʏ 𝑯ᴏ 𝑺ᴋᴛᴀ 𝑻ᴇʀɪ  𝑪ᴜᴅᴀɪ 𝑲ɪ 𝑺ᴄʀɪᴘᴛ 𝑨ʙ 𝑳ᴇᴀᴋ 𝑯ᴏᴋᴇ 𝑯ʏ 𝑴ᴀɴᴇɢɪ 𓂃✍︎",
"⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
"🇮🇳 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇮🇳",
"🇯🇵 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇯🇵",
"🇺🇸 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇺🇸",
"🇬🇧 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐔𝐊 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇬🇧",
"🇰🇷 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇰🇷",
"🇩🇪 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇩🇪",
"🇫🇷 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐅ʀᴀɴᴄᴇ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇫🇷",
"🇮🇹 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐈ᴛᴀʟʏ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇮🇹",
"🇧🇷 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐁ʀᴀᴢɪʟ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇧🇷",
"🇨🇦 ✦ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴇ 𝐒ᴀᴛʜ  ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️  𝐁ᴀᴀᴘ 𝐀ᴜʀ  𝐂ᴀɴᴀᴅᴀ 𝐖ᴀʟᴇ 𝐁ʜɪ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ✦ 🇨🇦",
"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💛 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💚 ݁˖⭑.ᐟ",
"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐒𝐋𝐀𝐕𝐄 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐓𝐌𝐊𝐂 -/- ⋆˚💙 ݁˖⭑.ᐟ",
]

# ─── FUN RAIDS TEXT LISTS (Menu8) ──────────────────────────────────────

shayari_texts = [
"तेरी आँखों में खोया रहूँ, तू मिले तो ये जहाँ भूल जाऊँ। 💕",
"प्यार में क्या रखा है, बस तेरे बिना लगता है जीना भी सज़ा नहीं। 💔",
"चाँद से खूबसूरत है तेरा चेहरा, तू है तो दुनिया लगती है मेरी। 🌙",
"तेरी यादों में खोया रहूँ, हर सांस में तू बसी है। 💭",
"हर दिन तुझसे प्यार बढ़े, हर सांस तुझसे निभे। 💗",
"तेरी हँसी में जान है, तेरी बातों में पहचान है। 😊",
"तेरी बाहों में मिली राहत, तेरी आँखों में मिला सुकून। 🌹",
"तू है तो हर ग़म भूला, तू है तो ये दिल झूला। 🎠",
"हर रोज़ तुझसे प्यार हो, हर शाम तुझपे निसार हो। 🌅",
"तेरी मुस्कान है जादू, जो बिखेरे हर दिन बहार। 🌺",
"Your love is the poetry my heart always wanted to write. 📝💖",
"In a world full of trends, I want to remain your timeless classic. 🌟",
"You are the missing piece of my soul, the calm in my chaos. 🧩",
"Every love story is beautiful, but ours is my favorite chapter. 📖",
"You are the sun in my day, the moon in my night, and the stars in my dreams. 🌞🌙",
"Meeting you was fate, becoming your friend was a choice, but falling in love with you was beyond my control. 💫",
"I didn't choose you, my heart did. And it doesn't know how to unchoose. ❤️‍🔥",
"You are not just my love; you are my home. 🏠",
"Your smile is the best part of my day, and your laugh is my favorite sound. 😄🎶",
"You are my today and all of my tomorrows. 📅❤️",
"Teri smile dekh ke lagta hai, jaise mera wifi full signal pe aa gaya. 📶😄",
"Pyaar kya hai? Maine tujhse jaana, tera naam sunke hi dil ho jaata hai deewana. 🫀",
"Tu hai toh din hai, warna toh har pal hai night shift. 🌃",
"Dil ki baat kehni thi, bas yahi socha, tujhse milke samjha, pyaar kya hai bhai! 🥰",
"Teri ek smile pe, main de doon jaan bhi, par tu maange toh, de doon duniya bhi. 😄🌎",
"Chand se chura ke laaya hoon, teri muskaan, rakh lo dil mein, yeh hai meri jaan. 🌙💖",
"Tere bina dil hai veeran, tu aaja ve, dil ki yeh raah, hai bas teri hi ore. 🛤️💔",
"Pyaar ka sabak mila, tujhse hi yaar, ab toh bas tera hi hai, yeh dil bekarar. 🫀",
"Kya baat hai tujh mein, hai koi jaadu, dekhta hi rahu, na ho mera wajood. 👀✨",
"Tu hi meri subah, tu hi mera sukoon, tere bina toh jaise, khaali hai yeh khwabon ka jahoon. ☁️"
]

rizz_texts = [
"क्या तुम सड़क हो? क्योंकि मैं हर दिन तुम्हें क्रॉस करना चाहता हूँ। 😏",
"तुम्हारी हँसी सुनकर लगता है जैसे मेरा दिन बन गया। 😄",
"तुम्हारी आँखों में खो जाऊँ तो वापस न आऊँ। 👀",
"क्या तुम्हारे पास कोई मैप है? क्योंकि मैं तुम्हारे दिल में खो गया हूँ। 🗺️",
"तुम बिना makeup के भी परफेक्ट हो – लेकिन मैं तो तुम्हें हर तरह से चाहता हूँ। 💋",
"मैं तुमसे प्यार नहीं करता – मैं तो तुम्हें worship करता हूँ। 🙌",
"तुम मेरे दिन की सबसे अच्छी notification हो। 🔔",
"तुम मेरे सबसे पसंदीदा गाने की धुन हो। 🎶",
"मैं तुम्हें चाँद से भी ऊपर रखता हूँ – क्योंकि तुम तो सूरज हो। ☀️",
"तुम मेरी रूह की तसल्ली हो – बस साथ रहो। 🕊️",
"Are you a magician? Because whenever I look at you, everyone else disappears. 🎩✨",
"Do you have a map? I keep getting lost in your eyes. 🗺️👀",
"Is your name Google? Because you have everything I'm searching for. 🔍💕",
"Are you a camera? Because every time I look at you, I smile. 📸😊",
"If beauty were a crime, you'd be serving a life sentence. ⛓️🔥",
"Do you believe in love at first sight, or should I walk by again? 🚶‍♂️🔄",
"Excuse me, but I think you dropped something – my jaw. 👇😮",
"Are you Wi-Fi? Because I'm feeling a connection. 📶❤️",
"If you were a vegetable, you'd be a cute-cumber! 🥒😉",
"You must be a 10 because you've got me feeling like a 1 with you. 1️⃣0️⃣",
"Tera naam kya hai? Kyunki mera plan hai tera baap banana! 😎👀",
"Kya tum Google ho? Kyunki mujhe tum mein woh sab milta hai jo main dhundh raha tha. 🔍💕",
"Tum toh mere WiFi jaisi ho, bina tumhare connection hi nahi aata. 📶😏",
"Kya tum chocolate ho? Kyunki main toh din raat tumhe kha sakta hoon. 🍫😋",
"Tumhari smile dekh ke lagta hai, mera din set aur raat forget. 🌞",
"Main driver nahi hoon, par tumhare dil ki steering le sakta hoon? 🚗💨",
"Kya tum Starbucks ho? Kyunki main har din tumhara naam pukaarna chahta hoon. ☕😄",
"Meri battery low hai, kya tum mere charger ban sakte ho? 🔋❤️",
"Kya tum doctor ho? Kyunki mera dil dekh ke toh tumne dhadkana sikha diya. 👨‍⚕️💓",
"Tumhari height kya hai? Kyunki lagta hai tum heaven se chhidi hui ho. 📏👼"
]

pickup_texts = [
"क्या तुम्हारा नाम Google है? क्योंकि तुममें वो सब है जो मैं ढूंढ रहा हूँ। 🔍",
"तुम्हारी आँखें तारे हैं और मैं उनमें खो जाना चाहता हूँ। ✨",
"क्या तुम WiFi हो? क्योंकि मुझे तुमसे कनेक्शन महसूस हो रहा है। 📶",
"तुम्हारी मुस्कान देखकर मेरा दिन बन जाता है। 😊",
"क्या तुम चॉकलेट हो? क्योंकि मैं तुम्हें हर वक़्त खाना चाहता हूँ। 🍫",
"तुम्हारे बिना मेरी ज़िंदगी अधूरी है। 💔",
"तुम मेरे सपनों की रानी हो। 👑",
"तुम्हारी बातें सुनकर दिल खुश हो जाता है। 💕",
"क्या तुम मेरे साथ चलोगी? 🚶‍♀️",
"तुम मेरी दुनिया हो। 🌍",
"Are you a time traveler? Because I see you in my future. ⏳",
"Is your name Angel? Because you fell from heaven. 👼",
"Do you have a Band-Aid? Because I just scraped my knee falling for you. 🩹",
"Are you a magician? Because whenever I look at you, everyone else disappears. 🎩",
"Can I follow you home? Because my parents always told me to follow my dreams. 🏠",
"Are you French? Because Eiffel for you. 🗼",
"Is your name Google? Because you have everything I'm searching for. 🔍",
"You must be a 10 because you've got me feeling like a 1 with you. 1️⃣0️⃣",
"Roses are red, violets are blue, sugar is sweet, and so are you. 🌹",
"I must be a snowflake because I've fallen for you. ❄️",
"Tum toh mere WiFi jaisi ho, bina tumhare connection hi nahi aata. 📶",
"Kya tum chocolate ho? Kyunki main toh din raat tumhe kha sakta hoon. 🍫",
"Tumhari smile dekh ke lagta hai, mera din set aur raat forget. 🌞",
"Meri battery low hai, kya tum mere charger ban sakte ho? 🔋",
"Kya tum doctor ho? Kyunki mera dil dekh ke toh tumne dhadkana sikha diya. 👨‍⚕️",
"Tumhari aankhon mein pyaar hai ya paani, maine toh dooba marne ka plan banaya. 🏊",
"Mera DNA toh tumse match karta hai, kyunki main toh tumhara hi bana hoon. 🧬",
"Tumse milke lagta hai jaise, sach mein pyaar hota hai. 😅",
"Tum toh mere sapno ki rani ho. 👑",
"Tumhari baatein sunke lagta hai, jaise koi khwab ho. 💭"
]

romance_texts = [
"तेरी आँखों की गहराई में मेरी दुनिया बसी है। 💕",
"हर सांस में तू बसी है, तू ही मेरी हँसी है। 😊",
"चाँद से खूबसूरत है तेरा चेहरा। 🌙",
"तेरी यादों में खोया रहूँ। 💭",
"प्यार का हर लम्हा तेरे साथ जीया। 🥀",
"तेरे बिना ये दिल है बेक़रार। ❤️",
"हर दिन तुझसे प्यार बढ़े। 💗",
"तेरी हँसी में जान है। 😊",
"तेरी बाहों में मिली राहत। 🌹",
"तू है तो हर ग़म भूला। 🎠",
"You are the poetry my heart always wanted to write. 📝",
"In a world full of trends, I want to be your classic. 🌟",
"You are the missing piece of my soul. 🧩",
"Our love story is my favorite chapter. 📖",
"You are the sun in my day, the moon in my night. 🌞🌙",
"Falling in love with you was beyond my control. 💫",
"I didn't choose you, my heart did. ❤️‍🔥",
"You are not just my love; you are my home. 🏠",
"Your smile is the best part of my day. 😄",
"You are my today and all of my tomorrows. 📅",
"Teri smile dekh ke lagta hai, wifi full signal pe aa gaya. 📶",
"Pyaar kya hai? Maine tujhse jaana. 🫀",
"Tu hai toh din hai, warna toh har pal hai night shift. 🌃",
"Tujhse milke samjha, pyaar kya hai bhai! 🥰",
"Teri ek smile pe, de doon jaan bhi. 😄",
"Chand se chura ke laaya hoon, teri muskaan. 🌙",
"Tere bina dil hai veeran. 💔",
"Pyaar ka sabak mila, tujhse hi yaar. 🫀",
"Kya baat hai tujh mein, hai koi jaadu. 👀",
"Tu hi meri subah, tu hi mera sukoon. ☁️"
]

troll_texts = [
"Bhai tujhe dekh ke lagta hai troll ka mascot tu hai 😂",
"Ter personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅",
"Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟",
"Teri maa ne bhi socha hoga — yaar galti ho gayi 😹",
"Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂",
"Teri iq level calculator mein error aata hai 🧮",
"Tu chhata hua papad hai — touch karte hi toot gaya 😹",
"Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞",
"Teri personality dekh ke AI bhi depressed ho gaya 🤖",
"Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂",
"Your life is like a bad web series — flop in season 1 📺",
"Your personality is like a blank meme template — nothing 😂",
"You're so boring that even sleep runs away from you 😴",
"Your existence is proof that anyone can use the internet 📶",
"Your thinking is 2G speed in a 5G world 📡",
"Your life is a loading screen that never loads ⏳",
"You're the reason 'error' exists in the dictionary 📖",
"Your vibe check: FAILED 😂",
"You're irrelevant — even Google doesn't know you 🔍",
"You're a hero whose movie flopped in 3 minutes 🎬",
"Bhai tera swag Excel mein error hai — #NAME? 📊",
"Tu itna dheema hai ke kachhua bhi race jeet gaya 🐢",
"Teri thinking 2G speed pe chal rahi hai 📡",
"Beta tera ek message dekh ke aasman bhi sharma gaya ☁️",
"Bhai teri life ek loading screen hai — jo kabhi load nahi hoti ⏳",
"Ter maa ne tujhe chhoda nahi chhodni chahiye thi 😂",
"Beta tera existence proof hai ke koi bhi internet use kar sakta hai 📶",
"Bhai teri personality ek blank page hai — aur blank hi rahega 📄",
"Tu sirf chat mein hero hai real duniya mein zero 💻",
"Beta teri soch itni outdated hai ke floppy disk bhi reject kar de 💾",
"🤡 Bhai tujhe dekh ke lagta hai troll ka mascot tu hai 😂🔥",
"😹 Tu itna troll hai ke khud ko pata nahi 💀🤡",
"🤡 Teri baatein sun ke log seriously nahi lete — aur le bhi nahi chahiye 😂😹",
"😹 Beta tu internet ka troll #1 candidate hai 💀🤡",
"🤡 Tujhe real life mein bhi ignore karte honge log 😂🔥",
"😹 Bhai teri comments section mein sabne dislike diya 👎🤡",
"🤡 Tu troll karne ki koshish karta hai — khud troll bana rehta hai 😂💀",
"😹 Teri troll game weak hai — aur weak troll game bhi troll hai 🤡🔥",
"🤡 Beta jo tu sochta hai funny hai woh boring hai 😂😹",
"😹 Bhai tera troll skill level: tutorial mode pe stuck 🤡💀",
"🤡 Tu troll hai par original nahi — copy-paste troll 😂🔥",
"😹 Teri trolling se logon ko secondhand embarrassment hoti hai 🤡😂",
"🤡 Beta tujhe seriously lena — woh troll hoga apne aap pe 😹💀",
"😹 Bhai tera meme quality — delete worthy 🤡😂",
"🤡 Tu troll karta hai online — real duniya mein kaanta nahi milta 😹🔥",
"😹 Beta teri har post pe raat ko cry karta hai 🤡💀",
"🤡 Tujhe dekh ke pata chalta hai — internet access free nahi honi chahiye 😂😹",
"😹 Bhai teri troll attempt genuine cringe hai 🤡🔥",
"🤡 Tu troll ka wannabe version hai 😂💀",
"😹 Beta asli troll woh hota hai jise pata nahi woh troll hai — tu wahi hai 🤡😂",
"🤡 Bhai teri comments log copy karke dusron ko dikhate hain — example ke liye kya nahi karna chahiye 😹🔥",
"😹 Tu troll karta hai par khud hi jal jaata hai 🤡💀",
"🤡 Beta teri troll attempts fail hoti hain kyunki tujhe original hona chahiye 😂😹",
"😹 Bhai seriously — apni energy sahi jagah lagao 🤡🔥",
"🤡 Teri trolling mein timing nahi content nahi creativity nahi 😂💀",
"😹 Beta tu woh insaan hai jo khud ko troll king samjhta hai — aur paida hota hai troll ke neeche 🤡😂",
"🤡 Bhai tera troll fail isliye hota hai — genuine nahi hai 😹🔥",
"😹 Tu troll karta hai aur end mein rota hai — classic 🤡💀",
"🤡 Beta tujhe sun ke logon ko stress nahi hoti — pity hoti hai 😂😹",
"😹 Bhai teri troll quality inspect hua — returned as defective 🤡🔥",
"🤡 Tu original troll nahi — fan-made version hai 😂💀",
"😹 Beta teri trolling attempt mein best cheez — mujhe engage nahi karta 🤡😂",
"🤡 Bhai teri presence troll community ke liye embarrassment hai 😹🔥",
"😹 Tu troll karta hai aur log silent ho jaate hain — cringe se 🤡💀",
"🤡 Beta teri troll ka response — ignore — kyunki deserve nahi karta 😂😹",
"😹 Bhai tera troll skill tree mein sirf ek node hai — aur woh bhi locked hai 🤡🔥",
"🤡 Tu troll ka demo version hai — full version nahi aaya 😂💀",
"😹 Beta trolling seekh pehle phir aa — abhi tu syllabus mein nahi hai 🤡😂",
"🤡 Bhai teri baatein sun ke log empathy feel karte hain — tere liye 😹🔥",
"😹 Tu troll nahi — annoying hai — alag concept hai 🤡💀",
"🤡 Beta tera troll game 0/10 — ek baar apni chat history padh 😂😹",
"😹 Bhai tu sirf apna time barbad kar raha hai — mera nahi 🤡🔥",
"🤡 Teri troll attempt ek baar bhi hit nahi hui — streak: 0 😂💀",
"😹 Beta tera troll unprovoked aur uninspired tha 🤡😂",
"🤡 Bhai tu troll ke bhi standards neeche hai 😹🔥",
"😹 Teri trolling see aur feel karna — dono experience kharab hain 🤡💀",
"🤡 Beta teri troll ne sirf yeh prove kiya — tujhe better kaam dhundhna chahiye 😂😹",
"😹 Bhai troll mein skill hoti hai — teri mein nahi 🤡🔥",
"🤡 Tu troll hai aur tera troll bhi troll hai — recursion 😂💀",
"😹 Beta ek advice — yeh mat kar — seriously apni life mein focus kar 🤡😎",
"Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟",
"Teri maa ne bhi socha hoga — yaar galti ho gayi 😹",
"Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂",
"Teri iq level calculator mein error aata hai 🧮",
"Tu chhata hua papad hai — touch karte hi toot gaya 😹",
"Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞",
"Teri personality dekh ke AI bhi depressed ho gaya 🤖",
"Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂",
"Your life is like a bad web series — flop in season 1 📺",
"Your personality is like a blank meme template — nothing 😂",
"You're so boring that even sleep runs away from you 😴",
"Your existence is proof that anyone can use the internet 📶",
"Your thinking is 2G speed in a 5G world 📡",
"Your life is a loading screen that never loads ⏳",
"You're the reason 'error' exists in the dictionary 📖",
"Your vibe check: FAILED 😂",
"You're irrelevant — even Google doesn't know you 🔍",
"You're a hero whose movie flopped in 3 minutes 🎬",
"Bhai tera swag Excel mein error hai — #NAME? 📊",
"Tu itna dheema hai ke kachhua bhi race jeet gaya 🐢",
"Teri thinking 2G speed pe chal rahi hai 📡",
"Beta tera ek message dekh ke aasman bhi sharma gaya ☁️",
"Bhai teri life ek loading screen hai — jo kabhi load nahi hoti ⏳",
"Ter maa ne tujhe chhoda nahi chhodni chahiye thi 😂",
"Beta tera existence proof hai ke koi bhi internet use kar sakta hai 📶",
"Bhai teri personality ek blank page hai — aur blank hi rahega 📄",
"Tu sirf chat mein hero hai real duniya mein zero 💻",
"Beta teri soch itni outdated hai ke floppy disk bhi reject kar de 💾"
]

ragebait_texts = [
"Bhai tera reaction dekh ke mujhe hasi aa rahi hai 😂",
"Tu itna triggered ho gaya, jaise meri baat teri maa ne sun li ho 😹",
"Rage bait pe itna emotional mat ho, beta 😂",
"Tu toh aisa gussa ho raha hai jaise teri team world cup haar gayi 🏏",
"Bhai shant ho ja, tera BP high ho jayega 😂",
"Teri gaali sun ke mujhe neend aa rahi hai 😴",
"Tu rage karta hai aur main popcorn kha raha hoon 🍿",
"Beta tu toh aisa hai jaise bina phone ke reh gaya ho 📱",
"Teri rage dekh ke lagta hai, teri gf ne break up kar diya 💔",
"Tu toh aisa hai jaise internet slow ho gaya ho 😂",
"Your rage is entertaining, please continue 😂",
"Getting triggered over this? That's cute 🥺",
"You're so angry, did someone steal your Wi-Fi? 📶",
"Rage bait level: professional 😂",
"Your anger is my daily dose of comedy 🤡",
"Calm down, it's just a message 📩",
"You're acting like I insulted your whole bloodline 😂",
"The rage is real, and it's hilarious 😭",
"You need a therapist for that anger issues 🧠",
"I love how easy it is to get you triggered 😈",
"Bhai tera reaction dekh ke mujhe hasi aa rahi hai 😂",
"Tu itna triggered ho gaya, jaise maine teri game delete kar di ho 🎮",
"Rage bait pe itna emotional mat ho, beta 😂",
"Tu toh aisa gussa ho raha hai jaise teri team haar gayi 🏏",
"Bhai shant ho ja, tera BP high ho jayega 😂",
"Teri gaali sun ke mujhe neend aa rahi hai 😴",
"Tu rage karta hai aur main popcorn kha raha hoon 🍿",
"Beta tu toh aisa hai jaise bina phone ke reh gaya ho 📱",
"Teri rage dekh ke lagta hai, teri gf ne break up kar diya 💔",
"Tu toh aisa hai jaise internet slow ho gaya ho 😂"
]

roast_texts = [
"Ter life ek bakwas webseries ki tarah hai — 1 season mein flop 😂",
"Bhai teri personality ek sada hua pyaz jaisi hai 🧅",
"Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟",
"Teri maa ne bhi socha hoga — yaar galti ho gayi 😹",
"Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂",
"Teri iq level calculator mein error aata hai 🧮",
"Tu chhata hua papad hai — touch karte hi toot gaya 😹",
"Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞",
"Teri personality dekh ke AI bhi depressed ho gaya 🤖",
"Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂",
"Your life is a joke, and not even a funny one 😂",
"You're so irrelevant, even your shadow leaves you 🏃",
"Ter life ek bakwas webseries ki tarah hai — 1 season mein flop 😂",
"Bhai teri personality ek sada hua pyaz jaisi hai 🧅",
"Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟",
"Teri maa ne bhi socha hoga — yaar galti ho gayi 😹",
"Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂",
"Teri iq level calculator mein error aata hai 🧮",
"Tu chhata hua papad hai — touch karte hi toot gaya 😹",
"Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞",
"Teri personality dekh ke AI bhi depressed ho gaya 🤖",
"Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂",
"Your life is a joke, and not even a funny one 😂",
"You're so irrelevant, even your shadow leaves you 🏃",
"Your existence is a notification I always swipe away 📱",
"You're like a software update — always annoying and never useful 💻",
"Your brain is like a browser with 100 tabs open — all useless 🌐",
"You're the human equivalent of a loading screen ⏳",
"Your personality is like a broken pencil — pointless ✏️",
"You're not stupid, you just have bad luck thinking 🤔",
"You're the reason God created jokes 😂",
"Your life is a meme, and not a good one 🗿",
"Bhai teri zindagi ek bakwas webseries jaisi hai 📺",
"Teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅",
"Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟",
"Teri maa ne bhi socha hoga — yaar galti ho gayi 😹",
"Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂",
"Teri iq level calculator mein error aata hai 🧮",
"Tu chhata hua papad hai — touch karte hi toot gaya 😹",
"Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞",
"Teri personality dekh ke AI bhi depressed ho gaya 🤖",
"Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂",
"🔥 Teri zindagi ek bakwas webseries ki tarah hai — 1 season mein flop 😂📺",
"🤣 Bhai teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅💀",
"😹 Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟😂",
"🔥 Teri maa ne bhi socha hoga — yaar galti ho gayi 😹👶",
"🤣 Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂💀",
"😹 Beta tu Google Maps pe search kare toh bhi worthless aayega 🗺️😈",
"🔥 Teri iq level negative hai — calculator mein error aata hai 🧮😂",
"🤣 Tu chhata hua papad hai — touch karte hi toot gaya 😹🔥",
"😹 Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞😂",
"🔥 Teri personality dekh ke AI bhi depressed ho gaya hoga 🤖😹",
"🤣 Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂💀",
"😹 Bhai teri soch utni hi purani hai jitna tera Nokia phone 📱😂",
"🔥 Tera existence mere life mein irrelevant hai — bilkul sarkari kaam jaisa 📋😹",
"🤣 Tu itna boring hai ke neend khud aa jaaye tujhe dekh ke 😴😂",
"😹 Teri profile pic dekh ke emoji wale bhi sue kar sakte hain 😱🔥",
"🔥 Bhai tu aisa player hai jo kabhi goal nahi kar sakta apni hi team ke khilaf 😂⚽",
"🤣 Teri advice sunna waisa hai jaise sade kele se rasta poochna 🍌😹",
"😹 Tu garib nahi hai — but tujhe dekh ke gareebi ko takleef hoti hai 💰😂",
"🔥 Teri kismat itni kharab hai ke lottery ticket bhi teri traf nahi dekhti 🎫😹",
"🤣 Bhai tera sense of humor graveyard se udhaara liya hai kya 🪦😂",
"😹 Tu itna irrelevant hai ke khud Google bhi nahi jaanta tera naam 🔍🔥",
"🔥 Teri body language bolta hai — main hara hua insaan hoon 😂💀",
"🤣 Tu ek hi baar funny tha — jab tune mujhe seriously liya 😹⚡",
"😹 Bhai teri achievements list mein sirf ek cheez hai — exist karna 😂🔥",
"🔥 Tujhe dekh ke lagta hai — nature ne mistake ki thi 🌿😹",
"🤣 Teri skills dekh ke Thanos bhi bola hoga — yeh toh automatically wipe ho jaayega 💀😂",
"😹 Beta tera future itna dark hai ke sunglasses pehenne ki zaroorat nahi 🕶️🔥",
"🔥 Teri batting dekh ke khud pitch ne sorry bola 🏏😂",
"🤣 Bhai tu aisa idea hai jo meeting mein sab ignore karte hain 📊😹",
"😹 Teri zubaan aur dimag mein kabhi meetup nahi hota 🧠💬😂",
"🔥 Tu aisa hero hai jiska movie 3 minutes mein flop ho gayi 🎬😹",
"🤣 Teri gaali sunne ke baad dushmano ne mafi maang li 😂⚔️",
"😹 Bhai tera swag level Excel mein error hai — #NAME? 📊🔥",
"🔥 Tu itna dheema hai ke kachhua bhi race jeet gaya 🐢😂",
"🤣 Teri thinking 2G speed pe chal rahi hai duniya 5G mein hai 📡😹",
"😹 Beta tera ek message dekh ke aasman bhi sharma gaya ☁️😂",
"🔥 Bhai teri life ek loading screen hai — jo kabhi load nahi hoti ⏳😹",
"🤣 Tu aisa mirror hai jo galat reflection dikhata hai 🪞😂",
"😹 Teri maa ne tujhe chhoda nahi chhodni chahiye thi 😂🔥",
"🔥 Beta tera existence proof hai ke koi bhi internet use kar sakta hai 📶😹",
"🤣 Tujhe dekh ke lagta hai — maa baap ne education mein invest nahi kiya 📚😂",
"😹 Teri personality ek blank page hai — aur blank hi rahega 📄🔥",
"🔥 Tu sirf chat mein hero hai real duniya mein zero 💻😂",
"🤣 Bhai teri jawab dene ki speed se tortoise bhi impress nahi 🐢😹",
"😹 Teri soch itni outdated hai ke floppy disk bhi reject kar de 💾😂",
"🔥 Tu aisa WiFi password hai jo koi yaad nahi rakhta 🔑😹",
"🤣 Beta teri awaaz sunne ke baad mujhe silence zyada priceless laga 🤫😂",
"😹 Bhai tera roast karna waisa hai jaise sadi hui vegetable ko season karna 🥦🔥",
"🔥 Teri social skills dekh ke chatbot bhi impress ho ga",
"Your existence is a notification I always swipe away 📱",
"You're like a software update — always annoying and never useful 💻",
"Your brain is like a browser with 100 tabs open — all useless 🌐",
"You're the human equivalent of a loading screen ⏳",
"Your personality is like a broken pencil — pointless ✏️",
"You're not stupid, you just have bad luck thinking 🤔",
"You're the reason God created jokes 😂",
"Your life is a meme, and not a good one 🗿",
"Bhai teri zindagi ek bakwas webseries jaisi hai 📺",
"Teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅",
"Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟",
"Teri maa ne bhi socha hoga — yaar galti ho gayi 😹",
"Tujhe dekh ke pata chalta hai — darr darr ke jeena kya hota hai 😂",
"Teri iq level calculator mein error aata hai 🧮",
"Tu chhata hua papad hai — touch karte hi toot gaya 😹",
"Bhai teri aukat itni hai ke mirror bhi muh fer leta hai 🪞",
"Teri personality dekh ke AI bhi depressed ho gaya 🤖",
"Tu aisa dost hai jo aaye na aaye — fark nahi padta 😂"
]

# ─── NON-ABUSIVE RAID TEXTS (Menu9) ────────────────────────────────────

attack_texts = [
"🗡️ Tera baap aaya hai sunta nahi kya 👑😈",
"⚡ Mere saamne aake dikhao himmat hai toh 😎💪",
"🔥 Attack mode on — teri khair nahi aaj 😡⚔️",
"💀 Tujhe itna marunga ke teri maa bhi nahi pehchanegi 😂🔥",
"💥 Beta ye territory meri hai nikal yahan se 🏴‍☠️⚡",
"🗡️ Aukaat hai toh saamne aa nahi toh chup baith 😈💀",
"⚡ Tu keyboard warrior hai asli mard nahi 😂👊",
"🔥 Teri maa ne bhi bola tera baap chahiye 😹💔",
"💥 Chal hat yahan se chota baccha 🤣👋",
"⚔️ Mujhe gaali de ke dekh kya hoga teri life mein 😈⚡",
"💀 Bhai seedha bol de surrender karega ya maar khayega 😎🔥",
"🗡️ Attack karta hoon toh block nahi hoga tera 😡⚔️",
"⚡ Yeh game mein nahi real life mein bhi kaatenge tujhe 💪😤",
"🔥 Tera confidence dekh ke hansi aati hai yaar 😂💥",
"💥 Andha hai ya dikhta nahi kaun boss hai yahan 👑⚔️",
"⚔️ Teri har gaali pe 10 gaaliyan waapis aayengi 😈🔥",
"💀 Beta peeth nahi dikhana mujhe — coward 🏃‍♂️😂",
"🗡️ Lad le ek baar — guarantee hai rota hoga tu 😹⚡",
"⚡ Keyboard tod ke aa toh baat karte hain 💥👊",
"🔥 Teri bhasha se pata chalta hai ghar mein parhe nahi 😂🤣",
"⚔️ Main yahan hoon — tu kahan chhupta hai aaja 😎💀",
"💀 Teri har move ka jawab taiyaar hai mere paas 🎯🔥",
"🗡️ Tu sirf darta hai asli attack nahi kar sakta 😂⚡",
"⚡ Baahubali nahi hai tu yahan — chal nikal 👋💥",
"🔥 Teri aukaat utni hai jitni do takke ki 😹🗡️",
"💥 Attack aur reaction — dono mein haar jayega tu ⚔️😎",
"⚔️ Ek baar aake dekh kya hota hai tere saath 💀🔥",
"💀 Sher ke saamne bakra nahi ban — phir bhi ban raha 😂⚡",
"🗡️ Yeh teri territory nahi bhai — haath jod ke ja 🙏😈",
"⚡ Tu attack karega aur main finish karunga 💥⚔️",
"🔥 Teri himmat hai toh mujhse seedha baat kar 😤💀",
"💥 Keyboard pe hero ban raha hai — asli duniya mein zero 😂🗡️",
"⚔️ Maar kha aur phir rota mat — warning hai 😈⚡",
"💀 Teri speed se faster hoon main — bhaag nahi sakta 🔥💥",
"🗡️ Yaar teri life mein koi nahi kya isliye yahan ata hai 😂⚔️",
"⚡ Hero mat ban — yahan real khiladi baithe hain 👑💀",
"🔥 Attack kiya — ab lash uthane ki taiyaari kar 😹⚡",
"⚔️ Teri har galti ka hisaab hoga — ruk 😈🔥",
"💀 Bhai attack se pehle 1% dimag use kar 🧠💥",
"🗡️ Chal hat nahi toh main khud hataunga isko 😤⚡",
"⚡ Yeh war hai — aur tu already haar gaya 😎🔥",
"🔥 Teri maa bhi tera lecture sunke bore ho gayi hogi 😹💥",
"💥 Main attack mein vishwas nahi karta — main finish mein karta hoon ⚔️😈",
"⚔️ Chal randike ek baar try kar le — rona mat baad mein 😂💀",
"💀 Ab samjha kya hua? No? Toh phir ek aur attack 🔥⚡",
]

war_texts = [
"⚔️ War shuru ho gayi — aur tu pehle hi haar gaya 😂🔥",
"💣 Bhai main war mein nahi aata — main war khatam karne aata hoon 😈⚡",
"🏴‍☠️ Tera jhanda uraya — apna wala lehraya 😎💀",
"⚔️ Tu lad raha hai mujhse — yeh teri sabse badi galti hai 🔥😂",
"💣 Main war nahi khelta — main result deliver karta hoon 👑⚡",
"🏴‍☠️ Battlefield pe aake to dekh — tera rank kya hai 😈⚔️",
"⚔️ Randike war declare kiya toh surrender ka option bhi rakh 😂💣",
"💣 Tu soldier nahi hai — tu sirf noise hai 🔊😂",
"🏴‍☠️ War mein strategy chahiye — tu sirf emotion se ladta hai 😹⚔️",
"⚔️ Beta yeh teri territory nahi — nikalja 👋💣",
"💣 Tera war cry sunke mujhe neend aati hai 😴😂",
"🏴‍☠️ Main akela kaafi hoon — teri poori army ke liye ⚔️😈",
"⚔️ War ghoshit kiya — white flag kahan hai tera 🏳️😂",
"💣 Bhai tu pehle khud ko toh jeet — phir mujhse lad 😎💀",
"🏴‍☠️ Tera war tactic: bolna aur bhaagna 😹⚔️",
"⚔️ Main chhoda nahi — tu chhoda baad mein roega 😂💣",
"💣 Battle field pe aate waqt socha — main jeet sakta hoon? Nahi 😈🏴‍☠️",
"⚔️ Tu ek round bhi nahi jeeta — aur war ki baat karta hai 😂💀",
"💣 Bhai surrender kar le — dignity bachegi thodi 🙏😹",
"🏴‍☠️ War mein aaye — aur pehli line mein fail ho gaye ⚔️😂",
"⚔️ Tera morale zero hai — teri army teri khud ki dushman hai 😂💣",
"💣 Main war expert hoon — tu war ka victim hai 😎🏴‍☠️",
"🏴‍☠️ Beta teri strategy ek broken compass jaisi hai ⚔️😂",
"⚔️ War mein seena taan ke aa — peeth dikha ke nahi 😹💣",
"💣 Bhai teri army mein sirf tu hai — aur tu kaafi nahi 😈🏴‍☠️",
"🏴‍☠️ Teri war cry sun ke dushman khud aa gaye — rescue karne ⚔️😂",
"⚔️ Beta teri territory war se pehle hi haari thi 💣😹",
"💣 Main war mein nahi — main tujhe personally destroy karne mein hoon 😈🏴‍☠️",
"🏴‍☠️ Tera war plan sunke GPS bhi confused hai ⚔️😂",
"⚔️ Tu war mein aaya — par weapons lana bhool gaya 💣😹",
"💣 Bhai yeh war nahi tujhe sirf reality check tha 😂🏴‍☠️",
"🏴‍☠️ Teri army tujhse zyada samajhdaar hai — unhone bandh kiya ⚔️😈",
"⚔️ War mein bhi excuse karta hai — aur life mein bhi 😂💣",
"💣 Tu jo war soch raha hai — woh meri morning routine hai 😎🏴‍☠️",
"🏴‍☠️ Bhai teri war itni slow hai ke climate change pehle ho jaayega ⚔️😹",
"⚔️ Main tujhse war karta hoon — aur tujhe pata bhi nahi chalta 💣😂",
"💣 War ghoshit kar ke tu pehla tha — haar ke bhi pehla hai 😹🏴‍☠️",
"🏴‍☠️ Teri war mein consistency hai — consistently losing ⚔️😂",
"⚔️ Bhai war mein bhagna galat hai — tu phir bhi karta hai 💣😈",
"💣 Tu war mein aaya — main pehle se tere base par tha 🏴‍☠️😂",
"🏴‍☠️ Teri war strategy mein sirf ek problem hai — sab kuch ⚔️😹",
"⚔️ Beta war ka matalab samjha nahi tujhe — sikhaunga abhi 💣😂",
"💣 War mein hero nahi bante — survivors bante hain — aur tu nahi banega 🏴‍☠️😈",
"🏴‍☠️ Teri war mein dum nahi — sirf dhool hai ⚔️😂",
"⚔️ Bhai war declare karna alag baat hai — jeetan alag 💣😹",
"💣 Tu war mein aaya sirf lose karne ke liye — congratulations 🏴‍☠️😂",
"🏴‍☠️ Main akele teri sab pe bhaari hoon — aur tujhe pata hai ⚔️😈",
"⚔️ Teri war ka sabse bura part — tu khud tha 💣😂",
"💣 War mein aaye — teri team ne hi tujhe chhod diya 🏴‍☠️😹",
"🏴‍☠️ Beta war khatam — teri taraf se surrender accepted ⚔️😎",
]

savage_texts = [
"😈 Confidence is silent, insecurity is loud! 🔥",
"💀 You're not as important as you think! 🌪️",
"🔥 Reality check — you're not that special! 💥",
"😏 Your opinion is noted, but not needed! 📝",
"💀 Let's be honest — you're overrated! 🎭",
"🔥 The truth hurts, but it sets you free! 💪",
"😈 You're not the main character, sorry! 📺",
"💀 Your ego is writing checks your skills can't cash! 💰",
"🔥 Stay humble or get humbled! ⚡",
"😏 You're a classic example of overconfidence! 🎯",
"💀 Let your actions speak, not your mouth! 🔥",
"😈 Your presence is as useful as a screen door on a submarine! 🚪",
"🔥 Let's be real — you're not that impressive! 💥",
"💀 You're the CEO of overestimating yourself! 🏢",
"😏 Stay in your lane, champ! 🏎️",
"🔥 You're not as hot as you think! ❄️",
"💀 Confidence without skill is just delusion! 🎭",
"😈 Your reputation precedes you — and it's not good! 📉",
"🔥 Let's keep it real — you're average at best! ⭐",
"💀 You're a cautionary tale for others! ⚠️",
"😈 Main savage hoon — tujhe explanation nahi deta 🔥💀",
"💀 Teri feelings mere liye statistics hain — irrelevant 😂😈",
"🔥 Main woh nahi hoon jo tujhe comfortable feel karaaye 😎💀",
"😈 Beta teri baatein mujhe bore karti hain — next 😂🔥",
"💀 Teri opinion meri life mein footnote bhi nahi hai 😈😹",
"🔥 Main tujhe explain nahi karta — tujhse better logon ke paas time deta hoon 😎💀",
"😈 Tera attitude dekh ke mujhe apni nails file karni chahiye 💅😂",
"💀 Bhai tujhe reject karna meri hobby hai 🔥😈",
"🔥 Teri presence mujhe remind karaati hai — kuch logon ko mute karna chahiye 🔇😂",
"😈 Main bad vibes nahi leta — teri taraf bhi nahi 💀🔥",
"💀 Tu mere standard se neeche hai — elevator laga le 🛗😂",
"🔥 Teri baat sunna — option nahi habit nahi aur interest bhi nahi 😈💀",
"😈 Main ghanta samjhata hoon — samajh nahi aaya toh teri problem 😂🔥",
"💀 Teri ego itni badi hai — uske liye alag zip code chahiye 📮😂",
"🔥 Beta mujhe tujhse jealousy feel nahi hoti — pity hoti hai 😈💀",
"😈 Main woh insaan nahi hoon jis par tu waqt barbad kare — ya main karta hoon 😂🔥",
"💀 Teri life choices dekh ke main grateful hoon main tujhsa nahi hoon 😹😈",
"🔥 Bhai teri smartness ka level: WiFi password ignore karna 📶😂",
"😈 Teri mastiyan mujhe entertain nahi karti — bore karti hain 💀🔥",
"💀 Main savage nahi — main simply tujhse better hoon 😎😂",
"🔥 Teri personality ek blank meme format jaisi hai — kuch nahi 😈💀",
"😈 Beta apni journey pe focus kar — meri disturb mat kar 😂🔥",
"💀 Teri hard work ka result tera hi face hai — kaafi bura 😹😈",
"🔥 Main tujhe miss nahi karta — mujhe tujhse better cheezein miss hoti hain 😂💀",
"😈 Teri baatein sun ke laga — yeh real person hai ya chatbot glitch 🤖😂",
"💀 Bhai teri intelligence ke liye sorry feel hoti hai 🔥😈",
"🔥 Main tujhe block isliye nahi karta — kyunki tujhe exist karna pata hai 😂💀",
"😈 Teri struggles dekh ke mujhe motivation milti hai — teri tarah mat banna 😹🔥",
"💀 Tu jo effort lagate ho mujhpe — woh apni growth mein lagao 😎😂",
"🔥 Teri vibes mujhe 2G network se bhi slow lagti hain 📡😈",
"😈 Main tujhe pehle judge nahi karta — par tujhe pehle judge hota hoon 💀😂",
"💀 Bhai tera shadow bhi tujhse zyada interesting hai 🔥😂",
"🔥 Teri logic sun ke Albert Einstein ne resign kar diya hoga 🧪😈",
"😈 Tu mere jaisa ban sakta hai — agar try karta 10 saal toh bhi nahi 💀😂",
"💀 Teri taraf se koi bhi reaction — mujhe bored karta hai 🔥😹",
"🔥 Main respectful hoon — tere sath nahi 😈💀",
"😈 Beta teri vibe check: FAILED 😂🔥",
"💀 Teri har move predicted thi — boring player 😹😈",
"🔥 Main tujhe second chance nahi deta — teri pehli impression kafi thi 😂💀",
"😈 Teri friendship ke offer ko professionally decline karta hoon 😎😂",
"💀 Beta tu mujhe feel nahi karaata — tu sirf annoy karta hai 🔥😈",
"🔥 Teri dimagi capacity dekh ke solar calculator bhi sorry bol de 🔋😂",
"😈 Main uun logon mein nahi hoon jo tere liye time waste karein 💀🔥",
"💀 Teri life ka GPS tujhe wrong direction mein le ja raha hai 🗺️😂",
"🔥 Bhai teri alag identity bana — copier mat ban 😈💀",
"😈 Tu mere radar par bhi nahi aata — itna irrelevant hai 😂🔥",
"💀 Teri maa ne bhi socha hoga — yaar isko kuch aur karna chahiye tha 😹😈",
"🔥 Main woh hoon jo teri nightmares mein aata hai — as a reminder 😎💀",
"😈 Beta teri bakaiti mujhe filter nahi karti — automatically skip ho jaati hai 😂🔥",
"💀 Tu savage hone ki koshish karta hai — mujhe dekh savage ka example 😈😹",
]

ultra_texts = [
"🔥 ULTRA mode activated — time to dominate! 👑",
"🌪️ ULTRA MODE ACTIVATED — teri poori existence question mein hai 😈🔥",
"⚡ Ultra attack — pehle gaali sunna phir rona — sequence yaad kar 😂💀",
"🌪️ Beta ultra level pe aake dekh — yahan teri category nahi hai 👑🔥",
"⚡ ULTRA BLOW — teri soch se lekar attitude tak sab destroy 💥😈",
"🌪️ Yeh ultra mode hai — blocking nahi help karega 😂⚡",
"⚡ Ultra raid engaged — ab teri poori chat history history hai 📜😹",
"🌪️ Beta ultra speed mein aa — par seedha home le jaata hoon 💀🔥",
"⚡ Ultra fire — teri har defensive move kaam nahi karegi 😈🌪️",
"🌪️ Yeh ultra level fight hai — tu still bronze mein hai 😂⚡",
"⚡ ULTRA DAMAGE — teri reputation, teri aukaat, teri everything 💥😹",
"🌪️ Ultra mode mein poori teri army bhi kaafi nahi 😈🔥",
"⚡ Beta ultra attack sunne ke baad sun raha hai kya? Normal hai 😂🌪️",
"🌪️ ULTRA RANT incoming — tune jo kiya uska hisaab hoga 💀⚡",
"⚡ Yeh ultra version hai — tujhe pata bhi nahi kya aaya 😹🔥",
"🌪️ Ultra mode ON — timer chal raha hai teri destruction ka 😈⚡",
"⚡ Beta ultra strike pe tujhe sirf ek option hai — disappear 😂💀",
"🌪️ ULTRA COMBO — reply + react + roast + raid all at once 🔥⚡",
"⚡ Yeh ultra level rage hai — aur tujhe taste hoga 😈🌪️",
"🌪️ Ultra activated — pehle bol sorry phir ja 😹😂",
"⚡ Beta ULTRA message ka matlab — tu mere liye mission ban gaya 💀🔥",
"🌪️ ULTRA STORM — har cheez destroy ho rahi hai teri side pe 😈⚡",
"⚡ Yeh ultra nahi — tujhe sirf samjhane ki koshish thi 😂🌪️",
"🌪️ Ultra mode finish — teri team ne tera saath chhoda 💀🔥",
"⚡ Beta ULTRA = mera minimum effort on you 😈😂",
"🌪️ ULTRA RAIN — tune invite kiya tha — enjoy karna tha na? 😹⚡",
"⚡ Ultra mode mein ek hi rule — no mercy 💀🔥",
"🌪️ Beta ULTRA sabse pehle yeh — teri galti ka hisaab 😈⚡",
"⚡ Yeh ultra speed se aaya — aur teri samajh mein ultra slow aayega 😹🌪️",
"🌪️ ULTRA LOCK — ab yahan se nahi jayega tu 💀🔥",
"⚡ Beta ultra strike mein teri saari strategy fail hai 😂😈",
"🌪️ Ultra level pe chal — toh teri duniya hi badal jaayegi 🔥⚡",
"⚡ ULTRA — yeh word hi teri aukat se bada hai 😹💀",
"🌪️ Beta ultra mein main hoon — tujhe pata nahi tha kya 😈🔥",
"⚡ Yeh ultra raid hai — har message teri ek problem hai 😂🌪️",
"🌪️ ULTRA DONE — tu done kar le pehle 💀⚡",
"⚡ Beta ultra mein welcome — pehle bol kya karna hai 😹🔥",
"🌪️ Ultra mode — ab seedha point pe aata hoon — tu fail hai 😂😈",
"⚡ ULTRA BLAST — teri timeline pe aaya — nahi ruk sakta 💥🌪️",
"🌪️ Beta ultra mein aake teri baat karo — nahi aata toh seedha ja 💀🔥",
"⚡ Yeh ultra war hai — aur teri taraf se koi nahi 😂😈",
"🌪️ ULTRA FINAL — bas yahi hoga — accept kar 💀⚡",
"⚡ Beta ultra strike complete — check teri status 😹🔥",
"🌪️ Ultra mode mein log surrender karte hain — tujhe bhi karna hoga 😈⚡",
"⚡ Yeh ultra punishment nahi — tutorial hai teri life ka 😂💀",
"🌪️ ULTRA JUDGEMENT — teri har move judged ho rahi hai 🔥⚡",
"⚡ Beta ultra mein ek cheez — main hoon aur tu nahi rahe 😈🌪️",
"🌪️ Ultra mode completed — teri side destroyed 💀😂",
"⚡ Yeh ultra attack ka last wave hai — teri koi repair nahi 😹🔥",
"🌪️ ULTRA END — teri war khatam teri taraf se flag gira 😈⚡",
"⚡ Beta ultra mein aana tha — rona nahi tha — par dono kiye 😂💀",
]

# ─── NEW MENU9 RAID TEXTS ───────────────────────────────────────────────

shame_texts = [
"😤 Sharam kar — itna gira hua kaam karte kaise hain tum log 🔥💀",
"🙅 Bhai teri harkat dekh ke pura group sharam se doob gaya 😂😤",
"😤 Yeh sab karke tujhe pride feel hoti hai? Really? 💀🔥",
"🙅 Beta teri harkaten dekh ke maa baap sharmayenge 😂😤",
"😤 Sharam nahi hai tujhe bilkul — clearly 💀😹",
"🙅 Bhai itna gira hua kaam dekh ke log muh fer lete hain 😤🔥",
"😤 Tu itna neeche gira — zameen bhi neeche ho gayi 💀😂",
"🙅 Beta sharam bhi nahi aata aisa karte hue 😤😹",
"😤 Yeh harkat dekh ke lagta hai — tujhe value kisi ne nahi sikhaya 💀🔥",
"🙅 Bhai log tujhe dekh ke aankhein pher lete hain — soch kya kar raha hai 😤😂",
"😤 Teri galti nahi — environment ki galti — par ab waqt hai change ka 💀😹",
"🙅 Beta sharam isliye nahi aati kyunki sharam feel karna seekha nahi 😤🔥",
"😤 Yeh kaam karke tujhe khushi mili? Toh mujhe tujhse zyada chinta hai 💀😂",
"🙅 Bhai teri harkat pura record hai — aur yeh record kharab hai 😤😹",
"😤 Tu sochta hai koi dekh nahi raha — sab dekh rahe hain 💀🔥",
"🙅 Beta aisa behave karta hai — khud se bhi embarrassing lagta hai tu 😤😂",
"😤 Yeh sab dekh ke lagta hai — teri parwarish kahan gayi 💀😹",
"🙅 Bhai teri harkaton ka hisaab hoga — aaj nahi toh kal 😤🔥",
"😤 Tu sharminda nahi hai — woh most shameful cheez hai 💀😂",
"🙅 Beta logo ne tujhe judge kiya — kyunki tune judge hone wala kaam kiya 😤😹",
"😤 Yeh bura kaam karke tujhe kya mila — kuch nahi — bas naam barbad 💀🔥",
"🙅 Bhai sharam karo — itna toh haq hai tumhara 😤😂",
"😤 Tu yahan cool lagne ki koshish mein sharminda ho gaya 💀😹",
"🙅 Beta ghalat rasta chhod — vapas aa 😤🔥",
"😤 Yeh sab karke teri image bani hai — worst category mein 💀😂",
"🙅 Bhai teri harkat ka review — 0 stars — do not recommend 😤😹",
"😤 Tu itna neeche gira — recovery mushkil lagti hai 💀🔥",
"🙅 Beta tujhe samjhana waqt waste hai — par try kar raha hoon 😤😂",
"😤 Yeh sab dekh ke mujhe tujhse zyada tujhpe gussa nahi — hairaani hai 💀😹",
"🙅 Bhai sharam se doob — par us mein bhi tujhe help chahiye shayad 😤🔥",
"😤 Teri harkat ek lesson hai — dusron ke liye kya nahi karna chahiye 💀😂",
"🙅 Beta teri yeh sab dekh ke khud bhi tujhse door rehna chahta hoon 😤😹",
"😤 Yeh gaaliyaan nahi — sirf reality check hai 💀🔥",
"🙅 Bhai sharam tab aati hai jab insaan mein insaniyat hoti hai 😤😂",
"😤 Tu ek example bana diya khud ko — negative example 💀😹",
"🙅 Beta tujhe ek baar ruk ke soochna chahiye tha — nahi soocha 😤🔥",
"😤 Yeh sab karke tu yahan hai — aur sochta hai main galat hoon? 💀😂",
"🙅 Bhai itna toh bata — tujhe kaisa feel hota hai yeh sab karne ke baad 😤😹",
"😤 Tu sharminda nahi — tujhe sharminda feel karna chahiye 💀🔥",
"🙅 Beta yeh rasta galat hai — abhi bhi change ho sakta hai 😤😂",
"😤 Yeh sab khud se bura nahi tha — tu tha 💀😹",
"🙅 Bhai teri harkaton ka real world impact sun — sab tujhse dur hain 😤🔥",
"😤 Tu soch raha hai main overreact kar raha hoon — par tujhe hisaab hoga 💀😂",
"🙅 Beta tujhe pata hai tu kya kar raha hai — aur phir bhi kar raha hai 😤😹",
"😤 Yeh sharm ki baat hai — aur tujhe realize karna chahiye 💀🔥",
"🙅 Bhai tujhe mirror mein dekhna chahiye — ek baar 😤😂",
"😤 Tu itna bura nahi hai — par yeh kaam bura tha 💀😹",
"🙅 Beta sharam isliye nahi aati — kyunki tu sochta nahi consequences ke baare mein 😤🔥",
"😤 Yeh moment tera lowest point hai — aur abhi bhi jaag sakta hai 💀😂",
"🙅 Bhai aaj ek kaam kar — sharminda ho aur badal — bas itna chahiye 😤😎",
]

diss_texts = [
"🎤 Tera naam sun ke log mute kar dete hain khud ko 🔇😂",
"💀 Tu diss kar raha hai — khud ko diss kar pehle 🪞😹",
"🎙️ Teri rap jaisi hai — no flow no bars no future 🎵😂",
"💥 Bhai tera verse sun ke Eminem ne retire le liya 😹🎤",
"🔥 Teri diss itni kamzor hai ke whisper bhi zyada loud hai 🤫😂",
"💀 Tu sirf bolne mein mard hai karne mein? Zero 😈🎙️",
"🎤 Beta teri bars mein bar hi nahi — sirf khali string 🎸😂",
"💥 Tera diss track sunne ke baad logon ne earbuds tod diye 🎧😹",
"🔥 Bhai teri lyric likh ke dekha — autocorrect ne bhi reject kiya ✍️😂",
"💀 Tu diss karta hai aur log diss ko diss karte hain 😂🎤",
"🎙️ Teri voice aisi hai ke autotune bhi nahi bach sakta 🎶😹",
"💥 Beta freestyle kar le — ya phir stop the embarrassment 🛑😂",
"🔥 Tujhe sun ke DJ ne plug nikal diya 🔌😹",
"💀 Bhai tera flow aisa hai jaise jaam mein traffic — ruka hua 🚗😂",
"🎤 Teri soch itni slow hai ke beat ke saath nahi chalti 🥁😹",
"💥 Tera diss mujhe sula raha hai — better than sleeping pills 😴😂",
"🔥 Bhai asli diss toh tab hogi jab tu actually kuch achieve kare 🏆😹",
"💀 Teri lyrics Google Translate se better hain — bas 🌐😂",
"🎙️ Beta chal hat stage se — pehle walk-on music bana 🎵😹",
"💥 Tera punchline itna weak hai ke paper bhi survive kar le 📄😂",
"🔥 Bhai teri diss sun ke crowd ne baat karna shuru kar diya 🙄😹",
"💀 Tu verse likhta hai ya grocery list — same energy 🛒😂",
"🎤 Teri bars mein calories zyada hain — totally empty 😹🔥",
"💥 Bhai teri rhyme sunke chhote bacche bhi sharma jaate hain 😂💀",
"🔥 Teri diss aisi hai — sirf uski maa samjhi 😹🎙️",
"💀 Tu diss karta hai mujhe — main khud apni diss sunta hoon for fun 😂💥",
"🎤 Tera stage naam kya hai — Bakwas ke Raja? 👑😹",
"💥 Bhai teri microphone bhi teri awaaz se dara hua hai 🎙️😂",
"🔥 Tu diss mein expert hai — aur expert hone mein loser 😹💀",
"💀 Teri har line mein cringe hai — Olympic level 🥇😂",
"🎙️ Beta khud ki diss sun le — ek baar realise hoga 😹🔥",
"💥 Bhai tera diss itna slow hai ke mujhe neend aa gayi 😴😂",
"🔥 Teri creativity level: template pe naam likhna 💀😹",
"💀 Tu diss karne ke liye paida hua tha — aur fail ho gaya 😂🎤",
"🎙️ Tera rhyme scheme: aab aab aab — boring AF 📝😹",
"💥 Bhai teri diss response mein Soulja Boy beat use karta hun 😂🔥",
"🔥 Tu keyboard pe rap karta hai — phone pe nahi kaata 📱💀",
"💀 Teri diss sun ke mic khud neeche gir gaya 🎙️😂",
"🎤 Beta teri bars itni weak hain ke paper toh chodh kaagaz bhi nahi chhapega 📰😹",
"💥 Bhai tera flow paani mein nahi petrol mein hai — ab blast 🔥😂",
"🔥 Teri diss sunta hoon toh lagta hai sabne kaan band kar rakhe hain 🔇💀",
"💀 Tu diss mein ghusaa — tu diss tha diss 😹😂",
"🎙️ Bhai tera verse industry standard se neeche hai — ground floor bhi nahi 🏚️🔥",
"💥 Teri awaaz mein woh baat nahi jo diss mein chahiye — talent 😂💀",
"🔥 Beta teri diss itni pathetic hai ke pity vote mil sakta tha 🗳️😹",
"💀 Bhai teri rap career ek Instagram story jaisi hai — 24 ghante mein khatam 📸😂",
"🎤 Tu rapper nahi rapper ki copy ki copy ka knock-off hai 😹🔥",
"💥 Teri diss sun ke auto-generated ho sakti thi — aur better hoti 🤖😂",
"🔥 Bhai freestyle maar — aur phir sun khud ko — tujhe pata chalega 🎧💀",
"💀 Teri diss ka reply nahi deta — tujhe dignify karna time waste hai 😂🎙️",
]

devil_texts = [
"😈 DEVIL MODE — yahan woh aaya hai jo tujhe deserve karta hai 🔥💀",
"😈 Beta main devil nahi — main tera worst nightmare hoon 🔥⚡",
"😈 Devil raid activate — teri poori timeline disturbed 💀😂",
"😈 Bhai devil pe hath lagaya — ab bhog 🔥💥",
"😈 DEVIL FURY — teri sab cheez ek baar mein 💀⚡",
"😈 Beta devil ke saamne hum sab khiladi hain — tu beginner 🔥😂",
"😈 DEVIL ATTACK — teri defense devil ke touch se fail 💀😈",
"😈 Bhai devil mode mein koi safe nahi — tu bhi nahi 🔥⚡",
"😈 Teri galti — devil ko challenge karna 💀😂",
"😈 Beta devil ki bhasha — punishment aur reward — tu punishment mein hai 🔥😈",
"😈 DEVIL LEVEL RAGE — teri poori life on line 💀⚡",
"😈 Bhai devil se lad ke koi nahi jeeta — tu bhi nahi jeetega 🔥😂",
"😈 Devil mode — tera sab kuch noted — sab 💀😈",
"😈 Beta DEVIL FIRE — teri poori duniya burn 🔥⚡",
"😈 DEVIL RAID COMPLETE — tujhe koi nahi bachayega 💀😂",
"😈 Bhai devil teri har move pe already plan bana chuka 🔥😈",
"😈 Devil mode — tera future bleak — teri choice thi 💀⚡",
"😈 Beta devil ne tujhe select kiya — koi bada reason hoga 🔥😂",
"😈 DEVIL STORM — teri poori squad disbanded 💀😈",
"😈 Bhai devil ke game mein tera turn tha — abhi mera 🔥⚡",
"😈 Devil raid engage — now teri responsibility 💀😂",
"😈 Beta devil level punishment — tujhse tune karaya tha 🔥😈",
"😈 DEVIL ZONE — nikal ja nahi toh devil ka guest ban 💀⚡",
"😈 Bhai devil hamesha sunta hai — teri bhi sun li 🔥😂",
"😈 Devil mode ACTIVATED — teri poori timeline hijacked 💀😈",
"😈 Beta devil ke saamne sirf ek option — respect ya suffer 🔥⚡",
"😈 DEVIL FINAL BLOW — teri defense completely gone 💀😂",
"😈 Bhai devil ne decide kiya — teri loss is inevitable 🔥😈",
"😈 Devil mein aake dekha — tu deserving nahi tha challenge ka 💀⚡",
"😈 Beta DEVIL RAIN — teri har cheez soaked in fire 🔥😂",
"😈 DEVIL vs YOU — spoiler: devil wins 💀😈",
"😈 Bhai devil ke saamne teri prayers bhi kaam nahi aate 🔥⚡",
"😈 Devil mode — teri weak spots identified — attack 💀😂",
"😈 Beta devil ki nazar se tu nahi chhupta 🔥😈",
"😈 DEVIL JUDGMENT — teri poori history reviewed — verdict: guilty 💀⚡",
"😈 Bhai devil ki duniya mein tu tourist tha — time up 🔥😂",
"😈 Devil fury — tere steps already tracked hain 💀😈",
"😈 Beta DEVIL COUNTER — teri har move ka counter ready tha 🔥⚡",
"😈 DEVIL FINISH — teri game over — my game continues 💀😂",
"😈 Bhai devil mode se nikalna — tujhe option nahi 🔥😈",
"😈 Devil attack — teri soul targeted — figuratively 💀⚡",
"😈 Beta devil ne kaha — teri aukat nahi — aur devil galat nahi hota 🔥😂",
"😈 DEVIL STORM OVER — teri side: scorched earth 💀😈",
"😈 Bhai devil ke rules simple hain — tu follow nahi kiya 🔥⚡",
"😈 Devil raid — teri position compromised — retreat 💀😂",
"😈 Beta DEVIL mein aake rota mat — khud aaya tha 🔥😈",
"😈 DEVIL WAVE — teri har defence erased 💀⚡",
"😈 Bhai devil ka favorite — log jo khud ko smart samjhte hain — tu 🔥😂",
"😈 Devil mode DONE — check teri condition 💀😈",
"😈 Beta devil ne aaj tujhe yaadgaar bana diya — wrong reasons se 🔥⚡",
]

karma_texts = [
"☯️ Karma aaya — teri sab harkat ka hisaab ho raha hai 🔥💀",
"☯️ Beta karma kisi ki nahi sunta — teri bhi nahi 😂⚡",
"☯️ KARMA STRIKE — tune jo kiya woh teri taraf wapas aaya 🔥😈",
"☯️ Bhai karma judge nahi karta — deliver karta hai 💀😂",
"☯️ Karma mode activate — teri sab galtiyan wapas aa rahi hain 🔥⚡",
"☯️ Beta karma tujhe bhool nahi gaya — yaad rakha tha 😂💀",
"☯️ KARMA DELIVERY — teri harkat ka package arrive ho gaya 🔥😈",
"☯️ Bhai karma se koi nahi bachta — tu bhi nahi bachega 💀⚡",
"☯️ Karma tujhe dhundh raha tha — dhundh liya 🔥😂",
"☯️ Beta karma aata hai jab expect nahi karte — sun le 😂💀",
"☯️ KARMA HITS DIFFERENT — teri sab cheez wapas 🔥⚡",
"☯️ Bhai karma teri priority nahi thi — karma mein tu priority hai 😂💀",
"☯️ Karma cycle complete — tune jo kiya tune hi bhoga 🔥😈",
"☯️ Beta karma slow hota hai par sure hota hai — yeh sure tha 💀⚡",
"☯️ KARMA CALL — teri line pe aa gaya 🔥😂",
"☯️ Bhai karma mein koi error nahi — teri galti recorded thi 😂💀",
"☯️ Karma teri taraf waapis — enjoy 🔥⚡",
"☯️ Beta karma tera address jaanta tha 😂💀",
"☯️ KARMA FINAL — teri poori account balance zero 🔥😈",
"☯️ Bhai karma se lad nahi sakte — tu chhupa nahi karma se 💀⚡",
"☯️ Karma strike — tune deserve kiya — mila 🔥😂",
"☯️ Beta karma ko excuse nahi deta — sirf result deta hai 😂💀",
"☯️ KARMA STORM — teri sab beizzati aaj ekatha aayi 🔥⚡",
"☯️ Bhai karma tujhse behtar account maintain karta hai 😂💀",
"☯️ Karma mein tera account — overdraft mein hai 🔥😈",
"☯️ Beta karma ki speed teri speed se faster hai 💀⚡",
"☯️ KARMA BLAST — teri sab cheezon ka hisaab 🔥😂",
"☯️ Bhai karma ko pata tha tune kya kiya — sab record mein hai 😂💀",
"☯️ Karma kisi pe bhi nahi rulta — teri bhi nahi 🔥⚡",
"☯️ Beta karma tera future nahi — karma tera present hai 😂💀",
"☯️ KARMA INVOICE — teri sab galtiyon ka bill aa gaya 🔥😈",
"☯️ Bhai karma mein koi discount nahi milta — full price pay 💀⚡",
"☯️ Karma delivered — tune jo bheja wahi mila 🔥😂",
"☯️ Beta karma tujhse kisi ki nahi sunta — seedha deliver karta hai 😂💀",
"☯️ KARMA FULL CIRCLE — teri sab harkat ghumke teri hi taraf aayi 🔥⚡",
"☯️ Bhai karma teri taraf — aur tu prepared nahi tha 😂💀",
"☯️ Karma hit kiya — tujhe pata tha aayega — aaya 🔥😈",
"☯️ Beta karma mein interest bhi hota hai — tera compound ho gaya 💀⚡",
"☯️ KARMA COMPLETE — lesson mila? 🔥😂",
"☯️ Bhai karma ne tujhe select kiya — deservingly 😂💀",
"☯️ Karma tujhe yaad dila raha hai — tune kya kiya tha 🔥⚡",
"☯️ Beta karma ki awaaz nahi hoti — par result loud hota hai 😂💀",
"☯️ KARMA RESPONSE — teri har cheez ka seedha jawab 🔥😈",
"☯️ Bhai karma ki list mein tu first position pe tha 💀⚡",
"☯️ Karma tujhe bhool nahi gaya — teri galti note thi 🔥😂",
"☯️ Beta karma aur tu — aaj inka meetup schedule tha 😂💀",
"☯️ KARMA WRAP UP — teri life lesson: yeh tha 🔥⚡",
"☯️ Bhai karma ne apna kaam kiya — efficient tha 😂💀",
"☯️ Karma strike final — teri sab cheez balanced ho gayi — zero pe 🔥😈",
"☯️ Beta karma yaad rakhna — abhi bhi teri account open hai ☯️😂",
]

doom_texts = [
"💀 DOOM activated — teri poori existence on countdown 🔥😈",
"💀 Beta doom aaya — tera timer start ho gaya 😂⚡",
"💀 DOOM STRIKE — teri poori defense wiped 🔥😈",
"💀 Bhai doom se koi nahi bachta — teri bhi date aane wali thi 😂💀",
"💀 Doom mode — teri sab cheez: scheduled for deletion 🔥⚡",
"💀 Beta doom tera waqt dekh ke aaya — perfect timing 😂😈",
"💀 DOOM RAID — teri poori squad: doomed 🔥💀",
"💀 Bhai doom pe haath lagaya — yeh result expect karna chahiye tha 😂⚡",
"💀 Doom finale — teri poori story: ended 🔥😈",
"💀 Beta doom ki awaaz sunna nahi chahte log — teri aa gayi 😂💀",
"💀 DOOM COMPLETE — teri sab cheez: finished 🔥⚡",
"💀 Bhai doom tujhse pehle plan kar ke aaya tha 😂😈",
"💀 Doom level CRITICAL — teri situation: hopeless 🔥💀",
"💀 Beta doom ne tujhe select kiya — teri achievement nahi 😂⚡",
"💀 DOOM COUNTDOWN — teri sab cheez: 3... 2... 1... done 🔥😈",
"💀 Bhai doom mein rasta ek hi hota hai — neeche 😂💀",
"💀 Doom activated — teri poori future: uncertain 🔥⚡",
"💀 Beta doom ki language — teri samajh nahi aati — result aata hai 😂😈",
"💀 DOOM FINAL — teri poori team: gone 🔥💀",
"💀 Bhai doom aur tu — aaj ka meetup tera worst tha 😂⚡",
"💀 Doom mode — tera har step: tracked 🔥😈",
"💀 Beta doom ne teri position: permanent zero confirm ki 😂💀",
"💀 DOOM RAIN — teri har cheez: destroyed 🔥⚡",
"💀 Bhai doom mein mercy nahi hoti — teri request: denied 😂😈",
"💀 Doom strike — teri sab galtiyan: collected 🔥💀",
"💀 Beta doom clock — teri ticking: started 😂⚡",
"💀 DOOM WAVE — teri poori defense: overwhelmed 🔥😈",
"💀 Bhai doom ki speed mein teri situation resolve ho gayi — badly 😂💀",
"💀 Doom verdict — teri case: closed — against you 🔥⚡",
"💀 Beta doom se pehle sun: teri galti — doom aaya 😂😈",
"💀 DOOM ARRIVAL — teri poori day ruined 🔥💀",
"💀 Bhai doom ne tujhe apna project bana liya 😂⚡",
"💀 Doom mode final — teri sab cheez: ash 🔥😈",
"💀 Beta doom ki ek khasiyat — woh aata zaroor hai 😂💀",
"💀 DOOM EXECUTION — teri poori plan: failed 🔥⚡",
"💀 Bhai doom tera number leke aaya tha — mila 😂😈",
"💀 Doom level MAX — teri recovery: impossible 🔥💀",
"💀 Beta doom ki taraf se ek gift — teri haari 😂⚡",
"💀 DOOM COMPLETE CYCLE — teri poori existence reset 🔥😈",
"💀 Bhai doom tujhse better hai — wait nahi karta 😂💀",
"💀 Doom mode — teri sab cheez: compromised 🔥⚡",
"💀 Beta DOOM aur tu — tujhe jeetna tha par doom ka hi naam hai 😂😈",
"💀 DOOM FINAL WAVE — teri sab: erased 🔥💀",
"💀 Bhai doom ne tujhe memorable bana diya — galat reasons se 😂⚡",
"💀 Doom activated final time — teri countdown: zero 🔥😈",
"💀 Beta DOOM se seekhna tha — tujhe nahi tha pata ab hai 😂💀",
"💀 DOOM OVER — teri side: collapsed — mine: standing 🔥⚡",
"💀 Bhai doom ne tera chapter likh diya — R.I.P. chapter 😂😈",
"💀 Doom final message — tujhe yaad rahega — sahi reasons se nahi 🔥💀",
"💀 Beta DOOM complete — check teri condition — yahi tha 😂⚡",
]

# ─── GAME TEXTS (Menu10) ──────────────────────────────────────────────

truth_texts = [
"Tumhara sabse bada secret kya hai jo kisi ko nahi pata? 🤫",
"Kisi pe crush tha jo ab dost hai? 😳",
"Kabhi kisi ki baat repeat ki thi jo confidence mein batai gayi thi? 😬",
"Woh kaun hai jis par sabse zyada trust karte ho? ❤️",
"Life mein sabse bada regret kya hai? 💭",
"Kabhi class ya office se bina bataye bhaage ho? 😂",
"Tumhari sabse embarrassing memory kya hai? 😳",
"Kabhi kisi ko jhooth bol ke escape kiya hai? 🤥",
"Tumhara sabse bada fear kya hai? 😨",
"Kabhi kisi se pyaar kiya hai jo tumhe pata nahi? 💔",
"Tumhari life ka best decision kya tha? ✅",
"Kabhi kisi ko ghost kiya hai? 👻",
"Tumhara sabse bada achievement kya hai? 🏆",
"Kabhi kisi ko 'I love you' bola hai jhooth mein? 💀",
"Tumhari sabse badi weakness kya hai? 😅",
"Kabhi kisi ka trust todna pada hai? 💔",
"Tumhari favourite memory kya hai? 📸",
"Kabhi kisi ko dekh ke jealous feel kiya hai? 😤",
"Tumhara sabse bada dream kya hai? 🌟",
"Kabhi kisi ki feelings hurt kari hai? 😢",
"Tumhari sabse badi strength kya hai? 💪",
"Kabhi kisi ko forgive kiya hai jo worth nahi tha? 🙏",
"Tumhara worst date experience kya tha? 😬",
"Kabhi kisi ko block kiya hai without reason? 🚫",
"Tumhari guilty pleasure kya hai? 🍫",
"Kabhi kisi se jealous hoke galat kiya hai? 😤",
"Tumhara favourite childhood memory kya hai? 🧸",
"Kabhi kisi ko sacrifice kiya hai apne liye? 🥺",
"Tumhari life ki best advice kya hai? 💡",
"Kabhi apne best friend se jhooth bola hai? 🤥"
]

dare_texts = [
"Apni maa ko call kar ke bol — 'Main tujhse pyaar karta hoon' 📞❤️",
"Apni sabse embarrassing photo share kar group mein 📸😹",
"Kisi bhi friend ko abhi message kar — 'Bhai mujhe pata chal gaya' — aur reaction dekho 😈",
"10 seconds ke liye khud se hi baat karo — loud 🗣️",
"Abhi ek push-up kar aur photo bhejo 💪",
"Apne crush ko 'Hi' bol — screenshot bhejo 😳",
"Khud ki roast karo ek paragraph mein — seriously 😂",
"Apna phone wallpaper change karo kisi funny photo mein 📱",
"5 random logo ko 'I love you' message karo 💌",
"Apni last seen status pe kuch funny likho 📝",
"Kisi bhi group mein 'Main pagal hoon' bolo 🤪",
"Apna profile pic change karo kisi meme se 🖼️",
"Apne best friend ko call karo aur kuch funny bolo 📞",
"Apni gallery se koi embarrassing photo share karo 📸",
"Kisi random person ko compliment do 🌹",
"Apne parents ko 'I love you' bolo ❤️",
"Kisi bhi chat mein 'I am the best' bolo 😎",
"Apna phone number kisi stranger ko do 📱",
"Kisi ko 'You are amazing' bol kar photo bhejo 💖",
"Apni life ka sabse embarrassing story share karo 📖",
"Kisi ko 'Mujhe tumse pyaar hai' bol kar block karo 💀",
"Apni bio mein kuch weird likho 📝",
"Kisi bhi group mein 'Main aaj gussa hoon' bolo 😤",
"Apne crush ko 'Hi' bol kar screenshot bhejo 😳",
"Kisi ko 'You are my hero' bolo 🦸",
"Apni last seen story mein kuch funny daalo 📱",
"Kisi bhi chat mein 'Main bhagwan hoon' bolo 😂",
"Apne best friend ko 'Main teri maa hoon' bolo 🤣",
"Kisi random person ko 'You are beautiful' bolo 💕",
"Apni life ki best memory share karo 📸"
]

situation_texts = [
"Agar tumhe 1 crore mil jaye toh kya karoge? 💰",
"Agar tum 1 din invisible ho sakte ho toh kya karoge? 👻",
"Agar tumhe ek wish mil jaye toh kya maangoge? ✨",
"Agar tum president ban jao toh kya change karoge? 🏛️",
"Agar tumhe time travel karna hai toh kahan jaoge? ⏳",
"Agar tumhe 3 wishes mil jaye toh kya maangoge? 🌟",
"Agar tum superpower choose kar sakte ho toh kya? 🦸",
"Agar tumhe ek book likhni hai toh kya likhoge? 📖",
"Agar tum famous ho jao toh kya karoge? 🌟",
"Agar tumhe ek din kuch bhi karne ko mile toh kya karoge? 🎉",
"Agar tumhe ek country choose karni hai toh kaunsi? 🌍",
"Agar tumhe ek language seekhni hai toh kaunsi? 🗣️",
"Agar tum apna naam change kar sakte ho toh kya rakhenge? 📛",
"Agar tumhe apni life 1 word mein describe karni hai toh kya? 💬",
"Agar tumhe ek famous personality se milna hai toh kaun? 🌟",
"Agar tumhe 1 din life free ho toh kya karoge? 🎈",
"Agar tumhe apni life ka best moment choose karna hai toh kya? 📸",
"Agar tumhe ek skill seekhni hai toh kaunsi? 🎯",
"Agar tumhe apni life ka worst moment choose karna hai toh kya? 😢",
"Agar tumhe ek adventure karna hai toh kya? 🏔️",
"Agar tumhe apni life change karni hai toh kya change karoge? 🔄",
"Agar tumhe ek dream choose karna hai toh kya? 💭",
"Agar tumhe apni life ka best decision choose karna hai toh kya? ✅",
"Agar tumhe ek challenge choose karna hai toh kya? 🏆",
"Agar tumhe apni life ka best friend choose karna hai toh kaun? 🤝",
"Agar tumhe apni life ka worst decision choose karna hai toh kya? ❌",
"Agar tumhe ek goal choose karna hai toh kya? 🎯",
"Agar tumhe apni life ka best memory choose karna hai toh kya? 📸",
"Agar tumhe apni life ka worst memory choose karna hai toh kya? 😢",
"Agar tumhe apni life ka best achievement choose karna hai toh kya? 🏆"
]

# ─── QUIZ TEXTS ────────────────────────────────────────────────────────

quiz_texts = [
{"q": "IIT JEE mein kaunsi book sabse important hai?", "a": "HC Verma"},
{"q": "Physics mein 'g' ki value kya hai?", "a": "9.8"},
{"q": "Formula E = mc² kisne diya?", "a": "Einstein"},
{"q": "IIT ka full form kya hai?", "a": "Indian Institute of Technology"},
{"q": "JEE ka full form kya hai?", "a": "Joint Entrance Examination"},
{"q": "Physics mein SI unit of force kya hai?", "a": "Newton"},
{"q": "Chemistry mein H2O kya hai?", "a": "Water"},
{"q": "Maths mein 'pi' ki value kya hai?", "a": "3.14"},
{"q": "Biology mein human body mein kitna water hai?", "a": "70%"},
{"q": "IIT mein admission kaunsi exam se hota hai?", "a": "JEE Advanced"},
{"q": "NEET ka full form kya hai?", "a": "National Eligibility cum Entrance Test"},
{"q": "Human body mein kitna blood hai?", "a": "5 liters"},
{"q": "Heart ka function kya hai?", "a": "Blood pump"},
{"q": "Brain ka weight kitna hai?", "a": "1.4 kg"},
{"q": "Biology mein DNA ka full form kya hai?", "a": "Deoxyribonucleic Acid"},
{"q": "Human eye mein kitne colors dikhte hain?", "a": "10 million"},
{"q": "Body mein kitne bones hain?", "a": "206"},
{"q": "Blood group kaunse type ke hote hain?", "a": "A, B, AB, O"},
{"q": "NEET mein kitne questions hote hain?", "a": "200"},
{"q": "MBBS ka full form kya hai?", "a": "Bachelor of Medicine and Bachelor of Surgery"},
{"q": "Earth ka sabse bada ocean kaunsa hai?", "a": "Pacific Ocean"},
{"q": "World ka sabse lamba river kaunsa hai?", "a": "Nile River"},
{"q": "Human body mein sabse bada organ kaunsa hai?", "a": "Skin"},
{"q": "Universe ka sabse bada planet kaunsa hai?", "a": "Jupiter"},
{"q": "Light ki speed kya hai?", "a": "3x10^8 m/s"},
{"q": "Earth ka sabse ooncha mountain kaunsa hai?", "a": "Mount Everest"},
{"q": "World mein sabse zyada population wala country kaunsa hai?", "a": "India"},
{"q": "Computer ka brain kaunsa hai?", "a": "CPU"},
{"q": "Mobile OS kaunse hain?", "a": "Android, iOS"},
{"q": "World ka sabse bada desert kaunsa hai?", "a": "Sahara Desert"}
]

# ─── RIDDLE TEXTS ──────────────────────────────────────────────────────

riddle_texts = [
{"q": "Main hoon jo andar aata hai par bahar nahi jaata. Main hoon jo har insaan ke paas hai. Main kya hoon?", "a": "Sans (Breath)"},
{"q": "Main hoon jo duniya mein sabse bada hai, par main kisi ko dikhta nahi. Main kya hoon?", "a": "Pyaar (Love)"},
{"q": "Main hoon jo haath mein aata hai par pakda nahi jaata. Main kya hoon?", "a": "Pani (Water)"},
{"q": "Main hoon jo har insaan ko dikhta hai par koi dekh nahi sakta. Main kya hoon?", "a": "Andhera (Darkness)"},
{"q": "Main hoon jo kabhi nahi rukta, kabhi nahi thakta. Main kya hoon?", "a": "Samay (Time)"},
{"q": "Main hoon jo duniya mein sabse tez hai, par main kisi ko dikhta nahi. Main kya hoon?", "a": "Vichar (Thought)"},
{"q": "Main hoon jo andar hota hai par bahar nahi. Main kya hoon?", "a": "Dil (Heart)"},
{"q": "Main hoon jo har insaan ke paas hai par koi use nahi karta. Main kya hoon?", "a": "Dimag (Brain)"},
{"q": "Main hoon jo kabhi nahi sota, kabhi nahi thakta. Main kya hoon?", "a": "Aankh (Eye)"},
{"q": "Main hoon jo har insaan ki madad karta hai par koi use nahi dekhta. Main kya hoon?", "a": "Hawa (Air)"},
{"q": "Main hoon jo duniya mein sabse chhota hai, par sab se bada kaam karta hoon. Main kya hoon?", "a": "Beej (Seed)"},
{"q": "Main hoon jo kabhi nahi marta, kabhi nahi hota. Main kya hoon?", "a": "Atma (Soul)"},
{"q": "The person who makes it doesn't need it. The person who buys it doesn't use it. The person who uses it doesn't know they're using it. What is it?", "a": "coffin"},
]

# ─── FUN TEXTS (Joke, Fact, Compliment, Quotes) ──────────────────────

joke_list = [
"Main apni life mein itna positive hoon... ki blood group bhi B+ hai! 😂",
"Teacher: Kal absent kyun the? Student: Sir, mujhe bukhar tha. Teacher: Proof? Student: Aaj aa gaya na! 😹",
"Santa: Main ghar ke bahar khada hun. Banta: Andar aa jao. Santa: Andar wala bhi main hoon! 🤣",
"Meri girlfriend ne kaha — tujhse better koi nahi. Phir chali gayi. Better koi mila hoga shayad 😂",
"Doctor: Patient ko hawa ki zaroorat hai. Nurse: Kya karein? Doctor: Fan on karo. Nurse: Ceiling se pakad ke? 😹",
"Ghar mein sabse zyada kaam mera — internet chalaana! 😂",
"Padhai karo beta future bright hoga. Maine padhi — future gaya andhera mein. 😂",
"Wo bolti hai 'I need space' — main bola ठीक है, NASA se contact karo! 😂",
"Mera wifi itna slow hai ke circle of life bhi nahi chalta 🐢",
"Main sochta hoon kal se gym jaunga... kal kab aata hai? 🤔",
"Mummy ka 2 minute aur Maggi ka 2 minute kabhi same nahi hote",
"Aaj kal log 'seen' karke itna attitude dikhate hain, jaise message nahi loan approve kar rahe ho",
"Meri life itni private hai ki mujhe khud next update ka pata nahi hota 🤡 ",
"Mere jokes pe sirf do log haste hain... main aur meri overconfidence 🤣",
"Log bolte hain Be yourself... phir judge bhi wahi log karte hain",
"Life ne itne twists diye hain ki Google Maps bhi rerouting kar de",
]

fact_list = [
"🧠 Insaan ka dimag 75% paani se bana hai!",
"🐙 Octopus ke teen dil hote hain!",
"🌙 Chand par mobile signal nahi hai — par WiFi aata hai ek satellite se! (Future plan 😂)",
"🍯 Sahi tarike se rakha hua honey kabhi kharab nahi hota!",
"⚡ Bijli ka ek bolt 5 times zyada garam hota hai sun ki surface se!",
"🦈 Shark insaan se zyada purana hai — dinasors se bhi pehle!",
"👁️ Insaan ki aankh 10 million rangon ko differentiate kar sakti hai!",
"🐝 Ek machhar ek second mein 600 baar apne pankh hilata hai!",
"🦒 Giraffe ki tongue 20 inches lambi hoti hai!",
"🐧 Penguins ek dusre ko pehchanne ke liye unique calls use karte hain!",
"🚀 Space mein awaaz travel nahi karti, kyunki wahan hawa nahi hoti.",
"👅 Har insaan ki tongue print fingerprints ki tarah unique hoti hai.",
"🦒 Giraffe apni 21-inch lambi tongue se kaan saaf kar sakta hai.",
"⚡ Lightning ka temperature Suraj ki surface se bhi zyada hota hai",
"🌍 Har second Earth par lagbhag 100 lightning strikes hoti hain.",
"🐌 Snail 3 saal tak so sakta hai (kuch species mein).",
"🧊 Garam paani kuch conditions mein thande paani se jaldi jam sakta hai (Mpemba effect).",
"👀 Insaan ka brain ulta image dekhta hai aur use seedha process karta hai.",
"🍌 Banana technically ek berry hai, lekin strawberry nahi.",
"🦘 Kangaroo peeche ki taraf chal nahi sakta.",
"🐧 Penguins propose karne ke liye apne partner ko chhota sa pathar gift karte hain (kuch species mein).",
"💀 Human body mein itni blood vessels hoti hain ki unhe line mein jodo to lagbhag 100,000 km lambi ho jaayengi.",
"🌌 Hum raat ko jo kuch stars dekhte hain, unki light kai saal pehle nikli hoti hai.",
"🐝 Bees insaanon ke chehre pehchaan sakti hain.",
]

compliment_list = [
"Bhai tu bahut positive energy rakhta hai — seriously 🌟",
"Teri thinking bahut alag hai — creative hai tu 🧠✨",
"Tu jo bhi karta hai dil se karta hai — yeh rare hai ❤️",
"Teri sense of humor? Top tier 😂👑",
"Tujhse baat karna genuinely enjoyable hota hai 🗣️✨",
"Tu ek natural leader hai — log tujhe follow karte hain 👑",
"Teri mehnat dekh ke lagta hai, success teri waiting hai 💪",
"Teri smile contagious hai — sabko khushi deti hai 😊",
"Tu bahut strong insaan hai — sab handle kar leta hai 💪",
"Teri vibe bohot positive hai — tere saath time acha lagta hai ✨",
"You're one of a kind.",
"Tumhari vibe alag hi level ki hai.",
"You're effortlessly cool.",
"Tum jahan hote ho, wahan energy aa jaati hai.",
"You make everything look easy.",
"Tumhari personality hi alag hai.",
"You're genuinely impressive.",
"Tumhare ideas hamesha unique hote hain.",
"You're unforgettable.",
"Tum confidence ka perfect example ho.",
"Built different. 💯",
"Aura speaks louder than words.",
"You're the main character.",
"Tumhari smile mood fix kar deti hai.",
"You make people feel comfortable.",
"You're naturally adorable.",
"Tumhari laugh contagious hai.",
"You're a walking green flag.",
"You're sunshine in human form.",
"Tumhare saath time ka pata hi nahi chalta.",
"You have the kindest heart.",
"You're effortlessly charming.",
"You make ordinary moments special.",
"Standards on another level.",
"Too real to be fake.",
"Calm outside, dangerous inside.",
"Rare people have this kind of aura.",
"Silent, but unforgettable.",
"Class never chases attention.",
"You don't follow trends, you set them.",
"You're the flex you don't even need to show.",
"Some people have looks, you have presence.",
"Your aura deserves its own fan club.",
"You're proof that being real is attractive.",
"Not everyone shines, but you do.",
"You don't need attention, attention finds you.",
"Legends don't introduce themselves.",
"Your vibe is expensive.",
"You're the kind of person people remember.",
"You make confidence look natural. 😎",
]

quote_list = [
"💭 Sapne woh nahi jo sote waqt aate hain, sapne woh hain jo sone nahi dete. — APJ Abdul Kalam",
"💭 'Mehnat karo itna ki luck ko bhi mauka mile tujhe dhundhne ka.' — Unknown",
"💭 'Duniya ka sabse bada teacher: failure hai.' — Unknown",
"💭 'Ek accha dost aur ek accha kitaab — dono hi tujhe better banate hain.' — Unknown",
"💭 'Zindagi ek echo hai — jo bejhoge woh wapas aayega.' — Unknown",
"💭 'Success is not final, failure is not fatal: it is the courage to continue that counts.' — Churchill",
"💭 'The only way to do great work is to love what you do.' — Steve Jobs",
"💭 'In the middle of difficulty lies opportunity.' — Einstein",
"💭 'Believe you can and you're halfway there.' — Theodore Roosevelt",
"💭 'The best time to plant a tree was 20 years ago. The second best time is now.' — Chinese Proverb",
"💭 People's lives don't end when they die, it ends when they lose faith. — Itachi Uchiha",
"💭 Wake up to reality. Nothing ever goes as planned in this world. — Madara Uchiha",
"💭 Those who break the rules are trash, but those who abandon their friends are worse than trash. — Kakashi Hatake",
"💭 When people are protecting something truly precious, they truly become strong. — Haku",
"💭 A lesson without pain is meaningless. — Edward Elric",
"💭 A person grows up when they're able to overcome hardships. — Jiraiya",
"💭 Power comes in response to a need, not a desire. — Goku",
"💭 If you don't take risks, you can't create a future. — Monkey D. Luffy",
"💭 The world isn't perfect, but it's there for us. — Roy Mustang",
"💭 Fear is not evil. It tells you your weakness. — Gildarts Clive",
"💭 The moment you think of giving up, think of the reason why you held on so long. — Natsu Dragneel",
"💭 Hard work is worthless for those that don't believe in themselves. — Naruto Uzumaki",
"💭 The difference between the novice and the master is that the master has failed more times than the novice has tried. — Koro-sensei",
"💭 To know sorrow is not terrifying. What is terrifying is to know you can't go back to happiness. — Matsumoto Rangiku",
"💭 Whatever you lose, you'll find it again. But what you throw away you'll never get back. — Kenshin Himura",
"💭 Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
"💭 The only way to do great work is to love what you do. — Steve Jobs",
"💭 Stay hungry, stay foolish. — Steve Jobs",
"💭 Your time is limited, so don't waste it living someone else's life. — Steve Jobs",
"💭 The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
"💭 Be yourself; everyone else is already taken. — Oscar Wilde",
"💭 It always seems impossible until it's done. — Nelson Mandela",
"💭 Dream big and dare to fail. — Norman Vaughan",
"💭 Do what you can, with what you have, where you are. — Theodore Roosevelt",
"💭 Believe you can and you're halfway there. — Theodore Roosevelt",
"💭 The best way to predict the future is to create it. — Peter Drucker",
"💭 Discipline is choosing between what you want now and what you want most.",
"💭 Don't watch the clock; do what it does. Keep going. — Sam Levenson",
"💭 The journey of a thousand miles begins with one step. — Lao Tzu",
"💭 Fall seven times, stand up eight. — Japanese Proverb",
"💭 Action is the foundational key to all success. — Pablo Picasso",
"💭 Work hard in silence, let success make the noise.",
"💭 Great things never come from comfort zones.",
"💭 Small steps every day lead to big results.",
"💭 Consistency beats motivation.",
"💭 Discipline creates freedom.",
"💭 Your only competition is the person you were yesterday.",
"💭 Never let success get to your head or failure get to your heart.",
"💭 A calm mind is a powerful weapon.",
"💭 Pressure creates diamonds.",
]
# ─── PWR & OWS TEXT LISTS ─────────────────────────────────────────────
pwr_texts = [
"Kyun",
"Re",
"Mc",
"Ka",
"Baccha",
"Apna",
"Papa",
"Sa",
"Hawabji",
"Karega",
"Randi",
"Rand",
"Ka",
"Beta",
"Teri",
"Maa",
"Ki",
"Kali",
"Kali",
"Chut",
"Ma",
"Lund",
"Daal",
"Ka",
"Mix",
"Kar",
"Dunga",
"Te",
"RANDI",
"Ka",
"Beta",
"Teri",
"Mausi",
"Ko",
"Apna",
"Lund",
"Pa",
"Baitha",
"Ka",
"Puri",
"Duniya",
"Ghumunga",
"Re",
"Chinnar",
"Ka",
"Beta",
"Tere",
"Baap",
"Ko",
"Apna",
"Goto",
"Sa",
"Chap",
"Ka",
"Maar",
"DUNGA",
"Mc",
"Dhanda",
"Wali",
"Ka",
"Ladka",
"Kaha",
"Gayi",
"Teri",
"Speed",
"Abb",
"Apna",
"Papa",
"Sa",
"Hawabaji",
"Nahi",
"KAREGA",
"Mc",
"Ka",
"Pill",
"Teri",
"Bhen",
"Ka",
"Rape",
"Kar",
"Dunga",
"Bc",
"Majduri",
"Ruko",
"Teri",
"Tho",
"Mai",
"Tera",
"Bhen",
"Betiyon",
"Ka",
"Rape",
"Kar",
"Ka",
"Bhagg",
"Jaunga",
"Mc",
"Teri",
"Maa",
"Ke"

]
ows_texts = [
"Kyun",
"Re",
"Mc",
"Ka",
"Baccha",
"Apna",
"Papa",
"Sa",
"Hawabji",
"Karega",
"Randi",
"Rand",
"Ka",
"Beta",
"Teri",
"Maa",
"Ki",
"Kali",
"Kali",
"Chut",
"Ma",
"Lund",
"Daal",
"Ka",
"Mix",
"Kar",
"Dunga",
"Te",
"RANDI",
"Ka",
"Beta",
"Teri",
"Mausi",
"Ko",
"Apna",
"Lund",
"Pa",
"Baitha",
"Ka",
"Puri",
"Duniya",
"Ghumunga",
"Re",
"Chinnar",
"Ka",
"Beta",
"Tere",
"Baap",
"Ko",
"Apna",
"Goto",
"Sa",
"Chap",
"Ka",
"Maar",
"DUNGA",
"Mc",
"Dhanda",
"Wali",
"Ka",
"Ladka",
"Kaha",
"Gayi",
"Teri",
"Speed",
"Abb",
"Apna",
"Papa",
"Sa",
"Hawabaji",
"Nahi",
"KAREGA",
"Mc",
"Ka",
"Pill",
"Teri",
"Bhen",
"Ka",
"Rape",
"Kar",
"Dunga",
"Bc",
"Majduri",
"Ruko",
"Teri",
"Tho",
"Mai",
"Tera",
"Bhen",
"Betiyon",
"Ka",
"Rape",
"Kar",
"Ka",
"Bhagg",
"Jaunga",
"Mc",
"Teri",
"Maa",
"Ke"
]

ADD_BOTS_LIST = [
"@Soulreaper99_bot", "@Soulreaper98_bot", "@Soulreaper97_bot",
"@Soulreaper96_bot", "@Soulreaper95_bot", "@Soulreaper94_bot",
"@Soulreaper93_bot", "@Soulreapernc1_bot", "@Soulreapernc2_bot",
"@Soulreapernc3_bot", "@Asurfighter12bot",
]

GC_FAST_EMOJIS = ["❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","🩷","🩵","🩶","💖","💘","💝","💗","💓","💞","💕","💟","❣️","❤️‍🔥","❤️‍🩹"]

premium_raid_texts = {
"mr": mr_texts, "mr2": mr2_texts, "br": br_texts, "br2": br2_texts,
"br3": br3_texts, "sqr": sqr_texts, "sq2": sq2_texts, "cr": cr_texts,
"bar": bar_texts, "gr": gr_texts
}
premium_spam_texts = {
"ms": ms_texts, "ms2": ms2_texts, "bs": bs_texts, "bs2": bs2_texts,
"bs3": bs3_texts, "sqs": sqs_texts, "sqs2": sqs2_texts, "cs": cs_texts,
"bas": bas_texts, "gs": gs_texts
}

# ═══════════════════════════════════════════════════════════════════════
# SECTION 2: AESTHETIC BOX UI SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def build_box(title: str, items: list, footer: str = None) -> str:
    """
    Build an aesthetic box-style menu with rich Unicode decorations.
    Renders beautifully in Telegram's ``` code block (dark background).
    
    Features:
    - Double-line outer border (╔═╗ ╚═╝)
    - Decorative title with ✦ symbols
    - Section separators with ⋆｡°✩
    - Proper padding and alignment
    """
    W = 48  # Total width inside borders

    lines = []
    
    # ── Top border with title ──
    title_text = f" ✦ {title} ✦ "
    left_pad = (W - len(title_text)) // 2
    right_pad = W - len(title_text) - left_pad
    lines.append(f"╔{'═' * W}╗")
    lines.append(f"║{' ' * left_pad}{title_text}{' ' * right_pad}║")
    lines.append(f"╠{'═' * W}╣")

    # ── Content ──
    for item in items:
        if item == "":
            # Empty line
            lines.append(f"║{' ' * W}║")
        elif item.startswith("───") and item.endswith("───"):
            # Section header: "─── 〔 SECTION NAME 〕 ───"
            raw = item.strip("─ ").strip("〔 〕").strip()
            sec_text = f" ──〔 {raw} 〕── "
            # Center it
            sp = (W - len(sec_text)) // 2
            lines.append(f"║{' ' * sp}{sec_text}{' ' * (W - len(sec_text) - sp)}║")
        else:
            # Regular line — trim if too long
            text = item[:W] if len(item) > W else item
            lines.append(f"║ {text.ljust(W - 1)}║")

    # ── Bottom border ──
    lines.append(f"╚{'═' * W}╝")

    result = "\n".join(lines)
    if footer:
        result += "\n\n" + footer

    return f"```\n{result}\n```"


def menu_header() -> str:
    """Return the standard header for all menus."""
    return (
        "✦═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━═✦\n"
        "     ⚡️ ZYЯΣX ✕ ΛΣƬΉΣЯ ⚡️ USERBOT\n"
        "✦═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━═✦"
    )


def menu_footer(cmd: str = ".menu") -> str:
    """Return the standard footer for menus."""
    return f"💡 Use `{cmd}` for this menu • `.menu` for main"


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3: DATABASE & ENCRYPTION
# ═══════════════════════════════════════════════════════════════════════

db_pool = None
cipher = None


async def init_db():
    global db_pool
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL not set — JSON/file fallback")
        return
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id BIGINT PRIMARY KEY, session_encrypted TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS app_config (
                key_name TEXT PRIMARY KEY, key_value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id BIGINT PRIMARY KEY, plan TEXT NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP, status TEXT DEFAULT 'active'
            );
            CREATE TABLE IF NOT EXISTS premium_protections (
                user_id BIGINT, command_name TEXT,
                PRIMARY KEY (user_id, command_name)
            );
            CREATE TABLE IF NOT EXISTS user_wallet (
                user_id BIGINT PRIMARY KEY, balance DECIMAL(10,2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS dm_settings (
                user_id BIGINT PRIMARY KEY, shield_enabled BOOLEAN DEFAULT FALSE,
                god_protection BOOLEAN DEFAULT FALSE,
                "freeze" BOOLEAN DEFAULT FALSE, auto_reply TEXT
            );
            CREATE TABLE IF NOT EXISTS dm_approved (
                user_id BIGINT, approved_id BIGINT, PRIMARY KEY (user_id, approved_id)
            );
            CREATE TABLE IF NOT EXISTS dm_blocked (
                user_id BIGINT, blocked_id BIGINT, PRIMARY KEY (user_id, blocked_id)
            );
            CREATE TABLE IF NOT EXISTS dm_warnings (
                user_id BIGINT, target_id BIGINT, count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS dm_filters (
                user_id BIGINT, word TEXT, response TEXT,
                response_type TEXT DEFAULT 'text', PRIMARY KEY (user_id, word)
            );
            CREATE TABLE IF NOT EXISTS sangmata_history (
                user_id BIGINT, target_id BIGINT, old_name TEXT,
                old_username TEXT, new_name TEXT, new_username TEXT,
                change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS user_freeze (
                user_id BIGINT PRIMARY KEY, frozen BOOLEAN DEFAULT FALSE
            );
            CREATE TABLE IF NOT EXISTS broadcast_users (
                user_id BIGINT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS god_protection (
                user_id BIGINT PRIMARY KEY, enabled BOOLEAN DEFAULT FALSE,
                action TEXT DEFAULT 'delete', threshold_mentions INTEGER DEFAULT 3,
                threshold_sec INTEGER DEFAULT 10, auto_mute BOOLEAN DEFAULT FALSE,
                mute_duration_min INTEGER DEFAULT 5
            );
        """)
    print("✅ Database ready")


async def get_encryption_key() -> str:
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT key_value FROM app_config WHERE key_name='encryption_key'")
        if row:
            return row["key_value"]
        new_key = Fernet.generate_key().decode()
        await conn.execute(
            "INSERT INTO app_config (key_name, key_value) VALUES ($1, $2)",
            "encryption_key", new_key
        )
        return new_key


async def init_cipher():
    global cipher
    key = await get_encryption_key()
    cipher = Fernet(key.encode())


def encrypt_session(sess: str) -> str:
    if cipher is None:
        raise RuntimeError("Cipher not initialized")
    return cipher.encrypt(sess.encode()).decode()


def decrypt_session(data: str) -> str:
    if cipher is None:
        raise RuntimeError("Cipher not initialized")
    return cipher.decrypt(data.encode()).decode()


# ═══════════════════════════════════════════════════════════════════════
# SECTION 4: BROADCAST JSON
# ═══════════════════════════════════════════════════════════════════════

def load_broadcast_json() -> List[int]:
    if os.path.exists(BROADCAST_JSON_PATH):
        try:
            with open(BROADCAST_JSON_PATH, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return list(data.keys())
        except:
            pass
    return []


def save_broadcast_json(users_list: List[int]) -> List[int]:
    clean = sorted(set(int(u) for u in users_list))
    with open(BROADCAST_JSON_PATH, 'w') as f:
        json.dump(clean, f, indent=2)
    return clean


def add_to_broadcast_json(user_id: int) -> List[int]:
    """Add user — NEVER removes, always adds."""
    users = load_broadcast_json()
    uid = int(user_id)
    if uid not in users:
        users.append(uid)
        save_broadcast_json(users)
    return users


# ═══════════════════════════════════════════════════════════════════════
# SECTION 5: CHANNEL VERIFICATION (FIXED)
# ═══════════════════════════════════════════════════════════════════════

async def is_user_in_channel(client: TelegramClient, user_id: int, channel_data: dict) -> bool:
    """
    PROPERLY check if a user has joined a channel.
    Uses GetParticipantRequest — the ONLY reliable method.
    Handles: public channels, private channels, invite links, errors.
    """
    try:
        channel_id = channel_data["id"]
        channel_entity = await client.get_entity(channel_id)

        # ── Method 1: GetParticipantRequest (Most Reliable) ──
        try:
            result = await client(GetParticipantRequest(
                channel=channel_entity,
                participant=user_id
            ))
            return True  # No exception = user IS a member

        except UserNotParticipantError:
            return False  # User is NOT a member

        except (ChannelInvalidError, ChannelPrivateError) as e:
            print(f"[Verify] Access error: {e}")
            return False

    except ValueError as e:
        print(f"[Verify] Entity error: {e}")
        return False
    except Exception as e:
        print(f"[Verify] Unexpected: {e}")
        return False


def get_join_buttons():
    buttons = []
    for idx, ch in enumerate(REQUIRED_CHANNELS, 1):
        buttons.append([
            KeyboardButtonUrl(text=f"🔗 Join {ch['name']}", url=ch["invite"])
        ])
    buttons.append([
        KeyboardButtonCallback(text="✅ I have joined all", data=b"verify_channels")
    ])
    return buttons


# ═══════════════════════════════════════════════════════════════════════
# SECTION 6: DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def save_session(user_id: int, session_str: str):
    encrypted = encrypt_session(session_str)
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_sessions (user_id, session_encrypted) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
            SET session_encrypted = $2, updated_at = CURRENT_TIMESTAMP
        """, user_id, encrypted)


async def load_sessions() -> Dict[int, str]:
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id, session_encrypted FROM user_sessions")
    sessions = {}
    for row in rows:
        try:
            sessions[row["user_id"]] = decrypt_session(row["session_encrypted"])
        except:
            await delete_session(row["user_id"])
    return sessions


async def delete_session(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM user_sessions WHERE user_id=$1", user_id)


async def set_freeze(user_id: int, frozen: bool):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_freeze (user_id, frozen) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET frozen=$2
        """, user_id, frozen)


async def get_freeze(user_id: int) -> bool:
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT frozen FROM user_freeze WHERE user_id=$1", user_id)
        return row["frozen"] if row else False


async def get_balance(user_id: int) -> float:
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM user_wallet WHERE user_id=$1", user_id)
        return float(row["balance"]) if row else 0.0


async def add_balance(user_id: int, amount: float):
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_wallet (user_id, balance) VALUES ($1, $2)
            ON CONFLICT(user_id) DO UPDATE
            SET balance = user_wallet.balance + $2, updated_at = CURRENT_TIMESTAMP
        """, user_id, amount)


async def deduct_balance(user_id: int, amount: float):
    balance = await get_balance(user_id)
    if balance < amount:
        raise ValueError("Insufficient balance")
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE user_wallet SET balance = balance - $2, updated_at = CURRENT_TIMESTAMP WHERE user_id = $1",
            user_id, amount
        )


async def add_premium_user(user_id: int, plan: str, days: int):
    expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO premium_users (user_id, plan, expiry_date, status) VALUES ($1, $2, $3, 'active')
            ON CONFLICT (user_id) DO UPDATE
            SET plan = $2, expiry_date = $3, status = 'active', start_date = CURRENT_TIMESTAMP
        """, user_id, plan, expiry)
    for cmd in PROTECTED_COMMANDS:
        await add_protection(user_id, cmd)
    try:
        await MAIN_BOT_CLIENT.send_message(
            user_id,
            f"🛡️ **Premium Activated!**\nPlan: {plan.upper()}\nExpires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}\nYou are protected from all raids."
        )
    except:
        pass


async def get_premium_user(user_id: int):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM premium_users WHERE user_id = $1", user_id)
        return dict(row) if row else None


async def check_premium_status(user_id: int):
    data = await get_premium_user(user_id)
    if not data or data['status'] != 'active':
        return None
    if data['expiry_date'] < datetime.datetime.now():
        async with db_pool.acquire() as conn:
            await conn.execute("UPDATE premium_users SET status = 'expired' WHERE user_id = $1", user_id)
        return None
    return data


async def add_protection(user_id: int, command: str):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO premium_protections (user_id, command_name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id, command
        )


async def remove_protection(user_id: int, command: str):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM premium_protections WHERE user_id = $1 AND command_name = $2",
            user_id, command
        )


async def get_protections(user_id: int) -> Set[str]:
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT command_name FROM premium_protections WHERE user_id = $1", user_id
        )
    return {row['command_name'] for row in rows}


async def is_protected(target_user: int, command: str) -> bool:
    prem = await check_premium_status(target_user)
    if not prem:
        return False
    protections = await get_protections(target_user)
    return command in protections


# ═══════════════════════════════════════════════════════════════════════
# SECTION 7: MAIN BOT SETUP
# ═══════════════════════════════════════════════════════════════════════

MAIN_BOT_CLIENT = TelegramClient(
    "main_bot_session", API_ID, API_HASH,
    connection_retries=3, auto_reconnect=False
)

active_userbots = {}
user_sessions = {}
user_states = {}
running_tasks = set()

broadcast_users = set(load_broadcast_json())

print("🚀 Main Bot initialized...")


# ═══════════════════════════════════════════════════════════════════════
# SECTION 8: SAFE MESSAGE HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def safe_reply(event, text, buttons=None, **kwargs):
    try:
        return await event.reply(text, buttons=buttons, **kwargs)
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        return await event.reply(text, buttons=buttons, **kwargs)
    except:
        return None


async def safe_respond(event, text, **kwargs):
    try:
        return await event.respond(text, **kwargs)
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        return await event.respond(text, **kwargs)
    except:
        return None


async def safe_edit(event, text, buttons=None, **kwargs):
    try:
        return await event.edit(text, buttons=buttons, **kwargs)
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        return await event.edit(text, buttons=buttons, **kwargs)
    except MessageNotModifiedError:
        pass
    except:
        return None


async def safe_send_main(chat, text, **kwargs):
    try:
        return await MAIN_BOT_CLIENT.send_message(chat, text, **kwargs)
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        return await MAIN_BOT_CLIENT.send_message(chat, text, **kwargs)
    except:
        return None


# ═══════════════════════════════════════════════════════════════════════
# SECTION 9: ALL MENU UI DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

# ─── MENU: Main ──────────────────────────────────────────────────
MENU_MAIN = build_box("📖 MAIN MENU", [
    "",
    "─── 〔 ⚡️ SYSTEM INFO 〕 ───",
    "",
    "  ✦ Owner  : ZYЯΣX ✕ ΛΣƬΉΣЯ",
    "  ✦ Cmds   : 500+",
    "  ✦ Prefix : `.`",
    "",
    "─── 〔 📂 NAVIGATION 〕 ───",
    "",
    "  ▸ `.menu1`   → Admin, Mute, Group",
    "  ▸ `.menu2`   → Raid Engine + PWR",
    "  ▸ `.menu3`   → Spam, Deathgod, OWS",
    "  ▸ `.menu4`   → Protection, React",
    "  ▸ `.menu5`   → Tools, Music, Echo",
    "  ▸ `.menu6`   → Send & Tag",
    "  ▸ `.menu7`   → Fun Meters",
    "  ▸ `.menu8`   → Fun Raids",
    "  ▸ `.menu9`   → Non-Abusive Raids",
    "  ▸ `.menu10`  → Games & Fun",
    "  ▸ `.menu11a` → Premium Part A",
    "  ▸ `.menu11b` → Premium Part B",
    "  ▸ `.menu12`  → Protection",
    "  ▸ `.menu13`  → Premium Raids",
    "  ▸ `.menu14`  → Premium Spam",
    "",
], footer="💡 Use `.cmds` for full list • `.ping` for latency")


# ─── MENU 1: Admin & Group ──────────────────────────────────────
MENU_1 = build_box("👑 ADMIN & GROUP", [
    "",
    "─── 〔 ADMIN 〕 ───",
    "",
    "  ▸ `.admins`    → List admins",
    "  ▸ `.addadmin`  → Add admin (reply)",
    "  ▸ `.deladmin`  → Remove admin",
    "",
    "─── 〔 MUTE 〕 ───",
    "",
    "  ▸ `.mute`      → Local mute",
    "  ▸ `.unmute`    → Unmute",
    "  ▸ `.gmute`     → Global mute",
    "  ▸ `.gunmute`   → Global unmute",
    "  ▸ `.mutelist`  → Status",
    "",
    "─── 〔 GROUP MOD 〕 ───",
    "",
    "  ▸ `.lock`      → Lock group",
    "  ▸ `.unlock`    → Unlock",
    "  ▸ `.purge`     → Delete N msgs",
    "  ▸ `.throw`     → Kick user",
    "  ▸ `.addbots`   → Add bots",
    "",
    "─── 〔 AUTO TAG 〕 ───",
    "",
    "  ▸ `.autotag`       → Tag all members",
    "  ▸ `.stopautotag`   → Stop tagging",
    "",
], footer=menu_footer(".menu1"))


# ─── MENU 2: Raid Engine ────────────────────────────────────────
MENU_2 = build_box("⚔️ RAID ENGINE", [
    "",
    "─── 〔 REPLY RAID 〕 ───",
    "",
    "  ▸ `.reply`   → Start reply raid",
    "  ▸ `.sreply`  → Stop reply raid",
    "",
    "─── 〔 RR (Reply+React) 〕 ───",
    "",
    "  ▸ `.rr`   → Start RR raid",
    "  ▸ `.srr`  → Stop RR raid",
    "",
    "─── 〔 FLAG RAID 〕 ───",
    "",
    "  ▸ `.flag`   → Start flag raid",
    "  ▸ `.sflag`  → Stop flag raid",
    "",
    "─── 〔 HEART RAID 〕 ───",
    "",
    "  ▸ `.hrr`   → Start heart raid",
    "  ▸ `.shrr`  → Stop heart raid",
    "",
    "─── 〔 GOD RAID (4 replies) 〕 ───",
    "",
    "  ▸ `.replygod` → Start god raid",
    "  ▸ `.sgod`     → Stop god raid",
    "",
    "─── 〔 CUSTOM RAID 〕 ───",
    "",
    "  ▸ `.customraid`    → Start custom",
    "  ▸ `.stopcustomraid`→ Stop custom",
    "",
    "─── 〔 PWR RAID (Sequential) 〕 ───",
    "",
    "  ▸ `.pwr`  → Start PWR raid",
    "  ▸ `.spwr` → Stop PWR raid",
    "",
], footer=menu_footer(".menu2"))


# ─── MENU 3: Spam & Text ─────────────────────────────────────────
MENU_3 = build_box("💣 SPAM & TEXT", [
    "",
    "─── 〔 SPRAY COMMANDS 〕 ───",
    "",
    "  ▸ `.spray`      → Infinite spray",
    "  ▸ `.dspray`     → Stop chat spray",
    "  ▸ `.tspray`     → Spam saved text",
    "  ▸ `.rspray`     → Random saved text",
    "  ▸ `.multispray` → Rotate texts",
    "  ▸ `.countspray` → Exactly N times",
    "  ▸ `.spraydelay` → Adjust speed",
    "",
    "─── 〔 TEXT MANAGER 〕 ───",
    "",
    "  ▸ `.addtext`   → Save text",
    "  ▸ `.listtexts` → Show saved",
    "  ▸ `.edittext`  → Edit saved",
    "  ▸ `.deltext`   → Delete text",
    "  ▸ `.cleartext` → Delete all",
    "",
    "─── 〔 DEATHGOD 〕 ───",
    "",
    "  ▸ `.deathgod`  → Start deathgod",
    "  ▸ `.sdeathgod` → Stop deathgod",
    "",
    "─── 〔 OWS SPAM 〕 ───",
    "",
    "  ▸ `.ows` → Start OWS spam",
    "  ▸ `.sows` → Stop OWS spam",
    "",
    "─── 〔 GLOBAL STOP 〕 ───",
    "",
    "  ▸ `.stopallspray` → Stop ALL sprays",
    "",
], footer=menu_footer(".menu3"))


# ─── MENU 4: Protection ──────────────────────────────────────────
MENU_4 = build_box("🛡️ PROTECTION", [
    "",
    "─── 〔 ANTI-DELETE 〕 ───",
    "",
    "  ▸ `.antidel on/off` → Toggle",
    "  ▸ `.antidel` → Status",
    "",
    "─── 〔 WATCHSPAM 〕 ───",
    "",
    "  ▸ `.watchspam`   → Add watch",
    "  ▸ `.unwatchspam` → Remove watch",
    "  ▸ `.watchlist`   → Active watches",
    "",
    "─── 〔 AUTO REACT 〕 ───",
    "",
    "  ▸ `.ar`       → Set auto-react",
    "  ▸ `.sar`      → Disable",
    "  ▸ `.react`    → React to target",
    "  ▸ `.unreact`  → Remove react",
    "  ▸ `.reactlist`→ All targets",
    "",
], footer=menu_footer(".menu4"))


# ─── MENU 5: Tools ───────────────────────────────────────────────
MENU_5 = build_box("⚙️ TOOLS & UTILITY", [
    "",
    "─── 〔 TOOLS 〕 ───",
    "",
    "  ▸ `.tts`     → Text-to-Speech",
    "  ▸ `.qrcode`  → Generate QR",
    "  ▸ `.fancy`   → Fancy styles",
    "  ▸ `.style`   → Bold/Italic/Mono",
    "  ▸ `.emoji`   → Add emojis",
    "  ▸ `.calc`    → Calculate",
    "  ▸ `.weather` → Weather info",
    "  ▸ `.ip`      → IP location",
    "  ▸ `.short`   → Shorten URL",
    "  ▸ `.info`    → User info",
    "",
    "─── 〔 ECHO 〕 ───",
    "",
    "  ▸ `.echo` → Echo back text",
    "",
    "─── 〔 MUSIC 〕 ───",
    "",
    "  ▸ `.music`  → Send as voice",
    "  ▸ `.dmusic` → Download MP3",
    "",
    "─── 〔 NOTES 〕 ───",
    "",
    "  ▸ `.notesadd`    → Save note",
    "  ▸ `.noteslist`   → View notes",
    "  ▸ `.notesdelete` → Delete note",
    "",
    "─── 〔 DM SHIELD (Premium) 〕 ───",
    "",
    "  ▸ `.dmshield`   → Toggle shield",
    "  ▸ `.approve`    → Approve DM",
    "  ▸ `.unapprove`  → Remove approval",
    "  ▸ `.unblock`    → Unblock user",
    "  ▸ `.blockedlist`→ List blocked",
    "",
    "─── 〔 OWNER/ADMIN 〕 ───",
    "",
    "  ▸ `.copy`   → Clone profile",
    "  ▸ `.normal` → Restore original",
    "  ▸ `.banner` → Set menu banner",
    "  ▸ `.rembanner` → Remove banner",
    "  ▸ `.nc`     → Name Changer",
    "",
], footer=menu_footer(".menu5"))


# ─── MENU 6: Send & Tag ─────────────────────────────────────────
MENU_6 = build_box("📨 SEND & TAG", [
    "",
    "─── 〔 SEND MESSAGE 〕 ───",
    "",
    "  ▸ `.send @user <msg>` → Direct msg",
    "",
    "─── 〔 TAG MULTIPLE 〕 ───",
    "",
    "  ▸ `.tag @user1 msg1 @user2 msg2 ...`",
    "",
    "─── 〔 BASIC 〕 ───",
    "",
    "  ▸ `.ping`   → Check latency",
    "  ▸ `.status` → Bot status",
    "  ▸ `.id`     → User & chat ID",
    "  ▸ `.bclist` → Broadcast count",
    "",
], footer=menu_footer(".menu6"))


# ─── MENU 7: Fun Meters ─────────────────────────────────────────
MENU_7 = build_box("🎭 FUN METERS", [
    "",
    "─── 〔 % METERS 〕 ───",
    "",
    "  ▸ `.studmeter`  → Stud %",
    "  ▸ `.looks`      → Looks %",
    "  ▸ `.gay`        → Gay %",
    "  ▸ `.lesbian`    → Lesbian %",
    "  ▸ `.straight`   → Straight %",
    "  ▸ `.bi`         → Bi %",
    "  ▸ `.trans`      → Trans %",
    "  ▸ `.simp`       → Simp %",
    "  ▸ `.chad`       → Chad %",
    "  ▸ `.friendly`   → Friendly %",
    "  ▸ `.stupidmeter`→ Stupid %",
    "  ▸ `.sigma`      → Sigma %",
    "  ▸ `.pookie`     → Pookie %",
    "  ▸ `.baddie`     → Baddie %",
    "",
    "─── 〔 SCORE METERS 〕 ───",
    "",
    "  ▸ `.rizz` → Rizz (1-100)",
    "  ▸ `.iq`   → IQ (1-200)",
    "",
    "─── 〔 RELATIONSHIP 〕 ───",
    "",
    "  ▸ `.bestfrnd` → Ask best friend",
    "  ▸ `.marriage` → Propose",
    "  ▸ `.divorce`  → Ask divorce",
    "",
], footer=menu_footer(".menu7"))


# ─── MENU 8: Fun Raids ──────────────────────────────────────────
MENU_8 = build_box("🎯 FUN RAIDS", [
    "",
    "─── 〔 SHAYARI RAID 〕 ───",
    "  ▸ `.shayariraid`  •  `.sshayariraid`",
    "",
    "─── 〔 RIZZ RAID 〕 ───",
    "  ▸ `.rizzraid`  •  `.srizzraid`",
    "",
    "─── 〔 PICKUP RAID 〕 ───",
    "  ▸ `.pickupraid`  •  `.spickupraid`",
    "",
    "─── 〔 ROMANCE RAID 〕 ───",
    "  ▸ `.romanceraid`  •  `.sromanceraid`",
    "",
    "─── 〔 TROLL RAID 〕 ───",
    "  ▸ `.trollraid`  •  `.strollraid`",
    "",
    "─── 〔 RAGEBAIT RAID 〕 ───",
    "  ▸ `.ragebaitraid`  •  `.sragebaitraid`",
    "",
    "─── 〔 ROAST RAID 〕 ───",
    "  ▸ `.roastraid`  •  `.sroastraid`",
    "",
], footer="💡 Usage: .<raid> @user <count> • .s<raid> @user to stop")


# ─── MENU 9: Non-Abusive Raids ──────────────────────────────────
MENU_9 = build_box("💢 NON-ABUSIVE RAIDS", [
    "",
    "─── 〔 ATTACK 〕 ───",
    "  ▸ `.attackraid`  •  `.sattackraid`",
    "",
    "─── 〔 WAR 〕 ───",
    "  ▸ `.warraid`  •  `.swarraid`",
    "",
    "─── 〔 SAVAGE 〕 ───",
    "  ▸ `.savageraid`  •  `.ssavageraid`",
    "",
    "─── 〔 ULTRA 〕 ───",
    "  ▸ `.ultraraid`  •  `.sultraraid`",
    "",
    "─── 〔 SHAME 〕 ───",
    "  ▸ `.shameraid`  •  `.sshameraid`",
    "",
    "─── 〔 DISS 〕 ───",
    "  ▸ `.dissraid`  •  `.sdissraid`",
    "",
    "─── 〔 DEVIL 〕 ───",
    "  ▸ `.devilraid`  •  `.sdevilraid`",
    "",
    "─── 〔 KARMA 〕 ───",
    "  ▸ `.karmaraid`  •  `.skarmaraid`",
    "",
    "─── 〔 DOOM 〕 ───",
    "  ▸ `.doomraid`  •  `.sdoomraid`",
    "",
], footer="💡 Usage: .<raid> @user <count> • .s<raid> @user to stop")


# ─── MENU 10: Games & Fun ───────────────────────────────────────
MENU_10 = build_box("🎮 GAMES & FUN", [
    "",
    "─── 〔 TRUTH/DARE/SITUATION 〕 ───",
    "",
    "  ▸ `.truth`     → Random truth",
    "  ▸ `.dare`      → Random dare",
    "  ▸ `.situation` → Random situation",
    "",
    "─── 〔 RIDDLE & QUIZ (60s timer) 〕 ───",
    "",
    "  ▸ `.riddle` → Paheli with timer",
    "  ▸ `.quiz`   → JEE/NEET/GK quiz",
    "",
    "─── 〔 RPS (Rock-Paper-Scissors) 〕 ───",
    "",
    "  ▸ `.rps r/p/s` → Play RPS",
    "",
    "─── 〔 TIC-TAC-TOE 〕 ───",
    "",
    "  ▸ `.ttt`       → Start game",
    "  ▸ `.ttt_move`  → Make a move",
    "",
    "─── 〔 DICE / FLIP 〕 ───",
    "",
    "  ▸ `.dice` → Roll dice",
    "  ▸ `.flip` → Flip coin",
    "",
    "─── 〔 JOKE / FACT / COMPLIMENT / QUOTE 〕 ───",
    "",
    "  ▸ `.joke`       → Random joke",
    "  ▸ `.fact`       → Interesting fact",
    "  ▸ `.compliment` → Compliment",
    "  ▸ `.quote`      → Quote",
    "",
], footer=menu_footer(".menu10"))


# ─── MENU 11A: Premium Part A ──────────────────────────────────
MENU_11A = build_box("✨ PREMIUM PART A", [
    "",
    "─── 〔 TEXT FORMATTING 〕 ───",
    "",
    "  ▸ `.upper`    → Uppercase",
    "  ▸ `.lower`    → Lowercase",
    "  ▸ `.reverse`  → Reverse text",
    "  ▸ `.len`      → Char count",
    "  ▸ `.wcount`   → Word count",
    "  ▸ `.bold`     → Bold",
    "  ▸ `.italic`   → Italic",
    "  ▸ `.mono`     → Monospace",
    "  ▸ `.camel`    → camelCase",
    "  ▸ `.repeat`   → Repeat N times",
    "  ▸ `.big`      → Big text",
    "  ▸ `.small`    → Small text",
    "  ▸ `.shadow`   → Shadow text",
    "  ▸ `.zalgo`    → Zalgo effect",
    "  ▸ `.leet`     → Leet speak",
    "",
    "─── 〔 UTILITY 〕 ───",
    "",
    "  ▸ `.hex`       → Hex encode",
    "  ▸ `.octal`     → Octal encode",
    "  ▸ `.ascii`     → ASCII codes",
    "  ▸ `.nato`      → NATO phonetic",
    "  ▸ `.palindrome`→ Check palindrome",
    "  ▸ `.vowels`    → Count vowels",
    "  ▸ `.wordfreq`  → Word frequency",
    "  ▸ `.charcount` → Chars (spaces)",
    "  ▸ `.lettercount`→ Letters (no spaces)",
    "  ▸ `.charinfo`  → Unicode info",
    "",
    "─── 〔 STYLISH TEXT 〕 ───",
    "",
    "  ▸ `.titlecase`   → Title Case",
    "  ▸ `.snake`       → snake_case",
    "  ▸ `.shout`       → SHOUT IT!",
    "  ▸ `.mock`        → mOcKiNg",
    "  ▸ `.spaceit`     → S p a c e d",
    "  ▸ `.removespaces`→ Remove spaces",
    "  ▸ `.clap`        → 👏 Clap 👏",
    "  ▸ `.mirror`      → Mirror text",
    "  ▸ `.flip_text`   → Flip upside down",
    "",
], footer=menu_footer(".menu11a"))


# ─── MENU 11B: Premium Part B ──────────────────────────────────
MENU_11B = build_box("🌟 PREMIUM PART B", [
    "",
    "─── 〔 TYPING EFFECT 〕 ───",
    "",
    "  ▸ `.typing bold`    → Bold style",
    "  ▸ `.typing italic`  → Italic style",
    "  ▸ `.typing double`  → Double struck",
    "  ▸ `.typing script`  → Script style",
    "  ▸ `.typing mono`    → Monospace",
    "  ▸ `.typing circle`  → Circled letters",
    "  ▸ `.typing square`  → Squared letters",
    "  ▸ `.typing <text>`  → Bold (default)",
    "",
    "─── 〔 MATH & FUNCTIONS 〕 ───",
    "",
    "  ▸ `.bmi`       → BMI calculator",
    "  ▸ `.age`       → Age from DOB",
    "  ▸ `.prime`     → Check prime",
    "  ▸ `.factorial` → Factorial",
    "  ▸ `.fibonacci` → Fibonacci seq",
    "  ▸ `.square`    → Square number",
    "  ▸ `.roman`     → Roman numeral",
    "  ▸ `.table`     → Multiplication",
    "  ▸ `.percentage`→ Calculate %",
    "  ▸ `.number`    → Number properties",
    "  ▸ `.countdown` → Countdown timer",
    "",
    "─── 〔 ENCRYPTION & HASH 〕 ───",
    "",
    "  ▸ `.encrypt`   → Caesar cipher",
    "  ▸ `.decrypt`   → Decrypt Caesar",
    "  ▸ `.sha1`      → SHA-1 hash",
    "  ▸ `.sha512`    → SHA-512 hash",
    "",
    "─── 〔 FUN GAMES 〕 ───",
    "",
    "  ▸ `.coin`    → Flip a coin",
    "  ▸ `.lucky`   → Lucky number",
    "  ▸ `.roll`    → Roll a dice",
    "  ▸ `.timer`   → Set a timer",
    "  ▸ `.typetest`→ Typing speed",
    "",
    "─── 〔 OTHER PREMIUM 〕 ───",
    "",
    "  ▸ `.afk`           → Set AFK",
    "  ▸ `.afk off`       → Remove AFK",
    "  ▸ `.premiumstatus` → Check status",
    "  ▸ `.protect`       → Protect cmd",
    "  ▸ `.unprotect`     → Remove protect",
    "  ▸ `.protectlist`   → List protected",
    "",
], footer=menu_footer(".menu11b"))


# ─── MENU 12: Protection & Premium ──────────────────────────────
MENU_12 = build_box("🔰 PROTECTION & PREMIUM", [
    "",
    "─── 〔 DM SHIELD (Premium) 〕 ───",
    "",
    "  ▸ `.dmshield on/off` → Toggle",
    "  ▸ `.approve @user`   → Approve DM",
    "  ▸ `.unapprove @user` → Remove",
    "  ▸ `.unblock @user`   → Unblock",
    "  ▸ `.blockedlist`     → List blocked",
    "  ▸ `.block @user`     → Block user",
    "",
    "─── 〔 GOD PROTECTION 〕 ───",
    "",
    "  ▸ `.godprotection` → Status/Help",
    "",
    "─── 〔 AUTO-REPLY & FILTERS 〕 ───",
    "",
    "  ▸ `.setautoreply`  → Set auto-reply",
    "  ▸ `.delautoreply`  → Remove",
    "  ▸ `.filter`        → Add filter",
    "  ▸ `.delfilter`     → Remove filter",
    "  ▸ `.listfilters`   → All filters",
    "",
    "─── 〔 SANGMATA (Name History) 〕 ───",
    "",
    "  ▸ `.sangmata`    → Show history",
    "  ▸ `.tracknames`  → Auto track (on/off)",
    "",
], footer=menu_footer(".menu12"))


# ─── MENU 13: Premium Raids ────────────────────────────────────
MENU_13 = build_box("💥 PREMIUM RAIDS", [
    "",
    "─── 〔 START/STOP 〕 ───",
    "",
    "  ▸ `.mr`   •  `.smr`   → Raid 1",
    "  ▸ `.mr2`  •  `.smr2`  → Raid 2",
    "  ▸ `.br`   •  `.sbr`   → Raid 3",
    "  ▸ `.br2`  •  `.sbr2`  → Raid 4",
    "  ▸ `.br3`  •  `.sbr3`  → Raid 5",
    "  ▸ `.sqr`  •  `.ssqr`  → Raid 6",
    "  ▸ `.sq2`  •  `.ssq2`  → Raid 7",
    "  ▸ `.cr`   •  `.scr`   → Raid 8",
    "  ▸ `.bar`  •  `.sbar`  → Raid 9",
    "  ▸ `.gr`   •  `.sgr`   → Raid 10",
    "",
], footer=menu_footer(".menu13"))


# ─── MENU 14: Premium Spam ─────────────────────────────────────
MENU_14 = build_box("🔥 PREMIUM SPAM", [
    "",
    "─── 〔 START/STOP 〕 ───",
    "",
    "  ▸ `.ms`   •  `.sms`   → Spam 1",
    "  ▸ `.ms2`  •  `.sms2`  → Spam 2",
    "  ▸ `.bs`   •  `.sbs`   → Spam 3",
    "  ▸ `.bs2`  •  `.sbs2`  → Spam 4",
    "  ▸ `.bs3`  •  `.sbs3`  → Spam 5",
    "  ▸ `.sqs`  •  `.ssqs`  → Spam 6",
    "  ▸ `.sqs2` •  `.ssqs2` → Spam 7",
    "  ▸ `.cs`   •  `.scs`   → Spam 8",
    "  ▸ `.bas`  •  `.sbas`  → Spam 9",
    "  ▸ `.gs`   •  `.sgs`   → Spam 10",
    "",
], footer=menu_footer(".menu14"))


# ─── MAP: command -> menu string ──
MENU_MAP = {
    "menu": MENU_MAIN,
    "menu1": MENU_1,
    "menu2": MENU_2,
    "menu3": MENU_3,
    "menu4": MENU_4,
    "menu5": MENU_5,
    "menu6": MENU_6,
    "menu7": MENU_7,
    "menu8": MENU_8,
    "menu9": MENU_9,
    "menu10": MENU_10,
    "menu11a": MENU_11A,
    "menu11b": MENU_11B,
    "menu12": MENU_12,
    "menu13": MENU_13,
    "menu14": MENU_14,
}


# ═══════════════════════════════════════════════════════════════════════
# SECTION 10: SHUTDOWN HANDLER
# ═══════════════════════════════════════════════════════════════════════

async def shutdown_handler(sig, frame):
    print("🛑 Shutting down...")
    for uid in list(broadcast_users):
        try:
            await MAIN_BOT_CLIENT.send_message(uid, "⚠️ Bot is going offline for maintenance.\nWe'll be back soon!")
            await asyncio.sleep(0.5)
        except:
            pass
    for uid, client in list(active_userbots.items()):
        try:
            await client.disconnect()
        except:
            pass
    for task in list(running_tasks):
        if not task.done():
            task.cancel()
            try:
                await asyncio.shield(task)
            except:
                pass
    await MAIN_BOT_CLIENT.disconnect()
    sys.exit(0)


signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown_handler(s, f)))
signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown_handler(s, f)))


# ═══════════════════════════════════════════════════════════════════════
# SECTION 11: MAIN BOT HANDLERS
# ═══════════════════════════════════════════════════════════════════════

# ─── /start ──────────────────────────────────────────────────────
@MAIN_BOT_CLIENT.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    user_id = event.sender_id
    add_to_broadcast_json(user_id)
    broadcast_users.add(user_id)

    try:
        async with db_pool.acquire() as conn:
            await conn.execute("INSERT INTO broadcast_users (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
    except:
        pass

    buttons = [
        [KeyboardButtonCallback("💎 Buy Premium", data="buy_menu")],
        [KeyboardButtonCallback("💰 Deposit / Check Balance", data="deposit")],
        [KeyboardButtonUrl("🔗 Premium Features", url=PREMIUM_FEATURES_LINK)],
    ]

    bal = await get_balance(user_id)
    intro = (
        "╔═══════════════════════════════════════════╗\n"
        "║  ✦ 👑 ⚡️ZYЯΣX ✕ ΛΣƬΉΣЯ⚡️ 𝐀𝐔𝐓𝐎-𝐃𝐄𝐏𝐋𝐎𝐘 👑 ✦  ║\n"
        "╚═══════════════════════════════════════════╝\n\n"
        f"Welcome to the **Ultimate Userbot Manager**.\n"
        f"• To start your personal userbot, type `/login`\n"
        f"• To stop it, use `/logout`\n"
        f"• Use the buttons below to buy premium or deposit.\n\n"
        f"💰 **Your Wallet Balance:** ₹{bal:.2f}\n\n"
        "Enjoy the premium experience! 🚀"
    )
    await safe_reply(event, intro, buttons=buttons)

    # ── Check channels ──
    not_joined = []
    for ch in REQUIRED_CHANNELS:
        if not await is_user_in_channel(MAIN_BOT_CLIENT, user_id, ch):
            not_joined.append(ch)

    if not_joined:
        msg = (
            "⚠️═══⟦ ꜰᴏʀᴄᴇ ᴊᴏɪɴ ʀᴇqᴜɪʀᴇᴅ ⟧═══⚠️\n\n"
            "✧➤ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀʟʟ 4 ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ᴡᴀɪᴛ ꜰᴏʀ ᴀᴘᴘʀᴏᴠᴀʟ ɪꜰ ɴᴇᴇᴅᴇᴅ.\n"
            "✧➤ ᴀꜰᴛᴇʀ ᴀᴘᴘʀᴏᴠᴀʟ, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴠᴇʀɪꜰʏ.\n"
            "❀═════════════════════════════❀"
        )
        await safe_respond(event, msg, buttons=get_join_buttons())


# ─── Channel verification callback ──────────────────────────────
@MAIN_BOT_CLIENT.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()

    if data == "verify_channels":
        user_id = event.sender_id
        not_joined = []
        for ch in REQUIRED_CHANNELS:
            if not await is_user_in_channel(MAIN_BOT_CLIENT, user_id, ch):
                not_joined.append(ch)

        if not_joined:
            msg = "⚠️ **You have not joined all required channels.**\n\nPlease join the following channels:\n\n"
            for ch in not_joined:
                msg += f"• {ch['name']}: {ch['invite']}\n"
            msg += "\n❀═════════════════════════════❀"
            await safe_edit(event, msg, buttons=get_join_buttons())
            await event.answer("Please join all channels first.", alert=True)
            return

        try:
            await safe_edit(event, "✅ **All channels verified!**\n\n📱 Now send your phone number (with country code).")
        except MessageNotModifiedError:
            pass

        user_states[user_id] = {"step": "NUMBER"}
        await safe_respond(event, "📱 **Step 1:** Send your phone number with country code.\nExample: `+919876543210`")
        await event.answer("Verified! Now send your number.")
        return


# ═══════════════════════════════════════════════════════════════════════
# SECTION 12: MAIN EVENT LOOP — MENU COMMAND DISPATCHER
# ═══════════════════════════════════════════════════════════════════════

@MAIN_BOT_CLIENT.on(events.NewMessage)
async def menu_dispatcher(event):
    """Handle .menu, .menu1, .menu2, ... .menu14 commands for MAIN BOT."""
    if not event.is_private:
        return

    text = event.raw_text.strip().lower() if event.raw_text else ""

    # ── Show menu in main bot (for users to see what's available) ──
    if text in MENU_MAP:
        # Check premium if needed
        if text in ("menu11a", "menu11b", "menu13", "menu14"):
            prem = await check_premium_status(event.sender_id)
            if not prem:
                await safe_reply(event, "❌ Premium only. Buy with `/buy` in main bot.")
                return

        await safe_reply(event, MENU_MAP[text])
        return


# ═══════════════════════════════════════════════════════════════════════
# SECTION 13: MENU COMMAND REGISTRATION (for USERBOT)
# ═══════════════════════════════════════════════════════════════════════

def register_userbot_menus(user_bot):
    """Register all .menu .menu1-14 commands on the userbot."""

    @user_bot.on(events.NewMessage(pattern=r"\.menu\b"))
    async def userbot_menu(event):
        await safe_edit(event, MENU_MAIN)

    @user_bot.on(events.NewMessage(pattern=r"\.menu1\b"))
    async def userbot_menu1(event):
        await safe_edit(event, MENU_1)

    @user_bot.on(events.NewMessage(pattern=r"\.menu2\b"))
    async def userbot_menu2(event):
        await safe_edit(event, MENU_2)

    @user_bot.on(events.NewMessage(pattern=r"\.menu3\b"))
    async def userbot_menu3(event):
        await safe_edit(event, MENU_3)

    @user_bot.on(events.NewMessage(pattern=r"\.menu4\b"))
    async def userbot_menu4(event):
        await safe_edit(event, MENU_4)

    @user_bot.on(events.NewMessage(pattern=r"\.menu5\b"))
    async def userbot_menu5(event):
        await safe_edit(event, MENU_5)

    @user_bot.on(events.NewMessage(pattern=r"\.menu6\b"))
    async def userbot_menu6(event):
        await safe_edit(event, MENU_6)

    @user_bot.on(events.NewMessage(pattern=r"\.menu7\b"))
    async def userbot_menu7(event):
        await safe_edit(event, MENU_7)

    @user_bot.on(events.NewMessage(pattern=r"\.menu8\b"))
    async def userbot_menu8(event):
        await safe_edit(event, MENU_8)

    @user_bot.on(events.NewMessage(pattern=r"\.menu9\b"))
    async def userbot_menu9(event):
        await safe_edit(event, MENU_9)

    @user_bot.on(events.NewMessage(pattern=r"\.menu10\b"))
    async def userbot_menu10(event):
        await safe_edit(event, MENU_10)

    @user_bot.on(events.NewMessage(pattern=r"\.menu11a\b"))
    async def userbot_menu11a(event):
        if not await check_premium_status(event.sender_id):
            await safe_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
            return
        await safe_edit(event, MENU_11A)

    @user_bot.on(events.NewMessage(pattern=r"\.menu11b\b"))
    async def userbot_menu11b(event):
        if not await check_premium_status(event.sender_id):
            await safe_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
            return
        await safe_edit(event, MENU_11B)

    @user_bot.on(events.NewMessage(pattern=r"\.menu12\b"))
    async def userbot_menu12(event):
        if not await check_premium_status(event.sender_id):
            await safe_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
            return
        await safe_edit(event, MENU_12)

    @user_bot.on(events.NewMessage(pattern=r"\.menu13\b"))
    async def userbot_menu13(event):
        if not await check_premium_status(event.sender_id):
            await safe_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
            return
        await safe_edit(event, MENU_13)

    @user_bot.on(events.NewMessage(pattern=r"\.menu14\b"))
    async def userbot_menu14(event):
        if not await check_premium_status(event.sender_id):
            await safe_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
            return
        await safe_edit(event, MENU_14)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 14: REMAINING BOT COMMANDS (LOGIN, LOGOUT, BUY, ETC.)
# ═══════════════════════════════════════════════════════════════════════

# ─── /login ──
@MAIN_BOT_CLIENT.on(events.NewMessage(pattern="/login"))
async def login_handler(event):
    if not event.is_private:
        return
    user_id = event.sender_id

    not_joined = []
    for ch in REQUIRED_CHANNELS:
        if not await is_user_in_channel(MAIN_BOT_CLIENT, user_id, ch):
            not_joined.append(ch)

    if not_joined:
        msg = "⚠️═══⟦ ꜰᴏʀᴄᴇ ᴊᴏɪɴ ʀᴇqᴜɪʀᴇᴅ ⟧═══⚠️\n\n"
        for ch in not_joined:
            msg += f"✧➤ {ch['name']} ({ch['invite']}) – Please send join request & wait for approval.\n"
        msg += "\n❀═════════════════════════════❀"
        await safe_reply(event, msg, buttons=get_join_buttons())
        return

    user_states[user_id] = {"step": "NUMBER"}
    await safe_reply(event, "📱 **Step 1:** Please send your Telegram phone number **with country code**.\nExample: `+919876543210`")


# ─── Phone number handler ──
@MAIN_BOT_CLIENT.on(events.NewMessage)
async def handle_login_phone(event):
    if not event.is_private:
        return
    if event.raw_text and event.raw_text.startswith('/'):
        return
    user_id = event.sender_id
    state = user_states.get(user_id)
    if not state or state.get("step") != "NUMBER":
        return

    phone = re.sub(r'[\s\-\(\)]', '', event.raw_text.strip())
    if not re.match(r'^\+?\d{10,15}$', phone):
        await safe_reply(event, "❌ Invalid phone. Send with country code, e.g., `+919876543210`")
        return

    try:
        temp_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_client.connect()
        await temp_client.send_code_request(phone)
        user_states[user_id] = {"step": "CODE", "phone": phone, "temp_client": temp_client}
        await safe_reply(event, "📨 **Code sent!** Send the numeric code (e.g., `12345`).")
    except ValueError as e:
        await safe_reply(event, f"❌ Invalid phone: {e}")
        user_states.pop(user_id, None)
    except FloodWaitError as e:
        await safe_reply(event, f"⏳ Wait {e.seconds}s and try again.")
        user_states.pop(user_id, None)
    except Exception as e:
        await safe_reply(event, f"❌ Error: {e}")
        user_states.pop(user_id, None)


# ─── Code handler ──
@MAIN_BOT_CLIENT.on(events.NewMessage)
async def handle_login_code(event):
    if not event.is_private:
        return
    if event.raw_text and event.raw_text.startswith('/'):
        return
    user_id = event.sender_id
    state = user_states.get(user_id)
    if not state or state.get("step") != "CODE":
        return

    code = event.raw_text.strip().replace(" ", "").replace("-", "")
    if not code.isdigit():
        await safe_reply(event, "❌ Send only the numeric code.")
        return

    temp_client = state.get("temp_client")
    phone = state.get("phone")
    if not temp_client:
        await safe_reply(event, "❌ Session expired. Start again with `/login`.")
        user_states.pop(user_id, None)
        return

    try:
        await temp_client.sign_in(phone, code=code)
        session_str = temp_client.session.save()
        await save_session(user_id, session_str)
        task = asyncio.create_task(run_user_bot_with_restart(session_str, user_id))
        task.set_name(f"userbot_restart_{user_id}")
        running_tasks.add(task)
        task.add_done_callback(running_tasks.discard)

        # Notify owners
        try:
            user_entity = await MAIN_BOT_CLIENT.get_entity(user_id)
            uname = f"@{user_entity.username}" if user_entity.username else "No username"
            phone_display = phone[:3] + "***" + phone[-3:] if len(phone) > 6 else phone
            for owner in MY_OWNER_IDS:
                await MAIN_BOT_CLIENT.send_message(owner, f"🔐 Login\n👤 {user_entity.first_name}\n🆔 {user_id}\n📱 {phone_display}\n🔗 {uname}")
        except:
            pass

        await safe_reply(event, "✅ **Userbot started!**\nType `.menu` to see commands.")
        user_states.pop(user_id, None)
        await temp_client.disconnect()

    except SessionPasswordNeededError:
        state["step"] = "PASSWORD"
        await safe_reply(event, "🔐 **2FA enabled.** Send your password.")
    except FloodWaitError as e:
        await safe_reply(event, f"⏳ Wait {e.seconds}s.")
    except Exception as e:
        if "invalid code" in str(e).lower():
            await safe_reply(event, "❌ **Invalid code.** Try again.")
        else:
            await safe_reply(event, f"❌ Login failed: {e}")
            user_states.pop(user_id, None)


# ─── 2FA password handler ──
@MAIN_BOT_CLIENT.on(events.NewMessage)
async def handle_login_password(event):
    if not event.is_private:
        return
    if event.raw_text and event.raw_text.startswith('/'):
        return
    user_id = event.sender_id
    state = user_states.get(user_id)
    if not state or state.get("step") != "PASSWORD":
        return

    password = event.raw_text.strip()
    temp_client = state.get("temp_client")
    if not temp_client:
        await safe_reply(event, "❌ Session expired. Use `/login` again.")
        user_states.pop(user_id, None)
        return

    try:
        await temp_client.sign_in(password=password)
        session_str = temp_client.session.save()
        await save_session(user_id, session_str)
        task = asyncio.create_task(run_user_bot_with_restart(session_str, user_id))
        task.set_name(f"userbot_restart_{user_id}")
        running_tasks.add(task)
        task.add_done_callback(running_tasks.discard)

        await safe_reply(event, "✅ **Userbot started!**\nType `.menu` to see commands.")
        user_states.pop(user_id, None)
        await temp_client.disconnect()

    except Exception as e:
        if "password" in str(e).lower():
            await safe_reply(event, "❌ **Incorrect password.** Try again.")
        else:
            await safe_reply(event, f"❌ Login failed: {e}")
            user_states.pop(user_id, None)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 15: USERBOT LAUNCHER (with restart loop)
# ═══════════════════════════════════════════════════════════════════════

async def run_user_bot_with_restart(session_string, chat_id):
    """Launch userbot with crash recovery and restart logic."""
    restart_count = 0
    last_restart_time = 0
    session_invalid_notified = False

    while True:
        try:
            await run_user_bot(session_string, chat_id)
            break  # Normal exit
        except FloodWaitError as e:
            wait = e.seconds + 1
            print(f"⏳ FloodWait {wait}s")
            try:
                await MAIN_BOT_CLIENT.send_message(chat_id, f"⚠️ Flood limit. Wait {wait//60}m {wait%60}s.")
            except:
                pass
            await asyncio.sleep(wait)
            restart_count = 0
            session_invalid_notified = False

        except (UnauthorizedError, ValueError, RPCError) as e:
            error_msg = str(e)
            if "SESSION_INVALID" in error_msg or "invalid" in error_msg.lower():
                if not session_invalid_notified:
                    session_invalid_notified = True
                    try:
                        await MAIN_BOT_CLIENT.send_message(chat_id, "⚠️ Session expired. Use `/login` again.")
                    except:
                        pass
                try:
                    if chat_id in active_userbots:
                        await active_userbots[chat_id].disconnect()
                        del active_userbots[chat_id]
                except:
                    pass
                user_sessions.pop(chat_id, None)
                await delete_session(chat_id)
                break

        except AuthKeyDuplicatedError:
            print(f"🔴 AuthKey duplicated for {chat_id}. Stopping restarts.")
            try:
                await MAIN_BOT_CLIENT.send_message(chat_id, "⚠️ Session used from 2 places. Use `/login` again.")
            except:
                pass
            if chat_id in active_userbots:
                try:
                    await active_userbots[chat_id].disconnect()
                except:
                    pass
                del active_userbots[chat_id]
            user_sessions.pop(chat_id, None)
            await delete_session(chat_id)
            break

        except asyncio.CancelledError:
            break

        except Exception as e:
            error_msg = str(e)
            now = time.time()

            if any(x in error_msg for x in ["EOF", "input", "interactive"]):
                print(f"🚫 Invalid session (EOF) for {chat_id}. Stopping.")
                try:
                    await MAIN_BOT_CLIENT.send_message(chat_id, "⚠️ Session expired. Use `/login` again.")
                except:
                    pass
                try:
                    if chat_id in active_userbots:
                        await active_userbots[chat_id].disconnect()
                        del active_userbots[chat_id]
                except:
                    pass
                user_sessions.pop(chat_id, None)
                await delete_session(chat_id)
                break

            if restart_count >= 5 and (now - last_restart_time) < 60:
                print(f"⚠️ Too many restarts for {chat_id}. Waiting 60s.")
                await asyncio.sleep(60)
                restart_count = 0

            restart_count += 1
            last_restart_time = now
            print(f"⚠️ Crashed: {error_msg[:80]}. Restart #{restart_count}")
            await asyncio.sleep(5)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 16: USERBOT ENGINE — ALL COMMANDS (FULL IMPLEMENTATION)
# ═══════════════════════════════════════════════════════════════════════

async def run_user_bot(session_string, chat_id):
    user_bot = None
    try:
        user_bot = TelegramClient(
            StringSession(session_string), API_ID, API_HASH,
            auto_reconnect=False, connection_retries=2
        )
        await user_bot.start()
        active_userbots[chat_id] = user_bot

        me = await user_bot.get_me()
        OWNER_IDS = {me.id}
        BOT_ID = (await MAIN_BOT_CLIENT.get_me()).id

        # ── Register menu commands ──
        register_userbot_menus(user_bot)

        # ── State ──
        state = type('State', (), {})()
        state.admins = set()
        state.muted = set()
        state.gmuted = set()
        state.reply_on = set()
        state.rr_on = set()
        state.flag_on = set()
        state.hrr_on = set()
        state.replygod_on = set()
        state.deathgod_on = {}
        state.custom_raid = {}
        state.group_locks = set()
        state.spray_tasks = {}
        state.spray_delay = 0.10
        state.notes = {}
        state.nc_state = {"active": False, "task": None, "lang": "hindi", "texts": []}
        state.clone_active = False
        state.clone_data = {"name": None, "bio": None, "photo": None}
        state.cloned_bot_id = None
        state.auto_react = None
        state.antidel_on = False
        state.antidel_map = {}
        state.watch_map = {}
        state.afk_data = {}
        state.dm_shield = False
        state.god_protection = False
        state.dm_approved = set()
        state.dm_blocked = set()
        state.filter_map = {}
        state.start_time = time.time()

        # Raid states
        state.shayari_raid = {}
        state.rizz_raid = {}
        state.pickup_raid = {}
        state.romance_raid = {}
        state.troll_raid = {}
        state.ragebait_raid = {}
        state.roast_raid = {}
        state.attack_raid = {}
        state.war_raid = {}
        state.savage_raid = {}
        state.ultra_raid = {}
        state.shame_raid = {}
        state.diss_raid = {}
        state.devil_raid = {}
        state.karma_raid = {}
        state.doom_raid = {}
        state.pwr_raid = {}
        state.ows_spam = {}
        state.premium_raid_tgts = {}
        state.premium_spam_tgts = {}

        user_bot.state = state

        # ═══════════════════════════════════════════════════════════════════
        # HELPERS
        # ═══════════════════════════════════════════════════════════════════

        async def s_edit(event, text, **kw):
            try:
                if event.is_channel and not event.is_group:
                    return await event.reply(text, **kw)
                m = await event.edit(text, **kw) if hasattr(event, 'edit') else await event.reply(text, **kw)
                return m
            except MessageNotModifiedError:
                pass
            except:
                try:
                    return await event.reply(text, **kw)
                except:
                    pass

        async def s_send(chat, text, reply_to=None, **kw):
            try:
                return await user_bot.send_message(chat, text, reply_to=reply_to, **kw)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 1)
                return await user_bot.send_message(chat, text, reply_to=reply_to, **kw)
            except:
                return None

        async def get_targets(event, arg):
            t = set()
            if event.is_reply:
                try:
                    r = await event.get_reply_message()
                    if r and r.sender_id and r.sender_id not in (me.id, BOT_ID):
                        t.add(int(r.sender_id))
                except:
                    pass
            for x in arg.strip().split():
                x = x.strip()
                if x.isdigit():
                    t.add(int(x))
                else:
                    try:
                        e = await user_bot.get_entity(x)
                        if hasattr(e, 'id') and e.id not in (me.id, BOT_ID):
                            t.add(int(e.id))
                    except:
                        pass
            return t

        def is_owner(uid):
            return uid in OWNER_IDS

        def is_admin(uid):
            return uid in OWNER_IDS or uid in state.admins

        async def is_prem(uid):
            return await check_premium_status(uid) is not None

        def get_random_text(lst):
            return random.choice(lst) if lst else "✨"

        # ── Raid runner ──
        async def run_raid(raid_dict, texts_list, event, arg):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets. Reply to user or give IDs.")
                return
            if not texts_list:
                await s_edit(event, "❌ Text list empty. Admin use `.addtext`.")
                return
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            raid_dict[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"⚔️ Raid `{rid}` started on {len(tgts)} target(s). `.stopraid {rid}` to end.")
            while raid_dict.get(rid, {}).get("active"):
                try:
                    txt = random.choice(texts_list)
                    if isinstance(tgts, set):
                        for uid in tgts:
                            try:
                                await s_send(cid, txt, reply_to=uid)
                            except:
                                pass
                            await asyncio.sleep(state.spray_delay)
                    else:
                        for uid in tgts:
                            try:
                                await s_send(cid, txt, reply_to=uid)
                            except:
                                pass
                            await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.8)
            raid_dict.pop(rid, None)

        # ── Spam runner ──
        async def run_spam(spam_dict, texts_list, event, arg):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not texts_list:
                await s_edit(event, "❌ Text list empty.")
                return
            cid = event.chat_id
            sid = random.randint(1000, 9999)
            spam_dict[sid] = {"targets": tgts, "active": True}
            await s_edit(event, f"💬 Spam `{sid}` started. `.stopspam {sid}` to stop.")
            while spam_dict.get(sid, {}).get("active"):
                try:
                    txt = random.choice(texts_list)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.8)
            spam_dict.pop(sid, None)

        # ═══════════════════════════════════════════════════════════════════
        # 1. REPLY, RR, FLAG, HRR COMMANDS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.reply\b'))
        async def cmd_reply(event):
            if not reply_texts:
                await s_edit(event, "❌ reply_texts is empty.")
                return
            state.reply_on.add(event.chat_id)
            await s_edit(event, "✅ Reply mode ON")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sreply\b'))
        async def cmd_sreply(event):
            state.reply_on.discard(event.chat_id)
            await s_edit(event, "✅ Reply mode OFF")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.rr\b'))
        async def cmd_rr(event):
            if not rr_texts:
                await s_edit(event, "❌ rr_texts is empty.")
                return
            state.rr_on.add(event.chat_id)
            await s_edit(event, "✅ RR mode ON")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.srr\b'))
        async def cmd_srr(event):
            state.rr_on.discard(event.chat_id)
            await s_edit(event, "✅ RR mode OFF")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.flag\b'))
        async def cmd_flag(event):
            if not flag_texts:
                await s_edit(event, "❌ flag_texts is empty.")
                return
            state.flag_on.add(event.chat_id)
            await s_edit(event, "✅ Flag mode ON")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sflag\b'))
        async def cmd_sflag(event):
            state.flag_on.discard(event.chat_id)
            await s_edit(event, "✅ Flag mode OFF")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.hrr\b'))
        async def cmd_hrr(event):
            if not heart_texts:
                await s_edit(event, "❌ heart_texts is empty.")
                return
            state.hrr_on.add(event.chat_id)
            await s_edit(event, "✅ Heart reply ON")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.shrr\b'))
        async def cmd_shrr(event):
            state.hrr_on.discard(event.chat_id)
            await s_edit(event, "✅ Heart reply OFF")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.replygod\b'))
        async def cmd_replygod(event):
            if not replygod_texts:
                await s_edit(event, "❌ replygod_texts is empty.")
                return
            state.replygod_on.add(event.chat_id)
            await s_edit(event, "✅ ReplyGod ON")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sgod\b'))
        async def cmd_sgod(event):
            state.replygod_on.discard(event.chat_id)
            await s_edit(event, "✅ ReplyGod OFF")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.deathgod\b'))
        async def cmd_deathgod(event, arg=""):
            if not deathgod_replies:
                await s_edit(event, "❌ deathgod_replies is empty.")
                return
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            cid = event.chat_id
            did = random.randint(1000, 9999)
            state.deathgod_on[did] = {"targets": tgts, "active": True, "chat": cid}
            await s_edit(event, f"☠️ DeathGod `{did}` started on {len(tgts)} target(s). `.stopdeathgod {did}`")
            while state.deathgod_on.get(did, {}).get("active"):
                try:
                    txt = random.choice(deathgod_replies)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                            await asyncio.sleep(0.3)
                            await s_send(cid, txt, reply_to=uid)
                            await asyncio.sleep(0.3)
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.5)
            state.deathgod_on.pop(did, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sdeathgod\b'))
        async def cmd_sdeathgod(event, arg=""):
            did = arg.strip()
            if did and did.isdigit():
                did = int(did)
                if did in state.deathgod_on:
                    state.deathgod_on[did]["active"] = False
                    await s_edit(event, f"✅ DeathGod `{did}` stopped")
                    return
            # Stop all
            cnt = 0
            for k in list(state.deathgod_on.keys()):
                state.deathgod_on[k]["active"] = False
                cnt += 1
            await s_edit(event, f"✅ All DeathGods ({cnt}) stopped")

        # Auto-reply handler (triggered by any incoming message)
        @user_bot.on(events.NewMessage(incoming=True))
        async def auto_reply_handler(event):
            if not event.message or event.text or not event.sender_id:
                return
            if event.sender_id in (me.id, BOT_ID) or event.sender_id in state.muted or event.sender_id in state.gmuted:
                return
            cid = event.chat_id

            # Reply mode
            if cid in state.reply_on and reply_texts:
                try:
                    txt = random.choice(reply_texts)
                    await event.reply(txt)
                except:
                    pass

            # RR mode
            if cid in state.rr_on and rr_texts:
                try:
                    txt = random.choice(rr_texts)
                    await event.reply(txt)
                except:
                    pass

            # Flag mode
            if cid in state.flag_on and flag_texts:
                try:
                    txt = random.choice(flag_texts)
                    await event.reply(txt)
                except:
                    pass

            # Heart reply
            if cid in state.hrr_on and heart_texts:
                try:
                    txt = random.choice(heart_texts)
                    await event.reply(txt)
                except:
                    pass

            # ReplyGod
            if cid in state.replygod_on and replygod_texts:
                try:
                    txt = random.choice(replygod_texts)
                    await event.reply(txt)
                except:
                    pass

        # ═══════════════════════════════════════════════════════════════════
        # 2. MUTE / GMUTE COMMANDS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.mute\b'))
        async def cmd_mute(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            state.muted.update(tgts)
            await s_edit(event, f"🔇 Muted {len(tgts)} user(s) in this chat.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.unmute\b'))
        async def cmd_unmute(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            state.muted.difference_update(tgts)
            await s_edit(event, f"🔊 Unmuted {len(tgts)} user(s).")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.gmute\b'))
        async def cmd_gmute(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            state.gmuted.update(tgts)
            await s_edit(event, f"🌐 Globally muted {len(tgts)} user(s).")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.gunmute\b'))
        async def cmd_gunmute(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            state.gmuted.difference_update(tgts)
            await s_edit(event, f"🌐 Unmuted {len(tgts)} globally.")

        # ═══════════════════════════════════════════════════════════════════
        # 3. SPRAY COMMANDS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.spray\b'))
        async def cmd_spray(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not reply_texts:
                await s_edit(event, "❌ reply_texts is empty.")
                return
            cid = event.chat_id
            sid = f"spray_{cid}_{random.randint(1000,9999)}"
            state.spray_tasks[sid] = {"active": True, "targets": tgts}
            await s_edit(event, f"🌀 Spray `{sid}` started. `.stopspray {sid}`")
            while state.spray_tasks.get(sid, {}).get("active"):
                try:
                    txt = random.choice(reply_texts)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.5)
            state.spray_tasks.pop(sid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.dspray\b'))
        async def cmd_dspray(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not deathgod_replies:
                await s_edit(event, "❌ deathgod_replies is empty.")
                return
            cid = event.chat_id
            sid = f"dspray_{cid}_{random.randint(1000,9999)}"
            state.spray_tasks[sid] = {"active": True, "targets": tgts}
            await s_edit(event, f"🌀 DeathSpray `{sid}` started. `.stopspray {sid}`")
            while state.spray_tasks.get(sid, {}).get("active"):
                try:
                    txt = random.choice(deathgod_replies)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                            await asyncio.sleep(0.15)
                            await s_send(cid, txt, reply_to=uid)
                            await asyncio.sleep(0.15)
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.3)
            state.spray_tasks.pop(sid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.tspray\b'))
        async def cmd_tspray(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not rr_texts:
                await s_edit(event, "❌ rr_texts is empty.")
                return
            cid = event.chat_id
            sid = f"tspray_{cid}_{random.randint(1000,9999)}"
            state.spray_tasks[sid] = {"active": True, "targets": tgts}
            await s_edit(event, f"🌀 TSpray `{sid}` started. `.stopspray {sid}`")
            while state.spray_tasks.get(sid, {}).get("active"):
                try:
                    txt = random.choice(rr_texts)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.5)
            state.spray_tasks.pop(sid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.rspray\b'))
        async def cmd_rspray(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not replygod_texts:
                await s_edit(event, "❌ replygod_texts is empty.")
                return
            cid = event.chat_id
            sid = f"rspray_{cid}_{random.randint(1000,9999)}"
            state.spray_tasks[sid] = {"active": True, "targets": tgts}
            await s_edit(event, f"🌀 RSpray `{sid}` started. `.stopspray {sid}`")
            while state.spray_tasks.get(sid, {}).get("active"):
                try:
                    txt = random.choice(replygod_texts)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.5)
            state.spray_tasks.pop(sid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.multispray\b'))
        async def cmd_multispray(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            all_texts = reply_texts + rr_texts + flag_texts + heart_texts + replygod_texts
            if not all_texts:
                await s_edit(event, "❌ All text lists empty.")
                return
            cid = event.chat_id
            sid = f"multi_{cid}_{random.randint(1000,9999)}"
            state.spray_tasks[sid] = {"active": True, "targets": tgts}
            await s_edit(event, f"🌀 MultiSpray `{sid}` started. `.stopspray {sid}`")
            while state.spray_tasks.get(sid, {}).get("active"):
                try:
                    txt = random.choice(all_texts)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.5)
            state.spray_tasks.pop(sid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.countspray\b'))
        async def cmd_countspray(event, arg=""):
            parts = arg.strip().split(maxsplit=1)
            count = 10
            targets_arg = arg
            if parts and parts[0].isdigit():
                count = int(parts[0])
                targets_arg = parts[1] if len(parts) > 1 else ""
            tgts = await get_targets(event, targets_arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not reply_texts:
                await s_edit(event, "❌ reply_texts is empty.")
                return
            cid = event.chat_id
            for i in range(min(count, 100)):
                try:
                    txt = random.choice(reply_texts)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.3)
            await s_edit(event, f"✅ CountSpray done ({count}x)")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.stopspray\b'))
        async def cmd_stopspray(event, arg=""):
            sid = arg.strip()
            if sid and sid.startswith("spray_"):
                if sid in state.spray_tasks:
                    state.spray_tasks[sid]["active"] = False
                    await s_edit(event, f"✅ Stopped `{sid}`")
                    return
            # Stop all
            cnt = 0
            for k in list(state.spray_tasks.keys()):
                state.spray_tasks[k]["active"] = False
                cnt += 1
            await s_edit(event, f"✅ All sprays ({cnt}) stopped.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.spraydelay\b'))
        async def cmd_spraydelay(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            try:
                d = float(arg.strip())
                if 0.01 <= d <= 5.0:
                    state.spray_delay = d
                    await s_edit(event, f"✅ Spray delay set to {d}s")
                else:
                    await s_edit(event, "❌ Use 0.01-5.0")
            except:
                await s_edit(event, f"Current delay: {state.spray_delay}s")

        # ═══════════════════════════════════════════════════════════════════
        # 4. CUSTOM RAID
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.customraid\b'))
        async def cmd_customraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not reply_texts:
                await s_edit(event, "❌ reply_texts is empty.")
                return
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.custom_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"⚔️ CustomRaid `{rid}` started. `.stopcustomraid {rid}`")
            while state.custom_raid.get(rid, {}).get("active"):
                try:
                    txt = random.choice(reply_texts)
                    for uid in tgts:
                        try:
                            await s_send(cid, txt, reply_to=uid)
                        except:
                            pass
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.6)
            state.custom_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.stopcustomraid\b'))
        async def cmd_stopcustomraid(event, arg=""):
            rid = arg.strip()
            if rid and rid.isdigit():
                rid = int(rid)
                if rid in state.custom_raid:
                    state.custom_raid[rid]["active"] = False
                    await s_edit(event, f"✅ CustomRaid `{rid}` stopped")
                    return
            cnt = 0
            for k in list(state.custom_raid.keys()):
                state.custom_raid[k]["active"] = False
                cnt += 1
            await s_edit(event, f"✅ All custom raids ({cnt}) stopped.")

        # ═══════════════════════════════════════════════════════════════════
        # 5. FUN RAIDS (Menu8)
        # ═══════════════════════════════════════════════════════════════════

        # Shayari Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.shayariraid\b'))
        async def cmd_shayariraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.shayari_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"🎭 ShayariRaid `{rid}` started. `.stopshayari {rid}`")
            while state.shayari_raid.get(rid, {}).get("active"):
                txt = random.choice(shayari_texts) if shayari_texts else "✨ शायरी"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.shayari_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sshayariraid\b'))
        async def cmd_stopshayari(event, arg=""):
            cnt = 0
            for k in list(state.shayari_raid.keys()):
                state.shayari_raid[k]["active"] = False
                cnt += 1
            await s_edit(event, f"✅ ShayariRaid ({cnt}) stopped.")

        # Rizz Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.rizzraid\b'))
        async def cmd_rizzraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.rizz_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"🔥 RizzRaid `{rid}` started. `.stoprizz {rid}`")
            while state.rizz_raid.get(rid, {}).get("active"):
                txt = random.choice(rizz_texts) if rizz_texts else "✨ Rizz"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.rizz_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.srizzraid\b'))
        async def cmd_stoprizz(event, arg=""):
            for k in list(state.rizz_raid.keys()):
                state.rizz_raid[k]["active"] = False
            await s_edit(event, "✅ RizzRaid stopped.")

        # Pickup Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.pickupraid\b'))
        async def cmd_pickupraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.pickup_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"💘 PickupRaid `{rid}` started. `.stoppinger {rid}`")
            while state.pickup_raid.get(rid, {}).get("active"):
                txt = random.choice(pickup_texts) if pickup_texts else "✨ Pickup"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.pickup_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.spickupraid\b'))
        async def cmd_stoppinger(event, arg=""):
            for k in list(state.pickup_raid.keys()):
                state.pickup_raid[k]["active"] = False
            await s_edit(event, "✅ PickupRaid stopped.")

        # Romance Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.romanceraid\b'))
        async def cmd_romanceraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.romance_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"💝 RomanceRaid `{rid}` started. `.stopromance {rid}`")
            while state.romance_raid.get(rid, {}).get("active"):
                txt = random.choice(romance_texts) if romance_texts else "✨ Romance"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.romance_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sromanceraid\b'))
        async def cmd_stopromance(event, arg=""):
            for k in list(state.romance_raid.keys()):
                state.romance_raid[k]["active"] = False
            await s_edit(event, "✅ RomanceRaid stopped.")

        # Troll Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.trollraid\b'))
        async def cmd_trollraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.troll_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"🤡 TrollRaid `{rid}` started. `.stoptroll {rid}`")
            while state.troll_raid.get(rid, {}).get("active"):
                txt = random.choice(troll_texts) if troll_texts else "✨ Troll"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.troll_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.strollraid\b'))
        async def cmd_stoptroll(event, arg=""):
            for k in list(state.troll_raid.keys()):
                state.troll_raid[k]["active"] = False
            await s_edit(event, "✅ TrollRaid stopped.")

        # Ragebait Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.ragebaitraid\b'))
        async def cmd_ragebaitraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.ragebait_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"😡 RagebaitRaid `{rid}` started. `.stopragebait {rid}`")
            while state.ragebait_raid.get(rid, {}).get("active"):
                txt = random.choice(ragebait_texts) if ragebait_texts else "✨ Rage"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.ragebait_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sragebaitraid\b'))
        async def cmd_stopragebait(event, arg=""):
            for k in list(state.ragebait_raid.keys()):
                state.ragebait_raid[k]["active"] = False
            await s_edit(event, "✅ RagebaitRaid stopped.")

        # Roast Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.roastraid\b'))
        async def cmd_roastraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.roast_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"🔥 RoastRaid `{rid}` started. `.stoproast {rid}`")
            while state.roast_raid.get(rid, {}).get("active"):
                txt = random.choice(roast_texts) if roast_texts else "✨ Roast"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(1.0)
            state.roast_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sroastraid\b'))
        async def cmd_stoproast(event, arg=""):
            for k in list(state.roast_raid.keys()):
                state.roast_raid[k]["active"] = False
            await s_edit(event, "✅ RoastRaid stopped.")

        # ═══════════════════════════════════════════════════════════════════
        # 6. NON-ABUSIVE RAIDS (Menu9)
        # ═══════════════════════════════════════════════════════════════════

        # Attack Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.attackraid\b'))
        async def cmd_attackraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.attack_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"⚔️ AttackRaid `{rid}` started. `.stopattackraid {rid}`")
            while state.attack_raid.get(rid, {}).get("active"):
                txt = random.choice(attack_texts) if attack_texts else "✨ Attack"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.8)
            state.attack_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sattackraid\b'))
        async def cmd_stopattackraid(event, arg=""):
            for k in list(state.attack_raid.keys()):
                state.attack_raid[k]["active"] = False
            await s_edit(event, "✅ AttackRaid stopped.")

        # War Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.warraid\b'))
        async def cmd_warraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.war_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"⚔️ WarRaid `{rid}` started. `.stopwarraid {rid}`")
            while state.war_raid.get(rid, {}).get("active"):
                txt = random.choice(war_texts) if war_texts else "✨ War"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.8)
            state.war_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.swarraid\b'))
        async def cmd_stopwarraid(event, arg=""):
            for k in list(state.war_raid.keys()):
                state.war_raid[k]["active"] = False
            await s_edit(event, "✅ WarRaid stopped.")

        # Savage Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.savageraid\b'))
        async def cmd_savageraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.savage_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"💀 SavageRaid `{rid}` started. `.stopsavageraid {rid}`")
            while state.savage_raid.get(rid, {}).get("active"):
                txt = random.choice(savage_texts) if savage_texts else "✨ Savage"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.8)
            state.savage_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.ssavageraid\b'))
        async def cmd_stopsavageraid(event, arg=""):
            for k in list(state.savage_raid.keys()):
                state.savage_raid[k]["active"] = False
            await s_edit(event, "✅ SavageRaid stopped.")

        # Ultra Raid
        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.ultraraid\b'))
        async def cmd_ultraraid(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts: tgts = {event.chat_id}
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.ultra_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"🔮 UltraRaid `{rid}` started. `.stopultraraid {rid}`")
            while state.ultra_raid.get(rid, {}).get("active"):
                txt = random.choice(ultra_texts) if ultra_texts else "✨ Ultra"
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.8)
            state.ultra_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sultraraid\b'))
        async def cmd_stopultraraid(event, arg=""):
            for k in list(state.ultra_raid.keys()):
                state.ultra_raid[k]["active"] = False
            await s_edit(event, "✅ UltraRaid stopped.")

        # Shame / Diss / Devil / Karma / Doom
        for cmd_name, state_dict, texts_list, stop_name in [
            ("shameraid", "shame_raid", shame_texts, "sshameraid"),
            ("dissraid", "diss_raid", diss_texts, "sdissraid"),
            ("devilraid", "devil_raid", devil_texts, "sdevilraid"),
            ("karmaraid", "karma_raid", karma_texts, "skarmaraid"),
            ("doomraid", "doom_raid", doom_texts, "sdoomraid"),
        ]:
            d = getattr(state, state_dict)
            t = texts_list

            @user_bot.on(events.NewMessage(outgoing=True, pattern=rf'\.{cmd_name}\b'))
            async def _(event, arg="", d=d, t=t, cmd_name=cmd_name):
                tgts = await get_targets(event, arg)
                if not tgts: tgts = {event.chat_id}
                cid = event.chat_id
                rid = random.randint(1000, 9999)
                d[rid] = {"targets": tgts, "active": True}
                await s_edit(event, f"💥 {cmd_name.capitalize()} `{rid}` started. `.stop{cmd_name} {rid}`")
                while d.get(rid, {}).get("active"):
                    txt = random.choice(t) if t else "✨"
                    try:
                        for uid in tgts:
                            await s_send(cid, txt, reply_to=uid)
                            await asyncio.sleep(state.spray_delay)
                    except:
                        pass
                    await asyncio.sleep(0.8)
                d.pop(rid, None)

            @user_bot.on(events.NewMessage(outgoing=True, pattern=rf'\.{stop_name}\b'))
            async def _(event, arg="", d=d):
                for k in list(d.keys()):
                    d[k]["active"] = False
                await s_edit(event, f"✅ {cmd_name.capitalize()} stopped.")

        # ═══════════════════════════════════════════════════════════════════
        # 7. PREMIUM RAID / SPAM COMMANDS (Menu11a, Menu11b)
        # ═══════════════════════════════════════════════════════════════════

        async def prem_raid_handler(event, arg, key, texts_dict):
            if not await is_prem(event.sender_id):
                await s_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
                return
            lst = texts_dict.get(key, [])
            if not lst:
                await s_edit(event, f"❌ Text list `{key}` is empty.")
                return
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            cid = event.chat_id
            pid = random.randint(1000, 9999)
            state.premium_raid_tgts[pid] = {"targets": tgts, "active": True, "list": lst}
            await s_edit(event, f"👑 PremiumRaid `{pid}` ({key}) started. `.stoppremraid {pid}`")
            while state.premium_raid_tgts.get(pid, {}).get("active"):
                txt = random.choice(lst)
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.6)
            state.premium_raid_tgts.pop(pid, None)

        async def prem_spam_handler(event, arg, key, texts_dict):
            if not await is_prem(event.sender_id):
                await s_edit(event, "❌ Premium only. Buy with `/buy` in main bot.")
                return
            lst = texts_dict.get(key, [])
            if not lst:
                await s_edit(event, f"❌ Text list `{key}` is empty.")
                return
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            cid = event.chat_id
            pid = random.randint(1000, 9999)
            state.premium_spam_tgts[pid] = {"targets": tgts, "active": True, "list": lst}
            await s_edit(event, f"👑 PremiumSpam `{pid}` ({key}) started. `.stoppremspam {pid}`")
            while state.premium_spam_tgts.get(pid, {}).get("active"):
                txt = random.choice(lst)
                try:
                    for uid in tgts:
                        await s_send(cid, txt, reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.6)
            state.premium_spam_tgts.pop(pid, None)

        # Register premium raid commands
        for cmd, key in [("mr","mr"),("mr2","mr2"),("br","br"),("br2","br2"),("br3","br3"),
                          ("sqr","sqr"),("sq2","sq2"),("cr","cr"),("bar","bar"),("gr","gr")]:
            @user_bot.on(events.NewMessage(outgoing=True, pattern=rf'\.{cmd}\b'))
            async def _(event, arg="", k=key):
                await prem_raid_handler(event, arg, k, premium_raid_texts)

        # Register premium spam commands
        for cmd, key in [("ms","ms"),("ms2","ms2"),("bs","bs"),("bs2","bs2"),("bs3","bs3"),
                          ("sqs","sqs"),("sqs2","sqs2"),("cs","cs"),("bas","bas"),("gs","gs")]:
            @user_bot.on(events.NewMessage(outgoing=True, pattern=rf'\.{cmd}\b'))
            async def _(event, arg="", k=key):
                await prem_spam_handler(event, arg, k, premium_spam_texts)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.stoppremraid\b'))
        async def cmd_stoppremraid(event, arg=""):
            pid = arg.strip()
            if pid and pid.isdigit():
                pid = int(pid)
                if pid in state.premium_raid_tgts:
                    state.premium_raid_tgts[pid]["active"] = False
                    await s_edit(event, f"✅ PremiumRaid `{pid}` stopped")
                    return
            cnt = 0
            for k in list(state.premium_raid_tgts.keys()):
                state.premium_raid_tgts[k]["active"] = False
                cnt += 1
            await s_edit(event, f"✅ All premium raids ({cnt}) stopped.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.stoppremspam\b'))
        async def cmd_stoppremspam(event, arg=""):
            pid = arg.strip()
            if pid and pid.isdigit():
                pid = int(pid)
                if pid in state.premium_spam_tgts:
                    state.premium_spam_tgts[pid]["active"] = False
                    await s_edit(event, f"✅ PremiumSpam `{pid}` stopped")
                    return
            cnt = 0
            for k in list(state.premium_spam_tgts.keys()):
                state.premium_spam_tgts[k]["active"] = False
                cnt += 1
            await s_edit(event, f"✅ All premium spams ({cnt}) stopped.")

        # ═══════════════════════════════════════════════════════════════════
        # 8. PWR / OWS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.pwr\b'))
        async def cmd_pwr(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not reply_texts:
                await s_edit(event, "❌ reply_texts is empty.")
                return
            cid = event.chat_id
            rid = random.randint(1000, 9999)
            state.pwr_raid[rid] = {"targets": tgts, "active": True}
            await s_edit(event, f"⚡ PWR `{rid}` started. `.stoppwr {rid}`")
            while state.pwr_raid.get(rid, {}).get("active"):
                try:
                    txt = random.choice(reply_texts)
                    for uid in tgts:
                        await s_send(cid, f"「 ✨ 」➣ {txt}", reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.6)
            state.pwr_raid.pop(rid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.spwr\b'))
        async def cmd_stoppwr(event, arg=""):
            for k in list(state.pwr_raid.keys()):
                state.pwr_raid[k]["active"] = False
            await s_edit(event, "✅ PWR stopped.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.ows\b'))
        async def cmd_ows(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            if not ows_texts:
                await s_edit(event, "❌ ows_texts is empty.")
                return
            cid = event.chat_id
            oid = random.randint(1000, 9999)
            state.ows_spam[oid] = {"targets": tgts, "active": True}
            await s_edit(event, f"🌊 OWS `{oid}` started. `.stowo {oid}`")
            while state.ows_spam.get(oid, {}).get("active"):
                try:
                    txt = random.choice(ows_texts)
                    for uid in tgts:
                        await s_send(cid, f"「 🏄 」➣ {txt}", reply_to=uid)
                        await asyncio.sleep(state.spray_delay)
                except:
                    pass
                await asyncio.sleep(0.5)
            state.ows_spam.pop(oid, None)

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.sows\b'))
        async def cmd_stopows(event, arg=""):
            for k in list(state.ows_spam.keys()):
                state.ows_spam[k]["active"] = False
            await s_edit(event, "✅ OWS stopped.")

        # ═══════════════════════════════════════════════════════════════════
        # 9. CLONE COMMANDS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.clone\b'))
        async def cmd_clone(event, arg=""):
            target_user = None
            if event.is_reply:
                try:
                    r = await event.get_reply_message()
                    if r and r.sender_id:
                        target_user = await user_bot.get_entity(r.sender_id)
                except:
                    pass
            elif arg.strip():
                try:
                    target_user = await user_bot.get_entity(arg.strip())
                except:
                    pass

            if not target_user:
                await s_edit(event, "❌ Reply to someone or provide username/ID.")
                return

            try:
                # Name
                fname = getattr(target_user, 'first_name', '') or ''
                lname = getattr(target_user, 'last_name', '') or ''
                full_name = f"{fname} {lname}".strip()
                bio = ""
                try:
                    full_info = await user_bot(functions.users.GetFullUserRequest(target_user))
                    bio = getattr(full_info, 'about', '') or ''
                except:
                    pass

                # Profile photo
                photo_bytes = None
                try:
                    photos = await user_bot.get_profile_photos(target_user, limit=1)
                    if photos:
                        photo_bytes = await user_bot.download_file(photos[0].big_photo)
                except:
                    pass

                state.clone_active = True
                state.clone_data = {"name": full_name, "bio": bio, "photo": photo_bytes}
                me_self = await user_bot.get_me()

                if full_name:
                    await user_bot(UpdateProfileRequest(first_name=fname, last_name=lname))

                if photo_bytes:
                    try:
                        file = BytesIO(photo_bytes)
                        await user_bot(UploadProfilePhotoRequest(file=file))
                    except:
                        pass

                if bio:
                    try:
                        await user_bot(functions.account.UpdateProfileRequest(about=bio))
                    except:
                        pass

                await s_edit(event, f"✅ Cloned **{full_name}**")
            except Exception as e:
                await s_edit(event, f"❌ Clone failed: {e}")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.revert\b'))
        async def cmd_revert(event, arg=""):
            if not state.clone_active:
                await s_edit(event, "❌ No clone active.")
                return
            state.clone_active = False
            try:
                me_self = await user_bot.get_me()
                orig_name = f"Zyrex User {me_self.id}"
                await user_bot(UpdateProfileRequest(first_name=orig_name, last_name=""))
                try:
                    photos = await user_bot.get_profile_photos('me')
                    if photos:
                        await user_bot(DeletePhotosRequest(id=[InputDocument(
                            id=p.id, access_hash=p.access_hash, file_reference=p.file_reference
                        ) for p in photos[:1]]))
                except:
                    pass
                await s_edit(event, "✅ Reverted to original.")
            except Exception as e:
                await s_edit(event, f"❌ Revert failed: {e}")

        # ═══════════════════════════════════════════════════════════════════
        # 10. NC (Night Core / Language Spam)
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.nc\b'))
        async def cmd_nc(event, arg=""):
            if state.nc_state["active"]:
                state.nc_state["active"] = False
                if state.nc_state["task"]:
                    state.nc_state["task"].cancel()
                await s_edit(event, "✅ NC stopped.")
                return

            parts = arg.strip().split(maxsplit=1)
            lang = "hindi"
            text = arg.strip()
            if parts and parts[0].lower() in ("hindi", "english", "hinglish", "marathi", "punjabi", "bhojpuri"):
                lang = parts[0].lower()
                text = parts[1] if len(parts) > 1 else ""

            if not text:
                await s_edit(event, "❌ Usage: `.nc hindi <text>` or `.nc english <text>`")
                return

            state.nc_state["active"] = True
            state.nc_state["lang"] = lang
            state.nc_state["chat_id"] = event.chat_id

            async def nc_loop():
                while state.nc_state.get("active"):
                    try:
                        if lang == "hindi":
                            msg = f"🇮🇳 {text}"
                        elif lang == "english":
                            msg = f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 {text}"
                        elif lang == "hinglish":
                            msg = f"💫 {text}"
                        elif lang == "marathi":
                            msg = f"🟠 {text}"
                        elif lang == "punjabi":
                            msg = f"🟢 {text}"
                        elif lang == "bhojpuri":
                            msg = f"🟡 {text}"
                        else:
                            msg = text
                        await s_send(event.chat_id, msg)
                        await asyncio.sleep(1.5)
                    except:
                        await asyncio.sleep(2)
                state.nc_state["task"] = None

            state.nc_state["task"] = asyncio.create_task(nc_loop())
            await s_edit(event, f"🌀 NC started ({lang}). `.nc` to stop.")

        # ═══════════════════════════════════════════════════════════════════
        # 11. AFK
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.afk\b'))
        async def cmd_afk(event, arg=""):
            reason = arg.strip() or "AFK"
            state.afk_data["afk"] = True
            state.afk_data["reason"] = reason
            state.afk_data["time"] = time.time()
            state.afk_data["chat"] = event.chat_id
            await s_edit(event, f"🟡 AFK: {reason}")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.unafk\b'))
        async def cmd_unafk(event, arg=""):
            state.afk_data["afk"] = False
            state.afk_data.clear()
            await s_edit(event, "🟢 Back! AFK removed.")

        # Incoming AFK reply
        @user_bot.on(events.NewMessage(incoming=True))
        async def afk_reply(event):
            if state.afk_data.get("afk") and event.sender_id and event.sender_id not in (me.id, BOT_ID) and event.is_private:
                elapsed = int(time.time() - state.afk_data.get("time", time.time()))
                hrs, rem = divmod(elapsed, 3600)
                mins, secs = divmod(rem, 60)
                dur = f"{hrs}h {mins}m {secs}s" if hrs else f"{mins}m {secs}s" if mins else f"{secs}s"
                reason = state.afk_data.get("reason", "AFK")
                try:
                    await event.reply(f"🟡 AFK ({dur}): {reason}")
                except:
                    pass

        # ═══════════════════════════════════════════════════════════════════
        # 12. DM SHIELD / GOD PROTECTION
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.dmshield\b'))
        async def cmd_dmshield(event, arg=""):
            state.dm_shield = not state.dm_shield
            await s_edit(event, f"🛡️ DM Shield {'ON' if state.dm_shield else 'OFF'}")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.dmapprove\b'))
        async def cmd_dmapprove(event, arg=""):
            tgts = await get_targets(event, arg)
            if tgts:
                state.dm_approved.update(tgts)
                await s_edit(event, f"✅ Approved {len(tgts)} user(s) for DM.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.dmblock\b'))
        async def cmd_dmblock(event, arg=""):
            tgts = await get_targets(event, arg)
            if tgts:
                state.dm_blocked.update(tgts)
                await s_edit(event, f"🔇 Blocked {len(tgts)} user(s) from DM.")
                for uid in tgts:
                    try:
                        await user_bot(BlockRequest(uid))
                    except:
                        pass

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.godprotection\b'))
        async def cmd_godprotection(event, arg=""):
            state.god_protection = not state.god_protection
            await s_edit(event, f"⚡ God Protection {'ON' if state.god_protection else 'OFF'}")

        # DM Shield handler
        @user_bot.on(events.NewMessage(incoming=True))
        async def dmshield_handler(event):
            if not event.is_private:
                return
            if event.sender_id in (me.id, BOT_ID):
                return
            if state.dm_shield and event.sender_id not in state.dm_approved:
                if event.sender_id not in state.dm_blocked:
                    try:
                        await event.reply("🛡️ DM Shield Active. Use `/login` in main bot to contact.")
                    except:
                        pass
                return

        # ═══════════════════════════════════════════════════════════════════
        # 13. FILTER / NOTE / ANTIDEL / WATCH
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.filter\b'))
        async def cmd_filter(event, arg=""):
            parts = arg.strip().split(" ", 1)
            if len(parts) < 2:
                await s_edit(event, "❌ Usage: `.filter keyword response`")
                return
            kw, resp = parts
            state.filter_map[kw.lower()] = resp
            await s_edit(event, f"✅ Filter `{kw}` added.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.delfilter\b'))
        async def cmd_delfilter(event, arg=""):
            kw = arg.strip().lower()
            if kw in state.filter_map:
                del state.filter_map[kw]
                await s_edit(event, f"✅ Filter `{kw}` removed.")
            else:
                await s_edit(event, "❌ Filter not found.")

        # Filter auto-reply
        @user_bot.on(events.NewMessage(incoming=True))
        async def filter_handler(event):
            if not event.text:
                return
            if event.sender_id in (me.id, BOT_ID):
                return
            for kw, resp in state.filter_map.items():
                if kw in event.text.lower():
                    try:
                        await event.reply(resp)
                    except:
                        pass
                    break

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.note\b'))
        async def cmd_note(event, arg=""):
            parts = arg.strip().split(" ", 1)
            if len(parts) < 2:
                await s_edit(event, "❌ Usage: `.note name content`")
                return
            nname, ncontent = parts
            state.notes[nname] = ncontent
            await s_edit(event, f"✅ Note `{nname}` saved.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.getnote\b'))
        async def cmd_getnote(event, arg=""):
            nname = arg.strip()
            if nname in state.notes:
                await s_edit(event, f"📝 **{nname}**:\n{state.notes[nname]}")
            else:
                await s_edit(event, "❌ Note not found.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.delnote\b'))
        async def cmd_delnote(event, arg=""):
            nname = arg.strip()
            if nname in state.notes:
                del state.notes[nname]
                await s_edit(event, f"✅ Note `{nname}` deleted.")
            else:
                await s_edit(event, "❌ Note not found.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.antidel\b'))
        async def cmd_antidel(event, arg=""):
            state.antidel_on = not state.antidel_on
            await s_edit(event, f"🗑️ Anti-Delete {'ON' if state.antidel_on else 'OFF'}")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.watch\b'))
        async def cmd_watch(event, arg=""):
            tgts = await get_targets(event, arg)
            if tgts:
                cid = event.chat_id
                for uid in tgts:
                    state.watch_map[uid] = cid
                await s_edit(event, f"👁️ Watching {len(tgts)} user(s).")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.unwatch\b'))
        async def cmd_unwatch(event, arg=""):
            tgts = await get_targets(event, arg)
            if tgts:
                for uid in tgts:
                    state.watch_map.pop(uid, None)
                await s_edit(event, f"✅ Unwatched {len(tgts)} user(s).")
            else:
                state.watch_map.clear()
                await s_edit(event, "✅ All unwatched.")

        # ═══════════════════════════════════════════════════════════════════
        # 14. GROUP LOCK / FREEZE
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.lock\b'))
        async def cmd_lock(event, arg=""):
            state.group_locks.add(event.chat_id)
            await s_edit(event, "🔒 Group locked.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.unlock\b'))
        async def cmd_unlock(event, arg=""):
            state.group_locks.discard(event.chat_id)
            await s_edit(event, "🔓 Group unlocked.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.freeze\b'))
        async def cmd_freeze(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            cid = event.chat_id
            for uid in tgts:
                try:
                    banned = ChatBannedRights(
                        until_date=None, send_messages=True,
                        send_media=True, send_stickers=True, send_gifs=True,
                        send_games=True, send_inline=True, send_polls=True,
                        invite_users=True, change_info=True, pin_messages=True
                    )
                    await user_bot.edit_permissions(cid, uid, banned)
                except:
                    pass
            await s_edit(event, f"🧊 Froze {len(tgts)} user(s).")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.unfreeze\b'))
        async def cmd_unfreeze(event, arg=""):
            tgts = await get_targets(event, arg)
            if not tgts:
                await s_edit(event, "❌ No targets.")
                return
            cid = event.chat_id
            for uid in tgts:
                try:
                    rights = ChatBannedRights(
                        until_date=None, send_messages=False, send_media=False,
                        send_stickers=False, send_gifs=False, send_games=False,
                        send_inline=False, send_polls=False, invite_users=False,
                        change_info=False, pin_messages=False
                    )
                    await user_bot.edit_permissions(cid, uid, rights)
                except:
                    pass
            await s_edit(event, f"✅ Unfroze {len(tgts)} user(s).")

        # ═══════════════════════════════════════════════════════════════════
        # 15. ADMIN COMMANDS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.addadmin\b'))
        async def cmd_addadmin(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            tgts = await get_targets(event, arg)
            if tgts:
                state.admins.update(tgts)
                await s_edit(event, f"✅ Admin added: {len(tgts)} user(s).")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.deladmin\b'))
        async def cmd_deladmin(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            tgts = await get_targets(event, arg)
            if tgts:
                state.admins.difference_update(tgts)
                await s_edit(event, f"✅ Admin removed: {len(tgts)} user(s).")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.admins\b'))
        async def cmd_listadmins(event, arg=""):
            lst = list(state.admins) if state.admins else ["None"]
            await s_edit(event, f"👑 Admins: {', '.join(str(x) for x in lst)}")

        # ═══════════════════════════════════════════════════════════════════
        # 16. PING / STATS
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.ping\b'))
        async def cmd_ping(event, arg=""):
            start = time.time()
            try:
                m = await s_edit(event, "🏓 Pong!")
                elapsed = (time.time() - start) * 1000
                await s_edit(event, f"🏓 Pong! `{elapsed:.0f}ms`")
            except:
                pass

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.uptime\b'))
        async def cmd_uptime(event, arg=""):
            elapsed = int(time.time() - state.start_time)
            hrs, rem = divmod(elapsed, 3600)
            mins, secs = divmod(rem, 60)
            await s_edit(event, f"⏱️ Uptime: `{hrs}h {mins}m {secs}s`")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.stats\b'))
        async def cmd_stats(event, arg=""):
            await s_edit(event, f"📊 **Stats**\n"
                f"Raids: {len(state.shayari_raid)+len(state.rizz_raid)+len(state.pickup_raid)} active\n"
                f"Sprays: {len(state.spray_tasks)} active\n"
                f"Filters: {len(state.filter_map)}\n"
                f"Notes: {len(state.notes)}\n"
                f"Muted: {len(state.muted)}\n"
                f"GMuted: {len(state.gmuted)}")

        # ═══════════════════════════════════════════════════════════════════
        # 17. STOP ALL (emergency kill switch)
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.stopall\b'))
        async def cmd_stopall(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            # Stop all raids
            for d in [state.shayari_raid, state.rizz_raid, state.pickup_raid,
                      state.romance_raid, state.troll_raid, state.ragebait_raid,
                      state.roast_raid, state.attack_raid, state.war_raid,
                      state.savage_raid, state.ultra_raid, state.shame_raid,
                      state.diss_raid, state.devil_raid, state.karma_raid,
                      state.doom_raid, state.pwr_raid, state.custom_raid,
                      state.deathgod_on, state.premium_raid_tgts, state.premium_spam_tgts]:
                for k in list(d.keys()):
                    d[k]["active"] = False
            for k in list(state.spray_tasks.keys()):
                state.spray_tasks[k]["active"] = False
            # Turn off reply modes
            state.reply_on.clear()
            state.rr_on.clear()
            state.flag_on.clear()
            state.hrr_on.clear()
            state.replygod_on.clear()
            # Stop NC
            state.nc_state["active"] = False
            if state.nc_state["task"]:
                state.nc_state["task"].cancel()
                state.nc_state["task"] = None
            await s_edit(event, "🛑 **ALL STOPPED** — raids, sprays, reply modes, NC.")

        # ═══════════════════════════════════════════════════════════════════
        # 18. TEXT LIST MANAGEMENT (Owner only)
        # ═══════════════════════════════════════════════════════════════════

        LIST_MAP = {
            "reply": reply_texts, "rr": rr_texts, "flag": flag_texts,
            "heart": heart_texts, "replygod": replygod_texts,
            "deathgod": deathgod_replies, "ows": ows_texts,
            "shayari": shayari_texts, "rizz": rizz_texts,
            "pickup": pickup_texts, "romance": romance_texts,
            "troll": troll_texts, "ragebait": ragebait_texts, "roast": roast_texts,
            "attack": attack_texts, "war": war_texts,
            "savage": savage_texts, "ultra": ultra_texts,
            "shame": shame_texts, "diss": diss_texts,
            "devil": devil_texts, "karma": karma_texts, "doom": doom_texts,
            "mr": mr_texts, "mr2": mr2_texts, "br": br_texts,
            "br2": br2_texts, "br3": br3_texts,
            "sqr": sqr_texts, "sq2": sq2_texts, "cr": cr_texts,
            "bar": bar_texts, "gr": gr_texts,
            "ms": ms_texts, "ms2": ms2_texts, "bs": bs_texts,
            "bs2": bs2_texts, "bs3": bs3_texts,
            "sqs": sqs_texts, "sqs2": sqs2_texts, "cs": cs_texts,
            "bas": bas_texts, "gs": gs_texts,
        }

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.addtext\b'))
        async def cmd_addtext(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            parts = arg.strip().split(" ", 1)
            if len(parts) < 2:
                lst_names = ", ".join(LIST_MAP.keys())
                await s_edit(event, f"❌ Usage: `.addtext <listname> <text>`\nLists: {lst_names}")
                return
            lst_name, text = parts
            lst_name = lst_name.lower()
            if lst_name not in LIST_MAP:
                await s_edit(event, f"❌ Unknown list `{lst_name}`.")
                return
            LIST_MAP[lst_name].append(text)
            await s_edit(event, f"✅ Added to `{lst_name}` (now {len(LIST_MAP[lst_name])} items)")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.deltext\b'))
        async def cmd_deltext(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            parts = arg.strip().split(" ", 1)
            if len(parts) < 2:
                await s_edit(event, "❌ Usage: `.deltext <listname> <index>`")
                return
            lst_name, idx_str = parts
            lst_name = lst_name.lower()
            if lst_name not in LIST_MAP:
                await s_edit(event, f"❌ Unknown list `{lst_name}`.")
                return
            try:
                idx = int(idx_str)
                lst = LIST_MAP[lst_name]
                if 0 <= idx < len(lst):
                    removed = lst.pop(idx)
                    await s_edit(event, f"✅ Removed item {idx} from `{lst_name}`")
                else:
                    await s_edit(event, f"❌ Index {idx} out of range (0-{len(lst)-1})")
            except ValueError:
                await s_edit(event, "❌ Provide numeric index.")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.cleartext\b'))
        async def cmd_cleartext(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            lst_name = arg.strip().lower()
            if lst_name in LIST_MAP:
                LIST_MAP[lst_name].clear()
                await s_edit(event, f"✅ Cleared `{lst_name}`")
            else:
                await s_edit(event, f"❌ Unknown list. Available: {', '.join(LIST_MAP.keys())}")

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.listtext\b'))
        async def cmd_listtext(event, arg=""):
            lst_name = arg.strip().lower()
            if lst_name in LIST_MAP:
                lst = LIST_MAP[lst_name]
                if lst:
                    lines = [f"{i}: {t[:50]}" for i, t in enumerate(lst[:20])]
                    await s_edit(event, f"📋 `{lst_name}` ({len(lst)}):\n" + "\n".join(lines))
                else:
                    await s_edit(event, f"📋 `{lst_name}` is empty.")
            else:
                await s_edit(event, f"❌ Unknown list. Available: {', '.join(LIST_MAP.keys())}")

        # ═══════════════════════════════════════════════════════════════════
        # 19. BROADCAST (via main bot)
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.broadcast\b'))
        async def cmd_broadcast(event, arg=""):
            if event.sender_id not in OWNER_IDS:
                return
            if not arg.strip():
                await s_edit(event, "❌ Usage: `.broadcast <message>`")
                return
            msg = arg.strip()
            users = load_broadcast_users()
            sent = 0
            for uid in users:
                try:
                    await s_send(uid, f"📢 **Broadcast:**\n{msg}")
                    sent += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
            await s_edit(event, f"✅ Broadcast sent to {sent}/{len(users)} users.")

        # ═══════════════════════════════════════════════════════════════════
        # 20. ADD BOTS TO GROUP
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.addbots\b'))
        async def cmd_addbots(event, arg=""):
            if not event.is_group:
                await s_edit(event, "❌ Group only.")
                return
            cid = event.chat_id
            added = 0
            for bot_username in ADD_BOTS_LIST:
                try:
                    bot_entity = await user_bot.get_entity(bot_username)
                    await user_bot(InviteToChannelRequest(cid, [bot_entity]))
                    added += 1
                    await asyncio.sleep(2)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 1)
                except:
                    pass
            await s_edit(event, f"✅ Added {added} bots.")

        # ═══════════════════════════════════════════════════════════════════
        # 21. GC FAST / EMOJI SPAM
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.gcf\b'))
        async def cmd_gcf(event, arg=""):
            if not event.is_group:
                await s_edit(event, "❌ Group only.")
                return
            cid = event.chat_id
            try:
                count = int(arg.strip()) if arg.strip().isdigit() else 50
                count = min(count, 200)
            except:
                count = 50
            for _ in range(count):
                try:
                    emoji = random.choice(GC_FAST_EMOJIS)
                    await s_send(cid, emoji)
                    await asyncio.sleep(0.03)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 1)
                except:
                    pass
            await s_edit(event, f"✅ GCF done ({count}x)")

        # ═══════════════════════════════════════════════════════════════════
        # 22. HELP
        # ═══════════════════════════════════════════════════════════════════

        @user_bot.on(events.NewMessage(outgoing=True, pattern=r'\.help\b'))
        async def cmd_help(event, arg=""):
            await s_edit(event, "📖 Type `.menu` to see all menus or any `.menu1`–`.menu14`")

        # ═══════════════════════════════════════════════════════════════════
        # READY
        # ═══════════════════════════════════════════════════════════════════

        print(f"✅ Userbot {me.id} ready — ALL commands loaded")
        await user_bot.run_until_disconnected()

    except Exception as e:
        print(f"❌ Userbot error: {e}")
        traceback.print_exc()
        raise
    finally:
        if user_bot:
            try:
                await user_bot.disconnect()
            except:
                pass
        if chat_id in active_userbots:
            del active_userbots[chat_id]
# ═══════════════════════════════════════════════════════════════════════
# SECTION 17: MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

async def main():
    """Main entry point."""
    print("🚀 Starting ZYЯΣX ✕ ΛΣƬΉΣЯ Userbot System...")

    # ── Init DB ──
    await init_db()
    await init_cipher()

    # ── Start main bot ──
    print("📡 Starting Main Bot...")
    await MAIN_BOT_CLIENT.start(bot_token=BOT_TOKEN)
    print("✅ Main Bot online")

    # ── Load existing sessions and restart userbots ──
    sessions = await load_sessions()
    for uid, session_str in sessions.items():
        task = asyncio.create_task(run_user_bot_with_restart(session_str, uid))
        task.set_name(f"userbot_restart_{uid}")
        running_tasks.add(task)
        task.add_done_callback(running_tasks.discard)
        await asyncio.sleep(1.5)  # Stagger startups

    print(f"🚀 {len(sessions)} userbots launched")

    # ── Keep running ──
    await MAIN_BOT_CLIENT.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
