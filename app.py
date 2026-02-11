#!/usr/bin/env python3
"""
Reddit Goldmine Analyzer — Web UI
"""

import json
import os
import streamlit as st

st.set_page_config(
    page_title="Reddit Goldmine Analyzer",
    page_icon="⛏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")

# ── Styles ────────────────────────────────────────────────────────────────────

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #F5F0EA;
    --surface: #FFFFFF;
    --text: #2C2520;
    --text-2: #6E645C;
    --text-3: #A69E96;
    --accent: #B5522A;
    --accent-soft: rgba(181,82,42,0.06);
    --green: #4A7A52;
    --amber: #B8862B;
    --red: #B41E1E;
    --border: #E2DAD1;
    --border-lt: #EDE8E2;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% -10%, rgba(181,82,42,0.045), transparent 50%),
        radial-gradient(ellipse at 90% 110%, rgba(74,122,82,0.035), transparent 45%),
        var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
}
.stApp > header { background: transparent !important; }
.block-container { max-width: 760px !important; padding: 2.5rem 1rem 2rem !important; }

h1,h2,h3,h4,h5,h6 { font-family: 'Outfit', sans-serif !important; color: var(--text) !important; }
p, li, span, label, .stMarkdown { color: var(--text) !important; }
hr { border-color: var(--border) !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }

div[data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    gap: 0 !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important;
    margin-bottom: 1.5rem !important;
}
div[data-baseweb="radio"] > div { flex: none !important; }
div[data-baseweb="radio"] label {
    background: transparent !important;
    color: var(--text-3) !important;
    border-radius: 0 !important;
    padding: 6px 0 10px !important;
    margin-right: 28px !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.2s, border-color 0.2s !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}
div[data-baseweb="radio"] label[data-checked="true"],
div[data-baseweb="radio"] label:has(input:checked) {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}
div[data-baseweb="radio"] label span[data-testid="stMarkdownContainer"] p { color: inherit !important; }

.stTextInput > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}
.stTextInput input { color: var(--text) !important; font-family: 'Outfit', sans-serif !important; }
.stTextInput label { color: var(--text-2) !important; font-size: 0.82rem !important; }

.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 0.84rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stDownloadButton > button {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    transition: border-color 0.2s !important;
}
.stDownloadButton > button:hover { border-color: var(--accent) !important; }

.streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    color: var(--text-3) !important;
    font-size: 0.78rem !important;
    padding: 0.2rem 0 !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid var(--border-lt) !important;
    padding-left: 1rem !important;
    margin-left: 2rem !important;
}

.stSpinner > div { color: var(--accent) !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Components ── */

.gm-hero { padding: 0.5rem 0 2rem; }
.gm-hero-title {
    font-family: 'Instrument Serif', serif;
    font-size: 3.4rem;
    font-weight: 400;
    line-height: 1.02;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.03em;
}
.gm-hero-sub {
    font-size: 0.92rem;
    color: var(--text-2);
    margin-top: 0.75rem;
    font-weight: 300;
}

.gm-thread-bar {
    padding: 1rem 0;
    border-top: 1px solid var(--border);
}
.gm-thread-bar-title {
    font-size: 0.88rem;
    color: var(--text);
    font-weight: 500;
    line-height: 1.4;
}
.gm-thread-bar-meta {
    font-size: 0.73rem;
    color: var(--text-3);
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

.gm-stats {
    display: flex;
    gap: 2rem;
    padding: 0.8rem 0 0.5rem;
    flex-wrap: wrap;
}
.gm-stat { display: flex; align-items: baseline; gap: 0.35rem; }
.gm-stat-n {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}
.gm-stat-l { font-size: 0.78rem; color: var(--text-3); }

.gm-section {
    padding: 2.2rem 0 0;
    margin-bottom: 0.4rem;
}
.gm-section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    padding-bottom: 0.55rem;
    border-bottom: 1px solid var(--border);
}

.gm-pp {
    padding: 1rem 0;
    border-bottom: 1px solid var(--border-lt);
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.gm-pp-n {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-3);
    min-width: 22px;
    padding-top: 3px;
}
.gm-pp-body { flex: 1; }
.gm-pp-desc {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.5;
    margin-bottom: 0.45rem;
}
.gm-pp-meta {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
}
.gm-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 3px;
    letter-spacing: 0.02em;
}
.gm-sev-critical { background: rgba(180,30,30,0.08); color: var(--red); }
.gm-sev-high { background: var(--accent-soft); color: var(--accent); }
.gm-sev-medium { background: rgba(184,134,43,0.08); color: var(--amber); }
.gm-sev-low { background: rgba(74,122,82,0.08); color: var(--green); }
.gm-intent {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    color: var(--text-2);
}
.gm-sep { color: var(--border); font-size: 0.7rem; }
.gm-cat { font-size: 0.72rem; color: var(--text-3); }

