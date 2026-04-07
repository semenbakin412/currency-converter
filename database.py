import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import os

DB_PATH = "travel_wallet.db"


def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            current_trip_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица путешествий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            from_country TEXT NOT NULL,
            to_country TEXT NOT NULL,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            exchange_rate REAL NOT NULL,
            from_balance REAL NOT NULL,
            to_balance REAL NOT NULL,
            is_custom_rate INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Таблица расходов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            converted_amount REAL NOT NULL,
            converted_currency TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def get_connection():
    """Получить соединение с БД"""
    return sqlite3.connect(DB_PATH)


# --- Пользователи ---

def get_or_create_user(user_id: int, username: str = None, first_name: str = None):
    """Получить или создать пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            'INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
            (user_id, username, first_name)
        )
        conn.commit()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
    
    conn.close()
    return user


def set_current_trip(user_id: int, trip_id: int):
    """Установить текущее путешествие"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET current_trip_id = ? WHERE user_id = ?', (trip_id, user_id))
    conn.commit()
    conn.close()


def get_current_trip_id(user_id: int) -> Optional[int]:
    """Получить ID текущего путешествия"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_trip_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# --- Путешествия ---

def create_trip(user_id: int, name: str, from_country: str, to_country: str,
                from_currency: str, to_currency: str, exchange_rate: float,
                from_balance: float, to_balance: float, is_custom_rate: bool = False) -> int:
    """Создать новое путешествие"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trips (user_id, name, from_country, to_country, from_currency, 
                          to_currency, exchange_rate, from_balance, to_balance, is_custom_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, from_country, to_country, from_currency, to_currency,
          exchange_rate, from_balance, to_balance, 1 if is_custom_rate else 0))
    
    trip_id = cursor.lastrowid
    
    # Устанавливаем как текущее
    cursor.execute('UPDATE users SET current_trip_id = ? WHERE user_id = ?', (trip_id, user_id))
    
    conn.commit()
    conn.close()
    return trip_id


def get_trips(user_id: int) -> List[tuple]:
    """Получить все путешествия пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, from_country, to_country, from_currency, to_currency,
               exchange_rate, from_balance, to_balance, is_custom_rate, created_at
        FROM trips WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    trips = cursor.fetchall()
    conn.close()
    return trips


def get_trip(trip_id: int) -> Optional[tuple]:
    """Получить путешествие по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, from_country, to_country, from_currency, to_currency,
               exchange_rate, from_balance, to_balance, is_custom_rate, created_at
        FROM trips WHERE id = ?
    ''', (trip_id,))
    trip = cursor.fetchone()
    conn.close()
    return trip


def update_trip_balance(trip_id: int, from_balance: float, to_balance: float):
    """Обновить баланс путешествия"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE trips SET from_balance = ?, to_balance = ? WHERE id = ?',
        (from_balance, to_balance, trip_id)
    )
    conn.commit()
    conn.close()


def update_trip_rate(trip_id: int, exchange_rate: float, is_custom: bool = True):
    """Обновить курс путешествия"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE trips SET exchange_rate = ?, is_custom_rate = ? WHERE id = ?',
        (exchange_rate, 1 if is_custom else 0, trip_id)
    )
    conn.commit()
    conn.close()


def delete_trip(trip_id: int):
    """Удалить путешествие"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE trip_id = ?', (trip_id,))
    cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    conn.close()


# --- Расходы ---

def add_expense(trip_id: int, amount: float, currency: str,
                converted_amount: float, converted_currency: str, description: str = None):
    """Добавить расход"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO expenses (trip_id, amount, currency, converted_amount, converted_currency, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (trip_id, amount, currency, converted_amount, converted_currency, description))
    
    conn.commit()
    conn.close()


def get_expenses(trip_id: int, limit: int = 50) -> List[tuple]:
    """Получить историю расходов"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, amount, currency, converted_amount, converted_currency, description, created_at
        FROM expenses WHERE trip_id = ? ORDER BY created_at DESC LIMIT ?
    ''', (trip_id, limit))
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def get_total_expenses(trip_id: int) -> tuple:
    """Получить общую сумму расходов в обеих валютах"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(amount), SUM(converted_amount) 
        FROM expenses WHERE trip_id = ?
    ''', (trip_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] or 0, result[1] or 0


# Инициализировать БД при импорте
init_db()
