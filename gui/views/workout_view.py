import customtkinter as ctk
from gui.styles import BG_MAIN, BG_CARD, ACCENT, TEXT_MAIN, TEXT_DIM
from health_app import WORKOUT_PLANS

INTENSITY_COLORS = {
    "Light":    "#22c55e",
    "Moderate": "#f59e0b",
    "Intense":  "#ef4444",
}


class WorkoutView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.controller = controller

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.winfo_children():
            w.destroy()

        data      = self.controller.user_data
        intensity = data.get('workout_intensity', 'Moderate')
        confidence = data.get('workout_confidence', 0.0)
        plan      = WORKOUT_PLANS.get(intensity, WORKOUT_PLANS['Moderate'])
        color     = INTENSITY_COLORS.get(intensity, ACCENT)

        # ── Top bar ──────────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent", height=60)
        top.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        top.grid_propagate(False)

        ctk.CTkLabel(top, text="Workout Plan",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left")

        conf_lbl = ctk.CTkLabel(
            top,
            text=f"Model confidence: {confidence:.0%}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
        )
        conf_lbl.pack(side="right")

        # ── Scrollable content ────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        scroll.grid_columnconfigure((0, 1), weight=1)

        # ── Intensity badge card ──────────────────────────────────────────────
        badge_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=16)
        badge_card.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        inner = ctk.CTkFrame(badge_card, fg_color="transparent")
        inner.pack(pady=25, padx=30, fill="x")

        ctk.CTkLabel(inner, text="RECOMMENDED INTENSITY",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")

        ctk.CTkLabel(inner, text=plan['label'],
                     font=ctk.CTkFont(size=32, weight="bold"),
                     text_color=color).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(inner, text=plan['description'],
                     font=ctk.CTkFont(size=13),
                     text_color=TEXT_DIM).pack(anchor="w", pady=(6, 0))

        # ── Stats row ─────────────────────────────────────────────────────────
        stats_frame = ctk.CTkFrame(inner, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(16, 0))

        for label, value in [("Duration", plan['duration']),
                              ("Frequency", plan['frequency'])]:
            box = ctk.CTkFrame(stats_frame, fg_color="#334155", corner_radius=10)
            box.pack(side="left", padx=(0, 12), pady=0, ipadx=16, ipady=8)
            ctk.CTkLabel(box, text=label,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_DIM).pack()
            ctk.CTkLabel(box, text=value,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_MAIN).pack()

        # ── Exercise cards ────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="EXERCISES",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_MAIN).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 6))

        for i, (name, detail) in enumerate(plan['exercises']):
            col = i % 2
            row = 2 + i // 2

            card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=14)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=8)

            accent_bar = ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=2)
            accent_bar.pack(side="left", fill="y", padx=(12, 0), pady=16)

            text_box = ctk.CTkFrame(card, fg_color="transparent")
            text_box.pack(side="left", fill="both", expand=True, padx=14, pady=16)

            ctk.CTkLabel(text_box, text=name,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_MAIN, anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_box, text=detail,
                         font=ctk.CTkFont(size=12),
                         text_color=TEXT_DIM, anchor="w",
                         wraplength=260, justify="left").pack(anchor="w", pady=(4, 0))