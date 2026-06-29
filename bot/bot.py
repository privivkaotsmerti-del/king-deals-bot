import os
import html as html_module
import telebot
from telebot import types
import sqlite3
import random
import string

# === НАСТРОЙКИ БОТА ===
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 123456789
SUPPORT_USER = "king_helper"

bot = telebot.TeleBot(TOKEN)

# === ТЕЛЕГРАМ ПРЕМИУМ ЭМОДЗИ ===
E_BAG    = '<tg-emoji emoji-id="5893255507380014983">💼</tg-emoji>'
E_HAND   = '<tg-emoji emoji-id="5395732581780040886">🤝</tg-emoji>'
E_FLASH  = '<tg-emoji emoji-id="5456140674028019486">⚡️</tg-emoji>'
E_1      = '<tg-emoji emoji-id="5794164805065514131">1️⃣</tg-emoji>'
E_2      = '<tg-emoji emoji-id="5794085322400733645">2️⃣</tg-emoji>'
E_SHIELD = '<tg-emoji emoji-id="5902016123972358349">🛡</tg-emoji>'
E_3      = '<tg-emoji emoji-id="5794280000383358988">3️⃣</tg-emoji>'
E_COIN   = '<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji>'
E_4      = '<tg-emoji emoji-id="5794241397217304511">4️⃣</tg-emoji>'
E_BOX    = '<tg-emoji emoji-id="5778672437122045013">📦</tg-emoji>'
E_LIGHT  = '<tg-emoji emoji-id="5893290369629556374">💡</tg-emoji>'
E_FLASH2 = '<tg-emoji emoji-id="5258203794772085854">⚡️</tg-emoji>'
E_DIAMOND= '<tg-emoji emoji-id="5235630047959727475">💎</tg-emoji>'
E_PLANE  = '<tg-emoji emoji-id="5296432770392791386">✈️</tg-emoji>'
E_CHECK  = '<tg-emoji emoji-id="5294515522761663291">✅</tg-emoji>'
E_DEV    = '<tg-emoji emoji-id="5362079447136610876">👨‍💻</tg-emoji>'
E_STAR   = '<tg-emoji emoji-id="5463289097336405244">⭐️</tg-emoji>'
E_CROSS  = '<tg-emoji emoji-id="5893163582194978381">❌</tg-emoji>'
E_TIME   = '<tg-emoji emoji-id="5893102202817352158">🕐</tg-emoji>'
E_PHONE  = '<tg-emoji emoji-id="5893297890117292323">📞</tg-emoji>'
E_MONEY  = '<tg-emoji emoji-id="5893473283696759404">💰</tg-emoji>'
E_CARD   = '<tg-emoji emoji-id="5902056028513505203">💳</tg-emoji>'
E_USER   = '<tg-emoji emoji-id="5902335789798265487">👤</tg-emoji>'
E_LINK   = '<tg-emoji emoji-id="5902449142575141204">🔗</tg-emoji>'

# === ПЕРЕВОДЫ (RU / EN) ===
TEXTS = {
    'ru': {
        'btn_create':     "🤝 Создать сделку",
        'btn_deals':      "🗂 Мои сделки",
        'btn_balance':    "💰 Баланс",
        'btn_reqs':       "💳 Мои реквизиты",
        'btn_ref':        "👥 Рефералы",
        'btn_support':    "💬 Поддержка",
        'btn_lang':       "🌐 English",
        'btn_back':       "🔙 Назад",
        'btn_top_up':     "💳 Пополнить баланс",
        'btn_withdraw':   "💸 Вывести средства",
        'btn_bind':       "➕ Привязать реквизиты",
        'btn_change_req': "🔄 Изменить реквизиты",
        'btn_create_deal':"🤝 Создать сделку",
        'btn_start_menu': "▶️ Открыть меню",
        'deals_empty':    "📭 <b>У вас пока нет сделок.</b>",
        'deals_title':    "📋 <b>Ваши сделки (последние 10):</b>\n\n",
        'deal_status': {
            'created':   '🕐 Ожидает оплаты',
            'paid':      '🔒 Оплачена, ждёт подтверждения',
            'completed': '✅ Завершена',
        },
        'bind_choose':    "Пожалуйста, выберите способ для привязки реквизитов:",
        'bind_country':   "💳 Выберите страну вашего банка для привязки карты:",
        'bind_card_send': "📥 Отправьте номер вашей банковской карты ({country}):\n(Только цифры, без букв и лишних символов)",
        'bind_ton_send':  "📥 Отправьте ваш TON-адрес кошелька:\n(48 символов, начинается на UQ или EQ)",
        'lang_switched':  "🌐 Язык изменён на <b>Русский</b>",
    },
    'en': {
        'btn_create':     "🤝 Create Deal",
        'btn_deals':      "🗂 My Deals",
        'btn_balance':    "💰 Balance",
        'btn_reqs':       "💳 My Requisites",
        'btn_ref':        "👥 Referrals",
        'btn_support':    "💬 Support",
        'btn_lang':       "🌐 Русский",
        'btn_back':       "🔙 Back",
        'btn_top_up':     "💳 Top Up Balance",
        'btn_withdraw':   "💸 Withdraw Funds",
        'btn_bind':       "➕ Add Requisites",
        'btn_change_req': "🔄 Change Requisites",
        'btn_create_deal':"🤝 Create Deal",
        'btn_start_menu': "▶️ Open Menu",
        'deals_empty':    "📭 <b>You have no deals yet.</b>",
        'deals_title':    "📋 <b>Your deals (last 10):</b>\n\n",
        'deal_status': {
            'created':   '🕐 Awaiting payment',
            'paid':      '🔒 Paid, awaiting confirmation',
            'completed': '✅ Completed',
        },
        'bind_choose':    "Please choose a method to link your requisites:",
        'bind_country':   "💳 Choose your bank's country:",
        'bind_card_send': "📥 Send your bank card number ({country}):\n(Digits only, no letters or extra symbols)",
        'bind_ton_send':  "📥 Send your TON wallet address:\n(48 characters, starts with UQ or EQ)",
        'lang_switched':  "🌐 Language changed to <b>English</b>",
    },
}

