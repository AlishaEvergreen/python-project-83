import os
from datetime import datetime

import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor


class BaseRepository:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")
        self.connection_params = self._parse_database_url(database_url)

    def _parse_database_url(self, database_url):
        return extensions.parse_dsn(database_url)

    def _connect(self):
        return psycopg2.connect(**self.connection_params)


class UrlsRepository(BaseRepository):
    def get_entities(self):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""SELECT * FROM urls
                            ORDER BY id DESC, created_at DESC""")
                return cur.fetchall()

    def get_url_data_by_id(self, id):
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
                    VALUES (%s, %s) RETURNING id""",
                    (url["url"], created_at)
                )
                url_id = cur.fetchone()[0]
            conn.commit()

        return url_id

    def get_url_data_by_name(self, url):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
                return cur.fetchone()


class UrlChecksRepository(BaseRepository):
    def get_checks_by_id(self, url_id):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                            SELECT * FROM url_checks
                            WHERE url_id = %s
                            ORDER BY id DESC, created_at DESC
                            """,
                            (url_id,)
                            )
                return cur.fetchall()

    def save_url_check(self, url):
        created_at = datetime.now().strftime('%Y-%m-%d')

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks (url_id, status_code, h1,
                    title, description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (url['id'], 0, '', '', '', created_at)
                    )
                url_check_id = cur.fetchone()[0]
            conn.commit()

        return url_check_id
