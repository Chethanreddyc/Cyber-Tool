"""
╔══════════════════════════════════════════════════════════╗
║       CYBER TOOL — Phishing Email Service                ║
║   For AUTHORISED security awareness testing ONLY         ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import smtplib
import threading
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import stats_tracker
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# ── Palette ────────────────────────────────────────────────────
BG_DARK    = "#0a0f1e"
PANEL_BG   = "#0d1526"
CARD_BG    = "#0f1c35"
ACCENT     = "#7b2ff7"    # purple theme for phishing module
ACCENT2    = "#00d4ff"
TEXT_MAIN  = "#e8f4fd"
TEXT_MUTED = "#4a6fa5"
BORDER     = "#1e3a5f"
ERROR_C    = "#ff4d6d"
SUCCESS_C  = "#00e5a0"
WARN_C     = "#f0b429"
ENTRY_BG   = "#070e1c"

# ══════════════════════════════════════════════════════════════
#  Pre-made HTML Email Templates
# ══════════════════════════════════════════════════════════════
TEMPLATES = {

    "🔴 Google — Security Alert": {
        "subject": "Security Alert: New sign-in to your Google Account",
        "preview": "Someone signed into your account from a new device.",
        "from_name": "Google Security Team",
        "html": """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f3f4;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" bgcolor="#f1f3f4">
  <tr><td align="center" style="padding:40px 0;">
    <table width="520" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.15);">
      <!-- Header -->
      <tr><td style="background:#4285F4;padding:20px 30px;border-radius:8px 8px 0 0;">
        <span style="color:#fff;font-size:22px;font-weight:bold;">G</span>
        <span style="color:#fff;font-size:16px;font-weight:600;margin-left:6px;">oogle</span>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:30px 30px 10px;">
        <h2 style="color:#202124;font-size:22px;margin:0 0 16px;">Security alert</h2>
        <p style="color:#3c4043;font-size:15px;line-height:1.6;margin:0 0 16px;">
          A new sign-in was detected on your Google Account <strong>{TARGET_EMAIL}</strong>.
        </p>
        <table cellpadding="0" cellspacing="0" style="background:#f8f9fa;border-radius:6px;width:100%;margin:16px 0;">
          <tr><td style="padding:14px 18px;">
            <p style="margin:0;font-size:13px;color:#5f6368;"><strong>Device:</strong> Windows PC (Chrome)</p>
            <p style="margin:6px 0 0;font-size:13px;color:#5f6368;"><strong>Location:</strong> Mumbai, India</p>
            <p style="margin:6px 0 0;font-size:13px;color:#5f6368;"><strong>Time:</strong> {SEND_TIME}</p>
          </td></tr>
        </table>
        <p style="color:#3c4043;font-size:14px;">If this was you, no action needed. If not, secure your account immediately:</p>
        <table cellpadding="0" cellspacing="0"><tr><td style="padding:16px 0;">
          <a href="https://accounts.google.com"
             style="background:#4285F4;color:#fff;padding:12px 28px;border-radius:4px;text-decoration:none;font-size:14px;font-weight:600;">
            Review Activity
          </a>
        </td></tr></table>
      </td></tr>
      <!-- Footer -->
      <tr><td style="padding:16px 30px;border-top:1px solid #e8eaed;">
        <p style="color:#80868b;font-size:12px;margin:0;">© 2024 Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>""",
    },

    "🔵 PayPal — Account Limited": {
        "subject": "Your PayPal account access has been limited",
        "preview": "We've limited account access. Verify your info to restore it.",
        "from_name": "PayPal Service",
        "html": """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