.gm-list-item {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border-lt);
    font-size: 0.88rem;
    line-height: 1.6;
    color: var(--text);
    display: flex;
    gap: 0.7rem;
}
.gm-list-item:last-child { border-bottom: none; }
.gm-list-marker {
    color: var(--text-3);
    flex-shrink: 0;
    font-size: 0.82rem;
    padding-top: 1px;
}

.gm-quote {
    border-left: 2px solid var(--border);
    padding: 0.8rem 1.2rem;
    margin-top: 0.5rem;
    border-radius: 0 4px 4px 0;
    background: var(--accent-soft);
}
.gm-quote-text {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-size: 1rem;
    color: var(--text-2);
    line-height: 1.7;
}

.gm-footer {
    text-align: left;
    padding: 3rem 0 1rem;
    font-size: 0.7rem;
    color: var(--text-3);
    letter-spacing: 0.02em;
}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

SEV_CLASS = {
    "critical": "gm-sev-critical",
    "high": "gm-sev-high",
    "medium": "gm-sev-medium",
    "low": "gm-sev-low",
}
SEV_LABEL = {"critical": "CRITICAL", "high": "HIGH", "medium": "MED", "low": "LOW"}
INTENT_SYM = {"high": "$$$", "medium": "$$", "low": "$", "none": "—"}


def _html(s):
    st.markdown(s, unsafe_allow_html=True)


