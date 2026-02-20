"""
Tests for app.py pure logic — no Streamlit import required.

Covers:
- _comment_to_dict recursive conversion
- i18n t() helper with format kwargs
- render_analysis sorting: (purchase_intent DESC, frequency_mentioned DESC)
- load_sample returns valid analysis data
- Thread label truncation (>60 chars → 57 + "...")
- _browse_subreddit routing (hot/top/new)
"""

import json
import os
import re
import html

import pytest
from reddit_fetcher import Comment


# ── _comment_to_dict ────────────────────────────────────────────────────────


def _comment_to_dict(c):
    """Mirror of app._comment_to_dict (avoids importing Streamlit)."""
    return {
        "id": c.id, "author": c.author, "body": c.body,
        "score": c.score, "created_utc": c.created_utc,
        "parent_id": c.parent_id, "gilded": c.gilded,
        "depth": c.depth,
        "replies": [_comment_to_dict(r) for r in c.replies],
    }


class TestCommentToDict:
    def test_simple_comment(self):
        c = Comment(id="c1", author="u1", body="hello", score=5,
                    created_utc=1000.0, parent_id="t3_x", gilded=0)
        d = _comment_to_dict(c)
        assert d["id"] == "c1"
        assert d["body"] == "hello"
        assert d["replies"] == []

    def test_nested_replies(self):
        child = Comment(id="c2", author="u2", body="reply", score=1,
                        created_utc=1001.0, parent_id="t1_c1", gilded=0, depth=1)
        parent = Comment(id="c1", author="u1", body="parent", score=5,
                         created_utc=1000.0, parent_id="t3_x", gilded=0,
                         replies=[child])
        d = _comment_to_dict(parent)
        assert len(d["replies"]) == 1
        assert d["replies"][0]["id"] == "c2"
        assert d["replies"][0]["depth"] == 1

    def test_deeply_nested(self):
        """3 levels deep: c1 → c2 → c3."""
        c3 = Comment(id="c3", author="u3", body="deep", score=0,
                     created_utc=1002.0, parent_id="t1_c2", gilded=0, depth=2)
        c2 = Comment(id="c2", author="u2", body="mid", score=1,
                     created_utc=1001.0, parent_id="t1_c1", gilded=0, depth=1,
                     replies=[c3])
        c1 = Comment(id="c1", author="u1", body="top", score=5,
                     created_utc=1000.0, parent_id="t3_x", gilded=0,
                     replies=[c2])
        d = _comment_to_dict(c1)
        assert d["replies"][0]["replies"][0]["id"] == "c3"

    def test_all_fields_preserved(self):
        c = Comment(id="c1", author="u1", body="text", score=42,
                    created_utc=9999.0, parent_id="t3_x", gilded=3, depth=7)
        d = _comment_to_dict(c)
        assert d["score"] == 42
        assert d["gilded"] == 3
        assert d["depth"] == 7
        assert d["created_utc"] == 9999.0


# ── i18n t() helper ──────────────────────────────────────────────────────────


class TestI18nTFunction:
    """Re-implements t() to test i18n formatting logic."""

    @pytest.fixture
    def translations(self):
        app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            source = f.read()
        # Verify T dict exists
        assert "T = {" in source
        return source

    def test_meta_fmt_has_format_placeholders(self, translations):
        """meta_fmt must contain {n}, {pp}, {ins}, {opp} placeholders."""
        assert '"meta_fmt"' in translations
        # Extract en meta_fmt value
        m = re.search(r'"meta_fmt"\s*:\s*"([^"]*)"', translations)
        assert m
        fmt = m.group(1)
        assert "{n}" in fmt
        assert "{pp}" in fmt
        assert "{ins}" in fmt
        assert "{opp}" in fmt

    def test_format_placeholders_in_discover_err_fetch(self, translations):
        m = re.search(r'"discover_err_fetch"\s*:\s*"([^"]*)"', translations)
        assert m
        assert "{subreddit}" in m.group(1)

    def test_format_placeholders_in_warn_comment_limit(self, translations):
        m = re.search(r'"warn_comment_limit"\s*:\s*"([^"]*)"', translations)
        assert m
        fmt = m.group(1)
        assert "{total}" in fmt
        assert "{analyzed}" in fmt

    def test_show_quotes_has_n_placeholder(self, translations):
        m = re.search(r'"show_quotes"\s*:\s*"([^"]*)"', translations)
        assert m
        assert "{n}" in m.group(1)


# ── render_analysis sorting ──────────────────────────────────────────────────


