import requests
from dotenv import load_dotenv
import os
load_dotenv()

def get_current_rate(default: str = "USD", currencies: list[str] = ["EUR", "GBP", "JPY"]):
    url = "https://api.exchangerate.host/live"
    params = {
        "access_key": os.getenv("CURRENCY_API_KEY"),
        "source": default,
        "currencies": ",".join(currencies)
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data


def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Конвертируй одну валюту в другую
    Выходные данные:
    {'success': True, 'terms': 'https://currencylayer.com/terms', 'privacy': 'https://currencylayer.com/privacy', 'query': {'from': 'USD', 'to': 'EUR', 'amount': 100}, 'info': {'timestamp': 1775136485, 'quote': 0.867405}, 'result': 86.7405}
"""

    url = "https://api.exchangerate.host/convert"
    params = {
        "access_key": os.getenv("CURRENCY_API_KEY"),
        "from": from_currency,
        "to": to_currency,
        "amount": amount
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_all_supported_currencies(base: str = "USD"):
    url = "https://api.exchangerate.host/list"
    params = {
        "access_key": os.getenv("CURRENCY_API_KEY"),
        "base": base
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data


if __name__ == "__main__":
   print(convert_currency(100, "USD", "EUR"))
   

