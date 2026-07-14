import os
import sys

# Locate the core python installation (bypasses isolated virtual environments correctly)
base_dir = getattr(sys, 'base_prefix', sys.prefix)
tcl_dir = os.path.join(base_dir, "tcl", "tcl8.6")
tk_dir = os.path.join(base_dir, "tcl", "tk8.6")

if os.path.exists(tcl_dir) and os.path.exists(tk_dir):
    os.environ["TCL_LIBRARY"] = tcl_dir
    os.environ["TK_LIBRARY"] = tk_dir

import customtkinter as ctk
from gui.styles import BG_MAIN, BG_CARD, ACCENT, TEXT_MAIN, TEXT_DIM
from gui.views.setup_view import SetupView
from gui.views.dashboard_view import DashboardView
from gui.views.diet_view import DietView
from gui.views.workout_view import WorkoutView
from gui.views.assistant_view import AssistantView
from gui.views.settings_view import SettingsView

class FitAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FitAI Coach")
        self.geometry("1400x900")
        self.configure(fg_color=BG_MAIN)
        ctk.set_appearance_mode("dark")
        
        # User data will be populated by SetupView
        self.user_data = None
        
        # Center setup initially
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Kill stray background loops cleanly
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start application on Setup mode
        self.setup_view = SetupView(parent=self, controller=self)
        self.setup_view.grid(row=0, column=0, sticky="nsew")

    def finish_setup(self):
        """Transition application state from Setup to Active Dashboard."""
        self.setup_view.destroy()
        
        # Reconfigure base grid for App Layout (Sidebar[0] + Content[1])
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        self._build_sidebar()
        
        self.main_container = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Load views dynamically
        self.views = {}
        for ViewClass in (DashboardView, DietView, WorkoutView, AssistantView, SettingsView):
            view_name = ViewClass.__name__
            view = ViewClass(parent=self.main_container, controller=self)
            self.views[view_name] = view
            view.grid(row=0, column=0, sticky="nsew")
            
        self.show_view("DashboardView", "Home")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color=BG_CARD, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand = ctk.CTkLabel(self.sidebar, text="FitAI Coach", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_MAIN)
        brand.pack(pady=(40, 50))
        
        self.nav_buttons = {}
        nav_items = [
            ("Home", "DashboardView"), 
            ("Diet Plan", "DietView"), 
            ("Workout Plan", "WorkoutView"), 
            ("AI Assistant", "AssistantView"), 
            ("Settings", "SettingsView")
        ]
        
        for name, view_name in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=name, anchor="w", 
                fg_color="transparent", text_color=TEXT_DIM, height=45,
                font=ctk.CTkFont(size=14, weight="normal"),
                hover_color="#334155",
                command=lambda v=view_name, n=name: self.show_view(v, n)
            )
            btn.pack(fill="x", padx=20, pady=5)
            self.nav_buttons[name] = btn
            
        logout = ctk.CTkButton(self.sidebar, text="Logout", anchor="w", fg_color="transparent",
                               text_color="#ef4444", hover_color="#fee2e2", height=45,
                               font=ctk.CTkFont(size=14), command=self.on_closing)
        logout.pack(side="bottom", fill="x", padx=20, pady=40)

    def show_view(self, view_name, tab_name):
        view = self.views[view_name]
        view.tkraise()
        
        ACCENT_SUB = "#0891b2"
        # Reset navigation button styles
        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=ACCENT, text_color="#000", font=ctk.CTkFont(size=14, weight="bold"), hover_color=ACCENT_SUB)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_DIM, font=ctk.CTkFont(size=14, weight="normal"), hover_color="#334155")
        
        if hasattr(view, 'on_show'):
            view.on_show()

    def on_closing(self):
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = FitAIApp()
    app.mainloop()
