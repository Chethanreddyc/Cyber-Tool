"""
╔══════════════════════════════════════════════════════════╗
║     CYBER TOOL — Security Awareness Training             ║
║   Quiz-based red-team awareness training platform        ║
║   For AUTHORISED security education ONLY                 ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import threading
import time
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Palette ────────────────────────────────────────────────────
BG_DARK    = "#0a0f1e"
PANEL_BG   = "#0d1526"
CARD_BG    = "#0f1c35"
ACCENT     = "#00e5a0"       # green theme for training
ACCENT2    = "#00d4ff"
ACCENT3    = "#7b2ff7"
TEXT_MAIN  = "#e8f4fd"
TEXT_MUTED = "#4a6fa5"
BORDER     = "#1e3a5f"
ERROR_C    = "#ff4d6d"
SUCCESS_C  = "#00e5a0"
WARN_C     = "#f0b429"
ENTRY_BG   = "#070e1c"

# ── Category colours ───────────────────────────────────────────
CAT_COLORS = {
    "Phishing":   "#7b2ff7",
    "Password":   "#00d4ff",
    "Social Eng": "#ff6b35",
    "General":    "#00e5a0",
}

# ── Question bank (placeholder — logic added next) ─────────────
QUESTIONS = []   # populated by quiz engine in next phase


# ══════════════════════════════════════════════════════════════
#  Main Page
# ══════════════════════════════════════════════════════════════
class AwarenessTrainingPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=0)
        self._score        = 0
        self._total        = 0
        self._streak       = 0
        self._max_streak   = 0
        self._wrong_cats   = {}   # category → wrong count
        self._session_time = 0
        self._timer_running= False
        self._build_ui()
        self._show_home()

    # ══════════════════════════════════════════════════════════
    #  Master layout
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── Header bar ────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="  🎓  Security Awareness Training",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(side="left", padx=24, pady=14)

        ctk.CTkLabel(
            header,
            text="🛡  Red-Team Education Platform",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=WARN_C,
        ).pack(side="right", padx=24)

        # ── Body: left sidebar + right content ────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        # divider
        ctk.CTkFrame(body, width=1, fg_color=BORDER,
                     corner_radius=0).pack(fill="y", side="left")

        # content area
        self.content = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(fill="both", expand=True)

    # ── Sidebar ───────────────────────────────────────────────
    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=PANEL_BG,
                               width=200, corner_radius=0)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="MODULES",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=18, pady=(20, 8))

        self._nav_btns = {}
        nav_items = [
            ("🏠", "Home",      self._show_home),
            ("🎣", "Phishing",  lambda: self._start_quiz("Phishing")),
            ("🔐", "Password",  lambda: self._start_quiz("Password")),
            ("🧠", "Social Eng",lambda: self._start_quiz("Social Eng")),
            ("🛡", "General",   lambda: self._start_quiz("General")),
            ("🏆", "Full Test", lambda: self._start_quiz("All")),
        ]
        for icon, label, cmd in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(family="Consolas", size=13),
                fg_color="transparent",
                hover_color="#0d1f3a",
                text_color=TEXT_MUTED,
                height=40, corner_radius=8,
                command=lambda c=cmd, l=label: (self._set_nav(l), c()),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_btns[label] = btn

        # spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # ── Live session score ─────────────────────────────────
        ctk.CTkFrame(sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=6)

        ctk.CTkLabel(
            sidebar, text="SESSION SCORE",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(pady=(4, 0))

        self.score_big = ctk.CTkLabel(
            sidebar, text="—",
            font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
            text_color=ACCENT,
        )
        self.score_big.pack()

        self.score_sub = ctk.CTkLabel(
            sidebar, text="Start a quiz",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=TEXT_MUTED,
        )
        self.score_sub.pack(pady=(0, 4))

        # streak
        self.streak_label = ctk.CTkLabel(
            sidebar, text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=WARN_C,
        )
        self.streak_label.pack(pady=(0, 12))

    def _set_nav(self, label):
        for lbl, btn in self._nav_btns.items():
            btn.configure(fg_color="transparent", text_color=TEXT_MUTED)
        if label in self._nav_btns:
            self._nav_btns[label].configure(
                fg_color="#0a2010", text_color=ACCENT)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ══════════════════════════════════════════════════════════
    #  HOME PAGE
    # ══════════════════════════════════════════════════════════
    def _show_home(self):
        self._set_nav("Home")
        self._clear_content()

        scroll = ctk.CTkScrollableFrame(
            self.content, fg_color=BG_DARK, scrollbar_fg_color=PANEL_BG)
        scroll.pack(fill="both", expand=True)

        # ── Hero ──────────────────────────────────────────────
        hero = ctk.CTkFrame(scroll, fg_color=PANEL_BG, corner_radius=16,
                             border_width=1, border_color=BORDER)
        hero.pack(fill="x", padx=28, pady=(28, 20))

        hi = ctk.CTkFrame(hero, fg_color="transparent")
        hi.pack(fill="x", padx=30, pady=24)

        ctk.CTkLabel(
            hi, text="🎓  Welcome to the Training Centre",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color=ACCENT, anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            hi,
            text="Test and improve your cybersecurity awareness with real-world attack scenarios.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(anchor="w", pady=(6, 0))

        # ── Module cards ──────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="  ⚡  Choose a Training Module",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", padx=28, pady=(4, 10))

        modules = [
            {
                "icon": "🎣", "title": "Phishing Recognition",
                "desc": "Can you spot a fake email? Analyse real-looking phishing scenarios and learn the tell-tale signs.",
                "color": "#7b2ff7", "tag": "BEGINNER • 10 Q",
                "cmd": lambda: (self._set_nav("Phishing"), self._start_quiz("Phishing")),
            },
            {
                "icon": "🔐", "title": "Password Security",
                "desc": "Test your knowledge of password hygiene, entropy, breach patterns, and best practices.",
                "color": "#00d4ff", "tag": "BEGINNER • 8 Q",
                "cmd": lambda: (self._set_nav("Password"), self._start_quiz("Password")),
            },
            {
                "icon": "🧠", "title": "Social Engineering",
                "desc": "USB drops, pretexting, vishing, tailgating — would you fall for these real-world attacks?",
                "color": "#ff6b35", "tag": "INTERMEDIATE • 8 Q",
                "cmd": lambda: (self._set_nav("Social Eng"), self._start_quiz("Social Eng")),
            },
            {
                "icon": "🛡", "title": "General Security",
                "desc": "MFA, public Wi-Fi, software updates, device security — core cyber hygiene knowledge.",
                "color": "#00e5a0", "tag": "ALL LEVELS • 8 Q",
                "cmd": lambda: (self._set_nav("General"), self._start_quiz("General")),
            },
        ]

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=4)
        grid.columnconfigure((0, 1), weight=1, uniform="col")

        for i, mod in enumerate(modules):
            card = self._home_card(grid, mod)
            card.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")

        # ── Full Test button ───────────────────────────────────
        ctk.CTkButton(
            scroll,
            text="  🏆  Start Full Assessment  (all 34 questions)",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color=ACCENT3,
            hover_color="#5a1fc7",
            text_color="#fff",
            height=50, corner_radius=12,
            command=lambda: (self._set_nav("Full Test"),
                             self._start_quiz("All")),
        ).pack(fill="x", padx=30, pady=(12, 28))

    def _home_card(self, parent, mod):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=14,
                             border_width=1, border_color=BORDER)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=18)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=mod["icon"],
                     font=ctk.CTkFont(size=32)).pack(side="left")
        ctk.CTkLabel(top, text=mod["tag"],
                     font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                     text_color=mod["color"],
                     fg_color=ENTRY_BG,
                     corner_radius=6, padx=8, pady=3).pack(side="right")

        ctk.CTkLabel(inner, text=mod["title"],
                     font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                     text_color=mod["color"], anchor="w",
                     ).pack(fill="x", pady=(10, 4))

        ctk.CTkLabel(inner, text=mod["desc"],
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color=TEXT_MUTED, anchor="w",
                     wraplength=280, justify="left",
                     ).pack(fill="x")

        ctk.CTkButton(
            inner, text="  Start →",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=mod["color"], hover_color=mod["color"],
            text_color="#05101a",
            height=34, corner_radius=8, width=100,
            command=mod["cmd"],
        ).pack(anchor="w", pady=(14, 0))

        card.bind("<Enter>", lambda _, c=card, col=mod["color"]: c.configure(border_color=col))
        card.bind("<Leave>", lambda _, c=card: c.configure(border_color=BORDER))
        return card

    # ══════════════════════════════════════════════════════════
    #  QUIZ LAYOUT SKELETON
    # ══════════════════════════════════════════════════════════
    def _start_quiz(self, category):
        """Build the quiz UI. Logic & questions wired in next phase."""
        self._clear_content()
        self._score   = 0
        self._total   = 0
        self._streak  = 0
        self._category = category

        # outer scroll
        outer = ctk.CTkFrame(self.content, fg_color=BG_DARK,
                              corner_radius=0)
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Progress / score strip ─────────────────────────────
        top_strip = ctk.CTkFrame(outer, fg_color=PANEL_BG,
                                  corner_radius=12, height=56,
                                  border_width=1, border_color=BORDER)
        top_strip.pack(fill="x", pady=(0, 12))
        top_strip.pack_propagate(False)

        ts_inner = ctk.CTkFrame(top_strip, fg_color="transparent")
        ts_inner.pack(fill="both", expand=True, padx=16, pady=8)

        # category badge
        self.cat_badge = ctk.CTkLabel(
            ts_inner,
            text=f"  {'ALL MODULES' if category == 'All' else category.upper()}  ",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#05101a",
            fg_color=CAT_COLORS.get(category, ACCENT3),
            corner_radius=6,
        )
        self.cat_badge.pack(side="left", padx=(0, 12))

        self.q_counter = ctk.CTkLabel(
            ts_inner, text="Question  0  /  ?",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=TEXT_MUTED,
        )
        self.q_counter.pack(side="left")

        # score in top strip
        self.strip_score = ctk.CTkLabel(
            ts_inner, text="Score: 0",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=ACCENT,
        )
        self.strip_score.pack(side="right", padx=(0, 8))

        self.timer_lbl = ctk.CTkLabel(
            ts_inner, text="⏱  0:00",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=TEXT_MUTED,
        )
        self.timer_lbl.pack(side="right", padx=16)

        # progress bar
        self.quiz_progress = ctk.CTkProgressBar(
            outer, height=6, corner_radius=3,
            progress_color=ACCENT, fg_color=CARD_BG,
        )
        self.quiz_progress.set(0)
        self.quiz_progress.pack(fill="x", pady=(0, 14))

        # ── Question card ─────────────────────────────────────
        self.q_card = ctk.CTkFrame(outer, fg_color=PANEL_BG,
                                    corner_radius=16,
                                    border_width=1, border_color=BORDER)
        self.q_card.pack(fill="x", pady=(0, 12))

        q_inner = ctk.CTkFrame(self.q_card, fg_color="transparent")
        q_inner.pack(fill="x", padx=24, pady=20)

        # category tag on card
        self.q_cat_tag = ctk.CTkLabel(
            q_inner, text="",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        )
        self.q_cat_tag.pack(fill="x")

        # question text
        self.q_label = ctk.CTkLabel(
            q_inner, text="Loading questions…",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=TEXT_MAIN, anchor="w",
            wraplength=680, justify="left",
        )
        self.q_label.pack(fill="x", pady=(8, 0))

        # optional scenario box (for email/chat scenario questions)
        self.scenario_box = ctk.CTkTextbox(
            q_inner,
            fg_color=ENTRY_BG, border_color=BORDER, border_width=1,
            text_color="#a8c7fa",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8, height=100, wrap="word",
            state="disabled",
        )
        # packed only when needed

        # ── Answer buttons ────────────────────────────────────
        self.ans_frame = ctk.CTkFrame(outer, fg_color="transparent")
        self.ans_frame.pack(fill="x", pady=(0, 10))
        self.ans_frame.columnconfigure((0, 1), weight=1, uniform="ans")

        self._ans_btns = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.ans_frame,
                text="",
                font=ctk.CTkFont(family="Consolas", size=13),
                fg_color=CARD_BG,
                hover_color="#1a2d50",
                border_width=1, border_color=BORDER,
                text_color=TEXT_MAIN,
                height=56, corner_radius=12,
                anchor="w",
            )
            btn.grid(row=i // 2, column=i % 2, padx=6, pady=5, sticky="ew")
            self._ans_btns.append(btn)

        # ── Feedback strip ────────────────────────────────────
        self.feedback_card = ctk.CTkFrame(
            outer, fg_color=CARD_BG, corner_radius=12,
            border_width=1, border_color=BORDER,
        )
        # not packed until answer selected

        fb_inner = ctk.CTkFrame(self.feedback_card, fg_color="transparent")
        fb_inner.pack(fill="x", padx=20, pady=14)

        self.fb_icon  = ctk.CTkLabel(
            fb_inner, text="",
            font=ctk.CTkFont(size=28),
        )
        self.fb_icon.pack(side="left", padx=(0, 12))

        fb_text_col = ctk.CTkFrame(fb_inner, fg_color="transparent")
        fb_text_col.pack(side="left", fill="x", expand=True)

        self.fb_result = ctk.CTkLabel(
            fb_text_col, text="",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=SUCCESS_C, anchor="w",
        )
        self.fb_result.pack(fill="x")

        self.fb_explain = ctk.CTkLabel(
            fb_text_col, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED, anchor="w",
            wraplength=560, justify="left",
        )
        self.fb_explain.pack(fill="x", pady=(4, 0))

        self.next_btn = ctk.CTkButton(
            self.feedback_card,
            text="  Next Question →",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color=ACCENT, hover_color="#00b880",
            text_color="#05101a",
            height=40, corner_radius=10,
            command=self._next_question,
        )
        self.next_btn.pack(fill="x", padx=20, pady=(0, 14))

        # ── Stop quiz button ──────────────────────────────────
        ctk.CTkButton(
            outer,
            text="  ⛔  End Session",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="transparent", border_width=1, border_color=ERROR_C,
            hover_color="#1a0008", text_color=ERROR_C,
            height=34, corner_radius=8,
            command=self._end_quiz,
        ).pack(pady=(4, 0))

        # kick off the quiz
        self._init_quiz(category)

    # ══════════════════════════════════════════════════════════
    #  Stubs — quiz engine wired in next phase
    # ══════════════════════════════════════════════════════════
    def _init_quiz(self, category):
        self.q_label.configure(
            text="⚠  Quiz engine loading…\n\nQuestions will be wired in the next phase.",
            text_color=WARN_C,
        )
        for btn in self._ans_btns:
            btn.configure(text="—", state="disabled")

    def _next_question(self):
        pass

    def _end_quiz(self):
        self._show_home()

    # ══════════════════════════════════════════════════════════
    #  Score helpers  (sidebar live update)
    # ══════════════════════════════════════════════════════════
    def _refresh_sidebar_score(self):
        if self._total == 0:
            self.score_big.configure(text="—")
            self.score_sub.configure(text="Start a quiz")
            self.streak_label.configure(text="")
        else:
            pct = int(self._score / self._total * 100)
            self.score_big.configure(text=f"{pct}%")
            self.score_sub.configure(
                text=f"{self._score} / {self._total} correct")
            if self._streak >= 3:
                self.streak_label.configure(
                    text=f"🔥  {self._streak} streak!")
            else:
                self.streak_label.configure(text="")
