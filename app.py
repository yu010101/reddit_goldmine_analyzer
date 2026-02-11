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
    initial_sidebar_state="collapsed",
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")

# ── Custom CSS ──────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Playfair+Display:wght@700;900&display=swap');

:root {
    --gold: #D4A017;
    --gold-light: #F2CC5B;
    --gold-dim: #8B6914;
    --bg-deep: #0B0E11;
    --bg-card: #13171C;
    --bg-surface: #0F1216;
    --text-primary: #E8E4DD;
    --text-secondary: #8A8680;
    --text-muted: #5C5955;
    --border: #1E2329;
}

.stApp {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stApp > header { background-color: transparent !important; }
.block-container {
    max-width: 960px !important;
    padding-top: 2rem !important;
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
}
p, li, span, label, .stMarkdown {
    color: var(--text-primary) !important;
}
hr { border-color: var(--border) !important; opacity: 0.5 !important; }

#MainMenu, footer, .stDeployButton { display: none !important; }

div[data-baseweb="radio"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 0 !important;
}
div[data-baseweb="radio"] > div { flex: 1 !important; }
div[data-baseweb="radio"] label {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}
div[data-baseweb="radio"] label[data-checked="true"],
div[data-baseweb="radio"] label:has(input:checked) {
    background: var(--gold-dim) !important;
    color: var(--gold-light) !important;
}
div[data-baseweb="radio"] label span[data-testid="stMarkdownContainer"] p {
    color: inherit !important;
}

.stTextInput > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}
.stTextInput input { color: var(--text-primary) !important; }
.stTextInput label { color: var(--text-secondary) !important; font-size: 0.85rem !important; }

.stButton > button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
    color: #0B0E11 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.55rem 2rem !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    filter: brightness(1.15) !important;
    transform: translateY(-1px) !important;
}

.stDownloadButton > button {
    background: var(--bg-card) !important;
    color: var(--gold-light) !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.25s ease !important;
}
.stDownloadButton > button:hover {
    background: var(--gold-dim) !important;
    color: #0B0E11 !important;
}

