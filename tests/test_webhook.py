import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import httpx

from src.models import Post
from src.storage.db import PostDatabase
from src.scheduler.runner import MonitorRunner

class TestWebhookDispatch(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        self.db = PostDatabase(str(db_path))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_webhook_successful_delivery(self):
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_posts.return_value = [
            Post(
                post_id="post_wh_1",
                page_name="TechPage",
                text="New product launch announcement.",
                url="https://facebook.com/tech/1",
                images=["https://scontent.fbcdn.net/img1.jpg"]
            )
        ]

        runner = MonitorRunner(
            pages=["TechPage"],
            db=self.db,
            fetcher=mock_fetcher,
            webhook_url="https://api.example.com/webhook"
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
            payload = call_kwargs["json"]
            self.assertEqual(payload["event"], "post.new")
            self.assertEqual(payload["page"], "TechPage")
            self.assertEqual(payload["post"]["post_id"], "post_wh_1")
            self.assertEqual(payload["post"]["images"], ["https://scontent.fbcdn.net/img1.jpg"])

    def test_webhook_http_error_does_not_crash_runner(self):
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_posts.return_value = [
            Post(post_id="post_wh_err", page_name="TechPage", text="Test post", url="")
        ]

        runner = MonitorRunner(
            pages=["TechPage"],
            db=self.db,
            fetcher=mock_fetcher,
            webhook_url="https://api.example.com/webhook"
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("500 Internal Error", request=None, response=mock_resp)
            mock_client.post.return_value = mock_resp

            # Polling should succeed without throwing unhandled exception
            summary = runner.poll_once()
            self.assertEqual(summary["new_posts_found"], 1)

    def test_webhook_network_timeout_handled_gracefully(self):
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_posts.return_value = [
            Post(post_id="post_wh_timeout", page_name="TechPage", text="Test post", url="")
        ]

        runner = MonitorRunner(
            pages=["TechPage"],
            db=self.db,
            fetcher=mock_fetcher,
            webhook_url="https://api.example.com/webhook"
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__.return_value = mock_client
            mock_client.post.side_effect = httpx.ConnectTimeout("Connection timed out")

            summary = runner.poll_once()
            self.assertEqual(summary["new_posts_found"], 1)

    def test_no_webhook_configured_skips_post_request(self):
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_posts.return_value = [
            Post(post_id="post_no_wh", page_name="TechPage", text="No webhook", url="")
        ]

        runner = MonitorRunner(
            pages=["TechPage"],
            db=self.db,
            fetcher=mock_fetcher,
            webhook_url=None
        )

        with patch("httpx.Client") as mock_client_cls:
            summary = runner.poll_once()
            self.assertEqual(summary["new_posts_found"], 1)
            mock_client_cls.assert_not_called()

if __name__ == "__main__":
    unittest.main()
