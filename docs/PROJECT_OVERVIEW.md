# Reddit Goldmine Analyzer - プロジェクト概要

## 🎯 プロジェクトの目的

RedditのJSON APIを活用し、AIで顧客の「痛点」「購買意欲」「市場機会」を大規模に発見するツールを提供する。

**コンセプト**: 「顧客は文字どおり『自分が欲しいもの』を叫んでくれている。あとはこちらが、大規模に『聞き耳を立てる』だけ。」

---

## 🚀 主要機能

### 1. Reddit JSON API データ取得
- **ワンステップ取得**: URLに `.json` を付けるだけ
- **完全なデータ**: すべてのコメント・メタデータを構造化
- **バッチ処理**: 複数スレッド・サブレディット全体を一括処理

### 2. AI分析エンジン
- **痛点検出**: ユーザーが抱える具体的な問題を抽出
- **購買意欲分析**: High/Medium/Low/None で緊急性を評価
- **深刻度評価**: Critical/High/Medium/Low で影響度を判定
- **カテゴリ分類**: マーケティング、財務、運用、技術など

### 3. レポート生成
- **Markdown形式**: 読みやすく、共有しやすい
- **優先順位付け**: 購買意欲順に自動ソート
- **実例付き**: 実際のコメントを引用
- **市場機会提案**: AIが具体的なビジネスアイデアを提案

---

## 📁 プロジェクト構成

```
reddit_goldmine_analyzer/
├── README.md                  # プロジェクト説明
├── USAGE_GUIDE.md            # 詳細な使用ガイド
├── PROJECT_OVERVIEW.md       # このファイル
├── reddit_fetcher.py         # データ取得モジュール
├── ai_analyzer.py            # AI分析モジュール
├── goldmine_finder.py        # メインツール
├── demo.py                   # デモスクリプト
└── output/                   # 分析結果の出力先
```

---

## 🔧 技術スタック

### バックエンド
- **Python 3.11+**
- **requests**: HTTP通信
- **OpenAI API**: AI分析 (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)

### データ処理
- **JSON**: Reddit APIのレスポンス形式
- **dataclasses**: 型安全なデータ構造

### 出力
- **Markdown**: レポート形式
- **JSON**: 構造化データ

---

## 🎨 アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                     goldmine_finder.py                       │
│                    (統合ツール・CLI)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│   reddit_fetcher.py       │  │    ai_analyzer.py        │
│   (データ取得・構造化)      │  │    (AI分析エンジン)       │
└───────────────────────────┘  └──────────────────────────┘
                │                           │
                ▼                           ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│   Reddit JSON API         │  │    OpenAI API            │
│   (old.reddit.com)        │  │    (GPT-4.1-mini)        │
└───────────────────────────┘  └──────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
                ┌──────────────────────────┐
                │   output/                │
                │   - thread_xxx.json      │
                │   - analysis_xxx.json    │
                │   - report_xxx.md        │
                │   - summary_xxx.md       │
                └──────────────────────────┘
```

---

## 📊 データフロー

### 1. データ取得フェーズ

```
Reddit URL
    ↓
URL正規化 (.json 追加)
    ↓
HTTP GET リクエスト
    ↓
JSON レスポンス
    ↓
構造化 (Thread, Comment オブジェクト)
    ↓
thread_xxx.json に保存
```

### 2. AI分析フェーズ

```
thread_xxx.json
    ↓
コメントをフラット化
    ↓
AIプロンプト生成
    ↓
OpenAI API 呼び出し
    ↓
JSON レスポンス (痛点・洞察・市場機会)
    ↓
PainPoint オブジェクトに変換
    ↓
analysis_xxx.json に保存
```

### 3. レポート生成フェーズ

```
AnalysisResult
    ↓
購買意欲順にソート
    ↓
Markdown テンプレート適用
    ↓
絵文字・フォーマット追加
    ↓