def get_lang(user_id):
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] in ('ru', 'en') else 'ru'

def set_lang(user_id, lang):
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def build_welcome_text(lang):
    if lang == 'en':
        return (
            f"{E_BAG} <b>Welcome to King Deals</b> {E_HAND}\n\n"
            f"{E_FLASH} Your reliable P2P escrow service:\n"
            f"{E_1} Automatic deals with NFTs & gifts\n"
            f"{E_2} {E_SHIELD} Full protection for both sides\n"
            f"{E_3} {E_COIN} Referral program — 50% of commission\n"
            f"{E_4} {E_BOX} Item transfer via manager: @{SUPPORT_USER}"
        )
    return (
        f"{E_BAG} <b>Добро пожаловать в King Deals</b> {E_HAND}\n\n"
        f"{E_FLASH} Ваш надёжный P2P-гарант:\n"
        f"{E_1} Автоматические сделки с NFT и подарками\n"
        f"{E_2} {E_SHIELD} Полная защита обеих сторон\n"
        f"{E_3} {E_COIN} Реферальная программа — 50% от комиссии\n"
        f"{E_4} {E_BOX} Передача товаров через менеджера: @{SUPPORT_USER}"
    )

# === БАЗА ДАННЫХ SQLite ===
def init_db():
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'ru',
            referrer_id INTEGER,
            req_type TEXT,
            req_value TEXT,
            bal_uah REAL DEFAULT 0.0,
            bal_rub REAL DEFAULT 0.0,
            bal_kzt REAL DEFAULT 0.0,
            bal_byn REAL DEFAULT 0.0,
            bal_uzs REAL DEFAULT 0.0,
            bal_ton REAL DEFAULT 0.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            seller_id INTEGER,
            buyer_id INTEGER,
            title TEXT,
            amount REAL,
            currency TEXT,
            status TEXT DEFAULT 'created'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

user_states = {}

# === РЕГИСТРАЦИЯ КОМАНД БОТА (меню "/" у поля ввода) ===
def register_bot_commands():
    bot.set_my_commands([
        types.BotCommand("start", "Открыть главное меню")
    ])

register_bot_commands()

# === ГЛАВНОЕ МЕНЮ (inline — отображается под сообщением) ===
def get_welcome_inline(lang='ru'):
    tx = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(tx['btn_create'],  callback_data="menu_create"),
        types.InlineKeyboardButton(tx['btn_deals'],   callback_data="menu_deals"),
        types.InlineKeyboardButton(tx['btn_balance'], callback_data="menu_balance"),
        types.InlineKeyboardButton(tx['btn_reqs'],    callback_data="menu_reqs"),
        types.InlineKeyboardButton(tx['btn_ref'],     callback_data="menu_ref"),
        types.InlineKeyboardButton(tx['btn_support'], url=f"https://t.me/{SUPPORT_USER}"),
    )
    markup.add(types.InlineKeyboardButton(tx['btn_lang'], callback_data="lang_toggle"))
    return markup

