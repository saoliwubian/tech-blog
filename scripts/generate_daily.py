"""
TechPulse AI Daily Report Generator
====================================
Runs in GitHub Actions to automatically generate AI industry daily reports.

Usage:
  python scripts/generate_daily.py

Environment Variables:
  LLM_API_KEY    - API key for OpenAI-compatible LLM (required)
  LLM_BASE_URL   - API base URL (default: https://api.deepseek.com)
  LLM_MODEL      - Model name (default: deepseek-chat)
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

# Timezone: UTC+8 (Beijing)
CST = timezone(timedelta(hours=8))
TODAY = datetime.now(CST)
DATE_STR = TODAY.strftime("%Y-%m-%d")
YEAR = TODAY.strftime("%Y")
MONTH_DAY = f"{TODAY.strftime('%m')}月{TODAY.strftime('%d')}日"
WEEKDAY_MAP = ["一", "二", "三", "四", "五", "六", "日"]
WEEKDAY = WEEKDAY_MAP[TODAY.weekday()]

# Paths
BLOG_ROOT = Path(__file__).resolve().parent.parent
AI_DAILY_DIR = BLOG_ROOT / "public" / "ai-daily"
INDEX_HTML = AI_DAILY_DIR / "index.html"
STYLE_CSS = AI_DAILY_DIR / "style.css"
TEMPLATE_HTML = AI_DAILY_DIR / "2026-06-06.html"  # Use as template reference

# LLM Config
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "") or "https://api.deepseek.com"
LLM_MODEL = os.environ.get("LLM_MODEL", "") or "deepseek-chat"

# RSS Feed Sources
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.technologyreview.com/feed/",
    "https://arstechnica.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
]

# ─── Helpers ──────────────────────────────────────────────────────────────

def fetch_url(url: str, timeout: int = 15) -> str | None:
    """Fetch URL content with urllib (no external deps needed)."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (TechPulse Bot; +https://github.com/saoliwubian/tech-blog)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def parse_rss(xml_text: str, source_name: str, max_items: int = 5) -> list[dict]:
    """Parse RSS/Atom feed and return list of articles."""
    articles = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return articles

    # RSS 2.0
    for item in root.iter("item"):
        if len(articles) >= max_items:
            break
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        desc = item.findtext("description", "")
        pub_date = item.findtext("pubDate", "")
        if title:
            articles.append({
                "source": source_name,
                "title": title.strip(),
                "link": link.strip(),
                "description": desc.strip()[:300],
                "pub_date": pub_date.strip(),
            })

    # Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", ns):
        if len(articles) >= max_items:
            break
        title = entry.findtext("atom:title", "", ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary = entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns)
        if title:
            articles.append({
                "source": source_name,
                "title": title.strip(),
                "link": link.strip(),
                "description": summary.strip()[:300],
                "pub_date": "",
            })

    return articles


def fetch_all_rss() -> list[dict]:
    """Fetch all RSS feeds and return combined articles."""
    all_articles = []
    for feed_url in RSS_FEEDS:
        source_name = feed_url.split("/")[2]
        print(f"  Fetching {source_name}...")
        xml = fetch_url(feed_url)
        if xml:
            articles = parse_rss(xml, source_name)
            all_articles.extend(articles)
            print(f"    → {len(articles)} articles")
    return all_articles


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """Call OpenAI-compatible LLM API."""
    import urllib.request
    import urllib.error

    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    })

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] LLM API call failed: {e}", file=sys.stderr)
        raise


