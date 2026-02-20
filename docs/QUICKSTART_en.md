# Quick Start Guide

**Get up and running with Reddit Goldmine Analyzer in 5 minutes**

---

## Step 1: Setup (1 minute)

```bash
# Navigate to the project directory
cd reddit_goldmine_analyzer

# Verify the files are in place
ls -l
```

**Prerequisites**:
- Python 3.11+
- An OpenAI API key (set as an environment variable)
- Internet connection

---

## Step 2: Run the Demo (1 minute)

```bash
# Run the demo script
python demo.py
```

**Expected output**:
```
======================================================================
Reddit Goldmine Analyzer - Demo
======================================================================

Loaded sample data: thread_1pyxz90.json

Thread title: Episode 001: Christian Reed...
Comments: 20
Score: 10

Running AI analysis...

======================================================================
Analysis Results
======================================================================

Pain points found: 5

1. Podcast distribution is limited to few platforms...
   Purchase Intent: HIGH
   Category: Marketing & Distribution

...
```

---

## Step 3: Review the Report (1 minute)

```bash
# View the generated report
cat report_1pyxz90.md
```

**Report structure**:
- Pain points discovered (ranked by purchase intent)
- Key insights
- Market opportunities
- Overall sentiment analysis

---

## Step 4: Analyze a Real Thread (2 minutes)

### 4-1. Find a Reddit Thread

1. Go to [reddit.com](https://reddit.com)
2. Pick a subreddit you are interested in (e.g., r/Entrepreneur)
3. Find a thread with a healthy number of comments
4. Copy the URL

**Example**: `https://www.reddit.com/r/Entrepreneur/comments/xxx/my_pain_points/`

### 4-2. Run the Analysis

```bash
# Analyze by URL
python goldmine_finder.py --url "YOUR_URL_HERE"
```

**Full example**:
```bash
python goldmine_finder.py \
  --url "https://www.reddit.com/r/Entrepreneur/comments/1r1699p/how_other_founders_monitor_reddit_without_spam/"
```

### 4-3. Check the Results

```bash
# List output files
ls output/

# View the report
cat output/report_*.md
```

---

## Next Steps

### Analyze an Entire Subreddit

```bash
# Analyze the top 10 threads in r/SaaS
python goldmine_finder.py \
  --subreddit SaaS \
  --limit 10 \
  --min-comments 5
```

### View the Summary Report

```bash
# Generated automatically after a subreddit analysis
cat output/summary_SaaS.md
```

### Compare Multiple Subreddits

```bash
# Analyze the same topic from different angles
python goldmine_finder.py --subreddit Entrepreneur --output entrepreneur/
python goldmine_finder.py --subreddit startups --output startups/
python goldmine_finder.py --subreddit smallbusiness --output smallbusiness/

# Look for overlapping high-intent pain points
grep "HIGH" entrepreneur/summary_*.md
grep "HIGH" startups/summary_*.md
grep "HIGH" smallbusiness/summary_*.md
```

---

## Web UI

You can also use the Streamlit-based web interface:

```bash
streamlit run app.py
```

This opens an interactive dashboard where you can paste a Reddit URL, run the analysis, and browse the results visually.

---

## Frequently Asked Questions

### Q1: I get "Error: Failed to fetch data"

**A**: This is usually a network issue or Reddit rate-limiting. Wait a few seconds and try again.

```bash
# Retry
python goldmine_finder.py --url "YOUR_URL_HERE"
```

### Q2: The analysis takes a long time

**A**: This is normal. Each thread takes roughly 5--15 seconds depending on its size.

- More comments means longer processing time
- The AI analysis itself takes a few seconds
- Rate-limit back-off may add waiting time

### Q3: I want faster results

**A**: Switch to a lighter model.

```python
# In ai_analyzer.py
analyzer = AIAnalyzer(model="gpt-4.1-nano")  # Faster and cheaper
```

### Q4: How much does it cost?

**A**: Roughly $0.01--0.05 per thread.

- **gpt-4.1-nano** -- cheapest option
- **gpt-4.1-mini** -- balanced (recommended default)

---

## Useful Commands

### Show Help

```bash
python goldmine_finder.py --help
```

### Specify an Output Directory

```bash
python goldmine_finder.py \
  --subreddit SaaS \
  --output my_analysis/
```

### Set a Minimum Comment Threshold

```bash
python goldmine_finder.py \
  --subreddit Entrepreneur \
  --min-comments 15
```

### Batch Processing

```bash
# Create a list of URLs
cat > urls.txt << EOF
https://www.reddit.com/r/SaaS/comments/xxx/
https://www.reddit.com/r/startups/comments/yyy/
EOF

# Analyze them all at once
python goldmine_finder.py --batch urls.txt
```

---

## Learning Resources

### Documentation

1. **README.md** -- Project overview
2. **USAGE_GUIDE.md** -- Detailed usage instructions
3. **PROJECT_OVERVIEW.md** -- Architecture and technical details

### Practical Examples

```bash
# Example 1: Discover SaaS founder pain points
python goldmine_finder.py --subreddit SaaS --limit 20

# Example 2: Research indie hacker needs
python goldmine_finder.py --subreddit indiehackers --limit 15

# Example 3: Deep-dive into a specific thread
python goldmine_finder.py \
  --url "https://www.reddit.com/r/Entrepreneur/comments/xxx/pain_points/"
```

---

## Troubleshooting

### If Something Goes Wrong

1. **Read the error message** -- it usually points to the cause.
2. **Check your network connection.**
3. **Verify your API key**: `echo $OPENAI_API_KEY`
4. **Re-run the demo**: `python demo.py`

### Further Help

- See README.md for a project overview
- See USAGE_GUIDE.md for in-depth instructions
- Read the inline code comments for implementation details

---

## Tips for Best Results

### 1. Choose High-Quality Threads

**Good candidates**:
- 10+ comments
- Concrete problem discussions
- Active back-and-forth conversation

**Avoid**:
- Threads with very few comments
- Mostly self-promotion
- Troll-heavy threads

### 2. Cross-Reference Across Subreddits

Analyze the same topic in multiple subreddits and look for pain points that keep coming up.

### 3. Read the Original Comments

AI analysis is a starting point. Always go back and read the actual comments for nuance and context.

### 4. Monitor Regularly

Run the same subreddit analysis weekly or monthly to track emerging trends over time.

---

**You are all set!**

**Happy Goldmining!**

---

Next up: read [USAGE_GUIDE_en.md](USAGE_GUIDE_en.md) for the full usage reference.
