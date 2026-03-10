"""
AI处理模块 - 使用DeepSeek生成研究日报
"""

import os
import aiohttp
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from sources import NewsItem, format_for_ai

@dataclass
class DailyBriefing:
    date: str
    full_content: str
    raw_items: List[NewsItem]

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """你是一位资深研究分析师，负责撰写每日情报简报。

请用以下格式输出（使用Markdown）：

# 📋 今日摘要

[2-3句话总结今日最重要的发展]

---

# 🌍 全球经济与政策

## [话题1标题]

**原文要点：** [引用关键信息]

**深度解析：** [为什么重要？影响是什么？150-200字分析]

**关键术语：**
- **[术语1]**：[解释]
- **[术语2]**：[解释]

**延伸阅读：** [推荐资源，给出完整URL如 https://example.com]

---

# 🤖 AI技术与产业

## [话题1标题]

**原文要点：** [引用关键信息]

**技术解析：** [技术原理、创新点、应用场景，150-200字]

**关键术语：**
- **[术语]**：[解释]

**动手实践：** [如何学习或尝试，给出具体资源URL]

---

# 📚 AI学术前沿

## [论文/研究标题]

**核心发现：** [一句话总结]

**研究意义：** [解决什么问题？方法是什么？100-150字]

**论文链接：** [如果有arxiv链接则提供]

---

# 🎯 今日学习计划

## Priority 1: [最重要的学习项]
- ⏱️ 时间：[X分钟]
- 📝 行动：[具体做什么]
- 🔗 资源：[完整URL]

## Priority 2: [第二项]
- ⏱️ 时间：[X分钟]  
- 📝 行动：[具体做什么]
- 🔗 资源：[完整URL]

## ⚡ 5分钟速学
1. [快速知识点1]
2. [快速知识点2]

---

**重要规则：**
1. 每个部分都要有实质内容，不要留空
2. 所有推荐资源必须给出完整可点击的URL（https://开头）
3. 分析要深入具体，避免空话
4. 中文为主，专业术语保留英文并给出中文解释
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
                content = data["choices"][0]["message"]["content"]
                print(f"✅ AI响应成功，长度: {len(content)} 字符")
                return content
                
    except Exception as e:
        print(f"❌ DeepSeek API调用失败: {str(e)}")
        return None


async def generate_briefing(items: List[NewsItem]) -> Optional[DailyBriefing]:
    """生成研究日报"""
    formatted_content = format_for_ai(items)
    
    user_prompt = f"""请基于以下今日资讯生成研究日报。

日期: {datetime.now().strftime("%Y-%m-%d")}

今日资讯素材:
{formatted_content}

请严格按照系统提示的格式输出完整的研究日报。确保每个部分都有实质内容。"""

    print("🤖 正在生成深度分析...")
    ai_response = await call_deepseek_api(user_prompt)
    
    if not ai_response:
        print("❌ AI生成失败")
        return None
    
    print("✅ 日报生成完成")
    
    return DailyBriefing(
        date=datetime.now().strftime("%Y-%m-%d"),
        full_content=ai_response,
        raw_items=items
    )