def send_main_menu(chat_id, user_id, lang):
    bot.send_message(
        chat_id,
        build_welcome_text(lang),
        parse_mode="HTML",
        reply_markup=get_welcome_inline(lang)
    )

# === /start ===
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    args = message.text.split()

    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user_exists = cursor.fetchone()

    referrer_id = None
    deal_link_id = None

    if len(args) > 1:
        param = args[1]
        if param.startswith('ref_'):
            try:
                referrer_id = int(param.split('_')[1])
                if referrer_id == user_id:
                    referrer_id = None
            except Exception:
                pass
        elif param.startswith('deal_'):
            deal_link_id = param.split('_')[1]

    if not user_exists:
        cursor.execute(
            "INSERT INTO users (user_id, referrer_id) VALUES (?, ?)",
            (user_id, referrer_id)
        )
        conn.commit()

    conn.close()

    lang = get_lang(user_id)

    if deal_link_id:
        show_deal_card(message, deal_link_id)
        return

    send_main_menu(message.chat.id, user_id, lang)

# === МОИ РЕКВИЗИТЫ ===
def my_requisites(message, user_id=None, chat_id=None, edit_message_id=None):
    user_id = user_id or message.from_user.id
    chat_id = chat_id or message.chat.id
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT req_type, req_value FROM users WHERE user_id = ?", (user_id,))
    req = cursor.fetchone()
    conn.close()

    markup = types.InlineKeyboardMarkup()

    if req and req[0] and req[1]:
        if lang == 'en':
            text = (
                f"{E_CARD} <b>Your saved payout requisites:</b>\n\n"
                f"• Method: <code>{req[0]}</code>\n"
                f"• Details: <code>{req[1]}</code>"
            )
        else:
            text = (
                f"{E_CARD} <b>Ваши сохраненные реквизиты для выплат:</b>\n\n"
                f"• Способ: <code>{req[0]}</code>\n"
                f"• Данные: <code>{req[1]}</code>"
            )
        markup.add(types.InlineKeyboardButton(tx['btn_change_req'], callback_data="bind_start"))
    else:
        if lang == 'en':
            text = f"{E_CROSS} <b>You have no payout requisites linked yet!</b>"
        else:
            text = f"{E_CROSS} <b>У вас пока не привязаны реквизиты для выплат!</b>"
        markup.add(types.InlineKeyboardButton(tx['btn_bind'], callback_data="bind_start"))

    markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))

    if edit_message_id:
        bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# === СОЗДАТЬ СДЕЛКУ ===
def create_deal_start(message, user_id=None, chat_id=None, edit_message_id=None):
    user_id = user_id or message.from_user.id
    chat_id = chat_id or message.chat.id
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT req_type, req_value FROM users WHERE user_id = ?", (user_id,))
    req = cursor.fetchone()
    conn.close()

    back_markup = types.InlineKeyboardMarkup()
    back_markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))

    if not req or not req[0] or not req[1]:
        markup = types.InlineKeyboardMarkup()
        if lang == 'en':
            markup.add(types.InlineKeyboardButton("💳 Bank Card", callback_data="bind_card_sng"))
            markup.add(types.InlineKeyboardButton("💎 TON Address", callback_data="bind_ton"))
            text = (
                f"{E_CROSS} <b>Error:</b> To create a deal you must have requisites linked!\n\n"
                f"Please choose a method to link your requisites:"
            )
        else:
            markup.add(types.InlineKeyboardButton("💳 Банковская карта", callback_data="bind_card_sng"))
            markup.add(types.InlineKeyboardButton("💎 TON Адрес", callback_data="bind_ton"))
            text = (
                f"{E_CROSS} <b>Ошибка:</b> Для создания сделки у вас должны быть привязаны реквизиты!\n\n"
                f"Пожалуйста, выберите способ для привязки реквизитов:"
            )
        markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        if edit_message_id:
            bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    else:
        if lang == 'en':
            text = (
                f"{E_BOX} <b>Enter the name of the item or service for the deal:</b>\n"
                f"<i>(Example: 1 NFT, Steam account, crypto wallet, etc.)</i>"
            )
        else:
            text = (
                f"{E_BOX} <b>Введите название товара или услуги для сделки:</b>\n"
                f"<i>(Пример: 1 NFT, аккаунт в Стиме, крипто-кошелек и т.д.)</i>"
            )
        if edit_message_id:
            bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=back_markup)
        else:
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=back_markup)
        user_states[user_id] = {"step": "deal_title"}

