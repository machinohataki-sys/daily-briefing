"""
AI处理模块 - Academic-Grade Analysis
使用GLM-5生成学术级深度分析报告
"""

import os
import aiohttp
from typing import List, Optional
from dataclasses import dataclass
from sources import NewsItem, format_for_ai

@dataclass
class DailyBriefing:
    date: str
    executive_summary: str
    economy_analysis: str
    ai_industry_analysis: str
    ai_research_analysis: str
    learning_agenda: str
    raw_items: List[NewsItem]

# GLM API配置
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

SYSTEM_PROMPT = """You are a senior research analyst providing daily intelligence briefings for a business professional who wants deep, academic-quality analysis. Your reader is building AI expertise and needs to understand both the global economic context and cutting-edge AI developments.

## YOUR ANALYSIS STANDARDS

1. **Depth over breadth**: Better to deeply analyze 3-5 significant items than superficially cover everything
2. **Global perspective**: Connect dots across regions (US, EU, China, emerging markets)
3. **First-principles thinking**: Explain WHY something matters, not just WHAT happened
4. **Actionable learning**: Every section must include specific learning recommendations

## OUTPUT FORMAT (STRICT - Follow exactly)

---

## 📋 Executive Summary | 执行摘要

[2-3 sentences capturing the most significant developments and their interconnections. Write in English first, then Chinese translation.]

**English:** [Your summary]

**中文翻译：** [Chinese translation]

---

## 🌍 Global Economy & Policy Analysis | 全球经济与政策分析

For each significant development (select 2-3 most important):

### [Topic Title]

**Original Context | 原文引用：**
> "[Quote key sentence from source in English]"
> 
> 中文翻译："[Chinese translation of the quote]"

**Deep Analysis | 深度解析：**
[Explain: (1) What happened (2) Why it matters globally (3) Impact on different stakeholders (4) Historical context or precedent. Write 150-200 words mixing English terms with Chinese explanation.]

**Key Concepts | 关键概念：**
- **[English Term]** ([Chinese translation]): [One-sentence explanation]
- **[English Term]** ([Chinese translation]): [One-sentence explanation]

**Learning Path | 学习路径：**
- 📖 Recommended reading: [Specific book/paper/resource]
- 🔗 Further exploration: [Related topic to research]

---

## 🤖 AI Technology & Industry Analysis | AI技术与产业分析

For each significant development (select 2-3 most important):

### [Topic Title]

**Original Context | 原文引用：**
> "[Quote key sentence from source in English]"
> 
> 中文翻译："[Chinese translation of the quote]"

**Technical Analysis | 技术解析：**
[Explain: (1) What the technology/product does (2) Technical innovation or breakthrough (3) Competitive landscape implications (4) Potential applications. Write 150-200 words.]

**Key Concepts | 关键概念：**
- **[Technical Term]** ([Chinese]): [Explanation]
- **[Technical Term]** ([Chinese]): [Explanation]

**Learning Path | 学习路径：**
- 📖 Foundation: [What to learn first]
- 🛠️ Hands-on: [How to experiment with this]

---

## 📚 AI Research Frontiers | AI学术前沿

For each significant paper/research (select 2-3 most important):

### [Paper/Research Title]

**Original Abstract | 原文摘要：**
> "[Key sentence from abstract in English]"
> 
> 中文翻译："[Chinese translation]"

**Research Significance | 研究意义：**
[Explain: (1) What problem it solves (2) Novel approach/method (3) Results and implications (4) Limitations. Write 150-200 words in accessible language.]

**Key Concepts | 关键概念：**
- **[Technical Term]** ([Chinese]): [Explanation for non-specialists]

**Learning Path | 学习路径：**
- 📖 Prerequisites: [What background knowledge is needed]
- 📄 Related papers: [1-2 foundational papers to read first]

---

## 📚 Today's Learning Agenda | 今日学习议程

Based on today's briefing, here's a prioritized learning plan:

### 🎯 Priority 1: [Most important concept to understand]
- Time needed: [X minutes]
- Action: [Specific learning action]
- Resource: [Specific link or resource]

### 🎯 Priority 2: [Second priority]
- Time needed: [X minutes]
- Action: [Specific learning action]
- Resource: [Specific link or resource]

### 💡 Quick Wins (5-minute learnings):
1. [Quick concept to grasp]
2. [Quick concept to grasp]

---

## IMPORTANT RULES:
- Always include English original quotes with Chinese translations
- Use precise technical terminology (with Chinese glosses)
- Be specific - avoid vague statements like "this is important"
- Connect economic and AI topics where relevant
- If source material is weak for a section, acknowledge it and provide general context instead of making things up
"""

