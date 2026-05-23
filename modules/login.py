"""
╔══════════════════════════════════════════════════════════╗
║              CYBER TOOL — Login Screen                   ║
╚══════════════════════════════════════════════════════════╝
Default Credentials:
    Username : admin
    Password : admin123
"""

import customtkinter as ctk
from tkinter import messagebox
import time
import threading


# ── Default credentials (can be extended to a DB/file later) ──
DEFAULT_USERS = {
    "admin": "admin123",
}

# ── Palette ────────────────────────────────────────────────────
BG_DARK      = "#0a0f1e"   # deep navy background
PANEL_BG     = "#0d1526"   # card background
ACCENT       = "#00d4ff"   # cyan accent
ACCENT2      = "#7b2ff7"   # purple accent
ENTRY_BG     = "#111c35"   # input background
ENTRY_BORDER = "#1e3a5f"   # input border
TEXT_MAIN    = "#e8f4fd"   # primary text
TEXT_MUTED   = "#4a6fa5"   # muted / placeholder text
BTN_HOVER    = "#00aacc"   # button hover
ERROR_COLOR  = "#ff4d6d"   # error red
SUCCESS_COLOR= "#00e5a0"   # success green


class LoginWindow(ctk.CTk):
    """Standalone login window. Calls on_success(username) when authenticated."""

    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        # ── Window setup ───────────────────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Cyber Tool — Login")
        self.geometry("480x620")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        self._center_window(480, 620)

        # Track login attempts
        self._attempts      = 0
        self._max_attempts  = 5
        self._locked        = False
        self._show_password = False

        self._build_ui()
        self._start_animations()

    # ── Centre window on screen ────────────────────────────────
    def _center_window(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI Construction ────────────────────────────────────────
    def _build_ui(self):
        # Outer frame (card with border illusion)
        self.card = ctk.CTkFrame(
            self,
            fg_color=PANEL_BG,
            corner_radius=24,
            border_width=1,
            border_color=ENTRY_BORDER,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88, relheight=0.92)

        # ── Shield icon area ───────────────────────────────────
        icon_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        icon_frame.pack(pady=(36, 0))

        self.shield_label = ctk.CTkLabel(
            icon_frame,
            text="🛡",
            font=("Segoe UI Emoji", 56),
        )
        self.shield_label.pack()

        # Glowing ring (canvas trick)
        self.glow_alpha = 0.0
        self.glow_dir   = 1

        # ── App title ──────────────────────────────────────────
        ctk.CTkLabel(
            self.card,
            text="CYBER TOOL",
            font=ctk.CTkFont(family="Consolas", size=26, weight="bold"),
            text_color=ACCENT,
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            self.card,
            text="AI-Powered Security Suite",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 28))

        # ── Separator ─────────────────────────────────────────
        ctk.CTkFrame(self.card, height=1, fg_color=ENTRY_BORDER).pack(
            fill="x", padx=30, pady=(0, 24)
        )

        # ── Form container ────────────────────────────────────
        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(fill="x", padx=30)

        # Username
        ctk.CTkLabel(
            form,
            text="USERNAME",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.username_entry = ctk.CTkEntry(
            form,
            placeholder_text="Enter username",
            placeholder_text_color=TEXT_MUTED,
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=14),
            height=44,
            corner_radius=10,
        )
        self.username_entry.pack(fill="x", pady=(0, 18))
        self.username_entry.insert(0, "admin")          # pre-fill default

        # Password label row
        pw_label_row = ctk.CTkFrame(form, fg_color="transparent")
        pw_label_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            pw_label_row,
            text="PASSWORD",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left")

        # Password entry row (entry + eye toggle)
        pw_row = ctk.CTkFrame(form, fg_color="transparent")
        pw_row.pack(fill="x", pady=(0, 6))

        self.password_entry = ctk.CTkEntry(
            pw_row,
            placeholder_text="Enter password",
            placeholder_text_color=TEXT_MUTED,
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            border_width=1,
            text_color=TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=14),
            height=44,
            corner_radius=10,
            show="●",
        )
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.insert(0, "admin123")       # pre-fill default

        self.eye_btn = ctk.CTkButton(
            pw_row,
            text="👁",
            width=44,
            height=44,
            fg_color=ENTRY_BG,
            hover_color="#1a2a4a",
            border_color=ENTRY_BORDER,
            border_width=1,
            corner_radius=10,
            command=self._toggle_password,
            font=ctk.CTkFont(size=16),
        )
        self.eye_btn.pack(side="left", padx=(6, 0))

        # ── Status / error label ──────────────────────────────
        self.status_label = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=ERROR_COLOR,
            anchor="w",
            height=20,
        )
        self.status_label.pack(fill="x", pady=(6, 0))

        # ── Login button ──────────────────────────────────────
        self.login_btn = ctk.CTkButton(
            form,
            text="  LOGIN  →",
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            height=50,
            corner_radius=12,
            fg_color=ACCENT,
            hover_color=BTN_HOVER,
            text_color="#05101a",
            command=self._attempt_login,
        )
        self.login_btn.pack(fill="x", pady=(14, 0))

        # Bind Enter key
        self.bind("<Return>", lambda e: self._attempt_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())

        # ── Default-credentials hint ──────────────────────────
        hint_frame = ctk.CTkFrame(self.card, fg_color="#0a1020", corner_radius=10)
        hint_frame.pack(fill="x", padx=30, pady=(22, 0))

        ctk.CTkLabel(
            hint_frame,
            text="⚑  Default credentials are pre-filled",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#3a85b5",
            pady=8,
        ).pack()

        # ── Footer ────────────────────────────────────────────
        ctk.CTkLabel(
            self.card,
            text="© 2026 Cyber Tool  •  For Authorized Use Only",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#1e3a5f",
        ).pack(side="bottom", pady=(0, 16))

    # ── Toggle password visibility ────────────────────────────
    def _toggle_password(self):
        self._show_password = not self._show_password
        self.password_entry.configure(show="" if self._show_password else "●")
        self.eye_btn.configure(text="🙈" if self._show_password else "👁")

    # ── Pulsing glow animation on shield ─────────────────────
    def _start_animations(self):
        self._pulse_shield()

    def _pulse_shield(self):
        """Slowly pulse the shield emoji colour between cyan tints."""
        colors = [
            "#00d4ff", "#00c4ef", "#00b4df",
            "#00c4ef", "#00d4ff", "#20e4ff",
        ]
        self._pulse_idx = 0

        def step():
            if not self.winfo_exists():
                return
            color = colors[self._pulse_idx % len(colors)]
            try:
                self.shield_label.configure(text_color=color)
            except Exception:
                return
            self._pulse_idx += 1
            self.after(400, step)

        self.after(400, step)

    # ── Login logic ───────────────────────────────────────────
    def _attempt_login(self):
        if self._locked:
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Basic empty-field check
        if not username:
            self._show_error("⚠  Username cannot be empty.")
            self._shake(self.username_entry)
            return
        if not password:
            self._show_error("⚠  Password cannot be empty.")
            self._shake(self.password_entry)
            return

        # Credential check
        if DEFAULT_USERS.get(username) == password:
            self._show_success("✔  Access granted — loading…")
            self.login_btn.configure(state="disabled", text="  Loading…")
            self.after(900, lambda: self._launch_app(username))
        else:
            self._attempts += 1
            remaining = self._max_attempts - self._attempts
            if remaining > 0:
                self._show_error(
                    f"✘  Invalid credentials. {remaining} attempt(s) left."
                )
                self._shake(self.card)
                # Flash entry borders red
                self._flash_error_border()
            else:
                self._lockout()

    def _launch_app(self, username):
        """Destroy login window and invoke the success callback."""
        try:
            self.destroy()
        except Exception:
            pass
        self.on_success(username)

    # ── Lockout after max attempts ────────────────────────────
    def _lockout(self):
        self._locked = True
        self.login_btn.configure(state="disabled", text="  LOCKED", fg_color=ERROR_COLOR)
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self._countdown(30)

    def _countdown(self, seconds):
        if not self.winfo_exists():
            return
        if seconds <= 0:
            self._locked    = False
            self._attempts  = 0
            self.login_btn.configure(
                state="normal", text="  LOGIN  →", fg_color=ACCENT
            )
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self._show_error("")
            return
        self._show_error(f"🔒  Too many attempts. Retry in {seconds}s.")
        self.after(1000, lambda: self._countdown(seconds - 1))

    # ── Visual feedback helpers ───────────────────────────────
    def _show_error(self, msg):
        self.status_label.configure(text=msg, text_color=ERROR_COLOR)

    def _show_success(self, msg):
        self.status_label.configure(text=msg, text_color=SUCCESS_COLOR)

    def _flash_error_border(self):
        """Flash entry borders red then back."""
        def red():
            if not self.winfo_exists(): return
            self.username_entry.configure(border_color=ERROR_COLOR)
            self.password_entry.configure(border_color=ERROR_COLOR)

        def reset():
            if not self.winfo_exists(): return
            self.username_entry.configure(border_color=ENTRY_BORDER)
            self.password_entry.configure(border_color=ENTRY_BORDER)

        red()
        self.after(600, reset)

    def _shake(self, widget, count=6, distance=8):
        """Horizontal shake animation for a widget."""
        original_x = widget.winfo_x()

        def do_shake(c, d):
            if c == 0:
                widget.place_configure(x=original_x) if hasattr(widget, 'place_info') else None
                return
            # Use pack/grid-safe approach via padding trick
            try:
                widget.pack_configure(padx=(d, 0))
            except Exception:
                pass
            self.after(40, lambda: do_shake(c - 1, -d))

        do_shake(count, distance)


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    def on_login(user):
        print(f"[✔] Logged in as: {user}")

    app = LoginWindow(on_success=on_login)
    app.mainloop()
