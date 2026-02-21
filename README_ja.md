<div align="center">

# Reddit Goldmine Analyzer

**AIでRedditスレッドから市場インサイトを自動抽出**

顧客の痛点・購買意欲・市場機会を大規模に発見します。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://redditgoldmineanalyzer-mtkdansfuhyqccwslcunwt.streamlit.app/)

[ライブデモ](https://redditgoldmineanalyzer-mtkdansfuhyqccwslcunwt.streamlit.app/) · [CLI の使い方](#-cli-の使い方) · [クイックスタート](#-クイックスタート) · [English](README.md)

</div>

---

## できること

RedditスレッドのURLを入力するだけで、人々が*本当にお金を払いたい*と思っている課題を構造化して抽出します。

**出力例**（実際の r/Entrepreneur スレッドから）:

| 痛点 | 深刻度 | 購買意欲 | カテゴリ |
|------|--------|---------|---------|
| ハードウェアスタートアップの製造・流通の課題 | 🟠 HIGH | 💰💰💰 HIGH | 製造・オペレーション |
| ポッドキャストの動画制作品質の低さ | 🟡 MEDIUM | 💰💰 MEDIUM | 制作品質 |
| プラットフォーム間でのポッドキャスト配信の限界 | 🟡 MEDIUM | 💰 LOW | 配信・アクセス |

さらに**キーインサイト**、**市場機会**、**センチメント分析**も自動で抽出します。

---

## 仕組み

```
1. 取得    →  RedditスレッドをJSON API経由で取得（認証不要）
2. 分析    →  AIが痛点・購買意欲・市場機会を抽出
3. レポート →  優先度付きのレポートを生成（Markdown + JSON）
```

**アーキテクチャ:**

```
Reddit URL → reddit_fetcher.py → ai_analyzer.py → レポート (MD + JSON)
                                         ↑
                                   OpenAI / GPT-4.1
```

---

## Web デモ

ブラウザですぐに試せます。サンプルデータモードなら**APIキー不要**です。

**[ライブデモを開く](https://redditgoldmineanalyzer-mtkdansfuhyqccwslcunwt.streamlit.app/)**

ローカルで実行する場合:

```bash
pip install -r requirements.txt
streamlit run app.py
```

![デモ](docs/demo.gif)

**主な機能:**
- **サンプルデータモード** — APIキー不要で分析結果をすぐ確認
- **ライブ分析モード** — OpenAI APIキーを入力して任意のReddit URLをリアルタイム分析
- 深刻度・購買意欲のカラーバッジ表示
- コメント例の展開表示
- 分析結果のワンクリックダウンロード

---

## CLI の使い方

### 単一スレッドを分析

```bash
python goldmine_finder.py --url "https://www.reddit.com/r/Entrepreneur/comments/xxx/"
```

### サブレディット全体をスキャン

```bash
python goldmine_finder.py --subreddit Entrepreneur --limit 10 --min-comments 5
```

### 複数URLをバッチ分析

```bash
python goldmine_finder.py --batch urls.txt --output my_analysis/
```

**出力ファイル:**
- `thread_xxx.json` — 生のスレッドデータ
- `analysis_xxx.json` — AI分析結果
- `report_xxx.md` — 人間が読めるレポート
- `summary_xxx.md` — クロススレッドサマリー（サブレディット/バッチモード）

---

## クイックスタート

### 1. クローン & インストール

```bash
git clone https://github.com/yu010101/reddit_goldmine_analyzer.git
cd reddit_goldmine_analyzer
pip install -r requirements.txt
```

### 2. デモを試す（APIキー不要）

```bash
python demo.py
```

### 3. Web UIを起動（サンプルデータはAPIキー不要）

```bash
streamlit run app.py
```

### 4. ライブデータを分析（OpenAI APIキーが必要）

```bash
export OPENAI_API_KEY="your-key-here"
python goldmine_finder.py --url "https://www.reddit.com/r/SaaS/comments/xxx/"
```

### 5. Dockerで実行

```bash
docker compose up
```

---

## プロジェクト構成

```
reddit_goldmine_analyzer/
├── app.py                 # Streamlit Web UI
├── goldmine_finder.py     # CLIツール（メインエントリポイント）
├── reddit_fetcher.py      # Reddit JSON APIフェッチャー
├── ai_analyzer.py         # AI分析エンジン
├── config.py              # 設定の一元管理（環境変数でオーバーライド可）
├── demo.py                # クイックデモスクリプト
├── examples/              # サンプルデータ（APIキー不要で動作）
│   ├── sample_thread.json
│   ├── sample_analysis.json
│   ├── sample_analysis_saas.json
│   ├── sample_analysis_sideproject.json
│   ├── sample_analysis_startups.json
│   └── sample_report.md
├── tests/                 # ユニット・統合テスト（pytest, 278件）
├── docs/                  # ドキュメント（英語・日本語）
├── Dockerfile             # コンテナセットアップ
├── docker-compose.yml     # Docker Compose設定
├── requirements.txt
├── LICENSE
├── README.md              # 英語版README
└── README_ja.md           # 本ファイル（日本語）
```

---

## 設定

### 環境変数によるオーバーライド

`config.py` で定義された全設定は `RGA_` プレフィックス付き環境変数でオーバーライドできます:

```bash
RGA_MODEL=gpt-4.1-nano python goldmine_finder.py --url "..."
RGA_RATE_LIMIT_DELAY=3 python goldmine_finder.py --subreddit SaaS
```

### AIモデル

```python
analyzer = AIAnalyzer(model="gpt-4.1-mini")   # デフォルト（バランス型）
analyzer = AIAnalyzer(model="gpt-4.1-nano")   # より高速・低コスト
```

### レート制限

```python
fetcher = RedditFetcher()
fetcher.rate_limit_delay = 3  # リクエスト間隔（デフォルト: 2秒）
```

---

## コスト

- 1スレッドあたり約 $0.01〜0.05（GPT-4.1-mini使用時）
- Reddit APIは無料（公開JSONエンドポイント、認証不要）

---

## テスト

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

278テスト全パス。セキュリティ監査テスト、XSSエスケープ検証を含みます。

---

## ライセンス

[MIT](LICENSE)

---

## コントリビュート

Issue・プルリクエスト歓迎です!

---

<div align="center">

**Happy Goldmining!**

</div>