def load_sample():
    with open(os.path.join(EXAMPLES_DIR, "sample_analysis.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def render_hero():
    _html(
        '<div class="gm-hero">'
        '<h1 class="gm-hero-title">Reddit Goldmine<br>Analyzer</h1>'
        '<p class="gm-hero-sub">Paste a Reddit thread. See what people want to pay for.</p>'
        '</div>'
    )


def render_thread(data):
    title = data.get("thread_title", "")
    n = data.get("total_comments", 0)
    _html(
        f'<div class="gm-thread-bar">'
        f'<div class="gm-thread-bar-title">{title}</div>'
        f'<div class="gm-thread-bar-meta">{n} comments analyzed</div>'
        f'</div>'
    )


def render_stats(data):
    pp = len(data.get("pain_points", []))
    ins = len(data.get("key_insights", []))
    opp = len(data.get("market_opportunities", []))
    _html(
        '<div class="gm-stats">'
        f'<div class="gm-stat"><span class="gm-stat-n">{pp}</span><span class="gm-stat-l">pain points</span></div>'
        f'<div class="gm-stat"><span class="gm-stat-n">{ins}</span><span class="gm-stat-l">insights</span></div>'
        f'<div class="gm-stat"><span class="gm-stat-n">{opp}</span><span class="gm-stat-l">opportunities</span></div>'
        '</div>'
    )


def render_section(label):
    _html(f'<div class="gm-section"><div class="gm-section-label">{label}</div></div>')


def render_pain_point(pp, idx):
    sev = pp.get("severity", "medium")
    intent = pp.get("purchase_intent", "none")
    desc = pp.get("description", "")
    cat = pp.get("category", "")
    freq = pp.get("frequency_mentioned", 0)
    examples = pp.get("example_comments", [])

    sev_cls = SEV_CLASS.get(sev, "gm-sev-medium")
    sev_lbl = SEV_LABEL.get(sev, "MED")
    intent_sym = INTENT_SYM.get(intent, "—")
    num = f"{idx:02d}"

    _html(
        f'<div class="gm-pp">'
        f'<div class="gm-pp-n">{num}</div>'
        f'<div class="gm-pp-body">'
        f'<div class="gm-pp-desc">{desc}</div>'
        f'<div class="gm-pp-meta">'
        f'<span class="gm-tag {sev_cls}">{sev_lbl}</span>'
        f'<span class="gm-sep">/</span>'
        f'<span class="gm-intent">{intent_sym}</span>'
        f'<span class="gm-sep">/</span>'
        f'<span class="gm-cat">{cat}</span>'
        f'<span class="gm-sep">&middot;</span>'
        f'<span class="gm-cat">{freq}&times;</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    if examples:
        with st.expander(f"Show {len(examples)} quotes"):
            for ex in examples:
                st.markdown(f"> {ex}")


def render_insights(items):
    if not items:
        return
    rows = []
    for item in items:
        rows.append(
            f'<div class="gm-list-item">'
            f'<span class="gm-list-marker">&mdash;</span>'
            f'<span>{item}</span>'
            f'</div>'
        )
    _html("".join(rows))


def render_opportunities(items):
    if not items:
        return
    rows = []
    for item in items:
        rows.append(
            f'<div class="gm-list-item">'
            f'<span class="gm-list-marker">&rarr;</span>'
            f'<span>{item}</span>'
            f'</div>'
        )
    _html("".join(rows))


def render_sentiment(text):
    if not text:
        return
    _html(
        f'<div class="gm-quote">'
        f'<div class="gm-quote-text">{text}</div>'
        f'</div>'
    )


def render_analysis(data):
    render_thread(data)
    render_stats(data)

    pain_points = data.get("pain_points", [])
    insights = data.get("key_insights", [])
    opportunities = data.get("market_opportunities", [])
    sentiment = data.get("sentiment_summary", "")

    render_section("Pain Points")
    intent_order = {"high": 4, "medium": 3, "low": 2, "none": 1}
    sorted_pps = sorted(
        pain_points,
        key=lambda x: (intent_order.get(x.get("purchase_intent", "none"), 0), x.get("frequency_mentioned", 0)),
        reverse=True,
    )
    for i, pp in enumerate(sorted_pps, 1):
        render_pain_point(pp, i)

    render_section("Key Insights")
    render_insights(insights)

    render_section("Market Opportunities")
    render_opportunities(opportunities)

    render_section("Sentiment")
    render_sentiment(sentiment)

    _html('<div style="height:1.5rem"></div>')
    st.download_button(
        label="Download analysis (.json)",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="analysis.json",
        mime="application/json",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

render_hero()

mode = st.radio(
    "mode",
    ["Sample Data", "Live Analysis"],
    horizontal=True,
    label_visibility="collapsed",
)

if mode == "Sample Data":
    render_analysis(load_sample())
else:
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    url = st.text_input("Reddit Thread URL", placeholder="https://www.reddit.com/r/...")

    if st.button("Analyze", type="primary", disabled=not (api_key and url)):
        os.environ["OPENAI_API_KEY"] = api_key
        try:
            from reddit_fetcher import RedditFetcher
            from ai_analyzer import AIAnalyzer

            with st.spinner("Fetching thread..."):
                fetcher = RedditFetcher()
                thread = fetcher.fetch_thread(url)

            if thread is None:
                st.error("Could not fetch thread. Check the URL.")
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

                with st.spinner("Analyzing..."):
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
                render_analysis(analysis_data)

        except Exception as e:
            st.error(str(e))

_html('<div class="gm-footer">Reddit Goldmine Analyzer &mdash; MIT License</div>')
