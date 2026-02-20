"""
Tests for ai_analyzer.py: full pipeline with mocked OpenAI API.

Covers:
- analyze_thread end-to-end (mocked)
- Comment filtering (short, empty, nested)
- Comment capping (MAX_COMMENTS)
- _analyze_with_ai response parsing
- Edge cases (missing fields, empty response, API errors)
- save_analysis file I/O
- generate_report sorting & content
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from ai_analyzer import AIAnalyzer, AnalysisResult, PainPoint


def _make_analyzer():
    """Create an AIAnalyzer without requiring a real API key."""
    analyzer = AIAnalyzer.__new__(AIAnalyzer)
    analyzer.model = "gpt-4.1-mini"
    analyzer.client = MagicMock()
    return analyzer


def _make_mock_client(response_dict):
    """Return a MagicMock OpenAI client that returns *response_dict* as JSON."""
    mock_msg = MagicMock()
    mock_msg.content = json.dumps(response_dict)
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    client = MagicMock()
    client.chat.completions.create.return_value = mock_completion
    return client


# ── analyze_thread ────────────────────────────────────────────────────────────


class TestAnalyzeThread:
    """Tests for AIAnalyzer.analyze_thread with mocked _analyze_with_ai"""

    def test_basic_pipeline(self, minimal_thread_dict, mock_ai_response):
        analyzer = _make_analyzer()
        ai_return = {
            "pain_points": [PainPoint(**pp) for pp in mock_ai_response["pain_points"]],
            "key_insights": mock_ai_response["key_insights"],
            "market_opportunities": mock_ai_response["market_opportunities"],
            "sentiment_summary": mock_ai_response["sentiment_summary"],
        }
        with patch.object(analyzer, "_analyze_with_ai", return_value=ai_return):
            result = analyzer.analyze_thread(minimal_thread_dict)

        assert isinstance(result, AnalysisResult)
        assert result.thread_id == "test123"
        assert result.thread_title == "Test Thread Title"
        assert len(result.pain_points) == 2
        assert result.analyzed_comments > 0

    def test_short_comments_filtered(self, minimal_thread_dict):
        """Comments <= 10 chars and empty ones must be filtered out."""
        analyzer = _make_analyzer()
        empty_return = {
            "pain_points": [], "key_insights": [],
            "market_opportunities": [], "sentiment_summary": "",
        }
        with patch.object(analyzer, "_analyze_with_ai", return_value=empty_return) as mock_ai:
            analyzer.analyze_thread(minimal_thread_dict)
            comments_passed = mock_ai.call_args[1]["comments"]
            # "short" (5 chars) and "" should be filtered; 3 remain
            assert len(comments_passed) == 3
            for c in comments_passed:
                assert len(c) > 10

    def test_empty_comments(self):
        analyzer = _make_analyzer()
        thread = {"id": "e", "title": "Empty", "selftext": "body", "comments": []}
        empty_return = {
            "pain_points": [], "key_insights": [],
            "market_opportunities": [], "sentiment_summary": "",
        }
        with patch.object(analyzer, "_analyze_with_ai", return_value=empty_return):
            result = analyzer.analyze_thread(thread)
        assert result.analyzed_comments == 0
        assert result.total_comments == 0

    def test_missing_comments_key(self):
        analyzer = _make_analyzer()
        thread = {"id": "n", "title": "No Comments Key"}
        empty_return = {
            "pain_points": [], "key_insights": [],
            "market_opportunities": [], "sentiment_summary": "",
        }
        with patch.object(analyzer, "_analyze_with_ai", return_value=empty_return):
            result = analyzer.analyze_thread(thread)
        assert result.analyzed_comments == 0

    def test_comment_capping(self):
        analyzer = _make_analyzer()
        comments = [
            {"body": f"Comment number {i} is long enough to pass", "replies": []}
            for i in range(200)
        ]
        thread = {"id": "big", "title": "Big", "selftext": "", "comments": comments}
        empty_return = {
            "pain_points": [], "key_insights": [],
            "market_opportunities": [], "sentiment_summary": "",
        }
        with patch.object(analyzer, "_analyze_with_ai", return_value=empty_return):
            with patch("ai_analyzer.cfg") as mock_cfg:
                mock_cfg.MAX_COMMENTS = 50
                mock_cfg.MAX_COMMENTS_IN_PROMPT = 25
                mock_cfg.TEMPERATURE = 0.3
                result = analyzer.analyze_thread(thread)
        assert result.analyzed_comments == 50


# ── _analyze_with_ai ─────────────────────────────────────────────────────────


class TestAnalyzeWithAI:
    """Tests for _analyze_with_ai with mocked OpenAI client"""

    def test_valid_response(self, mock_ai_response):
        analyzer = _make_analyzer()
        analyzer.client = _make_mock_client(mock_ai_response)
        result = analyzer._analyze_with_ai("Title", "Body", ["Comment 1", "Comment 2"])

        assert len(result["pain_points"]) == 2
        assert isinstance(result["pain_points"][0], PainPoint)
        assert result["pain_points"][0].description == "Users struggle with billing management"
        assert len(result["key_insights"]) == 2
        assert len(result["market_opportunities"]) == 2

    def test_empty_pain_points(self):
        resp = {"pain_points": [], "key_insights": [], "market_opportunities": [], "sentiment_summary": ""}
        analyzer = _make_analyzer()
        analyzer.client = _make_mock_client(resp)
        result = analyzer._analyze_with_ai("T", "B", ["C"])
        assert result["pain_points"] == []

    def test_missing_fields_in_response(self):
        """API returns only sentiment — other fields should default to []."""
        resp = {"sentiment_summary": "Neutral"}
        analyzer = _make_analyzer()
        analyzer.client = _make_mock_client(resp)
        result = analyzer._analyze_with_ai("T", "B", ["C"])
        assert result["pain_points"] == []
        assert result["key_insights"] == []
        assert result["market_opportunities"] == []
        assert result["sentiment_summary"] == "Neutral"

    def test_pain_point_missing_optional_fields(self):
        """Pain point with only description should use safe defaults."""
        resp = {
            "pain_points": [{"description": "A problem"}],
            "key_insights": [], "market_opportunities": [], "sentiment_summary": "",
        }
        analyzer = _make_analyzer()
        analyzer.client = _make_mock_client(resp)
        result = analyzer._analyze_with_ai("T", "B", ["C"])
        pp = result["pain_points"][0]
        assert pp.description == "A problem"
        assert pp.severity == "medium"
        assert pp.purchase_intent == "none"
        assert pp.category == "Other"
        assert pp.frequency_mentioned == 0
        assert pp.example_comments == []

    def test_api_error_propagates(self):
        analyzer = _make_analyzer()
        analyzer.client.chat.completions.create.side_effect = Exception("Rate limit")
        with pytest.raises(Exception, match="Rate limit"):
            analyzer._analyze_with_ai("T", "B", ["C"])


# ── save_analysis ─────────────────────────────────────────────────────────────


class TestSaveAnalysis:
    def test_save_and_reload(self, tmp_path):
        analyzer = _make_analyzer()
        result = AnalysisResult(
            thread_id="t1", thread_title="Test", total_comments=10,
            pain_points=[
                PainPoint("Problem", "high", 3, ["ex"], "medium", "Tech"),
            ],
            key_insights=["insight"],
            market_opportunities=["opportunity"],
            sentiment_summary="Positive",
            analyzed_comments=10,
        )
        fp = str(tmp_path / "analysis.json")
        analyzer.save_analysis(result, fp)

        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["thread_id"] == "t1"
        assert len(data["pain_points"]) == 1
        assert data["pain_points"][0]["severity"] == "high"
        assert data["key_insights"] == ["insight"]


# ── generate_report ──────────────────────────────────────────────────────────


class TestGenerateReportExtended:
    def _result(self, **overrides):
        defaults = dict(
            thread_id="t1", thread_title="Test Thread", total_comments=10,
            pain_points=[], key_insights=[], market_opportunities=[],
            sentiment_summary="Neutral", analyzed_comments=10,
        )
        defaults.update(overrides)
        return AnalysisResult(**defaults)

    def test_empty_pain_points(self):
        report = _make_analyzer().generate_report(self._result())
        assert "Test Thread" in report
        assert "Pain Points" in report

    def test_sorted_by_purchase_intent(self):
        pps = [
            PainPoint("Low", "low", 1, [], "low", "A"),
            PainPoint("High", "high", 5, [], "high", "B"),
            PainPoint("Medium", "medium", 3, [], "medium", "C"),
        ]
        report = _make_analyzer().generate_report(self._result(pain_points=pps))
        assert report.index("High") < report.index("Low")

    def test_unicode_content(self):
        report = _make_analyzer().generate_report(
            self._result(thread_title="日本語スレッド", sentiment_summary="ポジティブ"),
        )
        assert "日本語スレッド" in report
        assert "ポジティブ" in report


# ── Sample data integration ──────────────────────────────────────────────────


class TestSampleDataIntegrity:
    """Verify examples/sample_thread.json can go through the flatten pipeline."""

    def test_flatten_sample_thread(self, sample_thread_data):
        analyzer = _make_analyzer()
        flat = analyzer._flatten_comments(sample_thread_data.get("comments", []))
        assert len(flat) > 0
        # Every flattened comment must have a 'body' key
        for c in flat:
            assert "body" in c

    def test_sample_analysis_schema(self, sample_analysis_data):
        """sample_analysis.json must match AnalysisResult shape."""
        required = [
            "thread_id", "thread_title", "total_comments",
            "pain_points", "key_insights", "market_opportunities",
            "sentiment_summary",
        ]
        for field in required:
            assert field in sample_analysis_data

        for pp in sample_analysis_data["pain_points"]:
            assert pp["severity"] in ("low", "medium", "high", "critical")
            assert pp["purchase_intent"] in ("none", "low", "medium", "high")
            assert isinstance(pp["frequency_mentioned"], int)
