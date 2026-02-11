#!/usr/bin/env python3
"""
Reddit Goldmine Analyzer - Streamlit Web UI
"""

import json
import os
import streamlit as st

st.set_page_config(
    page_title="Reddit Goldmine Analyzer",
    page_icon="⛏️",
    layout="wide",
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")

# --- Helpers ---

SEVERITY_COLORS = {
    "critical": "#e74c3c",
    "high": "#e67e22",
    "medium": "#f1c40f",
    "low": "#2ecc71",
}

INTENT_LABELS = {
    "high": ("💰💰💰 HIGH", "#27ae60"),
    "medium": ("💰💰 MEDIUM", "#f39c12"),
    "low": ("💰 LOW", "#95a5a6"),
    "none": ("⚫ NONE", "#7f8c8d"),
}


def severity_badge(level: str) -> str:
    color = SEVERITY_COLORS.get(level, "#bdc3c7")
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em;font-weight:600">{level.upper()}</span>'


def intent_badge(level: str) -> str:
    label, color = INTENT_LABELS.get(level, ("⚫ NONE", "#7f8c8d"))
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.85em;font-weight:600">{label}</span>'


def load_sample_analysis():
    path = os.path.join(EXAMPLES_DIR, "sample_analysis.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sample_thread():
    path = os.path.join(EXAMPLES_DIR, "sample_thread.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_analysis(data: dict):
    """Render analysis results in the UI."""
    # --- Metrics row ---
    pain_points = data.get("pain_points", [])
    insights = data.get("key_insights", [])
    opportunities = data.get("market_opportunities", [])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Comments Analyzed", data.get("total_comments", 0))
    col2.metric("Pain Points", len(pain_points))
    col3.metric("Key Insights", len(insights))
    col4.metric("Market Opportunities", len(opportunities))

    st.markdown("---")

    # --- Pain Points ---
    st.subheader("Pain Points Discovered")

    intent_order = {"high": 4, "medium": 3, "low": 2, "none": 1}
    sorted_pps = sorted(
        pain_points,
        key=lambda x: (intent_order.get(x.get("purchase_intent", "none"), 0), x.get("frequency_mentioned", 0)),
        reverse=True,
    )

    for pp in sorted_pps:
        sev = pp.get("severity", "medium")
        intent = pp.get("purchase_intent", "none")
        desc = pp.get("description", "")
        cat = pp.get("category", "")
        freq = pp.get("frequency_mentioned", 0)
        examples = pp.get("example_comments", [])

        st.markdown(
            f"**{desc}**&ensp;{severity_badge(sev)}&ensp;{intent_badge(intent)}",
            unsafe_allow_html=True,
        )
        st.caption(f"Category: {cat} · Mentioned {freq} time(s)")

        if examples:
            with st.expander("Example comments"):
                for ex in examples:
                    st.markdown(f"> {ex}")

    st.markdown("---")

    # --- Key Insights ---
    st.subheader("Key Insights")
    for insight in insights:
        st.markdown(f"- {insight}")

    st.markdown("---")

    # --- Market Opportunities ---
    st.subheader("Market Opportunities")
    for opp in opportunities:
        st.markdown(f"- {opp}")

    st.markdown("---")

    # --- Sentiment ---
    st.subheader("Sentiment Analysis")
    st.info(data.get("sentiment_summary", "N/A"))

    # --- Download ---
    st.download_button(
        label="Download Analysis JSON",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="analysis.json",
        mime="application/json",
    )


# --- Main UI ---

st.title("⛏️ Reddit Goldmine Analyzer")
st.caption("Discover customer pain points, purchase intent & market opportunities from Reddit threads")

mode = st.radio(
    "Choose mode",
    ["Sample Data (no API key needed)", "Live Analysis (requires OpenAI API key)"],
    horizontal=True,
)

if mode.startswith("Sample"):
    st.markdown("### Sample Analysis")
    st.markdown(
        "Explore a pre-analyzed r/Entrepreneur thread. No API key required."
    )

    data = load_sample_analysis()

    st.markdown(f"**Thread**: {data.get('thread_title', '')}")
    render_analysis(data)

else:
    st.markdown("### Live Analysis")

    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    thread_url = st.text_input(
        "Reddit Thread URL",
        placeholder="https://www.reddit.com/r/Entrepreneur/comments/...",
    )

    if st.button("Analyze", type="primary", disabled=not (api_key and thread_url)):
        os.environ["OPENAI_API_KEY"] = api_key

        try:
            from reddit_fetcher import RedditFetcher
            from ai_analyzer import AIAnalyzer

            with st.spinner("Fetching thread data..."):
                fetcher = RedditFetcher()
                thread = fetcher.fetch_thread(thread_url)

            if thread is None:
                st.error("Failed to fetch thread. Please check the URL and try again.")
            else:
                # Convert to dict
                def comment_to_dict(c):
                    return {
                        "id": c.id, "author": c.author, "body": c.body,
                        "score": c.score, "created_utc": c.created_utc,
                        "parent_id": c.parent_id, "gilded": c.gilded,
                        "depth": c.depth,
                        "replies": [comment_to_dict(r) for r in c.replies],
                    }

                thread_dict = {
                    "id": thread.id, "title": thread.title,
                    "author": thread.author, "selftext": thread.selftext,
                    "score": thread.score, "num_comments": thread.num_comments,
                    "created_utc": thread.created_utc, "url": thread.url,
                    "subreddit": thread.subreddit, "upvote_ratio": thread.upvote_ratio,
                    "comments": [comment_to_dict(c) for c in thread.comments],
                }

                with st.spinner("Running AI analysis..."):
                    analyzer = AIAnalyzer()
                    result = analyzer.analyze_thread(thread_dict)

                # Build result dict
                analysis_data = {
                    "thread_id": result.thread_id,
                    "thread_title": result.thread_title,
                    "total_comments": result.total_comments,
                    "pain_points": [
                        {
                            "description": pp.description,
                            "severity": pp.severity,
                            "frequency_mentioned": pp.frequency_mentioned,
                            "example_comments": pp.example_comments,
                            "purchase_intent": pp.purchase_intent,
                            "category": pp.category,
                        }
                        for pp in result.pain_points
                    ],
                    "key_insights": result.key_insights,
                    "market_opportunities": result.market_opportunities,
                    "sentiment_summary": result.sentiment_summary,
                }

                st.success("Analysis complete!")
                st.markdown(f"**Thread**: {result.thread_title}")
                render_analysis(analysis_data)

        except Exception as e:
            st.error(f"Error: {e}")
