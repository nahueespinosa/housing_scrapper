import sqlite3

from contextlib import closing
from providers import Property


class Database:
    sql_create_properties_table = \
        """
        CREATE TABLE IF NOT EXISTS properties (
            id integer PRIMARY KEY,
            internal_id text NOT NULL,
            provider text NOT NULL,
            url text NOT NULL,
            captured_date integer DEFAULT CURRENT_TIMESTAMP
        );
        """
    sql_create_index_on_properties_table = 'CREATE INDEX IF NOT EXISTS properties_internal_provider ON properties (internal_id, provider)'
    sql_select_property = 'SELECT * FROM properties WHERE internal_id=:internal_id AND provider=:provider'
    sql_insert_property = 'INSERT INTO properties (internal_id, provider, url) VALUES (:internal_id, :provider, :url)'

    def __init__(self, filename: str):
        self.filename = filename
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.filename)
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(self.sql_create_properties_table)
            cursor.execute(self.sql_create_index_on_properties_table)
        return self

    def __exit__(self, type, value, traceback):
        self.connection.commit()
        self.connection.close()

    def property_exists(self, prop: Property) -> bool:
        if self.connection:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute(self.sql_select_property, prop.__dict__)
                return cursor.fetchone() is not None

    def insert_property(self, prop: Property) -> bool:
        if self.connection:
            if not self.property_exists(prop):
                with closing(self.connection.cursor()) as cursor:
                    cursor.execute(self.sql_insert_property, prop.__dict__)
                return True
        return False
