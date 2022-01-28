import logging
import sqlite3

from providers.provider import Property
from contextlib import closing
from typing import Dict, Iterable, List


DATABASE_NAME = 'properties.db'

def create_database() -> None:
    sql_create_properties_table = """
                                  CREATE TABLE IF NOT EXISTS properties (
                                      id integer PRIMARY KEY,
                                      internal_id text NOT NULL,
                                      provider text NOT NULL,
                                      url text NOT NULL,
                                      captured_date integer DEFAULT CURRENT_TIMESTAMP
                                  );
                                  """
    sql_create_index_on_properties_table = 'CREATE INDEX IF NOT EXISTS properties_internal_provider ON properties (internal_id, provider)'

    with sqlite3.connect(DATABASE_NAME) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql_create_properties_table)
            cursor.execute(sql_create_index_on_properties_table)

def property_exists(connection: sqlite3.Connection, prop: Property) -> bool:
    stmt = 'SELECT * FROM properties WHERE internal_id=:internal_id AND provider=:provider'
    with closing(connection.cursor()) as cursor:
        logging.info(f"Processing property {prop.provider}:{prop.internal_id}")
        cursor.execute(stmt, prop.__dict__)
        return cursor.fetchone() is not None

def store_properties(properties: Iterable[Property]) -> List[Property]:
    stmt = 'INSERT INTO properties (internal_id, provider, url) VALUES (:internal_id, :provider, :url)'
    new_properties = []
    with sqlite3.connect(DATABASE_NAME) as connection:
        for prop in properties:
            if not property_exists(connection, prop):
                connection.execute(stmt, prop.__dict__)
                new_properties.append(prop)
    return new_properties
