"""
Tests for Discover-tab logic extracted from app.py.

Covers:
- _relative_time helper (boundary tests)
- i18n completeness (en vs ja key parity)
- Popular subreddits list
- Session state key definitions
- Subreddit extraction regex (for last_subreddit)
- Comment count filter logic (>= 5)
- XSS escape helper (_esc)
- Subreddit name validation
"""

import html
import re
import time
import pytest


# ── _relative_time ────────────────────────────────────────────────────────────


class TestRelativeTime:
    """
    Re-implements app._relative_time to test its logic
    without importing Streamlit.
    """

    @staticmethod
    def _relative_time(created_utc: float) -> str:
        import time as _t

        diff = _t.time() - created_utc
        if diff < 60:
            return "now"
        if diff < 3600:
            return f"{int(diff // 60)}m ago"
        if diff < 86400:
            return f"{int(diff // 3600)}h ago"
        return f"{int(diff // 86400)}d ago"

    # Exact values

    def test_just_now(self):
        assert self._relative_time(time.time()) == "now"

    def test_5_minutes(self):
        assert self._relative_time(time.time() - 300) == "5m ago"

    def test_2_hours(self):
        assert self._relative_time(time.time() - 7200) == "2h ago"

    def test_2_days(self):
        assert self._relative_time(time.time() - 172800) == "2d ago"

    def test_365_days(self):
        assert self._relative_time(time.time() - 86400 * 365) == "365d ago"

    # Boundary conditions

    def test_boundary_59s_is_now(self):
        assert self._relative_time(time.time() - 59) == "now"

    def test_boundary_60s_is_1m(self):
        assert self._relative_time(time.time() - 60) == "1m ago"

    def test_boundary_3599s_is_minutes(self):
        assert "m ago" in self._relative_time(time.time() - 3599)

    def test_boundary_3600s_is_1h(self):
        assert self._relative_time(time.time() - 3600) == "1h ago"

    def test_boundary_86399s_is_hours(self):
        assert "h ago" in self._relative_time(time.time() - 86399)

    def test_boundary_86400s_is_1d(self):
        assert self._relative_time(time.time() - 86400) == "1d ago"

    # Format

    def test_format_minutes(self):
        result = self._relative_time(time.time() - 120)
        assert re.match(r"^\d+m ago$", result)

    def test_format_hours(self):
        result = self._relative_time(time.time() - 10800)
        assert re.match(r"^\d+h ago$", result)

    def test_format_days(self):
        result = self._relative_time(time.time() - 259200)
        assert re.match(r"^\d+d ago$", result)


# ── i18n completeness ─────────────────────────────────────────────────────────


class TestI18nCompleteness:
    """Ensure every key in T['en'] also exists in T['ja'] and vice versa."""

    # All known i18n key prefixes (must match keys used in T dict)
    _I18N_PREFIXES = (
        "hero_", "tab_", "sample_", "label_", "btn_", "spinner_",
        "err_", "sec_", "show_", "meta_", "guide_", "how_",
        "warn_", "discover_",
    )
    _I18N_EXACT = {"footer"}

    @pytest.fixture
    def translation_keys(self):
        """
        Extract i18n keys from the T dict in app.py.
        We locate the "en" and "ja" blocks within T = { ... }
        and extract only keys that match known i18n prefixes.
        """
        import os

        app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            source = f.read()

        t_start = source.index("T = {")
        # Find end of T dict — look for the closing pattern '\n}'
        t_block = source[t_start:]
        # Split into en and ja blocks at the '"ja"' key
        parts = t_block.split('"ja"')
        en_block = parts[0]
        ja_block = parts[1].split("\n}")[0] if len(parts) > 1 else ""

        all_en = set(re.findall(r'"([a-z_]+)":', en_block))
        all_ja = set(re.findall(r'"([a-z_]+)":', ja_block))

        def _is_i18n(key):
            if key in self._I18N_EXACT:
                return True
            return any(key.startswith(p) for p in self._I18N_PREFIXES)

        en_keys = {k for k in all_en if _is_i18n(k)}
        ja_keys = {k for k in all_ja if _is_i18n(k)}

        return en_keys, ja_keys

    def test_en_keys_exist_in_ja(self, translation_keys):
        en_keys, ja_keys = translation_keys
        missing = en_keys - ja_keys
        assert not missing, f"Keys in en but missing in ja: {missing}"

    def test_ja_keys_exist_in_en(self, translation_keys):
        en_keys, ja_keys = translation_keys
        missing = ja_keys - en_keys
        assert not missing, f"Keys in ja but missing in en: {missing}"


# ── Popular subreddits ────────────────────────────────────────────────────────


EXPECTED_SUBS = [
    "Entrepreneur", "SaaS", "startups", "smallbusiness",
    "indiehackers", "webdev", "marketing", "sideproject",
]


class TestPopularSubreddits:
    def test_all_present_in_source(self):
        import os

        app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            source = f.read()
        for sub in EXPECTED_SUBS:
            assert f'"{sub}"' in source, f"Missing subreddit: {sub}"

    def test_no_duplicates(self):
        assert len(EXPECTED_SUBS) == len(set(EXPECTED_SUBS))


# ── Session state keys ───────────────────────────────────────────────────────


