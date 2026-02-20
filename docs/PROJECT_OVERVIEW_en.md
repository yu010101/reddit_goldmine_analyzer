# Reddit Goldmine Analyzer - Project Overview

## Project Purpose

Provide a tool that leverages the Reddit JSON API and AI to discover customer "pain points," "purchase intent," and "market opportunities" at scale.

**Concept**: "Customers are literally screaming about what they want. All we need to do is listen -- at scale."

---

## Core Features

### 1. Reddit JSON API Data Fetching
- **One-step fetching**: Simply append `.json` to a Reddit URL
- **Complete data**: All comments and metadata are captured in a structured format
- **Batch processing**: Process multiple threads or entire subreddits at once

### 2. AI Analysis Engine
- **Pain point detection**: Extract specific problems that users face
- **Purchase intent analysis**: Evaluate urgency as High / Medium / Low / None
- **Severity assessment**: Determine impact level as Critical / High / Medium / Low
- **Category classification**: Marketing, Finance, Operations, Technology, and more

### 3. Report Generation
- **Markdown format**: Easy to read and share
- **Prioritized**: Automatically sorted by purchase intent
- **Evidence-based**: Includes actual user comments as citations
- **Market opportunity suggestions**: AI proposes concrete business ideas

---

## Project Structure

```
reddit_goldmine_analyzer/
├── README.md                  # Project description
├── USAGE_GUIDE.md            # Detailed usage guide
├── PROJECT_OVERVIEW.md       # This file (Japanese)
├── reddit_fetcher.py         # Data fetching module
├── ai_analyzer.py            # AI analysis module
├── goldmine_finder.py        # Main tool
├── demo.py                   # Demo script
└── output/                   # Analysis output directory
```

---

## Tech Stack

### Backend
- **Python 3.11+**
- **requests**: HTTP communication
- **OpenAI API**: AI analysis (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)

### Data Processing
- **JSON**: Reddit API response format
- **dataclasses**: Type-safe data structures

### Output
- **Markdown**: Report format
- **JSON**: Structured data

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     goldmine_finder.py                       │
│                  (Integration Tool / CLI)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│   reddit_fetcher.py       │  │    ai_analyzer.py        │
│   (Data Fetching &        │  │    (AI Analysis Engine)   │
│    Structuring)           │  │                          │
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

## Data Flow

### 1. Data Fetching Phase

```
Reddit URL
    ↓
URL normalization (append .json)
    ↓
HTTP GET request
    ↓
JSON response
    ↓
Structuring (Thread, Comment objects)
    ↓
Save to thread_xxx.json
```

### 2. AI Analysis Phase

```
thread_xxx.json
    ↓
Flatten comments
    ↓
Generate AI prompt
    ↓
Call OpenAI API
    ↓
JSON response (pain points, insights, market opportunities)
    ↓
Convert to PainPoint objects
    ↓
Save to analysis_xxx.json
```

### 3. Report Generation Phase

```
AnalysisResult
    ↓
Sort by purchase intent
    ↓
Apply Markdown template
    ↓
Add formatting
    ↓
Save to report_xxx.md
```

---

## Module Details

### reddit_fetcher.py

**Responsibility**: Fetch data from Reddit as JSON and structure it

**Key Classes**:
- `RedditFetcher`: API communication and data fetching
- `Thread`: Thread data model
- `Comment`: Comment data model (recursive reply structure)

**Key Methods**:
```python
fetch_thread(url: str) -> Thread
fetch_subreddit_hot(subreddit: str, limit: int) -> List[Dict]
save_to_json(thread: Thread, filepath: str)
get_all_comments_flat(thread: Thread) -> List[Comment]
```

**Features**:
- Rate limiting (default 2-second interval)
- Automatic URL normalization
- Recursive comment parsing

### ai_analyzer.py

**Responsibility**: Analyze pain points and purchase intent using AI

**Key Classes**:
- `AIAnalyzer`: AI analysis engine
- `PainPoint`: Pain point data model
- `AnalysisResult`: Analysis result data model

**Key Methods**:
```python
analyze_thread(thread_data: Dict) -> AnalysisResult
generate_report(result: AnalysisResult) -> str
save_analysis(result: AnalysisResult, filepath: str)
```

