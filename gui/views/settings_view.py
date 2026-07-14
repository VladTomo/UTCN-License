import customtkinter as ctk
from gui.styles import BG_MAIN, TEXT_MAIN

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.controller = controller
        
        lbl = ctk.CTkLabel(self, text="Settings / Profile View\n(Under Construction)", font=("Helvetica", 24, "bold"), text_color=TEXT_MAIN)
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        
    def on_show(self):
        pass