.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    border: 1px solid var(--border) !important;
}
.streamlit-expanderContent {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

.stSpinner > div { color: var(--gold) !important; }
.stAlert { border-radius: 10px !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.gm-metric-row { display: flex; gap: 12px; margin: 1.2rem 0 1.8rem; }
.gm-metric-card {
    flex: 1;
    background: #13171C;
    border: 1px solid #1E2329;
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.gm-metric-card .icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
.gm-metric-card .value { font-size: 1.8rem; font-weight: 700; color: #E8E4DD; line-height: 1; }
.gm-metric-card .label { font-size: 0.75rem; color: #5C5955; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }

.gm-pp-card {
    background: #13171C;
    border: 1px solid #1E2329;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.gm-pp-desc { font-size: 0.95rem; font-weight: 600; color: #E8E4DD; line-height: 1.45; margin-bottom: 0.6rem; }
.gm-pp-badges { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.gm-badge {
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    display: inline-block;
}
.gm-badge-critical { background: rgba(220,38,38,0.18); color: #DC2626; }
.gm-badge-high-sev { background: rgba(234,88,12,0.18); color: #EA580C; }
.gm-badge-medium-sev { background: rgba(202,138,4,0.18); color: #CA8A04; }
.gm-badge-low-sev { background: rgba(22,163,74,0.18); color: #16A34A; }
.gm-badge-high-int { background: rgba(22,163,74,0.18); color: #16A34A; }
.gm-badge-medium-int { background: rgba(202,138,4,0.18); color: #CA8A04; }
.gm-badge-low-int { background: rgba(107,114,128,0.18); color: #6B7280; }
.gm-badge-none-int { background: rgba(55,65,81,0.18); color: #374151; }
.gm-pp-meta { color: #5C5955; font-size: 0.75rem; }

.gm-section-hdr {
    display: flex; align-items: center; gap: 0.6rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #1E2329;
}
.gm-section-hdr .icon { font-size: 1.3rem; }
.gm-section-hdr .title { font-size: 1.15rem; font-weight: 700; color: #E8E4DD; letter-spacing: -0.01em; }

.gm-list-card {
    background: #13171C;
    border: 1px solid #1E2329;
    border-radius: 12px;
    padding: 0.3rem 1.4rem;
}
.gm-list-item {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 0.75rem 0;
    border-bottom: 1px solid #1E2329;
}
.gm-list-item:last-child { border-bottom: none; }
.gm-list-dot {
    width: 5px; min-width: 5px; height: 5px;
    border-radius: 50%;
    margin-top: 0.55rem;
    flex-shrink: 0;
}
.gm-list-text { font-size: 0.9rem; color: #C8C4BD; line-height: 1.55; }

.gm-sentiment {
    background: linear-gradient(135deg, #13171C, #171C22);
    border: 1px solid #1E2329;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-top: 0.5rem;
}
.gm-sentiment-text { font-size: 0.9rem; color: #A8A49D; line-height: 1.65; font-style: italic; }

.gm-thread-info {
    background: #13171C;
    border: 1px solid #1E2329;
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin: 0.8rem 0 0.3rem;
}
.gm-thread-label { font-size: 0.7rem; color: #5C5955; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.3rem; }
.gm-thread-title { font-size: 0.92rem; color: #C8C4BD; }

.gm-footer {
    text-align: center;
    padding: 3rem 0 1.5rem;
    color: #3A3835;
    font-size: 0.75rem;
    letter-spacing: 0.03em;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

SEVERITY_BADGE = {
    "critical": ("CRITICAL", "gm-badge-critical", "🔴"),
    "high":     ("HIGH",     "gm-badge-high-sev", "🟠"),
    "medium":   ("MEDIUM",   "gm-badge-medium-sev", "🟡"),
    "low":      ("LOW",      "gm-badge-low-sev", "🟢"),
}

INTENT_BADGE = {
    "high":   ("HIGH",   "gm-badge-high-int"),
    "medium": ("MEDIUM", "gm-badge-medium-int"),
    "low":    ("LOW",    "gm-badge-low-int"),
    "none":   ("NONE",   "gm-badge-none-int"),
}

SEV_BORDER = {
    "critical": "#DC2626",
    "high": "#EA580C",
    "medium": "#CA8A04",
    "low": "#16A34A",
}


def _html(markup):
    """Render HTML without markdown code-block interference."""
    st.markdown(markup, unsafe_allow_html=True)


def load_sample_analysis():
    with open(os.path.join(EXAMPLES_DIR, "sample_analysis.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def render_hero():
    _html(
'<div style="text-align:center; padding:2.5rem 0 1rem;">'
'<div style="font-size:3rem; margin-bottom:0.2rem;">⛏️</div>'
'<h1 style="font-family:Playfair Display,serif !important; font-size:2.6rem !important;'
' font-weight:900 !important; letter-spacing:-0.02em; margin:0 !important;'
' color:#D4A017 !important; line-height:1.15;">'
'Reddit Goldmine Analyzer</h1>'
'<p style="color:#8A8680 !important; font-size:1.05rem; margin-top:0.6rem;'
' font-weight:300; letter-spacing:0.01em;">Turn any Reddit thread into market intelligence</p>'
'</div>'
    )


def render_metrics(data):
    pain_points = data.get("pain_points", [])
    insights = data.get("key_insights", [])
    opportunities = data.get("market_opportunities", [])

    metrics = [
        ("💬", "Comments", data.get("total_comments", 0)),
        ("🎯", "Pain Points", len(pain_points)),
        ("💡", "Insights", len(insights)),
        ("🚀", "Opportunities", len(opportunities)),
    ]

    cards = []
    for icon, label, value in metrics:
        cards.append(
            f'<div class="gm-metric-card">'
            f'<div class="icon">{icon}</div>'
            f'<div class="value">{value}</div>'
            f'<div class="label">{label}</div>'
            f'</div>'
        )

    _html('<div class="gm-metric-row">' + "".join(cards) + '</div>')


def render_pain_point_card(pp):
    sev = pp.get("severity", "medium")
    intent = pp.get("purchase_intent", "none")
    desc = pp.get("description", "")
    cat = pp.get("category", "")
    freq = pp.get("frequency_mentioned", 0)
    examples = pp.get("example_comments", [])

    sev_label, sev_cls, sev_dot = SEVERITY_BADGE.get(sev, ("MEDIUM", "gm-badge-medium-sev", "🟡"))
    int_label, int_cls = INTENT_BADGE.get(intent, ("NONE", "gm-badge-none-int"))
    border_color = SEV_BORDER.get(sev, "#CA8A04")

    _html(
        f'<div class="gm-pp-card" style="border-left:3px solid {border_color};">'
        f'<div class="gm-pp-desc">{desc}</div>'
        f'<div class="gm-pp-badges">'
        f'<span class="gm-badge {sev_cls}">{sev_dot} {sev_label}</span>'
        f'<span class="gm-badge {int_cls}">💰 INTENT: {int_label}</span>'
        f'<span class="gm-pp-meta">{cat} · {freq}× mentioned</span>'
        f'</div>'
        f'</div>'
    )

    if examples:
        with st.expander(f"View {len(examples)} comment(s)", expanded=False):
            for ex in examples:
                st.markdown(f"> _{ex}_")


def render_section_header(icon, title):
    _html(
        f'<div class="gm-section-hdr">'
        f'<span class="icon">{icon}</span>'
        f'<span class="title">{title}</span>'
        f'</div>'
    )


def render_list_card(items, accent="#D4A017"):
    if not items:
        return
    rows = []
    for item in items:
        rows.append(
            f'<div class="gm-list-item">'
            f'<div class="gm-list-dot" style="background:{accent};"></div>'
            f'<div class="gm-list-text">{item}</div>'
            f'</div>'
        )
    _html('<div class="gm-list-card">' + "".join(rows) + '</div>')


def render_sentiment(text):
    if not text:
        return
    _html(
        f'<div class="gm-sentiment">'
        f'<div class="gm-sentiment-text">"{text}"</div>'
        f'</div>'
    )


def render_thread_info(title):
    _html(
        f'<div class="gm-thread-info">'
        f'<div class="gm-thread-label">Analyzing Thread</div>'
        f'<div class="gm-thread-title">🧵 {title}</div>'
        f'</div>'
    )


def render_analysis(data):
    render_metrics(data)

    pain_points = data.get("pain_points", [])
    insights = data.get("key_insights", [])
    opportunities = data.get("market_opportunities", [])
    sentiment = data.get("sentiment_summary", "")

    # Pain Points
    render_section_header("🎯", "Pain Points")
    intent_order = {"high": 4, "medium": 3, "low": 2, "none": 1}
    sorted_pps = sorted(
        pain_points,
        key=lambda x: (intent_order.get(x.get("purchase_intent", "none"), 0), x.get("frequency_mentioned", 0)),
        reverse=True,
    )
    for pp in sorted_pps:
        render_pain_point_card(pp)

    # Key Insights
    render_section_header("💡", "Key Insights")
    render_list_card(insights, "#D4A017")

    # Market Opportunities
    render_section_header("🚀", "Market Opportunities")
    render_list_card(opportunities, "#16A34A")

    # Sentiment
    render_section_header("📊", "Sentiment")
    render_sentiment(sentiment)

    # Download
    _html('<div style="height:1.5rem"></div>')
    st.download_button(
        label="⬇  Download Analysis JSON",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="analysis.json",
        mime="application/json",
    )


# ── Main ─────────────────────────────────────────────────────────────────────

render_hero()

mode = st.radio(
    "mode",
    ["Sample Data", "Live Analysis"],
    horizontal=True,
    label_visibility="collapsed",
)

if mode == "Sample Data":
    data = load_sample_analysis()
    render_thread_info(data.get("thread_title", ""))
    render_analysis(data)

else:
    _html('<div style="height:0.5rem"></div>')
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    thread_url = st.text_input("Reddit Thread URL", placeholder="https://www.reddit.com/r/...")

    if st.button("Analyze", type="primary", disabled=not (api_key and thread_url)):
        os.environ["OPENAI_API_KEY"] = api_key

        try:
            from reddit_fetcher import RedditFetcher
            from ai_analyzer import AIAnalyzer

            with st.spinner("Fetching thread..."):
                fetcher = RedditFetcher()
                thread = fetcher.fetch_thread(thread_url)

            if thread is None:
                st.error("Could not fetch thread. Check the URL and try again.")
            else:
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

                render_thread_info(result.thread_title)
                render_analysis(analysis_data)

        except Exception as e:
            st.error(f"Error: {e}")

# Footer
_html('<div class="gm-footer">Reddit Goldmine Analyzer · Open Source · MIT License</div>')
