"""
Tests for new reddit_fetcher.py methods and mocked network calls.

Covers:
- _parse_post_listing (new)
- _fetch_listing (new, mocked HTTP)
- fetch_subreddit_top / fetch_subreddit_new (new)
- fetch_thread (mocked HTTP)
- save_to_json (file I/O)
- Network error handling
"""

import json
import pytest
from unittest.mock import patch, MagicMock

import requests

from reddit_fetcher import RedditFetcher, Comment, Thread


# ── _parse_post_listing ──────────────────────────────────────────────────────


class TestParsePostListing:
    """Tests for RedditFetcher._parse_post_listing"""

    def setup_method(self):
        self.fetcher = RedditFetcher()

    def test_basic_parsing(self, mock_listing_response):
        posts = self.fetcher._parse_post_listing(mock_listing_response)
        assert len(posts) == 3
        assert posts[0]["id"] == "post1"
        assert posts[0]["title"] == "First Post Title"
        assert posts[0]["score"] == 150

    def test_subreddit_field_present(self, mock_listing_response):
        posts = self.fetcher._parse_post_listing(mock_listing_response)
        for post in posts:
            assert "subreddit" in post
        assert posts[0]["subreddit"] == "test"

    def test_permalink_is_full_url(self, mock_listing_response):
        posts = self.fetcher._parse_post_listing(mock_listing_response)
        for post in posts:
            assert post["permalink"].startswith("https://www.reddit.com/r/")

    def test_all_required_fields(self, mock_listing_response):
        posts = self.fetcher._parse_post_listing(mock_listing_response)
        required = [
            "id", "title", "author", "score", "num_comments",
            "url", "permalink", "created_utc", "selftext", "subreddit",
        ]
        for post in posts:
            for field in required:
                assert field in post, f"Missing field: {field}"

    def test_empty_response(self):
        assert self.fetcher._parse_post_listing({}) == []

    def test_empty_children(self):
        assert self.fetcher._parse_post_listing({"data": {"children": []}}) == []

    def test_missing_data_key(self):
        assert self.fetcher._parse_post_listing({"other": "value"}) == []

    def test_missing_optional_fields_use_defaults(self):
        """Posts with missing fields should use .get() defaults."""
        data = {
            "data": {
                "children": [
                    {"kind": "t3", "data": {"id": "x", "permalink": "/r/x/comments/x/"}}
                ]
            }
        }
        posts = self.fetcher._parse_post_listing(data)
        assert len(posts) == 1
        assert posts[0]["selftext"] == ""
        assert posts[0]["subreddit"] == ""


# ── _fetch_listing (mocked HTTP) ─────────────────────────────────────────────


