from abc import ABC, abstractmethod
from datetime import timedelta, timezone
from pathlib import Path
from typing import Self

import pandas as pd

from tradedb._dev.util import create_repr


class DBChart[T: "HistDB"](ABC):
    def __init__(
        self, db: T, symbol: str, timeframe: timedelta, tz: timezone = timezone.utc
    ):
        self._db: T = db
        self._symbol: str = symbol
        self._timeframe: timedelta = timeframe
        self._tz: timezone = tz

    def __repr__(self) -> str:
        return create_repr(self, DBChart.symbol, DBChart.timeframe)

    @abstractmethod
    def __getitem__(self, key: int | slice) -> pd.DataFrame:
        pass

    @abstractmethod
    def insert(self, data: pd.DataFrame):
        pass

    @property
    def db(self) -> T:
        return self._db

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def timeframe(self) -> timedelta:
        return self._timeframe


class HistDB[T: DBChart](ABC):
    def __init__(self, path: Path):
        self._path: Path = path

    def __repr__(self) -> str:
        return create_repr(self, HistDB.path)

    def __enter__(self) -> Self:
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc, tb):
        pass

    @abstractmethod
    def chart(self, symbol: str, timeframe: timedelta) -> T:
        pass

    @property
    def path(self) -> Path:
        return Path(self._path)
