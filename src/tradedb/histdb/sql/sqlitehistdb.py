from datetime import timedelta
from pathlib import Path

import pandas as pd
from peewee import SqliteDatabase

from tradedb.histdb.histdb import DBChart, HistDB
from tradedb.histdb.sql.model import DB_PROXY, create_model


class SqliteChart(DBChart["SqliteHistDB"]):
    def __init__(self, db: "SqliteHistDB", symbol: str, timeframe: timedelta):
        super().__init__(db, symbol, timeframe)
        self._table = create_model(timeframe)
        self.db._conn.create_tables([self._table])
        self._query = self._table.select(
            self._table.timestamp,
            self._table.open,
            self._table.high,
            self._table.low,
            self._table.close,
            self._table.volume,
        ).where(self._table.symbol == self.symbol)

    def __len__(self) -> int:
        return self._query.count()

    def insert(self, data: pd.DataFrame):
        super().insert(data)
        data = data.assign(symbol=lambda _: self.symbol)
        data["timestamp"] = data.index.tz_convert("UTC").view("int64")  # type: ignore
        with self.db._conn.atomic():
            self._table.insert_many(data.to_dict("records")).on_conflict(
                "REPLACE"
            ).execute()

    def _query_slice(self, start: int | None, stop: int | None):
        count: int = len(self)
        if start is None:
            start = 0
        elif start < 0:
            start = count - abs(start)
        if stop is None:
            stop = count
        elif stop < 0:
            stop = count - abs(stop)
        return (
            self._query.order_by(self._table.timestamp.asc())
            .offset(start)
            .limit(stop - start)
        )

    def __getitem__(self, key: int | slice):
        query = self._query_slice(
            key.start if isinstance(key, slice) else key,
            key.stop if isinstance(key, slice) else key + 1,
        )
        data: pd.DataFrame = pd.DataFrame(
            list(query.dicts()),
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        data["timestamp"] = pd.to_datetime(data["timestamp"], unit="us", utc=True)
        data.set_index("timestamp", inplace=True)
        data.index.name = "datetime"
        data.index.freq = self.timeframe  # type: ignore
        return data.astype("float64")


class SqliteHistDB(HistDB[SqliteChart]):
    def __init__(self, path: Path):
        super().__init__(path)
        self._conn = SqliteDatabase(self._path)
        self._conn.connect()
        DB_PROXY.initialize(self._conn)

    def __exit__(self, exc_type, exc, tb):
        self._conn.close()

    def chart(self, symbol: str, timeframe: timedelta) -> SqliteChart:
        return SqliteChart(self, symbol, timeframe)
