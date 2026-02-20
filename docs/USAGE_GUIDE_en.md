# Reddit Goldmine Analyzer - Usage Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Practical Use Cases](#practical-use-cases)
4. [How to Read Reports](#how-to-read-reports)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Get Started in 1 Minute

```bash
# 1. Navigate to the directory
cd /home/ubuntu/reddit_goldmine_analyzer

# 2. Run the demo
python3 demo.py

# 3. Check the report
cat report_1pyxz90.md
```

### Analyze a Real Thread

```bash
# Find a thread of interest on Reddit
# Example: https://www.reddit.com/r/Entrepreneur/comments/xxx/my_pain_points/

# Copy the URL and run
python3 goldmine_finder.py --url "https://www.reddit.com/r/Entrepreneur/comments/xxx/my_pain_points/"

# Check the results
ls output/
cat output/report_xxx.md
```

---

## Basic Usage

### Command-Line Options

```bash
python3 goldmine_finder.py [options]
```

#### Main Options

| Option | Description | Example |
|--------|-------------|---------|
| `--url` | URL of a single thread | `--url "https://reddit.com/r/..."` |
| `--subreddit` | Subreddit name | `--subreddit Entrepreneur` |
| `--limit` | Number of posts to fetch | `--limit 20` |
| `--min-comments` | Minimum number of comments | `--min-comments 10` |
| `--batch` | File containing a list of URLs | `--batch urls.txt` |
| `--output` | Output directory | `--output my_analysis/` |

### Usage Patterns

#### Pattern 1: Single Thread Analysis

```bash
python3 goldmine_finder.py \
  --url "https://www.reddit.com/r/SaaS/comments/xxx/" \
  --output saas_analysis/
```

**When to use**:
- You want to dig deep into a specific discussion
- You found a high-quality thread
- You want to analyze feedback about a competitor's product

#### Pattern 2: Subreddit Exploration

```bash
python3 goldmine_finder.py \
  --subreddit indiehackers \
  --limit 15 \
  --min-comments 8 \
  --output indie_analysis/
```

**When to use**:
- Exploring a new market
- Understanding trends
- Comparing multiple pain points

#### Pattern 3: Batch Analysis

```bash
# Create a URL list
cat > high_value_threads.txt << EOF
https://www.reddit.com/r/Entrepreneur/comments/aaa/
https://www.reddit.com/r/startups/comments/bbb/
https://www.reddit.com/r/SaaS/comments/ccc/
EOF

# Run batch analysis
python3 goldmine_finder.py \
  --batch high_value_threads.txt \
  --output batch_results/
```

**When to use**:
- You have a pre-curated set of threads
- Running regular monitoring
- Gathering multiple perspectives on a specific topic

---

## Practical Use Cases

### Use Case 1: Discovering New SaaS Product Ideas

**Goal**: Discover pain points faced by SaaS entrepreneurs and generate product ideas

```bash
# Step 1: Analyze multiple SaaS-related subreddits
python3 goldmine_finder.py --subreddit SaaS --limit 20 --output uc1_saas/
python3 goldmine_finder.py --subreddit indiehackers --limit 20 --output uc1_indie/
python3 goldmine_finder.py --subreddit microsaas --limit 15 --output uc1_micro/

# Step 2: Check the summary reports
cat uc1_saas/summary_SaaS.md | grep "$$$"
cat uc1_indie/summary_indiehackers.md | grep "$$$"

# Step 3: List pain points with high purchase intent
# Step 4: Review the market opportunity sections
# Step 5: Validate product concepts
```

**Expected outcomes**:
- Concrete problems that real users face
- Pain points at the "willing to pay to solve" level
- Niches that competitors are overlooking

### Use Case 2: Competitor Weakness Analysis

**Goal**: Identify user dissatisfaction with competitor products

```bash
# Analyze threads found by searching for a competitor's product name
python3 goldmine_finder.py \
  --url "https://www.reddit.com/r/SaaS/comments/xxx/alternatives_to_competitor/" \
  --output competitor_analysis/

# Extract the following from the report:
# 1. Features users are dissatisfied with
# 2. Features users want but are not offered
# 3. Complaints about pricing
# 4. Issues with support
```

**Expected outcomes**:
- Differentiation points for your own product
- Features to prioritize for implementation
- Hints for marketing messaging

### Use Case 3: Improving Customer Support

**Goal**: Identify issues that customers frequently encounter

```bash
# Regularly analyze threads about your own product
python3 goldmine_finder.py \
  --subreddit YourProductSubreddit \
  --limit 30 \
  --min-comments 3 \
  --output support_insights/

# Review the category-based analysis for:
# - Technical issues
# - UI/UX problems
# - Gaps in documentation
```

**Expected outcomes**:
- Common question patterns
- Areas for documentation improvement
- Early detection of product bugs

### Use Case 4: Finding Content Marketing Ideas

**Goal**: Discover topics that your target audience cares about

```bash
# Analyze subreddits where your target audience gathers
python3 goldmine_finder.py \
  --subreddit Entrepreneur \
  --limit 25 \
  --output content_ideas/

# From the key insights section:
# - Blog post topics
# - YouTube video ideas
# - Webinar themes
```

**Expected outcomes**:
- Data-driven content ideas
- Actual language and phrasing used by real users
- Stories that resonate with your audience

---

## How to Read Reports

### Report Structure

```
report_xxx.md
├── Thread Information
├── Discovered Pain Points
├── Key Insights
├── Market Opportunities
└── Overall Sentiment Analysis
```

### Pain Point Evaluation Criteria

#### Severity

- **Critical**: Threatens the viability of the business
- **High**: Causes significant losses or inefficiencies
- **Medium**: Room for improvement
- **Low**: Minor inconvenience

#### Purchase Intent

- **$$$ (High)**: Wants a solution immediately; ready to pay
- **$$ (Medium)**: Would consider purchasing if a good solution exists
- **$ (Low)**: Would try it if it were free
- **None**: Just venting; not looking for a solution

### How to Prioritize

1. **Purchase Intent High x Severity High** -- Top priority
2. **Purchase Intent High x Severity Medium** -- Address early
3. **Purchase Intent Medium x Severity High** -- Worth considering
4. **All others** -- Reference information

### Using Summary Reports

```markdown
# Structure of summary_xxx.md

## Top Pain Points Ranking
-> Sorted by purchase intent across all threads
-> The most market-viable problems at a glance

## Category-Based Analysis
-> Which areas have concentrated problems
-> Compare against your own strengths

## Integrated Market Opportunities
-> Specific business ideas suggested by AI
-> List of hypotheses to validate
```

---

## Troubleshooting

### Common Issues

#### 1. "Error: Failed to fetch data"

**Cause**:
- Network issues
- Reddit API rate limiting
- Invalid URL

**Solution**:
```bash
# Increase the rate limit delay
# Change rate_limit_delay to 3 in reddit_fetcher.py

# Verify the URL
# Correct format: https://www.reddit.com/r/subreddit/comments/id/title/

# Check network connectivity
curl -I https://old.reddit.com
```

#### 2. "AI analysis error"

**Cause**:
- OpenAI API key is not set
- API quota exceeded
- Network issues

**Solution**:
```bash
# Check the API key
echo $OPENAI_API_KEY

# Re-set the key
export OPENAI_API_KEY="your-key-here"

# Switch to a different model (a more affordable one)
# Change to model="gpt-4.1-nano" in ai_analyzer.py
```

#### 3. "Too few comments"

**Cause**:
- The thread genuinely has few comments
- Reddit's "more comments" have not been expanded

**Solution**:
```bash
# Choose more active threads
python3 goldmine_finder.py \
  --subreddit Entrepreneur \
  --min-comments 15  # Raise the minimum comment threshold
```

#### 4. "Analysis results don't match expectations"

**Cause**:
- Differences in AI model interpretation
- Prompt adjustments needed

**Solution**:
```python
# Adjust the prompt in the _analyze_with_ai method in ai_analyzer.py
# Example: Add more specific instructions
# Example: Explain industry-specific terminology
```

### Debug Mode

```bash
# Output detailed logs
python3 goldmine_finder.py --url "..." 2>&1 | tee debug.log

# Inspect JSON data
cat output/thread_xxx.json | python3 -m json.tool | less

# Inspect analysis data
cat output/analysis_xxx.json | python3 -m json.tool | less
```

---

## Best Practices

### 1. Choose High-Quality Threads

**Good examples**:
- 10 or more comments
- Discusses specific problems
- Active exchange of opinions

**Bad examples**:
- 3 or fewer comments
- Purely promotional
- Heavy trolling

### 2. Validate from Multiple Perspectives

```bash
# Analyze the same topic across multiple subreddits
python3 goldmine_finder.py --subreddit Entrepreneur --output view1/
python3 goldmine_finder.py --subreddit startups --output view2/
python3 goldmine_finder.py --subreddit smallbusiness --output view3/

# Look for common pain points
```

### 3. Monitor Regularly

```bash
# Track trends on a weekly basis
cat > weekly_monitor.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
python3 goldmine_finder.py \
  --subreddit YourTargetSubreddit \
  --limit 20 \
  --output "weekly_$DATE/"
EOF

chmod +x weekly_monitor.sh
```

### 4. Read the Actual Comments

Do not rely solely on the AI analysis results -- always read the original comments as well:

```bash
# Check the "Actual Comment Examples" section in the report
# Visit the original thread to understand the context
```

---

## Next Steps

1. **Run the demo**: `python3 demo.py`
2. **Analyze a subreddit you're interested in**: `python3 goldmine_finder.py --subreddit ...`
3. **Read the report**: `cat output/report_xxx.md`
4. **Validate the pain points**: Interview real users
5. **Turn your product idea into reality**: Build a prototype

---

**Happy Goldmining!**
