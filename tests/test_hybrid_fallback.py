import pytest
from unittest.mock import MagicMock
from src.fetchers.hybrid import HybridFetcher
from src.models import Post

def test_auto_mode_prefers_fast_http_tier():
    hybrid = HybridFetcher(mode="auto")
    
    mock_http = MagicMock()
    mock_http.fetch_posts.return_value = [
        Post(post_id="http_post_1", page_name="QCGov", text="Fast HTTP success", url="")
    ]
    
    mock_pw = MagicMock()
    
    hybrid.http_fetcher = mock_http
    hybrid.playwright_fetcher = mock_pw
    
    posts = hybrid.fetch_posts("QCGov", limit=3)
    
    assert len(posts) == 1
    assert posts[0].post_id == "http_post_1"
    mock_http.fetch_posts.assert_called_once_with("QCGov", 3)
    mock_pw.fetch_posts.assert_not_called()

def test_auto_mode_falls_back_to_playwright_when_http_yields_zero():
    hybrid = HybridFetcher(mode="auto")
    
    mock_http = MagicMock()
    mock_http.fetch_posts.return_value = []  # HTTP got 0 posts (needs fresh visitor cookies)
    
    mock_pw = MagicMock()
    mock_pw.fetch_posts.return_value = [
        Post(post_id="pw_post_1", page_name="QCGov", text="Playwright fallback", url="")
    ]
    
    hybrid.http_fetcher = mock_http
    hybrid.playwright_fetcher = mock_pw
    
    posts = hybrid.fetch_posts("QCGov", limit=5)
    
    assert len(posts) == 1
    assert posts[0].post_id == "pw_post_1"
    mock_http.fetch_posts.assert_called_once_with("QCGov", 5)
    mock_pw.fetch_posts.assert_called_once_with("QCGov", 5)

def test_forced_http_mode_never_invokes_playwright():
    hybrid = HybridFetcher(mode="http")
    
    mock_http = MagicMock()
    mock_http.fetch_posts.return_value = []
    
    mock_pw = MagicMock()
    
    hybrid.http_fetcher = mock_http
    hybrid.playwright_fetcher = mock_pw
    
    posts = hybrid.fetch_posts("cnn", limit=5)
    
    assert posts == []
    mock_http.fetch_posts.assert_called_once_with("cnn", 5)
    mock_pw.fetch_posts.assert_not_called()

def test_forced_playwright_mode_bypasses_http_tier():
    hybrid = HybridFetcher(mode="playwright")
    
    mock_http = MagicMock()
    mock_pw = MagicMock()
    mock_pw.fetch_posts.return_value = [
        Post(post_id="pw_direct", page_name="NASA", text="Space telescope photo", url="")
    ]
    
    hybrid.http_fetcher = mock_http
    hybrid.playwright_fetcher = mock_pw
    
    posts = hybrid.fetch_posts("NASA", limit=2)
    
    assert len(posts) == 1
    assert posts[0].post_id == "pw_direct"
    mock_http.fetch_posts.assert_not_called()
    mock_pw.fetch_posts.assert_called_once_with("NASA", 2)
