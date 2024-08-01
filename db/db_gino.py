import logging
from gino import Gino
from typing import List
import sqlalchemy as sa
from config import POSTGRES_URI

db = Gino()
logger = logging.getLogger(__name__)


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


async def on_startup():
    logger.info("Установка соединения с PostgreSQL...")
    await db.set_bind(POSTGRES_URI)
