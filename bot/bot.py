import os
import html as html_module
import telebot
from telebot import types
import sqlite3
import random
import string
import threading
import time
import requests
from flask import Flask
from waitress import serve

# === НАЛАШТУВАННЯ ===
TOKEN        = os.environ.get("TELEGRAM_BOT_TOKEN")
SUPPORT_USER = "king_dealsSupport"
NOTIFY_ID    = 7908632313   # @qw1zo — сповіщення про нових юзерів та угоди

bot = telebot.TeleBot(TOKEN)
BOT_DIR = os.path.dirname(__file__)

# === БАНЕРИ ===
def banner(name):
    path = os.path.join(BOT_DIR, f"banner_{name}.png")
    return path if os.path.exists(path) else os.path.join(BOT_DIR, "banner.png")

BANNER_MAIN   = os.path.join(BOT_DIR, "banner.png")
BANNER_DEALS  = banner("deals")
BANNER_BAL    = banner("balance")
BANNER_REQS   = banner("reqs")
BANNER_REF    = banner("ref")
BANNER_CREATE = banner("create")
BANNER_BIND   = banner("bind")

# === ПРЕМІУМ ЕМОДЗІ ===
def E(emoji_id, fallback):
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

E_BAG    = E("5893255507380014983", "💼")
E_HAND   = E("5395732581780040886", "🤝")
E_FLASH  = E("5456140674028019486", "⚡️")
E_1      = E("5794164805065514131", "1️⃣")
E_2      = E("5794085322400733645", "2️⃣")
E_SHIELD = E("5902016123972358349", "🛡")
E_3      = E("5794280000383358988", "3️⃣")
E_4      = E("5794241397217304511", "4️⃣")
E_BOX    = E("5778672437122045013", "📦")
E_CHECK  = E("5294515522761663291", "✅")
E_DEV    = E("5362079447136610876", "👨‍💻")
E_CROSS  = E("5893163582194978381", "❌")
E_TIME   = E("5893102202817352158", "🕐")
E_USER   = E("5902335789798265487", "👤")
E_LINK   = E("5902449142575141204", "🔗")
E_PLANE  = E("5296432770392791386", "✈️")
E_STAR   = E("5463289097336405244", "⭐️")
E_FLASH2 = E("5258203794772085854", "⚡️")
E_MONEY  = E("5893473283696759404", "💰")
E_COIN   = E("5893473283696759404", "💰")
E_PIN    = E("5895440460322706085", "📌")
E_TON    = E("5427168083074628963", "💎")
E_CARD   = E("5445353829304387411", "💳")
E_STARS  = E("5924870095925942277", "⭐")
E_USDT   = E("6039802097916974085", "🌑")
E_BTC    = E("5816788957614053645", "🌑")
E_CLOUD  = E("5467538555158943525", "☁️")
E_CROWN  = E("5217822164362739968", "👑")
E_CART   = E("5312361253610475399", "🛒")
E_BANK   = E("5332455502917949981", "🏦")
E_DONE   = E("5206607081334906820", "✅")
E_CANCEL = E("5220978205702481649", "❌")
E_PEOPLE = E("6032609071373226027", "👥")
E_GLOBE  = E("5776233299424843260", "🌐")
E_WAIT   = E("5307677879186698240", "⏳")
E_LOCK   = E("5472107687172341080", "🔒")

# === ПЕРЕКЛАДИ ===
TEXTS = {
    'ru': {
        'btn_create':    "🤝 Создать сделку",
        'btn_deals':     "🏁 Мои сделки",
        'btn_balance':   "💰 Баланс",
        'btn_reqs':      "🗃 Мои реквизиты",
        'btn_ref':       "🔗 Рефералы",
        'btn_lang':      "🌐 Язык / Lang",
        'btn_support':   "💬 Техподдержка",
        'btn_back':      "📦 Назад в меню",
        'btn_back_step': "⬅️ Назад",
        'btn_top_up':    "🖥 Пополнить",
        'btn_withdraw':  "💸 Вывести",
        'deal_status': {
            'created':   '🕐 Ожидает оплаты',
            'paid':      '🔒 Оплачена, ждёт подтверждения',
            'completed': '✅ Завершена',
        },
    },
    'en': {
        'btn_create':    "🤝 Create Deal",
        'btn_deals':     "🏁 My Deals",
        'btn_balance':   "💰 Balance",
        'btn_reqs':      "🗃 My Requisites",
        'btn_ref':       "🔗 Referrals",
        'btn_lang':      "🌐 Язык / Lang",
        'btn_support':   "💬 Support",
        'btn_back':      "📦 Back to menu",
        'btn_back_step': "⬅️ Back",
        'btn_top_up':    "🖥 Top Up",
        'btn_withdraw':  "💸 Withdraw",
        'deal_status': {
            'created':   '🕐 Awaiting payment',
            'paid':      '🔒 Paid, awaiting confirmation',
            'completed': '✅ Completed',
        },
    },
}