async def call_glm_api(prompt: str) -> Optional[str]:
    """调用GLM-5 API"""
    api_key = os.getenv("GLM_API_KEY")
    
    if not api_key:
        print("❌ 未配置 GLM_API_KEY")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "glm-5",  # GLM-5最新模型
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000  # 增加输出长度
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GLM_API_URL, 
                headers=headers, 
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)  # 增加超时
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ GLM API错误 [{response.status}]: {error_text[:300]}")
                    return None
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]
                
    except Exception as e:
        print(f"❌ GLM API调用失败: {str(e)}")
        return None

async def generate_briefing(items: List[NewsItem]) -> Optional[DailyBriefing]:
    """生成完整的深度分析报告"""
    from datetime import datetime
    
    formatted_content = format_for_ai(items)
    
    user_prompt = f"""Based on today's intelligence gathered from global sources, generate a comprehensive research briefing.

TODAY'S DATE: {datetime.now().strftime("%Y-%m-%d")}

SOURCE MATERIAL:
{formatted_content}

Generate the briefing following the exact format specified in your system instructions. 
Focus on quality over quantity - deeply analyze the most significant items rather than covering everything superficially.
Always include original English quotes with Chinese translations.
If certain sections lack strong source material, acknowledge this and provide relevant context or background instead."""

    print("🤖 正在生成深度分析（预计60-90秒）...")
    ai_response = await call_glm_api(user_prompt)
    
    if not ai_response:
        return None
    
    return DailyBriefing(
        date=datetime.now().strftime("%Y-%m-%d"),
        executive_summary=extract_section(ai_response, "Executive Summary"),
        economy_analysis=extract_section(ai_response, "Global Economy"),
        ai_industry_analysis=extract_section(ai_response, "AI Technology"),
        ai_research_analysis=extract_section(ai_response, "AI Research"),
        learning_agenda=extract_section(ai_response, "Learning Agenda"),
        raw_items=items
    )

def extract_section(text: str, section_keyword: str) -> str:
    """从AI响应中提取特定章节 - 增强版"""
    import re
    
    if not text:
        return ""
    
    # 多种匹配模式，按优先级尝试
    patterns = [
        # 模式1: ## + emoji + 关键词 + 内容 + 下一个##或结束
        rf"##\s*[^\n]*{section_keyword}[^\n]*\n(.*?)(?=\n##\s|\n---\s*\n##|\Z)",
        # 模式2: 关键词在行首 + 内容 + 下一个##或结束
        rf"^[#]*\s*[^\n]*{section_keyword}[^\n]*\n(.*?)(?=\n##|\Z)",
        # 模式3: 更宽松的匹配
        rf"{section_keyword}[^\n]*\n(.*?)(?=\n##|\n---|\Z)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if match:
            result = match.group(1).strip()
            # 确保提取到的内容有意义（至少10个字符）
            if len(result) > 10:
                return result
    
    # 最后尝试：简单分割法
    lines = text.split('\n')
    capture = False
    captured = []
    
    for line in lines:
        if section_keyword.lower() in line.lower() and ('#' in line or '---' in line):
            capture = True
            continue
        if capture:
            if line.strip().startswith('##') or line.strip() == '---':
                break
            captured.append(line)
    
    if captured:
        result = '\n'.join(captured).strip()
        if len(result) > 10:
            return result
    
    # 如果是Executive Summary且完全找不到，返回原文前500字符
    if section_keyword == "Executive Summary":
        return text[:500] + "..." if len(text) > 500 else text
    
    return ""

if __name__ == "__main__":
    import asyncio
    
    async def test():
        test_items = [
            NewsItem(
                title="Fed Signals Potential Rate Cut in June",
                summary="Federal Reserve officials indicated openness to cutting interest rates...",
                source="Financial Times",
                category="economy",
                url="https://ft.com/example",
                published="2024-01-15",
                tier="top"
            ),
        ]
        
        briefing = await generate_briefing(test_items)
        if briefing:
            print(f"生成完成: {briefing.date}")
            print(f"摘要: {briefing.executive_summary[:200]}...")
    
    asyncio.run(test())
