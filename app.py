#!/usr/bin/env python3
"""
Reddit Goldmine Analyzer — Web UI
"""

import html as _html_mod
import json
import os
import re
import time as _time
import streamlit as st

st.set_page_config(
    page_title="Reddit Goldmine Analyzer",
    page_icon="⛏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")

SAMPLE_CATALOG = [
    {"id": "saas", "file": "sample_analysis_saas.json",
     "label_en": "r/SaaS \u2014 Building a SaaS", "label_ja": "r/SaaS \u2014 SaaS\u69cb\u7bc9"},
    {"id": "sideproject", "file": "sample_analysis_sideproject.json",
     "label_en": "r/SideProject \u2014 First 100 Users", "label_ja": "r/SideProject \u2014 \u6700\u521d\u306e100\u30e6\u30fc\u30b6\u30fc"},
    {"id": "startups", "file": "sample_analysis_startups.json",
     "label_en": "r/startups \u2014 Tools for Early-Stage", "label_ja": "r/startups \u2014 \u30a2\u30fc\u30ea\u30fc\u30b9\u30c6\u30fc\u30b8\u30c4\u30fc\u30eb"},
    {"id": "entrepreneur", "file": "sample_analysis.json",
     "label_en": "r/Entrepreneur \u2014 Podcast Discussion", "label_ja": "r/Entrepreneur \u2014 \u30dd\u30c3\u30c9\u30ad\u30e3\u30b9\u30c8\u8b70\u8ad6"},
]

# ── i18n ──────────────────────────────────────────────────────────────────────

