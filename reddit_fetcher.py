#!/usr/bin/env python3
"""
Reddit JSON Fetcher
Fetches and structures data from Reddit threads in JSON format
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import requests

import config as cfg

logger = logging.getLogger(__name__)


@dataclass
class Comment:
    """Comment data class"""
    id: str
    author: str
    body: str
    score: int
    created_utc: float
    parent_id: str
    gilded: int
    depth: int = 0
    replies: List['Comment'] = None

    def __post_init__(self):
        if self.replies is None:
            self.replies = []


@dataclass
class Thread:
    """Thread data class"""
    id: str
    title: str
    author: str
    selftext: str
    score: int
    num_comments: int
    created_utc: float
    url: str
    subreddit: str
    upvote_ratio: float
    comments: List[Comment] = None

    def __post_init__(self):
        if self.comments is None:
            self.comments = []


class RedditFetcher:
    """Reddit JSON API Fetcher"""

    def __init__(self, user_agent: str | None = None, rate_limit_delay: float | None = None):
        self.user_agent = user_agent or cfg.USER_AGENT
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.rate_limit_delay = rate_limit_delay if rate_limit_delay is not None else cfg.RATE_LIMIT_DELAY

    def fetch_thread(self, url: str) -> Optional[Thread]:
        """
        Fetch data from a Reddit thread URL in JSON format.

        Args:
            url: Reddit thread URL (e.g., https://www.reddit.com/r/Entrepreneur/comments/xxx/)

        Returns:
            Thread: Structured thread data
        """
        json_url = self._normalize_url(url)

        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(json_url, timeout=cfg.REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()

            thread = self._parse_thread(data)
            return thread

        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch data: %s", e)
            return None
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON: %s", e)
            return None
        except ValueError as e:
            logger.error("Failed to parse thread: %s", e)
            return None

    def _parse_post_listing(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a Reddit listing response into a list of post dicts."""
        posts = []
        for child in data.get('data', {}).get('children', []):
            post_data = child.get('data', {})
            posts.append({
                'id': post_data.get('id'),
                'title': post_data.get('title'),
                'author': post_data.get('author'),
                'score': post_data.get('score'),
                'num_comments': post_data.get('num_comments'),
                'url': post_data.get('url'),
                'permalink': f"https://www.reddit.com{post_data.get('permalink')}",
                'created_utc': post_data.get('created_utc'),
                'selftext': post_data.get('selftext', ''),
                'subreddit': post_data.get('subreddit', ''),
            })
        return posts

    def _fetch_listing(self, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse a subreddit listing URL."""
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, timeout=cfg.REQUEST_TIMEOUT)
            response.raise_for_status()
            return self._parse_post_listing(response.json())
        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch subreddit: %s", e)
            return []
        except json.JSONDecodeError as e:
            logger.error("Failed to parse subreddit JSON: %s", e)
            return []

    def fetch_subreddit_hot(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetch hot posts from a subreddit.

        Args:
            subreddit: Subreddit name (e.g., "Entrepreneur")
            limit: Number of posts to fetch (max 100)

        Returns:
            List[Dict]: List of posts
        """
        url = f"https://old.reddit.com/r/{subreddit}/hot.json?limit={min(limit, 100)}"
        return self._fetch_listing(url)

    def fetch_subreddit_top(self, subreddit: str, time_filter: str = "week", limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetch top posts from a subreddit.

        Args:
            subreddit: Subreddit name (e.g., "Entrepreneur")
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Number of posts to fetch (max 100)

        Returns:
            List[Dict]: List of posts
        """
        url = f"https://old.reddit.com/r/{subreddit}/top.json?t={time_filter}&limit={min(limit, 100)}"
        return self._fetch_listing(url)

    def fetch_subreddit_new(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetch new posts from a subreddit.

        Args:
            subreddit: Subreddit name (e.g., "Entrepreneur")
            limit: Number of posts to fetch (max 100)

        Returns:
            List[Dict]: List of posts
        """
        url = f"https://old.reddit.com/r/{subreddit}/new.json?limit={min(limit, 100)}"
        return self._fetch_listing(url)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to JSON API endpoint"""
        if url.endswith('.json'):
            return url

        if 'old.reddit.com' not in url:
            if 'www.reddit.com' in url:
                url = url.replace('www.reddit.com', 'old.reddit.com')
            elif 'reddit.com' in url:
                url = url.replace('reddit.com', 'old.reddit.com')

        url = url.rstrip('/')
        return f"{url}.json"

    def _parse_thread(self, data: List[Dict]) -> Thread:
        """Build Thread object from JSON data"""
        try:
            post_listing = data[0]['data']['children'][0]['data']
        except (IndexError, KeyError, TypeError) as e:
            raise ValueError(f"Unexpected Reddit API response structure: {e}") from e

        thread = Thread(
            id=post_listing.get('id', ''),
            title=post_listing.get('title', ''),
            author=post_listing.get('author', ''),
            selftext=post_listing.get('selftext', ''),
            score=post_listing.get('score', 0),
            num_comments=post_listing.get('num_comments', 0),
            created_utc=post_listing.get('created_utc', 0),
            url=post_listing.get('url', ''),
            subreddit=post_listing.get('subreddit', ''),
            upvote_ratio=post_listing.get('upvote_ratio', 0.0),
        )

        if len(data) > 1:
            comments_listing = data[1]['data']['children']
            thread.comments = self._parse_comments(comments_listing)

        return thread

    def _parse_comments(self, comments_data: List[Dict], depth: int = 0) -> List[Comment]:
        """Recursively parse comments"""
        comments = []

        for item in comments_data:
            kind = item.get('kind')

            if kind == 'more':
                continue

            if kind != 't1':
                continue

            comment_data = item.get('data', {})

            comment = Comment(
                id=comment_data.get('id', ''),
                author=comment_data.get('author', ''),
                body=comment_data.get('body', ''),
                score=comment_data.get('score', 0),
                created_utc=comment_data.get('created_utc', 0),
                parent_id=comment_data.get('parent_id', ''),
                gilded=comment_data.get('gilded', 0),
                depth=depth,
            )

            replies_data = comment_data.get('replies')
            if isinstance(replies_data, dict):
                replies_children = replies_data.get('data', {}).get('children', [])
                comment.replies = self._parse_comments(replies_children, depth + 1)

            comments.append(comment)

        return comments

    def save_to_json(self, thread: Thread, filepath: str):
        """Save thread data to a JSON file"""
        def comment_to_dict(comment: Comment) -> Dict:
            return {
                'id': comment.id,
                'author': comment.author,
                'body': comment.body,
                'score': comment.score,
                'created_utc': comment.created_utc,
                'parent_id': comment.parent_id,
                'gilded': comment.gilded,
                'depth': comment.depth,
                'replies': [comment_to_dict(r) for r in comment.replies]
            }

        thread_dict = {
            'id': thread.id,
            'title': thread.title,
            'author': thread.author,
            'selftext': thread.selftext,
            'score': thread.score,
            'num_comments': thread.num_comments,
            'created_utc': thread.created_utc,
            'url': thread.url,
            'subreddit': thread.subreddit,
            'upvote_ratio': thread.upvote_ratio,
            'comments': [comment_to_dict(c) for c in thread.comments]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(thread_dict, f, ensure_ascii=False, indent=2)

        logger.info("Data saved: %s", filepath)

    def get_all_comments_flat(self, thread: Thread) -> List[Comment]:
        """Get all comments in a thread as a flat list"""
        all_comments = []

        def flatten(comments: List[Comment]):
            for comment in comments:
                all_comments.append(comment)
                if comment.replies:
                    flatten(comment.replies)

        flatten(thread.comments)
        return all_comments


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    fetcher = RedditFetcher()

    logger.info("=== Fetching hot posts from r/Entrepreneur... ===")
    hot_posts = fetcher.fetch_subreddit_hot("Entrepreneur", limit=5)

    for i, post in enumerate(hot_posts, 1):
        logger.info("%d. %s", i, post['title'])
        logger.info("   Score: %s | Comments: %s", post['score'], post['num_comments'])
        logger.info("   URL: %s", post['permalink'])

    if hot_posts:
        logger.info("=== Fetching details of the first thread... ===")
        first_post_url = hot_posts[0]['permalink']
        thread = fetcher.fetch_thread(first_post_url)

        if thread:
            logger.info("Title: %s", thread.title)
            logger.info("Author: %s", thread.author)
            logger.info("Score: %s", thread.score)
            logger.info("Comments: %s", thread.num_comments)
            body_preview = thread.selftext[:200] + "..." if len(thread.selftext) > 200 else thread.selftext
            logger.info("Body: %s", body_preview)

            all_comments = fetcher.get_all_comments_flat(thread)
            logger.info("Total comments fetched: %d", len(all_comments))

            fetcher.save_to_json(thread, f"thread_{thread.id}.json")
