import tempfile
from pathlib import Path
from src.models import Post
from src.storage.db import PostDatabase

def test_db_save_and_deduplication():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = PostDatabase(str(db_path))

        post1 = Post(
            post_id="post_101",
            page_name="QCGov",
            text="Announcement 1",
            url="https://facebook.com/QCGov/posts/101",
            images=["https://scontent.fmnl...jpg"],
            raw_metadata={"source": "http_relay_json"}
        )

        # First insert succeeds
        assert db.save_post(post1) is True
        assert db.exists("post_101") is True

        # Second insert is duplicate, returns False
        assert db.save_post(post1) is False

        # Query latest
        posts = db.get_latest_posts("QCGov")
        assert len(posts) == 1
        assert posts[0].post_id == "post_101"
        assert posts[0].text == "Announcement 1"
        assert posts[0].images == ["https://scontent.fmnl...jpg"]
        assert posts[0].raw_metadata == {"source": "http_relay_json"}

def test_db_query_multiple_pages():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = PostDatabase(str(db_path))

        p_qc = Post(post_id="p1", page_name="QCGov", text="QC update", url="")
        p_manila = Post(post_id="p2", page_name="ManilaPIO", text="Manila update", url="")

        db.save_post(p_qc)
        db.save_post(p_manila)

        qc_posts = db.get_latest_posts("QCGov")
        assert len(qc_posts) == 1
        assert qc_posts[0].post_id == "p1"

        manila_posts = db.get_latest_posts("ManilaPIO")
        assert len(manila_posts) == 1
        assert manila_posts[0].post_id == "p2"

        all_posts = db.get_latest_posts(limit=10)
        assert len(all_posts) == 2
