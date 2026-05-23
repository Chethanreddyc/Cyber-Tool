"""
╔══════════════════════════════════════════════════════════╗
║            CYBER TOOL — Main Dashboard                   ║
╚══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import threading
import os

# ── Palette (shared) ───────────────────────────────────────────
BG_DARK      = "#0a0f1e"
SIDEBAR_BG   = "#080d1a"
PANEL_BG     = "#0d1526"
CARD_BG      = "#0f1c35"
ACCENT       = "#00d4ff"
ACCENT2      = "#7b2ff7"
ACCENT3      = "#ff6b35"
ACCENT4      = "#00e5a0"
TEXT_MAIN    = "#e8f4fd"
TEXT_MUTED   = "#4a6fa5"
BORDER       = "#1e3a5f"
HOVER_BG     = "#12213d"


class CyberToolApp(ctk.CTk):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Cyber Tool — AI Security Suite")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_DARK)
        self._center()

        # Active page frame holder
        self._current_page  = None
        self._nav_buttons   = {}

        self._build_layout()
        self._show_home()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 1200) // 2
        y = (sh - 750)  // 2
        self.geometry(f"1200x750+{x}+{y}")

    # ══════════════════════════════════════════════════════════
    #  Layout skeleton
    # ══════════════════════════════════════════════════════════
    def _build_layout(self):
        # ── Top bar ───────────────────────────────────────────
        self.topbar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, height=54, corner_radius=0)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)

        # Logo
        ctk.CTkLabel(
            self.topbar,
            text="  🛡  CYBER TOOL",
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left", padx=16, pady=10)

        # Top-right user info
        ctk.CTkLabel(
            self.topbar,
            text=f"👤  {self.username}",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=TEXT_MUTED,
        ).pack(side="right", padx=20)

        ctk.CTkFrame(self.topbar, width=1, fg_color=BORDER).pack(side="right", fill="y", pady=8)

        # Version tag
        ctk.CTkLabel(
            self.topbar,
            text="v1.0.0",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=BORDER,
        ).pack(side="right", padx=14)

        # ── Body (sidebar + content) ──────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(body, fg_color=SIDEBAR_BG, width=210, corner_radius=0)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Thin divider
        ctk.CTkFrame(body, width=1, fg_color=BORDER, corner_radius=0).pack(fill="y", side="left")

        # ── Content area ──────────────────────────────────────
        self.content = ctk.CTkFrame(body, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════
    #  Sidebar
    # ══════════════════════════════════════════════════════════
    def _build_sidebar(self):
        # Nav section header
        ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(20, 6))

        nav_items = [
            ("🏠", "Home",              self._show_home),
            ("🔐", "Password Analyser", self._show_password),
            ("📧", "Email Analyser",    self._show_email),
            ("💀", "Password Cracker",  self._show_cracker),
            ("🎣", "Phishing Service",  self._show_phishing),
            ("🚨", "Threat Detection",  self._show_threat),
            ("📊", "Reports",           self._show_reports),
        ]

        for icon, label, cmd in nav_items:
            self._nav_btn(icon, label, cmd)

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # Separator
        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=8)

        # Bottom section label
        ctk.CTkLabel(
            self.sidebar,
            text="COMING SOON",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color="#1e3a5f",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 6))

        for icon, label in [("👁", "User Tracking")]:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(family="Consolas", size=13),
                fg_color="transparent",
                hover_color=HOVER_BG,
                text_color="#1e3a5f",
                height=40,
                corner_radius=8,
                state="disabled",
            )
            btn.pack(fill="x", padx=10, pady=2)

        # Logout
        ctk.CTkButton(
            self.sidebar,
            text="  🚪  Logout",
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="transparent",
            hover_color="#1a0a0a",
            text_color="#ff4d6d",
            height=40,
            corner_radius=8,
            command=self._logout,
        ).pack(fill="x", padx=10, pady=(6, 16))

    def _nav_btn(self, icon, label, cmd):
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"  {icon}  {label}",
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="transparent",
            hover_color=HOVER_BG,
            text_color=TEXT_MUTED,
            height=42,
            corner_radius=8,
            command=lambda c=cmd, l=label: (self._set_active_nav(l), c()),
        )
        btn.pack(fill="x", padx=10, pady=2)
        self._nav_buttons[label] = btn

    def _set_active_nav(self, label):
        """Highlight the active sidebar button only — no page loading."""
        for lbl, btn in self._nav_buttons.items():
            btn.configure(
                fg_color="transparent",
                text_color=TEXT_MUTED,
            )
        if label in self._nav_buttons:
            self._nav_buttons[label].configure(
                fg_color="#112040",
                text_color=ACCENT,
            )

    # ══════════════════════════════════════════════════════════
    #  Clear content helper
    # ══════════════════════════════════════════════════════════
    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ══════════════════════════════════════════════════════════
    #  HOME PAGE
    # ══════════════════════════════════════════════════════════
    def _show_home(self):
        self._set_active_nav("Home")
        self._clear_content()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color=BG_DARK, scrollbar_fg_color=SIDEBAR_BG)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Hero banner ───────────────────────────────────────
        hero = ctk.CTkFrame(scroll, fg_color=PANEL_BG, corner_radius=16,
                             border_width=1, border_color=BORDER)
        hero.pack(fill="x", padx=28, pady=(28, 20))

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=30, pady=24)

        ctk.CTkLabel(
            hero_inner,
            text=f"Welcome back, {self.username} 🛡",
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            hero_inner,
            text="AI-Powered Cybersecurity Suite  •  All tools in one place",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        # ── Section title ─────────────────────────────────────
        ctk.CTkLabel(
            scroll,
            text="  ⚡  Security Modules",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=28, pady=(8, 10))

        # ── Module cards grid ─────────────────────────────────
        modules = [
            {
                "icon":  "🔐",
                "title": "Password Analyser",
                "desc":  "Analyse password strength with AI-powered suggestions, entropy scoring, and breach detection.",
                "color": ACCENT,
                "cmd":   self._show_password,
                "tag":   "AI  •  ACTIVE",
                "tag_c": "#003d4d",
            },
            {
                "icon":  "💀",
                "title": "Password Cracker",
                "desc":  "Simulate dictionary and brute-force attacks to test password resilience and cracking time.",
                "color": ACCENT3,
                "cmd":   self._show_cracker,
                "tag":   "SIM  •  ACTIVE",
                "tag_c": "#3d1a05",
            },
            {
                "icon":  "🎣",
                "title": "Phishing Service",
                "desc":  "Identify and simulate phishing emails with AI analysis. Detect spoofed senders and malicious links.",
                "color": ACCENT2,
                "cmd":   self._show_phishing,
                "tag":   "AI  •  ACTIVE",
                "tag_c": "#1a0a3d",
            },
            {
                "icon":  "🚨",
                "title": "Threat Detection",
                "desc":  "Real-time threat monitoring and AI-based suspicious behaviour detection across inputs.",
                "color": ACCENT4,
                "cmd":   self._show_threat,
                "tag":   "AI  •  ACTIVE",
                "tag_c": "#003d25",
            },
        ]

        # 2-column grid using a frame
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=4)
        grid.columnconfigure((0, 1), weight=1, uniform="col")

        for i, mod in enumerate(modules):
            card = self._module_card(grid, mod)
            card.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")

        # ── Email analyser card (full-width) ──────────────────
        ctk.CTkLabel(
            scroll,
            text="  🔍  AI Analysers",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=28, pady=(12, 10))

        email_mod = {
            "icon":  "📧",
            "title": "Suspicious Email Analyser",
            "desc":  "Paste any email and let Gemini AI dissect it — headers, sender reputation, phishing signals, link safety, and an overall threat score.",
            "color": "#f0b429",
            "cmd":   self._show_email,
            "tag":   "AI  •  ACTIVE",
            "tag_c": "#3d2e05",
        }
        email_card = self._module_card(scroll, email_mod, full_width=True)
        email_card.pack(fill="x", padx=30, pady=(0, 20))

    def _module_card(self, parent, mod, full_width=False):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=18)

        # Top row: icon + tag
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top,
            text=mod["icon"],
            font=ctk.CTkFont(size=32),
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=mod["tag"],
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color=mod["color"],
            fg_color=mod["tag_c"],
            corner_radius=6,
            padx=8,
            pady=3,
        ).pack(side="right")

        # Title
        ctk.CTkLabel(
            inner,
            text=mod["title"],
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            text_color=mod["color"],
            anchor="w",
        ).pack(fill="x", pady=(10, 4))

        # Description
        ctk.CTkLabel(
            inner,
            text=mod["desc"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
            anchor="w",
            wraplength=340 if not full_width else 700,
            justify="left",
        ).pack(fill="x")

        # Launch button
        ctk.CTkButton(
            inner,
            text="  Launch →",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            fg_color=mod["color"],
            hover_color=mod["color"],
            text_color="#05101a",
            height=36,
            corner_radius=8,
            width=110,
            command=mod["cmd"],
        ).pack(anchor="w", pady=(14, 0))

        # Hover effects
        def on_enter(_):
            card.configure(border_color=mod["color"])
        def on_leave(_):
            card.configure(border_color=BORDER)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        return card

    # ══════════════════════════════════════════════════════════
    #  Page loaders
    # ══════════════════════════════════════════════════════════
    def _load_page(self, PageClass, nav_label):
        self._set_active_nav(nav_label)
        self._clear_content()
        try:
            page = PageClass(self.content)
            page.pack(fill="both", expand=True)
        except Exception as e:
            self._page_error(str(e))

    def _page_error(self, msg):
        ctk.CTkLabel(
            self.content,
            text=f"⚠  Error loading page:\n{msg}",
            font=ctk.CTkFont(family="Consolas", size=14),
            text_color="#ff4d6d",
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _placeholder_page(self, title, icon, color, nav_label):
        self._set_active_nav(nav_label)
        self._clear_content()
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text=icon, font=ctk.CTkFont(size=64)).pack()
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color=color,
        ).pack(pady=10)
        ctk.CTkLabel(
            frame,
            text="Module coming soon…",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=TEXT_MUTED,
        ).pack()

    # ── Page navigators ───────────────────────────────────────
    def _show_password(self):
        self._set_active_nav("Password Analyser")
        self._clear_content()
        try:
            from modules.password_analyzer import PasswordAnalyzerPage
            PasswordAnalyzerPage(self.content).pack(fill="both", expand=True)
        except Exception as e:
            self._page_error(str(e))

    def _show_email(self):
        self._set_active_nav("Email Analyser")
        self._clear_content()
        try:
            from modules.email_analyzer import EmailAnalyzerPage
            EmailAnalyzerPage(self.content).pack(fill="both", expand=True)
        except Exception as e:
            self._page_error(str(e))

    def _show_cracker(self):
        self._set_active_nav("Password Cracker")
        self._clear_content()
        try:
            from modules.password_cracker import PasswordCrackerPage
            PasswordCrackerPage(self.content).pack(fill="both", expand=True)
        except Exception as e:
            self._page_error(str(e))

    def _show_phishing(self):
        self._set_active_nav("Phishing Service")
        self._clear_content()
        try:
            from modules.phishing_service import PhishingServicePage
            PhishingServicePage(self.content).pack(fill="both", expand=True)
        except Exception as e:
            self._page_error(str(e))

    def _show_threat(self):
        self._placeholder_page("Threat Detection", "🚨", ACCENT4, "Threat Detection")

    def _show_reports(self):
        self._set_active_nav("Reports")
        self._clear_content()
        try:
            from modules.reports import ReportsPage
            ReportsPage(self.content).pack(fill="both", expand=True)
        except Exception as e:
            self._page_error(str(e))

    # ── Logout ────────────────────────────────────────────────
    def _logout(self):
        self.destroy()
        from modules.login import LoginWindow
        def relaunch(user):
            app = CyberToolApp(username=user)
            app.mainloop()
        LoginWindow(on_success=relaunch).mainloop()
