# tradedb

A Python library for storing market data 🐍💾

## Installation

### Requirements

- Python 3.13+

### Install

#### uv

```bash
uv add git+https://github.com/fburleson/tradedb.git
```

#### pip

```bash
pip install git+https://github.com/fburleson/tradedb.git
```

## Usage

```py
from datetime import timedelta

from tradedb import SqliteHistDB


def main():
    db = SqliteHistDB("data.db")
    min15 = db.chart("EURUSD", timedelta(minutes=15))
    print(min15[-100:])


if __name__ == "__main__":
    main()

```