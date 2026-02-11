#!/usr/bin/env python3
"""
Demo script - Reddit Goldmine Analyzer usage example
Works without an API key by loading pre-computed sample data.
"""

import json
import os

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")


def demo():
    """Run demo using sample data (no API key required)."""
    print("=" * 70)
    print("Reddit Goldmine Analyzer - Demo")
    print("=" * 70)
    print()

    thread_file = os.path.join(EXAMPLES_DIR, "sample_thread.json")
    analysis_file = os.path.join(EXAMPLES_DIR, "sample_analysis.json")

    try:
        with open(thread_file, "r", encoding="utf-8") as f:
            thread_data = json.load(f)

        with open(analysis_file, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)

        print(f"Loaded sample data: {thread_file}")
        print()
        print(f"Thread title: {thread_data['title']}")
        print(f"Comments: {thread_data['num_comments']}")
        print(f"Score: {thread_data['score']}")
        print()

        print("=" * 70)
        print("Analysis Results (pre-computed, no API key needed)")
        print("=" * 70)
        print()

        pain_points = analysis_data.get("pain_points", [])
        print(f"Pain points found: {len(pain_points)}")
        print()

        # Sort by purchase intent
        intent_order = {"high": 4, "medium": 3, "low": 2, "none": 1}
        sorted_pain_points = sorted(
            pain_points,
            key=lambda x: intent_order.get(x.get("purchase_intent", "none"), 0),
            reverse=True,
        )

        for i, pp in enumerate(sorted_pain_points[:5], 1):
            intent = pp.get("purchase_intent", "none")
            intent_emoji = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW", "none": "NONE"}.get(intent, "NONE")
            print(f"{i}. {pp['description']}")
            print(f"   Purchase Intent: {intent_emoji}")
            print(f"   Category: {pp.get('category', 'N/A')}")
            print()

        print("=" * 70)
        print("Key Insights")
        print("=" * 70)
        print()

        for insight in analysis_data.get("key_insights", []):
            print(f"  - {insight}")

        print()
        print("=" * 70)
        print("Market Opportunities")
        print("=" * 70)
        print()

        for opportunity in analysis_data.get("market_opportunities", []):
            print(f"  - {opportunity}")

        print()
        print("=" * 70)
        print("Demo complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  - Run the Web UI:   streamlit run app.py")
        print("  - Analyze live data: python goldmine_finder.py --url <reddit-url>")
        print()

    except FileNotFoundError as e:
        print(f"Sample data not found: {e}")
        print()
        print("Make sure the examples/ directory exists with sample data files.")
        print()


if __name__ == "__main__":
    demo()
