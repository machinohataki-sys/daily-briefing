"""
邮件发送模块 - Email Sender
支持多种发送方式：Resend API / Gmail SMTP / 通用SMTP
"""

import os
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

async def send_via_resend(to_email: str, subject: str, html_content: str) -> bool:
    """使用Resend API发送邮件（推荐，免费额度100封/天）"""
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("RESEND_FROM_EMAIL", "Daily Briefing <onboarding@resend.dev>")
    
    if not api_key:
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.resend.com/emails",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status in (200, 201):
                    return True
                else:
                    error = await response.text()
                    print(f"Resend错误 [{response.status}]: {error}")
                    return False
    except Exception as e:
        print(f"Resend发送失败: {e}")
        return False

def send_via_smtp(to_email: str, subject: str, html_content: str) -> bool:
    """使用SMTP发送邮件（Gmail或其他SMTP服务器）"""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("SMTP_FROM", smtp_user)
    
    if not smtp_user or not smtp_pass:
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        # 添加HTML内容
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)
        
        # 发送
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, to_email, msg.as_string())
        
        return True
        
    except Exception as e:
        print(f"SMTP发送失败: {e}")
        return False

async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    发送邮件 - 自动选择可用的发送方式
    优先级：Resend > SMTP
    """
    # 尝试Resend
    if os.getenv("RESEND_API_KEY"):
        print("  使用 Resend API 发送...")
        if await send_via_resend(to_email, subject, html_content):
            return True
        print("  Resend失败，尝试备选方案...")
    
    # 尝试SMTP
    if os.getenv("SMTP_USER"):
        print("  使用 SMTP 发送...")
        return send_via_smtp(to_email, subject, html_content)
    
    print("❌ 未配置任何邮件发送方式")
    print("   请配置 RESEND_API_KEY 或 SMTP_USER + SMTP_PASS")
    return False

# 测试用
if __name__ == "__main__":
    import asyncio
    
    async def test():
        success = await send_email(
            to_email="test@example.com",
            subject="测试邮件",
            html_content="<h1>Hello!</h1><p>这是一封测试邮件。</p>"
        )
        print(f"发送结果: {'成功' if success else '失败'}")
    
    asyncio.run(test())
