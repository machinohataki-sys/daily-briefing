"""
信息源抓取模块 - Global Research Sources
全球顶级学术、财经、科技信息源
"""

import asyncio
import aiohttp
import feedparser
import re
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass
from html import unescape

@dataclass
class NewsItem:
    title: str
    summary: str
    source: str
    category: str
    url: str
    published: str
    tier: str  # 'academic' | 'top' | 'industry' | 'news'

# ============== 全球顶级信息源配置 ==============
RSS_SOURCES = {
    # 全球宏观经济与政策分析
    "economy": [
        {
            "name": "Reuters Business",
            "url": "https://feeds.reuters.com/reuters/businessNews",
            "tier": "top"
        },
        {
            "name": "BBC Business",
            "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
            "tier": "top"
        },
        {
            "name": "CNBC",
            "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
            "tier": "news"
        },
        {
            "name": "MarketWatch",
            "url": "https://feeds.marketwatch.com/marketwatch/topstories/",
            "tier": "news"
        },
    ],
    # AI技术与产业深度分析
    "ai_product": [
        {
            "name": "MIT Technology Review",
            "url": "https://www.technologyreview.com/feed/",
            "tier": "top"
        },
        {
            "name": "Wired",
            "url": "https://www.wired.com/feed/tag/ai/latest/rss",
            "tier": "top"
        },
        {
            "name": "Ars Technica",
            "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
            "tier": "top"
        },
        {
            "name": "The Verge AI",
            "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "tier": "news"
        },
        {
            "name": "TechCrunch AI",
            "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "tier": "industry"
        },
    ],
    # AI学术研究前沿
    "ai_research": [
        {
            "name": "arXiv cs.AI",
            "url": "https://rss.arxiv.org/rss/cs.AI",
            "tier": "academic"
        },
        {
            "name": "arXiv cs.LG",
            "url": "https://rss.arxiv.org/rss/cs.LG",
            "tier": "academic"
        },
        {
            "name": "arXiv cs.CL",
            "url": "https://rss.arxiv.org/rss/cs.CL",
            "tier": "academic"
        },
        {
            "name": "Google AI Blog",
            "url": "https://blog.google/technology/ai/rss/",
            "tier": "industry"
        },
    ],
}

def clean_html(text: str) -> str:
    """清理HTML标签，保留纯文本"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

async def fetch_rss(session: aiohttp.ClientSession, source: Dict, category: str) -> List[NewsItem]:
    """抓取单个RSS源"""
    items = []
    try:
        async with session.get(
            source["url"], 
            timeout=aiohttp.ClientTimeout(total=20),
            ssl=False
        ) as response:
            if response.status != 200:
                print(f"  ⚠️ {source['name']} 返回 {response.status}")
                return items
            
            content = await response.text()
            feed = feedparser.parse(content)
            
            for entry in feed.entries[:15]:
                title = clean_html(entry.get("title", ""))
                summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
                
                if not title:
                    continue
                
                items.append(NewsItem(
                    title=title,
                    summary=summary[:800],
                    source=source["name"],
                    category=category,
                    url=entry.get("link", ""),
                    published=entry.get("published", ""),
                    tier=source.get("tier", "news")
                ))
            
            print(f"  ✓ {source['name']}: {len(items)} 条")
            
    except asyncio.TimeoutError:
        print(f"  ⚠️ {source['name']} 超时")
    except Exception as e:
        print(f"  ⚠️ {source['name']} 错误: {str(e)[:80]}")
    
    return items

async def fetch_category(session: aiohttp.ClientSession, category: str, sources: List[Dict]) -> List[NewsItem]:
    """并发抓取一个分类下的所有源"""
    tasks = [fetch_rss(session, source, category) for source in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    items = []
    for result in results:
        if isinstance(result, list):
            items.extend(result)
    
    return items

async def fetch_all_sources() -> List[NewsItem]:
    """抓取所有信息源"""
    all_items = []
    
    async with aiohttp.ClientSession(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        }
    ) as session:
        for category, sources in RSS_SOURCES.items():
            category_name = {
                "economy": "🌍 全球经济与政策",
                "ai_product": "🤖 AI技术与产业", 
                "ai_research": "📚 AI学术研究"
            }.get(category, category)
            
            print(f"\n{category_name}:")
            items = await fetch_category(session, category, sources)
            all_items.extend(items)
    
    # 去重
    seen_titles = set()
    unique_items = []
    for item in all_items:
        title_key = item.title[:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_items.append(item)
    
    # 按tier排序
    tier_order = {"academic": 0, "top": 1, "industry": 2, "news": 3}
    unique_items.sort(key=lambda x: tier_order.get(x.tier, 4))
    
    return unique_items

def format_for_ai(items: List[NewsItem]) -> str:
    """将抓取的内容格式化为AI可处理的深度分析文本"""
    sections = {
        "economy": [],
        "ai_product": [],
        "ai_research": []
    }
    
    for item in items:
        sections[item.category].append(item)
    
    output = []
    
    if sections["economy"]:
        output.append("=" * 60)
        output.append("SECTION 1: GLOBAL ECONOMY & POLICY")
        output.append("=" * 60 + "\n")
        for i, item in enumerate(sections["economy"][:10], 1):
            output.append(f"[{i}] {item.title}")
            output.append(f"    Source: {item.source} | Tier: {item.tier}")
            output.append(f"    URL: {item.url}")
            if item.summary:
                output.append(f"    Summary: {item.summary}")
            output.append("")
    
    if sections["ai_product"]:
        output.append("\n" + "=" * 60)
        output.append("SECTION 2: AI TECHNOLOGY & INDUSTRY")
        output.append("=" * 60 + "\n")
        for i, item in enumerate(sections["ai_product"][:10], 1):
            output.append(f"[{i}] {item.title}")
            output.append(f"    Source: {item.source} | Tier: {item.tier}")
            output.append(f"    URL: {item.url}")
            if item.summary:
                output.append(f"    Summary: {item.summary}")
            output.append("")
    
    if sections["ai_research"]:
        output.append("\n" + "=" * 60)
        output.append("SECTION 3: AI ACADEMIC RESEARCH")
        output.append("=" * 60 + "\n")
        for i, item in enumerate(sections["ai_research"][:10], 1):
            output.append(f"[{i}] {item.title}")
            output.append(f"    Source: {item.source} | Tier: {item.tier}")
            output.append(f"    URL: {item.url}")
            if item.summary:
                output.append(f"    Summary: {item.summary}")
            output.append("")
    
    return "\n".join(output)

if __name__ == "__main__":
    async def test():
        items = await fetch_all_sources()
        print(f"\n总计抓取: {len(items)} 条")
        print(format_for_ai(items))
    
    asyncio.run(test())