report_xxx.md に保存
```

---

## 🧩 主要モジュール詳細

### reddit_fetcher.py

**責務**: RedditからデータをJSONで取得し、構造化する

**主要クラス**:
- `RedditFetcher`: API通信とデータ取得
- `Thread`: スレッドデータモデル
- `Comment`: コメントデータモデル (再帰的な返信構造)

**主要メソッド**:
```python
fetch_thread(url: str) -> Thread
fetch_subreddit_hot(subreddit: str, limit: int) -> List[Dict]
save_to_json(thread: Thread, filepath: str)
get_all_comments_flat(thread: Thread) -> List[Comment]
```

**特徴**:
- レート制限対策 (デフォルト2秒間隔)
- URL自動正規化
- 再帰的なコメント解析

### ai_analyzer.py

**責務**: AIを使って痛点・購買意欲を分析

**主要クラス**:
- `AIAnalyzer`: AI分析エンジン
- `PainPoint`: 痛点データモデル
- `AnalysisResult`: 分析結果データモデル

**主要メソッド**:
```python
analyze_thread(thread_data: Dict) -> AnalysisResult
generate_report(result: AnalysisResult) -> str
save_analysis(result: AnalysisResult, filepath: str)
```

**AIプロンプト設計**:
- システムプロンプト: 市場調査専門家のペルソナ
- JSON形式での構造化出力
- 購買意欲の明確な定義
- 実例引用の要求

**特徴**:
- 複数モデル対応 (GPT-4.1-mini, nano, Gemini)
- JSON mode で確実な構造化出力
- エラーハンドリング

### goldmine_finder.py

**責務**: 統合ツールとCLIインターフェース

**主要クラス**:
- `GoldmineFinder`: 統合ツール

**主要メソッド**:
```python
analyze_single_thread(url: str) -> Dict
analyze_subreddit(subreddit: str, limit: int, min_comments: int) -> List[Dict]
batch_analyze_urls(urls: List[str]) -> List[Dict]
```

**CLIオプション**:
- `--url`: 単一スレッド
- `--subreddit`: サブレディット全体
- `--batch`: バッチ処理
- `--output`: 出力先指定

**特徴**:
- 進捗表示
- エラーハンドリング
- サマリーレポート自動生成

---

## 📈 使用シナリオ

### シナリオ1: 新規SaaS製品のアイデア発見

**目標**: 市場のニーズを発見し、製品コンセプトを検証

**手順**:
1. 関連サブレディットを複数分析
2. 購買意欲Highの痛点を抽出
3. 市場機会セクションを確認
4. 実際のユーザーにインタビュー
5. MVPを構築

### シナリオ2: 競合分析

**目標**: 競合製品の弱点を特定

**手順**:
1. 競合製品に関するスレッドを検索
2. ユーザーの不満を分析
3. 自社製品の差別化ポイントを明確化
4. マーケティングメッセージに反映

### シナリオ3: カスタマーサポート改善

**目標**: 頻出する問題を特定し、プロアクティブに対応

**手順**:
1. 自社製品サブレディットを定期監視
2. カテゴリ別に問題を分類
3. FAQやドキュメントを更新
4. 製品改善に反映

---

## 🎯 成功指標

### 定量的指標
- 分析したスレッド数
- 発見した痛点の数
- 購買意欲Highの痛点の割合
- 実際に製品化したアイデアの数

### 定性的指標
- 市場理解の深化
- ユーザーの言葉遣いの習得
- 競合との差別化ポイントの明確化

---

## 🔮 今後の拡張可能性

### 機能拡張
- [ ] 感情分析の強化
- [ ] トレンド分析 (時系列)
- [ ] 競合製品の自動検出
- [ ] 多言語対応
- [ ] Webダッシュボード

### データソース拡張
- [ ] Twitter/X の分析
- [ ] Hacker News
- [ ] Product Hunt
- [ ] Discord コミュニティ

### AI機能拡張
- [ ] 製品アイデアの自動生成
- [ ] マーケティングメッセージの提案
- [ ] ターゲット顧客ペルソナの生成
- [ ] 競合マッピング

---

## 🛡️ 制限事項と注意点

### Reddit API
- レート制限: 1リクエスト/2秒 (推奨)
- 認証不要だが、User-Agent必須
- 商用利用時は利用規約を確認

### AI分析
- APIコスト: 1スレッドあたり約$0.01-0.05
- 精度: 100%ではない、人間の検証が必要
- 言語: 英語が最も精度が高い

### データプライバシー
- 公開データのみを使用
- 個人情報の取り扱いに注意
- 利用規約を遵守

---

## 📚 参考資料

### Reddit API
- [Reddit JSON API ドキュメント](https://github.com/reddit-archive/reddit/wiki/json)
- [Reddit API 利用規約](https://www.reddit.com/wiki/api/)

### OpenAI API
- [OpenAI API ドキュメント](https://platform.openai.com/docs/)
- [JSON mode](https://platform.openai.com/docs/guides/structured-outputs)

---

## 👥 対象ユーザー

- **起業家**: 新規ビジネスアイデアを探している
- **プロダクトマネージャー**: ユーザーニーズを深く理解したい
- **マーケター**: ターゲット顧客の言葉遣いを学びたい
- **投資家**: 市場機会を評価したい
- **研究者**: ソーシャルメディア分析に興味がある

---

## 🎓 学習リソース

### 初心者向け
1. `demo.py` を実行してツールの動作を理解
2. `USAGE_GUIDE.md` で基本的な使い方を学習
3. サンプルレポートを読んで出力形式を理解

### 中級者向け
1. `reddit_fetcher.py` のコードを読んでAPI連携を学習
2. `ai_analyzer.py` のプロンプトをカスタマイズ
3. 独自のサブレディットで分析を実施

### 上級者向け
1. モジュールを拡張して新機能を追加
2. 他のデータソースと統合
3. Webアプリケーション化

---

**作成日**: 2026-02-11
**バージョン**: 1.0
**ライセンス**: MIT
