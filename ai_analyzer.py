#!/usr/bin/env python3
"""
AI Analyzer for Reddit Goldmine
Extracts pain points, purchase intent, and need patterns from Reddit comments using AI
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class PainPoint:
    """Pain point data"""
    description: str
    severity: str  # "low", "medium", "high", "critical"
    frequency_mentioned: int
    example_comments: List[str]
    purchase_intent: str  # "none", "low", "medium", "high"
    category: str


@dataclass
class AnalysisResult:
    """Analysis result"""
    thread_id: str
    thread_title: str
    total_comments: int
    pain_points: List[PainPoint]
    key_insights: List[str]
    market_opportunities: List[str]
    sentiment_summary: str


class AIAnalyzer:
    """AI Analysis Engine"""

    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Args:
            model: Model to use (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)
        """
        self.client = OpenAI()
        self.model = model

    def analyze_thread(self, thread_data: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze an entire thread to extract pain points, purchase intent, and market opportunities.

        Args:
            thread_data: Thread data fetched by reddit_fetcher.py

        Returns:
            AnalysisResult: Analysis results
        """
        # Flatten comments
        all_comments = self._flatten_comments(thread_data.get('comments', []))

        # Extract comment texts
        comment_texts = [c['body'] for c in all_comments if c['body'] and len(c['body']) > 10]

        print(f"Analyzing: processing {len(comment_texts)} comments...")

        # Batch AI analysis
        analysis = self._analyze_with_ai(
            thread_title=thread_data.get('title', ''),
            thread_body=thread_data.get('selftext', ''),
            comments=comment_texts[:100]  # Up to 100 comments
        )

        return AnalysisResult(
            thread_id=thread_data.get('id', ''),
            thread_title=thread_data.get('title', ''),
            total_comments=len(comment_texts),
            pain_points=analysis['pain_points'],
            key_insights=analysis['key_insights'],
            market_opportunities=analysis['market_opportunities'],
            sentiment_summary=analysis['sentiment_summary']
        )

    def _flatten_comments(self, comments: List[Dict], result: List[Dict] = None) -> List[Dict]:
        """Recursively flatten comments"""
        if result is None:
            result = []

        for comment in comments:
            result.append(comment)
            if comment.get('replies'):
                self._flatten_comments(comment['replies'], result)

        return result

    def _analyze_with_ai(self, thread_title: str, thread_body: str, comments: List[str]) -> Dict[str, Any]:
        """Analyze comments using AI"""

        # Combine comments
        comments_text = "\n\n---\n\n".join([f"Comment {i+1}: {c}" for i, c in enumerate(comments[:50])])

        prompt = f"""You are an expert in market research and business opportunity discovery.
Analyze the following Reddit thread and comments, then extract customer "pain points", "purchase intent", and "market opportunities".

【Thread Title】
{thread_title}

【Thread Body】
{thread_body}

【Comments】
{comments_text}

Return the analysis results in the following JSON format:

{{
  "pain_points": [
    {{
      "description": "Description of the pain point",
      "severity": "one of: low/medium/high/critical",
      "frequency_mentioned": estimated number of times mentioned in comments,
      "example_comments": ["actual comment example 1", "actual comment example 2"],
      "purchase_intent": "one of: none/low/medium/high",
      "category": "category name (e.g., Marketing, Finance, Operations, Technology, etc.)"
    }}
  ],
  "key_insights": [
    "Important insight 1",
    "Important insight 2",
    "Important insight 3"
  ],
  "market_opportunities": [
    "Market opportunity 1: specific product/service idea",
    "Market opportunity 2: specific product/service idea"
  ],
  "sentiment_summary": "Summary of overall sentiment (positive/negative/neutral, with reasoning)"
}}

Important instructions:
1. Focus on specific, actionable pain points
2. Evaluate purchase intent by the urgency of "I need a solution right now"
3. Focus market opportunities on products/services that can actually be sold
4. Prioritize problems people would "pay money to solve"
5. Always respond in JSON format only (no other text)
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a market research expert. Respond only in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            # Convert to PainPoint objects
            pain_points = []
            for pp in result.get('pain_points', []):
                pain_points.append(PainPoint(
                    description=pp.get('description', ''),
                    severity=pp.get('severity', 'medium'),
                    frequency_mentioned=pp.get('frequency_mentioned', 0),
                    example_comments=pp.get('example_comments', []),
                    purchase_intent=pp.get('purchase_intent', 'none'),
                    category=pp.get('category', 'Other')
                ))

            return {
                'pain_points': pain_points,
                'key_insights': result.get('key_insights', []),
                'market_opportunities': result.get('market_opportunities', []),
                'sentiment_summary': result.get('sentiment_summary', '')
            }

        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                'pain_points': [],
                'key_insights': [],
                'market_opportunities': [],
                'sentiment_summary': 'Analysis failed due to an error'
            }

    def save_analysis(self, result: AnalysisResult, filepath: str):
        """Save analysis results to a JSON file"""
        data = {
            'thread_id': result.thread_id,
            'thread_title': result.thread_title,
            'total_comments': result.total_comments,
            'pain_points': [
                {
                    'description': pp.description,
                    'severity': pp.severity,
                    'frequency_mentioned': pp.frequency_mentioned,
                    'example_comments': pp.example_comments,
                    'purchase_intent': pp.purchase_intent,
                    'category': pp.category
                }
                for pp in result.pain_points
            ],
            'key_insights': result.key_insights,
            'market_opportunities': result.market_opportunities,
            'sentiment_summary': result.sentiment_summary
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Analysis saved: {filepath}")

    def generate_report(self, result: AnalysisResult) -> str:
        """Generate a human-readable report from analysis results"""
        report = f"""
# Reddit Goldmine Analysis Report

## Thread Info
- **Title**: {result.thread_title}
- **Thread ID**: {result.thread_id}
- **Comments Analyzed**: {result.total_comments}

---

## Pain Points Discovered

"""

        # Sort by purchase intent (highest first)
        intent_order = {'high': 4, 'medium': 3, 'low': 2, 'none': 1}
        sorted_pain_points = sorted(
            result.pain_points,
            key=lambda x: (intent_order.get(x.purchase_intent, 0), x.frequency_mentioned),
            reverse=True
        )

        for i, pp in enumerate(sorted_pain_points, 1):
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(pp.severity, '⚪')

            intent_emoji = {
                'high': '💰💰💰',
                'medium': '💰💰',
                'low': '💰',
                'none': '⚫'
            }.get(pp.purchase_intent, '⚫')

            report += f"""
### {i}. {pp.description}

- **Severity**: {severity_emoji} {pp.severity.upper()}
- **Purchase Intent**: {intent_emoji} {pp.purchase_intent.upper()}
- **Frequency**: mentioned {pp.frequency_mentioned} time(s)
- **Category**: {pp.category}

**Example Comments**:
"""
            for example in pp.example_comments[:2]:
                report += f'> {example}\n\n'

            report += "\n"

        report += f"""
---

## Key Insights

"""
        for insight in result.key_insights:
            report += f"- {insight}\n"

        report += f"""
---

## Market Opportunities

"""
        for opportunity in result.market_opportunities:
            report += f"- {opportunity}\n"

        report += f"""
---

## Sentiment Analysis

{result.sentiment_summary}

---

**Analysis completed at**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return report


# Test
if __name__ == "__main__":
    import glob

    thread_files = glob.glob("thread_*.json")
    if not thread_files:
        print("No thread data found for analysis.")
        print("Please run reddit_fetcher.py first.")
    else:
        analyzer = AIAnalyzer()

        for thread_file in thread_files[:1]:
            print(f"\n{'='*60}")
            print(f"Starting analysis: {thread_file}")
            print(f"{'='*60}\n")

            with open(thread_file, 'r', encoding='utf-8') as f:
                thread_data = json.load(f)

            result = analyzer.analyze_thread(thread_data)

            # Save results
            analysis_file = thread_file.replace('thread_', 'analysis_')
            analyzer.save_analysis(result, analysis_file)

            # Generate report
            report = analyzer.generate_report(result)
            report_file = thread_file.replace('thread_', 'report_').replace('.json', '.md')

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"\nReport saved: {report_file}")
            print(f"\n{report}")