# === БАЗА ДАНИХ ===
def init_db():
    conn = sqlite3.connect('king_deals.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id    INTEGER PRIMARY KEY,
        username   TEXT,
        lang       TEXT DEFAULT 'ru',
        referrer_id INTEGER,
        req_ton    TEXT,
        req_card   TEXT,
        req_stars  TEXT,
        req_usdt   TEXT,
        req_btc    TEXT,
        bal_rub    REAL DEFAULT 0.0,
        bal_uah    REAL DEFAULT 0.0,
        bal_kzt    REAL DEFAULT 0.0,
        bal_byn    REAL DEFAULT 0.0,
        bal_ton    REAL DEFAULT 0.0,
        bal_stars  REAL DEFAULT 0.0,
        bal_usdt   REAL DEFAULT 0.0,
        bal_btc    REAL DEFAULT 0.0,
        ref_earned REAL DEFAULT 0.0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS deals (
        deal_id    TEXT PRIMARY KEY,
        seller_id  INTEGER,
        buyer_id   INTEGER,
        title      TEXT,
        amount     REAL,
        currency   TEXT,
        pay_method TEXT,
        role       TEXT DEFAULT 'seller',
        status     TEXT DEFAULT 'created'
    )''')
    conn.commit()
    conn.close()

init_db()

user_states = {}

# === ХЕЛПЕРИ ===
def get_lang(user_id):
    conn = sqlite3.connect('king_deals.db')
    c = conn.cursor()
    c.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] in ('ru','en') else 'ru'

def set_lang(user_id, lang):
    conn = sqlite3.connect('king_deals.db')
    conn.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def notify_owner(text):
    try:
        bot.send_message(NOTIFY_ID, text, parse_mode="HTML")
    except Exception:
        pass

def send_screen(chat_id, banner_path, text, markup, old_msg_id=None):
    if old_msg_id:
        try:
            bot.delete_message(chat_id, old_msg_id)
        except Exception:
            pass
    # Telegram не підтримує <blockquote> в caption — замінюємо
    clean = text.replace("<blockquote>", "<i>").replace("</blockquote>", "</i>")
    try:
        with open(banner_path, "rb") as f:
            bot.send_photo(chat_id, f, caption=clean, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        # fallback — текстове повідомлення без HTML
        try:
            import re
            plain = re.sub(r'<[^>]+>', '', clean)
            bot.send_message(chat_id, plain, reply_markup=markup)
        except Exception:
            pass

# === ТЕКСТИ ЕКРАНІВ ===
def welcome_text(lang):
    if lang == 'en':
        return (
            f"{E_BAG} <b>Welcome to King Deals</b> {E_HAND}\n\n"
            f"<blockquote>{E_FLASH} Your reliable P2P escrow:\n"
            f"{E_1} Automatic deals with NFT & gifts\n"
            f"{E_2} {E_SHIELD} Full protection for both sides\n"
            f"{E_3} {E_USDT} Referral program — 50% of commission\n"
            f"{E_4} {E_BOX} Item transfer via manager: @{SUPPORT_USER}</blockquote>"
        )
    return (
        f"{E_BAG} <b>Добро пожаловать в King Deals</b> {E_HAND}\n\n"
        f"<blockquote>{E_FLASH} Ваш надёжный P2P-гарант:\n"
        f"{E_1} Автоматические сделки с NFT и подарками\n"
        f"{E_2} {E_SHIELD} Полная защита обеих сторон\n"
        f"{E_3} {E_USDT} Реферальная программа — 50% от комиссии\n"
        f"{E_4} {E_BOX} Передача товаров через менеджера: @{SUPPORT_USER}</blockquote>"
    )

def main_markup(lang):
    tx = TEXTS[lang]
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(tx['btn_reqs'],   callback_data="menu_reqs"),
        types.InlineKeyboardButton(tx['btn_create'], callback_data="menu_create"),
    )
    kb.add(
        types.InlineKeyboardButton(tx['btn_balance'], callback_data="menu_balance"),
        types.InlineKeyboardButton(tx['btn_deals'],   callback_data="menu_deals"),
    )
    kb.add(
        types.InlineKeyboardButton(tx['btn_ref'],  callback_data="menu_ref"),
        types.InlineKeyboardButton(tx['btn_lang'], callback_data="menu_lang"),
    )
    kb.add(types.InlineKeyboardButton(tx['btn_support'], url=f"https://t.me/{SUPPORT_USER}"))
    return kb

# === /start ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid  = message.from_user.id
    uname = message.from_user.username or ""
    args = message.text.split()

    conn = sqlite3.connect('king_deals.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
    exists = c.fetchone()

    ref_id = None
    deal_link = None
    if len(args) > 1:
        p = args[1]
        if p.startswith("ref_"):
            try:
                ref_id = int(p.split("_")[1])
                if ref_id == uid:
                    ref_id = None
            except Exception:
                pass
        elif p.startswith("deal_"):
            deal_link = p.split("_")[1]

    if not exists:
        c.execute("INSERT INTO users (user_id, username, referrer_id) VALUES (?,?,?)", (uid, uname, ref_id))
        conn.commit()
        notify_owner(
            f"{E_USER} <b>Новый пользователь!</b>\n"
            f"ID: <code>{uid}</code>\n"
            f"Username: @{uname if uname else '—'}"
        )
    else:
        c.execute("UPDATE users SET username=? WHERE user_id=?", (uname, uid))
        conn.commit()
    conn.close()

    lang = get_lang(uid)
    if deal_link:
        show_deal_card(message, deal_link)
        return
    send_screen(message.chat.id, BANNER_MAIN, welcome_text(lang), main_markup(lang))

# === МОИ РЕКВИЗИТЫ ===
def screen_reqs(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    c    = conn.cursor()
    c.execute("SELECT req_ton, req_card, req_stars, req_usdt, req_btc FROM users WHERE user_id=?", (uid,))
    row = c.fetchone() or (None,)*5
    conn.close()
    ton, card, stars, usdt, btc = row

    def v(x): return f"<code>{x}</code>" if x else "—"

    if lang == 'en':
        text = (
            f"{E_PIN} <b>My Requisites</b>\n\n"
            f"<blockquote>{E_TON} TON wallet: {v(ton)}\n"
            f"{E_CARD} Card: {v(card)}\n"
            f"{E_STARS} Stars: {v(stars)}\n"
            f"{E_USDT} USDT (TRC20): {v(usdt)}\n"
            f"{E_BTC} BTC: {v(btc)}</blockquote>"
        )
    else:
        text = (
            f"{E_PIN} <b>Мои реквизиты</b>\n\n"
            f"<blockquote>{E_TON} TON-кошелёк: {v(ton)}\n"
            f"{E_CARD} Карта: {v(card)}\n"
            f"{E_STARS} Stars: {v(stars)}\n"
            f"{E_USDT} USDT (TRC20): {v(usdt)}\n"
            f"{E_BTC} BTC: {v(btc)}</blockquote>"
        )
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💎 TON-кошелёк" if lang=='ru' else "💎 TON wallet", callback_data="req_ton"),
        types.InlineKeyboardButton("🖥 Карта" if lang=='ru' else "🖥 Card", callback_data="req_card"),
    )
    kb.add(
        types.InlineKeyboardButton("⭐ @username (Stars)", callback_data="req_stars"),
        types.InlineKeyboardButton("💵 USDT (TRC20)", callback_data="req_usdt"),
    )
    kb.add(types.InlineKeyboardButton("₿ BTC", callback_data="req_btc"))
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_REQS, text, kb, old_msg_id)

# === БАЛАНС ===
def screen_balance(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    c    = conn.cursor()
    c.execute("SELECT bal_rub,bal_uah,bal_kzt,bal_byn,bal_ton,bal_stars,bal_usdt,bal_btc FROM users WHERE user_id=?", (uid,))
    b = c.fetchone() or (0,)*8
    conn.close()

    if lang == 'en':
        text = (
            f"{E_CARD} <b>Personal Account</b>\n"
            f"{E_USER} Telegram ID: <code>{uid}</code>\n\n"
            f"<blockquote>{E_MONEY} Balance:\n"
            f"🇷🇺 RUB: {b[0]}\n🇺🇦 UAH: {b[1]}\n🇰🇿 KZT: {b[2]}\n🇧🇾 BYN: {b[3]}\n"
            f"{E_TON} TON: {b[4]}\n{E_STARS} STARS: {b[5]}\n{E_USDT} USDT: {b[6]}\n{E_BTC} BTC: {b[7]}</blockquote>"
        )
    else:
        text = (
            f"{E_CARD} <b>Личный кабинет</b>\n"
            f"{E_USER} Telegram ID: <code>{uid}</code>\n\n"
            f"<blockquote>{E_MONEY} Баланс:\n"
            f"🇷🇺 RUB: {b[0]}\n🇺🇦 UAH: {b[1]}\n🇰🇿 KZT: {b[2]}\n🇧🇾 BYN: {b[3]}\n"
            f"{E_TON} TON: {b[4]}\n{E_STARS} STARS: {b[5]}\n{E_USDT} USDT: {b[6]}\n{E_BTC} BTC: {b[7]}</blockquote>"
        )
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(tx['btn_top_up'],  url=f"https://t.me/{SUPPORT_USER}"),
        types.InlineKeyboardButton(tx['btn_withdraw'], url=f"https://t.me/{SUPPORT_USER}"),
    )
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_BAL, text, kb, old_msg_id)

# === РЕФЕРАЛЫ ===
def screen_ref(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    bot_un = bot.get_me().username
    ref_url = f"https://t.me/{bot_un}?start=ref_{uid}"
    conn = sqlite3.connect('king_deals.db')
    c    = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (uid,))
    cnt = c.fetchone()[0]
    c.execute("SELECT ref_earned FROM users WHERE user_id=?", (uid,))
    earned_row = c.fetchone()
    earned = earned_row[0] if earned_row else 0.0
    conn.close()

    if lang == 'en':
        text = (
            f"{E_LINK} <b>Referral Program</b>\n\n"
            f"<blockquote>{E_LINK} Your link:\n<code>{ref_url}</code>\n"
            f"{E_PEOPLE} Referrals: <b>{cnt}</b>\n"
            f"{E_MONEY} Earned: <b>{earned} TON</b></blockquote>\n\n"
            f"{E_USDT} Bonus: <b>50%</b> of commission from each referral deal!"
        )
    else:
        text = (
            f"{E_LINK} <b>Реферальная программа</b>\n\n"
            f"<blockquote>{E_LINK} Ваша ссылка:\n<code>{ref_url}</code>\n"
            f"{E_PEOPLE} Рефералов: <b>{cnt}</b>\n"
            f"{E_MONEY} Заработано: <b>{earned} TON</b></blockquote>\n\n"
            f"{E_USDT} Бонус: <b>50%</b> от комиссии с каждой сделки реферала!"
        )
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔗 Скопировать реф. ссылку" if lang=='ru' else "🔗 Copy ref link", callback_data="ref_copy"))
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_REF, text, kb, old_msg_id)

# === МОИ СДЕЛКИ ===
def screen_deals(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    c    = conn.cursor()
    c.execute(
        "SELECT deal_id,title,amount,currency,status FROM deals WHERE seller_id=? OR buyer_id=? ORDER BY rowid DESC LIMIT 10",
        (uid, uid)
    )
    deals = c.fetchall()
    conn.close()
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    if not deals:
        text = f"{E_BOX} <b>{'No deals yet.' if lang=='en' else 'Сделок пока нет.'}</b>"
    else:
        title_line = "📋 <b>Your deals (last 10):</b>\n\n" if lang=='en' else "📋 <b>Ваши сделки (последние 10):</b>\n\n"
        text = title_line
        for d in deals:
            did, dtitle, amt, cur, st = d
            st_text = tx['deal_status'].get(st, st)
            text += f"• <b>{html_module.escape(str(dtitle))}</b> — {amt} {html_module.escape(str(cur))}\n  ID: <code>{did}</code> | {st_text}\n\n"
    send_screen(chat_id, BANNER_DEALS, text, kb, old_msg_id)

# === ЯЗЫК ===
def screen_lang(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    text = f"{E_GLOBE} <b>Choose a language / Выберите язык:</b>"
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
        types.InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en"),
    )
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_MAIN, text, kb, old_msg_id)

# === СОЗДАТЬ СДЕЛКУ — ВЫБОР РОЛИ ===
def screen_create_role(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    if lang == 'en':
        text = (
            f"{E_BAG} <b>New Deal</b>\n\n"
            f"<blockquote>{E_CLOUD} What is your role?</blockquote>\n"
            f"{E_CROWN} <b>Seller</b> — you are selling an item/service...\n"
            f"{E_CART} <b>Buyer</b> — you are paying..."
        )
        btn_sell = "👑 I'm the Seller"
        btn_buy  = "🛒 I'm the Buyer"
    else:
        text = (
            f"{E_BAG} <b>Новая сделка</b>\n\n"
            f"<blockquote>{E_CLOUD} Кем вы выступаете?</blockquote>\n"
            f"{E_CROWN} <b>Продавец</b> — вы продаёте товар/услугу...\n"
            f"{E_CART} <b>Покупатель</b> — вы платите..."
        )
        btn_sell = "🔥 Я продавец"
        btn_buy  = "🛒 Я покупатель"
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(btn_sell, callback_data="role_seller"),
        types.InlineKeyboardButton(btn_buy,  callback_data="role_buyer"),
    )
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_CREATE, text, kb, old_msg_id)

# === СПОСОБ ОПЛАТЫ ===
def screen_pay_method(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    if lang == 'en':
        text = (
            f"{E_1} <b>Payment method:</b>\n\n"
            f"<blockquote>{E_CLOUD} How will the buyer pay?</blockquote>"
        )
    else:
        text = (
            f"{E_1} <b>Способ получения оплаты:</b>\n\n"
            f"<blockquote>{E_CLOUD} Как покупатель переведёт?</blockquote>"
        )
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🖥 Карта" if lang=='ru' else "🖥 Card",  callback_data="pm_card"),
        types.InlineKeyboardButton("⭐ Stars",                                 callback_data="pm_stars"),
    )
    kb.add(types.InlineKeyboardButton(f"💰 {'Крипта' if lang=='ru' else 'Crypto'}", callback_data="pm_crypto"))
    kb.add(
        types.InlineKeyboardButton(tx['btn_back_step'], callback_data="menu_create"),
        types.InlineKeyboardButton(tx['btn_back'],      callback_data="menu_main"),
    )
    send_screen(chat_id, BANNER_CREATE, text, kb, old_msg_id)

# === ВЫБОР КРИПТЫ ===
def screen_crypto_choose(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    text = (
        f"{E_1} <b>{'Choose cryptocurrency:' if lang=='en' else 'Выберите криптовалюту:'}</b>\n\n"
        f"<blockquote>{E_CLOUD} {'Which cryptocurrency?' if lang=='en' else 'Какую криптовалюту принимаете?'}</blockquote>"
    )
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("💎 TON",  callback_data="cur_TON"),
        types.InlineKeyboardButton("💵 USDT", callback_data="cur_USDT"),
        types.InlineKeyboardButton("₿ BTC",   callback_data="cur_BTC"),
    )
    kb.add(
        types.InlineKeyboardButton(tx['btn_back_step'], callback_data="pm_back"),
        types.InlineKeyboardButton(tx['btn_back'],      callback_data="menu_main"),
    )
    send_screen(chat_id, BANNER_CREATE, text, kb, old_msg_id)

# === ВЫБОР ВАЛЮТЫ КАРТЫ ===
def screen_card_currency(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    text = f"{E_BANK} <b>{'Choose card currency:' if lang=='en' else 'Выберите валюту карты:'}</b>"
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🇷🇺 RUB", callback_data="cur_RUB"),
        types.InlineKeyboardButton("🇺🇦 UAH", callback_data="cur_UAH"),
        types.InlineKeyboardButton("🇰🇿 KZT", callback_data="cur_KZT"),
        types.InlineKeyboardButton("🇧🇾 BYN", callback_data="cur_BYN"),
    )
    kb.add(
        types.InlineKeyboardButton(tx['btn_back_step'], callback_data="pm_back"),
        types.InlineKeyboardButton(tx['btn_back'],      callback_data="menu_main"),
    )
    send_screen(chat_id, BANNER_CREATE, text, kb, old_msg_id)

# === ВВОД НАЗВИ/СУМИ ===
def ask_deal_title(chat_id, uid, old_msg_id=None):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    text = (
        f"{E_BOX} <b>{'Enter item/service name:' if lang=='en' else 'Введите название товара/услуги:'}</b>\n"
        f"<i>{'Example: NFT, Steam account, etc.' if lang=='en' else 'Пример: NFT, аккаунт Steam, и т.д.'}</i>"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_CREATE, text, kb, old_msg_id)
    user_states[uid] = user_states.get(uid, {})
    user_states[uid]['step'] = 'deal_title'

def ask_deal_amount(chat_id, uid):
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    kb   = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(
        chat_id, BANNER_CREATE,
        f"{E_MONEY} <b>{'Enter the amount:' if lang=='en' else 'Укажите сумму:'}</b>\n"
        f"<i>{'Numbers only, e.g.: 500' if lang=='en' else 'Только число, например: 500'}</i>",
        kb
    )

# === ПОКРОКОВІ КРОКИ ===
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) is not None)
def handle_steps(message):
    uid   = message.from_user.id
    state = user_states[uid]
    step  = state.get('step')
    lang  = get_lang(uid)
    tx    = TEXTS[lang]

    kb_back = types.InlineKeyboardMarkup()
    kb_back.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))

    # --- реквизиты ---
    if step == 'req_ton':
        addr = message.text.strip()
        if len(addr) != 48 or addr[:2] not in ('UQ','EQ'):
            send_screen(message.chat.id, BANNER_BIND,
                f"{E_CROSS} <b>Неверный формат!</b>\n48 символов, начинается UQ или EQ.", kb_back)
            return
        _save_req(uid, 'req_ton', addr)
        del user_states[uid]
        send_screen(message.chat.id, BANNER_BIND, f"{E_DONE} <b>TON-кошелёк сохранён!</b>", kb_back)

    elif step == 'req_card':
        num = message.text.replace(' ','')
        if not num.isdigit() or len(num) < 13:
            send_screen(message.chat.id, BANNER_BIND,
                f"{E_CROSS} <b>Неверный номер карты!</b>\nТолько цифры.", kb_back)
            return
        _save_req(uid, 'req_card', num)
        del user_states[uid]
        send_screen(message.chat.id, BANNER_BIND, f"{E_DONE} <b>Карта сохранена!</b>", kb_back)

    elif step == 'req_stars':
        un = message.text.strip().lstrip('@')
        _save_req(uid, 'req_stars', f"@{un}")
        del user_states[uid]
        send_screen(message.chat.id, BANNER_BIND, f"{E_DONE} <b>Stars username сохранён!</b>", kb_back)

    elif step == 'req_usdt':
        addr = message.text.strip()
        if not addr.startswith('T') or len(addr) < 30:
            send_screen(message.chat.id, BANNER_BIND,
                f"{E_CROSS} <b>Неверный USDT TRC20 адрес!</b>\nНачинается на T, ~34 символа.", kb_back)
            return
        _save_req(uid, 'req_usdt', addr)
        del user_states[uid]
        send_screen(message.chat.id, BANNER_BIND, f"{E_DONE} <b>USDT (TRC20) сохранён!</b>", kb_back)

    elif step == 'req_btc':
        addr = message.text.strip()
        if len(addr) < 25:
            send_screen(message.chat.id, BANNER_BIND,
                f"{E_CROSS} <b>Неверный BTC адрес!</b>", kb_back)
            return
        _save_req(uid, 'req_btc', addr)
        del user_states[uid]
        send_screen(message.chat.id, BANNER_BIND, f"{E_DONE} <b>BTC-адрес сохранён!</b>", kb_back)

    # --- сделка ---
    elif step == 'deal_title':
        user_states[uid]['title'] = message.text
        user_states[uid]['step']  = 'deal_amount'
        ask_deal_amount(message.chat.id, uid)

    elif step == 'deal_amount':
        try:
            amt = float(message.text.replace(',','.'))
            if amt <= 0: raise ValueError
        except ValueError:
            send_screen(message.chat.id, BANNER_CREATE,
                f"{E_CROSS} <b>Введите положительное число!</b>", kb_back)
            return
        user_states[uid]['amount'] = amt
        currency = user_states[uid].get('currency')
        # якщо валюта вже вибрана (крипта/stars) — одразу створюємо
        if currency:
            _finish_deal(message.chat.id, uid)
        else:
            # карта — просимо вибрати валюту
            screen_card_currency(message.chat.id, uid)

def _save_req(uid, col, val):
    conn = sqlite3.connect('king_deals.db')
    conn.execute(f"UPDATE users SET {col}=? WHERE user_id=?", (val, uid))
    conn.commit()
    conn.close()

def _finish_deal(chat_id, uid):
    state    = user_states.pop(uid, {})
    lang     = get_lang(uid)
    tx       = TEXTS[lang]
    title    = state.get('title','—')
    amount   = state.get('amount', 0)
    currency = state.get('currency','?')
    role     = state.get('role','seller')

    deal_id = ''.join(random.choices(string.ascii_letters+string.digits, k=8))
    bot_un  = bot.get_me().username
    deal_url = f"https://t.me/{bot_un}?start=deal_{deal_id}"

    conn = sqlite3.connect('king_deals.db')
    conn.execute(
        "INSERT INTO deals (deal_id,seller_id,title,amount,currency,role) VALUES (?,?,?,?,?,?)",
        (deal_id, uid, title, amount, currency, role)
    )
    conn.commit()
    conn.close()

    notify_owner(
        f"{E_HAND} <b>Новая сделка создана!</b>\n"
        f"ID: <code>{deal_id}</code>\n"
        f"Продавец: <code>{uid}</code>\n"
        f"Товар: {html_module.escape(title)}\n"
        f"Сумма: {amount} {currency}"
    )

    if lang == 'en':
        text = (
            f"{E_BOX} <b>Deal created!</b>\n\n"
            f"📝 Item: {html_module.escape(title)}\n"
            f"💵 Amount: {amount} {currency}\n\n"
            f"{E_LINK} Buyer link:\n<code>{deal_url}</code>\n\n"
            f"Send this link to the buyer."
        )
    else:
        text = (
            f"{E_BOX} <b>Сделка создана!</b>\n\n"
            f"📝 Товар: {html_module.escape(title)}\n"
            f"💵 Сумма: {amount} {currency}\n\n"
            f"{E_LINK} Ссылка для покупателя:\n<code>{deal_url}</code>\n\n"
            f"Перешлите эту ссылку покупателю."
        )
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
    send_screen(chat_id, BANNER_CREATE, text, kb)

# === КАРТОЧКА СДЕЛКИ ДЛЯ ПОКУПАТЕЛЯ ===
def show_deal_card(message, deal_id):
    conn = sqlite3.connect('king_deals.db')
    c    = conn.cursor()
    c.execute("SELECT seller_id,title,amount,currency,status FROM deals WHERE deal_id=?", (deal_id,))
    deal = c.fetchone()
    conn.close()

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(TEXTS['ru']['btn_back'], callback_data="menu_main"))

    if not deal:
        send_screen(message.chat.id, BANNER_MAIN, f"{E_CROSS} Сделка не найдена.", kb)
        return
    seller_id, title, amount, currency, status = deal
    if status != 'created':
        send_screen(message.chat.id, BANNER_MAIN, f"{E_CROSS} Сделка уже недействительна.", kb)
        return
    if seller_id == message.from_user.id:
        send_screen(message.chat.id, BANNER_MAIN, f"{E_CROSS} Нельзя открыть свою сделку.", kb)
        return
    kb2 = types.InlineKeyboardMarkup()
    kb2.add(
        types.InlineKeyboardButton("💳 Оплатить с баланса", callback_data=f"pay_{deal_id}"),
        types.InlineKeyboardButton("❌ Отказаться",          callback_data=f"cancel_{deal_id}"),
    )
    send_screen(
        message.chat.id, BANNER_CREATE,
        f"{E_HAND} <b>Вам предложена сделка</b>\n\n"
        f"{E_BOX} Товар: {html_module.escape(str(title))}\n"
        f"{E_MONEY} Сумма: {amount} {currency}",
        kb2
    )

# === CALLBACK ОБРОБНИК ===
@bot.callback_query_handler(func=lambda call: True)
def handle_cb(call):
    uid  = call.from_user.id
    mid  = call.message.message_id
    cid  = call.message.chat.id
    lang = get_lang(uid)
    tx   = TEXTS[lang]
    bot.answer_callback_query(call.id)
    d    = call.data

    if d == "menu_main":
        send_screen(cid, BANNER_MAIN, welcome_text(lang), main_markup(lang), mid)
    elif d == "menu_reqs":
        screen_reqs(cid, uid, mid)
    elif d == "menu_balance":
        screen_balance(cid, uid, mid)
    elif d == "menu_deals":
        screen_deals(cid, uid, mid)
    elif d == "menu_ref":
        screen_ref(cid, uid, mid)
    elif d == "menu_lang":
        screen_lang(cid, uid, mid)
    elif d == "menu_create":
        screen_create_role(cid, uid, mid)

    # мова
    elif d in ("set_lang_ru","set_lang_en"):
        new_lang = d.split("_")[2]
        set_lang(uid, new_lang)
        send_screen(cid, BANNER_MAIN, welcome_text(new_lang), main_markup(new_lang), mid)

    # реквізити
    elif d == "req_ton":
        user_states[uid] = {'step':'req_ton'}
        try: bot.delete_message(cid, mid)
        except: pass
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_BIND,
            f"{E_TON} <b>Введите TON-адрес кошелька:</b>\n"
            f"<i>(48 символов, начинается UQ или EQ)</i>", kb)
    elif d == "req_card":
        user_states[uid] = {'step':'req_card'}
        try: bot.delete_message(cid, mid)
        except: pass
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_BIND,
            f"{E_CARD} <b>Введите номер банковской карты:</b>\n<i>(Только цифры)</i>", kb)
    elif d == "req_stars":
        user_states[uid] = {'step':'req_stars'}
        try: bot.delete_message(cid, mid)
        except: pass
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_BIND,
            f"{E_STARS} <b>Введите ваш @username для получения Stars:</b>", kb)
    elif d == "req_usdt":
        user_states[uid] = {'step':'req_usdt'}
        try: bot.delete_message(cid, mid)
        except: pass
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_BIND,
            f"{E_USDT} <b>Введите USDT TRC20 адрес:</b>\n<i>(Начинается на T)</i>", kb)
    elif d == "req_btc":
        user_states[uid] = {'step':'req_btc'}
        try: bot.delete_message(cid, mid)
        except: pass
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_BIND,
            f"{E_BTC} <b>Введите BTC-адрес кошелька:</b>", kb)

    # роль у угоді
    elif d == "role_seller":
        user_states[uid] = {'role':'seller'}
        screen_pay_method(cid, uid, mid)
    elif d == "role_buyer":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        if uid in user_states:
            del user_states[uid]
        send_screen(cid, BANNER_CREATE,
            f"🛒 <b>{'To join a deal, open the link from the seller.' if lang=='en' else 'Чтобы вступить в сделку — откройте ссылку от продавца.'}</b>\n\n"
            f"<i>{'The seller sends you a link like: t.me/bot?start=deal_XXXX' if lang=='en' else 'Продавец пришлёт вам ссылку вида: t.me/bot?start=deal_XXXX'}</i>",
            kb, mid)

    # спосіб оплати
    elif d == "pm_card":
        user_states[uid]['pay_method'] = 'card'
        screen_card_currency(cid, uid, mid)
    elif d == "pm_stars":
        user_states[uid]['pay_method'] = 'stars'
        user_states[uid]['currency']   = 'STARS'
        ask_deal_title(cid, uid, mid)
    elif d == "pm_crypto":
        user_states[uid]['pay_method'] = 'crypto'
        screen_crypto_choose(cid, uid, mid)
    elif d == "pm_back":
        screen_pay_method(cid, uid, mid)

    # валюта/крипта
    elif d.startswith("cur_"):
        currency = d.split("_")[1]
        if uid in user_states:
            user_states[uid]['currency'] = currency
            step = user_states[uid].get('step')
            if step == 'deal_amount':
                # юзер вже ввів суму, тепер вибрав валюту
                _finish_deal(cid, uid)
            else:
                ask_deal_title(cid, uid, mid)
        else:
            send_screen(cid, BANNER_MAIN, welcome_text(lang), main_markup(lang), mid)

    # реферальна кнопка копіювання
    elif d == "ref_copy":
        bot_un = bot.get_me().username
        ref_url = f"https://t.me/{bot_un}?start=ref_{uid}"
        bot.answer_callback_query(call.id, ref_url, show_alert=True)

    # оплата угоди
    elif d.startswith("pay_"):
        deal_id = d.split("_")[1]
        conn = sqlite3.connect('king_deals.db')
        c    = conn.cursor()
        c.execute("SELECT seller_id,title,amount,currency,status FROM deals WHERE deal_id=?", (deal_id,))
        deal = c.fetchone()
        if not deal or deal[4] != 'created':
            bot.answer_callback_query(call.id, "Сделка недействительна.", show_alert=True)
            conn.close()
            return
        seller_id, title, amount, currency, _ = deal
        bal_col = f"bal_{currency.lower()}"
        try:
            c.execute(f"SELECT {bal_col} FROM users WHERE user_id=?", (uid,))
        except Exception:
            bot.answer_callback_query(call.id, "Ошибка валюты.", show_alert=True)
            conn.close()
            return
        row = c.fetchone()
        buyer_bal = row[0] if row else 0.0
        if buyer_bal < amount:
            bot.answer_callback_query(call.id,
                f"Недостаточно средств! Нужно {amount} {currency}, у вас {buyer_bal}.", show_alert=True)
            conn.close()
            return
        c.execute(f"UPDATE users SET {bal_col}={bal_col}-? WHERE user_id=?", (amount, uid))
        c.execute("UPDATE deals SET buyer_id=?,status='paid' WHERE deal_id=?", (uid, deal_id))
        conn.commit()
        conn.close()

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(f"{E_DONE} Товар получил, отпустить средства", callback_data=f"release_{deal_id}"))
        send_screen(cid, BANNER_CREATE,
            f"{E_CHECK} <b>Оплата прошла!</b>\n{E_LOCK} Средства заморожены гарантом.\n{E_BOX} Для получения: @{SUPPORT_USER}",
            kb, mid)
        with open(BANNER_CREATE,"rb") as f:
            bot.send_photo(seller_id, f,
                caption=f"{E_TIME} <b>Ваша сделка оплачена!</b>\nПередайте товар через @{SUPPORT_USER}.",
                parse_mode="HTML")

    elif d.startswith("cancel_"):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_MAIN, f"{E_CANCEL} Вы отказались от сделки.", kb, mid)

    elif d.startswith("release_"):
        deal_id = d.split("_")[1]
        conn = sqlite3.connect('king_deals.db')
        c    = conn.cursor()
        c.execute("SELECT seller_id,buyer_id,title,amount,currency,status FROM deals WHERE deal_id=?", (deal_id,))
        deal = c.fetchone()
        if not deal or deal[5] != 'paid':
            bot.answer_callback_query(call.id, "Ошибка.", show_alert=True)
            conn.close()
            return
        seller_id, buyer_id, title, amount, currency, _ = deal
        bal_col = f"bal_{currency.lower()}"
        try:
            c.execute(f"UPDATE users SET {bal_col}={bal_col}+? WHERE user_id=?", (amount, seller_id))
        except Exception:
            conn.close()
            return
        c.execute("UPDATE deals SET status='completed' WHERE deal_id=?", (deal_id,))
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (seller_id,))
        ref = c.fetchone()
        if ref and ref[0]:
            bonus = round(amount * 0.025, 8)
            try:
                c.execute(f"UPDATE users SET {bal_col}={bal_col}+?, ref_earned=ref_earned+? WHERE user_id=?",
                    (bonus, bonus, ref[0]))
                with open(BANNER_REF,"rb") as f:
                    bot.send_photo(ref[0], f,
                        caption=f"{E_COIN} Реферальный бонус: +{bonus} {currency}!", parse_mode="HTML")
            except Exception:
                pass
        conn.commit()
        conn.close()
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        send_screen(cid, BANNER_MAIN,
            f"{E_DONE} <b>Сделка завершена!</b>\nСпасибо, что используете King Deals! {E_HAND}", kb, mid)
        with open(BANNER_BAL,"rb") as f:
            bot.send_photo(seller_id, f,
                caption=f"{E_MONEY} <b>Сделка завершена!</b>\nВам зачислено {amount} {currency}.", parse_mode="HTML")

# === /add (поповнення балансу) ===
@bot.message_handler(commands=['add'])
def cmd_add(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.send_message(message.chat.id, "Формат: /add user_id сумма валюта")
        return
    try:
        tid    = int(parts[1])
        amount = float(parts[2])
        cur    = parts[3].lower()
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат.")
        return

    col_map = {
        'rub':'bal_rub','uah':'bal_uah','kzt':'bal_kzt','byn':'bal_byn',
        'ton':'bal_ton','stars':'bal_stars','usdt':'bal_usdt','btc':'bal_btc',
    }
    col = col_map.get(cur)
    if not col:
        bot.send_message(message.chat.id, f"Валюта не распознана. Доступные: {', '.join(col_map.keys())}")
        return

    conn = sqlite3.connect('king_deals.db')
    c    = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id=?", (tid,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id) VALUES (?)", (tid,))
    c.execute(f"UPDATE users SET {col}={col}+? WHERE user_id=?", (amount, tid))
    c.execute(f"SELECT {col} FROM users WHERE user_id=?", (tid,))
    new_bal = c.fetchone()[0]
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id,
        f"{E_DONE} Зачислено <b>{amount} {cur.upper()}</b> → <code>{tid}</code>\nНовый баланс: <b>{new_bal}</b>",
        parse_mode="HTML")

# === KEEP-ALIVE + САМОПІНГ ===
app = Flask(__name__)

@app.route('/')
def home():
    return "King Deals is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)

def self_ping():
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        return
    while True:
        time.sleep(840)
        try:
            requests.get(url, timeout=10)
            print("Self-ping OK")
        except Exception as e:
            print(f"Self-ping error: {e}")

# === ЗАПУСК ===
if __name__ == "__main__":
    if not os.environ.get("RENDER"):
        print("Не Render — бот не запускається.")
        exit(0)
    print("King Deals бот запущено на Render!")
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=self_ping,  daemon=True).start()
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    time.sleep(5)
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as e:
            print(f"Polling error: {e}. Retry in 10s...")
            time.sleep(10)
