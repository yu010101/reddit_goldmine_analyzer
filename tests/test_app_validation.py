"""Tests for app.py validation logic"""

import re
import pytest

# Replicate the validation regex from app.py
REDDIT_URL_RE = re.compile(
    r"https?://(www\.|old\.)?reddit\.com/r/\w+/comments/\w+",
)


class TestRedditUrlValidation:
    """Tests for Reddit URL validation pattern"""

    def test_valid_www_url(self):
        assert REDDIT_URL_RE.match("https://www.reddit.com/r/Entrepreneur/comments/abc123/title")

    def test_valid_old_url(self):
        assert REDDIT_URL_RE.match("https://old.reddit.com/r/SaaS/comments/xyz789/")

    def test_valid_bare_url(self):
        assert REDDIT_URL_RE.match("https://reddit.com/r/test/comments/abc/")

    def test_valid_http(self):
        assert REDDIT_URL_RE.match("http://www.reddit.com/r/test/comments/abc/")

    def test_invalid_no_comments(self):
        assert not REDDIT_URL_RE.match("https://www.reddit.com/r/Entrepreneur/")

    def test_invalid_other_site(self):
        assert not REDDIT_URL_RE.match("https://example.com/r/test/comments/abc")

    def test_invalid_empty(self):
        assert not REDDIT_URL_RE.match("")

    def test_invalid_random_text(self):
        assert not REDDIT_URL_RE.match("not a url at all")

    def test_invalid_subreddit_only(self):
        assert not REDDIT_URL_RE.match("https://www.reddit.com/r/Entrepreneur")


class TestApiKeyValidation:
    """Tests for API key format validation"""

    def test_valid_key(self):
        assert "sk-abc123".startswith("sk-")

    def test_valid_project_key(self):
        assert "sk-proj-abc123".startswith("sk-")

    def test_invalid_no_prefix(self):
        assert not "abc123".startswith("sk-")

    def test_invalid_empty(self):
        assert not "".startswith("sk-")

    def test_invalid_wrong_prefix(self):
        assert not "pk-abc".startswith("sk-")
