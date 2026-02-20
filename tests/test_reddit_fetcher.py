"""Tests for reddit_fetcher.py"""

import pytest
from reddit_fetcher import RedditFetcher, Comment, Thread


class TestNormalizeUrl:
    """Tests for RedditFetcher._normalize_url"""

    def setup_method(self):
        self.fetcher = RedditFetcher()

    def test_www_reddit_url(self):
        url = "https://www.reddit.com/r/Entrepreneur/comments/abc123/some_title/"
        result = self.fetcher._normalize_url(url)
        assert "old.reddit.com" in result
        assert result.endswith(".json")

    def test_old_reddit_url(self):
        url = "https://old.reddit.com/r/Entrepreneur/comments/abc123/"
        result = self.fetcher._normalize_url(url)
        assert result == "https://old.reddit.com/r/Entrepreneur/comments/abc123.json"

    def test_already_json(self):
        url = "https://old.reddit.com/r/Entrepreneur/comments/abc123.json"
        result = self.fetcher._normalize_url(url)
        assert result == url

    def test_bare_reddit_url(self):
        url = "https://reddit.com/r/SaaS/comments/xyz/"
        result = self.fetcher._normalize_url(url)
        assert "old.reddit.com" in result
        assert result.endswith(".json")
        assert "www" not in result

    def test_trailing_slash_stripped(self):
        url = "https://www.reddit.com/r/test/comments/abc/"
        result = self.fetcher._normalize_url(url)
        assert not result.endswith("/.json")


class TestParseComments:
    """Tests for RedditFetcher._parse_comments"""

    def setup_method(self):
        self.fetcher = RedditFetcher()

    def test_empty_list(self):
        assert self.fetcher._parse_comments([]) == []

    def test_skip_more_kind(self):
        data = [{"kind": "more", "data": {"children": []}}]
        assert self.fetcher._parse_comments(data) == []

    def test_parse_single_comment(self):
        data = [
            {
                "kind": "t1",
                "data": {
                    "id": "c1",
                    "author": "user1",
                    "body": "Hello world",
                    "score": 5,
                    "created_utc": 1000000.0,
                    "parent_id": "t3_abc",
                    "gilded": 0,
                    "replies": "",
                },
            }
        ]
        comments = self.fetcher._parse_comments(data)
        assert len(comments) == 1
        assert comments[0].id == "c1"
        assert comments[0].body == "Hello world"
        assert comments[0].depth == 0

    def test_nested_replies(self):
        data = [
            {
                "kind": "t1",
                "data": {
                    "id": "c1",
                    "author": "user1",
                    "body": "Parent",
                    "score": 3,
                    "created_utc": 1000000.0,
                    "parent_id": "t3_abc",
                    "gilded": 0,
                    "replies": {
                        "data": {
                            "children": [
                                {
                                    "kind": "t1",
                                    "data": {
                                        "id": "c2",
                                        "author": "user2",
                                        "body": "Reply",
                                        "score": 1,
                                        "created_utc": 1000001.0,
                                        "parent_id": "t1_c1",
                                        "gilded": 0,
                                        "replies": "",
                                    },
                                }
                            ]
                        }
                    },
                },
            }
        ]
        comments = self.fetcher._parse_comments(data)
        assert len(comments) == 1
        assert len(comments[0].replies) == 1
        assert comments[0].replies[0].id == "c2"
        assert comments[0].replies[0].depth == 1


class TestGetAllCommentsFlat:
    """Tests for RedditFetcher.get_all_comments_flat"""

    def setup_method(self):
        self.fetcher = RedditFetcher()

    def test_flat_list(self):
        child = Comment(id="c2", author="u2", body="reply", score=1,
                        created_utc=0.0, parent_id="t1_c1", gilded=0, depth=1)
        parent = Comment(id="c1", author="u1", body="parent", score=2,
                         created_utc=0.0, parent_id="t3_x", gilded=0, depth=0,
                         replies=[child])
        thread = Thread(id="t1", title="T", author="a", selftext="",
                        score=1, num_comments=2, created_utc=0.0,
                        url="", subreddit="test", upvote_ratio=0.9,
                        comments=[parent])

        flat = self.fetcher.get_all_comments_flat(thread)
        assert len(flat) == 2
        assert flat[0].id == "c1"
        assert flat[1].id == "c2"