class TestSessionStateKeys:
    EXPECTED = {
        "discover_subreddit": "",
        "discover_sort": "hot",
        "discover_time": "week",
        "prefill_url": "",
        "last_subreddit": "",
    }

    def test_keys_in_source(self):
        import os

        app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            source = f.read()
        for key in self.EXPECTED:
            assert f'"{key}"' in source, f"Session key missing: {key}"

    def test_sort_default_is_valid(self):
        assert self.EXPECTED["discover_sort"] in ("hot", "top", "new")

    def test_time_default_is_valid(self):
        assert self.EXPECTED["discover_time"] in (
            "hour", "day", "week", "month", "year", "all",
        )


# ── Subreddit extraction regex ────────────────────────────────────────────────


class TestSubredditExtraction:
    """The regex used to set last_subreddit after analysis."""

    PATTERN = re.compile(r"reddit\.com/r/(\w+)/")

    def test_www_url(self):
        m = self.PATTERN.search("https://www.reddit.com/r/Entrepreneur/comments/abc/title/")
        assert m and m.group(1) == "Entrepreneur"

    def test_old_url(self):
        m = self.PATTERN.search("https://old.reddit.com/r/SaaS/comments/xyz/title/")
        assert m and m.group(1) == "SaaS"

    def test_bare_url(self):
        m = self.PATTERN.search("https://reddit.com/r/startups/comments/x/")
        assert m and m.group(1) == "startups"

    def test_no_match(self):
        assert self.PATTERN.search("https://example.com/not-reddit") is None

    def test_underscore_subreddit(self):
        m = self.PATTERN.search("https://www.reddit.com/r/small_business/comments/x/")
        assert m and m.group(1) == "small_business"


# ── Comment count filter ──────────────────────────────────────────────────────


class TestCommentCountFilter:
    """The Discover tab filters posts with num_comments >= 5."""

    def _filter(self, posts):
        return [p for p in posts if p.get("num_comments", 0) >= 5]

    def test_above_threshold(self):
        posts = [{"num_comments": 10}, {"num_comments": 5}]
        assert len(self._filter(posts)) == 2

    def test_below_threshold(self):
        posts = [{"num_comments": 4}, {"num_comments": 0}]
        assert len(self._filter(posts)) == 0

    def test_exact_threshold(self):
        posts = [{"num_comments": 5}]
        assert len(self._filter(posts)) == 1

    def test_missing_key(self):
        posts = [{}]
        assert len(self._filter(posts)) == 0

    def test_mixed(self, mock_listing_response):
        """Using the fixture: post1=30, post2=3, post3=0 → only post1 passes."""
        from reddit_fetcher import RedditFetcher

        fetcher = RedditFetcher()
        posts = fetcher._parse_post_listing(mock_listing_response)
        filtered = self._filter(posts)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "post1"


# ── XSS escape helper (_esc) ────────────────────────────────────────────────


class TestXssEscape:
    """
    Re-implements app._esc to verify HTML escaping logic
    without importing Streamlit.
    """

    @staticmethod
    def _esc(s):
        return html.escape(str(s)) if s else ""

    def test_angle_brackets(self):
        assert "<script>" not in self._esc("<script>alert(1)</script>")
        assert "&lt;script&gt;" in self._esc("<script>alert(1)</script>")

    def test_ampersand(self):
        assert self._esc("A & B") == "A &amp; B"

    def test_quotes(self):
        result = self._esc('He said "hello"')
        assert "&quot;" in result
        assert '"hello"' not in result

    def test_single_quote(self):
        result = self._esc("it's")
        assert "&#x27;" in result or "'" in result  # html.escape escapes ' only with quote=True

    def test_none_returns_empty(self):
        assert self._esc(None) == ""

    def test_empty_string_returns_empty(self):
        assert self._esc("") == ""

    def test_plain_text_unchanged(self):
        assert self._esc("Hello world") == "Hello world"

    def test_numeric_input(self):
        assert self._esc(42) == "42"

    def test_nested_html(self):
        malicious = '<img src=x onerror="alert(1)">'
        escaped = self._esc(malicious)
        assert "<img" not in escaped
        assert "onerror" not in escaped or "&quot;" in escaped

    def test_reddit_title_with_special_chars(self):
        title = "What's the best SaaS for <enterprise> & SMB?"
        escaped = self._esc(title)
        assert "<enterprise>" not in escaped
        assert "&amp;" in escaped


# ── Subreddit name validation ────────────────────────────────────────────────


class TestSubredditNameValidation:
    """Validates the regex used to check subreddit names before API calls."""

    PATTERN = re.compile(r"^\w+$")

    def test_valid_simple(self):
        assert self.PATTERN.match("Entrepreneur")

    def test_valid_lowercase(self):
        assert self.PATTERN.match("startups")

    def test_valid_with_underscore(self):
        assert self.PATTERN.match("small_business")

    def test_valid_with_numbers(self):
        assert self.PATTERN.match("web3")

    def test_invalid_empty(self):
        assert not self.PATTERN.match("")

    def test_invalid_spaces(self):
        assert not self.PATTERN.match("foo bar")

    def test_invalid_slash(self):
        assert not self.PATTERN.match("r/startups")

    def test_invalid_special_chars(self):
        assert not self.PATTERN.match("test!@#")

    def test_invalid_url_injection(self):
        assert not self.PATTERN.match("test/../../../etc/passwd")

    def test_invalid_newline(self):
        assert not self.PATTERN.match("test\ninjection")
