from datetime import date

import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    def __init__(self, database_url):
        self.connection_params = extensions.parse_dsn(database_url)
        self.conn = None

    def __enter__(self):
        if self.conn is None:
            self.conn = psycopg2.connect(**self.connection_params)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()


class CRUDClient:
    def __init__(self, conn):
        self.conn = conn

    def execute(
        self, query, params=None, fetch_one=False,
        fetch_all=False, fetch_id=False, commit=False,
    ):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())

            result = None
            if fetch_one:
                result = cur.fetchone()
            elif fetch_all:
                result = cur.fetchall()
            elif fetch_id:
                result = cur.fetchone()["id"]

            if commit:
                self.conn.commit()

            return result


class UrlsRepository:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_entities(self):
        with DatabaseConnection(self.database_url) as conn:
            return CRUDClient(conn).execute(
                """
                SELECT * FROM urls
                ORDER BY id DESC, created_at DESC
                """,
                fetch_all=True
            )

    def get_url_data_by_id(self, id):
        with DatabaseConnection(self.database_url) as conn:
            return CRUDClient(conn).execute(
                "SELECT * FROM urls WHERE id = %s",
                (id,),
                fetch_one=True
            )

    def get_url_data_by_name(self, url):
        with DatabaseConnection(self.database_url) as conn:
            return CRUDClient(conn).execute(
                "SELECT * FROM urls WHERE name = %s",
                (url,),
                fetch_one=True
            )

    def save_url(self, url):
        created_at = date.today()
        with DatabaseConnection(self.database_url) as conn:
            return CRUDClient(conn).execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id
                """,
                (url["url"], created_at),
                fetch_id=True,
                commit=True,
            )


class UrlChecksRepository:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_urls_with_last_check(self):
        query_urls = "SELECT id, name FROM urls ORDER BY id DESC"
        query_checks = """
        SELECT DISTINCT ON (url_id) url_id, status_code, created_at
        FROM url_checks
        ORDER BY url_id, created_at DESC
        """

        with DatabaseConnection(self.database_url) as conn:
            crud = CRUDClient(conn)
            urls = crud.execute(query_urls, fetch_all=True)
            checks = crud.execute(query_checks, fetch_all=True)

        checks_dict = {check["url_id"]: check for check in checks}
        for url in urls:
            check = checks_dict.get(url["id"])
            url["status_code"] = check["status_code"] if check else None
            url["created_at"] = check["created_at"] if check else None
        return urls

    def get_checks_by_id(self, url_id):
        with DatabaseConnection(self.database_url) as conn:
            return CRUDClient(conn).execute(
                """
                SELECT * FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC, created_at DESC
                """,
                (url_id,), fetch_all=True
            )

    def save_url_check(self, id, status_code, h1, title, description):
        created_at = date.today()
        with DatabaseConnection(self.database_url) as conn:
            return CRUDClient(conn).execute(
                """
                INSERT INTO url_checks (
                    url_id, status_code, h1, title, description, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                [id, status_code, h1, title, description, created_at],
                fetch_id=True,
                commit=True,
            )
