import json
import os
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import main
from src.models import Post
from src.storage.db import PostDatabase

def test_cli_comma_separated_pages(monkeypatch):
    test_args = ["main.py", "--page", "QCGov,ManilaPIO,cnn", "--limit", "2"]
    monkeypatch.setattr(sys, "argv", test_args)

    with patch("main.MonitorRunner") as mock_runner_cls, \
         patch("main.HybridFetcher") as mock_fetcher_cls, \
         patch("main.PostDatabase"):
        
        mock_runner = MagicMock()
        mock_runner.poll_once.return_value = {
            "polled_pages": 3,
            "new_posts_found": 0,
            "duplicates_skipped": 0,
            "details": []
        }
        mock_runner_cls.return_value = mock_runner

        main.main()

        mock_runner_cls.assert_called_once()
        call_kwargs = mock_runner_cls.call_args[1]
        assert call_kwargs["pages"] == ["QCGov", "ManilaPIO", "cnn"]

def test_cli_environment_variables_used_as_defaults(monkeypatch):
    monkeypatch.setenv("SPECTER_PAGE", "CustomLGU")
    monkeypatch.setenv("SPECTER_WEBHOOK_URL", "https://docker-webhook.internal/feed")
    monkeypatch.setenv("SPECTER_INTERVAL", "600")

    monkeypatch.setattr(sys, "argv", ["main.py"])

    with patch("main.MonitorRunner") as mock_runner_cls, \
         patch("main.HybridFetcher"), \
         patch("main.PostDatabase"):

        mock_runner = MagicMock()
        mock_runner.poll_once.return_value = {
            "polled_pages": 1,
            "new_posts_found": 0,
            "duplicates_skipped": 0,
            "details": []
        }
        mock_runner_cls.return_value = mock_runner

        main.main()

        call_kwargs = mock_runner_cls.call_args[1]
        assert call_kwargs["pages"] == ["CustomLGU"]
        assert call_kwargs["webhook_url"] == "https://docker-webhook.internal/feed"

def test_cli_json_output_mode(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = PostDatabase(str(db_path))
        p = Post(
            post_id="post_cli_json",
            page_name="TechDaily",
            text="Breaking news update.",
            url="https://facebook.com/tech/json",
            images=["https://scontent.fbcdn.net/p.jpg"]
        )
        db.save_post(p)

        monkeypatch.setattr(sys, "argv", ["main.py", "--page", "TechDaily", "--limit", "1", "--json"])

        captured_stdout = StringIO()
        with patch("main.PostDatabase", return_value=db), \
             patch("main.MonitorRunner") as mock_runner_cls, \
             patch("sys.stdout", captured_stdout):

            mock_runner = MagicMock()
            mock_runner.poll_once.return_value = {
                "polled_pages": 1,
                "new_posts_found": 0,
                "duplicates_skipped": 1,
                "details": []
            }
            mock_runner_cls.return_value = mock_runner

            main.main()

            output = captured_stdout.getvalue()
            parsed = json.loads(output)
            assert isinstance(parsed, list)
            assert len(parsed) == 1
            assert parsed[0]["post_id"] == "post_cli_json"
            assert parsed[0]["page_name"] == "TechDaily"
            assert parsed[0]["images"] == ["https://scontent.fbcdn.net/p.jpg"]
