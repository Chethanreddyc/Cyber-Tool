"""
╔══════════════════════════════════════════════════════════╗
║       CYBER TOOL — AI Suspicious Email Analyser          ║
║   Analyses email content with Google Gemini AI           ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import threading
import os
import re
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import stats_tracker
import tldextract
import requests

# ── Palette ────────────────────────────────────────────────────
BG_DARK    = "#0a0f1e"
PANEL_BG   = "#0d1526"
CARD_BG    = "#0f1c35"
ACCENT     = "#f0b429"       # gold theme for email
ACCENT2    = "#00d4ff"
TEXT_MAIN  = "#e8f4fd"
TEXT_MUTED = "#4a6fa5"
BORDER     = "#1e3a5f"
ERROR_C    = "#ff4d6d"
SUCCESS_C  = "#00e5a0"
WARN_C     = "#f0b429"
ENTRY_BG   = "#070e1c"

RISK_COLORS  = ["#00e5a0", "#00d4ff", "#f0b429", "#ff6b35", "#ff4d6d"]
RISK_LABELS  = ["Safe", "Low Risk", "Moderate", "High Risk", "Critical"]
RISK_EMOJIS  = ["✅", "🔵", "🟡", "🟠", "🚨"]

# Common phishing keywords
PHISHING_KEYWORDS = [
    "verify your account", "confirm your identity", "click here immediately",
    "your account will be suspended", "update your payment", "unusual activity",
    "you have won", "claim your prize", "limited time offer", "act now",
    "password expired", "login required", "security alert", "unauthorized access",
    "dear customer", "dear user", "kindly verify", "wire transfer", "urgent action",
    "bank account", "suspended", "blocked", "restricted", "validate",
]

SUSPICIOUS_DOMAINS = [
    "paypal-secure", "amazon-support", "google-verify", "apple-id-verify",
    "microsoft-update", "netflix-billing", "bank-secure",
]


class EmailAnalyzerPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)
        self._gemini = self._load_gemini()
        self._build_ui()

    def _load_gemini(self):
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key or api_key == "your_gemini_api_key_here":
                return None
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-3-flash-preview")
        except Exception:
            return None

    # ══════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  📧  Suspicious Email Analyser",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(side="left", padx=24, pady=14)

        ai_badge = "🤖 AI Active" if self._gemini else "⚠ No API Key"
        badge_color = SUCCESS_C if self._gemini else WARN_C
        ctk.CTkLabel(
            header,
            text=ai_badge,
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=badge_color,
        ).pack(side="right", padx=24)

        # Body layout
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    # ── LEFT — Email Input ─────────────────────────────────────
    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=14,
                             border_width=1, border_color=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            left,
            text="Email Details",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 2))

        ctk.CTkLabel(
            left,
            text="Fill in the email fields below for AI analysis",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 12))

        # Fields
        fields_frame = ctk.CTkFrame(left, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20)

        def field(label, placeholder, attr):
            ctk.CTkLabel(
                fields_frame,
                text=label,
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                text_color=TEXT_MUTED,
                anchor="w",
            ).pack(fill="x", pady=(10, 2))
            entry = ctk.CTkEntry(
                fields_frame,
                placeholder_text=placeholder,
                placeholder_text_color=TEXT_MUTED,
                fg_color=ENTRY_BG,
                border_color=BORDER,
                border_width=1,
                text_color=TEXT_MAIN,
                font=ctk.CTkFont(family="Consolas", size=12),
                height=36,
                corner_radius=8,
            )
            entry.pack(fill="x")
            setattr(self, attr, entry)

        field("FROM (Sender Email)", "e.g.  support@paypal-secure.com", "from_entry")
        field("TO (Recipient Email)", "e.g.  victim@gmail.com", "to_entry")
        field("SUBJECT", "e.g.  Urgent: Your account has been suspended", "subject_entry")
        field("REPLY-TO (if different)", "e.g.  hacker@evil.com (optional)", "replyto_entry")

        # Email body
        ctk.CTkLabel(
            left,
            text="EMAIL BODY",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(12, 4))

        self.body_text = ctk.CTkTextbox(
            left,
            fg_color=ENTRY_BG,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            height=150,
            wrap="word",
        )
        self.body_text.pack(fill="x", padx=20)
        self.body_text.insert("1.0", "Paste the full email body here…")
        self.body_text.bind("<FocusIn>", self._clear_body_placeholder)

        # Quick local scan label
        self.quick_label = ctk.CTkLabel(
            left,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
            wraplength=380,
        )
        self.quick_label.pack(fill="x", padx=20, pady=(8, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=16)

        self.analyse_btn = ctk.CTkButton(
            btn_frame,
            text="  🤖  AI Full Analysis",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color="#c8950f",
            text_color="#080d1a",
            height=44,
            corner_radius=10,
            command=self._run_ai_analysis,
        )
        self.analyse_btn.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="  ⚡  Quick Local Scan",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#1a2a4a",
            text_color=TEXT_MUTED,
            height=38,
            corner_radius=10,
            command=self._quick_scan,
        ).pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            btn_frame,
            text="  🗑  Clear All",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#1a0a0a",
            text_color=TEXT_MUTED,
            height=38,
            corner_radius=10,
            command=self._clear_all,
        ).pack(fill="x", pady=(8, 0))

    # ── RIGHT — Results ────────────────────────────────────────
    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=14,
                              border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Risk score meter
        score_frame = ctk.CTkFrame(right, fg_color=CARD_BG, corner_radius=12)
        score_frame.pack(fill="x", padx=16, pady=(16, 0))

        inner_score = ctk.CTkFrame(score_frame, fg_color="transparent")
        inner_score.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            inner_score,
            text="THREAT RISK SCORE",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x")

        self.risk_label = ctk.CTkLabel(
            inner_score,
            text="—  Awaiting analysis",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.risk_label.pack(fill="x", pady=(4, 8))

        # Risk bar
        risk_bar_bg = ctk.CTkFrame(inner_score, fg_color="#1a2a40", height=10, corner_radius=5)
        risk_bar_bg.pack(fill="x")

        self.risk_bar = ctk.CTkFrame(risk_bar_bg, fg_color=TEXT_MUTED, height=10,
                                      corner_radius=5, width=0)
        self.risk_bar.place(x=0, y=0, relheight=1)

        # Indicator tags
        self.tags_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.tags_frame.pack(fill="x", padx=16, pady=(10, 0))

        ctk.CTkLabel(
            self.tags_frame,
            text="DETECTION FLAGS",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x")

        self.flags_container = ctk.CTkFrame(self.tags_frame, fg_color="transparent")
        self.flags_container.pack(fill="x", pady=(6, 0))

        ctk.CTkLabel(
            self.flags_container,
            text="No flags yet",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        # Divider
        ctk.CTkFrame(right, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=12)

        # AI report box
        ctk.CTkLabel(
            right,
            text="AI Analysis Report",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", padx=16)

        self.result_box = ctk.CTkTextbox(
            right,
            fg_color=CARD_BG,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10,
            wrap="word",
            state="disabled",
        )
        self.result_box.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        self._set_result(
            "📧 AI Email Analysis results will appear here.\n\n"
            "Fill in the email fields on the left, then:\n"
            "• Click 'Quick Local Scan' for instant flags\n"
            "• Click 'AI Full Analysis' for Gemini AI deep dive\n\n"
            "The AI will check for:\n"
            "  🔴 Spoofed sender / domain  \n"
            "  🔴 Phishing keywords & urgency tactics\n"
            "  🔴 Suspicious links & redirects\n"
            "  🔴 Mismatched reply-to addresses\n"
            "  🔴 Social engineering patterns\n"
            "  🟢 Legitimacy signals"
        )

        # Status bar
        self.status_bar = ctk.CTkLabel(
            right,
            text="Ready",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.status_bar.pack(fill="x", padx=16, pady=(6, 12))

    # ══════════════════════════════════════════════════════════
    #  Quick local scan
    # ══════════════════════════════════════════════════════════
    def _quick_scan(self):
        data    = self._collect_inputs()
        flags   = []
        score   = 0

        # 1. Sender domain analysis
        sender = data["from"]
        if sender:
            domain = re.search(r'@([\w.\-]+)', sender)
            if domain:
                d = domain.group(1).lower()
                ext = tldextract.extract(d)
                # Check for lookalike / suspicious domains
                for sus in SUSPICIOUS_DOMAINS:
                    if sus in d:
                        flags.append(("🚨 Spoofed Domain", f"Domain '{d}' mimics a trusted brand", ERROR_C))
                        score += 30
                        break
                # Check for free email providers sending as brands
                free_providers = ["gmail", "yahoo", "hotmail", "outlook", "protonmail"]
                is_free = any(p in d for p in free_providers)
                subj = data["subject"].lower()
                if is_free and any(k in subj for k in ["account", "security", "verify", "bank", "payment"]):
                    flags.append(("⚠ Suspicious Sender", "Brand impersonation via free email provider", WARN_C))
                    score += 20

        # 2. Reply-to mismatch
        replyto = data["replyto"]
        if replyto and sender:
            s_dom = re.search(r'@([\w.\-]+)', sender)
            r_dom = re.search(r'@([\w.\-]+)', replyto)
            if s_dom and r_dom and s_dom.group(1) != r_dom.group(1):
                flags.append(("🚨 Reply-To Mismatch", "Reply-to domain differs from sender domain", ERROR_C))
                score += 25

        # 3. Subject phishing keywords
        subj_lower = data["subject"].lower()
        found_subj = [k for k in PHISHING_KEYWORDS if k in subj_lower]
        if found_subj:
            flags.append(("⚠ Phishing Subject", f"Contains: {', '.join(found_subj[:3])}", WARN_C))
            score += 15 * min(len(found_subj), 2)

        # 4. Body keyword scan
        body_text = data["body"].lower()
        found_body = [k for k in PHISHING_KEYWORDS if k in body_text]
        if found_body:
            flags.append(("⚠ Phishing Keywords", f"Found {len(found_body)} suspicious phrase(s) in body", WARN_C))
            score += 10 * min(len(found_body), 3)

        # 5. URLs in body
        urls = re.findall(r'https?://[\w./\-?=&%+#]+', data["body"])
        if urls:
            for url in urls[:5]:
                ext = tldextract.extract(url)
                domain_str = f"{ext.domain}.{ext.suffix}"
                legit_brands = ["paypal", "amazon", "google", "apple", "microsoft", "netflix", "bank"]
                for brand in legit_brands:
                    if brand in url.lower() and brand not in domain_str.lower():
                        flags.append(("🚨 Misleading URL", f"Brand name in path but not in domain: {url[:50]}", ERROR_C))
                        score += 20
                        break

        # 6. Urgency language
        urgency_words = ["immediately", "urgent", "asap", "right now", "suspend", "expire", "24 hours", "48 hours"]
        found_urgency = [w for w in urgency_words if w in body_text]
        if found_urgency:
            flags.append(("🟡 Urgency Tactics", f"Urgency language detected: {', '.join(found_urgency[:3])}", WARN_C))
            score += 10

        # 7. Generic greeting
        if re.search(r'\b(dear (customer|user|member|valued|sir|madam))\b', body_text):
            flags.append(("🟡 Generic Greeting", "Impersonal greeting — legitimate orgs use your name", WARN_C))
            score += 5

        score = min(score, 100)

        # Display flags
        self._update_flags(flags)
        self._update_risk_score(score)

        # Summary text
        level = min(score // 25, 4)
        summary = (
            f"━━━  QUICK SCAN REPORT  ━━━\n\n"
            f"{RISK_EMOJIS[level]} RISK LEVEL: {RISK_LABELS[level]} ({score}/100)\n\n"
            f"{'─'*40}\n"
            f"Flags Found: {len(flags)}\n\n"
        )
        for name, detail, _ in flags:
            summary += f"{name}\n   → {detail}\n\n"

        if not flags:
            summary += "✅ No obvious phishing indicators found.\nStill recommend AI Full Analysis for certainty."
        else:
            summary += f"{'─'*40}\n⚠  {len(flags)} issue(s) detected.\nRun 'AI Full Analysis' for deeper Gemini insights."

        self._set_result(summary)
        self.status_bar.configure(
            text=f"Quick scan complete — {len(flags)} flag(s) found",
            text_color=WARN_C if flags else SUCCESS_C,
        )

        # Record to stats
        try:
            level_label = RISK_LABELS[min(score // 25, 4)]
            stats_tracker.record_email_analyzed(risk_level=level_label)
            if score >= 50:
                stats_tracker.record_phishing_detected()
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════
    #  AI Full Analysis (Gemini)
    # ══════════════════════════════════════════════════════════
    def _run_ai_analysis(self):
        data = self._collect_inputs()
        if not any([data["from"], data["subject"], data["body"]]):
            self._set_result("⚠  Please fill in at least the sender, subject, or body.")
            return

        if not self._gemini:
            self._quick_scan()
            self._set_result(
                self.result_box.get("1.0", "end") +
                "\n\n──────────────────────────────\n"
                "💡 Add GEMINI_API_KEY to .env\n"
                "   for full AI-powered analysis."
            )
            return

        self.analyse_btn.configure(state="disabled", text="  ⏳  Analysing…")
        self.status_bar.configure(text="Sending to Gemini AI…", text_color=ACCENT2)
        # Also run quick scan first
        self._quick_scan()

        def run():
            try:
                prompt = f"""