class TestFetchListing:
    """Tests for RedditFetcher._fetch_listing with mocked HTTP"""

    def setup_method(self):
        self.fetcher = RedditFetcher()
        self.fetcher.rate_limit_delay = 0

    def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"children": []}}
        mock_response.raise_for_status.return_value = None
        with patch.object(self.fetcher.session, "get", return_value=mock_response):
            result = self.fetcher._fetch_listing("https://old.reddit.com/r/test/hot.json")
        assert result == []

    def test_connection_error(self):
        with patch.object(
            self.fetcher.session, "get",
            side_effect=requests.exceptions.ConnectionError("refused"),
        ):
            assert self.fetcher._fetch_listing("https://example.com") == []

    def test_timeout_error(self):
        with patch.object(
            self.fetcher.session, "get",
            side_effect=requests.exceptions.Timeout("timeout"),
        ):
            assert self.fetcher._fetch_listing("https://example.com") == []

    def test_http_error(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        with patch.object(self.fetcher.session, "get", return_value=mock_response):
            assert self.fetcher._fetch_listing("https://example.com") == []

    def test_json_decode_error(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("bad", "", 0)
        with patch.object(self.fetcher.session, "get", return_value=mock_response):
            assert self.fetcher._fetch_listing("https://example.com") == []


# ── fetch_subreddit_hot / top / new URL construction ─────────────────────────


class TestFetchSubredditVariants:
    """Verify correct URL construction for hot/top/new endpoints"""

    def setup_method(self):
        self.fetcher = RedditFetcher()
        self.fetcher.rate_limit_delay = 0

    @patch.object(RedditFetcher, "_fetch_listing", return_value=[])
    def test_hot_url(self, mock_fetch):
        self.fetcher.fetch_subreddit_hot("Entrepreneur", limit=10)
        mock_fetch.assert_called_once_with(
            "https://old.reddit.com/r/Entrepreneur/hot.json?limit=10"
        )

    @patch.object(RedditFetcher, "_fetch_listing", return_value=[])
    def test_top_url_default_week(self, mock_fetch):
        self.fetcher.fetch_subreddit_top("SaaS")
        mock_fetch.assert_called_once_with(
            "https://old.reddit.com/r/SaaS/top.json?t=week&limit=25"
        )

    @patch.object(RedditFetcher, "_fetch_listing", return_value=[])
    def test_top_url_custom_time_and_limit(self, mock_fetch):
        self.fetcher.fetch_subreddit_top("SaaS", time_filter="month", limit=50)
        mock_fetch.assert_called_once_with(
            "https://old.reddit.com/r/SaaS/top.json?t=month&limit=50"
        )

    @patch.object(RedditFetcher, "_fetch_listing", return_value=[])
    def test_new_url(self, mock_fetch):
        self.fetcher.fetch_subreddit_new("startups", limit=15)
        mock_fetch.assert_called_once_with(
            "https://old.reddit.com/r/startups/new.json?limit=15"
        )

    @patch.object(RedditFetcher, "_fetch_listing", return_value=[])
    def test_limit_capped_at_100(self, mock_fetch):
        self.fetcher.fetch_subreddit_hot("test", limit=200)
        url = mock_fetch.call_args[0][0]
        assert "limit=100" in url

    @patch.object(RedditFetcher, "_fetch_listing", return_value=[])
    def test_top_all_time_filters(self, mock_fetch):
        for tf in ("hour", "day", "week", "month", "year", "all"):
            self.fetcher.fetch_subreddit_top("t", time_filter=tf)
            url = mock_fetch.call_args[0][0]
            assert f"t={tf}" in url


# ── fetch_thread (mocked HTTP) ───────────────────────────────────────────────


class TestFetchThread:
    """Tests for RedditFetcher.fetch_thread with mocked HTTP"""

    def setup_method(self):
        self.fetcher = RedditFetcher()
        self.fetcher.rate_limit_delay = 0

    def _mock_thread_json(self):
        return [
            {
                "data": {
                    "children": [
                        {
                            "data": {
                                "id": "t1",
                                "title": "Test Thread",
                                "author": "author1",
                                "selftext": "body",
                                "score": 100,
                                "num_comments": 5,
                                "created_utc": 1700000000.0,
                                "url": "https://reddit.com/...",
                                "subreddit": "test",
                                "upvote_ratio": 0.95,
                            }
                        }
                    ]
                }
            },
            {"data": {"children": []}},
        ]

    def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.json.return_value = self._mock_thread_json()
        mock_response.raise_for_status.return_value = None
        with patch.object(self.fetcher.session, "get", return_value=mock_response):
            thread = self.fetcher.fetch_thread(
                "https://www.reddit.com/r/test/comments/t1/"
            )
        assert thread is not None
        assert thread.id == "t1"
        assert thread.title == "Test Thread"
        assert thread.subreddit == "test"

    def test_network_error_returns_none(self):
        with patch.object(
            self.fetcher.session, "get",
            side_effect=requests.exceptions.ConnectionError,
        ):
            assert self.fetcher.fetch_thread("https://reddit.com/r/t/comments/x/") is None

    def test_json_error_returns_none(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("bad", "", 0)
        with patch.object(self.fetcher.session, "get", return_value=mock_response):
            assert self.fetcher.fetch_thread("https://reddit.com/r/t/comments/x/") is None


# ── save_to_json (file I/O) ──────────────────────────────────────────────────


class TestSaveToJson:
    """Tests for RedditFetcher.save_to_json"""

    def test_save_and_reload(self, tmp_path):
        fetcher = RedditFetcher()
        child = Comment(
            id="c2", author="u2", body="reply", score=1,
            created_utc=1001.0, parent_id="t1_c1", gilded=0, depth=1,
        )
        parent = Comment(
            id="c1", author="u1", body="hello", score=5,
            created_utc=1000.0, parent_id="t3_t1", gilded=0, depth=0,
            replies=[child],
        )
        thread = Thread(
            id="t1", title="Test", author="a", selftext="body",
            score=10, num_comments=2, created_utc=1000.0,
            url="http://example.com", subreddit="test", upvote_ratio=0.9,
            comments=[parent],
        )
        fp = str(tmp_path / "thread.json")
        fetcher.save_to_json(thread, fp)

        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["id"] == "t1"
        assert len(data["comments"]) == 1
        assert data["comments"][0]["body"] == "hello"
        assert len(data["comments"][0]["replies"]) == 1
        assert data["comments"][0]["replies"][0]["id"] == "c2"

    def test_unicode_content(self, tmp_path):
        fetcher = RedditFetcher()
        thread = Thread(
            id="u1", title="日本語タイトル", author="user",
            selftext="本文テスト", score=1, num_comments=0,
            created_utc=0.0, url="", subreddit="jp",
            upvote_ratio=0.8, comments=[],
        )
        fp = str(tmp_path / "unicode.json")
        fetcher.save_to_json(thread, fp)

        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["title"] == "日本語タイトル"
        assert data["selftext"] == "本文テスト"
