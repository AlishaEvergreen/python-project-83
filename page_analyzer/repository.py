from datetime import date
from typing import Literal

import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    """Manages database connection lifecycle (open, close)."""
    def __init__(self, database_url):
        self.connection_params = extensions.parse_dsn(database_url)
        self.conn = None

    def __enter__(self):
        if not self.conn:
            self.conn = psycopg2.connect(**self.connection_params)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()


class CRUDClient:
    """Executes SQL queries and fetches results."""
    def __init__(self, conn):
        self.conn = conn

    def execute(
        self, query, params=None,
        output_mode: Literal[
            "fetch_one", "fetch_all", "fetch_id"
        ] = "fetch_one",
        commit=False,
    ):
        """
        Executes a SQL query and returns the result.

        Args:
            query (str): SQL query to execute.
            params (tuple, optional): Query parameters.
            output_mode (Literal["fetch_one", "fetch_all", "fetch_id"]):
                Determines how to fetch results.
                - "fetch_one": Return a single row.
                - "fetch_all": Return all rows.
                - "fetch_id": Return the ID of the inserted row.
            commit (bool): Commit the transaction if True.

        Returns:
            Result of the query:
                - dict (if fetch_one)
                - list of dicts (if fetch_all)
                - int (if fetch_id)
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())

            result = None
            if output_mode == "fetch_one":
                result = cur.fetchone()
            elif output_mode == "fetch_all":
                result = cur.fetchall()
            elif output_mode == "fetch_id":
                result = cur.fetchone()["id"]

            if commit:
                self.conn.commit()

            return result


class UrlsRepository:
    """Repository for managing URLs in the database."""
    def get_url_data_by_id(self, conn, id):
        """Fetches URL data by its ID."""
        return CRUDClient(conn).execute(
            "SELECT * FROM urls WHERE id = %s",
            (id,),
        )

    def get_url_data_by_name(self, conn, url):
        """Fetches URL data by its name."""
        return CRUDClient(conn).execute(
            "SELECT * FROM urls WHERE name = %s",
            (url,),
        )

    def save_url(self, conn, url):
        """Saves a new URL and return its ID."""
        created_at = date.today()
        return CRUDClient(conn).execute(
            " INSERT INTO urls (name) VALUES (%s) RETURNING id",
            (url["url"], created_at),
            output_mode="fetch_id",
            commit=True,
        )


class UrlChecksRepository:
    """Repository for managing URL checks in the database."""
    def get_urls_with_last_check(self, conn):
        """Fetches URLs with their latest check data."""
        query_urls = "SELECT id, name FROM urls ORDER BY id DESC"
        query_checks = """
        SELECT DISTINCT ON (url_id) url_id, status_code, created_at
        FROM url_checks
        ORDER BY url_id, created_at DESC
        """

        crud = CRUDClient(conn)
        urls = crud.execute(query_urls, output_mode="fetch_all")
        checks = crud.execute(query_checks, output_mode="fetch_all")

        checks_dict = {check["url_id"]: check for check in checks}
        for url in urls:
            check = checks_dict.get(url["id"])
            url["status_code"] = check["status_code"] if check else None
            url["created_at"] = check["created_at"] if check else None
        return urls

    def get_checks_by_id(self, conn, url_id):
        """Fetches all checks for a URL by its ID."""
        return CRUDClient(conn).execute(
            """
            SELECT * FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC, created_at DESC
            """,
            (url_id,),
            output_mode="fetch_all",
        )

    def save_url_check(self, conn, id, status_code, h1, title, description):
        """Saves a new URL check and return its ID."""
        return CRUDClient(conn).execute(
            """
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description,
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (id, status_code, h1, title, description),
            output_mode="fetch_id",
            commit=True,
        )
