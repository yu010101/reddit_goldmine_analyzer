"""Shared fixtures for all test modules."""

import json
import os
import pytest


@pytest.fixture
def sample_thread_data():
    """Load sample thread JSON from examples/."""
    path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_thread.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_analysis_data():
    """Load sample analysis JSON from examples/."""
    path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_analysis.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_listing_response():
    """A Reddit listing API response with 3 posts (varying num_comments)."""
    return {
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "id": "post1",
                        "title": "First Post Title",
                        "author": "user1",
                        "score": 150,
                        "num_comments": 30,
                        "url": "https://www.reddit.com/r/test/comments/post1/first/",
                        "permalink": "/r/test/comments/post1/first/",
                        "created_utc": 1700000000.0,
                        "selftext": "Body of first post",
                        "subreddit": "test",
                    },
                },
                {
                    "kind": "t3",
                    "data": {
                        "id": "post2",
                        "title": "Second Post Title",
                        "author": "user2",
                        "score": 75,
                        "num_comments": 3,
                        "url": "https://www.reddit.com/r/test/comments/post2/second/",
                        "permalink": "/r/test/comments/post2/second/",
                        "created_utc": 1700001000.0,
                        "selftext": "",
                        "subreddit": "test",
                    },
                },
                {
                    "kind": "t3",
                    "data": {
                        "id": "post3",
                        "title": "Third Post Title",
                        "author": "user3",
                        "score": 5,
                        "num_comments": 0,
                        "url": "https://www.reddit.com/r/test/comments/post3/third/",
                        "permalink": "/r/test/comments/post3/third/",
                        "created_utc": 1700002000.0,
                        "selftext": "No comments here",
                        "subreddit": "test",
                    },
                },
            ]
        }
    }


@pytest.fixture
def mock_ai_response():
    """A valid AI analysis response dict (parsed JSON)."""
    return {
        "pain_points": [
            {
                "description": "Users struggle with billing management",
                "severity": "high",
                "frequency_mentioned": 5,
                "example_comments": ["Billing is a nightmare", "I hate managing invoices"],
                "purchase_intent": "high",
                "category": "Finance",
            },
            {
                "description": "Lack of documentation",
                "severity": "medium",
                "frequency_mentioned": 2,
                "example_comments": ["Where are the docs?"],
                "purchase_intent": "low",
                "category": "Documentation",
            },
        ],
        "key_insights": [
            "Most users want automated billing",
            "Documentation is a recurring complaint",
        ],
        "market_opportunities": [
            "Build a billing automation SaaS",
            "Create a documentation generator tool",
        ],
        "sentiment_summary": "Mixed sentiment. Frustrated with billing but positive overall.",
    }


@pytest.fixture
def minimal_thread_dict():
    """Minimal thread dict with varied comments for filter testing."""
    return {
        "id": "test123",
        "title": "Test Thread Title",
        "selftext": "This is the thread body.",
        "comments": [
            {
                "body": "This is a comment with enough text to pass the filter.",
                "replies": [],
            },
            {
                "body": "Another substantial comment for the analysis pipeline.",
                "replies": [
                    {
                        "body": "A nested reply that is also long enough to pass.",
                        "replies": [],
                    }
                ],
            },
            {"body": "short", "replies": []},  # 5 chars — filtered out
            {"body": "", "replies": []},  # empty — filtered out
        ],
    }
