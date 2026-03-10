#!/usr/bin/env python3
"""
每日研究日报生成器
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from sources import fetch_all_sources
from ai_processor import generate_briefing
from email_sender import send_email
from report_generator import generate_html_report

load_dotenv()

async def main():
    print(f"[{datetime.now()}] 开始生成研究日报...")
    
    # Step 1: 抓取信息源
    print("📡 正在抓取信息源...")
    raw_content = await fetch_all_sources()
    
    if not raw_content:
        print("❌ 未抓取到任何内容，终止执行")
        return
    
    print(f"✅ 抓取完成，共 {len(raw_content)} 条内容")
    
    # Step 2: AI生成日报
    print("🤖 正在调用AI生成分析...")
    briefing = await generate_briefing(raw_content)
    
    if not briefing:
        print("❌ AI生成失败，终止执行")
        return
    
    # Step 3: 生成HTML
    print("📄 正在生成报告...")
    html_report = generate_html_report(briefing)
    print(f"📄 HTML报告长度: {len(html_report)} 字符")
    
    # Step 4: 发送邮件
    print("📧 正在发送邮件...")
    recipient = os.getenv("RECIPIENT_EMAIL")
    
    if not recipient:
        print("❌ 未配置收件人邮箱 RECIPIENT_EMAIL")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"📊 Research Intelligence Briefing | {today}"
    
    success = await send_email(
        to_email=recipient,
        subject=subject,
        html_content=html_report
    )
    
    if success:
        print(f"✅ 邮件发送成功 -> {recipient}")
    else:
        print("❌ 邮件发送失败")

if __name__ == "__main__":
    asyncio.run(main())
