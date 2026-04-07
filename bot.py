import os
import re
import math
from datetime import datetime

import telebot
from telebot import types
import requests
from dotenv import load_dotenv

import database
import keyboard as kb

# Загрузка конфигурации
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("CURRENCY_API_KEY")

# API URL
API_BASE_URL = "http://api.exchangerate.host"

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Состояния пользователей
user_states = {}  # user_id: {"state": "waiting_for_...", "data": {...}}

# Словарь стран и валют
COUNTRIES_CURRENCIES = {
    "россия": {"name": "Россия", "currency": "RUB", "code": "RUB", "symbol": "₽"},
    "russia": {"name": "Russia", "currency": "RUB", "code": "RUB", "symbol": "₽"},
    "италия": {"name": "Италия", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "italy": {"name": "Italy", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "сша": {"name": "США", "currency": "USD", "code": "USD", "symbol": "$"},
    "usa": {"name": "USA", "currency": "USD", "code": "USD", "symbol": "$"},
    "европа": {"name": "Еврозона", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "евро": {"name": "Еврозона", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "китай": {"name": "Китай", "currency": "CNY", "code": "CNY", "symbol": "¥"},
    "china": {"name": "China", "currency": "CNY", "code": "CNY", "symbol": "¥"},
    "япония": {"name": "Япония", "currency": "JPY", "code": "JPY", "symbol": "¥"},
    "japan": {"name": "Japan", "currency": "JPY", "code": "JPY", "symbol": "¥"},
    "англия": {"name": "Англия", "currency": "GBP", "code": "GBP", "symbol": "£"},
    "britain": {"name": "Britain", "currency": "GBP", "code": "GBP", "symbol": "£"},
    "великобритания": {"name": "Великобритания", "currency": "GBP", "code": "GBP", "symbol": "£"},
    "турция": {"name": "Турция", "currency": "TRY", "code": "TRY", "symbol": "₺"},
    "turkey": {"name": "Turkey", "currency": "TRY", "code": "TRY", "symbol": "₺"},
    "тайланд": {"name": "Таиланд", "currency": "THB", "code": "THB", "symbol": "฿"},
    "thailand": {"name": "Thailand", "currency": "THB", "code": "THB", "symbol": "฿"},
    "вьетнам": {"name": "Вьетнам", "currency": "VND", "code": "VND", "symbol": "₫"},
    "vietnam": {"name": "Vietnam", "currency": "VND", "code": "VND", "symbol": "₫"},
    "египет": {"name": "Египет", "currency": "EGP", "code": "EGP", "symbol": "E£"},
    "egypt": {"name": "Egypt", "currency": "EGP", "code": "EGP", "symbol": "E£"},
    "оаэ": {"name": "ОАЭ", "currency": "AED", "code": "AED", "symbol": "د.إ"},
    "uae": {"name": "UAE", "currency": "AED", "code": "AED", "symbol": "د.إ"},
    "швейцария": {"name": "Швейцария", "currency": "CHF", "code": "CHF", "symbol": "CHF"},
    "switzerland": {"name": "Switzerland", "currency": "CHF", "code": "CHF", "symbol": "CHF"},
    "франция": {"name": "Франция", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "france": {"name": "France", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "германия": {"name": "Германия", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "germany": {"name": "Germany", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "испания": {"name": "Испания", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "spain": {"name": "Spain", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "португалия": {"name": "Португалия", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "portugal": {"name": "Portugal", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "греция": {"name": "Греция", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "greece": {"name": "Greece", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "чехия": {"name": "Чехия", "currency": "CZK", "code": "CZK", "symbol": "Kč"},
    "czech": {"name": "Czech Republic", "currency": "CZK", "code": "CZK", "symbol": "Kč"},
    "польша": {"name": "Польша", "currency": "PLN", "code": "PLN", "symbol": "zł"},
    "poland": {"name": "Poland", "currency": "PLN", "code": "PLN", "symbol": "zł"},
    "венгрия": {"name": "Венгрия", "currency": "HUF", "code": "HUF", "symbol": "Ft"},
    "hungary": {"name": "Hungary", "currency": "HUF", "code": "HUF", "symbol": "Ft"},
    "швеция": {"name": "Швеция", "currency": "SEK", "code": "SEK", "symbol": "kr"},
    "sweden": {"name": "Sweden", "currency": "SEK", "code": "SEK", "symbol": "kr"},
    "норвегия": {"name": "Норвегия", "currency": "NOK", "code": "NOK", "symbol": "kr"},
    "norway": {"name": "Norway", "currency": "NOK", "code": "NOK", "symbol": "kr"},
    "датская": {"name": "Дания", "currency": "DKK", "code": "DKK", "symbol": "kr"},
    "denmark": {"name": "Denmark", "currency": "DKK", "code": "DKK", "symbol": "kr"},
    "финляндия": {"name": "Финляндия", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "finland": {"name": "Finland", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "голландия": {"name": "Нидерланды", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "netherlands": {"name": "Netherlands", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "бельгия": {"name": "Бельгия", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "belgium": {"name": "Belgium", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "австрия": {"name": "Австрия", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "austria": {"name": "Austria", "currency": "EUR", "code": "EUR", "symbol": "€"},
    "корея": {"name": "Корея", "currency": "KRW", "code": "KRW", "symbol": "₩"},
    "korea": {"name": "Korea", "currency": "KRW", "code": "KRW", "symbol": "₩"},
    "южная корея": {"name": "Южная Корея", "currency": "KRW", "code": "KRW", "symbol": "₩"},
    "south korea": {"name": "South Korea", "currency": "KRW", "code": "KRW", "symbol": "₩"},
    "сингапур": {"name": "Сингапур", "currency": "SGD", "code": "SGD", "symbol": "S$"},
    "singapore": {"name": "Singapore", "currency": "SGD", "code": "SGD", "symbol": "S$"},
    "малайзия": {"name": "Малайзия", "currency": "MYR", "code": "MYR", "symbol": "RM"},
    "malaysia": {"name": "Malaysia", "currency": "MYR", "code": "MYR", "symbol": "RM"},
    "индонезия": {"name": "Индонезия", "currency": "IDR", "code": "IDR", "symbol": "Rp"},
    "indonesia": {"name": "Indonesia", "currency": "IDR", "code": "IDR", "symbol": "Rp"},
    "филиппины": {"name": "Филиппины", "currency": "PHP", "code": "PHP", "symbol": "₱"},
    "philippines": {"name": "Philippines", "currency": "PHP", "code": "PHP", "symbol": "₱"},
    "австралия": {"name": "Австралия", "currency": "AUD", "code": "AUD", "symbol": "A$"},
    "australia": {"name": "Australia", "currency": "AUD", "code": "AUD", "symbol": "A$"},
    "канада": {"name": "Канада", "currency": "CAD", "code": "CAD", "symbol": "C$"},
    "canada": {"name": "Canada", "currency": "CAD", "code": "CAD", "symbol": "C$"},
    "мексика": {"name": "Мексика", "currency": "MXN", "code": "MXN", "symbol": "$"},
    "mexico": {"name": "Mexico", "currency": "MXN", "code": "MXN", "symbol": "$"},
    "бразилия": {"name": "Бразилия", "currency": "BRL", "code": "BRL", "symbol": "R$"},
    "brazil": {"name": "Brazil", "currency": "BRL", "code": "BRL", "symbol": "R$"},
    "аргентина": {"name": "Аргентина", "currency": "ARS", "code": "ARS", "symbol": "$"},
    "argentina": {"name": "Argentina", "currency": "ARS", "code": "ARS", "symbol": "$"},
    "чешская": {"name": "Чехия", "currency": "CZK", "code": "CZK", "symbol": "Kč"},
}


def get_country_currency(country_input: str) -> dict:
    """Получить информацию о валюте по названию страны"""
    country_lower = country_input.lower().strip()
    
    if country_lower in COUNTRIES_CURRENCIES:
        return COUNTRIES_CURRENCIES[country_lower]
    
    # Поиск по частичному совпадению
    for key, value in COUNTRIES_CURRENCIES.items():
        if country_lower in key or key in country_lower:
            return value
    
    return None


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Получить курс обмена через API"""
    try:
        url = f"{API_BASE_URL}/convert"
        params = {
            "access_key": API_KEY,
            "from": from_currency,
            "to": to_currency,
            "amount": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("success") or data.get("result"):
            return data.get("result", data.get("rates", {}).get(to_currency, 1))
        
        # Пробуем альтернативный формат
        if "rates" in data and to_currency in data["rates"]:
            return data["rates"][to_currency]
            
        return None
        
    except Exception as e:
        print(f"API Error: {e}")
        return None


def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    """Конвертировать сумму через API"""
    try:
        url = f"{API_BASE_URL}/convert"
        params = {
            "access_key": API_KEY,
            "from": from_currency,
            "to": to_currency,
            "amount": amount
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("success") or data.get("result"):
            return data.get("result", 0)
        
        return None
        
    except Exception as e:
        print(f"API Error: {e}")
        return None


def format_amount(amount: float) -> str:
    """Форматировать сумму с разделителями (2 знака после запятой)"""
    return f"{amount:,.2f}".replace(",", " ")


def format_rate(amount: float) -> str:
    """Форматировать курс (4 знака после запятой)"""
    return f"{amount:,.4f}".replace(",", " ")


def send_welcome(message):
    """Отправить приветственное сообщение"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Создаём пользователя в БД
    database.get_or_create_user(user_id, username, first_name)
    
    welcome_text = (
        f"👋 Привет, {first_name}!\n\n"
        "Добро пожаловать в **Travel Wallet** — твой мини-кошелёк для путешествий!\n\n"
        "Я помогу тебе:\n"
        "• 🌍 Создать путешествие и отслеживать расходы\n"
        "• 💱 Конвертировать валюты по актуальному курсу\n"
        "• 📊 Видеть остаток в обеих валютах\n"
        "• 📜 Вести историю расходов\n\n"
        "Выбери действие из меню ниже или нажми /start"
    )
    
    bot.send_message(
        user_id,
        welcome_text,
        reply_markup=kb.main_menu_keyboard(),
        parse_mode="Markdown"
    )


def handle_new_trip(user_id: int):
    """Начать процесс создания нового путешествия"""
    user_states[user_id] = {"state": "waiting_trip_name", "data": {}}
    
    bot.send_message(
        user_id,
        "🆕 *Создание нового путешествия*\n\n"
        "Введите название путешествия (например: *Китай 2026*, *Италия*, *Отпуск в Турции*):",
        parse_mode="Markdown"
    )


def handle_trip_name(user_id: int, name: str):
    """Обработка названия путешествия"""
    name = name.strip()
    if len(name) < 2:
        bot.send_message(
            user_id,
            "❌ Название слишком короткое. Введите название путешествия:"
        )
        return
    
    user_states[user_id]["data"]["trip_name"] = name
    user_states[user_id]["state"] = "waiting_from_country"
    
    bot.send_message(
        user_id,
        f"✅ Название: *{name}*\n\n"
        "Теперь введите страну, из которой вы выезжаете (ваша домашняя страна):\n\n"
        "_Например: Россия, USA, Германия_",
        parse_mode="Markdown"
    )


def handle_from_country(user_id: int, country: str):
    """Обработка ввода страны отправления"""
    country_info = get_country_currency(country)
    
    if not country_info:
        bot.send_message(
            user_id,
            "❌ Извините, я не знаю такую страну. Попробуйте ещё раз:\n"
            "_Например: Россия, USA, Германия, Китай_",
            parse_mode="Markdown"
        )
        return
    
    user_states[user_id]["data"]["from_country"] = country_info["name"]
    user_states[user_id]["data"]["from_currency"] = country_info["code"]
    user_states[user_id]["state"] = "waiting_to_country"
    
    bot.send_message(
        user_id,
        f"✅ Страна отправления: *{country_info['name']}*\n"
        f"💰 Валюта: *{country_info['code']}*\n\n"
        "Теперь введите страну назначения (куда вы едете):",
        parse_mode="Markdown"
    )


def handle_to_country(user_id: int, country: str):
    """Обработка ввода страны назначения"""
    country_info = get_country_currency(country)
    
    if not country_info:
        bot.send_message(
            user_id,
            "❌ Извините, я не знаю такую страну. Попробуйте ещё раз:\n"
            "_Например: Италия, Китай, Турция, США_",
            parse_mode="Markdown"
        )
        return
    
    data = user_states[user_id]["data"]
    
    if country_info["code"] == data["from_currency"]:
        bot.send_message(
            user_id,
            "⚠️ Страны совпадают по валюте. Выберите другую страну назначения:",
            parse_mode="Markdown"
        )
        return
    
    data["to_country"] = country_info["name"]
    data["to_currency"] = country_info["code"]
    
    # Получаем курс обмена
    from_curr = data["from_currency"]
    to_curr = data["to_currency"]
    
    bot.send_message(user_id, "⏳ Получаю актуальный курс обмена...")
    
    rate = get_exchange_rate(from_curr, to_curr)
    
    if rate is None:
        bot.send_message(
            user_id,
            "❌ Не удалось получить курс обмена от API. Попробуйте позже или введите курс вручную.",
            reply_markup=kb.main_menu_keyboard()
        )
        user_states.pop(user_id, None)
        return
    
    data["exchange_rate"] = rate
    user_states[user_id]["state"] = "confirm_rate"
    
    rate_text = (
        f"✅ Страна назначения: *{country_info['name']}*\n"
        f"💰 Валюта: *{to_curr}*\n\n"
        f"📊 *Актуальный курс обмена:*\n"
        f"1 {from_curr} = {format_rate(rate)} {to_curr}\n\n"
        "Этот курс вас устраивает?"
    )
    
    # Создаём клавиатуру подтверждения
    confirm_keyboard = types.InlineKeyboardMarkup(row_width=2)
    confirm_keyboard.add(
        types.InlineKeyboardButton("✅ Да, всё верно", callback_data="rate_accept"),
        types.InlineKeyboardButton("❌ Нет, введу свой", callback_data="rate_custom")
    )
    
    bot.send_message(user_id, rate_text, reply_markup=confirm_keyboard, parse_mode="Markdown")


def handle_custom_rate(user_id: int, rate_str: str):
    """Обработка ввода пользовательского курса"""
    try:
        rate = float(rate_str.replace(",", "."))
        if rate <= 0:
            raise ValueError()
        
        user_states[user_id]["data"]["exchange_rate"] = rate
        user_states[user_id]["data"]["is_custom_rate"] = True
        
        data = user_states[user_id]["data"]
        
        # Переходим к вводу суммы
        user_states[user_id]["state"] = "waiting_initial_amount"
        
        bot.send_message(
            user_id,
            f"✅ Вы установили курс:\n"
            f"1 {data['from_currency']} = {format_rate(rate)} {data['to_currency']}\n\n"
            f"💰 Теперь введите начальную сумму для поездки в *{data['from_currency']}*:\n"
            "_Например: 50000 или 100 000_",
            parse_mode="Markdown"
        )

    except ValueError:
        bot.send_message(
            user_id,
            "❌ Пожалуйста, введите корректное число (положительное):"
        )


def handle_initial_amount(user_id: int, amount_str: str):
    """Обработка ввода начальной суммы и создание путешествия"""
    try:
        # Убираем пробелы и обрабатываем число
        amount_str = amount_str.replace(" ", "").replace(",", ".")
        amount = float(amount_str)
        
        if amount <= 0:
            raise ValueError()
        
        data = user_states[user_id]["data"]
        from_curr = data["from_currency"]
        to_curr = data["to_currency"]
        rate = data["exchange_rate"]
        
        # Конвертируем сумму
        converted_amount = amount * rate
        
        # Создаём путешествие
        trip_name = data.get("trip_name", f"{data['from_country']} → {data['to_country']}")
        
        trip_id = database.create_trip(
            user_id=user_id,
            name=trip_name,
            from_country=data["from_country"],
            to_country=data["to_country"],
            from_currency=from_curr,
            to_currency=to_curr,
            exchange_rate=rate,
            from_balance=amount,
            to_balance=converted_amount,
            is_custom_rate=data.get("is_custom_rate", False)
        )
        
        # Очищаем состояние
        user_states.pop(user_id, None)
        
        success_text = (
            f"🎉 *Путешествие создано!*\n\n"
            f"📍 *{trip_name}*\n\n"
            f"💰 *Баланс:*\n"
            f"• В валюте дома: {format_amount(amount)} {from_curr}\n"
            f"• В валюте поездки: {format_amount(converted_amount)} {to_curr}\n\n"
            f"📊 Курс: 1 {from_curr} = {format_rate(rate)} {to_curr}\n"
            f"{'(установлен вручную)' if data.get('is_custom_rate') else '(актуальный)'}\n\n"
            "Теперь вы можете отправлять мне суммы расходов, и я буду их учитывать!"
        )
        
        bot.send_message(
            user_id,
            success_text,
            reply_markup=kb.main_menu_keyboard(),
            parse_mode="Markdown"
        )
        
    except ValueError:
        bot.send_message(
            user_id,
            "❌ Пожалуйста, введите корректное число (положительное):"
        )


def handle_expense_input(user_id: int, amount_str: str):
    """Обработка ввода суммы расхода"""
    try:
        amount_str = amount_str.replace(" ", "").replace(",", ".")
        amount = float(amount_str)
        
        if amount <= 0:
            raise ValueError()
        
        # Получаем текущее путешествие
        trip_id = database.get_current_trip_id(user_id)
        
        if not trip_id:
            bot.send_message(
                user_id,
                "❌ У вас нет активного путешествия. Создайте новое путешествие.",
                reply_markup=kb.main_menu_keyboard()
            )
            return
        
        trip = database.get_trip(trip_id)
        
        if not trip:
            bot.send_message(
                user_id,
                "❌ Путешествие не найдено. Создайте новое путешествие.",
                reply_markup=kb.main_menu_keyboard()
            )
            return
        
        _, name, from_country, to_country, from_curr, to_curr, rate, from_balance, to_balance, _, _ = trip
        
        # Конвертируем сумму (расходы в валюте страны пребывания - to_currency)
        # Курс: 1 FROM = rate TO, значит для конвертации TO -> FROM нужно делить
        converted_amount = amount / rate
        
        # Сохраняем во временное состояние
        user_states[user_id] = {
            "state": "confirm_expense",
            "data": {
                "trip_id": trip_id,
                "amount": amount,
                "converted_amount": converted_amount,
                "from_curr": from_curr,
                "to_curr": to_curr,
                "rate": rate
            }
        }
        
        expense_text = (
            f"💸 *Новый расход*\n\n"
            f"Вы ввели: *{format_amount(amount)} {to_curr}*\n"
            f"Конвертация: *{format_amount(amount)} {to_curr} = {format_amount(converted_amount)} {from_curr}*\n"
            f"(по курсу 1 {from_curr} = {format_rate(rate)} {to_curr})\n\n"
            f"Текущий баланс: {format_amount(to_balance)} {to_curr} = {format_amount(from_balance)} {from_curr}"
        )
        
        bot.send_message(
            user_id,
            expense_text,
            reply_markup=kb.confirm_expense_keyboard(amount, converted_amount, from_curr, to_curr),
            parse_mode="Markdown"
        )
        
    except ValueError:
        bot.send_message(
            user_id,
            "❌ Пожалуйста, введите корректное число (положительное):"
        )


def confirm_expense(user_id: int, amount: float, converted: float, from_curr: str, to_curr: str):
    """Подтвердить расход и обновить баланс"""
    state = user_states.get(user_id, {}).get("data", {})
    trip_id = state.get("trip_id")
    
    if not trip_id:
        bot.send_message(user_id, "❌ Что-то пошло не так. Начните заново.")
        return
    
    # Получаем текущий баланс
    trip = database.get_trip(trip_id)
    _, name, from_country, to_country, from_currency, to_currency, rate, from_balance, to_balance, is_custom, created_at = trip
    
    # Проверяем достаточно ли средств
    if to_balance < amount:
        bot.send_message(
            user_id,
            f"⚠️ Недостаточно средств! Баланс: {format_amount(to_balance)} {to_currency}",
            reply_markup=kb.main_menu_keyboard()
        )
        user_states.pop(user_id, None)
        return
    
    # Обновляем баланс (вычитаем расход)
    new_to_balance = to_balance - amount
    # Курс: 1 FROM = rate TO, значит для конвертации TO -> FROM нужно делить
    new_from_balance = from_balance - converted
    
    database.update_trip_balance(trip_id, new_from_balance, new_to_balance)
    
    # Записываем расход
    database.add_expense(
        trip_id=trip_id,
        amount=amount,
        currency=to_curr,
        converted_amount=converted,
        converted_currency=from_curr
    )
    
    # Очищаем состояние
    user_states.pop(user_id, None)
    
    success_text = (
        f"✅ *Расход учтён!*\n\n"
        f"Списано: {format_amount(amount)} {to_curr}\n"
        f"В домашней валюте: {format_amount(converted)} {from_curr}\n\n"
        f"💰 *Остаток:*\n"
        f"• {format_amount(new_to_balance)} {to_currency}\n"
        f"• {format_amount(new_from_balance)} {from_currency}"
    )
    
    bot.send_message(
        user_id,
        success_text,
        reply_markup=kb.main_menu_keyboard(),
        parse_mode="Markdown"
    )


def show_balance(user_id: int):
    """Показать баланс текущего путешествия"""
    trip_id = database.get_current_trip_id(user_id)
    
    if not trip_id:
        bot.send_message(
            user_id,
            "❌ У вас нет активного путешествия. Создайте новое путешествие.",
            reply_markup=kb.main_menu_keyboard()
        )
        return
    
    trip = database.get_trip(trip_id)
    
    if not trip:
        bot.send_message(
            user_id,
            "❌ Путешествие не найдено.",
            reply_markup=kb.main_menu_keyboard()
        )
        return
    
    _, name, from_country, to_country, from_curr, to_curr, rate, from_balance, to_balance, is_custom, created_at = trip
    
    # Получаем общие расходы
    total_from, total_to = database.get_total_expenses(trip_id)
    
    balance_text = (
        f"💰 *Баланс путешествия*\n\n"
        f"📍 *{name}*\n\n"
        f"💵 *Остаток:*\n"
        f"• В валюте поездки: {format_amount(to_balance)} {to_curr}\n"
        f"• В домашней валюте: {format_amount(from_balance)} {from_curr}\n\n"
        f"📊 *Потрачено всего:*\n"
        f"• {format_amount(total_to)} {to_curr}\n"
        f"• {format_amount(total_from)} {from_curr}\n\n"
        f"📈 Курс: 1 {from_curr} = {format_rate(rate)} {to_curr}\n"
        f"{'(установлен вручную)' if is_custom else '(актуальный)'}"
    )
    
    bot.send_message(
        user_id,
        balance_text,
        reply_markup=kb.main_menu_keyboard(),
        parse_mode="Markdown"
    )


def show_trips(user_id: int, edit_message: bool = False, message_id: int = None):
    """Показать список путешествий"""
    trips = database.get_trips(user_id)
    
    if not trips:
        msg = "📭 У вас пока нет путешествий. Создайте первое путешествие!"
        if edit_message:
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb.main_menu_keyboard())
        else:
            bot.send_message(user_id, msg, reply_markup=kb.main_menu_keyboard())
        return
    
    trips_text = "🎒 *Ваши путешествия:*\n\n"
    
    trip_id = database.get_current_trip_id(user_id)
    
    for trip in trips:
        trip_id_curr, name, from_country, to_country, from_curr, to_curr, rate, from_balance, to_balance, is_custom, created_at = trip
        # Зелёная галочка для активного, серый кружок для неактивного
        is_active = "✅" if trip_id_curr == trip_id else "⚪"
        
        trips_text += (
            f"{is_active} *{name}*\n"
            f"   💰 Остаток: {format_amount(to_balance)} {to_curr} / {format_amount(from_balance)} {from_curr}\n"
            f"   📊 Курс: 1 {from_curr} = {format_rate(rate)} {to_curr}\n\n"
        )
    
    trips_text += "_Нажмите на путешествие, чтобы сделать его активным_"
    
    if edit_message:
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=trips_text, reply_markup=kb.trips_list_keyboard(trips, trip_id), parse_mode="Markdown")
    else:
        bot.send_message(user_id, trips_text, reply_markup=kb.trips_list_keyboard(trips, trip_id), parse_mode="Markdown")
    

def show_history(user_id: int):
    """Показать историю расходов"""
    trip_id = database.get_current_trip_id(user_id)
    
    if not trip_id:
        bot.send_message(
            user_id,
            "❌ У вас нет активного путешествия. Создайте новое путешествие.",
            reply_markup=kb.main_menu_keyboard()
        )
        return

    trip = database.get_trip(trip_id)

    if not trip:
        bot.send_message(
            user_id,
            "❌ Путешествие не найдено.",
            reply_markup=kb.main_menu_keyboard()
        )
        return
    
    _, name, from_country, to_country, from_curr, to_curr, rate, _, _, _, _ = trip
    
    expenses = database.get_expenses(trip_id)
    
    if not expenses:
        bot.send_message(
            user_id,
            f"📜 *История расходов*\n\n"
            f"Путешествие: *{name}*\n\n"
            "Расходов пока нет.",
            reply_markup=kb.main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    history_text = f"📜 *История расходов*\n\n📍 *{name}*\n\n"
    
    for i, exp in enumerate(expenses[:20], 1):
        exp_id, amount, currency, converted_amount, converted_currency, description, created_at = exp
        
        date_str = datetime.fromisoformat(created_at).strftime("%d.%m %H:%M")
        
        history_text += (
            f"{i}. 💸 *{format_amount(amount)} {currency}*\n"
            f"   = {format_amount(converted_amount)} {converted_currency}\n"
            f"   📅 {date_str}\n\n"
        )
    
    total_from, total_to = database.get_total_expenses(trip_id)
    history_text += (
        f"--- Итого ---\n"
        f"Потрачено: {format_amount(total_to)} {to_curr} / {format_amount(total_from)} {from_curr}"
    )
    
    bot.send_message(
        user_id,
        history_text,
        reply_markup=kb.main_menu_keyboard(),
        parse_mode="Markdown"
    )


def handle_set_rate(user_id: int, edit_message: bool = False, message_id: int = None):
    """Начать изменение курса"""
    trip_id = database.get_current_trip_id(user_id)
    
    if not trip_id:
        msg = "❌ У вас нет активного путешествия. Создайте новое путешествие."
        if edit_message:
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb.main_menu_keyboard())
        else:
            bot.send_message(user_id, msg, reply_markup=kb.main_menu_keyboard())
        return
    
    trip = database.get_trip(trip_id)
    
    if not trip:
        msg = "❌ Путешествие не найдено."
        if edit_message:
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text=msg, reply_markup=kb.main_menu_keyboard())
        else:
            bot.send_message(user_id, msg, reply_markup=kb.main_menu_keyboard())
        return
    
    _, name, from_country, to_country, from_curr, to_curr, rate, _, _, _, _ = trip
    
    user_states[user_id] = {"state": "set_rate_menu", "data": {"trip_id": trip_id}}
    
    rate_text = (
        f"📊 *Изменение курса*\n\n"
        f"Путешествие: *{name}*\n\n"
        f"Текущий курс: 1 {from_curr} = {format_rate(rate)} {to_curr}\n\n"
        f"Выберите действие:"
    )
    
    if edit_message:
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text=rate_text, reply_markup=kb.set_rate_keyboard(trip_id, rate, from_curr, to_curr), parse_mode="Markdown")
    else:
        bot.send_message(user_id, rate_text, reply_markup=kb.set_rate_keyboard(trip_id, rate, from_curr, to_curr), parse_mode="Markdown")


def handle_new_rate(user_id: int, rate_str: str):
    """Обработка нового курса (введенного вручную)"""
    state = user_states.get(user_id, {})
    trip_id = state.get("data", {}).get("trip_id")
    
    if not trip_id:
        bot.send_message(user_id, "❌ Что-то пошло не так.")
        return
    
    try:
        rate = float(rate_str.replace(",", "."))
        if rate <= 0:
            raise ValueError()
        
        database.update_trip_rate(trip_id, rate, is_custom=True)
        
        # Пересчитываем баланс
        trip = database.get_trip(trip_id)
        _, name, from_country, to_country, from_curr, to_curr, old_rate, from_balance, to_balance, _, _ = trip
        
        # Пересчитываем баланс в домашней валюте (FROM)
        # Курс: 1 FROM = rate TO, значит для конвертации TO -> FROM нужно делить
        new_from_balance = to_balance / rate
        
        database.update_trip_balance(trip_id, new_from_balance, to_balance)
        
        user_states.pop(user_id, None)
        
        success_text = (
            f"✅ *Курс обновлён!*\n\n"
            f"Новый курс: 1 {from_curr} = {format_rate(rate)} {to_curr}\n\n"
            f"💰 Баланс пересчитан:\n"
            f"• {format_amount(to_balance)} {to_curr}\n"
            f"• {format_amount(new_from_balance)} {from_curr}"
        )

        bot.send_message(
            user_id,
            success_text,
            reply_markup=kb.main_menu_keyboard(),
            parse_mode="Markdown"
        )

    except ValueError:
        bot.send_message(
            user_id,
            "❌ Пожалуйста, введите корректное число:"
        )


def handle_use_api_rate(user_id: int):
    """Использовать официальный курс API"""
    state = user_states.get(user_id, {})
    trip_id = state.get("data", {}).get("trip_id")
    
    if not trip_id:
        bot.send_message(user_id, "❌ Что-то пошло не так.")
        return
    
    trip = database.get_trip(trip_id)
    _, name, from_country, to_country, from_curr, to_curr, old_rate, from_balance, to_balance, _, _ = trip
    
    # Получаем курс от API
    bot.send_message(user_id, "⏳ Получаю официальный курс от API...")
    
    new_rate = get_exchange_rate(from_curr, to_curr)
    
    if new_rate is None:
        bot.send_message(
            user_id,
            "❌ Не удалось получить курс от API. Попробуйте позже.",
            reply_markup=kb.main_menu_keyboard()
        )
        return

    # Обновляем курс (не пользовательский)
    database.update_trip_rate(trip_id, new_rate, is_custom=False)

    # Пересчитываем баланс
    # Курс: 1 FROM = rate TO, значит для конвертации TO -> FROM нужно делить
    new_from_balance = to_balance / new_rate
    database.update_trip_balance(trip_id, new_from_balance, to_balance)
    
    user_states.pop(user_id, None)
    
    success_text = (
        f"✅ *Официальный курс установлен!*\n\n"
        f"Курс: 1 {from_curr} = {format_rate(new_rate)} {to_curr}\n\n"
        f"💰 Баланс пересчитан:\n"
        f"• {format_amount(to_balance)} {to_curr}\n"
        f"• {format_amount(new_from_balance)} {from_curr}"
    )
    
    bot.send_message(
        user_id,
        success_text,
        reply_markup=kb.main_menu_keyboard(),
        parse_mode="Markdown"
    )


# --- Обработчики команд ---

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """Обработчик команды /start"""
    send_welcome(message)


@bot.message_handler(commands=['newtrip'])
def cmd_newtrip(message):
    """Обработчик команды /newtrip"""
    user_id = message.from_user.id
    database.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    handle_new_trip(user_id)


@bot.message_handler(commands=['switch'])
def cmd_switch(message):
    """Обработчик команды /switch"""
    user_id = message.from_user.id
    database.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    show_trips(user_id)


@bot.message_handler(commands=['balance'])
def cmd_balance(message):
    """Обработчик команды /balance"""
    user_id = message.from_user.id
    database.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    show_balance(user_id)


@bot.message_handler(commands=['history'])
def cmd_history(message):
    """Обработчик команды /history"""
    user_id = message.from_user.id
    database.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    show_history(user_id)


@bot.message_handler(commands=['setrate'])
def cmd_setrate(message):
    """Обработчик команды /setrate"""
    user_id = message.from_user.id
    database.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    handle_set_rate(user_id)


# --- Обработчики callback-запросов ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик callback-запросов"""
    user_id = call.from_user.id
    data = call.data
    
    try:
        bot.answer_callback_query(call.id)
    except:
        pass
    
    # Главное меню
    if data == "menu_new_trip":
        handle_new_trip(user_id)
    
    elif data == "menu_trips":
        show_trips(user_id)
    
    elif data == "menu_balance":
        show_balance(user_id)
    
    elif data == "menu_history":
        show_history(user_id)
    
    elif data == "menu_set_rate":
        handle_set_rate(user_id)
    
    elif data == "menu_back":
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text="Главное меню:",
            reply_markup=kb.main_menu_keyboard()
        )
    
    # Подтверждение курса
    elif data == "rate_accept":
        data_state = user_states.get(user_id, {}).get("data", {})
        data_state["is_custom_rate"] = False
        user_states[user_id] = {"state": "waiting_initial_amount", "data": data_state}
        
        from_curr = data_state["from_currency"]
        
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=f"✅ Курс подтверждён!\n\n💰 Теперь введите начальную сумму для поездки в *{from_curr}*:",
            parse_mode="Markdown"
        )
    
    elif data == "rate_custom":
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text="Введите курс обмена (сколько единиц валюты назначения за 1 единицу домашней валюты):"
        )
        user_states[user_id]["state"] = "waiting_custom_rate"
    
    # Подтверждение расхода
    elif data.startswith("confirm_expense_"):
        parts = data.split("_")
        if len(parts) >= 5:
            amount = float(parts[2])
            converted = float(parts[3])
            from_curr = parts[4]
            to_curr = parts[5]
            confirm_expense(user_id, amount, converted, from_curr, to_curr)
    
    elif data == "expense_cancel":
        user_states.pop(user_id, None)
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text="❌ Расход отменён.",
            reply_markup=kb.main_menu_keyboard()
        )
    
    # Переключение путешествия
    elif data.startswith("switch_trip_"):
        trip_id = int(data.split("_")[-1])
        database.set_current_trip(user_id, trip_id)
        show_trips(user_id, edit_message=True, message_id=call.message.message_id)
    
    # Подтверждение удаления путешествия
    elif data.startswith("confirm_delete_trip_"):
        trip_id = int(data.split("_")[-1])
        trip = database.get_trip(trip_id)
        if trip:
            _, name, from_country, to_country, from_curr, to_curr, rate, from_balance, to_balance, is_custom, created_at = trip
            bot.edit_message_text(
                chat_id=user_id,
                message_id=call.message.message_id,
                text=f"⚠️ *Вы уверены?*\n\n"
                     f"Вы действительно хотите удалить путешествие *\"{name}\"* безвозвратно?\n\n"
                     f"Все данные будут потеряны.",
                reply_markup=kb.confirm_delete_keyboard(trip_id, name),
                parse_mode="Markdown"
            )
    
    # Удаление путешествия (после подтверждения)
    elif data.startswith("delete_trip_"):
        trip_id = int(data.split("_")[-1])
        trip = database.get_trip(trip_id)
        if trip:
            _, name, _, _, _, _, _, _, _, _, _ = trip
            database.delete_trip(trip_id)
            
            # Если удалили текущее путешествие - сбрасываем
            current_trip_id = database.get_current_trip_id(user_id)
            if current_trip_id == trip_id:
                # Находим первое доступное путешествие
                trips = database.get_trips(user_id)
                if trips:
                    database.set_current_trip(user_id, trips[0][0])
                else:
                    # Нет путешествий - сбрасываем текущее
                    database.set_current_trip(user_id, None)
            
            # Показываем обновленный список путешествий
            show_trips(user_id, edit_message=True, message_id=call.message.message_id)
    
    # Отмена удаления
    elif data == "cancel_delete_trip":
        show_trips(user_id, edit_message=True, message_id=call.message.message_id)
    
    # Изменение курса - использовать официальный
    elif data.startswith("use_api_rate_"):
        trip_id = int(data.split("_")[-1])
        user_states[user_id] = {"state": "set_rate_menu", "data": {"trip_id": trip_id}}
        handle_use_api_rate(user_id)
    
    # Изменение курса - ввести вручную
    elif data.startswith("manual_rate_"):
        trip_id = int(data.split("_")[-1])
        trip = database.get_trip(trip_id)
        _, name, from_country, to_country, from_curr, to_curr, rate, _, _, _, _ = trip
        user_states[user_id] = {"state": "waiting_new_rate", "data": {"trip_id": trip_id}}
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=f"Введите новый курс (сколько {to_curr} за 1 {from_curr}):\n"
                 f"Например: 0.0123\n"
                 f"Текущий курс: 1 {from_curr} = {format_rate(rate)} {to_curr}",
            reply_markup=kb.back_keyboard("menu_back"),
            parse_mode="Markdown"
        )

    # Удаление путешествия
    elif data.startswith("trip_delete_"):
        trip_id = int(data.split("_")[-1])
        database.delete_trip(trip_id)
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text="✅ Путешествие удалено.",
            reply_markup=kb.main_menu_keyboard()
        )


# --- Обработчики текстовых сообщений ---

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработчик текстовых сообщений"""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Создаём пользователя если его нет
    database.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    
    # Проверяем, есть ли активное состояние
    state = user_states.get(user_id, {})
    current_state = state.get("state", "")
    
    # Проверяем, является ли сообщение числом (расход)
    try:
        # Пробуем распознать как число
        test_num = text.replace(" ", "").replace(",", ".")
        float(test_num)
        is_number = True
    except:
        is_number = False
    
    # Если есть активное путешествие и сообщение - число, обрабатываем как расход
    if is_number and current_state == "":
        trip_id = database.get_current_trip_id(user_id)
        if trip_id:
            handle_expense_input(user_id, text)
            return
    
    # Обработка по состояниям
    if current_state == "waiting_trip_name":
        handle_trip_name(user_id, text)
    
    elif current_state == "waiting_from_country":
        handle_from_country(user_id, text)
    
    elif current_state == "waiting_to_country":
        handle_to_country(user_id, text)
    
    elif current_state == "waiting_custom_rate":
        handle_custom_rate(user_id, text)
    
    elif current_state == "waiting_initial_amount":
        handle_initial_amount(user_id, text)
    
    elif current_state == "waiting_new_rate":
        handle_new_rate(user_id, text)
    
    else:
        # Показываем главное меню
        bot.send_message(
            user_id,
            "Я не понял ваше сообщение. Используйте кнопки меню или команды:",
            reply_markup=kb.main_menu_keyboard()
        )


# --- Запуск бота ---

if __name__ == "__main__":
    print("🚀 Travel Wallet Bot запущен!")
    print("Нажмите Ctrl+C для остановки")
    
    # Удаляем webhook для работы в режиме polling
    bot.remove_webhook()
    
    # Запускаем бота
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
