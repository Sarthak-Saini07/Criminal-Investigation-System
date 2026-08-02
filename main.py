"""
Main Application Entry Point for CRIMINAL INVESTIGATION AND CASE MANAGEMENT SYSTEM (CICMS).
Python 3.12 Desktop Application with Modern Dark Theme.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ModuleNotFoundError:
    print("\n" + "="*70)
    print(" [ERROR] Tkinter GUI Library is missing on your Linux system.")
    print("="*70)
    print(" To fix this, run the following command in your terminal:\n")
    print("     sudo apt update && sudo apt install -y python3-tk\n")
    print("="*70 + "\n")
    sys.exit(1)

from database.connection import get_db
from database.models import UserSession
from sql.seed_data import seed_database
from ui.login_frame import LoginFrame
from ui.main_window import MainWindow
from utils.logger import logger

def apply_modern_theme(root: tk.Tk):
    """Applies a high-contrast, modern police software theme to Tkinter TTK widgets."""
    style = ttk.Style()
    style.theme_use("clam")

    # Premium Color Palette
    BG_MAIN = "#0f1219"       # Deep Dark Navy
    SURFACE_CARD = "#1f2636"  # Card / Panel Background
    HEADER_BG = "#161b26"     # Header & Sidebar Background
    TEXT_PRIMARY = "#ffffff"  # Crisp White
    TEXT_SECONDARY = "#90a4ae"# Slate Grey
    ACCENT_GREEN = "#00e676"  # Neon Emerald
    ACCENT_BLUE = "#00b0ff"   # Neon Cyan
    BORDER_COLOR = "#2d374d"  # Subtle Border

    root.configure(bg=BG_MAIN)

    # Base Rules
    style.configure(".", background=BG_MAIN, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG_MAIN)
    style.configure("Card.TFrame", background=SURFACE_CARD, relief="flat", borderwidth=1)
    style.configure("Header.TFrame", background=HEADER_BG)
    style.configure("Sidebar.TFrame", background=HEADER_BG)

    # Label Styles
    style.configure("TLabel", background=BG_MAIN, foreground=TEXT_PRIMARY)
    style.configure("Header.TLabel", background=HEADER_BG, foreground=TEXT_PRIMARY)
    style.configure("Card.TLabel", background=SURFACE_CARD, foreground=TEXT_PRIMARY)
    style.configure("Muted.TLabel", background=SURFACE_CARD, foreground=TEXT_SECONDARY, font=("Segoe UI", 9))
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_GREEN)

    # Button Styles
    style.configure("TButton", background="#2a3447", foreground=TEXT_PRIMARY, borderwidth=0, padding=(10, 6), font=("Segoe UI", 9, "bold"))
    style.map("TButton", background=[("active", "#37455d")])

    style.configure("Accent.TButton", background=ACCENT_GREEN, foreground="#000000", font=("Segoe UI", 10, "bold"), padding=(12, 8))
    style.map("Accent.TButton", background=[("active", "#00c853")])

    style.configure("Nav.TButton", background=HEADER_BG, foreground="#b0bec5", anchor="w", font=("Segoe UI", 10), padding=(15, 10))
    style.map("Nav.TButton", background=[("active", "#252d3d")], foreground=[("active", ACCENT_BLUE)])

    style.configure("ActiveNav.TButton", background="#1a2332", foreground=ACCENT_GREEN, anchor="w", font=("Segoe UI", 10, "bold"), padding=(15, 10))

    # Treeview Data Table Styles
    style.configure("Treeview", background="#171c28", foreground="#e0e6ed", fieldbackground="#171c28", rowheight=30, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background="#232b3c", foreground=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"), padding=6)
    style.map("Treeview", background=[("selected", "#00b0ff")], foreground=[("selected", "#ffffff")])

    # Notebook Tabs
    style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
    style.configure("TNotebook.Tab", background="#232b3c", foreground=TEXT_SECONDARY, padding=[16, 8], font=("Segoe UI", 9, "bold"))
    style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)], foreground=[("selected", "#ffffff")])

    # Entry & Combobox
    style.configure("TEntry", fieldbackground="#171c28", foreground="white", insertcolor="white")
    style.configure("TCombobox", fieldbackground="#171c28", foreground="white")

class CICMSApplication:
    """Master Desktop Application Controller."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CICMS - Criminal Investigation & Case Management System")
        self.root.geometry("1400x820")
        self.root.minsize(1100, 680)
        
        apply_modern_theme(self.root)
        
        # Initialize Database Manager
        self.db = get_db()
        try:
            seed_database()
        except Exception as e:
            logger.warning(f"Database seeding check note: {e}")

        self.current_user_session = None
        self.show_login()

    def show_login(self):
        """Displays Login Frame."""
        for child in self.root.winfo_children():
            child.destroy()

        self.login_frame = LoginFrame(self.root, on_login_success=self.on_login_success)

    def on_login_success(self, session: UserSession):
        """Callback on successful login to launch Main Window."""
        self.current_user_session = session
        for child in self.root.winfo_children():
            child.destroy()

        self.main_window = MainWindow(self.root, session=session, on_logout=self.show_login)

    def run(self):
        """Starts desktop application GUI mainloop."""
        self.root.mainloop()

if __name__ == "__main__":
    logger.info("Initializing CICMS Police Desktop Application...")
    app = CICMSApplication()
    app.run()