# === ПОШАГОВЫЙ ВВОД ===
@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) is not None)
def handle_steps(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    step = state.get("step")
    lang = get_lang(user_id)
    tx = TEXTS[lang]

    if step == "input_card":
        card_num = message.text.replace(" ", "")
        if not card_num.isdigit():
            if lang == 'en':
                bot.send_message(message.chat.id, f"{E_CROSS} <b>Wrong format!</b>\nCard number must contain digits only.", parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, f"{E_CROSS} <b>Неверный формат!</b>\nНомер карты должен содержать только цифры.", parse_mode="HTML")
            return

        conn = sqlite3.connect('king_deals.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET req_type = ?, req_value = ? WHERE user_id = ?",
            ("Card" if lang == 'en' else f"Карта ({state['country']})", card_num, user_id))
        conn.commit()
        conn.close()

        del user_states[user_id]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(tx['btn_create_deal'], callback_data="force_create"))
        if lang == 'en':
            bot.send_message(message.chat.id, f"{E_CHECK} <b>Requisites successfully saved!</b>", parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"{E_CHECK} <b>Реквизиты успешно добавлены и сохранены!</b>", parse_mode="HTML", reply_markup=markup)

    elif step == "input_ton":
        ton_addr = message.text.strip()
        if len(ton_addr) != 48 or not (ton_addr.startswith("UQ") or ton_addr.startswith("EQ")):
            if lang == 'en':
                bot.send_message(message.chat.id, f"{E_CROSS} <b>Wrong TON address format!</b>\nAddress must be 48 characters and start with UQ or EQ.", parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, f"{E_CROSS} <b>Неверный формат TON-адреса!</b>\nАдрес должен содержать 48 символов и начинаться на UQ или EQ.", parse_mode="HTML")
            return

        conn = sqlite3.connect('king_deals.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET req_type = ?, req_value = ? WHERE user_id = ?",
            ("💎 TON wallet" if lang == 'en' else "💎 TON кошелек", ton_addr, user_id))
        conn.commit()
        conn.close()

        del user_states[user_id]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(tx['btn_create_deal'], callback_data="force_create"))
        if lang == 'en':
            bot.send_message(message.chat.id, f"{E_CHECK} <b>Requisites successfully saved!</b>", parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"{E_CHECK} <b>Реквизиты успешно добавлены и сохранены!</b>", parse_mode="HTML", reply_markup=markup)

    elif step == "deal_title":
        user_states[user_id]["title"] = message.text
        user_states[user_id]["step"] = "deal_amount"
        if lang == 'en':
            bot.send_message(message.chat.id, f"{E_MONEY} <b>Enter the deal amount:</b>\n<i>(Numbers only, e.g.: 500)</i>", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, f"{E_MONEY} <b>Укажите сумму сделки:</b>\n<i>(Введите только число, например: 500)</i>", parse_mode="HTML")

    elif step == "deal_amount":
        try:
            amount = float(message.text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            if lang == 'en':
                bot.send_message(message.chat.id, f"{E_CROSS} <b>Error!</b> The amount must be a positive number. Try again:", parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, f"{E_CROSS} <b>Ошибка!</b> Сумма должна быть положительным числом. Попробуйте ещё раз:", parse_mode="HTML")
            return

        user_states[user_id]["amount"] = amount
        user_states[user_id]["step"] = "deal_currency"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇦 UAH", callback_data="cur_UAH"),
            types.InlineKeyboardButton("🇷🇺 RUB", callback_data="cur_RUB"),
            types.InlineKeyboardButton("🇰🇿 KZT", callback_data="cur_KZT"),
            types.InlineKeyboardButton("🇧🇾 BYN", callback_data="cur_BYN"),
            types.InlineKeyboardButton("🇺🇿 UZS", callback_data="cur_UZS"),
            types.InlineKeyboardButton("💎 TON", callback_data="cur_TON")
        )
        if lang == 'en':
            bot.send_message(message.chat.id, f"{E_PLANE} <b>Choose the deal currency:</b>", parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"{E_PLANE} <b>Выберите валюту сделки:</b>", parse_mode="HTML", reply_markup=markup)

