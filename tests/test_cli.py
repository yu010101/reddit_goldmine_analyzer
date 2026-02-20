"""
Tests for goldmine_finder.py CLI (main function).

Covers:
- Argparse: no args → exit(1)
- --url mode dispatches to analyze_single_thread
- --subreddit mode dispatches to analyze_subreddit with limit/min-comments
- --batch mode reads file and dispatches to batch_analyze_urls
- --output sets output directory
- Exception handling (exit code)
"""

import sys
import pytest
from unittest.mock import patch, MagicMock


class TestCliNoArgs:
    """Running without arguments should print help and exit(1)."""

    def test_no_args_exits_with_1(self):
        with patch("sys.argv", ["goldmine_finder.py"]):
            with pytest.raises(SystemExit) as exc_info:
                from goldmine_finder import main
                main()
            assert exc_info.value.code == 1


class TestCliUrlMode:
    """--url dispatches to analyze_single_thread."""

    def test_url_calls_analyze_single_thread(self):
        test_url = "https://www.reddit.com/r/test/comments/abc/"
        with patch("sys.argv", ["goldmine_finder.py", "--url", test_url]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            main()
            mock_instance.analyze_single_thread.assert_called_once_with(test_url)


class TestCliSubredditMode:
    """--subreddit dispatches to analyze_subreddit."""

    def test_subreddit_with_defaults(self):
        with patch("sys.argv", ["goldmine_finder.py", "--subreddit", "SaaS"]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            main()
            mock_instance.analyze_subreddit.assert_called_once_with(
                "SaaS", limit=10, min_comments=5,
            )

    def test_subreddit_with_custom_limit(self):
        with patch("sys.argv", ["goldmine_finder.py", "--subreddit", "SaaS",
                                 "--limit", "20", "--min-comments", "10"]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            main()
            mock_instance.analyze_subreddit.assert_called_once_with(
                "SaaS", limit=20, min_comments=10,
            )


class TestCliBatchMode:
    """--batch reads URL file and dispatches to batch_analyze_urls."""

    def test_batch_reads_file(self, tmp_path):
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("https://reddit.com/r/a/comments/1/\nhttps://reddit.com/r/b/comments/2/\n")
        with patch("sys.argv", ["goldmine_finder.py", "--batch", str(urls_file)]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            main()
            call_args = mock_instance.batch_analyze_urls.call_args[0][0]
            assert len(call_args) == 2

    def test_batch_skips_empty_lines(self, tmp_path):
        urls_file = tmp_path / "urls.txt"
        urls_file.write_text("url1\n\n\nurl2\n  \n")
        with patch("sys.argv", ["goldmine_finder.py", "--batch", str(urls_file)]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            main()
            call_args = mock_instance.batch_analyze_urls.call_args[0][0]
            assert len(call_args) == 2  # empty/whitespace lines filtered


class TestCliOutputDir:
    """--output sets the output directory."""

    def test_custom_output(self, tmp_path):
        out = str(tmp_path / "custom_out")
        with patch("sys.argv", ["goldmine_finder.py", "--url", "http://test.com",
                                 "--output", out]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            main()
            MockFinder.assert_called_once_with(output_dir=out)


class TestCliExceptionHandling:
    """Exceptions during analysis result in exit(1)."""

    def test_general_exception_exits_1(self):
        with patch("sys.argv", ["goldmine_finder.py", "--url", "http://test.com"]), \
             patch("goldmine_finder.GoldmineFinder") as MockFinder:
            mock_instance = MagicMock()
            mock_instance.analyze_single_thread.side_effect = RuntimeError("boom")
            MockFinder.return_value = mock_instance
            from goldmine_finder import main
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
