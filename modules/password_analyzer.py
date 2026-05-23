"""
╔══════════════════════════════════════════════════════════╗
║         CYBER TOOL — AI Password Analyser                ║
║   Uses zxcvbn (local) + Google Gemini (AI insights)      ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import threading
import os
import re
import hashlib
import requests
from zxcvbn import zxcvbn

# ── Palette ────────────────────────────────────────────────────
BG_DARK      = "#0a0f1e"
PANEL_BG     = "#0d1526"
CARD_BG      = "#0f1c35"
ACCENT       = "#00d4ff"
TEXT_MAIN    = "#e8f4fd"
TEXT_MUTED   = "#4a6fa5"
BORDER       = "#1e3a5f"
ERROR_C      = "#ff4d6d"
SUCCESS_C    = "#00e5a0"
WARN_C       = "#f0b429"
ENTRY_BG     = "#070e1c"

STRENGTH_COLORS = ["#ff4d6d", "#ff6b35", "#f0b429", "#00d4ff", "#00e5a0"]
STRENGTH_LABELS = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
STRENGTH_EMOJIS = ["💀", "⚠️", "🟡", "🔵", "✅"]


class PasswordAnalyzerPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)
        self._gemini = self._load_gemini()
        self._build_ui()

    # ── Load Gemini ────────────────────────────────────────────
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
    #  UI Construction
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Page header ───────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  🔐  Password Analyser",
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

        # ── Main layout: left input | right results ────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    # ── LEFT panel ────────────────────────────────────────────
    def _build_left(self, parent):
        left = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=14,
                             border_width=1, border_color=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            left,
            text="Enter Password",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 6))

        ctk.CTkLabel(
            left,
            text="Type or paste a password to analyse it in real-time",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 14))

        # Password entry row
        pw_row = ctk.CTkFrame(left, fg_color="transparent")
        pw_row.pack(fill="x", padx=20)

        self._show_pw = False
        self.pw_entry = ctk.CTkEntry(
            pw_row,
            placeholder_text="e.g.  P@ssw0rd!2024",
            placeholder_text_color=TEXT_MUTED,
            fg_color=ENTRY_BG,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=16),
            height=48,
            corner_radius=10,
            show="●",
        )
        self.pw_entry.pack(side="left", fill="x", expand=True)
        self.pw_entry.bind("<KeyRelease>", self._on_keyrelease)

        ctk.CTkButton(
            pw_row,
            text="👁",
            width=48, height=48,
            fg_color=ENTRY_BG,
            hover_color="#1a2a4a",
            border_color=BORDER,
            border_width=1,
            corner_radius=10,
            command=self._toggle_pw,
            font=ctk.CTkFont(size=16),
        ).pack(side="left", padx=(6, 0))

        # ── Strength bar ──────────────────────────────────────
        ctk.CTkLabel(
            left,
            text="STRENGTH SCORE",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(18, 4))

        bar_frame = ctk.CTkFrame(left, fg_color="transparent")
        bar_frame.pack(fill="x", padx=20)

        self.strength_bars = []
        for i in range(5):
            bar = ctk.CTkFrame(
                bar_frame,
                fg_color="#1a2a40",
                height=8,
                corner_radius=4,
            )
            bar.pack(side="left", fill="x", expand=True, padx=2)
            self.strength_bars.append(bar)

        # Strength label
        self.strength_label = ctk.CTkLabel(
            left,
            text="—  Enter a password above",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.strength_label.pack(fill="x", padx=20, pady=(10, 0))

        # ── Quick stats ───────────────────────────────────────
        ctk.CTkLabel(
            left,
            text="QUICK STATS",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(20, 8))

        stats_frame = ctk.CTkFrame(left, fg_color=CARD_BG, corner_radius=10)
        stats_frame.pack(fill="x", padx=20)

        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=16, pady=12)

        stat_defs = [
            ("Length",    "len_val"),
            ("Uppercase", "upper_val"),
            ("Lowercase", "lower_val"),
            ("Numbers",   "num_val"),
            ("Symbols",   "sym_val"),
            ("Entropy",   "entropy_val"),
        ]
        self._stat_labels = {}
        for col_idx, (name, attr) in enumerate(stat_defs):
            cell = ctk.CTkFrame(stats_grid, fg_color="transparent")
            cell.grid(row=col_idx // 3, column=col_idx % 3, padx=12, pady=6, sticky="w")
            stats_grid.columnconfigure(col_idx % 3, weight=1)

            ctk.CTkLabel(
                cell,
                text=name,
                font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                text_color=TEXT_MUTED,
            ).pack(anchor="w")

            val_lbl = ctk.CTkLabel(
                cell,
                text="—",
                font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                text_color=TEXT_MAIN,
            )
            val_lbl.pack(anchor="w")
            self._stat_labels[attr] = val_lbl

        # ── Crack time ────────────────────────────────────────
        ctk.CTkLabel(
            left,
            text="ESTIMATED CRACK TIME",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(18, 4))

        self.crack_label = ctk.CTkLabel(
            left,
            text="—",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.crack_label.pack(fill="x", padx=20)

        # ── Buttons ───────────────────────────────────────────
        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=20)

        self.analyse_btn = ctk.CTkButton(
            btn_row,
            text="  🤖  AI Deep Analysis",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color="#00aacc",
            text_color="#05101a",
            height=44,
            corner_radius=10,
            command=self._run_ai_analysis,
        )
        self.analyse_btn.pack(fill="x")

        ctk.CTkButton(
            btn_row,
            text="  🔍  Check Breach (HIBP)",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#1a2a4a",
            text_color=TEXT_MUTED,
            height=38,
            corner_radius=10,
            command=self._check_breach,
        ).pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            btn_row,
            text="  🔄  Generate Strong Password",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#1a2a4a",
            text_color=TEXT_MUTED,
            height=38,
            corner_radius=10,
            command=self._generate_password,
        ).pack(fill="x", pady=(8, 0))

    # ── RIGHT panel ───────────────────────────────────────────
    def _build_right(self, parent):
        right = ctk.CTkScrollableFrame(
            parent, fg_color=PANEL_BG, corner_radius=14,
            label_text="", scrollbar_fg_color=PANEL_BG,
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(
            right,
            text="AI Analysis Report",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(8, 2))

        ctk.CTkLabel(
            right,
            text="Powered by Google Gemini",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=4, pady=(0, 12))

        # Result box
        self.result_box = ctk.CTkTextbox(
            right,
            fg_color=CARD_BG,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=10,
            height=420,
            wrap="word",
            state="disabled",
        )
        self.result_box.pack(fill="both", expand=True, padx=4)

        self._set_result(
            "🤖 AI Analysis results will appear here.\n\n"
            "1. Type a password on the left\n"
            "2. Click 'AI Deep Analysis' for Gemini insights\n\n"
            "• Strength score is calculated instantly (local)\n"
            "• AI provides detailed security recommendations\n"
            "• Breach check uses 'Have I Been Pwned' API"
        )

        # Status bar
        self.status_bar = ctk.CTkLabel(
            right,
            text="Ready",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.status_bar.pack(fill="x", padx=4, pady=(8, 0))

    # ══════════════════════════════════════════════════════════
    #  Real-time analysis
    # ══════════════════════════════════════════════════════════
    def _on_keyrelease(self, _=None):
        pw = self.pw_entry.get()
        if not pw:
            self._reset_stats()
            return
        self._update_stats(pw)

    def _update_stats(self, pw):
        result = zxcvbn(pw)
        score  = result["score"]   # 0-4

        # Strength bars
        for i, bar in enumerate(self.strength_bars):
            if i <= score:
                bar.configure(fg_color=STRENGTH_COLORS[score])
            else:
                bar.configure(fg_color="#1a2a40")

        # Strength label
        self.strength_label.configure(
            text=f"{STRENGTH_EMOJIS[score]}  {STRENGTH_LABELS[score]}  (score: {score}/4)",
            text_color=STRENGTH_COLORS[score],
        )

        # Quick stats
        length  = len(pw)
        upper   = sum(1 for c in pw if c.isupper())
        lower   = sum(1 for c in pw if c.islower())
        nums    = sum(1 for c in pw if c.isdigit())
        syms    = sum(1 for c in pw if not c.isalnum())

        # Shannon entropy approx
        import math
        charset = 0
        if any(c.islower() for c in pw): charset += 26
        if any(c.isupper() for c in pw): charset += 26
        if any(c.isdigit() for c in pw): charset += 10
        if any(not c.isalnum() for c in pw): charset += 32
        entropy = round(length * math.log2(charset), 1) if charset else 0

        self._stat_labels["len_val"].configure(text=str(length))
        self._stat_labels["upper_val"].configure(text=str(upper))
        self._stat_labels["lower_val"].configure(text=str(lower))
        self._stat_labels["num_val"].configure(text=str(nums))
        self._stat_labels["sym_val"].configure(text=str(syms))
        self._stat_labels["entropy_val"].configure(text=f"{entropy} bits")

        # Crack time
        crack = result.get("crack_times_display", {})
        online = crack.get("online_no_throttling_10_per_second", "N/A")
        offline = crack.get("offline_fast_hashing_1e10_per_second", "N/A")
        self.crack_label.configure(
            text=f"🌐 Online attack: {online}\n⚡ Offline (fast hash): {offline}",
            text_color=STRENGTH_COLORS[score],
        )

    def _reset_stats(self):
        for bar in self.strength_bars:
            bar.configure(fg_color="#1a2a40")
        self.strength_label.configure(text="—  Enter a password above", text_color=TEXT_MUTED)
        for lbl in self._stat_labels.values():
            lbl.configure(text="—")
        self.crack_label.configure(text="—", text_color=TEXT_MUTED)

    # ══════════════════════════════════════════════════════════
    #  AI Deep Analysis (Gemini)
    # ══════════════════════════════════════════════════════════
    def _run_ai_analysis(self):
        pw = self.pw_entry.get()
        if not pw:
            self._set_result("⚠  Please enter a password first.")
            return

        if not self._gemini:
            # Offline fallback
            self._offline_analysis(pw)
            return

        self.analyse_btn.configure(state="disabled", text="  ⏳  Analysing…")
        self.status_bar.configure(text="Sending to Gemini AI…", text_color=ACCENT)

        def run():
            try:
                result  = zxcvbn(pw)
                score   = result["score"]
                crack   = result.get("crack_times_display", {})
                feedback= result.get("feedback", {})

                prompt = f"""
