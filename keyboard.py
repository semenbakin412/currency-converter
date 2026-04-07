from telebot import types


def main_menu_keyboard():
    """Главное меню бота"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton("🆕 Создать новое путешествие", callback_data="menu_new_trip"),
        types.InlineKeyboardButton("🎒 Мои путешествия", callback_data="menu_trips")
    )
    keyboard.add(
        types.InlineKeyboardButton("💰 Баланс", callback_data="menu_balance"),
        types.InlineKeyboardButton("📜 История расходов", callback_data="menu_history")
    )
    keyboard.add(
        types.InlineKeyboardButton("📊 Изменить курс", callback_data="menu_set_rate")
    )
    
    return keyboard


def trips_list_keyboard(trips: list, current_trip_id: int = None):
    """Клавиатура списка путешествий"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    for trip in trips:
        trip_id, name, from_country, to_country = trip[0], trip[1], trip[2], trip[3]
        # Зелёная галочка для активного путешествия
        if trip_id == current_trip_id:
            btn_text = f"✅ {name}"
        else:
            btn_text = f"⚪ {name}"
        
        # Кнопка выбора путешествия (слева) и удаления (справа)
        keyboard.row(
            types.InlineKeyboardButton(btn_text, callback_data=f"switch_trip_{trip_id}"),
            types.InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_trip_{trip_id}")
        )
    
    keyboard.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="menu_back"))
    return keyboard


def confirm_delete_keyboard(trip_id: int, trip_name: str):
    """Клавиатура подтверждения удаления путешествия"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton("✅ Да, удалить", callback_data=f"delete_trip_{trip_id}"),
        types.InlineKeyboardButton("❌ Нет", callback_data="cancel_delete_trip")
    )
    
    return keyboard


def confirm_expense_keyboard(amount: float, converted: float, from_curr: str, to_curr: str):
    """Клавиатура подтверждения расхода"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    callback_data = f"confirm_expense_{amount}_{converted}_{from_curr}_{to_curr}"
    
    keyboard.add(
        types.InlineKeyboardButton("✅ Да, учесть", callback_data=callback_data),
        types.InlineKeyboardButton("❌ Нет", callback_data="expense_cancel")
    )
    
    return keyboard


def yes_no_keyboard(yes_callback: str, no_callback: str = "cancel"):
    """Универсальная да/нет клавиатура"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ Да", callback_data=yes_callback),
        types.InlineKeyboardButton("❌ Нет", callback_data=no_callback)
    )
    return keyboard


def back_keyboard(callback_data: str = "menu_back"):
    """Кнопка назад"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data=callback_data))
    return keyboard


def set_rate_keyboard(trip_id: int, current_rate: float, from_curr: str, to_curr: str):
    """Клавиатура изменения курса"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопка использования официального курса
    keyboard.add(types.InlineKeyboardButton("📡 Использовать официальный курс", callback_data=f"use_api_rate_{trip_id}"))
    
    # Кнопка ввода курса вручную
    keyboard.add(types.InlineKeyboardButton("✏️ Ввести курс вручную", callback_data=f"manual_rate_{trip_id}"))
    
    # Кнопка назад
    keyboard.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="menu_back"))
    
    return keyboard


def trips_management_keyboard(trip_id: int):
    """Меню управления путешествием"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton("💰 Показать баланс", callback_data=f"trip_balance_{trip_id}"),
        types.InlineKeyboardButton("📜 История", callback_data=f"trip_history_{trip_id}")
    )
    keyboard.add(
        types.InlineKeyboardButton("📊 Изменить курс", callback_data=f"trip_set_rate_{trip_id}"),
        types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"trip_delete_{trip_id}")
    )
    keyboard.add(types.InlineKeyboardButton("🔙 К списку путешествий", callback_data="menu_trips"))
    
    return keyboard