def generate_report(articles: list[dict]) -> dict:
    """Use LLM to analyze articles and generate structured report."""
    articles_text = "\n\n".join(
        f"[{i+1}] 来源: {a['source']}\n标题: {a['title']}\n链接: {a['link']}\n摘要: {a['description']}"
        for i, a in enumerate(articles)
    )

    system_prompt = """你是 TechPulse AI 日报编辑。你需要根据提供的 AI 行业新闻素材，生成结构化的日报内容。

输出格式为严格 JSON，不要包含任何其他文本。JSON 结构如下：

{
  "headline": {
    "title": "头条标题",
    "body": "头条正文（150-300字，用 <strong> 标签标注关键信息）",
    "source_name": "来源名称",
    "source_url": "来源链接"
  },
  "analysis": [
    {
      "title": "分析标题",
      "body": "分析正文（100-200字，用 <strong> 标签标注关键信息）",
      "impact": "high/medium/low",
      "tags": ["标签1", "标签2", "标签3"],
      "source_name": "来源名称",
      "source_url": "来源链接"
    }
  ],
  "quick_glance": [
    {
      "text": "一句话概括",
      "source_name": "来源名称",
      "source_url": "来源链接"
    }
  ],
  "mermaid_charts": [
    {
      "title": "图表标题",
      "type": "bar/pie/flowchart/quadrant",
      "code": "Mermaid 代码"
    }
  ]
}

要求：
1. 头条选影响最大的 1 条
2. 重点分析 3-6 条（优先选择有具体数据和技术细节的）
3. 速览 2-4 条
4. 生成 1-2 张 Mermaid 图表（柱状图用 xychart-beta，饼图用 pie，流程图用 flowchart）
5. 所有内容必须基于提供的素材，不得编造
6. 中文输出，技术术语保留英文
7. 如果素材不足，分析可以少放，但头条必须有
8. impact 只能是 high/medium/low"""

    user_prompt = f"""今天是 {DATE_STR}，以下是今天收集到的 AI 行业新闻素材：

{articles_text}

请生成今天的 AI 行业日报。"""

    response = call_llm(system_prompt, user_prompt, max_tokens=4096)

    # Extract JSON from response (handle markdown code blocks)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        response = json_match.group(1)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to find JSON object directly
        brace_start = response.find("{")
        brace_end = response.rfind("}") + 1
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(response[brace_start:brace_end])
            except json.JSONDecodeError:
                pass
        print(f"[ERROR] Failed to parse LLM response as JSON", file=sys.stderr)
        print(f"Response: {response[:500]}", file=sys.stderr)
        raise


def compute_issue_number() -> int:
    """Compute the issue number by counting existing daily HTML files."""
    existing = list(AI_DAILY_DIR.glob("????-??-??.html"))
    return len(existing) + 1


IMPACT_MAP = {
    "high": "🔥 高影响",
    "medium": "⚡ 中影响",
    "low": "💡 低影响",
}
IMPACT_CLASS = {
    "high": "severity-high",
    "medium": "severity-medium",
    "low": "severity-low",
}


