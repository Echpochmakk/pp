import os
import psycopg2
from psycopg2 import sql
from loguru import logger

class Database:
    def __init__(self):
        self.conn = self._connect()
        self._init_db()

    def _connect(self):
        try:
            return psycopg2.connect(
                host="postgres",
                database="bot",
                user=os.getenv('BOT_DATASOURCE_USERNAME'),
                password=os.getenv('BOT_DATASOURCE_PASSWORD')
            )
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _init_db(self):
        try:
            with self.conn.cursor() as cur:
                # Create tables if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS links (
                        id SERIAL PRIMARY KEY,
                        chat_id BIGINT NOT NULL,
                        url TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS updates (
                        id SERIAL PRIMARY KEY,
                        link_id INTEGER REFERENCES links(id),
                        update TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                self.conn.commit()
        except Exception as e:
            logger.error(f"Database init error: {e}")
            self.conn.rollback()

    def add_link(self, chat_id, url):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO links (chat_id, url) VALUES (%s, %s) RETURNING id",
                    (chat_id, url)  # Обратите внимание на запятую и скобки
                )
                self.conn.commit()
                return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Error adding link: {e}")
            self.conn.rollback()
            raise
    def get_links(self, chat_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT url FROM links WHERE chat_id = %s",
                    (chat_id,))
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error getting links: {e}")
            raise

    def get_last_updates(self, chat_id, limit=5):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT l.url, u.update 
                    FROM updates u
                    JOIN links l ON u.link_id = l.id
                    WHERE l.chat_id = %s
                    ORDER BY u.created_at DESC
                    LIMIT %s
                """, (chat_id, limit))
                return [{'url': row[0], 'update': row[1]} for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            raise

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()