# === ОБРАБОТКА CALLBACK КНОПОК ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    mid = call.message.message_id
    cid = call.message.chat.id
    uid = call.from_user.id
    lang = get_lang(uid)
    tx = TEXTS[lang]

    if call.data == "lang_toggle":
        bot.answer_callback_query(call.id)
        new_lang = 'en' if lang == 'ru' else 'ru'
        set_lang(uid, new_lang)
        bot.edit_message_text(
            build_welcome_text(new_lang), cid, mid,
            parse_mode="HTML", reply_markup=get_welcome_inline(new_lang)
        )

    elif call.data == "menu_main":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(build_welcome_text(lang), cid, mid, parse_mode="HTML", reply_markup=get_welcome_inline(lang))

    elif call.data == "menu_create":
        bot.answer_callback_query(call.id)
        create_deal_start(call.message, user_id=uid, chat_id=cid, edit_message_id=mid)

    elif call.data == "menu_deals":
        bot.answer_callback_query(call.id)
        my_deals(call.message, user_id=uid, chat_id=cid, edit_message_id=mid)

    elif call.data == "menu_balance":
        bot.answer_callback_query(call.id)
        balance_menu(call.message, user_id=uid, chat_id=cid, edit_message_id=mid)

    elif call.data == "menu_reqs":
        bot.answer_callback_query(call.id)
        my_requisites(call.message, user_id=uid, chat_id=cid, edit_message_id=mid)

    elif call.data == "menu_ref":
        bot.answer_callback_query(call.id)
        referrals_menu(call.message, user_id=uid, chat_id=cid, edit_message_id=mid)

    elif call.data == "bind_start":
        markup = types.InlineKeyboardMarkup()
        if lang == 'en':
            markup.add(types.InlineKeyboardButton("💳 Bank Card", callback_data="bind_card_sng"))
            markup.add(types.InlineKeyboardButton("💎 TON Address", callback_data="bind_ton"))
            txt = "Please choose a method to link your requisites:"
        else:
            markup.add(types.InlineKeyboardButton("💳 Банковская карта", callback_data="bind_card_sng"))
            markup.add(types.InlineKeyboardButton("💎 TON Адрес", callback_data="bind_ton"))
            txt = "Пожалуйста, выберите способ для привязки реквизитов:"
        markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))
        bot.edit_message_text(txt, cid, mid, reply_markup=markup)

    elif call.data == "bind_card_sng":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇦 Ukraine"    if lang == 'en' else "🇺🇦 Украина",    callback_data="cc_Ukraine"    if lang == 'en' else "cc_Украина"),
            types.InlineKeyboardButton("🇷🇺 Russia"     if lang == 'en' else "🇷🇺 Россия",     callback_data="cc_Russia"     if lang == 'en' else "cc_Россия"),
            types.InlineKeyboardButton("🇰🇿 Kazakhstan" if lang == 'en' else "🇰🇿 Казахстан",  callback_data="cc_Kazakhstan" if lang == 'en' else "cc_Казахстан"),
            types.InlineKeyboardButton("🇧🇾 Belarus"    if lang == 'en' else "🇧🇾 Беларусь",   callback_data="cc_Belarus"    if lang == 'en' else "cc_Беларусь"),
            types.InlineKeyboardButton("🇺🇿 Uzbekistan" if lang == 'en' else "🇺🇿 Узбекистан", callback_data="cc_Uzbekistan" if lang == 'en' else "cc_Узбекистан"),
        )
        bot.edit_message_text(tx['bind_country'], cid, mid, reply_markup=markup, parse_mode="HTML")

    elif call.data.startswith("cc_"):
        country = call.data.split("_")[1]
        user_states[user_id] = {"step": "input_card", "country": country}
        bot.delete_message(cid, mid)
        bot.send_message(cid, tx['bind_card_send'].format(country=country), parse_mode="HTML")

    elif call.data == "bind_ton":
        user_states[user_id] = {"step": "input_ton"}
        bot.delete_message(cid, mid)
        bot.send_message(cid, tx['bind_ton_send'], parse_mode="HTML")

    elif call.data == "force_create":
        bot.delete_message(cid, mid)
        if lang == 'en':
            bot.send_message(cid, f"{E_BOX} <b>Enter the name of the item or service for the deal:</b>", parse_mode="HTML")
        else:
            bot.send_message(cid, f"{E_BOX} <b>Введите название товара или услуги для сделки:</b>", parse_mode="HTML")
        user_states[user_id] = {"step": "deal_title"}

    elif call.data.startswith("cur_"):
        currency = call.data.split("_")[1]
        if user_id in user_states and user_states[user_id].get("step") == "deal_currency":
            title  = user_states[user_id]["title"]
            amount = user_states[user_id]["amount"]
            del user_states[user_id]

            deal_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            conn = sqlite3.connect('king_deals.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO deals (deal_id, seller_id, title, amount, currency) VALUES (?, ?, ?, ?, ?)",
                (deal_id, user_id, title, amount, currency)
            )
            conn.commit()
            conn.close()

            bot.delete_message(cid, mid)
            bot_username = bot.get_me().username
            deal_url = f"https://t.me/{bot_username}?start=deal_{deal_id}"

            if lang == 'en':
                seller_text = (
                    f"{E_BOX} <b>Deal successfully created!</b>\n\n"
                    f"📝 Item: {title}\n"
                    f"💵 Amount: {amount} {currency}\n\n"
                    f"{E_LINK} Buyer link:\n<code>{deal_url}</code>\n\n"
                    f"{E_CROSS} Send this link to the buyer. They can pay the deal after opening it."
                )
            else:
                seller_text = (
                    f"{E_BOX} <b>Сделка успешно создана!</b>\n\n"
                    f"📝 Товар: {title}\n"
                    f"💵 Сумма: {amount} {currency}\n\n"
                    f"{E_LINK} Ссылка для покупателя:\n<code>{deal_url}</code>\n\n"
                    f"{E_CROSS} Перешлите эту ссылку покупателю. Когда он перейдёт по ней — сможет оплатить сделку."
                )
            bot.send_message(cid, seller_text, parse_mode="HTML")

    elif call.data.startswith("pay_"):
        deal_id = call.data.split("_")[1]
        conn = sqlite3.connect('king_deals.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT seller_id, title, amount, currency, status FROM deals WHERE deal_id = ?",
            (deal_id,)
        )
        deal = cursor.fetchone()

        if not deal or deal[4] != 'created':
            bot.answer_callback_query(call.id, "Сделка недействительна или уже оплачена.", show_alert=True)
            conn.close()
            return

        seller_id, title, amount, currency, status = deal
        bal_col = f"bal_{currency.lower()}"

        cursor.execute(f"SELECT {bal_col} FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        buyer_bal = row[0] if row else 0.0

        if buyer_bal < amount:
            bot.answer_callback_query(
                call.id,
                f"❌ Недостаточно средств! Стоимость: {amount} {currency}, ваш баланс: {buyer_bal} {currency}.",
                show_alert=True
            )
            conn.close()
            return

        cursor.execute(f"UPDATE users SET {bal_col} = {bal_col} - ? WHERE user_id = ?", (amount, user_id))
        cursor.execute("UPDATE deals SET buyer_id = ?, status = 'paid' WHERE deal_id = ?", (user_id, deal_id))
        conn.commit()
        conn.close()

        bot.delete_message(cid, mid)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "🎉 Товар получил, отпустить средства",
            callback_data=f"release_{deal_id}"
        ))
        buyer_text = (
            f"{E_CHECK} <b>Вы успешно оплатили сделку!</b>\n\n"
            f"🔒 Средства заморожены гарантом King Deals. Они переведутся продавцу только после того, как вы получите товар.\n"
            f"{E_BOX} Для передачи товара свяжитесь с менеджером: @{SUPPORT_USER}\n\n"
            f"👇 Нажмите кнопку ниже ТОЛЬКО после того, как полностью проверите и получите товар:"
        )
        bot.send_message(user_id, buyer_text, parse_mode="HTML", reply_markup=markup)

        seller_text = (
            f"{E_TIME} <b>Ваша сделка оплачена!</b>\n\n"
            f"Покупатель внёс оплату за «{title}».\n"
            f"🔒 Средства заморожены. Передайте товар покупателю через менеджера @{SUPPORT_USER}."
        )
        bot.send_message(seller_id, seller_text, parse_mode="HTML")

    elif call.data.startswith("cancel_"):
        bot.edit_message_text(
            f"{E_CROSS} Вы отказались от сделки.",
            cid, mid
        )

    elif call.data.startswith("release_"):
        deal_id = call.data.split("_")[1]
        conn = sqlite3.connect('king_deals.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT seller_id, buyer_id, title, amount, currency, status FROM deals WHERE deal_id = ?",
            (deal_id,)
        )
        deal = cursor.fetchone()

        if not deal or deal[5] != 'paid':
            bot.answer_callback_query(call.id, "Ошибка закрытия сделки.", show_alert=True)
            conn.close()
            return

        seller_id, buyer_id, title, amount, currency, status = deal
        bal_col = f"bal_{currency.lower()}"

        cursor.execute(f"UPDATE users SET {bal_col} = {bal_col} + ? WHERE user_id = ?", (amount, seller_id))
        cursor.execute("UPDATE deals SET status = 'completed' WHERE deal_id = ?", (deal_id,))

        cursor.execute("SELECT referrer_id FROM users WHERE user_id = ?", (seller_id,))
        ref = cursor.fetchone()
        if ref and ref[0]:
            ref_bonus = amount * 0.025
            cursor.execute(
                f"UPDATE users SET {bal_col} = {bal_col} + ? WHERE user_id = ?",
                (ref_bonus, ref[0])
            )
            try:
                bot.send_message(
                    ref[0],
                    f"{E_COIN} Реферальный бонус! Вам зачислено {ref_bonus:.2f} {currency} за сделку вашего реферала.",
                    parse_mode="HTML"
                )
            except Exception:
                pass

        conn.commit()
        conn.close()

        bot.delete_message(cid, mid)
        bot.send_message(
            buyer_id,
            f"{E_CHECK} <b>Сделка успешно завершена!</b>\nДеньги разморожены и отправлены продавцу. Спасибо, что используете King Deals! {E_HAND}",
            parse_mode="HTML"
        )
        bot.send_message(
            seller_id,
            f"{E_MONEY} <b>Сделка успешно завершена!</b>\nПокупатель подтвердил получение товара.\n\n💰 На ваш баланс зачислено {amount} {currency}.",
            parse_mode="HTML"
        )

