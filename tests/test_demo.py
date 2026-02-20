"""
Tests for demo.py — standalone demo script.

Covers:
- Successful execution with sample data
- Output contains expected sections (title, pain points, insights, opportunities)
- Pain points sorted by purchase intent (high → low)
- FileNotFoundError handling when sample data is missing
"""

import os
import pytest


class TestDemoExecution:
    """demo.demo() runs end-to-end without errors."""

    def test_runs_without_error(self, capsys):
        from demo import demo
        demo()
        captured = capsys.readouterr()
        assert "Demo complete!" in captured.out

    def test_output_contains_thread_title(self, capsys):
        from demo import demo
        demo()
        captured = capsys.readouterr()
        assert "Thread title:" in captured.out

    def test_output_contains_analysis_sections(self, capsys):
        from demo import demo
        demo()
        captured = capsys.readouterr()
        assert "Pain points found:" in captured.out
        assert "Key Insights" in captured.out
        assert "Market Opportunities" in captured.out

    def test_output_contains_purchase_intent(self, capsys):
        from demo import demo
        demo()
        captured = capsys.readouterr()
        # Should have at least one intent label
        assert any(label in captured.out for label in ["HIGH", "MEDIUM", "LOW", "NONE"])

    def test_output_contains_next_steps(self, capsys):
        from demo import demo
        demo()
        captured = capsys.readouterr()
        assert "Next steps:" in captured.out
        assert "streamlit run app.py" in captured.out


class TestDemoPainPointSorting:
    """Pain points are sorted by purchase intent descending."""

    def test_high_before_low(self, capsys):
        from demo import demo
        demo()
        captured = capsys.readouterr()
        lines = captured.out.split("\n")
        intent_lines = [l for l in lines if "Purchase Intent:" in l]
        if len(intent_lines) >= 2:
            # First intent should be >= second intent
            order = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "NONE": 1}
            first_label = intent_lines[0].split(":")[-1].strip()
            second_label = intent_lines[1].split(":")[-1].strip()
            assert order.get(first_label, 0) >= order.get(second_label, 0)


class TestDemoMissingFiles:
    """FileNotFoundError is handled gracefully."""

    def test_missing_sample_data(self, capsys, monkeypatch, tmp_path):
        import demo
        monkeypatch.setattr(demo, "EXAMPLES_DIR", str(tmp_path / "nonexistent"))
        demo.demo()
        captured = capsys.readouterr()
        assert "Sample data not found" in captured.out