T = {
    "en": {
        "hero_title": 'Reddit <span class="gm-hero-accent">Goldmine</span><br>Analyzer',
        "hero_sub": "Find real problems people will pay you to solve — extracted from Reddit discussions by AI.",
        "tab_sample": "Sample Data",
        "tab_discover": "Discover",
        "tab_live": "Live Analysis",
        "sample_hint": 'Viewing a sample analysis. Switch to \u201c{tab_live}\u201d to analyze your own thread.',
        "label_api_key": "OpenAI API Key",
        "label_url": "Reddit Thread URL",
        "btn_analyze": "Analyze",
        "spinner_fetch": "Fetching thread...",
        "spinner_analyze": "Analyzing with AI...",
        "status_fetch": "Fetching thread from Reddit",
        "status_parse": "Parsing {n} comments",
        "status_ai": "Running AI analysis",
        "status_done": "Analysis complete",
        "status_browse": "Loading threads from r/{subreddit}",
        "err_fetch": "Could not fetch thread. Check the URL.",
        "sec_pain": "Pain Points",
        "sec_pain_sub": "What people are frustrated about — ranked by severity and purchase intent",
        "sec_insight": "Key Insights",
        "sec_insight_sub": "Recurring themes and hidden patterns across the discussion",
        "sec_opp": "Market Opportunities",
        "sec_opp_sub": "Concrete product/service ideas people would pay for",
        "sec_sentiment": "Sentiment",
        "sec_sentiment_sub": "Overall mood of the discussion",
        "show_quotes": "Show {n} quotes",
        "btn_download": "Download analysis (.json)",
        "meta_fmt": "{n} comments \u2192 {pp} pain points, {ins} insights, {opp} opportunities",
        "guide_step1": "Enter your OpenAI API key",
        "guide_step2": "Paste a Reddit thread URL",
        "guide_step3": "Click Analyze",
        "how_title": "What You Get",
        "how_desc": "Pick any Reddit thread where people discuss problems. AI reads every comment and extracts:<br><b>Pain Points</b> — what people are frustrated about, ranked by severity and purchase intent<br><b>Key Insights</b> — recurring themes and hidden patterns across the discussion<br><b>Market Opportunities</b> — concrete product/service ideas people would pay for",
        "how_sample": "Below is a real sample analysis. Scroll through to see what kind of insights you get, then switch to \u201c{tab_live}\u201d to analyze your own thread.",
        "how_live": "Enter your OpenAI API key and paste any Reddit thread URL. The AI will read through all comments and generate a structured report in seconds.",
        "err_invalid_url": "Please enter a valid Reddit thread URL (e.g. https://www.reddit.com/r/subreddit/comments/...)",
        "err_invalid_key": "API key format is invalid. It should start with \"sk-\".",
        "err_analysis": "AI analysis failed: {detail}",
        "warn_comment_limit": "This thread has {total} comments but only the first {analyzed} were analyzed.",
        "discover_how_title": "Find Threads to Analyze",
        "discover_how_desc": "Don\u2019t have a URL yet? Browse popular subreddits here. Find a discussion with lots of comments, then click \u201cAnalyze\u201d to extract pain points and opportunities from it.",
        "discover_related": "More threads from r/{subreddit}",
        "discover_subreddit_label": "Subreddit",
        "discover_sort_label": "Sort",
        "discover_time_label": "Period",
        "discover_btn_browse": "Browse",
        "discover_btn_analyze": "Analyze \u00bb",
        "discover_no_results": "No threads found with 5+ comments. Try a different subreddit or sort.",
        "discover_popular": "Popular subreddits",
        "discover_select_thread": "Select a thread",
        "discover_results_count": "{n} threads with 5+ comments",
        "discover_from_last": "Showing threads from your last analysis",
        "discover_err_fetch": "Could not fetch threads from r/{subreddit}. Please try again.",
        "discover_err_invalid_sub": "Subreddit name can only contain letters, numbers, and underscores.",
        "discover_empty_hint": "Click a subreddit above or type one below to start browsing.",
        "sample_select_label": "Choose an analysis",
        "sample_key_finding": "Key Finding",
        "sample_stats_comments": "Comments",
        "sample_stats_pain_points": "Pain Points",
        "sample_stats_high_intent": "High Intent",
        "footer": "MIT License",
    },
    "ja": {
        "hero_title": 'Reddit <span class="gm-hero-accent">Goldmine</span><br>Analyzer',
        "hero_sub": "Redditの議論からAIが「人がお金を払ってでも解決したい課題」を自動抽出。",
        "tab_sample": "\u30b5\u30f3\u30d7\u30eb\u30c7\u30fc\u30bf",
        "tab_discover": "\u30b9\u30ec\u30c3\u30c9\u63a2\u7d22",
        "tab_live": "\u30e9\u30a4\u30d6\u5206\u6790",
        "sample_hint": '\u30b5\u30f3\u30d7\u30eb\u5206\u6790\u3092\u8868\u793a\u4e2d\u3002\u81ea\u5206\u306e\u30b9\u30ec\u30c3\u30c9\u3092\u5206\u6790\u3059\u308b\u306b\u306f\u300c{tab_live}\u300d\u30bf\u30d6\u3078\u3002',
        "label_api_key": "OpenAI API\u30ad\u30fc",
        "label_url": "Reddit\u30b9\u30ec\u30c3\u30c9URL",
        "btn_analyze": "\u5206\u6790\u3059\u308b",
        "spinner_fetch": "\u30b9\u30ec\u30c3\u30c9\u53d6\u5f97\u4e2d\u2026",
        "spinner_analyze": "AI\u5206\u6790\u4e2d\u2026",
        "status_fetch": "Reddit\u304b\u3089\u30b9\u30ec\u30c3\u30c9\u3092\u53d6\u5f97\u4e2d",
        "status_parse": "{n}\u4ef6\u306e\u30b3\u30e1\u30f3\u30c8\u3092\u89e3\u6790\u4e2d",
        "status_ai": "AI\u5206\u6790\u3092\u5b9f\u884c\u4e2d",
        "status_done": "\u5206\u6790\u5b8c\u4e86",
        "status_browse": "r/{subreddit}\u306e\u30b9\u30ec\u30c3\u30c9\u3092\u8aad\u307f\u8fbc\u307f\u4e2d",
        "err_fetch": "\u30b9\u30ec\u30c3\u30c9\u3092\u53d6\u5f97\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002URL\u3092\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "sec_pain": "ペインポイント",
        "sec_pain_sub": "ユーザーが不満に思っていること。深刻度・購買意欲つき",
        "sec_insight": "主要インサイト",
        "sec_insight_sub": "議論に隠れたパターンや繰り返し出るテーマ",
        "sec_opp": "市場機会",
        "sec_opp_sub": "人がお金を払いそうな具体的なプロダクト・サービスのアイデア",
        "sec_sentiment": "センチメント",
        "sec_sentiment_sub": "議論全体のムード",
        "show_quotes": "{n}\u4ef6\u306e\u5f15\u7528\u3092\u8868\u793a",
        "btn_download": "\u5206\u6790\u7d50\u679c\u3092\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9 (.json)",
        "meta_fmt": "{n}\u4ef6\u306e\u30b3\u30e1\u30f3\u30c8 \u2192 {pp}\u4ef6\u306e\u8ab2\u984c, {ins}\u4ef6\u306e\u30a4\u30f3\u30b5\u30a4\u30c8, {opp}\u4ef6\u306e\u6a5f\u4f1a",
        "guide_step1": "OpenAI APIキーを入力",
        "guide_step2": "RedditスレッドのURLを貼り付け",
        "guide_step3": "「分析する」をクリック",
        "how_title": "何がわかるの？",
        "how_desc": "Redditスレッドを選ぶだけ。AIが全コメントを読み、以下を自動抽出します：<br><b>ペインポイント</b> — ユーザーが不満に思っていること。深刻度・購買意欲つき<br><b>主要インサイト</b> — 議論に隠れたパターンや繰り返し出るテーマ<br><b>市場機会</b> — 人がお金を払いそうな具体的なプロダクト・サービスのアイデア",
        "how_sample": "下のサンプル分析を見れば、どんなレポートが得られるか分かります。自分のスレッドを分析するには「{tab_live}」タブへ。",
        "how_live": "OpenAI APIキーとRedditスレッドURLを入力するだけ。AIが全コメントを読み、数秒で構造化レポートを生成します。",
        "err_invalid_url": "有効なRedditスレッドURLを入力してください（例: https://www.reddit.com/r/subreddit/comments/...）",
        "err_invalid_key": "APIキーの形式が正しくありません。「sk-」で始まる必要があります。",
        "err_analysis": "AI分析に失敗しました: {detail}",
        "warn_comment_limit": "このスレッドには{total}件のコメントがありますが、先頭{analyzed}件のみ分析しました。",
        "discover_how_title": "分析するスレッドを探す",
        "discover_how_desc": "URLが手元にない？ここからサブレディットを探索できます。コメントが多いスレッドを選んで「分析する」をクリックすれば、課題と市場機会を自動抽出します。",
        "discover_related": "r/{subreddit}\u306e\u4ed6\u306e\u30b9\u30ec\u30c3\u30c9",
        "discover_subreddit_label": "\u30b5\u30d6\u30ec\u30c7\u30a3\u30c3\u30c8",
        "discover_sort_label": "\u30bd\u30fc\u30c8",
        "discover_time_label": "\u671f\u9593",
        "discover_btn_browse": "\u95b2\u89a7",
        "discover_btn_analyze": "\u5206\u6790\u3059\u308b \u00bb",
        "discover_no_results": "\u30b3\u30e1\u30f3\u30c85\u4ef6\u4ee5\u4e0a\u306e\u30b9\u30ec\u30c3\u30c9\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002\u5225\u306e\u30b5\u30d6\u30ec\u30c7\u30a3\u30c3\u30c8\u3084\u30bd\u30fc\u30c8\u3092\u8a66\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "discover_popular": "\u4eba\u6c17\u306e\u30b5\u30d6\u30ec\u30c7\u30a3\u30c3\u30c8",
        "discover_select_thread": "\u30b9\u30ec\u30c3\u30c9\u3092\u9078\u629e",
        "discover_results_count": "\u30b3\u30e1\u30f3\u30c85\u4ef6\u4ee5\u4e0a\u306e\u30b9\u30ec\u30c3\u30c9: {n}\u4ef6",
        "discover_from_last": "\u524d\u56de\u306e\u5206\u6790\u304b\u3089\u95a2\u9023\u30b9\u30ec\u30c3\u30c9\u3092\u8868\u793a\u4e2d",
        "discover_err_fetch": "r/{subreddit}\u306e\u30b9\u30ec\u30c3\u30c9\u3092\u53d6\u5f97\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002\u3082\u3046\u4e00\u5ea6\u304a\u8a66\u3057\u304f\u3060\u3055\u3044\u3002",
        "discover_err_invalid_sub": "\u30b5\u30d6\u30ec\u30c7\u30a3\u30c3\u30c8\u540d\u306f\u82f1\u6570\u5b57\u3068\u30a2\u30f3\u30c0\u30fc\u30b9\u30b3\u30a2\u306e\u307f\u4f7f\u7528\u3067\u304d\u307e\u3059\u3002",
        "discover_empty_hint": "\u4e0a\u306e\u30b5\u30d6\u30ec\u30c7\u30a3\u30c3\u30c8\u3092\u30af\u30ea\u30c3\u30af\u3059\u308b\u304b\u3001\u4e0b\u306b\u540d\u524d\u3092\u5165\u529b\u3057\u3066\u63a2\u7d22\u3092\u59cb\u3081\u307e\u3057\u3087\u3046\u3002",
        "sample_select_label": "\u5206\u6790\u3092\u9078\u629e",
        "sample_key_finding": "\u6ce8\u76ee\u306e\u767a\u898b",
        "sample_stats_comments": "\u30b3\u30e1\u30f3\u30c8\u6570",
        "sample_stats_pain_points": "\u8ab2\u984c\u6570",
        "sample_stats_high_intent": "\u8cfc\u8cb7\u610f\u6b32\u9ad8",
        "footer": "MIT License",
    },
}