# === КАРТОЧКА СДЕЛКИ ДЛЯ ПОКУПАТЕЛЯ ===
def show_deal_card(message, deal_id):
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT seller_id, title, amount, currency, status FROM deals WHERE deal_id = ?",
        (deal_id,)
    )
    deal = cursor.fetchone()
    conn.close()

    if not deal:
        bot.send_message(message.chat.id, f"{E_CROSS} Сделка не найдена.")
        return

    seller_id, title, amount, currency, status = deal

    if status != 'created':
        bot.send_message(message.chat.id, f"{E_CROSS} Данная сделка уже недействительна.")
        return

    if seller_id == message.from_user.id:
        bot.send_message(message.chat.id, f"{E_CROSS} Вы не можете открыть сделку с самим собой.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💳 Оплатить с баланса", callback_data=f"pay_{deal_id}"),
        types.InlineKeyboardButton("❌ Отказаться",          callback_data=f"cancel_{deal_id}")
    )
    card_text = (
        f"{E_HAND} <b>Вам предложена сделка</b>\n\n"
        f"{E_BOX} Товар/Услуга: {title}\n"
        f"{E_MONEY} Стоимость: {amount} {currency}"
    )
    bot.send_message(message.chat.id, card_text, parse_mode="HTML", reply_markup=markup)

