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
            is_suspension=False
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

def test_db_suspension_query():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = PostDatabase(str(db_path))

        p_normal = Post(post_id="p1", page_name="QCGov", text="Normal", url="", is_suspension=False)
        p_susp = Post(post_id="p2", page_name="QCGov", text="Walang pasok", url="", is_suspension=True, suspension_details={"confidence": 0.95})

        db.save_post(p_normal)
        db.save_post(p_susp)

        suspensions = db.get_suspension_posts()
        assert len(suspensions) == 1
        assert suspensions[0].post_id == "p2"
        assert suspensions[0].suspension_details["confidence"] == 0.95
