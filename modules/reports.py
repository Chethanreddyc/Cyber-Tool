"""
╔══════════════════════════════════════════════════════════╗
║       CYBER TOOL — Reports Dashboard                     ║
║   Live stats: passwords cracked, emails analyzed,        ║
║   phishing sent, and more                                ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import os
import sys
import time
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import stats_tracker

# ── Palette ────────────────────────────────────────────────────
BG_DARK    = "#0a0f1e"
PANEL_BG   = "#0d1526"
CARD_BG    = "#0f1c35"
ACCENT     = "#00d4ff"
ACCENT2    = "#7b2ff7"
TEXT_MAIN  = "#e8f4fd"
TEXT_MUTED = "#4a6fa5"
BORDER     = "#1e3a5f"
ERROR_C    = "#ff4d6d"
SUCCESS_C  = "#00e5a0"
WARN_C     = "#f0b429"
ORANGE     = "#ff6b35"
ENTRY_BG   = "#070e1c"


class ReportsPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)
        self._build_ui()
        self._refresh()

    # ══════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  📊  Activity Reports",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(side="left", padx=24, pady=14)

        # Refresh button
        ctk.CTkButton(
            header,
            text="  🔄  Refresh",
            width=110, height=34,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color="#0a1a2e",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            command=self._refresh,
        ).pack(side="right", padx=10)

        # Reset button
        ctk.CTkButton(
            header,
            text="  🗑  Reset Stats",
            width=120, height=34,
            fg_color="transparent", border_width=1, border_color=ERROR_C,
            hover_color="#1a0008",
            text_color=ERROR_C,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            command=self._confirm_reset,
        ).pack(side="right", padx=(0, 6))

        # Last updated label
        self.updated_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=TEXT_MUTED,
        )
        self.updated_label.pack(side="right", padx=10)

        # ── Scrollable body ───────────────────────────────────
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                            scrollbar_fg_color=PANEL_BG)
        self.body.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Stat cards row ────────────────────────────────────
        self._cards_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self._cards_frame.pack(fill="x", pady=(0, 16))

        # ── Charts row ────────────────────────────────────────
        charts_row = ctk.CTkFrame(self.body, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 16))
        charts_row.columnconfigure(0, weight=1)
        charts_row.columnconfigure(1, weight=1)
        charts_row.rowconfigure(0, weight=1)

        self._chart_left  = ctk.CTkFrame(
            charts_row, fg_color=PANEL_BG, corner_radius=14,
            border_width=1, border_color=BORDER, height=260,
        )
        self._chart_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._chart_left.pack_propagate(False)

        self._chart_right = ctk.CTkFrame(
            charts_row, fg_color=PANEL_BG, corner_radius=14,
            border_width=1, border_color=BORDER, height=260,
        )
        self._chart_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._chart_right.pack_propagate(False)

        # ── Activity Log ──────────────────────────────────────
        log_frame = ctk.CTkFrame(self.body, fg_color=PANEL_BG, corner_radius=14,
                                  border_width=1, border_color=BORDER)
        log_frame.pack(fill="both", expand=True)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            log_header, text="📋  ACTIVITY LOG",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(side="left")

        self.log_count_label = ctk.CTkLabel(
            log_header, text="",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=TEXT_MUTED,
        )
        self.log_count_label.pack(side="right")

        self.log_box = ctk.CTkTextbox(
            log_frame,
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=8, wrap="word", height=260,
            state="disabled",
        )
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    # ══════════════════════════════════════════════════════════
    #  Refresh (load latest stats)
    # ══════════════════════════════════════════════════════════
    def _refresh(self):
        try:
            s = stats_tracker.get_all()
        except Exception:
            s = {}

        # ── Stat Cards ────────────────────────────────────────
        for w in self._cards_frame.winfo_children():
            w.destroy()

        card_defs = [
            ("🔑", "Passwords\nAnalyzed",  s.get("passwords_analyzed", 0),  ACCENT,    "Total passwords analyzed"),
            ("💀", "Hashes\nCracked",      s.get("passwords_cracked", 0),   ORANGE,    "Successful hash cracks"),
            ("📧", "Emails\nAnalyzed",     s.get("emails_analyzed", 0),     WARN_C,    "Emails scanned for phishing"),
            ("🚨", "Phishing\nDetected",   s.get("phishing_emails_detected",0), ERROR_C,   "Emails flagged as phishing"),
            ("🎣", "Phishing\nEmails Sent",s.get("phishing_emails_sent", 0),  "#b44fff",  "Simulation emails sent"),
            ("🔍", "Breach\nChecks",       s.get("breaches_checked", 0),    SUCCESS_C, "Have I Been Pwned lookups"),
        ]

        self._cards_frame.columnconfigure(
            list(range(len(card_defs))), weight=1, uniform="card"
        )

        for col, (icon, label, value, color, tip) in enumerate(card_defs):
            self._stat_card(self._cards_frame, col, icon, label, value, color, tip)

        # ── Bar chart (activity breakdown) ────────────────────
        for w in self._chart_left.winfo_children():
            w.destroy()
        for w in self._chart_right.winfo_children():
            w.destroy()

        self._build_bar_chart(self._chart_left, s)
        self._build_donut_summary(self._chart_right, s)

        # ── Activity log ──────────────────────────────────────
        history = s.get("history", [])
        self.log_count_label.configure(text=f"{len(history)} events")

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")

        if not history:
            self.log_box.insert("1.0", "  No activity recorded yet.\n  Use any module and come back to see your stats!")
        else:
            # Newest first
            for entry in reversed(history):
                ts     = entry.get("time", "")
                event  = entry.get("event", "")
                detail = entry.get("detail", "")
                line   = f"[{ts}]  {event}"
                if detail:
                    line += f"\n              └─ {detail}"
                self.log_box.insert("end", line + "\n")

        self.log_box.configure(state="disabled")

        # Timestamp
        self.updated_label.configure(
            text=f"Last updated: {time.strftime('%H:%M:%S')}"
        )

    # ── Stat Card ─────────────────────────────────────────────
    def _stat_card(self, parent, col, icon, label, value, color, tip):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=14,
                             border_width=1, border_color=BORDER)
        card.grid(row=0, column=col, sticky="nsew", padx=5, pady=0)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # Icon
        ctk.CTkLabel(
            inner, text=icon,
            font=ctk.CTkFont(size=28),
            text_color=color,
        ).pack(anchor="w")

        # Value
        ctk.CTkLabel(
            inner, text=str(value),
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
            text_color=color,
        ).pack(anchor="w", pady=(4, 0))

        # Label
        ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            justify="left",
        ).pack(anchor="w")

        # Thin color accent bar at bottom
        ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0).pack(
            fill="x", side="bottom"
        )

    # ── Bar Chart ─────────────────────────────────────────────
    def _build_bar_chart(self, parent, s):
        ctk.CTkLabel(
            parent, text="📊  MODULE ACTIVITY",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 10))

        bars = [
            ("Passwords Analyzed", s.get("passwords_analyzed", 0),  ACCENT),
            ("Hashes Cracked",     s.get("passwords_cracked", 0),   ORANGE),
            ("Emails Analyzed",    s.get("emails_analyzed", 0),     WARN_C),
            ("Phishing Detected",  s.get("phishing_emails_detected",0), ERROR_C),
            ("Phishing Sent",      s.get("phishing_emails_sent", 0),   "#b44fff"),
            ("Breach Checks",      s.get("breaches_checked", 0),    SUCCESS_C),
        ]

        max_val = max((v for _, v, _ in bars), default=1) or 1

        for label, val, color in bars:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)

            ctk.CTkLabel(
                row, text=label,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color=TEXT_MUTED,
                width=140, anchor="w",
            ).pack(side="left")

            bar_bg = ctk.CTkFrame(row, fg_color="#0a1a30", height=14, corner_radius=7)
            bar_bg.pack(side="left", fill="x", expand=True)

            fill_w = max(val / max_val, 0.02) if val > 0 else 0
            bar_fill = ctk.CTkFrame(bar_bg, fg_color=color, height=14, corner_radius=7)
            bar_fill.place(relx=0, rely=0, relwidth=fill_w, relheight=1)

            ctk.CTkLabel(
                row, text=str(val),
                font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                text_color=color, width=36,
            ).pack(side="left", padx=(6, 0))

    # ── Donut Summary (text-based) ────────────────────────────
    def _build_donut_summary(self, parent, s):
        ctk.CTkLabel(
            parent, text="🧮  SUMMARY & TOTALS",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 10))

        total_events = len(s.get("history", []))
        cracked      = s.get("passwords_cracked", 0)
        analyzed_pw  = s.get("passwords_analyzed", 0)
        emails       = s.get("emails_analyzed", 0)
        detected     = s.get("phishing_emails_detected", 0)
        sent         = s.get("phishing_emails_sent", 0)
        breaches     = s.get("breaches_checked", 0)

        crack_rate    = f"{cracked/analyzed_pw*100:.1f}%" if analyzed_pw else "—"
        detect_rate   = f"{detected/emails*100:.1f}%"    if emails       else "—"
        last_reset    = s.get("last_reset") or "Never"

        summary_rows = [
            ("Total Events Logged",   str(total_events),    ACCENT),
            ("Crack Success Rate",    crack_rate,            ORANGE),
            ("Phishing Detection Rate", detect_rate,        ERROR_C),
            ("Phishing Campaigns",    str(sent),             "#b44fff"),
            ("HIBP Breach Lookups",   str(breaches),         SUCCESS_C),
            ("Stats Last Reset",      last_reset,            TEXT_MUTED),
        ]

        for label, val, color in summary_rows:
            row = ctk.CTkFrame(parent, fg_color=ENTRY_BG, corner_radius=8)
            row.pack(fill="x", padx=20, pady=3)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=8)

            ctk.CTkLabel(
                inner, text=label,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color=TEXT_MUTED, anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                inner, text=val,
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                text_color=color,
            ).pack(side="right")

    # ══════════════════════════════════════════════════════════
    #  Reset confirmation
    # ══════════════════════════════════════════════════════════
    def _confirm_reset(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Reset")
        dialog.geometry("360x200")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#12040a")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="⚠  Reset All Statistics?",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=ERROR_C,
        ).pack(pady=(24, 8))

        ctk.CTkLabel(
            dialog,
            text="This will permanently clear all counters\nand the activity log. This cannot be undone.",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED, justify="center",
        ).pack(pady=(0, 16))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row, text="✓  Reset All",
            width=130, height=36,
            fg_color=ERROR_C, hover_color="#c0392b",
            text_color="#fff",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            corner_radius=8,
            command=lambda: [dialog.destroy(), self._do_reset()],
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="Cancel",
            width=90, height=36,
            fg_color="transparent", border_width=1, border_color=BORDER,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            command=dialog.destroy,
        ).pack(side="left", padx=6)

    def _do_reset(self):
        stats_tracker.reset_all()
        self._refresh()