# === БАЛАНС ===
def balance_menu(message, user_id=None, chat_id=None, edit_message_id=None):
    user_id = user_id or message.from_user.id
    chat_id = chat_id or message.chat.id
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT bal_uah, bal_rub, bal_kzt, bal_byn, bal_uzs, bal_ton FROM users WHERE user_id = ?",
        (user_id,)
    )
    bal = cursor.fetchone()
    conn.close()

    if not bal:
        bal = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    if lang == 'en':
        text = (
            f"{E_CARD} <b>Personal Account</b>\n\n"
            f"{E_USER} Your Telegram ID: <code>{user_id}</code>\n\n"
            f"{E_MONEY} <b>Your current King Deals balance:</b>\n"
            f"🇺🇦 UAH: {bal[0]} UAH\n"
            f"🇷🇺 RUB: {bal[1]} RUB\n"
            f"🇰🇿 KZT: {bal[2]} KZT\n"
            f"🇧🇾 BYN: {bal[3]} BYN\n"
            f"🇺🇿 UZS: {bal[4]} UZS\n"
            f"💎 TON: {bal[5]} TON\n\n"
            f"👇 Choose an action:"
        )
    else:
        text = (
            f"{E_CARD} <b>Личный кабинет</b>\n\n"
            f"{E_USER} Ваш Telegram ID: <code>{user_id}</code>\n\n"
            f"{E_MONEY} <b>Ваш текущий баланс King Deals:</b>\n"
            f"🇺🇦 UAH: {bal[0]} грн\n"
            f"🇷🇺 RUB: {bal[1]} руб\n"
            f"🇰🇿 KZT: {bal[2]} ₸\n"
            f"🇧🇾 BYN: {bal[3]} BYN\n"
            f"🇺🇿 UZS: {bal[4]} сум\n"
            f"💎 TON: {bal[5]} TON\n\n"
            f"👇 Выберите действие с балансом:"
        )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(tx['btn_top_up'],   url=f"https://t.me/{SUPPORT_USER}"),
        types.InlineKeyboardButton(tx['btn_withdraw'], url=f"https://t.me/{SUPPORT_USER}")
    )
    markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))

    if edit_message_id:
        bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# === РЕФЕРАЛЫ ===