You are a cybersecurity expert specialising in email phishing and social engineering analysis.
Analyse the following email and provide a DETAILED threat report.

━━━ EMAIL DATA ━━━
FROM      : {data['from']}
TO        : {data['to']}
SUBJECT   : {data['subject']}
REPLY-TO  : {data['replyto']}
BODY:
{data['body']}
━━━━━━━━━━━━━━━━━

Provide a structured analysis including:

1. 🎯 THREAT CLASSIFICATION
   - Is this phishing, spam, legitimate, or BEC (Business Email Compromise)?
   - Overall risk score out of 100 and level (Safe/Low/Moderate/High/Critical)

2. 🔍 SENDER ANALYSIS
   - Domain legitimacy assessment
   - Spoofing indicators
   - Reply-to analysis

3. 📝 CONTENT ANALYSIS
   - Phishing keyword density
   - Urgency / fear tactics used
   - Social engineering techniques identified
   - Grammar/spelling issues (often a phishing sign)

4. 🔗 LINK ANALYSIS
   - Any suspicious URLs identified
   - Potential redirect traps or lookalike domains

5. 🧠 AI VERDICT
   - Confidence level
   - Top 3 red flags (if any)
   - Top 3 legitimacy signals (if any)

6. 🛡 RECOMMENDATIONS
   - What should the recipient do?
   - How to verify email authenticity?

