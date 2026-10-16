import sqlite3
import json
from typing import List, Optional
from pathlib import Path
from ..models import Post

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "posts.db"

class PostDatabase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    post_id TEXT PRIMARY KEY,
                    page_name TEXT NOT NULL,
                    text TEXT,
                    url TEXT,
                    published_at TEXT,
                    scraped_at TEXT NOT NULL,
                    images_json TEXT,
                    video TEXT,
                    metadata_json TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_page_scraped 
                ON posts(page_name, scraped_at DESC)
            """)
            conn.commit()

    def exists(self, post_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM posts WHERE post_id = ?", (post_id,))
            return cursor.fetchone() is not None

    def save_post(self, post: Post) -> bool:
        """
        Inserts post if not exists. Returns True if inserted, False if already existed.
        """
        if self.exists(post.post_id):
            return False

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO posts (
                    post_id, page_name, text, url, published_at, scraped_at,
                    images_json, video, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.post_id,
                post.page_name,
                post.text,
                post.url,
                post.published_at,
                post.scraped_at,
                json.dumps(post.images),
                post.video,
                json.dumps(post.raw_metadata) if post.raw_metadata else None,
            ))
            conn.commit()
            return True

    def get_latest_posts(self, page_name: Optional[str] = None, limit: int = 10) -> List[Post]:
        with self._get_connection() as conn:
            if page_name:
                cursor = conn.execute("""
                    SELECT * FROM posts WHERE page_name = ? 
                    ORDER BY scraped_at DESC LIMIT ?
                """, (page_name, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM posts ORDER BY scraped_at DESC LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()
            posts = []
            for r in rows:
                posts.append(Post(
                    post_id=r["post_id"],
                    page_name=r["page_name"],
                    text=r["text"] or "",
                    url=r["url"] or "",
                    published_at=r["published_at"],
                    scraped_at=r["scraped_at"],
                    images=json.loads(r["images_json"]) if r["images_json"] else [],
                    video=r["video"],
                    raw_metadata=json.loads(r["metadata_json"]) if r["metadata_json"] else {},
                ))
            return posts
