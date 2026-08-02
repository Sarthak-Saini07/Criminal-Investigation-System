"""
Login View Component for CICMS Desktop Application.
Provides secure authentication and role-based login routing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from database.connection import get_db
from database.queries import GET_USER_BY_USERNAME, UPDATE_LAST_LOGIN
from database.models import UserSession
from utils.helpers import verify_password
from utils.logger import logger

class LoginFrame(ttk.Frame):
    """Tkinter frame for user authentication and RBAC selection."""

    def __init__(self, parent: tk.Tk, on_login_success: Callable[[UserSession], None]):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.db = get_db()
        self._build_ui()

    def _build_ui(self):
        self.pack(fill=tk.BOTH, expand=True)
        
        # Center container
        center_card = ttk.Frame(self, padding=30, style="Card.TFrame")
        center_card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # App Title Header
        lbl_title = ttk.Label(center_card, text="CICMS POLICE SYSTEM", font=("Segoe UI", 18, "bold"), foreground="#38ef7d")
        lbl_title.pack(pady=(0, 5))

        lbl_sub = ttk.Label(center_card, text="Criminal Investigation & Case Management", font=("Segoe UI", 10, "italic"))
        lbl_sub.pack(pady=(0, 20))

        # Username
        ttk.Label(center_card, text="Username:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.ent_username = ttk.Entry(center_card, width=30, font=("Segoe UI", 10))
        self.ent_username.pack(pady=(0, 10))
        self.ent_username.insert(0, "admin")  # Pre-fill for demonstration

        # Password
        ttk.Label(center_card, text="Password:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.ent_password = ttk.Entry(center_card, width=30, show="•", font=("Segoe UI", 10))
        self.ent_password.pack(pady=(0, 20))
        self.ent_password.insert(0, "admin123")  # Pre-fill for demonstration

        # Login Button
        btn_login = ttk.Button(center_card, text="Login to System", command=self.handle_login, style="Accent.TButton")
        btn_login.pack(fill=tk.X, ipady=5)

        # Quick Roles Hint
        lbl_roles = ttk.Label(
            center_card,
            text="Roles: admin | officer | investigator | supervisor | analyst\nPassword: <role>123",
            font=("Segoe UI", 8), foreground="#8a99a8", justify=tk.CENTER
        )
        lbl_roles.pack(pady=(20, 0))

    def handle_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        user_data = self.db.fetch_one(GET_USER_BY_USERNAME, (username,))
        if not user_data:
            messagebox.showerror("Access Denied", "Invalid username or account disabled.")
            return

        if not verify_password(password, user_data["password_hash"]):
            messagebox.showerror("Access Denied", "Incorrect password.")
            return

        # Update Last Login
        self.db.execute_query(UPDATE_LAST_LOGIN, (user_data["user_id"],))

        session = UserSession(
            user_id=user_data["user_id"],
            username=user_data["username"],
            role=user_data["role"],
            officer_id=user_data.get("officer_id"),
            first_name=user_data.get("first_name", "Officer"),
            last_name=user_data.get("last_name", ""),
            rank_title=user_data.get("rank_title", "Inspector")
        )

        logger.info(f"User '{username}' logged in successfully with role '{session.role}'.")
        self.destroy()
        self.on_login_success(session)