if "lang" not in st.session_state:
    st.session_state.lang = "en"


def t(key, **kwargs):
    """Return translated string for current language."""
    text = T[st.session_state.lang].get(key, T["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# ── Styles ────────────────────────────────────────────────────────────────────

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #F4F3F0;
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
    background: radial-gradient(ellipse at 15% 0%, rgba(140,120,100,0.04), transparent 40%), var(--bg) !important;
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
    background: #fff !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}
.stTextInput input { color: var(--text) !important; font-family: 'Outfit', sans-serif !important; }
.stTextInput label { color: var(--text-2) !important; font-size: 0.82rem !important; }
.stSelectbox [data-baseweb="select"] { color: var(--text) !important; }
.stSelectbox [data-baseweb="select"] * { color: var(--text) !important; }
.stSelectbox label { color: var(--text-2) !important; font-size: 0.82rem !important; }

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

/* Expander as text link */
div[data-testid="stExpander"] { border: none !important; }
div[data-testid="stExpander"] details { border: none !important; background: none !important; }
div[data-testid="stExpander"] summary {
    padding: 0.1rem 0 0.3rem !important;
    gap: 0.3rem !important;
    border: none !important;
    background: none !important;
}
div[data-testid="stExpander"] summary span p {
    font-size: 0.73rem !important;
    color: var(--accent) !important;
}
div[data-testid="stExpander"] summary:hover span p {
    text-decoration: underline !important;
    text-underline-offset: 2px !important;
}
div[data-testid="stExpander"] summary svg {
    width: 10px !important;
    height: 10px !important;
    stroke: var(--accent) !important;
}
div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    border: none !important;
    background: none !important;
    border-left: 1.5px solid var(--border-lt) !important;
    padding: 0.4rem 0 0.4rem 1rem !important;
    margin-left: 0.3rem !important;
}
.streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    color: var(--accent) !important;
    font-size: 0.73rem !important;
    padding: 0.1rem 0 !important;
}
.streamlit-expanderContent {
    background: transparent !important;
    border: none !important;
    border-left: 1.5px solid var(--border-lt) !important;
    padding-left: 1rem !important;
    margin-left: 0.3rem !important;
}

