import os
from datetime import datetime

import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor


class UrlsRepository:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")
        self.connection_params = self._parse_database_url(database_url)

    def _parse_database_url(self, database_url):
        return extensions.parse_dsn(database_url)

    def _connect(self):
        return psycopg2.connect(**self.connection_params)

    def get_url_by_id(self, id):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                return cur.fetchone()

    def save_url(self, url):
        created_at = datetime.now().strftime('%Y-%m-%d')

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)""",
                    (url["url"], created_at)
                )
                conn.commit()

    def get_url_by_name(self, url):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
                return cur.fetchone()
