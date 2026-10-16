import pytest
from src.fetchers.http_fetcher import HttpFetcher
from src.fetchers.playwright_fetcher import PlaywrightFetcher
from src.fetchers.hybrid import HybridFetcher
from src.models import Post

def test_http_fetcher_parse_relay_html():
    fetcher = HttpFetcher()
    mock_html = """
    <html>
      <head></head>
      <body>
        <script type="application/json">
          {"require":[["RelayPrefetchedStreamCache","set",[],[{"data":{"node":{"message":{"text":"Important public advisory from Quezon City Government for all residents."}}}}]]]}
        </script>
      </body>
    </html>
    """
    posts = fetcher._parse_relay_html(mock_html, "QCGov", limit=5)
    assert len(posts) == 1
    assert "Important public advisory" in posts[0].text
    assert posts[0].page_name == "QCGov"

def test_hybrid_fetcher_coordination(monkeypatch):
    class MockHttpFetcher:
        def fetch_posts(self, page, limit):
            # Simulate HTTP failure / empty
            return []

    class MockPlaywrightFetcher:
        def fetch_posts(self, page, limit):
            # Simulate Playwright fallback success
            return [Post(post_id="pw_1", page_name=page, text="Fallback post", url="")]

    hybrid = HybridFetcher(mode="auto")
    monkeypatch.setattr(hybrid, "http_fetcher", MockHttpFetcher())
    monkeypatch.setattr(hybrid, "playwright_fetcher", MockPlaywrightFetcher())

    posts = hybrid.fetch_posts("QCGov", limit=1)
    assert len(posts) == 1
    assert posts[0].post_id == "pw_1"
    assert posts[0].text == "Fallback post"
