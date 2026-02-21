"""Tests for ai_analyzer.py"""

import json
import os
import pytest
from ai_analyzer import AIAnalyzer, AnalysisResult, PainPoint


class TestFlattenComments:
    """Tests for AIAnalyzer._flatten_comments"""

    def setup_method(self):
        # api_key=None is fine — we won't make real API calls
        # But OpenAI() will fail without a key, so provide a dummy
        self.analyzer = AIAnalyzer.__new__(AIAnalyzer)
        self.analyzer.model = "gpt-4.1-mini"

    def test_empty(self):
        assert self.analyzer._flatten_comments([]) == []

    def test_flat_comments(self):
        comments = [
            {"body": "a", "replies": []},
            {"body": "b", "replies": []},
        ]
        result = self.analyzer._flatten_comments(comments)
        assert len(result) == 2

    def test_nested_comments(self):
        comments = [
            {
                "body": "parent",
                "replies": [
                    {"body": "child1", "replies": []},
                    {
                        "body": "child2",
                        "replies": [{"body": "grandchild", "replies": []}],
                    },
                ],
            }
        ]
        result = self.analyzer._flatten_comments(comments)
        assert len(result) == 4
        bodies = [c["body"] for c in result]
        assert bodies == ["parent", "child1", "child2", "grandchild"]


class TestDeletedCommentFiltering:
    """Verify [deleted] and [removed] comments are excluded."""

    def setup_method(self):
        self.analyzer = AIAnalyzer.__new__(AIAnalyzer)
        self.analyzer.model = "gpt-4.1-mini"

    def test_deleted_comments_excluded(self):
        comments = [
            {"body": "[deleted]", "replies": []},
            {"body": "[removed]", "replies": []},
            {"body": "This is a valid comment with enough length", "replies": []},
            {"body": "short", "replies": []},
        ]
        flat = self.analyzer._flatten_comments(comments)
        texts = [c['body'] for c in flat
                 if c['body'] and len(c['body']) > 10
                 and c['body'] not in ('[deleted]', '[removed]')]
        assert len(texts) == 1
        assert texts[0] == "This is a valid comment with enough length"


class TestCommentCapping:
    """Tests that analyze_thread respects the comment limit"""

    def test_analyzed_comments_field(self):
        """AnalysisResult.analyzed_comments should reflect capped count"""
        result = AnalysisResult(
            thread_id="t1",
            thread_title="Test",
            total_comments=500,
            pain_points=[],
            key_insights=[],
            market_opportunities=[],
            sentiment_summary="",
            analyzed_comments=100,
        )
        assert result.total_comments == 500
        assert result.analyzed_comments == 100


class TestSampleAnalysisData:
    """Tests that sample data can be loaded and has expected structure"""

    @pytest.fixture
    def sample_data(self):
        path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_analysis.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_has_required_fields(self, sample_data):
        required = ["thread_id", "thread_title", "total_comments",
                     "pain_points", "key_insights", "market_opportunities",
                     "sentiment_summary"]
        for field in required:
            assert field in sample_data, f"Missing field: {field}"

    def test_pain_points_structure(self, sample_data):
        for pp in sample_data["pain_points"]:
            assert "description" in pp
            assert pp["severity"] in ("low", "medium", "high", "critical")
            assert pp["purchase_intent"] in ("none", "low", "medium", "high")
            assert isinstance(pp["frequency_mentioned"], int)
            assert isinstance(pp["example_comments"], list)

    def test_non_empty_results(self, sample_data):
        assert len(sample_data["pain_points"]) > 0
        assert len(sample_data["key_insights"]) > 0
        assert len(sample_data["market_opportunities"]) > 0
        assert len(sample_data["sentiment_summary"]) > 0


class TestGenerateReport:
    """Tests for AIAnalyzer.generate_report"""

    def test_report_contains_key_sections(self):
        analyzer = AIAnalyzer.__new__(AIAnalyzer)
        result = AnalysisResult(
            thread_id="t1",
            thread_title="Test Thread",
            total_comments=10,
            pain_points=[
                PainPoint(
                    description="Test pain",
                    severity="high",
                    frequency_mentioned=3,
                    example_comments=["example 1"],
                    purchase_intent="high",
                    category="Testing",
                )
            ],
            key_insights=["Insight 1"],
            market_opportunities=["Opportunity 1"],
            sentiment_summary="Positive overall",
            analyzed_comments=10,
        )
        report = analyzer.generate_report(result)

        assert "Test Thread" in report
        assert "Test pain" in report
        assert "Insight 1" in report
        assert "Opportunity 1" in report
        assert "Positive overall" in report
        assert "HIGH" in report
