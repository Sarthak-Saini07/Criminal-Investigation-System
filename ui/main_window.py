"""
Main Window View Container for CICMS Desktop Application.
Manages application header, sidebar navigation, view switching, and session management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database.models import UserSession
from ui.fir_view import FIRView
from ui.case_view import CaseView
from ui.suspect_view import SuspectView
from ui.victim_view import VictimView
from ui.witness_view import WitnessView
from ui.evidence_view import EvidenceView
from ui.investigation_view import InvestigationView
from ui.court_view import CourtView
from ui.analytics_view import AnalyticsView
from ui.reports_view import ReportsView
from ui.audit_view import AuditView
from utils.logger import logger

class MainWindow(ttk.Frame):
    """Main Desktop Application Window Layout."""

    def __init__(self, parent: tk.Tk, session: UserSession, on_logout: callable):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.on_logout = on_logout
        self.current_view_frame = None
        self.nav_buttons = {}
        self.pack(fill=tk.BOTH, expand=True)
        self._build_layout()

    def _build_layout(self):
        # 1. Header Bar
        header = ttk.Frame(self, padding=(20, 12), style="Header.TFrame")
        header.pack(fill=tk.X, side=tk.TOP)

        lbl_app = ttk.Label(header, text="🛡️  CICMS POLICE ENTERPRISE", font=("Segoe UI", 16, "bold"), foreground="#00e676", style="Header.TLabel")
        lbl_app.pack(side=tk.LEFT)

        # Clock Ticker
        self.lbl_clock = ttk.Label(header, font=("Consolas", 10), foreground="#00b0ff", style="Header.TLabel")
        self.lbl_clock.pack(side=tk.LEFT, padx=30)
        self._update_clock()

        # User Info Badge
        user_info = f"👤 {self.session.first_name} {self.session.last_name} ({self.session.rank_title})  |  Role: {self.session.role}"
        lbl_user = ttk.Label(header, text=user_info, font=("Segoe UI", 10, "bold"), foreground="#ffffff", style="Header.TLabel")
        lbl_user.pack(side=tk.RIGHT, padx=20)

        btn_logout = ttk.Button(header, text="Log Out", command=self.handle_logout)
        btn_logout.pack(side=tk.RIGHT)

        # 2. Main Body Container (Sidebar + Content Area)
        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar Frame
        sidebar = ttk.Frame(body, padding=(10, 15), width=240, style="Sidebar.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(sidebar, text="MAIN NAVIGATION", font=("Segoe UI", 9, "bold"), foreground="#607d8b", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 12), padx=10)

        nav_items = [
            ("analytics", "📊  Analytics & Insights", self.show_analytics),
            ("firs", "📜  FIR Management", self.show_firs),
            ("cases", "💼  Case Management", self.show_cases),
            ("suspects", "🎯  Suspect Registry", self.show_suspects),
            ("victims", "🩹  Victim Records", self.show_victims),
            ("witnesses", "👁️  Witness Module", self.show_witnesses),
            ("evidence", "📦  Evidence Vault", self.show_evidence),
            ("investigations", "🔬  Investigation Notes", self.show_investigations),
            ("court", "⚖️  Court & Chargesheets", self.show_court),
            ("reports", "📁  Report Center", self.show_reports),
            ("audit", "🔒  Audit & Backups", self.show_audit)
        ]

        for key, label_text, cmd in nav_items:
            btn = ttk.Button(sidebar, text=label_text, command=cmd, style="Nav.TButton")
            btn.pack(fill=tk.X, pady=2, ipady=3)
            self.nav_buttons[key] = btn

        # Right View Content Frame
        self.content_area = ttk.Frame(body, padding=15)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Load default view (Analytics Dashboard)
        self.show_analytics()

    def _update_clock(self):
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.lbl_clock.config(text=f"🕒 {now_str}")
        self.after(1000, self._update_clock)

    def _switch_view(self, active_key: str, view_class):
        """Helper to switch active view inside content frame cleanly."""
        # 1. Destroy ALL existing child widgets in content_area to eliminate stacking!
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # 2. Update active button highlights
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(style="ActiveNav.TButton")
            else:
                btn.configure(style="Nav.TButton")

        # 3. Instantiate new view frame
        self.current_view_frame = view_class(self.content_area, self.session)

    def show_analytics(self):
        self._switch_view("analytics", AnalyticsView)

    def show_firs(self):
        self._switch_view("firs", FIRView)

    def show_cases(self):
        self._switch_view("cases", CaseView)

    def show_suspects(self):
        self._switch_view("suspects", SuspectView)

    def show_victims(self):
        self._switch_view("victims", VictimView)

    def show_witnesses(self):
        self._switch_view("witnesses", WitnessView)

    def show_evidence(self):
        self._switch_view("evidence", EvidenceView)

    def show_investigations(self):
        self._switch_view("investigations", InvestigationView)

    def show_court(self):
        self._switch_view("court", CourtView)

    def show_reports(self):
        self._switch_view("reports", ReportsView)

    def show_audit(self):
        self._switch_view("audit", AuditView)

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of CICMS?"):
            logger.info(f"User '{self.session.username}' logged out.")
            self.destroy()
            self.on_logout()
