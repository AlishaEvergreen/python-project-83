from datetime import datetime

import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor


class BaseRepository:
    def __init__(self, database_url):
        self.connection_params = self._parse_database_url(database_url)

    def _parse_database_url(self, database_url):
        return extensions.parse_dsn(database_url)

    def _connect(self):
        return psycopg2.connect(**self.connection_params)

    def _execute_and_fetch_one(self, query, params=None):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchone()

    def _execute_and_fetch_all(self, query, params=None):
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def _execute_and_fetch_id(self, query, params=None, fetch_id=False):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if fetch_id:
                    return cur.fetchone()[0]
            conn.commit()


class UrlsRepository(BaseRepository):
    def get_entities(self):
        return self._execute_and_fetch_all(
            """SELECT * FROM urls ORDER BY id DESC, created_at DESC"""
        )

    def get_url_data_by_id(self, id):
        query = "SELECT * FROM urls WHERE id = %s"
        return self._execute_and_fetch_one(query, (id,))

    def get_url_data_by_name(self, url):
        return self._execute_and_fetch_one(
            "SELECT * FROM urls WHERE name = %s", (url,)
        )

    def save_url(self, url):
        created_at = datetime.now().strftime('%Y-%m-%d')
        return self._execute_and_fetch_id(
            """INSERT INTO urls (name, created_at)
               VALUES (%s, %s) RETURNING id""",
            (url["url"], created_at),
            fetch_id=True
        )


class UrlChecksRepository(BaseRepository):
    def get_urls_with_last_check(self):
        query = """
        SELECT u.id, u.name, c.status_code, c.created_at
        FROM urls AS u
        LEFT JOIN (
            SELECT DISTINCT ON (url_id) url_id, status_code, created_at
            FROM url_checks
            ORDER BY url_id, created_at DESC
        ) AS c ON u.id = c.url_id
        ORDER BY u.id DESC;
        """
        return self._execute_and_fetch_all(query)

    def get_checks_by_id(self, url_id):
        return self._execute_and_fetch_all(
            """SELECT * FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC, created_at DESC""",
            (url_id,)
        )

    def save_url_check(self, id, status_code, h1, title, description):
        created_at = datetime.now().strftime('%Y-%m-%d')
        return self._execute_and_fetch_id(
            """INSERT INTO url_checks (url_id, status_code, h1,
               title, description, created_at)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING id""",
            [id, status_code, h1, title, description, created_at],
            fetch_id=True
        )
