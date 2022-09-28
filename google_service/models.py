import os

import requests
import time
from xmltodict import parse
from datetime import datetime
import logging

from django.db import models
from django.core.cache import cache

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Create your models here.


def usd_to_rub() -> float:
    cbr_xml: str = 'https://www.cbr.ru/scripts/XML_daily.asp'
    resp: requests.Response = requests.get(cbr_xml)
    cbr_data: list = parse(resp.text)['ValCurs']['Valute']
    for currency in cbr_data:
        if currency['CharCode'] == 'USD':
            return currency['Value'].replace(',', '.')


def get_cached_price(key: str, timeout: int = 600) -> float:
    value = cache.get(key)
    if not value:
        value = usd_to_rub()
        cache.add(key=key, value=value, timeout=timeout)
    return float(value)


class Order(models.Model):
    """
    Заказ на поставку
    """
    vbeln = models.IntegerField(verbose_name="Order number", unique=True)
    ddate = models.DateField(verbose_name="Delivery date", default=None)
    price_usd = models.DecimalField(verbose_name="Price $", max_digits=15, decimal_places=4)
    price_rub = models.DecimalField(verbose_name="Price ₽", max_digits=15, decimal_places=4)
    overdue_message = models.BooleanField(verbose_name="Sending message", default=False)

    def __str__(self):
        return f"Order(id={self.id}, vbeln={self.vbeln}, dtime={self.ddate}, $={self.price_usd}, ₽={self.price_rub})"

    def is_overdue(self) -> bool:
        return True if self.ddate < datetime.now() else False

    def send_telegram(self, text: str):
        try:
            token = os.getenv('TELEGRAM_TOKEN')
            url = "https://api.telegram.org/bot"
            channel_id = f"@{os.getenv('TELEGRAM_CHANNEL_ID')}"
            url += token
            method = url + "/sendMessage"

            r = requests.post(method, data={
                "chat_id": channel_id,
                "text": text
            })

            if r.status_code != 200:
                logger.error("Ошибка отправки сообщения в тг")
            else:
                self.overdue_message = True
                super(Order, self).save()
                time.sleep(4)  # не лучший вариант, но не допускаем слишком частых вызововов
            return r.status_code
        except Exception:
            print("Ошибка при попытке отправить сообщение в тг."
                  "Проверьте что указан токен и он администратор группы")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        one_usd_price = get_cached_price('one_usd')
        self.price_rub = one_usd_price * float(self.price_usd)
        super(Order, self).save()

    class Meta:
        verbose_name = "Order"