**AI Prompt Design**:
- System prompt: Market research expert persona
- Structured output in JSON format
- Clear definitions for purchase intent levels
- Requires citation of actual user comments

**Features**:
- Multi-model support (GPT-4.1-mini, nano, Gemini)
- JSON mode for reliable structured output
- Error handling

### goldmine_finder.py

**Responsibility**: Integration tool and CLI interface

**Key Classes**:
- `GoldmineFinder`: Integration tool

**Key Methods**:
```python
analyze_single_thread(url: str) -> Dict
analyze_subreddit(subreddit: str, limit: int, min_comments: int) -> List[Dict]
batch_analyze_urls(urls: List[str]) -> List[Dict]
```

**CLI Options**:
- `--url`: Single thread
- `--subreddit`: Entire subreddit
- `--batch`: Batch processing
- `--output`: Output directory

**Features**:
- Progress display
- Error handling
- Automatic summary report generation

---

## Usage Scenarios

### Scenario 1: Discovering New SaaS Product Ideas

**Goal**: Identify market needs and validate product concepts

**Steps**:
1. Analyze multiple related subreddits
2. Extract pain points with High purchase intent
3. Review the market opportunities section
4. Interview actual users
5. Build an MVP

### Scenario 2: Competitive Analysis

**Goal**: Identify weaknesses in competitor products

**Steps**:
1. Search for threads about competitor products
2. Analyze user complaints
3. Clarify differentiation points for your own product
4. Reflect findings in marketing messaging

### Scenario 3: Customer Support Improvement

**Goal**: Identify frequently occurring issues and address them proactively

**Steps**:
1. Regularly monitor your product's subreddit
2. Classify issues by category
3. Update FAQs and documentation
4. Feed insights back into product improvements

---

## Success Metrics

### Quantitative Metrics
- Number of threads analyzed
- Number of pain points discovered
- Percentage of pain points with High purchase intent
- Number of ideas that actually became products

### Qualitative Metrics
- Deeper understanding of the market
- Mastery of user language and vocabulary
- Clearer differentiation from competitors

---

## Future Enhancements

### Feature Enhancements
- [ ] Improved sentiment analysis
- [ ] Trend analysis (time series)
- [ ] Automatic competitor product detection
- [ ] Multi-language support
- [ ] Web dashboard

### Data Source Expansion
- [ ] Twitter/X analysis
- [ ] Hacker News
- [ ] Product Hunt
- [ ] Discord communities

### AI Feature Expansion
- [ ] Automatic product idea generation
- [ ] Marketing message suggestions
- [ ] Target customer persona generation
- [ ] Competitive mapping

---

## Limitations and Notes

### Reddit API
- Rate limiting: 1 request per 2 seconds (recommended)
- No authentication required, but a User-Agent header is mandatory
- Review the terms of service before commercial use

### AI Analysis
- API cost: Approximately $0.01--0.05 per thread
- Accuracy: Not 100% -- human verification is necessary
- Language: English yields the highest accuracy

### Data Privacy
- Only publicly available data is used
- Handle personal information with care
- Comply with terms of service

---

## References

### Reddit API
- [Reddit JSON API Documentation](https://github.com/reddit-archive/reddit/wiki/json)
- [Reddit API Terms of Use](https://www.reddit.com/wiki/api/)

### OpenAI API
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [JSON mode](https://platform.openai.com/docs/guides/structured-outputs)

---

## Target Users

- **Entrepreneurs**: Looking for new business ideas
- **Product Managers**: Seeking a deeper understanding of user needs
- **Marketers**: Learning the language and vocabulary of target customers
- **Investors**: Evaluating market opportunities
- **Researchers**: Interested in social media analysis

---

## Learning Resources

### Beginners
1. Run `demo.py` to understand how the tool works
2. Study `USAGE_GUIDE.md` to learn the basics
3. Read sample reports to understand the output format

### Intermediate
1. Read the `reddit_fetcher.py` source code to learn API integration
2. Customize prompts in `ai_analyzer.py`
3. Conduct analysis on subreddits of your choice

### Advanced
1. Extend modules to add new features
2. Integrate with other data sources
3. Build a web application

---

**Created**: 2026-02-11
**Version**: 1.0
**License**: MIT