.stSpinner > div { color: var(--accent) !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* ── Hero ── */

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
.gm-hero-title::before {
    content: '';
    display: block;
    width: 28px;
    height: 3px;
    background: var(--accent);
    margin-bottom: 0.8rem;
}
.gm-hero-accent { color: var(--accent); }
.gm-hero-sub {
    font-size: 0.92rem;
    color: var(--text-2);
    margin-top: 0.75rem;
    font-weight: 300;
}

/* ── Thread bar ── */

.gm-thread-bar {
    padding: 1rem 0 0.3rem;
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

/* ── Section header variants ── */

.gm-sec-a { padding-top: 1.5rem; margin-bottom: 0.4rem; }
.gm-sec-a .gm-sec-l {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    padding: 0.5rem 0 0.5rem;
    border-bottom: 1px solid var(--border);
    border-top: 3px solid var(--accent);
}

.gm-sec-b { padding-top: 2.5rem; margin-bottom: 0.5rem; }
.gm-sec-b .gm-sec-l {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-size: 1.15rem;
    color: var(--text-2);
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-lt);
    font-weight: 400;
}

.gm-sec-c { padding-top: 2rem; margin-bottom: 0.4rem; }
.gm-sec-c .gm-sec-l {
    font-size: 0.8rem;
    color: var(--text-2);
    padding-bottom: 0.4rem;
    font-weight: 500;
}

.gm-sec-d { padding-top: 2.8rem; margin-bottom: 0.2rem; }
.gm-sec-d .gm-sec-l {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
}
.gm-sec-sub {
    font-size: 0.74rem;
    color: var(--text-3);
    font-weight: 400;
    margin-top: 0.2rem;
}

/* ── Pain points ── */

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
.gm-pp-feat .gm-pp-n { color: var(--accent); font-size: 0.82rem; }
.gm-pp-feat .gm-pp-desc { font-size: 0.95rem; font-weight: 600; }

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

/* ── Lists ── */

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
.gm-list-marker { color: var(--text-3); flex-shrink: 0; font-size: 0.82rem; padding-top: 1px; }

/* ── Sentiment ── */

.gm-quote {
    border-left: 2px solid var(--accent);
    padding: 0.8rem 1.2rem;
    margin-top: 0.5rem;
    border-radius: 0 4px 4px 0;
}
.gm-quote-text {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-size: 1.05rem;
    color: var(--text-2);
    line-height: 1.7;
}

/* ── Language toggle ── */

.gm-lang-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: -0.3rem;
}
.gm-lang-row div[data-baseweb="radio"] {
    border-bottom: none !important;
    margin-bottom: 0 !important;
    gap: 0 !important;
    justify-content: flex-end !important;
}
.gm-lang-row div[data-baseweb="radio"] label {
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    color: var(--text-3) !important;
    margin-right: 0 !important;
    margin-left: 2px !important;
    padding: 4px 10px !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    border-bottom: 1px solid var(--border) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.02em !important;
}
.gm-lang-row div[data-baseweb="radio"] label[data-checked="true"],
.gm-lang-row div[data-baseweb="radio"] label:has(input:checked) {
    color: var(--accent) !important;
    border-color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: var(--accent-soft) !important;
}

/* ── Guide / hint ── */

.gm-hint {
    font-size: 0.78rem;
    color: var(--text-3);
    margin: -0.5rem 0 1.2rem;
    font-weight: 300;
}
.gm-guide {
    font-size: 0.8rem;
    color: var(--text-3);
    margin-bottom: 1.5rem;
    line-height: 1.8;
    font-weight: 300;
}
.gm-guide-step {
    display: flex;
    gap: 0.6rem;
    align-items: baseline;
}
.gm-guide-n {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--accent);
    flex-shrink: 0;
}

/* ── How-to box ── */

.gm-how {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.5rem;
    background: rgba(255,255,255,0.5);
}
.gm-how-title {
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.4rem;
}
.gm-how-body {
    font-size: 0.84rem;
    color: var(--text-2);
    line-height: 1.65;
    font-weight: 300;
}

/* ── Discover tab ── */

/* Pill buttons: target all non-primary st.buttons (only pills are secondary) */
[data-testid="stHorizontalBlock"] .stButton > button:not([kind="primary"]) {
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 4px 14px !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    min-height: 0 !important;
    line-height: 1.4 !important;
}
[data-testid="stHorizontalBlock"] .stButton > button:not([kind="primary"]):hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(181,82,42,0.04) !important;
    opacity: 1 !important;
}

.gm-discover-card {
    padding: 0.65rem 0.6rem;
    margin: 0 -0.6rem;
    border-bottom: 1px solid var(--border-lt);
}
.gm-discover-card .gm-card-num {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-3);
    min-width: 1.5rem;
    vertical-align: top;
    padding-top: 0.1rem;
}
.gm-discover-title {
    font-size: 0.88rem;
    font-weight: 500;
    line-height: 1.45;
    margin-bottom: 0.2rem;
}
.gm-discover-title a {
    color: var(--text);
    text-decoration: none;
}
.gm-discover-title a:hover {
    color: var(--accent);
}
.gm-discover-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-3);
    padding-left: 1.5rem;
}
.gm-discover-hint {
    font-size: 0.73rem;
    color: var(--text-3);
    font-weight: 300;
    font-style: italic;
}
.gm-discover-empty {
    font-size: 0.82rem;
    color: var(--text-3);
    padding: 1.5rem 0 0.5rem;
    text-align: center;
}

