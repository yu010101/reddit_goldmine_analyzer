"""
Security audit tests — source code analysis.

Covers:
- Every unsafe_allow_html=True call uses _esc() for user data
- _esc() is imported/defined
- No raw user data in HTML rendering
- Discover card titles and subreddit names are escaped
- Render functions escape descriptions, categories, insights, opportunities, sentiment
"""

import os
import re
import pytest


@pytest.fixture(scope="module")
def app_source():
    """Load app.py source code."""
    path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestEscFunctionExists:
    """The _esc() function must exist and use html.escape."""

    def test_esc_defined(self, app_source):
        assert "def _esc(s):" in app_source

    def test_esc_uses_html_escape(self, app_source):
        assert "_html_mod.escape" in app_source

    def test_html_module_imported(self, app_source):
        assert "import html as _html_mod" in app_source


class TestRenderThreadEscaping:
    """render_thread must escape thread_title."""

    def test_title_uses_esc(self, app_source):
        # Find render_thread function body
        m = re.search(r"def render_thread\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert '_esc(data.get("thread_title"' in body


class TestRenderPainPointEscaping:
    """render_pain_point must escape description and category."""

    def test_desc_uses_esc(self, app_source):
        m = re.search(r"def render_pain_point\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert '_esc(pp.get("description"' in body

    def test_cat_uses_esc(self, app_source):
        m = re.search(r"def render_pain_point\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert '_esc(pp.get("category"' in body

    def test_expander_quotes_escaped(self, app_source):
        """Example comment quotes in expander must use _esc."""
        m = re.search(r"def render_pain_point\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert "_esc(ex)" in body


class TestRenderInsightsEscaping:
    """render_insights must escape each item."""

    def test_items_use_esc(self, app_source):
        m = re.search(r"def render_insights\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert "_esc(item)" in body


class TestRenderOpportunitiesEscaping:
    """render_opportunities must escape each item."""

    def test_items_use_esc(self, app_source):
        m = re.search(r"def render_opportunities\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert "_esc(item)" in body


class TestRenderSentimentEscaping:
    """render_sentiment must escape the text."""

    def test_text_uses_esc(self, app_source):
        m = re.search(r"def render_sentiment\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        assert "_esc(text)" in body


class TestDiscoverCardEscaping:
    """Discover tab cards must escape title and subreddit name."""

    def test_card_title_escaped(self, app_source):
        # Look for _esc in the card HTML generation area
        assert '_esc(_p["title"])' in app_source

    def test_card_subreddit_escaped(self, app_source):
        assert '_esc(_p.get("subreddit"' in app_source


class TestDiscoverErrorEscaping:
    """Error messages with user input must be escaped."""

    def test_err_fetch_subreddit_escaped(self, app_source):
        assert "_esc(_active_sub)" in app_source


class TestNoRawUserDataInHtml:
    """No f-string HTML should contain un-escaped user data patterns."""

    def test_render_thread_title_pre_escaped(self, app_source):
        """render_thread must assign title via _esc before using in HTML."""
        m = re.search(r"def render_thread\(.*?\n(.*?)(?=\ndef |\Z)", app_source, re.DOTALL)
        assert m
        body = m.group(1)
        # The variable 'title' must be set via _esc(...) before use
        assert "title = _esc(" in body

    def test_no_raw_data_get_in_fstring_html(self, app_source):
        """No data.get() or pp.get() should appear directly in f-string HTML without _esc."""
        lines = app_source.split("\n")
        violations = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("assert"):
                continue
            # Look for f-string HTML with raw .get() — must use _esc
            if re.search(r"f'.*\{(?:data|pp|_p)\.get\(", stripped):
                if "_esc" not in stripped:
                    violations.append(f"Line {i}: {stripped}")
        assert not violations, f"Un-escaped .get() in f-string HTML: {violations}"


class TestSubredditValidation:
    """Subreddit name validation regex exists before API calls."""

    def test_validation_regex_exists(self, app_source):
        assert r'_VALID_SUB_RE = re.compile(r"^\w+$")' in app_source

    def test_validation_used_before_browse_call(self, app_source):
        """_VALID_SUB_RE.match is called before _browse_subreddit in main body."""
        # Skip function definition — find the call in main body (after "# ── Main")
        main_section = app_source[app_source.index("# ── Main"):]
        val_pos = main_section.index("_VALID_SUB_RE.match")
        browse_pos = main_section.index("_browse_subreddit(")
        assert val_pos < browse_pos, "Validation must occur before API call"

    def test_st_stop_on_invalid_sub(self, app_source):
        """st.stop() is called when subreddit name is invalid."""
        # Find the validation block
        val_start = app_source.index("_VALID_SUB_RE.match")
        next_section = app_source[val_start:val_start + 200]
        assert "st.stop()" in next_section
