import os
import sqlite3
from pathlib import Path


def connect(db_path=None):
    if db_path is None:
        db_path = os.environ.get(
            "INVENTORY_DB",
            Path(__file__).parent / "inventory.db"
        )

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(connection):
    schema_path = Path(__file__).parent / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    connection.executescript(schema)