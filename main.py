"""
╔══════════════════════════════════════════════════════════╗
║           CYBER TOOL - AI-Powered Security Suite         ║
║                     Entry Point                          ║
╚══════════════════════════════════════════════════════════╝

Features:
  • 🔐 Password Strength Analyser (AI-powered)
  • 📧 Suspicious Email Detector (AI-powered)
  • 📤 Email Sender with Templates
  • 🤖 AI Assistant (Google Gemini)
  • 🎨 Modern Dark GUI (CustomTkinter)

Default Login:
  Username : admin
  Password : admin123

Author : Cyber Tool Project
Version: 1.0.0
"""

import sys
import os

# Ensure Python 3.8+
if sys.version_info < (3, 8):
    print("[ERROR] Python 3.8 or higher is required.")
    sys.exit(1)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def launch_main_app(username: str):
    """Called after successful login — opens the main dashboard."""
    try:
        from modules.app import CyberToolApp
        app = CyberToolApp(username=username)
        app.mainloop()
    except ModuleNotFoundError:
        # Dashboard not built yet — show placeholder
        import customtkinter as ctk
        ctk.set_appearance_mode("dark")
        root = ctk.CTk()
        root.title("Cyber Tool — Dashboard")
        root.geometry("900x600")
        root.configure(fg_color="#0a0f1e")
        ctk.CTkLabel(
            root,
            text=f"✅  Welcome, {username}!\n\nDashboard coming soon…",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#00d4ff",
        ).place(relx=0.5, rely=0.5, anchor="center")
        root.mainloop()


# ── Application entry-point ────────────────────────────────────
if __name__ == "__main__":
    try:
        from modules.login import LoginWindow
        login = LoginWindow(on_success=launch_main_app)
        login.mainloop()
    except ModuleNotFoundError as e:
        print(f"[ERROR] Missing module: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
