"""
Tests for dataclass definitions: Comment, Thread, PainPoint, AnalysisResult.

Covers:
- Default values (__post_init__)
- Field types
- Edge cases (None replies, empty lists)
"""

import pytest
from reddit_fetcher import Comment, Thread
from ai_analyzer import PainPoint, AnalysisResult


# ── Comment ──────────────────────────────────────────────────────────────────


class TestComment:
    def test_defaults(self):
        c = Comment(
            id="c1", author="u1", body="hello", score=1,
            created_utc=0.0, parent_id="t3_x", gilded=0,
        )
        assert c.depth == 0
        assert c.replies == []

    def test_replies_none_becomes_empty_list(self):
        c = Comment(
            id="c1", author="u1", body="hello", score=1,
            created_utc=0.0, parent_id="t3_x", gilded=0,
            replies=None,
        )
        assert c.replies == []

    def test_explicit_replies(self):
        child = Comment(
            id="c2", author="u2", body="reply", score=0,
            created_utc=0.0, parent_id="t1_c1", gilded=0, depth=1,
        )
        parent = Comment(
            id="c1", author="u1", body="parent", score=1,
            created_utc=0.0, parent_id="t3_x", gilded=0, replies=[child],
        )
        assert len(parent.replies) == 1
        assert parent.replies[0].id == "c2"


# ── Thread ───────────────────────────────────────────────────────────────────


class TestThread:
    def test_defaults(self):
        t = Thread(
            id="t1", title="T", author="a", selftext="",
            score=0, num_comments=0, created_utc=0.0,
            url="", subreddit="", upvote_ratio=0.0,
        )
        assert t.comments == []

    def test_comments_none_becomes_empty_list(self):
        t = Thread(
            id="t1", title="T", author="a", selftext="",
            score=0, num_comments=0, created_utc=0.0,
            url="", subreddit="", upvote_ratio=0.0,
            comments=None,
        )
        assert t.comments == []


# ── PainPoint ────────────────────────────────────────────────────────────────


class TestPainPoint:
    def test_all_fields(self):
        pp = PainPoint(
            description="Problem",
            severity="high",
            frequency_mentioned=3,
            example_comments=["ex1", "ex2"],
            purchase_intent="medium",
            category="Tech",
        )
        assert pp.description == "Problem"
        assert pp.severity == "high"
        assert pp.frequency_mentioned == 3
        assert len(pp.example_comments) == 2
        assert pp.purchase_intent == "medium"
        assert pp.category == "Tech"


# ── AnalysisResult ───────────────────────────────────────────────────────────


class TestAnalysisResult:
    def test_defaults(self):
        r = AnalysisResult(
            thread_id="t1", thread_title="T", total_comments=0,
            pain_points=[], key_insights=[], market_opportunities=[],
            sentiment_summary="",
        )
        assert r.analyzed_comments == 0

    def test_analyzed_vs_total(self):
        r = AnalysisResult(
            thread_id="t1", thread_title="T", total_comments=500,
            pain_points=[], key_insights=[], market_opportunities=[],
            sentiment_summary="", analyzed_comments=100,
        )
        assert r.total_comments == 500
        assert r.analyzed_comments == 100
        assert r.analyzed_comments < r.total_comments
