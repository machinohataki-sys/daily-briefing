"""
报告生成模块 - Academic Research Report Generator
生成学术级别的精美HTML邮件报告
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_processor import DailyBriefing

def markdown_to_html(text: str) -> str:
    """将Markdown格式转换为HTML"""
    if not text:
        return "<p>暂无内容</p>"
    
    # 处理Markdown链接格式 [text](url)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" style="color: #0066cc; text-decoration: underline;">\1</a>',
        text
    )
    
    # 处理独立的URL（带协议）
    text = re.sub(
        r'(?<!["\'>])(?<![=])(https?://[^\s<>\'")\]]+)',
        r'<a href="\1" style="color: #0066cc; text-decoration: underline;">\1</a>',
        text
    )
    
    # 处理不带协议的常见域名URL（如 example.com/path）
    # 匹配: 域名.后缀/路径 格式
    text = re.sub(
        r'(?<![/"\'@=])(?<![a-zA-Z0-9])((?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s<>\'")\]]*)?)',
        lambda m: f'<a href="https://{m.group(1)}" style="color: #0066cc; text-decoration: underline;">{m.group(1)}</a>' if '.' in m.group(1) and not m.group(1).endswith('.') else m.group(0),
        text
    )
    
    # 处理引用块 (blockquote)
    text = re.sub(
        r'^>\s*"(.+?)"$',
        r'<blockquote class="quote">"\1"</blockquote>',
        text,
        flags=re.MULTILINE
    )
    text = re.sub(
        r'^>\s*(.+)$',
        r'<blockquote>\1</blockquote>',
        text,
        flags=re.MULTILINE
    )
    
    # 合并连续的blockquote
    text = re.sub(
        r'</blockquote>\s*<blockquote>',
        '<br>',
        text
    )
    
    # 处理三级标题
    text = re.sub(r'^###\s+(.+)$', r'<h4 class="subsection">\1</h4>', text, flags=re.MULTILINE)
    
    # 处理粗体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # 处理列表项
    text = re.sub(r'^[-•]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\.\s+(.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)
    
    # 包装列表
    if '<li>' in text:
        # 简单处理：将连续的li包装在ul中
        text = re.sub(r'((?:<li>.*?</li>\s*)+)', r'<ul>\1</ul>', text, flags=re.DOTALL)
    
    # 处理段落
    paragraphs = text.split('\n\n')
    processed = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if not any(p.startswith(tag) for tag in ['<h', '<ul', '<ol', '<blockquote', '<div', '<li>']):
            if not p.startswith('<p>'):
                p = f'<p>{p}</p>'
        processed.append(p)
    
    return '\n'.join(processed)

def generate_html_report(briefing: "DailyBriefing") -> str:
    """生成学术级HTML格式的邮件报告"""
    
    # 处理AI生成的内容
    executive_summary_html = markdown_to_html(briefing.executive_summary)
    economy_html = markdown_to_html(briefing.economy_analysis)
    ai_industry_html = markdown_to_html(briefing.ai_industry_analysis)
    ai_research_html = markdown_to_html(briefing.ai_research_analysis)
    learning_html = markdown_to_html(briefing.learning_agenda)
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Intelligence Briefing | {briefing.date}</title>
    <style>
        /* Reset and base */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
            line-height: 1.8;
            color: #1a1a2e;
            background: #f8f9fa;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 40px 50px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        
        .header .subtitle {{
            font-size: 14px;
            opacity: 0.85;
            font-weight: 400;
        }}
        
        .header .date {{
            font-size: 13px;
            opacity: 0.7;
            margin-top: 12px;
        }}
        
        /* Content sections */
        .content {{
            padding: 40px 50px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .section-icon {{
            font-size: 24px;
            margin-right: 12px;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            color: #1a1a2e;
        }}
        
        .section-title-sub {{
            font-size: 14px;
            color: #6c757d;
            font-weight: 400;
            margin-left: 8px;
        }}
        
        /* Executive summary */
        .executive-summary {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 4px solid #1a1a2e;
            padding: 25px 30px;
            margin-bottom: 30px;
            border-radius: 0 8px 8px 0;
        }}
        
        .executive-summary p {{
            font-size: 15px;
            color: #333;
            margin-bottom: 12px;
        }}
        
        .executive-summary p:last-child {{
            margin-bottom: 0;
        }}
        
        /* Subsections */
        h4.subsection {{
            font-size: 17px;
            font-weight: 600;
            color: #16213e;
            margin: 25px 0 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        /* Blockquotes for original quotes */
        blockquote {{
            background: #f8f9fa;
            border-left: 3px solid #6c757d;
            padding: 15px 20px;
            margin: 15px 0;
            font-style: italic;
            color: #495057;
            border-radius: 0 6px 6px 0;
        }}
        
        blockquote.quote {{
            background: linear-gradient(135deg, #fff9e6 0%, #fff5d6 100%);
            border-left-color: #ffc107;
            font-style: normal;
        }}
        
        /* Typography */
        p {{
            margin-bottom: 15px;
            font-size: 15px;
            color: #333;
        }}
        
        strong {{
            font-weight: 600;
            color: #1a1a2e;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 15px 0 15px 25px;
        }}
        
        li {{
            margin-bottom: 10px;
            font-size: 14px;
            color: #444;
        }}
        
        li strong {{
            color: #0f3460;
        }}
        
        /* Learning agenda special styling */
        .learning-section {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            padding: 25px 30px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .learning-section h4 {{
            color: #2e7d32;
            border-bottom-color: #81c784;
        }}
        
        /* Footer */
        .footer {{
            background: #f8f9fa;
            padding: 25px 50px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}
        
        .footer p {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        
        /* Responsive */
        @media (max-width: 600px) {{
            .header, .content, .footer {{
                padding-left: 25px;
                padding-right: 25px;
            }}
            
            .header h1 {{
                font-size: 22px;
            }}
            
            .section-title {{
                font-size: 18px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Research Intelligence Briefing</h1>
            <div class="subtitle">全球经济与AI技术深度研究日报</div>
            <div class="date">{briefing.date} | Generated by AI Research Assistant</div>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📋</span>
                    <span class="section-title">Executive Summary</span>
                    <span class="section-title-sub">执行摘要</span>
                </div>
                <div class="executive-summary">
                    {executive_summary_html}
                </div>
            </div>
            
            <!-- Global Economy -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🌍</span>
                    <span class="section-title">Global Economy & Policy</span>
                    <span class="section-title-sub">全球经济与政策</span>
                </div>
                {economy_html}
            </div>
            
            <!-- AI Technology -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🤖</span>
                    <span class="section-title">AI Technology & Industry</span>
                    <span class="section-title-sub">AI技术与产业</span>
                </div>
                {ai_industry_html}
            </div>
            
            <!-- AI Research -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">📚</span>
                    <span class="section-title">AI Research Frontiers</span>
                    <span class="section-title-sub">AI学术前沿</span>
                </div>
                {ai_research_html}
            </div>
            
            <!-- Learning Agenda -->
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🎯</span>
                    <span class="section-title">Today's Learning Agenda</span>
                    <span class="section-title-sub">今日学习议程</span>
                </div>
                <div class="learning-section">
                    {learning_html}
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>This briefing was generated by AI based on publicly available sources.</p>
            <p>Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            <p style="margin-top: 10px; font-size: 11px; color: #999;">
                Sources: Financial Times, The Economist, Reuters, MIT Tech Review, arXiv, and more
            </p>
        </div>
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    from dataclasses import dataclass
    
    @dataclass
    class MockBriefing:
        date: str = "2024-01-15"
        executive_summary: str = """**English:** The Federal Reserve's latest signals suggest a potential pivot in monetary policy, while AI industry sees major consolidation moves.

**中文翻译：** 美联储最新信号暗示货币政策可能转向，同时AI行业出现重大整合动向。"""
        economy_analysis: str = """### Fed Policy Shift

**Original Context | 原文引用：**
> "The Federal Reserve is now more confident that inflation is moving sustainably toward its 2% target."
> 
> 中文翻译："美联储现在更有信心，认为通胀正在可持续地向2%目标迈进。"

**Deep Analysis | 深度解析：**
This shift represents a significant change in the Fed's stance...

**Key Concepts | 关键概念：**
- **Quantitative Tightening** (量化紧缩): The process of reducing the central bank's balance sheet
- **Forward Guidance** (前瞻性指引): Central bank communication about future policy intentions"""
        ai_industry_analysis: str = "AI industry analysis content here..."
        ai_research_analysis: str = "AI research analysis content here..."
        learning_agenda: str = """### 🎯 Priority 1: Understanding Fed Policy
- Time needed: 30 minutes
- Action: Read the latest FOMC statement
- Resource: federalreserve.gov"""
        raw_items: list = None
    
    html = generate_html_report(MockBriefing())
    
    with open("/tmp/test_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("测试报告已生成: /tmp/test_report.html")