<table width="100%" bgcolor="#f5f5f5" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:30px 0;">
    <table width="500" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:4px;border:1px solid #ddd;">
      <tr><td style="background:#003087;padding:18px 24px;border-radius:4px 4px 0 0;text-align:center;">
        <span style="color:#fff;font-size:26px;font-weight:bold;font-style:italic;">PayPal</span>
      </td></tr>
      <tr><td style="padding:28px 32px;">
        <h2 style="color:#2c2e2f;font-size:20px;margin:0 0 14px;">Your account access has been limited</h2>
        <p style="color:#444;font-size:14px;line-height:1.6;">
          Dear PayPal member,<br><br>
          We noticed unusual activity on your PayPal account associated with <strong>{TARGET_EMAIL}</strong>.
          To ensure the safety of your account, we have temporarily limited access until you verify your information.
        </p>
        <table cellpadding="0" cellspacing="0" style="background:#fef5e7;border-left:4px solid #f5a623;width:100%;margin:14px 0;">
          <tr><td style="padding:12px 16px;">
            <p style="margin:0;font-size:13px;color:#635e57;">⚠️ <strong>Action Required:</strong> Your account will be permanently limited if not verified within <strong>24 hours</strong>.</p>
          </td></tr>
        </table>
        <p style="font-size:14px;color:#444;">Please confirm your identity to restore full account access:</p>
        <table cellpadding="0" cellspacing="0"><tr><td style="padding:16px 0;">
          <a href="https://www.paypal.com"
             style="background:#009cde;color:#fff;padding:12px 32px;border-radius:4px;text-decoration:none;font-size:14px;font-weight:bold;">
            Confirm Your Identity
          </a>
        </td></tr></table>
      </td></tr>
      <tr><td style="background:#f5f5f5;padding:14px 24px;border-top:1px solid #ddd;border-radius:0 0 4px 4px;">
        <p style="color:#9da3a6;font-size:11px;margin:0;text-align:center;">
          PayPal • 2211 North First Street • San Jose, CA 95131
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>""",
    },

    "🟠 Amazon — Order Suspended": {
        "subject": "Action Required: Your Amazon order has been suspended",
        "preview": "Your recent order has been put on hold. Verify payment details.",
        "from_name": "Amazon Customer Service",
        "html": """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f2f2;font-family:Arial,sans-serif;">
<table width="100%" bgcolor="#f0f2f2" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:30px 0;">
    <table width="520" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid #ddd;">
      <tr><td style="background:#131921;padding:14px 24px;">
        <span style="color:#ff9900;font-size:28px;font-weight:bold;letter-spacing:-1px;">amazon</span>
      </td></tr>
      <tr><td style="padding:28px 32px;">
        <h2 style="color:#0f1111;font-size:19px;margin:0 0 12px;">Your order has been suspended</h2>
        <p style="color:#555;font-size:14px;line-height:1.6;">
          Hello,<br><br>
          We were unable to process the payment for your recent order. Your account
          <strong>{TARGET_EMAIL}</strong> requires immediate attention.
        </p>
        <table cellpadding="0" cellspacing="0" style="background:#fff3cd;border:1px solid #ff9900;border-radius:4px;width:100%;margin:16px 0;">
          <tr><td style="padding:12px 16px;">
            <p style="margin:0 0 6px;font-size:13px;color:#333;"><strong>Order #: 402-8827491-7364712</strong></p>
            <p style="margin:0;font-size:13px;color:#c45500;">Status: <strong>Payment Failed — Action Required</strong></p>
          </td></tr>
        </table>
        <p style="font-size:14px;color:#555;">Update your payment method to release your order:</p>
        <table cellpadding="0" cellspacing="0"><tr><td style="padding:16px 0;">
          <a href="https://www.amazon.com"
             style="background:#ff9900;color:#131921;padding:12px 28px;border-radius:4px;text-decoration:none;font-size:14px;font-weight:bold;">
            Update Payment Method
          </a>
        </td></tr></table>
      </td></tr>
      <tr><td style="background:#f0f2f2;padding:14px 24px;border-top:1px solid #ddd;text-align:center;">
        <p style="color:#999;font-size:11px;margin:0;">© 2024 Amazon.com, Inc. or its affiliates. All rights reserved.</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>""",
    },

    "🟣 Microsoft — Password Expiry": {
        "subject": "Your Microsoft password expires in 24 hours",
        "preview": "Your Microsoft 365 password is about to expire. Update it now.",
        "from_name": "Microsoft Account Team",
        "html": """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f2f2f2;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" bgcolor="#f2f2f2" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:40px 0;">
    <table width="500" cellpadding="0" cellspacing="0" style="background:#fff;border-top:4px solid #0078d4;">
      <tr><td style="padding:24px 36px 0;">
        <div style="font-size:26px;font-weight:300;color:#0078d4;letter-spacing:-1px;">Microsoft</div>
      </td></tr>
      <tr><td style="padding:20px 36px;">
        <h2 style="color:#252423;font-size:20px;margin:0 0 14px;">Your password is about to expire</h2>
        <p style="color:#605e5c;font-size:14px;line-height:1.6;">
          The password for your Microsoft account <strong>{TARGET_EMAIL}</strong> will expire in <strong>24 hours</strong>.
          After expiry, you will be locked out of Microsoft 365, Outlook, and all connected services.
        </p>
        <table cellpadding="0" cellspacing="0" style="background:#eff6fc;border-left:4px solid #0078d4;width:100%;margin:14px 0;">
          <tr><td style="padding:12px 16px;">
            <p style="margin:0;font-size:13px;color:#323130;">
              ⏰ Password expires: <strong>{SEND_TIME}</strong>
            </p>
          </td></tr>
        </table>
        <p style="font-size:14px;color:#605e5c;">Keep your account secure by updating your password now:</p>
        <table cellpadding="0" cellspacing="0"><tr><td style="padding:16px 0;">
          <a href="https://account.microsoft.com"
             style="background:#0078d4;color:#fff;padding:12px 32px;text-decoration:none;font-size:14px;font-weight:600;">
            Update Password
          </a>
        </td></tr></table>
        <p style="font-size:12px;color:#a19f9d;margin-top:16px;">
          If you don't update your password, your account access will be suspended automatically.
        </p>
      </td></tr>
      <tr><td style="padding:14px 36px;border-top:1px solid #edebe9;">
        <p style="color:#a19f9d;font-size:11px;margin:0;">Microsoft Corporation • One Microsoft Way • Redmond, WA 98052</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>""",
    },

    "🔷 Netflix — Payment Failed": {
        "subject": "Netflix billing issue — Update your payment info",
        "preview": "There was a problem with your Netflix payment. Update now to keep streaming.",
        "from_name": "Netflix Support",
        "html": """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#141414;font-family:Arial,sans-serif;">
