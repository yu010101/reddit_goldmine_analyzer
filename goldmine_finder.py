#!/usr/bin/env python3
"""
Reddit Goldmine Finder
Main tool for discovering "goldmines" from Reddit threads using AI
"""

import argparse
import json
import logging
import os
import sys
from typing import List, Dict
from reddit_fetcher import RedditFetcher
from ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


class GoldmineFinder:
    """Goldmine discovery tool"""

    def __init__(self, output_dir: str = "output"):
        self.fetcher = RedditFetcher()
        self.analyzer = AIAnalyzer()
        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

    def analyze_single_thread(self, url: str) -> Dict:
        """Analyze a single thread"""
        logger.info("=" * 70)
        logger.info("Starting thread analysis: %s", url)
        logger.info("=" * 70)

        logger.info("Fetching thread data...")
        thread = self.fetcher.fetch_thread(url)

        if not thread:
            logger.error("Failed to fetch thread")
            return None

        logger.info("Fetched: %d comments", thread.num_comments)

        thread_file = os.path.join(self.output_dir, f"thread_{thread.id}.json")
        self.fetcher.save_to_json(thread, thread_file)

        thread_dict = self._thread_to_dict(thread)

        logger.info("Running AI analysis...")
        result = self.analyzer.analyze_thread(thread_dict)

        analysis_file = os.path.join(self.output_dir, f"analysis_{thread.id}.json")
        self.analyzer.save_analysis(result, analysis_file)

        report = self.analyzer.generate_report(result)
        report_file = os.path.join(self.output_dir, f"report_{thread.id}.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info("Analysis complete!")
        logger.info("Report: %s", report_file)
        logger.info("Analysis data: %s", analysis_file)

        return {
            'thread': thread_dict,
            'analysis': result,
            'report_file': report_file
        }

    def analyze_subreddit(self, subreddit: str, limit: int = 10, min_comments: int = 5) -> List[Dict]:
        """Analyze multiple threads from a subreddit"""
        logger.info("=" * 70)
        logger.info("Subreddit analysis: r/%s", subreddit)
        logger.info("=" * 70)

        logger.info("Fetching hot posts from r/%s...", subreddit)
        posts = self.fetcher.fetch_subreddit_hot(subreddit, limit=limit)

        if not posts:
            logger.error("Failed to fetch posts")
            return []

        logger.info("Fetched %d posts", len(posts))

        filtered_posts = [p for p in posts if p['num_comments'] >= min_comments]
        logger.info("%d posts meet the minimum %d comments threshold", len(filtered_posts), min_comments)

        results = []

        for i, post in enumerate(filtered_posts, 1):
            logger.info("--- [%d/%d] ---", i, len(filtered_posts))
            logger.info("Title: %s", post['title'])
            logger.info("Comments: %d", post['num_comments'])

            result = self.analyze_single_thread(post['permalink'])
            if result:
                results.append(result)

        self._generate_summary_report(subreddit, results)

        return results

    def batch_analyze_urls(self, urls: List[str]) -> List[Dict]:
        """Batch analyze multiple URLs"""
        logger.info("=" * 70)
        logger.info("Batch analysis: %d threads", len(urls))
        logger.info("=" * 70)

        results = []

        for i, url in enumerate(urls, 1):
            logger.info("--- [%d/%d] ---", i, len(urls))
            result = self.analyze_single_thread(url)
            if result:
                results.append(result)

        self._generate_summary_report("batch", results)

        return results

    def _thread_to_dict(self, thread) -> Dict:
        """Convert Thread object to dictionary"""
        def comment_to_dict(comment):
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

        return {
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

    def _generate_summary_report(self, name: str, results: List[Dict]):
        """Generate summary report for multiple threads"""
        if not results:
            return

        summary_file = os.path.join(self.output_dir, f"summary_{name}.md")

        report = f"""# Reddit Goldmine Analysis - Summary Report

**Target**: {name}
**Threads Analyzed**: {len(results)}

---

## Top Pain Points (by Purchase Intent)

"""

        all_pain_points = []
        for result in results:
            analysis = result['analysis']
            for pp in analysis.pain_points:
                all_pain_points.append({
                    'thread_title': analysis.thread_title,
                    'description': pp.description,
                    'severity': pp.severity,
                    'purchase_intent': pp.purchase_intent,
                    'category': pp.category,
                    'frequency': pp.frequency_mentioned
                })

        intent_order = {'high': 4, 'medium': 3, 'low': 2, 'none': 1}
        sorted_pain_points = sorted(
            all_pain_points,
            key=lambda x: intent_order.get(x['purchase_intent'], 0),
            reverse=True
        )

        for i, pp in enumerate(sorted_pain_points[:20], 1):
            intent_emoji = {
                'high': '💰💰💰',
                'medium': '💰💰',
                'low': '💰',
                'none': '⚫'
            }.get(pp['purchase_intent'], '⚫')

            report += f"""
### {i}. {pp['description']}

- **Purchase Intent**: {intent_emoji} {pp['purchase_intent'].upper()}
- **Category**: {pp['category']}
- **Source Thread**: {pp['thread_title']}

"""

        report += """
---

## Category Breakdown

"""

        category_stats = {}
        for pp in all_pain_points:
            cat = pp['category']
            if cat not in category_stats:
                category_stats[cat] = {
                    'count': 0,
                    'high_intent': 0,
                    'medium_intent': 0,
                    'low_intent': 0
                }
            category_stats[cat]['count'] += 1
            if pp['purchase_intent'] == 'high':
                category_stats[cat]['high_intent'] += 1
            elif pp['purchase_intent'] == 'medium':
                category_stats[cat]['medium_intent'] += 1
            elif pp['purchase_intent'] == 'low':
                category_stats[cat]['low_intent'] += 1

        for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['high_intent'], reverse=True):
            report += f"""
**{cat}**
- Pain points: {stats['count']}
- High intent: {stats['high_intent']} | Medium intent: {stats['medium_intent']} | Low intent: {stats['low_intent']}

"""

        report += """
---

## Combined Market Opportunities

"""

        all_opportunities = []
        for result in results:
            all_opportunities.extend(result['analysis'].market_opportunities)

        for i, opp in enumerate(all_opportunities, 1):
            report += f"{i}. {opp}\n"

        report += f"""
---

**Generated at**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info("Summary report generated: %s", summary_file)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(
        description="Reddit Goldmine Finder - Discover customer pain points and purchase intent with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single thread
  python goldmine_finder.py --url "https://www.reddit.com/r/Entrepreneur/comments/xxx/"

  # Analyze an entire subreddit
  python goldmine_finder.py --subreddit Entrepreneur --limit 10

  # Batch analyze multiple URLs
  python goldmine_finder.py --batch urls.txt

  # Specify output directory
  python goldmine_finder.py --subreddit SaaS --output my_analysis/
        """
    )

    parser.add_argument('--url', help='Reddit thread URL to analyze')
    parser.add_argument('--subreddit', help='Subreddit name to analyze')
    parser.add_argument('--limit', type=int, default=10, help='Number of posts to fetch (default: 10)')
    parser.add_argument('--min-comments', type=int, default=5, help='Minimum number of comments (default: 5)')
    parser.add_argument('--batch', help='URL list file (one URL per line)')
    parser.add_argument('--output', default='output', help='Output directory (default: output/)')

    args = parser.parse_args()

    if not any([args.url, args.subreddit, args.batch]):
        parser.print_help()
        sys.exit(1)

    finder = GoldmineFinder(output_dir=args.output)

    try:
        if args.url:
            finder.analyze_single_thread(args.url)

        elif args.subreddit:
            finder.analyze_subreddit(args.subreddit, limit=args.limit, min_comments=args.min_comments)

        elif args.batch:
            with open(args.batch, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            finder.batch_analyze_urls(urls)

        logger.info("=" * 70)
        logger.info("All analyses complete!")
        logger.info("Results saved in %s/", args.output)
        logger.info("=" * 70)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