You are a cybersecurity expert AI assistant. Analyse the following password and provide a detailed security report.

Password: {pw}
zxcvbn Score: {score}/4
zxcvbn Strength: {STRENGTH_LABELS[score]}
Estimated crack time (online): {crack.get('online_no_throttling_10_per_second','N/A')}
Estimated crack time (offline fast hash): {crack.get('offline_fast_hashing_1e10_per_second','N/A')}
zxcvbn Warnings: {feedback.get('warning','')}
zxcvbn Suggestions: {', '.join(feedback.get('suggestions',[]))}

Please provide:
1. 🔍 VULNERABILITY ASSESSMENT — What makes this password strong or weak? Any patterns, dictionary words, keyboard walks?
2. ⚠️ SPECIFIC RISKS — List concrete attack vectors that could crack this password.
3. ✅ IMPROVEMENT SUGGESTIONS — Give 3 specific, actionable improvements.
4. 💡 EXAMPLE STRONGER ALTERNATIVE — Suggest one improved version (conceptually, not identical).
5. 📊 FINAL VERDICT — One-line summary with overall security rating out of 10.

Format your response clearly with headers. Be concise but thorough.
Do NOT repeat the actual password in your response for security.
"""
                response = self._gemini.generate_content(prompt)
                report   = response.text

                self.after(0, lambda: self._set_result(
                    f"━━━  AI SECURITY REPORT  ━━━\n"
                    f"Powered by Google Gemini 3 Flash Preview\n"
                    f"{'─'*45}\n\n{report}"
                ))
                self.after(0, lambda: self.status_bar.configure(
                    text="✔  AI Analysis complete", text_color=SUCCESS_C
                ))
            except Exception as e:
                self.after(0, lambda: self._set_result(
                    f"⚠  AI Analysis failed:\n{e}\n\n"
                    f"Running offline analysis instead…\n\n"
                    + self._offline_analysis_text(pw)
                ))
                self.after(0, lambda: self.status_bar.configure(
                    text=f"AI Error: {e}", text_color=ERROR_C
                ))
            finally:
                self.after(0, lambda: self.analyse_btn.configure(
                    state="normal", text="  🤖  AI Deep Analysis"
                ))

        threading.Thread(target=run, daemon=True).start()

    def _offline_analysis(self, pw):
        report = self._offline_analysis_text(pw)
        self._set_result("━━━  OFFLINE ANALYSIS REPORT  ━━━\n"
                         "(No Gemini API key configured)\n"
                         f"{'─'*45}\n\n{report}")

    def _offline_analysis_text(self, pw):
        result   = zxcvbn(pw)
        score    = result["score"]
        feedback = result.get("feedback", {})
        crack    = result.get("crack_times_display", {})

        lines = [
            f"🔐 Password Strength: {STRENGTH_LABELS[score]} ({score}/4)\n",
            f"📊 Stats:",
            f"   • Length : {len(pw)} characters",
            f"   • Uppercase : {sum(1 for c in pw if c.isupper())}",
            f"   • Lowercase : {sum(1 for c in pw if c.islower())}",
            f"   • Numbers  : {sum(1 for c in pw if c.isdigit())}",
            f"   • Symbols  : {sum(1 for c in pw if not c.isalnum())}",
            f"\n⏱ Crack Time Estimates:",
            f"   • Online  (10/s)        : {crack.get('online_no_throttling_10_per_second','N/A')}",
            f"   • Online throttled(100/h): {crack.get('online_throttling_100_per_hour','N/A')}",
            f"   • Offline (10k/s hash)  : {crack.get('offline_slow_hashing_1e4_per_second','N/A')}",
            f"   • Offline (10B/s hash)  : {crack.get('offline_fast_hashing_1e10_per_second','N/A')}",
        ]

        if feedback.get("warning"):
            lines.append(f"\n⚠️  Warning: {feedback['warning']}")
        if feedback.get("suggestions"):
            lines.append("\n💡 Suggestions:")
            for s in feedback["suggestions"]:
                lines.append(f"   • {s}")

        lines.append("\n─────────────────────────────────────")
        lines.append("💡 To unlock full AI analysis, add your")
        lines.append("   GEMINI_API_KEY to the .env file.")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════
    #  Breach check (Have I Been Pwned)
    # ══════════════════════════════════════════════════════════
    def _check_breach(self):
        pw = self.pw_entry.get()
        if not pw:
            self._set_result("⚠  Please enter a password first.")
            return

        self.status_bar.configure(text="Checking Have I Been Pwned…", text_color=ACCENT)

        def run():
            try:
                sha1   = hashlib.sha1(pw.encode("utf-8")).hexdigest().upper()
                prefix = sha1[:5]
                suffix = sha1[5:]

                resp = requests.get(
                    f"https://api.pwnedpasswords.com/range/{prefix}",
                    headers={"Add-Padding": "true"},
                    timeout=6,
                )
                count = 0
                for line in resp.text.splitlines():
                    h, n = line.split(":")
                    if h == suffix:
                        count = int(n)
                        break

                if count > 0:
                    msg = (
                        f"🚨  BREACHED PASSWORD DETECTED!\n\n"
                        f"This password has appeared in\n"
                        f"{count:,} known data breach(es).\n\n"
                        f"⚠️  Do NOT use this password anywhere!\n"
                        f"Change it immediately on all accounts.\n\n"
                        f"Source: HaveIBeenPwned.com (k-anonymity API)"
                    )
                    self.after(0, lambda: self.status_bar.configure(
                        text=f"⚠  Found in {count:,} breaches!", text_color=ERROR_C
                    ))
                else:
                    msg = (
                        f"✅  Password NOT found in known breaches\n\n"
                        f"This password does not appear in the\n"
                        f"HaveIBeenPwned database of 14+ billion\n"
                        f"compromised passwords.\n\n"
                        f"Note: This doesn't mean it's strong —\n"
                        f"check the strength score above too."
                    )
                    self.after(0, lambda: self.status_bar.configure(
                        text="✔  Not found in breach databases", text_color=SUCCESS_C
                    ))

                self.after(0, lambda: self._set_result(
                    f"━━━  BREACH CHECK REPORT  ━━━\n"
                    f"Using HaveIBeenPwned.com API\n"
                    f"{'─'*45}\n\n{msg}"
                ))

            except Exception as e:
                self.after(0, lambda: self._set_result(f"⚠  Breach check failed:\n{e}"))
                self.after(0, lambda: self.status_bar.configure(
                    text="Breach check failed", text_color=ERROR_C
                ))

        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════
    #  Generate strong password
    # ══════════════════════════════════════════════════════════
    def _generate_password(self):
        import secrets
        import string
        chars  = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pw     = "".join(secrets.choice(chars) for _ in range(20))
        # Ensure at least 1 of each category
        pw = (
            secrets.choice(string.ascii_uppercase)
            + secrets.choice(string.ascii_lowercase)
            + secrets.choice(string.digits)
            + secrets.choice("!@#$%^&*")
            + "".join(secrets.choice(chars) for _ in range(16))
        )
        import random
        pw_list = list(pw)
        random.shuffle(pw_list)
        pw = "".join(pw_list)

        self.pw_entry.delete(0, "end")
        self.pw_entry.insert(0, pw)
        self._update_stats(pw)

        try:
            import pyperclip
            pyperclip.copy(pw)
            self.status_bar.configure(text="✔  Strong password generated & copied to clipboard!", text_color=SUCCESS_C)
        except Exception:
            self.status_bar.configure(text="✔  Strong password generated!", text_color=SUCCESS_C)

    # ── Helpers ───────────────────────────────────────────────
    def _toggle_pw(self):
        self._show_pw = not self._show_pw
        self.pw_entry.configure(show="" if self._show_pw else "●")

    def _set_result(self, text):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")