def render_html(report: dict, issue_number: int) -> str:
    """Render the daily report as HTML."""

    # ── Headline ──
    hl = report["headline"]
    headline_html = f"""    <section class="headline">
      <div class="headline-label">📰 头条</div>
      <h1 class="headline-title">{hl['title']}</h1>
      <div class="headline-body">
        {hl['body']}
      </div>
      <div class="headline-source">
        来源：<a href="{hl['source_url']}" target="_blank" rel="noopener">{hl['source_name']}</a>
      </div>
    </section>"""

    # ── Analysis Cards ──
    analysis_cards = []
    for i, a in enumerate(report["analysis"], 1):
        impact = a.get("impact", "medium")
        impact_label = IMPACT_MAP.get(impact, "⚡ 中影响")
        impact_cls = IMPACT_CLASS.get(impact, "severity-medium")
        tags_html = "\n          ".join(
            f'<span class="tag">{t}</span>'
            for t in a.get("tags", [])
        )
        analysis_cards.append(f"""      <div class="analysis-card">
        <div class="analysis-card-header">
          <span class="analysis-index">#{i}</span>
          <h3 class="analysis-title">{a['title']}</h3>
        </div>
        <div class="analysis-body">
          {a['body']}
        </div>
        <div class="analysis-tags">
          <span class="tag {impact_cls}">{impact_label}</span>
          {tags_html}
        </div>
        <div class="analysis-source">
          来源：<a href="{a['source_url']}" target="_blank" rel="noopener">{a['source_name']}</a>
        </div>
      </div>""")

    analysis_count = len(analysis_cards)
    analysis_section = f"""    <section class="section">
      <div class="section-header">
        <span class="section-icon">🔍</span>
        <h2 class="section-title">重点分析</h2>
        <span class="section-count">{analysis_count} 条</span>
      </div>
{chr(10).join(analysis_cards)}
    </section>"""

    # ── Quick Glance ──
    quick_items = []
    for q in report.get("quick_glance", []):
        quick_items.append(f"""        <div class="quick-item">
          <span class="quick-bullet">▸</span>
          <span>{q['text']}</span>
          <span class="quick-source"><a href="{q['source_url']}" target="_blank" rel="noopener">{q['source_name']}</a></span>
        </div>""")

    quick_count = len(quick_items)
    quick_section = f"""    <section class="section">
      <div class="section-header">
        <span class="section-icon">⚡</span>
        <h2 class="section-title">速览</h2>
        <span class="section-count">{quick_count} 条</span>
      </div>
      <div class="quick-glance">
{chr(10).join(quick_items)}
      </div>
    </section>"""

    # ── Visualization ──
    viz_items = []
    for chart in report.get("mermaid_charts", []):
        viz_items.append(f"""      <div class="viz-container">
        <div class="viz-title">{chart['title']}</div>
        <div class="mermaid">
{chart['code']}
        </div>
      </div>""")

    viz_count = len(viz_items)
    viz_section = f"""    <section class="section">
      <div class="section-header">
        <span class="section-icon">📊</span>
        <h2 class="section-title">可视化</h2>
        <span class="section-count">{viz_count} 张</span>
      </div>
{chr(10).join(viz_items)}
    </section>"""

    # ── Source Links ──
    all_sources = []
    idx = 1
    all_sources.append({"name": hl["source_name"], "url": hl["source_url"]})
    for a in report["analysis"]:
        all_sources.append({"name": a["source_name"], "url": a["source_url"]})
    for q in report.get("quick_glance", []):
        all_sources.append({"name": q["source_name"], "url": q["source_url"]})

    # Deduplicate
    seen = set()
    unique_sources = []
    for s in all_sources:
        key = s["url"]
        if key not in seen:
            seen.add(key)
            unique_sources.append(s)

    source_items = []
    for i, s in enumerate(unique_sources, 1):
        source_items.append(f"""        <div class="quick-item">
          <span class="quick-bullet">{i}.</span>
          <span><a href="{s['url']}" target="_blank" rel="noopener" style="color:var(--accent-cyan);">{s['name']}</a></span>
        </div>""")

    source_section = f"""    <section class="section">
      <div class="section-header">
        <span class="section-icon">🔗</span>
        <h2 class="section-title">出处链接</h2>
      </div>
      <div class="quick-glance">
{chr(10).join(source_items)}
      </div>
    </section>"""

    # ── Compose Full HTML ──
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI 日报 {DATE_STR} — TechPulse</title>
  <meta name="description" content="{DATE_STR} AI 行业资讯日报：{hl['title']}" />
  <link rel="stylesheet" href="style.css" />
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
  <div class="container">
    <header class="masthead">
      <div class="masthead-title">TechPulse AI Daily</div>
      <div class="masthead-subtitle">AI 行业资讯日报</div>
      <div class="masthead-meta">
        <span class="masthead-edition">第 {issue_number:03d} 期</span>
        <span>{YEAR} 年 {MONTH_DAY} · 星期{WEEKDAY}</span>
        <div class="masthead-nav">
          <a href="index.html">← 目录</a>
          <a href="/">博客</a>
        </div>
      </div>
    </header>

{headline_html}

{analysis_section}

{quick_section}

{viz_section}

