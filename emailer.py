"""
Gmail SMTP email sender.
Sends styled HTML email reports with outperforming YouTube videos.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL

logger = logging.getLogger(__name__)


def _format_views(views):
    """Format view count with commas or shorthand."""
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)


def _format_ratio(ratio):
    """Format performance ratio as a percentage above average."""
    percentage = (ratio - 1) * 100
    return f"+{percentage:.0f}%"


def _build_html_report(analysis_results):
    """
    Build a styled HTML email body from the analysis results.
    """
    today = datetime.now().strftime("%B %d, %Y")
    total_channels = len(analysis_results)
    total_outperforming = sum(
        len(r["outperforming_videos"]) for r in analysis_results
    )

    # ─── CSS Styles ─────────────────────────────────────────
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#0f0f0f; font-family: 'Segoe UI', Arial, sans-serif;">
    <div style="max-width:700px; margin:0 auto; background-color:#1a1a2e; border-radius:12px; overflow:hidden; margin-top:20px; margin-bottom:20px;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:30px; text-align:center;">
            <h1 style="color:#ffffff; font-size:24px; margin:0 0 8px 0; font-weight:700;">
                🎯 YouTube Competitor Report
            </h1>
            <p style="color:#e0d4f7; font-size:14px; margin:0;">
                {today} &bull; UAbility Competitive Intelligence
            </p>
        </div>

        <!-- Summary Stats -->
        <div style="display:flex; padding:20px 30px; background-color:#16213e; border-bottom:1px solid #2a2a4a;">
            <div style="flex:1; text-align:center; padding:10px;">
                <div style="color:#667eea; font-size:28px; font-weight:700;">{total_channels}</div>
                <div style="color:#8888aa; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Channels Analyzed</div>
            </div>
            <div style="flex:1; text-align:center; padding:10px; border-left:1px solid #2a2a4a;">
                <div style="color:#f093fb; font-size:28px; font-weight:700;">{total_outperforming}</div>
                <div style="color:#8888aa; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Outperforming Videos</div>
            </div>
        </div>

        <!-- Channel Results -->
        <div style="padding:20px 30px;">
    """

    if not analysis_results:
        html += """
            <div style="text-align:center; padding:40px; color:#8888aa;">
                <p style="font-size:18px;">No outperforming videos found today.</p>
                <p style="font-size:13px;">All competitor channels are performing at baseline.</p>
            </div>
        """
    else:
        for channel_result in analysis_results:
            channel_name = channel_result["channel_name"]
            handle = channel_result["handle"]
            avg_views = channel_result["avg_views"]
            subscribers = channel_result["subscribers"]
            outperforming = channel_result["outperforming_videos"]

            html += f"""
            <!-- Channel Section -->
            <div style="margin-bottom:25px; border:1px solid #2a2a4a; border-radius:10px; overflow:hidden; background-color:#16213e;">
                <div style="padding:15px 20px; background-color:#1a1a3e; border-bottom:1px solid #2a2a4a;">
                    <h2 style="color:#e0e0ff; font-size:16px; margin:0 0 4px 0;">
                        📺 {channel_name}
                    </h2>
                    <p style="color:#6a6a8a; font-size:12px; margin:0;">
                        {handle} &bull; {_format_views(subscribers)} subscribers &bull; 
                        Avg: {_format_views(int(avg_views))} views/video
                    </p>
                </div>
                <div style="padding:10px 15px;">
            """

            # Show top 10 outperforming videos max
            for video in outperforming[:10]:
                title = video["title"]
                link = video["link"]
                views = video["views"]
                ratio = video["performance_ratio"]
                published = video.get("published_time", "")
                is_recent = video.get("is_recent", False)
                thumbnail = video.get("thumbnail", "")

                recent_badge = ""
                if is_recent:
                    recent_badge = '<span style="background:#27ae60; color:#fff; font-size:10px; padding:2px 6px; border-radius:3px; margin-left:6px;">RECENT</span>'

                ratio_color = "#27ae60" if ratio >= 2.0 else "#f39c12" if ratio >= 1.5 else "#3498db"

                html += f"""
                    <div style="display:flex; padding:10px; margin:5px 0; background-color:#1e2747; border-radius:8px; border-left:3px solid {ratio_color};">
                        <div style="flex:1; min-width:0;">
                            <a href="{link}" style="color:#c8c8ff; font-size:13px; text-decoration:none; font-weight:600; display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                                {title}
                            </a>
                            <div style="margin-top:5px; display:flex; gap:12px; flex-wrap:wrap;">
                                <span style="color:#8888aa; font-size:11px;">👁 {_format_views(views)} views</span>
                                <span style="color:{ratio_color}; font-size:11px; font-weight:700;">{_format_ratio(ratio)} above avg</span>
                                <span style="color:#8888aa; font-size:11px;">🕐 {published}</span>
                                {recent_badge}
                            </div>
                        </div>
                    </div>
                """

            remaining = len(outperforming) - 10
            if remaining > 0:
                html += f"""
                    <p style="color:#6a6a8a; font-size:12px; text-align:center; padding:5px;">
                        ... and {remaining} more outperforming videos
                    </p>
                """

            html += """
                </div>
            </div>
            """

    html += """
        </div>

        <!-- Footer -->
        <div style="padding:20px 30px; background-color:#0f0f1e; text-align:center; border-top:1px solid #2a2a4a;">
            <p style="color:#555577; font-size:11px; margin:0;">
                Automated by UAbility YouTube Monitor &bull; Powered by ScrapingDog API
            </p>
        </div>
    </div>
    </body>
    </html>
    """

    return html


def send_email_report(analysis_results):
    """
    Send the HTML email report via Gmail SMTP.

    Args:
        analysis_results: list of analysis dicts from analyzer.analyze_all_channels()

    Returns:
        True if email sent successfully, False otherwise.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD or not RECIPIENT_EMAIL:
        logger.error("Email credentials not configured. Check .env file.")
        return False

    today = datetime.now().strftime("%B %d, %Y")
    total_outperforming = sum(
        len(r["outperforming_videos"]) for r in analysis_results
    )

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎯 YouTube Competitor Report — {total_outperforming} Outperforming Videos ({today})"
    msg["From"] = f"UAbility Monitor <{GMAIL_ADDRESS}>"
    msg["To"] = RECIPIENT_EMAIL

    # Plain text fallback
    plain_text = f"YouTube Competitor Report for {today}\n"
    plain_text += f"Found {total_outperforming} outperforming videos.\n\n"
    for result in analysis_results:
        plain_text += f"\n{result['channel_name']} ({result['handle']}):\n"
        plain_text += f"  Average views: {int(result['avg_views'])}\n"
        for video in result["outperforming_videos"][:10]:
            plain_text += f"  - {video['title']} ({_format_views(video['views'])} views, {_format_ratio(video['performance_ratio'])} above avg)\n"
            plain_text += f"    {video['link']}\n"

    # Attach both versions
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(_build_html_report(analysis_results), "html"))

    # Send via Gmail SMTP
    try:
        logger.info(f"Sending email to {RECIPIENT_EMAIL}...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

        logger.info("✅ Email sent successfully!")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "❌ Gmail authentication failed. Check your email and App Password in .env. "
            "Make sure you're using an App Password, not your regular password."
        )
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False