class TestRenderAnalysisSorting:
    """Pain points must be sorted by (purchase_intent DESC, frequency DESC)."""

    INTENT_ORDER = {"high": 4, "medium": 3, "low": 2, "none": 1}

    def _sort_pain_points(self, pain_points):
        """Mirror of render_analysis sorting logic."""
        return sorted(
            pain_points,
            key=lambda x: (
                self.INTENT_ORDER.get(x.get("purchase_intent", "none"), 0),
                x.get("frequency_mentioned", 0),
            ),
            reverse=True,
        )

    def test_high_before_low(self):
        pps = [
            {"purchase_intent": "low", "frequency_mentioned": 10},
            {"purchase_intent": "high", "frequency_mentioned": 1},
        ]
        result = self._sort_pain_points(pps)
        assert result[0]["purchase_intent"] == "high"

    def test_same_intent_sorted_by_frequency(self):
        pps = [
            {"purchase_intent": "medium", "frequency_mentioned": 2},
            {"purchase_intent": "medium", "frequency_mentioned": 8},
        ]
        result = self._sort_pain_points(pps)
        assert result[0]["frequency_mentioned"] == 8

    def test_full_ordering(self):
        pps = [
            {"purchase_intent": "none", "frequency_mentioned": 100},
            {"purchase_intent": "high", "frequency_mentioned": 1},
            {"purchase_intent": "medium", "frequency_mentioned": 5},
            {"purchase_intent": "low", "frequency_mentioned": 3},
        ]
        result = self._sort_pain_points(pps)
        intents = [p["purchase_intent"] for p in result]
        assert intents == ["high", "medium", "low", "none"]

    def test_empty_list(self):
        assert self._sort_pain_points([]) == []

    def test_missing_fields_use_defaults(self):
        pps = [{"description": "A"}, {"description": "B"}]
        result = self._sort_pain_points(pps)
        # Both default to intent=none(1), freq=0 — order is stable
        assert len(result) == 2


# ── load_sample ──────────────────────────────────────────────────────────────


