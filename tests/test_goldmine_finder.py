"""
Tests for goldmine_finder.py (previously 0% coverage).

Covers:
- _thread_to_dict conversion
- analyze_single_thread (mocked fetcher + analyzer)
- analyze_subreddit filtering by min_comments
- batch_analyze_urls
- _generate_summary_report content & file I/O
- Edge cases: fetch failures, empty results
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from reddit_fetcher import Thread, Comment
from ai_analyzer import AnalysisResult, PainPoint


def _make_finder(tmp_path):
    """Create GoldmineFinder with mocked fetcher/analyzer (no real API calls)."""
    with patch("goldmine_finder.RedditFetcher"), \
         patch("goldmine_finder.AIAnalyzer"):
        from goldmine_finder import GoldmineFinder
        return GoldmineFinder(output_dir=str(tmp_path))


def _make_thread(**overrides):
    defaults = dict(
        id="t1", title="Title", author="auth", selftext="body",
        score=42, num_comments=3, created_utc=1000.0,
        url="http://test.com", subreddit="test", upvote_ratio=0.95,
        comments=[],
    )
    defaults.update(overrides)
    return Thread(**defaults)


def _make_analysis(**overrides):
    defaults = dict(
        thread_id="t1", thread_title="Title", total_comments=10,
        pain_points=[], key_insights=[], market_opportunities=[],
        sentiment_summary="Neutral", analyzed_comments=10,
    )
    defaults.update(overrides)
    return AnalysisResult(**defaults)


# ── _thread_to_dict ──────────────────────────────────────────────────────────


class TestThreadToDict:
    def test_basic_fields(self, tmp_path):
        finder = _make_finder(tmp_path)
        thread = _make_thread()
        d = finder._thread_to_dict(thread)
        assert d["id"] == "t1"
        assert d["title"] == "Title"
        assert d["score"] == 42
        assert d["comments"] == []

    def test_nested_comments(self, tmp_path):
        finder = _make_finder(tmp_path)
        child = Comment(
            id="c2", author="u2", body="reply", score=1,
            created_utc=1001.0, parent_id="t1_c1", gilded=0, depth=1,
        )
        parent = Comment(
            id="c1", author="u1", body="parent", score=5,
            created_utc=1000.0, parent_id="t3_t1", gilded=1, depth=0,
            replies=[child],
        )
        thread = _make_thread(comments=[parent])
        d = finder._thread_to_dict(thread)

        assert len(d["comments"]) == 1
        assert d["comments"][0]["id"] == "c1"
        assert d["comments"][0]["gilded"] == 1
        assert len(d["comments"][0]["replies"]) == 1
        assert d["comments"][0]["replies"][0]["id"] == "c2"

    def test_all_comment_fields_preserved(self, tmp_path):
        finder = _make_finder(tmp_path)
        c = Comment(
            id="c1", author="u1", body="hello", score=10,
            created_utc=999.0, parent_id="t3_t1", gilded=2, depth=0,
        )
        thread = _make_thread(comments=[c])
        d = finder._thread_to_dict(thread)
        cd = d["comments"][0]
        assert cd["author"] == "u1"
        assert cd["body"] == "hello"
        assert cd["score"] == 10
        assert cd["gilded"] == 2
        assert cd["depth"] == 0


# ── analyze_single_thread ────────────────────────────────────────────────────


class TestAnalyzeSingleThread:
    def _setup_finder(self, tmp_path, thread, analysis):
        finder = _make_finder(tmp_path)
        finder.fetcher.fetch_thread.return_value = thread
        finder.fetcher.save_to_json.return_value = None
        finder.analyzer.analyze_thread.return_value = analysis
        finder.analyzer.save_analysis.return_value = None
        finder.analyzer.generate_report.return_value = "# Report"
        return finder

    def test_success(self, tmp_path):
        thread = _make_thread()
        analysis = _make_analysis()
        finder = self._setup_finder(tmp_path, thread, analysis)

        result = finder.analyze_single_thread("https://reddit.com/r/test/comments/t1/")

        assert result is not None
        assert result["thread"]["id"] == "t1"
        assert result["analysis"] == analysis
        assert result["report_file"].endswith(".md")

    def test_fetch_failure_returns_none(self, tmp_path):
        finder = _make_finder(tmp_path)
        finder.fetcher.fetch_thread.return_value = None
        assert finder.analyze_single_thread("https://reddit.com/r/x/comments/bad/") is None

    def test_saves_report_file(self, tmp_path):
        thread = _make_thread()
        analysis = _make_analysis()
        finder = self._setup_finder(tmp_path, thread, analysis)
        result = finder.analyze_single_thread("https://reddit.com/r/test/comments/t1/")

        # Report file should exist
        assert os.path.exists(result["report_file"])
        with open(result["report_file"], "r") as f:
            assert "Report" in f.read()


# ── analyze_subreddit ─────────────────────────────────────────────────────────


class TestAnalyzeSubreddit:
    def test_filters_by_min_comments(self, tmp_path):
        posts = [
            {"title": "P1", "num_comments": 10, "permalink": "https://reddit.com/r/t/comments/1/"},
            {"title": "P2", "num_comments": 2, "permalink": "https://reddit.com/r/t/comments/2/"},
            {"title": "P3", "num_comments": 5, "permalink": "https://reddit.com/r/t/comments/3/"},
        ]
        finder = _make_finder(tmp_path)
        finder.fetcher.fetch_subreddit_hot.return_value = posts

        with patch.object(finder, "analyze_single_thread", return_value=None) as mock_analyze:
            finder.analyze_subreddit("test", limit=10, min_comments=5)
            assert mock_analyze.call_count == 2  # P1 (10) and P3 (5)

    def test_empty_posts(self, tmp_path):
        finder = _make_finder(tmp_path)
        finder.fetcher.fetch_subreddit_hot.return_value = []
        assert finder.analyze_subreddit("empty") == []

    def test_all_below_threshold(self, tmp_path):
        posts = [
            {"title": "P1", "num_comments": 1, "permalink": "url1"},
            {"title": "P2", "num_comments": 0, "permalink": "url2"},
        ]
        finder = _make_finder(tmp_path)
        finder.fetcher.fetch_subreddit_hot.return_value = posts
        with patch.object(finder, "analyze_single_thread") as mock:
            finder.analyze_subreddit("test", min_comments=5)
            mock.assert_not_called()


# ── batch_analyze_urls ────────────────────────────────────────────────────────


class TestBatchAnalyze:
    def test_processes_all_urls(self, tmp_path):
        finder = _make_finder(tmp_path)
        mock_result = {"thread": {}, "analysis": _make_analysis(), "report_file": "r.md"}

        with patch.object(finder, "analyze_single_thread", return_value=mock_result) as mock_analyze, \
             patch.object(finder, "_generate_summary_report"):
            results = finder.batch_analyze_urls(["url1", "url2", "url3"])
            assert mock_analyze.call_count == 3
            assert len(results) == 3

    def test_skips_failed_urls(self, tmp_path):
        finder = _make_finder(tmp_path)
        # First succeeds, second fails
        mock_result = {"thread": {}, "analysis": _make_analysis(), "report_file": "r.md"}

        with patch.object(finder, "analyze_single_thread", side_effect=[mock_result, None, mock_result]), \
             patch.object(finder, "_generate_summary_report"):
            results = finder.batch_analyze_urls(["url1", "url2", "url3"])
            assert len(results) == 2  # Only 2 succeed

    def test_empty_urls(self, tmp_path):
        finder = _make_finder(tmp_path)
        with patch.object(finder, "_generate_summary_report"):
            assert finder.batch_analyze_urls([]) == []


# ── _generate_summary_report ─────────────────────────────────────────────────


class TestGenerateSummaryReport:
    def test_empty_results_no_file(self, tmp_path):
        finder = _make_finder(tmp_path)
        finder._generate_summary_report("test", [])
        assert not os.path.exists(os.path.join(str(tmp_path), "summary_test.md"))

    def test_report_content(self, tmp_path):
        finder = _make_finder(tmp_path)
        analysis = _make_analysis(
            pain_points=[
                PainPoint("Pain A", "high", 3, ["ex1"], "high", "Tech"),
                PainPoint("Pain B", "low", 1, [], "low", "Marketing"),
            ],
            market_opportunities=["Opportunity X"],
        )
        results = [{"thread": {}, "analysis": analysis, "report_file": "r.md"}]
        finder._generate_summary_report("test_sub", results)

        fp = os.path.join(str(tmp_path), "summary_test_sub.md")
        assert os.path.exists(fp)

        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()

        assert "test_sub" in content
        assert "Pain A" in content
        assert "Pain B" in content
        assert "Opportunity X" in content
        assert "HIGH" in content
        assert "Tech" in content

    def test_pain_points_sorted_by_intent(self, tmp_path):
        finder = _make_finder(tmp_path)
        analysis = _make_analysis(
            pain_points=[
                PainPoint("Low Intent", "low", 1, [], "low", "A"),
                PainPoint("High Intent", "high", 5, [], "high", "B"),
            ],
            market_opportunities=[],
        )
        results = [{"thread": {}, "analysis": analysis, "report_file": "r.md"}]
        finder._generate_summary_report("sorted", results)

        fp = os.path.join(str(tmp_path), "summary_sorted.md")
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()

        # High intent should come before low intent
        assert content.index("High Intent") < content.index("Low Intent")


# ── Output directory ──────────────────────────────────────────────────────────


class TestOutputDirectory:
    def test_creates_output_dir(self, tmp_path):
        output = str(tmp_path / "new_output")
        assert not os.path.exists(output)
        with patch("goldmine_finder.RedditFetcher"), \
             patch("goldmine_finder.AIAnalyzer"):
            from goldmine_finder import GoldmineFinder
            GoldmineFinder(output_dir=output)
        assert os.path.isdir(output)