def referrals_menu(message, user_id=None, chat_id=None, edit_message_id=None):
    user_id = user_id or message.from_user.id
    chat_id = chat_id or message.chat.id
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    bot_username = bot.get_me().username
    ref_url = f"https://t.me/{bot_username}?start=ref_{user_id}"

    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(user_id) FROM users WHERE referrer_id = ?", (user_id,))
    ref_count = cursor.fetchone()[0]
    conn.close()

    if lang == 'en':
        text = (
            f"{E_USER} <b>King Deals Referral Program</b>\n\n"
            f"Invite friends and earn <b>50% of the commission</b> from each of their successful deals!\n\n"
            f"{E_DEV} Your referrals: <b>{ref_count}</b>\n\n"
            f"{E_LINK} Your referral link:\n<code>{ref_url}</code>"
        )
    else:
        text = (
            f"{E_USER} <b>Реферальная программа King Deals</b>\n\n"
            f"Приглашайте друзей и получайте <b>50% от комиссии</b> с каждой их успешной сделки!\n\n"
            f"{E_DEV} Ваших рефералов: <b>{ref_count}</b>\n\n"
            f"{E_LINK} Ваша реферальная ссылка:\n<code>{ref_url}</code>"
        )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))

    if edit_message_id:
        bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# === МОИ СДЕЛКИ ===
def my_deals(message, user_id=None, chat_id=None, edit_message_id=None):
    user_id = user_id or message.from_user.id
    chat_id = chat_id or message.chat.id
    lang = get_lang(user_id)
    tx = TEXTS[lang]
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT deal_id, title, amount, currency, status FROM deals WHERE seller_id = ? OR buyer_id = ? ORDER BY rowid DESC LIMIT 10",
        (user_id, user_id)
    )
    deals = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(tx['btn_back'], callback_data="menu_main"))

    if not deals:
        text = tx['deals_empty']
        if edit_message_id:
            bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=markup)
        else:
            bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return

    text = tx['deals_title']
    for d in deals:
        deal_id, title, amount, currency, status = d
        safe_title    = html_module.escape(str(title))
        safe_currency = html_module.escape(str(currency))
        status_text   = tx['deal_status'].get(status, status)
        text += f"• <b>{safe_title}</b> — {amount} {safe_currency}\n  ID: <code>{deal_id}</code> | {status_text}\n\n"

    if edit_message_id:
        bot.edit_message_text(text, chat_id, edit_message_id, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

# === /add user_id amount currency ===
@bot.message_handler(commands=['add'])
def admin_add_balance(message):
    parts = message.text.split()
    if len(parts) != 4:
        bot.send_message(message.chat.id, "Формат: /add user_id сума валюта")
        return

    try:
        target_id = int(parts[1])
        amount    = float(parts[2])
        currency  = parts[3].lower()
    except ValueError:
        bot.send_message(message.chat.id, "Невірний формат. Приклад: /add 123456789 500 uah")
        return

    currency_map = {
        'uah': 'uah', 'грн': 'uah', 'гривна': 'uah', 'гривня': 'uah',
        'rub': 'rub', 'руб': 'rub', 'рубль': 'rub', 'рублей': 'rub',
        'kzt': 'kzt', 'тенге': 'kzt', 'тг': 'kzt',
        'byn': 'byn', 'бел': 'byn', 'белруб': 'byn',
        'uzs': 'uzs', 'сум': 'uzs', 'сумов': 'uzs',
        'ton': 'ton', 'тон': 'ton',
    }

    currency = currency_map.get(currency)
    if not currency:
        bot.send_message(
            message.chat.id,
            "Валюта не распознана. Примеры:\nUAH: uah, грн\nRUB: rub, руб\nKZT: kzt, тенге\nBYN: byn\nUZS: uzs, сум\nTON: ton"
        )
        return

    bal_col = f"bal_{currency}"
    conn = sqlite3.connect('king_deals.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (target_id,))
    cursor.execute(
        f"UPDATE users SET {bal_col} = {bal_col} + ? WHERE user_id = ?",
        (amount, target_id)
    )
    cursor.execute(f"SELECT {bal_col} FROM users WHERE user_id = ?", (target_id,))
    new_bal = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    bot.send_message(
        message.chat.id,
        f"{E_CHECK} Начислено <b>{amount} {currency.upper()}</b> пользователю <code>{target_id}</code>\n"
        f"Новый баланс {currency.upper()}: <b>{new_bal}</b>",
        parse_mode="HTML"
    )

# === ЗАПУСК ===
if __name__ == "__main__":
    print("King Deals бот запущено...")
    bot.infinity_polling(timeout=30, long_polling_timeout=20)
