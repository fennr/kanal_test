import os
import logging
import requests
import gspread
import pandas as pd
from datetime import datetime
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Fields(str, Enum):
    VBELN = 'vbeln'
    DATE = 'ddate'
    USD = 'price_usd'


class GTable:
    """
    Данные гугл таблицы
    """

    def __init__(self, table_name: str, sheet_name: str):
        self.data_frame = None
        try:
            # google_service/gspread/
            _gp = gspread.service_account(filename='google_service/gspread/unwinddigital-test-b5be7a3a2d9e.json')
            _gs = _gp.open(table_name)
            _ws = _gs.worksheet(sheet_name)

            _all_rows = _ws.get_all_values()
            # Вставим свое именование колонок в соответствии и техническими именами полей модели
            _all_rows.pop(0)
            _columns = [Fields.VBELN.value, Fields.USD.value, Fields.DATE.value]

            self.data_frame = pd.DataFrame(_all_rows, columns=_columns)

        except gspread.SpreadsheetNotFound:
            logger.error(f"Не найдена гугл таблица")
        except gspread.WorksheetNotFound:
            logger.error(f"Не найден лист на гугл таблице")
        except gspread.exceptions.GSpreadException:
            logger.error(f"Превышено число запросов в минуту, блокировка со стороны гугла")
        except FileNotFoundError:
            logger.error(f"Не найден файл сервис аккаунта")

    def update_db_table(self):
        """
        Обновление БД на основе записей гугл таблицы
        :return:
        """
        save_ids = []
        from google_service.models import Order  # импорт внутри для тестирования
        for i, row in self.data_frame.iterrows():
            date: datetime = datetime.strptime(row[Fields.DATE], "%d.%m.%Y")
            correct_date: str = date.strftime("%Y-%m-%d")
            order, created = Order.objects.update_or_create(
                defaults={
                    Fields.VBELN: int(row[Fields.VBELN]),
                    Fields.DATE: correct_date,
                    Fields.USD: float(row[Fields.USD])
                },
                vbeln=int(row[Fields.VBELN])
            )

            save_ids.append(order.id)

            if created:
                logger.info(f"Add {order}")
            else:
                pass
            if order.is_overdue and not order.overdue_message:
                order.send_telegram(text=f"Заказ {order.vbeln} был просрочен!")

        # удаляем записи, которые не встретились в таблице
        Order.objects.exclude(id__in=save_ids).delete()

