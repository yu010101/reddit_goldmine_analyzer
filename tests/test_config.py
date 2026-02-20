"""
Tests for config.py: defaults and environment variable overrides.

Covers:
- All default values
- Environment variable overrides via monkeypatch
- Type correctness
- Invariants (MAX_COMMENTS_IN_PROMPT <= MAX_COMMENTS)
"""

import importlib
import pytest


def _reload_config():
    """Reload config module to pick up env var changes."""
    import config
    importlib.reload(config)
    return config


class TestConfigDefaults:
    """Verify default values when no env vars are set."""

    def setup_method(self):
        self.cfg = _reload_config()

    def test_rate_limit_delay(self):
        assert self.cfg.RATE_LIMIT_DELAY == 2.0
        assert isinstance(self.cfg.RATE_LIMIT_DELAY, float)

    def test_request_timeout(self):
        assert self.cfg.REQUEST_TIMEOUT == 30
        assert isinstance(self.cfg.REQUEST_TIMEOUT, int)

    def test_user_agent(self):
        assert "RedditGoldmineAnalyzer" in self.cfg.USER_AGENT
        assert isinstance(self.cfg.USER_AGENT, str)

    def test_model(self):
        assert self.cfg.MODEL == "gpt-4.1-mini"

    def test_temperature(self):
        assert self.cfg.TEMPERATURE == 0.3
        assert isinstance(self.cfg.TEMPERATURE, float)

    def test_max_comments(self):
        assert self.cfg.MAX_COMMENTS == 100
        assert isinstance(self.cfg.MAX_COMMENTS, int)

    def test_max_comments_in_prompt(self):
        assert self.cfg.MAX_COMMENTS_IN_PROMPT == 50
        assert isinstance(self.cfg.MAX_COMMENTS_IN_PROMPT, int)

    def test_prompt_limit_leq_max_comments(self):
        assert self.cfg.MAX_COMMENTS_IN_PROMPT <= self.cfg.MAX_COMMENTS


class TestConfigEnvironmentOverrides:
    """Verify that RGA_* env vars override defaults."""

    def teardown_method(self):
        _reload_config()  # Reset to defaults after each test

    def test_rate_limit_override(self, monkeypatch):
        monkeypatch.setenv("RGA_RATE_LIMIT_DELAY", "0.5")
        cfg = _reload_config()
        assert cfg.RATE_LIMIT_DELAY == 0.5

    def test_timeout_override(self, monkeypatch):
        monkeypatch.setenv("RGA_REQUEST_TIMEOUT", "60")
        cfg = _reload_config()
        assert cfg.REQUEST_TIMEOUT == 60

    def test_user_agent_override(self, monkeypatch):
        monkeypatch.setenv("RGA_USER_AGENT", "CustomAgent/2.0")
        cfg = _reload_config()
        assert cfg.USER_AGENT == "CustomAgent/2.0"

    def test_model_override(self, monkeypatch):
        monkeypatch.setenv("RGA_MODEL", "gpt-4o")
        cfg = _reload_config()
        assert cfg.MODEL == "gpt-4o"

    def test_temperature_override(self, monkeypatch):
        monkeypatch.setenv("RGA_TEMPERATURE", "0.7")
        cfg = _reload_config()
        assert cfg.TEMPERATURE == 0.7

    def test_max_comments_override(self, monkeypatch):
        monkeypatch.setenv("RGA_MAX_COMMENTS", "200")
        cfg = _reload_config()
        assert cfg.MAX_COMMENTS == 200

    def test_max_comments_in_prompt_override(self, monkeypatch):
        monkeypatch.setenv("RGA_MAX_COMMENTS_IN_PROMPT", "75")
        cfg = _reload_config()
        assert cfg.MAX_COMMENTS_IN_PROMPT == 75
