import logging
import os

from dotenv import load_dotenv

from kanal_test.celery import app
from google_service.gspread.table import *

load_dotenv()

logger = logging.getLogger(__name__)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    app.control.purge()  # очищаем очередь старых задач, если она была
    # не рекомендуется ставить слишком частое обновление в связи блокировкой запросов гуглом
    timer = os.getenv('TIMER')
    sender.add_periodic_task(
        float(timer),
        update_db.s(os.getenv('TABLE_NAME'), os.getenv('SHEET_NAME')),
        name=f'update db every {timer} sec'
    )
    sender.add_periodic_task(
        5.0,

    )


@app.task
def update_db(table_name, sheet_name):
    gtable = GTable(table_name, sheet_name)
    gtable.update_db_table()