<table width="100%" bgcolor="#141414" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:40px 0;">
    <table width="500" cellpadding="0" cellspacing="0" style="background:#222;border-radius:4px;">
      <tr><td style="padding:28px 32px;text-align:center;border-bottom:1px solid #333;">
        <span style="color:#e50914;font-size:32px;font-weight:bold;letter-spacing:-2px;">NETFLIX</span>
      </td></tr>
      <tr><td style="padding:28px 32px;">
        <h2 style="color:#fff;font-size:20px;text-align:center;margin:0 0 16px;">Payment Unsuccessful</h2>
        <p style="color:#b3b3b3;font-size:14px;line-height:1.7;text-align:center;">
          Hi there,<br><br>
          We're having trouble with your current billing information for account
          <strong style="color:#fff;">{TARGET_EMAIL}</strong>.
          We'll try again, but in the meantime, please update your payment details
          to avoid any interruption to your service.
        </p>
        <table cellpadding="0" cellspacing="0" style="background:#2a2a2a;border-radius:4px;width:100%;margin:16px 0;">
          <tr><td style="padding:14px 18px;text-align:center;">
            <p style="margin:0;font-size:13px;color:#e87c03;">⚠️ Account suspension in: <strong>48 hours</strong></p>
          </td></tr>
        </table>
        <table cellpadding="0" cellspacing="0" width="100%"><tr><td align="center" style="padding:14px 0;">
          <a href="https://www.netflix.com"
             style="background:#e50914;color:#fff;padding:14px 40px;border-radius:4px;text-decoration:none;font-size:15px;font-weight:bold;">
            Update Payment Info
          </a>
        </td></tr></table>
        <p style="color:#737373;font-size:12px;text-align:center;margin-top:16px;">
          Your streaming quality and features will remain the same after updating.
        </p>
      </td></tr>
      <tr><td style="padding:16px 32px;border-top:1px solid #333;text-align:center;">
        <p style="color:#737373;font-size:11px;margin:0;">© 2024 Netflix, Inc. | 100 Winchester Circle, Los Gatos, CA 95032</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>""",
    },

    "⚫ IT Dept — Credentials Required": {
        "subject": "IT Department: Urgent — System credentials verification required",
        "preview": "Your network credentials must be verified to maintain system access.",
        "from_name": "IT Department",
        "html": """\
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:40px 0;">
    <table width="520" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:6px;border-top:5px solid #c0392b;">
      <tr><td style="padding:20px 32px;background:#2c3e50;border-radius:0;">
        <span style="color:#ecf0f1;font-size:14px;font-weight:600;letter-spacing:2px;">🔒 IT SECURITY DEPARTMENT</span>
      </td></tr>
      <tr><td style="padding:28px 32px;">
        <h2 style="color:#2c3e50;font-size:19px;margin:0 0 12px;">⚠ Urgent: Credential Verification Required</h2>
        <p style="color:#555;font-size:14px;line-height:1.6;">
          Dear User,<br><br>
          Our security systems have detected that your corporate account
          <strong>{TARGET_EMAIL}</strong> has not completed the mandatory
          two-factor authentication migration required by our new security policy.
        </p>
        <table cellpadding="0" cellspacing="0" style="background:#fdf0f0;border:1px solid #f5c6c6;border-radius:4px;width:100%;margin:14px 0;">
          <tr><td style="padding:14px 18px;">
            <p style="margin:0 0 6px;font-size:13px;color:#333;"><strong>Deadline:</strong> {SEND_TIME}</p>
            <p style="margin:0;font-size:13px;color:#c0392b;"><strong>Failure to verify will result in account lockout and loss of network access.</strong></p>
          </td></tr>
        </table>
        <p style="font-size:14px;color:#555;">Please verify your credentials immediately to maintain access:</p>
        <table cellpadding="0" cellspacing="0"><tr><td style="padding:16px 0;">
          <a href="#"
             style="background:#c0392b;color:#fff;padding:12px 32px;border-radius:4px;text-decoration:none;font-size:14px;font-weight:bold;">
            Verify Credentials Now
          </a>
        </td></tr></table>
        <p style="font-size:12px;color:#999;margin-top:12px;">
          If you have already completed verification, please disregard this message.
        </p>
      </td></tr>
      <tr><td style="padding:14px 32px;border-top:1px solid #eee;background:#f9f9f9;border-radius:0 0 6px 6px;">
        <p style="color:#aaa;font-size:11px;margin:0;">IT Security Department | Internal Communication | Do not forward</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>""",
    },

}


# ══════════════════════════════════════════════════════════════
#  Phishing Service Page
# ══════════════════════════════════════════════════════════════
class PhishingServicePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)
        self._selected_template = list(TEMPLATES.keys())[0]
        self._build_ui()

    # ══════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Page header ───────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  🎣  Phishing Email Service",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(side="left", padx=24, pady=14)

        # Ethical banner
        ctk.CTkLabel(
            header,
            text="⚠  For Authorised Security Testing Only",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=WARN_C,
        ).pack(side="right", padx=24)

        # ── Ethical disclaimer bar ─────────────────────────────
        disc = ctk.CTkFrame(self, fg_color="#1a0a00", corner_radius=0, height=36)
        disc.pack(fill="x")
        disc.pack_propagate(False)

        ctk.CTkLabel(
            disc,
            text="🔐  This tool is strictly for authorised penetration testing and security awareness training. Misuse is illegal under the Computer Misuse Act and similar laws.",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#ff8c42",
            anchor="w",
        ).pack(fill="x", padx=20, pady=8)

        # ── Main 3-column layout ──────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=14)
        body.columnconfigure(0, weight=0)   # template list
        body.columnconfigure(1, weight=1)   # preview
        body.columnconfigure(2, weight=0)   # config panel
        body.rowconfigure(0, weight=1)

        self._build_template_list(body)
        self._build_preview(body)
        self._build_config_panel(body)

        # Select first template AFTER all panels are built
        self.after(50, lambda: self._select_template(self._selected_template))

    # ── Left: Template list ────────────────────────────────────
    def _build_template_list(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12,
                              border_width=1, border_color=BORDER, width=220)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.pack_propagate(False)

        ctk.CTkLabel(
            panel,
            text="EMAIL TEMPLATES",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(14, 6))

        self._template_buttons = {}

        for name in TEMPLATES:
            btn = ctk.CTkButton(
                panel,
                text=name,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color="transparent",
                hover_color="#1a1040",
                text_color=TEXT_MUTED,
                height=40,
                corner_radius=8,
                command=lambda n=name: self._select_template(n),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._template_buttons[name] = btn

        # First template will be selected by _build_ui after all panels exist

    # ── Centre: Preview panel ──────────────────────────────────
    def _build_preview(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12,
                              border_width=1, border_color=BORDER)
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            panel,
            text="TEMPLATE PREVIEW",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 4))

        # Subject line display
        self.preview_subject = ctk.CTkLabel(
            panel,
            text="",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=ACCENT,
            anchor="w",
            wraplength=500,
        )
        self.preview_subject.pack(fill="x", padx=16, pady=(0, 4))

        self.preview_hint = ctk.CTkLabel(
            panel,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
            wraplength=500,
        )
        self.preview_hint.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=(0, 8))

        # HTML source preview (read-only)
        self.html_preview = ctk.CTkTextbox(
            panel,
            fg_color=ENTRY_BG,
            border_color=BORDER,
            border_width=1,
            text_color="#a8c7fa",
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=8,
            wrap="none",
            state="disabled",
        )
        self.html_preview.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # ── Right: Config & send panel ─────────────────────────────
    def _build_config_panel(self, parent):
        panel = ctk.CTkScrollableFrame(
            parent, fg_color=PANEL_BG, corner_radius=12,
            border_width=1, border_color=BORDER, width=280,
            scrollbar_fg_color=PANEL_BG,
        )
        panel.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(
            panel,
            text="SEND CONFIGURATION",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(8, 10))

        def field(label, placeholder, attr, show=""):
            ctk.CTkLabel(
                panel,
                text=label,
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                text_color=TEXT_MUTED,
                anchor="w",
            ).pack(fill="x", padx=4, pady=(8, 2))
            e = ctk.CTkEntry(
                panel,
                placeholder_text=placeholder,
                placeholder_text_color=TEXT_MUTED,
                fg_color=ENTRY_BG,
                border_color=BORDER,
                border_width=1,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(family="Consolas", size=12),
                height=36,
                corner_radius=8,
                show=show,
            )
            e.pack(fill="x", padx=4)
            setattr(self, attr, e)

        # Target
        ctk.CTkLabel(
            panel,
            text="TARGET",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=ERROR_C,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(4, 6))

        field("TARGET EMAIL", "victim@example.com", "target_entry")

        # Optional custom subject override
        field("CUSTOM SUBJECT (optional)", "Leave blank to use template subject", "custom_subject")

        # Custom sender display name
        field("SENDER DISPLAY NAME", "e.g. Google Security Team", "sender_name_entry")

        # Divider
        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x", padx=4, pady=14)

        # SMTP Configuration
        ctk.CTkLabel(
            panel,
            text="SMTP CONFIGURATION",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(0, 6))

        field("YOUR EMAIL (sender)", "youremail@gmail.com", "smtp_email")
        field("APP PASSWORD", "Gmail App Password", "smtp_password", show="●")

        # SMTP host/port row
        ctk.CTkLabel(
            panel,
            text="SMTP SERVER",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(10, 2))

        smtp_row = ctk.CTkFrame(panel, fg_color="transparent")
        smtp_row.pack(fill="x", padx=4)

        self.smtp_host = ctk.CTkEntry(
            smtp_row,
            placeholder_text="smtp.gmail.com",
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN, font=ctk.CTkFont(family="Consolas", size=11),
            height=34, corner_radius=8,
        )
        self.smtp_host.pack(side="left", fill="x", expand=True)
        self.smtp_host.insert(0, "smtp.gmail.com")

        self.smtp_port = ctk.CTkEntry(
            smtp_row,
            placeholder_text="587",
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN, font=ctk.CTkFont(family="Consolas", size=11),
            height=34, corner_radius=8, width=60,
        )
        self.smtp_port.pack(side="left", padx=(6, 0))
        self.smtp_port.insert(0, "587")

        # Pre-fill from .env if available
        env_email = os.getenv("SENDER_EMAIL", "")
        env_pass  = os.getenv("SENDER_APP_PASSWORD", "")
        if env_email:
            self.smtp_email.insert(0, env_email)
        if env_pass:
            self.smtp_password.insert(0, env_pass)

        # Divider
        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x", padx=4, pady=14)

        # Quantity
        ctk.CTkLabel(
            panel,
            text="SEND COUNT  (1 – 5)",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(0, 4))

        self.count_slider = ctk.CTkSlider(
            panel, from_=1, to=5, number_of_steps=4,
            button_color=ACCENT, button_hover_color="#5a1fc7",
            progress_color=ACCENT, fg_color=BORDER,
            command=self._update_count_label,
        )
        self.count_slider.set(1)
        self.count_slider.pack(fill="x", padx=4)

        self.count_label = ctk.CTkLabel(
            panel, text="Send  1  email(s)",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=ACCENT,
        )
        self.count_label.pack(pady=(4, 0))

        # ── Status label ──────────────────────────────────────
        self.status_label = ctk.CTkLabel(
            panel,
            text="Ready to send",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
            wraplength=240,
        )
        self.status_label.pack(pady=(10, 0))

        # ── Send button ───────────────────────────────────────
        self.send_btn = ctk.CTkButton(
            panel,
            text="  🎣  Launch Phishing Email",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color="#5a1fc7",
            text_color="#fff",
            height=46,
            corner_radius=10,
            command=self._confirm_and_send,
        )
        self.send_btn.pack(fill="x", padx=4, pady=(12, 0))

        # Test connection button
        ctk.CTkButton(
            panel,
            text="  🔌  Test SMTP Connection",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#1a1040",
            text_color=TEXT_MUTED,
            height=36,
            corner_radius=10,
            command=self._test_smtp,
        ).pack(fill="x", padx=4, pady=(8, 4))

        # Log box
        ctk.CTkLabel(
            panel,
            text="SEND LOG",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(14, 4))

        self.log_box = ctk.CTkTextbox(
            panel,
            fg_color=ENTRY_BG,
            border_color=BORDER,
            border_width=1,
            text_color=SUCCESS_C,
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=8,
            height=130,
            wrap="word",
            state="disabled",
        )
        self.log_box.pack(fill="x", padx=4, pady=(0, 10))

    # ══════════════════════════════════════════════════════════
    #  Template selection
    # ══════════════════════════════════════════════════════════
    def _select_template(self, name):
        self._selected_template = name

        # Update button highlights
        for n, btn in self._template_buttons.items():
            if n == name:
                btn.configure(fg_color="#1a1040", text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_MUTED)

        # Update preview
        tpl = TEMPLATES[name]
        self.preview_subject.configure(text=f"📨  {tpl['subject']}")
        self.preview_hint.configure(text=f"Preview: {tpl['preview']}")

        self.html_preview.configure(state="normal")
        self.html_preview.delete("1.0", "end")
        # Show cleaned HTML preview
        self.html_preview.insert("1.0", tpl["html"].strip())
        self.html_preview.configure(state="disabled")

        # Pre-fill sender name
        if hasattr(self, "sender_name_entry"):
            self.sender_name_entry.delete(0, "end")
            self.sender_name_entry.insert(0, tpl["from_name"])

    def _update_count_label(self, val):
        n = int(val)
        self.count_label.configure(text=f"Send  {n}  email(s)")

    # ══════════════════════════════════════════════════════════
    #  Confirm dialog before sending
    # ══════════════════════════════════════════════════════════
    def _confirm_and_send(self):
        target = self.target_entry.get().strip()
        if not target:
            self._set_status("⚠  Enter a target email first.", ERROR_C)
            return

        # Confirmation popup
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm — Authorised Use Declaration")
        dialog.geometry("420x300")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#12040a")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="⚠  AUTHORISATION REQUIRED",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=ERROR_C,
        ).pack(pady=(24, 8))

        ctk.CTkLabel(
            dialog,
            text=(
                f"You are about to send a simulated phishing email to:\n\n"
                f"  {target}\n\n"
                "By clicking CONFIRM you declare that:\n"
                "  • You have explicit written authorisation\n"
                "  • This is for security awareness training only\n"
                "  • You have legal right to test this target"
            ),
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
            justify="left",
        ).pack(padx=24, pady=4)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(pady=16)

        ctk.CTkButton(
            btn_row, text="✓  CONFIRM & SEND",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=ERROR_C, hover_color="#c0392b",
            text_color="#fff", height=38, corner_radius=8, width=160,
            command=lambda: [dialog.destroy(), self._send_email()],
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="  Cancel",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent", border_width=1, border_color=BORDER,
            text_color=TEXT_MUTED, height=38, corner_radius=8, width=100,
            command=dialog.destroy,
        ).pack(side="left", padx=6)

    # ══════════════════════════════════════════════════════════
    #  SMTP Send
    # ══════════════════════════════════════════════════════════
    def _send_email(self):
        self.send_btn.configure(state="disabled", text="  ⏳  Sending…")
        threading.Thread(target=self._send_thread, daemon=True).start()

    def _send_thread(self):
        target      = self.target_entry.get().strip()
        smtp_email  = self.smtp_email.get().strip()
        smtp_pass   = self.smtp_password.get().strip()
        smtp_host   = self.smtp_host.get().strip() or "smtp.gmail.com"
        smtp_port   = int(self.smtp_port.get().strip() or 587)
        count       = int(self.count_slider.get())
        sender_name = self.sender_name_entry.get().strip()
        tpl         = TEMPLATES[self._selected_template]
        subject     = self.custom_subject.get().strip() or tpl["subject"]
        send_time   = datetime.now().strftime("%d %b %Y, %I:%M %p")

        html_body = tpl["html"].replace("{TARGET_EMAIL}", target).replace("{SEND_TIME}", send_time)

        if not smtp_email or not smtp_pass:
            self.after(0, lambda: self._set_status("⚠  Enter SMTP email and password.", ERROR_C))
            self.after(0, lambda: self.send_btn.configure(state="normal", text="  🎣  Launch Phishing Email"))
            return

        self.after(0, lambda: self._set_status("🔌  Connecting to SMTP…", ACCENT2))

        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.ehlo()
            server.starttls()
            server.login(smtp_email, smtp_pass)

            for i in range(count):
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"]    = f"{sender_name} <{smtp_email}>"
                msg["To"]      = target

                msg.attach(MIMEText(
                    f"Please view this email in an HTML-compatible client.\n\nSubject: {subject}",
                    "plain"
                ))
                msg.attach(MIMEText(html_body, "html"))

                server.sendmail(smtp_email, target, msg.as_string())
                self.after(0, lambda n=i+1: self._log(f"✔  Email {n}/{count} sent → {target}"))
                self.after(0, lambda n=i+1: self._set_status(f"✔  Sent {n}/{count}", SUCCESS_C))

            server.quit()
            self.after(0, lambda: self._set_status(f"✅  {count} email(s) sent successfully!", SUCCESS_C))
            self.after(0, lambda: self._log(f"── Campaign complete: {count} email(s) ──"))
            # Record to stats
            try:
                stats_tracker.record_phishing_sent(
                    target=target,
                    template=self._selected_template,
                )
            except Exception:
                pass

        except smtplib.SMTPAuthenticationError:
            self.after(0, lambda: self._set_status("⚠  Authentication failed. Check email/app password.", ERROR_C))
            self.after(0, lambda: self._log("✘  SMTP Auth Error — Invalid credentials"))
        except smtplib.SMTPException as e:
            self.after(0, lambda: self._set_status(f"⚠  SMTP Error: {e}", ERROR_C))
            self.after(0, lambda: self._log(f"✘  SMTP Error: {e}"))
        except Exception as e:
            self.after(0, lambda: self._set_status(f"⚠  Error: {e}", ERROR_C))
            self.after(0, lambda: self._log(f"✘  Error: {e}"))
        finally:
            self.after(0, lambda: self.send_btn.configure(state="normal", text="  🎣  Launch Phishing Email"))

    # ══════════════════════════════════════════════════════════
    #  Test SMTP connection
    # ══════════════════════════════════════════════════════════
    def _test_smtp(self):
        smtp_email = self.smtp_email.get().strip()
        smtp_pass  = self.smtp_password.get().strip()
        smtp_host  = self.smtp_host.get().strip() or "smtp.gmail.com"
        smtp_port  = int(self.smtp_port.get().strip() or 587)

        if not smtp_email or not smtp_pass:
            self._set_status("⚠  Enter SMTP credentials first.", ERROR_C)
            return

        self._set_status("🔌  Testing connection…", ACCENT2)

        def test():
            try:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=8)
                server.ehlo()
                server.starttls()
                server.login(smtp_email, smtp_pass)
                server.quit()
                self.after(0, lambda: self._set_status("✅  SMTP connection successful!", SUCCESS_C))
                self.after(0, lambda: self._log(f"✔  SMTP OK: {smtp_host}:{smtp_port}"))
            except smtplib.SMTPAuthenticationError:
                self.after(0, lambda: self._set_status("✘  Auth failed — check app password.", ERROR_C))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"✘  Connection failed: {e}", ERROR_C))

        threading.Thread(target=test, daemon=True).start()

    # ── Helpers ───────────────────────────────────────────────
    def _set_status(self, msg, color=TEXT_MUTED):
        self.status_label.configure(text=msg, text_color=color)

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