Be specific and technical. Format clearly with headers.
"""
                response = self._gemini.generate_content(prompt)
                report   = response.text

                self.after(0, lambda: self._set_result(
                    f"━━━  GEMINI AI FULL ANALYSIS  ━━━\n"
                    f"Powered by Google Gemini 3 Flash Preview\n"
                    f"{'─'*45}\n\n{report}"
                ))
                self.after(0, lambda: self.status_bar.configure(
                    text="✔  AI Analysis complete", text_color=SUCCESS_C
                ))
            except Exception as e:
                self.after(0, lambda: self._set_result(
                    f"⚠  AI Analysis failed:\n{e}\n\n"
                    "Showing Quick Scan results above."
                ))
                self.after(0, lambda: self.status_bar.configure(
                    text=f"AI Error: {str(e)[:60]}", text_color=ERROR_C
                ))
            finally:
                self.after(0, lambda: self.analyse_btn.configure(
                    state="normal", text="  🤖  AI Full Analysis"
                ))

        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════
    #  Risk display helpers
    # ══════════════════════════════════════════════════════════
    def _update_risk_score(self, score: int):
        level = min(score // 25, 4)
        color = RISK_COLORS[level]
        label = f"{RISK_EMOJIS[level]}  {RISK_LABELS[level]}  ({score}/100)"
        self.risk_label.configure(text=label, text_color=color)

        # Animate bar
        total_width = self.risk_bar.master.winfo_width() or 400
        bar_w       = int(total_width * score / 100)
        self.risk_bar.configure(fg_color=color, width=bar_w)
        self.risk_bar.place_configure(relwidth=score / 100)

    def _update_flags(self, flags):
        for w in self.flags_container.winfo_children():
            w.destroy()

        if not flags:
            ctk.CTkLabel(
                self.flags_container,
                text="✅  No flags detected",
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=SUCCESS_C,
            ).pack(anchor="w")
            return

        for name, _, color in flags:
            tag = ctk.CTkLabel(
                self.flags_container,
                text=f" {name} ",
                font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                text_color=color,
                fg_color="#0a0f1e",
                corner_radius=6,
                padx=6,
                pady=2,
            )
            tag.pack(side="left", padx=(0, 4), pady=2)

    # ══════════════════════════════════════════════════════════
    #  Helpers
    # ══════════════════════════════════════════════════════════
    def _collect_inputs(self):
        body = self.body_text.get("1.0", "end").strip()
        if body == "Paste the full email body here…":
            body = ""
        return {
            "from":    self.from_entry.get().strip(),
            "to":      self.to_entry.get().strip(),
            "subject": self.subject_entry.get().strip(),
            "replyto": self.replyto_entry.get().strip(),
            "body":    body,
        }

    def _clear_body_placeholder(self, _=None):
        current = self.body_text.get("1.0", "end").strip()
        if current == "Paste the full email body here…":
            self.body_text.delete("1.0", "end")

    def _clear_all(self):
        for entry in [self.from_entry, self.to_entry, self.subject_entry, self.replyto_entry]:
            entry.delete(0, "end")
        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", "Paste the full email body here…")
        self._update_flags([])
        self.risk_label.configure(text="—  Awaiting analysis", text_color=TEXT_MUTED)
        self.risk_bar.configure(width=0)
        self._set_result(
            "📧 Fields cleared. Ready for a new email analysis.\n\n"
            "Fill in the fields on the left and click Analyse."
        )
        self.status_bar.configure(text="Ready", text_color=TEXT_MUTED)

    def _set_result(self, text):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")
