"""
Tests for RedditFetcher._parse_thread — Thread object construction from raw JSON.

Covers:
- Basic field extraction
- Comments parsing from second element
- Missing optional fields use defaults
- Thread with no comments section
- Deeply nested comment tree
- 'more' kind comments are skipped
- Non-t1 kinds are skipped
"""

import pytest
from reddit_fetcher import RedditFetcher, Thread, Comment


def _make_raw_thread(**overrides):
    """Build minimal raw Reddit JSON for _parse_thread."""
    post = {
        "id": "abc123",
        "title": "Test Thread",
        "author": "testuser",
        "selftext": "Body text",
        "score": 42,
        "num_comments": 5,
        "created_utc": 1700000000.0,
        "url": "https://www.reddit.com/r/test/comments/abc123/test/",
        "subreddit": "test",
        "upvote_ratio": 0.95,
    }
    post.update(overrides)
    return [
        {"data": {"children": [{"data": post}]}},
        {"data": {"children": []}},
    ]


def _make_raw_comment(comment_id="c1", body="Test comment", score=10,
                       replies=None, depth=0, kind="t1"):
    """Build a raw comment dict as returned by Reddit API."""
    c = {
        "kind": kind,
        "data": {
            "id": comment_id,
            "author": "commenter",
            "body": body,
            "score": score,
            "created_utc": 1700001000.0,
            "parent_id": "t3_abc123",
            "gilded": 0,
        },
    }
    if replies is not None:
        c["data"]["replies"] = {"data": {"children": replies}}
    return c


class TestParseThreadBasic:
    def test_fields_extracted(self):
        fetcher = RedditFetcher()
        raw = _make_raw_thread()
        thread = fetcher._parse_thread(raw)
        assert isinstance(thread, Thread)
        assert thread.id == "abc123"
        assert thread.title == "Test Thread"
        assert thread.author == "testuser"
        assert thread.selftext == "Body text"
        assert thread.score == 42
        assert thread.num_comments == 5
        assert thread.subreddit == "test"
        assert thread.upvote_ratio == 0.95

    def test_empty_comments(self):
        fetcher = RedditFetcher()
        raw = _make_raw_thread()
        thread = fetcher._parse_thread(raw)
        assert thread.comments == []

    def test_defaults_for_missing_fields(self):
        fetcher = RedditFetcher()
        raw = [
            {"data": {"children": [{"data": {}}]}},
            {"data": {"children": []}},
        ]
        thread = fetcher._parse_thread(raw)
        assert thread.id == ""
        assert thread.title == ""
        assert thread.score == 0
        assert thread.upvote_ratio == 0.0


class TestParseThreadComments:
    def test_single_comment(self):
        fetcher = RedditFetcher()
        comment = _make_raw_comment()
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [comment]
        thread = fetcher._parse_thread(raw)
        assert len(thread.comments) == 1
        assert thread.comments[0].id == "c1"
        assert thread.comments[0].body == "Test comment"

    def test_multiple_comments(self):
        fetcher = RedditFetcher()
        c1 = _make_raw_comment(comment_id="c1", body="First")
        c2 = _make_raw_comment(comment_id="c2", body="Second")
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [c1, c2]
        thread = fetcher._parse_thread(raw)
        assert len(thread.comments) == 2

    def test_nested_replies(self):
        fetcher = RedditFetcher()
        child = _make_raw_comment(comment_id="c2", body="Reply")
        parent = _make_raw_comment(comment_id="c1", body="Parent", replies=[child])
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [parent]
        thread = fetcher._parse_thread(raw)
        assert len(thread.comments) == 1
        assert len(thread.comments[0].replies) == 1
        assert thread.comments[0].replies[0].id == "c2"
        assert thread.comments[0].replies[0].depth == 1

    def test_deeply_nested_3_levels(self):
        fetcher = RedditFetcher()
        c3 = _make_raw_comment(comment_id="c3", body="Deep")
        c2 = _make_raw_comment(comment_id="c2", body="Mid", replies=[c3])
        c1 = _make_raw_comment(comment_id="c1", body="Top", replies=[c2])
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [c1]
        thread = fetcher._parse_thread(raw)
        deep = thread.comments[0].replies[0].replies[0]
        assert deep.id == "c3"
        assert deep.depth == 2

    def test_more_kind_skipped(self):
        fetcher = RedditFetcher()
        more = {"kind": "more", "data": {"children": ["x", "y"]}}
        normal = _make_raw_comment(comment_id="c1")
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [more, normal]
        thread = fetcher._parse_thread(raw)
        assert len(thread.comments) == 1
        assert thread.comments[0].id == "c1"

    def test_non_t1_kind_skipped(self):
        fetcher = RedditFetcher()
        wrong_kind = _make_raw_comment(comment_id="c1", kind="t3")
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [wrong_kind]
        thread = fetcher._parse_thread(raw)
        assert len(thread.comments) == 0


class TestParseThreadNoCommentSection:
    def test_single_element_data(self):
        """Thread with only post data (no comments section)."""
        fetcher = RedditFetcher()
        raw = [{"data": {"children": [{"data": {"id": "t1", "title": "T"}}]}}]
        thread = fetcher._parse_thread(raw)
        assert thread.id == "t1"
        assert thread.comments == []


class TestParseThreadMalformedData:
    """Malformed Reddit responses raise ValueError instead of crashing."""

    def test_empty_list(self):
        fetcher = RedditFetcher()
        with pytest.raises(ValueError, match="Unexpected Reddit API response"):
            fetcher._parse_thread([])

    def test_missing_data_key(self):
        fetcher = RedditFetcher()
        with pytest.raises(ValueError, match="Unexpected Reddit API response"):
            fetcher._parse_thread([{"kind": "Listing"}])

    def test_empty_children(self):
        fetcher = RedditFetcher()
        with pytest.raises(ValueError, match="Unexpected Reddit API response"):
            fetcher._parse_thread([{"data": {"children": []}}])

    def test_none_input(self):
        fetcher = RedditFetcher()
        with pytest.raises((ValueError, TypeError)):
            fetcher._parse_thread(None)


class TestParseThreadCommentFields:
    def test_comment_gilded(self):
        fetcher = RedditFetcher()
        c = {
            "kind": "t1",
            "data": {
                "id": "c1", "author": "u", "body": "gilded comment",
                "score": 100, "created_utc": 1700000000.0,
                "parent_id": "t3_x", "gilded": 3,
            },
        }
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [c]
        thread = fetcher._parse_thread(raw)
        assert thread.comments[0].gilded == 3

    def test_comment_replies_as_empty_string(self):
        """Reddit sometimes returns replies as '' (empty string) instead of dict."""
        fetcher = RedditFetcher()
        c = {
            "kind": "t1",
            "data": {
                "id": "c1", "author": "u", "body": "text",
                "score": 1, "created_utc": 1700000000.0,
                "parent_id": "t3_x", "gilded": 0,
                "replies": "",  # Reddit returns empty string
            },
        }
        raw = _make_raw_thread()
        raw[1]["data"]["children"] = [c]
        thread = fetcher._parse_thread(raw)
        # Should handle gracefully — replies stays empty
        assert thread.comments[0].replies == []