{source_section}

    <div class="report-footer">
      <p>本文由 AI 自动搜索、筛选、整理生成 · 内容仅供参考</p>
      <p><a href="index.html">← 返回日报目录</a> · <a href="/">返回博客</a></p>
    </div>
  </div>

  <button class="back-top" id="backTop" title="回到顶部">↑</button>

  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'dark',
      themeVariables: {{
        primaryColor: '#e8a849',
        primaryTextColor: '#e8e0d4',
        primaryBorderColor: '#333330',
        lineColor: '#a89e90',
        secondaryColor: '#2a2520',
        tertiaryColor: '#1a1a1a',
        background: '#222222',
        mainBkg: '#2a2520',
        nodeBorder: '#e8a849',
        clusterBkg: '#1a1a1a',
        titleColor: '#e8a849',
        edgeLabelBackground: '#222222',
      }}
    }});

    const btn = document.getElementById('backTop');
    window.addEventListener('scroll', () => {{
      btn.classList.toggle('visible', window.scrollY > 400);
    }});
    btn.addEventListener('click', () => {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});
  </script>
</body>
</html>"""

    return html


def update_index(headline_title: str, analysis_count: int, quick_count: int, viz_count: int):
    """Update the index.html to include the new daily report entry."""
    content = INDEX_HTML.read_text(encoding="utf-8")

    # Remove all existing NEW badges
    content = content.replace('<span class="archive-badge badge-new">NEW</span>\n          <span class="archive-arrow">→</span>', '<span class="archive-arrow">→</span>')

    # Insert new entry before the empty-state div
    new_entry = f"""      <a class="archive-item" href="{DATE_STR}.html">
        <span class="archive-date">{DATE_STR}</span>
        <div class="archive-info">
          <div class="archive-title">{headline_title}</div>
          <div class="archive-desc">{analysis_count} 条重点 · {quick_count} 条速览 · {viz_count} 张图表</div>
        </div>
        <span class="archive-badge badge-new">NEW</span>
        <span class="archive-arrow">→</span>
      </a>
"""

    # Insert before the empty-state div
    marker = '      <div class="empty-state"'
    if marker in content:
        content = content.replace(marker, new_entry + marker)
    else:
        # Fallback: insert before </div> that closes archive-list
        content = content.replace(
            '    </div>\n\n    <!-- Footer -->',
            new_entry + '    </div>\n\n    <!-- Footer -->'
        )

    INDEX_HTML.write_text(content, encoding="utf-8")


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    print(f"=== TechPulse AI Daily Report Generator ===")
    print(f"Date: {DATE_STR} (星期{WEEKDAY})")
    print()

    if not LLM_API_KEY:
        print("[ERROR] LLM_API_KEY environment variable is required!", file=sys.stderr)
        sys.exit(1)

    # Step 1: Fetch RSS feeds
    print("[Step 1] Fetching RSS feeds...")
    articles = fetch_all_rss()
    print(f"  Total articles collected: {len(articles)}")

    if len(articles) < 3:
        print("[WARN] Too few articles collected. Generating a minimal report.", file=sys.stderr)

    # Step 2: Generate report via LLM
    print("[Step 2] Generating report via LLM...")
    report = generate_report(articles)
    print(f"  Headline: {report['headline']['title']}")
    print(f"  Analysis: {len(report.get('analysis', []))} items")
    print(f"  Quick glance: {len(report.get('quick_glance', []))} items")
    print(f"  Charts: {len(report.get('mermaid_charts', []))} items")

    # Step 3: Render HTML
    print("[Step 3] Rendering HTML...")
    issue_number = compute_issue_number()
    html = render_html(report, issue_number)

    output_path = AI_DAILY_DIR / f"{DATE_STR}.html"
    # Don't overwrite the template if it's the same date
    output_path.write_text(html, encoding="utf-8")
    print(f"  Written to: {output_path}")

    # Step 4: Update index
    print("[Step 4] Updating index page...")
    update_index(
        headline_title=report["headline"]["title"],
        analysis_count=len(report.get("analysis", [])),
        quick_count=len(report.get("quick_glance", [])),
        viz_count=len(report.get("mermaid_charts", [])),
    )
    print("  Index updated")

    # Step 5: Output summary for GitHub Actions
    print()
    print("=== Generation Complete ===")
    print(f"File: public/ai-daily/{DATE_STR}.html")
    print(f"Issue: #{issue_number:03d}")
    print(f"Headline: {report['headline']['title']}")


if __name__ == "__main__":
    main()
