"""
AI处理模块 - Academic-Grade Analysis
使用DeepSeek生成学术级深度分析报告
"""

import os
import re
import aiohttp
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
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

# DeepSeek API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """你是一位高级研究分析师，为商业专业人士提供每日情报简报。读者正在建立AI专业知识，需要了解全球经济背景和前沿AI发展。

## 分析标准

1. 深度优于广度：深入分析3-5个重要事项，而非泛泛而谈
2. 全球视角：连接美国、欧盟、中国、新兴市场的动态
3. 第一性原理：解释WHY（为什么重要），而非仅仅WHAT（发生了什么）
4. 可操作的学习：每个部分必须包含具体的学习建议

## 输出格式（严格遵循）

## 📋 Executive Summary | 执行摘要

[用2-3句话概括今日最重要的发展及其关联。先写英文，再写中文翻译。]

**English:** [英文摘要]

**中文翻译：** [中文翻译]

---

## 🌍 Global Economy & Policy | 全球经济与政策

选择2-3个最重要的发展：

### [主题标题]

**原文引用：**
> "[引用来源中的关键句子]"

**深度解析：**
[解释：(1)发生了什么 (2)为什么重要 (3)对不同利益相关者的影响 (4)历史背景。150-200字。]

**关键概念：**
- **[术语]**：[一句话解释]

**学习路径：**
- 📖 推荐阅读：[具体资源]
- 🔗 延伸探索：[相关主题]

---

## 🤖 AI Technology & Industry | AI技术与产业

选择2-3个最重要的发展：

### [主题标题]

**原文引用：**
> "[引用来源中的关键句子]"

**技术解析：**
[解释：(1)技术/产品功能 (2)技术创新点 (3)竞争格局影响 (4)潜在应用。150-200字。]

**关键概念：**
- **[术语]**：[解释]

**学习路径：**
- 📖 基础学习：[先学什么]
- 🛠️ 动手实践：[如何尝试]

---

## 📚 AI Research Frontiers | AI学术前沿

选择2-3篇重要论文/研究：

### [论文/研究标题]

**摘要引用：**
> "[摘要中的关键句子]"

**研究意义：**
[解释：(1)解决什么问题 (2)新方法 (3)结果和影响 (4)局限性。150-200字。]

**关键概念：**
- **[术语]**：[通俗解释]

**学习路径：**
- 📖 前置知识：[需要什么背景]
- 📄 相关论文：[1-2篇基础论文]

---

## 🎯 Today's Learning Agenda | 今日学习议程

### 🎯 Priority 1: [最重要的概念]
- 时间：[X分钟]
- 行动：[具体学习行动]
- 资源：[具体链接或资源]

### 🎯 Priority 2: [第二优先]
- 时间：[X分钟]
- 行动：[具体学习行动]
- 资源：[具体链接或资源]

### 💡 Quick Wins (5分钟速学):
1. [快速概念1]
2. [快速概念2]

---

## 重要规则：
- 使用精确的技术术语
- 具体化，避免"这很重要"这类空话
- 如果某部分素材不足，承认并提供相关背景
"""

async def call_deepseek_api(prompt: str) -> Optional[str]:
    """调用DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ 未配置 DEEPSEEK_API_KEY")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ DeepSeek API错误 [{response.status}]: {error_text[:300]}")
                    return None
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]
                
    except Exception as e:
        print(f"❌ DeepSeek API调用失败: {str(e)}")
        return None


def extract_section(text: str, section_keyword: str) -> str:
    """从AI响应中提取特定章节"""
    if not text:
        return ""
    
    # 方法1：正则匹配 ## 标题格式
    patterns = [
        rf"##\s*[^\n]*{section_keyword}[^\n]*\n(.*?)(?=\n##|\Z)",
        rf"#\s*[^\n]*{section_keyword}[^\n]*\n(.*?)(?=\n#|\Z)",
        rf"{section_keyword}[^\n]*\n(.*?)(?=\n##|\n#|\n---|\Z)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            result = match.group(1).strip()
            if len(result) > 20:
                return result
    
    # 方法2：按行扫描
    lines = text.split('\n')
    capture = False
    captured = []
    
    for line in lines:
        lower_line = line.lower()
        # 检测是否是目标章节的开始
        if section_keyword.lower() in lower_line and '#' in line:
            capture = True
            continue
        # 检测是否到达下一个章节
        if capture:
            if line.strip().startswith('#') and section_keyword.lower() not in lower_line:
                break
            if line.strip() == '---':
                continue
            captured.append(line)
    
    if captured:
        result = '\n'.join(captured).strip()
        if len(result) > 20:
            return result
    
    return ""


async def generate_briefing(items: List[NewsItem]) -> Optional[DailyBriefing]:
    """生成完整的深度分析报告"""
    formatted_content = format_for_ai(items)
    
    user_prompt = f"""基于今日收集的全球信息源，生成一份研究简报。

今日日期: {datetime.now().strftime("%Y-%m-%d")}

素材来源:
{formatted_content}

请严格按照系统提示中的格式生成简报。深入分析最重要的内容，而非泛泛覆盖所有内容。"""

    print("🤖 正在生成深度分析（预计60-90秒）...")
    ai_response = await call_deepseek_api(user_prompt)
    
    if not ai_response:
        return None
    
    print("✅ AI分析完成")
    print(f"📝 响应长度: {len(ai_response)} 字符")
    
    # 提取各部分
    executive = extract_section(ai_response, "Executive Summary") or extract_section(ai_response, "执行摘要")
    economy = extract_section(ai_response, "Global Economy") or extract_section(ai_response, "全球经济")
    ai_tech = extract_section(ai_response, "AI Technology") or extract_section(ai_response, "AI技术")
    ai_research = extract_section(ai_response, "AI Research") or extract_section(ai_response, "AI学术")
    learning = extract_section(ai_response, "Learning Agenda") or extract_section(ai_response, "学习议程")
    
    # 统计提取结果
    extracted = sum(1 for x in [executive, economy, ai_tech, ai_research, learning] if x)
    print(f"📊 成功提取 {extracted}/5 个章节")
    
    # 如果提取全部失败，使用完整响应
    if extracted == 0:
        print("⚠️ 分段提取失败，使用完整响应作为内容")
        # 将完整响应放入各个部分
        return DailyBriefing(
            date=datetime.now().strftime("%Y-%m-%d"),
            executive_summary=ai_response,
            economy_analysis="",
            ai_industry_analysis="",
            ai_research_analysis="",
            learning_agenda="",
            raw_items=items
        )
    
    return DailyBriefing(
        date=datetime.now().strftime("%Y-%m-%d"),
        executive_summary=executive if executive else "请查看下方详细分析",
        economy_analysis=economy if economy else "",
        ai_industry_analysis=ai_tech if ai_tech else "",
        ai_research_analysis=ai_research if ai_research else "",
        learning_agenda=learning if learning else "",
        raw_items=items
    )


if __name__ == "__main__":
    import asyncio
    
    async def test():
        test_items = [
            NewsItem(
                title="Fed Signals Potential Rate Cut",
                summary="Federal Reserve officials indicated openness to cutting rates...",
                source="Reuters",
                category="economy",
                url="https://reuters.com/example",
                published="2024-01-15",
                tier="top"
            ),
        ]
        
        briefing = await generate_briefing(test_items)
        if briefing:
            print(f"生成完成: {briefing.date}")
    
    asyncio.run(test())
