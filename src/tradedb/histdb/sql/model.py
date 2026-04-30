from datetime import timedelta
from typing import Type

from peewee import CharField, CompositeKey, FloatField, IntegerField, Model, Proxy

DB_PROXY = Proxy()


class OHLCModel(Model):
    symbol = CharField()
    timestamp = IntegerField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = FloatField(null=True)

    class Meta:
        database = DB_PROXY
        primary_key = CompositeKey("symbol", "timestamp")
        without_rowid = True


def create_model(timeframe: timedelta) -> Type[OHLCModel]:
    class DynamicOHLCModel(OHLCModel):
        class Meta:  # type: ignore
            table_name = f"timeframe_{int(timeframe.total_seconds())}"

    return DynamicOHLCModel
