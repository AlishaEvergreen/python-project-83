import psycopg2
from datetime import datetime
# from psycopg2.extras import NamedTupleCursor


def get_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


class UrlsRepository:
    def __init__(self, conn):
        self.conn = conn

    def save(self, url):
        date = datetime.now().strftime('%Y-%m-%d')
        url['created_at'] = date
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO urls (name, created_at) VALUES
                (%s, %s) RETURNING id""",
                (url['url'], url['created_at'])
            )
            id = cur.fetchone()[0]
            url['id'] = id
        self.conn.commit()

    def get_url_by_name(self, url):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
            return cur.fetchone()
