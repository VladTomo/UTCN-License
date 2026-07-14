import customtkinter as ctk
from gui.styles import BG_MAIN, BG_CARD, ACCENT, TEXT_MAIN, TEXT_DIM
from health_app import DIET_INFO

MEAL_SPLITS = [
    ("Breakfast", 0.25),
    ("Lunch",     0.35),
    ("Dinner",    0.30),
    ("Snack",     0.10),
]

MACRO_COLORS = {
    "Protein": "#38bdf8",
    "Fats":    "#f59e0b",
    "Carbs":   "#06b6d4",
}

# Calories per gram for each macro
KCAL_PER_G = {"Protein": 4, "Fats": 9, "Carbs": 4}


class DietView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.controller = controller
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.winfo_children():
            w.destroy()

        data       = self.controller.user_data
        diet_key   = data['diet_rec']
        info       = DIET_INFO.get(diet_key, DIET_INFO['Balanced'])
        color      = info['color']
        confidence = data.get('diet_confidence', 0.0)
        target     = data['target_cals']
        macros     = data['macros']
        menu       = data['menu']

        # ── Top bar ───────────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent", height=60)
        top.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        top.grid_propagate(False)
        ctk.CTkLabel(top, text="Diet Plan",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(top, text=f"Model confidence: {confidence:.0%}",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(side="right")

        # ── Scrollable body ───────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        scroll.grid_columnconfigure((0, 1), weight=1)

        # ── Section 1: Diet type header ───────────────────────────────────────
        self._diet_header(scroll, info, color, row=0)

        # ── Section 2: Macro targets + Calorie split ─────────────────────────
        self._macro_card(scroll, macros, target, color, row=1, col=0)
        self._calorie_split_card(scroll, target, row=1, col=1)

        # ── Section 3: Food guidelines ────────────────────────────────────────
        self._guidelines_card(scroll, info, color, row=2)

        # ── Section 4: Daily meal plan ────────────────────────────────────────
        self._meal_plan_section(scroll, menu, target, color, row=3)

    # ── Builders ──────────────────────────────────────────────────────────────

    def _diet_header(self, parent, info, color, row):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16)
        card.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(inner, text="RECOMMENDED DIET TYPE",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")
        ctk.CTkLabel(inner, text=info['title'],
                     font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=color).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(inner, text=info['description'],
                     font=ctk.CTkFont(size=13), text_color=TEXT_DIM,
                     wraplength=900, justify="left").pack(anchor="w", pady=(8, 0))

        rationale_box = ctk.CTkFrame(inner, fg_color="#1e3a47", corner_radius=10)
        rationale_box.pack(fill="x", pady=(14, 0))
        ctk.CTkLabel(rationale_box,
                     text=f"Why this diet?  {info['rationale']}",
                     font=ctk.CTkFont(size=12), text_color="#7dd3fc",
                     wraplength=880, justify="left").pack(padx=16, pady=12)

    def _macro_card(self, parent, macros, target, color, row, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(inner, text="DAILY MACRO TARGETS",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w", pady=(0, 12))

        total_macro_kcal = sum(macros[m] * KCAL_PER_G[m] for m in macros)

        for macro, grams in macros.items():
            kcal_contribution = grams * KCAL_PER_G[macro]
            pct = kcal_contribution / target if target > 0 else 0
            bar_color = MACRO_COLORS.get(macro, ACCENT)

            row_frame = ctk.CTkFrame(inner, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)

            header = ctk.CTkFrame(row_frame, fg_color="transparent")
            header.pack(fill="x")
            ctk.CTkLabel(header, text=macro,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_MAIN).pack(side="left")
            ctk.CTkLabel(header, text=f"{grams} g  ({pct:.0%} of calories)",
                         font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(side="right")

            bar = ctk.CTkProgressBar(row_frame, height=8,
                                     progress_color=bar_color,
                                     fg_color="#334155", corner_radius=4)
            bar.pack(fill="x", pady=(4, 0))
            bar.set(min(pct, 1.0))

        ctk.CTkFrame(inner, fg_color="#334155", height=1).pack(fill="x", pady=(16, 8))
        ctk.CTkLabel(inner, text=f"Total daily target: {target:,} kcal",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_MAIN).pack(anchor="w")

    def _calorie_split_card(self, parent, target, row, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(inner, text="CALORIE SPLIT BY MEAL",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w", pady=(0, 12))

        meal_colors = ["#06b6d4", "#38bdf8", "#0ea5e9", "#7dd3fc"]

        for (meal_name, pct), bar_color in zip(MEAL_SPLITS, meal_colors):
            kcal = int(target * pct)

            row_frame = ctk.CTkFrame(inner, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)

            header = ctk.CTkFrame(row_frame, fg_color="transparent")
            header.pack(fill="x")
            ctk.CTkLabel(header, text=meal_name,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_MAIN).pack(side="left")
            ctk.CTkLabel(header, text=f"{kcal:,} kcal  ({pct:.0%})",
                         font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(side="right")

            bar = ctk.CTkProgressBar(row_frame, height=8,
                                     progress_color=bar_color,
                                     fg_color="#334155", corner_radius=4)
            bar.pack(fill="x", pady=(4, 0))
            bar.set(pct)

        ctk.CTkFrame(inner, fg_color="#334155", height=1).pack(fill="x", pady=(16, 8))
        ctk.CTkLabel(inner, text=f"Total: {target:,} kcal / day",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_MAIN).pack(anchor="w")

    def _guidelines_card(self, parent, info, color, row):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16)
        card.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(inner, text="FOOD GUIDELINES",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w", pady=(0, 14))

        columns = ctk.CTkFrame(inner, fg_color="transparent")
        columns.pack(fill="x")
        columns.grid_columnconfigure((0, 1, 2), weight=1)

        # Eat column
        eat_col = ctk.CTkFrame(columns, fg_color="#14532d", corner_radius=12)
        eat_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(eat_col, text="FOODS TO EAT",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#4ade80").pack(anchor="w", padx=14, pady=(14, 8))
        for item in info['eat']:
            ctk.CTkLabel(eat_col, text=f"+ {item}",
                         font=ctk.CTkFont(size=12), text_color=TEXT_MAIN,
                         wraplength=280, justify="left").pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(eat_col, fg_color="transparent", height=14).pack()

        # Avoid column
        avoid_col = ctk.CTkFrame(columns, fg_color="#450a0a", corner_radius=12)
        avoid_col.grid(row=0, column=1, sticky="nsew", padx=8)
        ctk.CTkLabel(avoid_col, text="FOODS TO AVOID",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#f87171").pack(anchor="w", padx=14, pady=(14, 8))
        for item in info['avoid']:
            ctk.CTkLabel(avoid_col, text=f"- {item}",
                         font=ctk.CTkFont(size=12), text_color=TEXT_MAIN,
                         wraplength=280, justify="left").pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(avoid_col, fg_color="transparent", height=14).pack()

        # Tips column
        tips_col = ctk.CTkFrame(columns, fg_color="#1e1b4b", corner_radius=12)
        tips_col.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(tips_col, text="TIPS & HABITS",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#a5b4fc").pack(anchor="w", padx=14, pady=(14, 8))
        for item in info['tips']:
            ctk.CTkLabel(tips_col, text=f"* {item}",
                         font=ctk.CTkFont(size=12), text_color=TEXT_MAIN,
                         wraplength=280, justify="left").pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(tips_col, fg_color="transparent", height=14).pack()

    def _meal_plan_section(self, parent, menu, target, color, row):
        ctk.CTkLabel(parent, text="DAILY MEAL PLAN",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_MAIN).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 6))

        meal_grid = ctk.CTkFrame(parent, fg_color="transparent")
        meal_grid.grid(row=row + 1, column=0, columnspan=2,
                       sticky="nsew", padx=5, pady=(0, 20))
        meal_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        meal_items = list(menu.items())

        for i, (meal_key, (desc, kcal_str)) in enumerate(meal_items):
            card = ctk.CTkFrame(meal_grid, fg_color=BG_CARD, corner_radius=14)
            card.grid(row=0, column=i, sticky="nsew", padx=8, pady=8)

            accent = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2)
            accent.pack(fill="x", padx=12, pady=(12, 0))

            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="both", expand=True, padx=16, pady=12)

            ctk.CTkLabel(body, text=meal_key,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_DIM).pack(anchor="w")
            ctk.CTkLabel(body, text=desc,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_MAIN, wraplength=200,
                         justify="left").pack(anchor="w", pady=(4, 0))

            ctk.CTkFrame(body, fg_color="transparent", height=8).pack()

            kcal_frame = ctk.CTkFrame(body, fg_color="#334155", corner_radius=8)
            kcal_frame.pack(anchor="w")
            ctk.CTkLabel(kcal_frame, text=kcal_str,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).pack(padx=10, pady=6)