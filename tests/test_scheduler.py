import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.models import Post
from src.storage.db import PostDatabase
from src.scheduler.runner import MonitorRunner

class TestMonitorRunner(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        self.db = PostDatabase(str(db_path))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_webhook_dispatch_on_new_post(self):
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_posts.return_value = [
            Post(
                post_id="test_post_webhook_1",
                page_name="TestLGU",
                text="Normal advisory post without suspension.",
                url="https://facebook.com/test/1",
            )
        ]

        runner = MonitorRunner(
            pages=["TestLGU"],
            db=self.db,
            fetcher=mock_fetcher,
            webhook_url="https://webhook.site/test-hook"
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_client.post.return_value = mock_resp

            summary = runner.poll_once()

            self.assertEqual(summary["new_posts_found"], 1)
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args[1]
            self.assertEqual(call_kwargs["json"]["event"], "post.new")
            self.assertEqual(call_kwargs["json"]["page"], "TestLGU")
            self.assertEqual(call_kwargs["json"]["post"]["post_id"], "test_post_webhook_1")

if __name__ == "__main__":
    unittest.main()