/* ── Key finding highlight ── */

.gm-keyfind {
    border-left: 3px solid var(--accent);
    background: rgba(181,82,42,0.04);
    padding: 0.8rem 1rem;
    margin: 0.8rem 0 0.3rem;
    border-radius: 0 6px 6px 0;
}
.gm-keyfind-label {
    font-size: 0.66rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.3rem;
}
.gm-keyfind-text {
    font-size: 0.88rem;
    color: var(--text);
    line-height: 1.55;
    font-weight: 400;
}

/* ── Stats bar ── */

.gm-stats {
    display: flex;
    gap: 0;
    margin: 0.6rem 0 0.2rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    background: rgba(255,255,255,0.5);
}
.gm-stats-item {
    flex: 1;
    text-align: center;
    padding: 0.6rem 0.5rem;
    border-right: 1px solid var(--border-lt);
}
.gm-stats-item:last-child { border-right: none; }
.gm-stats-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}
.gm-stats-label {
    font-size: 0.66rem;
    font-weight: 500;
    color: var(--text-3);
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Grain overlay ── */

.gm-grain {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    background-size: 200px 200px;
}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

SEV_CLASS = {
    "critical": "gm-sev-critical",
    "high": "gm-sev-high",
    "medium": "gm-sev-medium",
    "low": "gm-sev-low",
}
SEV_LABEL = {"critical": "CRITICAL", "high": "HIGH", "medium": "MED", "low": "LOW"}
INTENT_SYM = {"high": "$$$", "medium": "$$", "low": "$", "none": "\u2014"}
_VALID_SUB_RE = re.compile(r"^\w+$")


def _html(s):
    st.markdown(s, unsafe_allow_html=True)


def _esc(s):
    """Escape user-supplied text for safe HTML rendering."""
    return _html_mod.escape(str(s)) if s else ""


@st.cache_data(ttl=3600, show_spinner=False)
def load_sample(filename: str = "sample_analysis.json"):
    try:
        with open(os.path.join(EXAMPLES_DIR, filename), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None


def _comment_to_dict(c):
    """Convert Comment dataclass to dict (recursive for replies)."""
    return {
        "id": c.id, "author": c.author, "body": c.body,
        "score": c.score, "created_utc": c.created_utc,
        "parent_id": c.parent_id, "gilded": c.gilded,
        "depth": c.depth,
        "replies": [_comment_to_dict(r) for r in c.replies],
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_thread(_url: str):
    """Fetch a Reddit thread. Cached 1 hour per URL."""
    from reddit_fetcher import RedditFetcher

    fetcher = RedditFetcher()
    thread = fetcher.fetch_thread(_url)
    if thread is None:
        return None
    return {
        "id": thread.id, "title": thread.title,
        "author": thread.author, "selftext": thread.selftext,
        "score": thread.score, "num_comments": thread.num_comments,
        "created_utc": thread.created_utc, "url": thread.url,
        "subreddit": thread.subreddit, "upvote_ratio": thread.upvote_ratio,
        "comments": [_comment_to_dict(c) for c in thread.comments],
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _analyze_thread(_thread_dict_json: str, _api_key: str):
    """Run AI analysis on a thread dict. Cached 1 hour."""
    import json as _json
    from ai_analyzer import AIAnalyzer

    thread_dict = _json.loads(_thread_dict_json)
    analyzer = AIAnalyzer(api_key=_api_key)
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
    return analysis_data, result.total_comments, result.analyzed_comments


def _relative_time(created_utc: float) -> str:
    """Convert a Unix timestamp to a relative time string like '2d ago'."""
    diff = _time.time() - created_utc
    if diff < 60:
        return "now"
    if diff < 3600:
        return f"{int(diff // 60)}m ago"
    if diff < 86400:
        return f"{int(diff // 3600)}h ago"
    return f"{int(diff // 86400)}d ago"


@st.cache_data(ttl=300, show_spinner=False)
def _browse_subreddit(subreddit: str, sort: str, time_filter: str, limit: int = 25):
    """Fetch subreddit posts. Cached 5 min."""
    from reddit_fetcher import RedditFetcher

    fetcher = RedditFetcher(rate_limit_delay=0)
    if sort == "top":
        return fetcher.fetch_subreddit_top(subreddit, time_filter=time_filter, limit=limit)
    elif sort == "new":
        return fetcher.fetch_subreddit_new(subreddit, limit=limit)
    else:
        return fetcher.fetch_subreddit_hot(subreddit, limit=limit)


# ── Render ────────────────────────────────────────────────────────────────────

def render_hero():
    _html(
        '<div class="gm-hero">'
        f'<h1 class="gm-hero-title">{t("hero_title")}</h1>'
        f'<p class="gm-hero-sub">{t("hero_sub")}</p>'
        '</div>'
    )


def render_thread(data):
    title = _esc(data.get("thread_title", ""))
    n = data.get("total_comments", 0)
    pp = len(data.get("pain_points", []))
    ins = len(data.get("key_insights", []))
    opp = len(data.get("market_opportunities", []))
    meta = t("meta_fmt", n=n, pp=pp, ins=ins, opp=opp)
    _html(
        f'<div class="gm-thread-bar">'
        f'<div class="gm-thread-bar-title">{title}</div>'
        f'<div class="gm-thread-bar-meta">{meta}</div>'
        f'</div>'
    )


def render_stats_bar(data):
    comments = data.get("total_comments", 0)
    pain_points = len(data.get("pain_points", []))
    high_intent = sum(
        1 for pp in data.get("pain_points", [])
        if pp.get("purchase_intent") == "high"
    )
    _html(
        '<div class="gm-stats">'
        f'<div class="gm-stats-item"><div class="gm-stats-num">{comments}</div>'
        f'<div class="gm-stats-label">{t("sample_stats_comments")}</div></div>'
        f'<div class="gm-stats-item"><div class="gm-stats-num">{pain_points}</div>'
        f'<div class="gm-stats-label">{t("sample_stats_pain_points")}</div></div>'
        f'<div class="gm-stats-item"><div class="gm-stats-num">{high_intent}</div>'
        f'<div class="gm-stats-label">{t("sample_stats_high_intent")}</div></div>'
        '</div>'
    )


def render_key_finding(data):
    finding = data.get("key_finding")
    if not finding:
        return
    _html(
        '<div class="gm-keyfind">'
        f'<div class="gm-keyfind-label">{t("sample_key_finding")}</div>'
        f'<div class="gm-keyfind-text">{_esc(finding)}</div>'
        '</div>'
    )


def render_section(label, style="a", sub=""):
    sub_html = f'<div class="gm-sec-sub">{_esc(sub)}</div>' if sub else ""
    _html(f'<div class="gm-sec-{style}"><div class="gm-sec-l">{_esc(label)}</div>{sub_html}</div>')


def render_pain_point(pp, idx):
    sev = pp.get("severity", "medium")
    intent = pp.get("purchase_intent", "none")
    desc = _esc(pp.get("description", ""))
    cat = _esc(pp.get("category", ""))
    freq = pp.get("frequency_mentioned", 0)
    examples = pp.get("example_comments", [])

    sev_cls = SEV_CLASS.get(sev, "gm-sev-medium")
    sev_lbl = SEV_LABEL.get(sev, "MED")
    intent_sym = INTENT_SYM.get(intent, "\u2014")
    num = f"{idx:02d}"
    feat = " gm-pp-feat" if idx == 1 else ""

    _html(
        f'<div class="gm-pp{feat}">'
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
        with st.expander(t("show_quotes", n=len(examples))):
            for ex in examples:
                st.markdown(f"> {_esc(ex)}")


def render_insights(items):
    if not items:
        return
    rows = []
    for item in items:
        rows.append(
            f'<div class="gm-list-item">'
            f'<span class="gm-list-marker">&mdash;</span>'
            f'<span>{_esc(item)}</span>'
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
            f'<span>{_esc(item)}</span>'
            f'</div>'
        )
    _html("".join(rows))


def render_sentiment(text):
    if not text:
        return
    _html(
        f'<div class="gm-quote">'
        f'<div class="gm-quote-text">{_esc(text)}</div>'
        f'</div>'
    )


def render_analysis(data):
    render_thread(data)
    render_stats_bar(data)
    render_key_finding(data)

    pain_points = data.get("pain_points", [])
    insights = data.get("key_insights", [])
    opportunities = data.get("market_opportunities", [])
    sentiment = data.get("sentiment_summary", "")

    render_section(t("sec_pain"), "a", t("sec_pain_sub"))
    intent_order = {"high": 4, "medium": 3, "low": 2, "none": 1}
    sorted_pps = sorted(
        pain_points,
        key=lambda x: (intent_order.get(x.get("purchase_intent", "none"), 0), x.get("frequency_mentioned", 0)),
        reverse=True,
    )
    for i, pp in enumerate(sorted_pps, 1):
        render_pain_point(pp, i)

    render_section(t("sec_insight"), "b", t("sec_insight_sub"))
    render_insights(insights)

    render_section(t("sec_opp"), "c", t("sec_opp_sub"))
    render_opportunities(opportunities)

    render_section(t("sec_sentiment"), "d", t("sec_sentiment_sub"))
    render_sentiment(sentiment)

    _html('<div style="height:1.5rem"></div>')
    st.download_button(
        label=t("btn_download"),
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="analysis.json",
        mime="application/json",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

# Language toggle (top-right, subtle)
_html('<div class="gm-lang-row">')
lang_choice = st.radio(
    "lang",
    ["English", "日本語"],
    index=0 if st.session_state.lang == "en" else 1,
    horizontal=True,
    label_visibility="collapsed",
    key="lang_toggle",
)
_html('</div>')
st.session_state.lang = "en" if lang_choice == "English" else "ja"

render_hero()

# Session state defaults for Discover tab
for _k, _v in [
    ("discover_subreddit", ""),
    ("discover_sort", "hot"),
    ("discover_time", "week"),
    ("prefill_url", ""),
    ("last_subreddit", ""),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

_POPULAR_SUBS = [
    "Entrepreneur", "SaaS", "startups", "smallbusiness",
    "indiehackers", "webdev", "marketing", "sideproject",
]

# Determine initial tab index (jump to Live Analysis when prefill_url is set)
_tab_names = [t("tab_sample"), t("tab_discover"), t("tab_live")]
_default_tab_idx = 2 if st.session_state.prefill_url else 0

mode = st.radio(
    "mode",
    _tab_names,
    index=_default_tab_idx,
    horizontal=True,
    label_visibility="collapsed",
)

# ── Tab: Sample Data ──────────────────────────────────────────────────────

if mode == t("tab_sample"):
    _html(
        '<div class="gm-how">'
        f'<div class="gm-how-title">{t("how_title")}</div>'
        f'<div class="gm-how-body">{t("how_desc")}<br><br>{t("how_sample", tab_live=t("tab_live"))}</div>'
        '</div>'
    )
    _lang_key = "label_ja" if st.session_state.lang == "ja" else "label_en"
    _sample_labels = [s[_lang_key] for s in SAMPLE_CATALOG]
    _sample_choice = st.selectbox(
        t("sample_select_label"),
        _sample_labels,
        index=0,
        key="sample_select",
    )
    _sample_idx = _sample_labels.index(_sample_choice) if _sample_choice in _sample_labels else 0
    _sample_file = SAMPLE_CATALOG[_sample_idx]["file"]
    _sample_data = load_sample(_sample_file)
    if _sample_data is None:
        st.error(t("err_analysis", detail="Sample data unavailable"))
        st.stop()
    render_analysis(_sample_data)

# ── Tab: Discover ─────────────────────────────────────────────────────────

elif mode == t("tab_discover"):
    _html(
        '<div class="gm-how">'
        f'<div class="gm-how-title">{t("discover_how_title")}</div>'
        f'<div class="gm-how-body">{t("discover_how_desc")}</div>'
        '</div>'
    )

    # Auto-populate from last analysed subreddit (one-shot)
    _from_last = False
    if st.session_state.last_subreddit and not st.session_state.discover_subreddit:
        st.session_state.discover_subreddit = st.session_state.last_subreddit
        _from_last = True

    # Popular subreddit pills (2 rows × 4) — no _html() wrappers
    _html(f'<div style="margin-top:0.5rem;margin-bottom:0.2rem;">'
          f'<span style="font-size:0.74rem;color:var(--text-3);font-weight:500;">'
          f'{t("discover_popular")}</span></div>')
    for _row_start in range(0, len(_POPULAR_SUBS), 4):
        _pill_cols = st.columns(4)
        for _i, _sub in enumerate(_POPULAR_SUBS[_row_start:_row_start + 4]):
            with _pill_cols[_i]:
                if st.button(_sub, key=f"pill_{_sub}"):
                    st.session_state.discover_subreddit = _sub
                    st.rerun()

    # Search controls — Period only shown when Sort=top
    if st.session_state.discover_sort == "top":
        _ctrl1, _ctrl2, _ctrl3 = st.columns([3, 1, 1.5])
    else:
        _ctrl1, _ctrl2 = st.columns([3, 1])
    with _ctrl1:
        _sub_input = st.text_input(
            t("discover_subreddit_label"),
            value=st.session_state.discover_subreddit,
            placeholder="e.g. Entrepreneur",
            key="disc_sub_input",
        )
    with _ctrl2:
        _sort_input = st.selectbox(
            t("discover_sort_label"),
            ["hot", "top", "new"],
            index=["hot", "top", "new"].index(st.session_state.discover_sort),
            key="disc_sort_input",
        )
    _time_input = st.session_state.discover_time
    if st.session_state.discover_sort == "top":
        _time_options = ["hour", "day", "week", "month", "year", "all"]
        with _ctrl3:
            _time_input = st.selectbox(
                t("discover_time_label"),
                _time_options,
                index=_time_options.index(st.session_state.discover_time),
                key="disc_time_input",
            )

    _do_browse = st.button(t("discover_btn_browse"), type="primary", key="disc_browse")

    if _do_browse and _sub_input.strip():
        _cleaned = _sub_input.strip()
        if not _VALID_SUB_RE.match(_cleaned):
            st.error(t("discover_err_invalid_sub"))
            st.stop()
        st.session_state.discover_subreddit = _cleaned
        st.session_state.discover_sort = _sort_input
        st.session_state.discover_time = _time_input

    # Show results if a subreddit is selected
    _active_sub = st.session_state.discover_subreddit
    if _active_sub:
        with st.status(t("status_browse", subreddit=_active_sub), expanded=False) as _disc_status:
            try:
                _posts = _browse_subreddit(
                    _active_sub,
                    st.session_state.discover_sort,
                    st.session_state.discover_time,
                )
            except Exception:
                _disc_status.update(label=t("discover_err_fetch", subreddit=_esc(_active_sub)), state="error")
                _posts = []
            else:
                # Filter: 5+ comments
                _posts = [p for p in _posts if p.get("num_comments", 0) >= 5]
                _disc_status.update(
                    label=f"r/{_esc(_active_sub)} — {len(_posts)} threads",
                    state="complete",
                    expanded=False,
                )

        if not _posts:
            st.info(t("discover_no_results"))
        else:
            # Hint when auto-populated from last analysis
            if _from_last:
                _html(f'<div class="gm-discover-hint">{t("discover_from_last")}</div>')

            _html(f'<div style="font-size:0.74rem;color:var(--text-3);margin:0.6rem 0 0;">'
                  f'{t("discover_results_count", n=len(_posts))}</div>')

            # Render numbered cards with Reddit links
            _cards_html = []
            _thread_labels = []
            for _idx, _p in enumerate(_posts, 1):
                _title_esc = _esc(_p["title"])
                _permalink = _esc(_p.get("permalink", ""))
                _sub_esc = _esc(_p.get("subreddit", _active_sub))
                _score_esc = _esc(_p["score"])
                _cmt_esc = _esc(_p["num_comments"])
                _cards_html.append(
                    f'<div class="gm-discover-card">'
                    f'<div class="gm-discover-title">'
                    f'<span class="gm-card-num">#{_idx}</span>'
                    f'<a href="{_permalink}" target="_blank" rel="noopener">{_title_esc}</a>'
                    f'</div>'
                    f'<div class="gm-discover-meta">r/{_sub_esc}'
                    f'&ensp;&middot;&ensp;{_score_esc} pts'
                    f'&ensp;&middot;&ensp;{_cmt_esc} comments'
                    f'&ensp;&middot;&ensp;{_relative_time(_p["created_utc"])}'
                    f'</div></div>'
                )
                # Selectbox label with matching number
                _lbl = _p["title"]
                if len(_lbl) > 55:
                    _lbl = _lbl[:52] + "..."
                _thread_labels.append(f"#{_idx}  {_lbl}")

            _html(''.join(_cards_html))

            # Thread selection + Analyze button
            _sel_col, _btn_col = st.columns([4, 1])
            with _sel_col:
                _selected = st.selectbox(
                    t("discover_select_thread"),
                    _thread_labels,
                    key="disc_thread_select",
                    label_visibility="collapsed",
                )
            with _btn_col:
                if st.button(t("discover_btn_analyze"), type="primary", key="disc_analyze"):
                    _sel_idx = _thread_labels.index(_selected) if _selected in _thread_labels else 0
                    st.session_state.prefill_url = _posts[_sel_idx]["permalink"]
                    st.rerun()
    else:
        # Empty state guidance
        _html(f'<div class="gm-discover-empty">{t("discover_empty_hint")}</div>')

# ── Tab: Live Analysis ────────────────────────────────────────────────────

else:
    _html(
        '<div class="gm-how">'
        f'<div class="gm-how-title">{t("how_title")}</div>'
        f'<div class="gm-how-body">{t("how_live")}</div>'
        '</div>'
    )
    # 3-step guide
    _html(
        '<div class="gm-guide">'
        f'<div class="gm-guide-step"><span class="gm-guide-n">1.</span><span>{t("guide_step1")}</span></div>'
        f'<div class="gm-guide-step"><span class="gm-guide-n">2.</span><span>{t("guide_step2")}</span></div>'
        f'<div class="gm-guide-step"><span class="gm-guide-n">3.</span><span>{t("guide_step3")}</span></div>'
        '</div>'
    )

    api_key = st.text_input(t("label_api_key"), type="password", placeholder="sk-...")

    # Prefill URL from Discover tab
    _prefill = st.session_state.get("prefill_url", "")
    url = st.text_input(t("label_url"), value=_prefill, placeholder="https://www.reddit.com/r/...")
    # Clear prefill after it's been consumed
    if _prefill:
        st.session_state.prefill_url = ""

    if st.button(t("btn_analyze"), type="primary", disabled=not (api_key and url)):
        # Validate inputs
        _reddit_url_re = re.compile(
            r"https?://(www\.|old\.)?reddit\.com/r/\w+/comments/\w+",
        )
        if not api_key.startswith("sk-"):
            st.error(t("err_invalid_key"))
            st.stop()
        if not _reddit_url_re.match(url):
            st.error(t("err_invalid_url"))
            st.stop()

        try:
            with st.status(t("spinner_fetch"), expanded=True) as _status:
                # Step 1: Fetch thread
                _status.update(label=t("status_fetch"), state="running")
                thread_dict = _fetch_thread(url)

                if thread_dict is None:
                    _status.update(label=t("err_fetch"), state="error")
                    st.error(t("err_fetch"))
                    st.stop()

                # Step 2: Parse
                _n_comments = thread_dict.get("num_comments", 0)
                _status.update(
                    label=t("status_parse", n=_n_comments),
                    state="running",
                )

                # Step 3: AI analysis
                _status.update(label=t("status_ai"), state="running")
                _thread_json = json.dumps(thread_dict, ensure_ascii=False)
                analysis_data, total, analyzed = _analyze_thread(_thread_json, api_key)

                # Done
                _status.update(label=t("status_done"), state="complete", expanded=False)

            # Save subreddit for related thread suggestions
            _m = re.search(r"reddit\.com/r/(\w+)/", url)
            if _m:
                st.session_state.last_subreddit = _m.group(1)

            if analyzed < total:
                st.warning(t(
                    "warn_comment_limit",
                    total=total,
                    analyzed=analyzed,
                ))
            render_analysis(analysis_data)

        except Exception as e:
            # Sanitize: show only the exception class name, not full traceback
            st.error(t("err_analysis", detail=type(e).__name__))

# Grain overlay + minimal footer
_html('<div class="gm-grain"></div>')
_html(f'<div style="padding:3rem 0 1rem; font-size:0.65rem; color:var(--text-3);">{t("footer")}</div>')