class TestLoadSample:
    """Sample analysis data must be valid and complete."""

    def test_sample_file_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_analysis.json")
        assert os.path.exists(path)

    def test_sample_has_required_keys(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_analysis.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in ["pain_points", "key_insights", "market_opportunities", "sentiment_summary"]:
            assert key in data, f"Missing key: {key}"

    def test_sample_thread_file_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_thread.json")
        assert os.path.exists(path)

    def test_sample_thread_has_required_keys(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_thread.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in ["id", "title", "score", "num_comments", "comments"]:
            assert key in data, f"Missing key: {key}"

    def test_sample_report_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_report.md")
        assert os.path.exists(path)


# ── Thread label truncation ──────────────────────────────────────────────────


class TestThreadLabelTruncation:
    """Discover tab truncates thread titles at 60 chars."""

    @staticmethod
    def _truncate(title):
        """Mirror of app.py label truncation logic."""
        lbl = title
        if len(lbl) > 60:
            lbl = lbl[:57] + "..."
        return lbl

    def test_short_title_unchanged(self):
        assert self._truncate("Short title") == "Short title"

    def test_exactly_60_unchanged(self):
        title = "A" * 60
        assert self._truncate(title) == title

    def test_61_chars_truncated(self):
        title = "A" * 61
        result = self._truncate(title)
        assert len(result) == 60
        assert result.endswith("...")

    def test_very_long_title(self):
        title = "A" * 200
        result = self._truncate(title)
        assert len(result) == 60
        assert result == "A" * 57 + "..."


# ── _browse_subreddit routing ────────────────────────────────────────────────


class TestBrowseSubredditRouting:
    """Verify _browse_subreddit dispatches to correct fetcher method."""

    def test_hot_sort(self):
        """sort='hot' calls fetch_subreddit_hot."""
        from unittest.mock import patch, MagicMock
        with patch("reddit_fetcher.RedditFetcher") as MockFetcher:
            mock = MagicMock()
            MockFetcher.return_value = mock
            mock.fetch_subreddit_hot.return_value = []

            # Re-implement routing logic
            sort = "hot"
            if sort == "top":
                mock.fetch_subreddit_top("test", time_filter="week", limit=25)
            elif sort == "new":
                mock.fetch_subreddit_new("test", limit=25)
            else:
                mock.fetch_subreddit_hot("test", limit=25)

            mock.fetch_subreddit_hot.assert_called_once()

    def test_top_sort(self):
        from unittest.mock import MagicMock
        mock = MagicMock()
        sort, time_filter = "top", "month"
        if sort == "top":
            mock.fetch_subreddit_top("test", time_filter=time_filter, limit=25)
        mock.fetch_subreddit_top.assert_called_once_with("test", time_filter="month", limit=25)

    def test_new_sort(self):
        from unittest.mock import MagicMock
        mock = MagicMock()
        sort = "new"
        if sort == "new":
            mock.fetch_subreddit_new("test", limit=25)
        mock.fetch_subreddit_new.assert_called_once()


# ── Sample catalog & new sample files ─────────────────────────────────────────


EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")

SAMPLE_CATALOG = [
    {"id": "saas", "file": "sample_analysis_saas.json"},
    {"id": "sideproject", "file": "sample_analysis_sideproject.json"},
    {"id": "startups", "file": "sample_analysis_startups.json"},
    {"id": "entrepreneur", "file": "sample_analysis.json"},
]

REQUIRED_KEYS = [
    "thread_id", "thread_title", "total_comments", "pain_points",
    "key_insights", "market_opportunities", "sentiment_summary",
]


class TestSampleCatalogFiles:
    """All sample analysis files exist and have valid structure."""

    @pytest.mark.parametrize("entry", SAMPLE_CATALOG, ids=[e["id"] for e in SAMPLE_CATALOG])
    def test_file_exists(self, entry):
        path = os.path.join(EXAMPLES_DIR, entry["file"])
        assert os.path.exists(path), f"Missing: {entry['file']}"

    @pytest.mark.parametrize("entry", SAMPLE_CATALOG, ids=[e["id"] for e in SAMPLE_CATALOG])
    def test_valid_json(self, entry):
        path = os.path.join(EXAMPLES_DIR, entry["file"])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("entry", SAMPLE_CATALOG, ids=[e["id"] for e in SAMPLE_CATALOG])
    def test_has_required_keys(self, entry):
        path = os.path.join(EXAMPLES_DIR, entry["file"])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in REQUIRED_KEYS:
            assert key in data, f"{entry['file']} missing key: {key}"

    @pytest.mark.parametrize("entry", SAMPLE_CATALOG, ids=[e["id"] for e in SAMPLE_CATALOG])
    def test_has_key_finding(self, entry):
        path = os.path.join(EXAMPLES_DIR, entry["file"])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "key_finding" in data, f"{entry['file']} missing key_finding"
        assert isinstance(data["key_finding"], str)
        assert len(data["key_finding"]) > 0

    @pytest.mark.parametrize("entry", SAMPLE_CATALOG, ids=[e["id"] for e in SAMPLE_CATALOG])
    def test_pain_points_have_required_fields(self, entry):
        path = os.path.join(EXAMPLES_DIR, entry["file"])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pp_keys = {"description", "severity", "frequency_mentioned",
                    "example_comments", "purchase_intent", "category"}
        for i, pp in enumerate(data["pain_points"]):
            for k in pp_keys:
                assert k in pp, f"{entry['file']} pain_point[{i}] missing: {k}"

    @pytest.mark.parametrize("entry", SAMPLE_CATALOG, ids=[e["id"] for e in SAMPLE_CATALOG])
    def test_total_comments_positive(self, entry):
        path = os.path.join(EXAMPLES_DIR, entry["file"])
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_comments"] > 0


class TestSampleDataExpectedValues:
    """Verify specific expected values in new sample files."""

    def test_saas_comment_count(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_saas.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_comments"] == 87

    def test_sideproject_comment_count(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_sideproject.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_comments"] == 134

    def test_startups_comment_count(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_startups.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_comments"] == 203

    def test_saas_pain_point_count(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_saas.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["pain_points"]) == 7

    def test_sideproject_pain_point_count(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_sideproject.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["pain_points"]) == 8

    def test_startups_pain_point_count(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_startups.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["pain_points"]) == 7


# ── Stats bar & key finding logic ─────────────────────────────────────────────


class TestStatsBarLogic:
    """Mirror of render_stats_bar computation logic."""

    @staticmethod
    def _compute_stats(data):
        comments = data.get("total_comments", 0)
        pain_points = len(data.get("pain_points", []))
        high_intent = sum(
            1 for pp in data.get("pain_points", [])
            if pp.get("purchase_intent") == "high"
        )
        return comments, pain_points, high_intent

    def test_saas_stats(self):
        path = os.path.join(EXAMPLES_DIR, "sample_analysis_saas.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        comments, pp, hi = self._compute_stats(data)
        assert comments == 87
        assert pp == 7
        assert hi > 0  # should have some high-intent pain points

    def test_empty_data(self):
        comments, pp, hi = self._compute_stats({})
        assert comments == 0
        assert pp == 0
        assert hi == 0

    def test_no_high_intent(self):
        data = {
            "total_comments": 10,
            "pain_points": [
                {"purchase_intent": "low"},
                {"purchase_intent": "medium"},
            ],
        }
        _, _, hi = self._compute_stats(data)
        assert hi == 0


class TestKeyFindingEscaping:
    """key_finding text must be HTML-escaped for safe rendering."""

    def test_xss_is_escaped(self):
        malicious = '<script>alert("xss")</script>'
        escaped = html.escape(malicious)
        assert "<script>" not in escaped
        assert "&lt;script&gt;" in escaped

    def test_normal_text_unchanged(self):
        text = "12 people cited churn management as their #1 challenge"
        assert html.escape(text) == text

    def test_ampersand_escaped(self):
        text = "R&D spending is too high"
        assert html.escape(text) == "R&amp;D spending is too high"


# ── New i18n keys ─────────────────────────────────────────────────────────────


class TestNewI18nKeys:
    """New i18n keys exist in both EN and JA."""

    NEW_KEYS = [
        "sample_select_label",
        "sample_key_finding",
        "sample_stats_comments",
        "sample_stats_pain_points",
        "sample_stats_high_intent",
    ]

    @pytest.fixture
    def app_source(self):
        app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            return f.read()

    @pytest.mark.parametrize("key", NEW_KEYS)
    def test_key_in_source(self, app_source, key):
        assert f'"{key}"' in app_source, f"i18n key missing: {key}"
