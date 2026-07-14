import customtkinter as ctk
from gui.styles import BG_MAIN, BG_CARD, ACCENT, TEXT_MAIN, TEXT_DIM
from health_app import DietRecommenderAI, WorkoutRecommenderAI, calculate_macros, get_meal_plan


class SetupView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card scales with the window/screen (e.g. wider on 1920x1080, narrower on
        # smaller displays) instead of a fixed pixel width, so it always looks
        # proportionate rather than either stranded in empty space or overflowing.
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(outer, fg_color=BG_CARD, corner_radius=20)
        card.grid(row=0, column=0)

        # Scrollable so every field stays reachable (never clipped) even on
        # shorter screens where the full form wouldn't otherwise fit vertically.
        form_frame = ctk.CTkScrollableFrame(card, fg_color="transparent",
                                            height=460,
                                            scrollbar_button_color=BG_CARD,
                                            scrollbar_button_hover_color="#334155")
        form_frame.grid_columnconfigure((0, 1), weight=1)

        def _resize_card(event):
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            width = max(480, min(680, int(screen_w * 0.34)))
            # Tall enough to show every field without scrolling on large screens
            # (e.g. 1920x1080); shrinks on smaller displays where the scrollable
            # frame's own scrollbar keeps every field reachable.
            height = max(260, min(460, screen_h - 380))
            card.configure(width=width)
            form_frame.configure(height=height)

        outer.bind("<Configure>", _resize_card)

        ctk.CTkLabel(card, text="Personalize Your AI Plan",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=TEXT_MAIN).pack(pady=(32, 6))
        ctk.CTkLabel(card,
                     text="Enter your metrics to generate a custom nutrition & fitness dashboard.",
                     font=ctk.CTkFont(size=13), text_color=TEXT_DIM,
                     wraplength=460).pack(pady=(0, 20))

        form_frame.pack(fill="both", expand=True, padx=40, pady=(0, 16))

        # ── Form variables ────────────────────────────────────────────────────
        self.name_var        = ctk.StringVar(value="")
        self.age_var         = ctk.StringVar(value="")
        self.gender_var      = ctk.StringVar(value="Female")
        self.weight_var      = ctk.StringVar(value="")
        self.height_var      = ctk.StringVar(value="")
        self.disease_var     = ctk.StringVar(value="None")
        self.severity_var    = ctk.StringVar(value="Mild")
        self.exercise_var    = ctk.StringVar(value="")
        self.activity_var    = ctk.StringVar(value="Moderately Active")
        self.goal_var        = ctk.StringVar(value="Maintain Weight")

        # ── Row 0: Name ───────────────────────────────────────────────────────
        self._entry(form_frame, "Name", self.name_var, 0, 0, colspan=2)

        # ── Row 1: Age / Gender ───────────────────────────────────────────────
        self._entry(form_frame, "Age", self.age_var, 1, 0)
        self._dropdown(form_frame, "Gender", ["Male", "Female"],
                       self.gender_var, 1, 1)

        # ── Row 2: Weight / Height ────────────────────────────────────────────
        self._entry(form_frame, "Weight (kg)", self.weight_var, 2, 0)
        self._entry(form_frame, "Height (cm)", self.height_var, 2, 1)

        # ── Row 3: Medical Condition / Severity ───────────────────────────────
        self._dropdown(form_frame, "Medical Condition",
                       ["None", "Hypertension", "Diabetes", "Obesity"],
                       self.disease_var, 3, 0)
        self._dropdown(form_frame, "Severity",
                       ["Mild", "Moderate", "Severe"],
                       self.severity_var, 3, 1)

        # ── Section divider ───────────────────────────────────────────────────
        div_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        div_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 2))
        ctk.CTkFrame(div_frame, fg_color="#334155", height=1).pack(fill="x")
        ctk.CTkLabel(div_frame, text="LIFESTYLE",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(pady=(6, 0))

        # ── Row 5: Weekly Exercise ────────────────────────────────────────────
        self._entry(form_frame, "Weekly Exercise (hrs)", self.exercise_var, 5, 0,
                    colspan=2, placeholder="e.g. 3")

        # ── Row 6: Activity Level ─────────────────────────────────────────────
        acts = ["Sedentary", "Lightly Active", "Moderately Active",
                "Very Active", "Extra Active"]
        self._dropdown(form_frame, "Activity Level", acts,
                       self.activity_var, 6, 0, colspan=2)

        # ── Row 7: Primary Goal ───────────────────────────────────────────────
        self._dropdown(form_frame, "Primary Goal",
                       ["Lose Weight", "Maintain Weight", "Gain Weight"],
                       self.goal_var, 7, 0, colspan=2)

        # ── Generate button ───────────────────────────────────────────────────
        self.error_lbl = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12),
                                      text_color="#ef4444")
        self.error_lbl.pack()

        ctk.CTkButton(
            card, text="Generate My Plan", height=50, corner_radius=12,
            fg_color=ACCENT, hover_color="#0891b2", text_color="#000",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.generate_plan,
        ).pack(fill="x", padx=40, pady=(6, 40))

    # ── Widget helpers ────────────────────────────────────────────────────────

    def _entry(self, parent, label, variable, row, col,
               colspan=1, placeholder=""):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, columnspan=colspan,
                   sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(frame, text=label,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="center", pady=(0, 4))
        entry = ctk.CTkEntry(frame, textvariable=variable, height=40,
                             fg_color="#334155", border_width=0,
                             text_color=TEXT_MAIN, justify="center",
                             placeholder_text=placeholder,
                             placeholder_text_color="#64748b")
        entry.pack(fill="x")

    def _dropdown(self, parent, label, values, variable, row, col, colspan=1):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, columnspan=colspan,
                   sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(frame, text=label,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="center", pady=(0, 4))
        ctk.CTkOptionMenu(frame, values=values, variable=variable,
                          height=40, fg_color="#334155",
                          button_color="#475569", button_hover_color=ACCENT,
                          text_color=TEXT_MAIN).pack(fill="x")

    # ── Plan generation ───────────────────────────────────────────────────────

    _CLINICAL_DEFAULTS = {
        'None':         {'cholesterol': 170.0, 'bp': 115, 'glucose': 85.0},
        'Diabetes':     {'cholesterol': 190.0, 'bp': 125, 'glucose': 160.0},
        'Hypertension': {'cholesterol': 205.0, 'bp': 150, 'glucose': 95.0},
        'Obesity':      {'cholesterol': 215.0, 'bp': 135, 'glucose': 108.0},
    }

    def generate_plan(self):
        self.error_lbl.configure(text="")
        try:
            user_info = {
                "name":            self.name_var.get().strip(),
                "age":             int(self.age_var.get()),
                "gender":          self.gender_var.get(),
                "weight_kg":       float(self.weight_var.get()),
                "height_cm":       float(self.height_var.get()),
                "disease":         self.disease_var.get(),
                "severity":        self.severity_var.get(),
                "weekly_exercise": float(self.exercise_var.get()),
                "activity_level":  self.activity_var.get(),
                "goal":            self.goal_var.get(),
            }
        except ValueError:
            self.error_lbl.configure(
                text="Please fill in all fields with valid numbers.")
            return

        clinical = self._CLINICAL_DEFAULTS.get(
            user_info['disease'], self._CLINICAL_DEFAULTS['None']
        )

        # 2. BMR / TDEE / target calories (Mifflin-St Jeor)
        w, h, a = user_info['weight_kg'], user_info['height_cm'], user_info['age']
        bmi = w / ((h / 100) ** 2)

        if user_info['gender'] == "Male":
            bmr = 88.362 + (13.397 * w) + (4.799 * h) - (5.677 * a)
        else:
            bmr = 447.593 + (9.247 * w) + (3.098 * h) - (4.330 * a)

        activity_multipliers = {
            "Sedentary": 1.2, "Lightly Active": 1.375,
            "Moderately Active": 1.55, "Very Active": 1.725,
            "Extra Active": 1.9,
        }
        tdee = bmr * activity_multipliers.get(user_info['activity_level'], 1.2)

        target_calories = tdee
        if user_info['goal'] == 'Lose Weight':   target_calories -= 500
        elif user_info['goal'] == 'Gain Weight': target_calories += 500
        target_calories = int(target_calories)

        # 3. AI predictions
        diet_model = DietRecommenderAI('diet_recommendations_dataset.csv')
        diet_rec, diet_conf = diet_model.predict_with_confidence(
            age=user_info['age'],
            weight=user_info['weight_kg'],
            height=user_info['height_cm'],
            disease=user_info['disease'],
            gender=user_info['gender'],
            activity_level=user_info['activity_level'],
            severity=user_info['severity'],
            cholesterol=clinical['cholesterol'],
            blood_pressure=clinical['bp'],
            glucose=clinical['glucose'],
            weekly_exercise=user_info['weekly_exercise'],
        )

        workout_model = WorkoutRecommenderAI('workout_dataset.csv')
        workout_intensity, workout_conf = workout_model.predict(
            age=user_info['age'],
            weight=user_info['weight_kg'],
            height=user_info['height_cm'],
            disease=user_info['disease'],
            gender=user_info['gender'],
            activity_level=user_info['activity_level'],
            goal=user_info['goal'],
        )

        # 4. Nutrition
        macros   = calculate_macros(target_calories, diet_type=diet_rec)
        raw_menu = get_meal_plan(diet_rec)
        menu_items = {
            "BREAKFAST": (raw_menu.get("Breakfast", "Healthy Meal"),
                          f"{int(target_calories * 0.25):,} kcal"),
            "LUNCH":     (raw_menu.get("Lunch", "Healthy Meal"),
                          f"{int(target_calories * 0.35):,} kcal"),
            "DINNER":    (raw_menu.get("Dinner", "Healthy Meal"),
                          f"{int(target_calories * 0.30):,} kcal"),
            "SNACK":     (raw_menu.get("Snack", "Healthy Snack"),
                          f"{int(target_calories * 0.10):,} kcal"),
        }

        # 5. Store & transition
        self.controller.user_data = {
            "name":               user_info['name'],
            "bmi":                bmi,
            "target_cals":        target_calories,
            "macros":             macros,
            "menu":               menu_items,
            "raw_info":           user_info,
            "diet_rec":           diet_rec,
            "diet_confidence":    diet_conf,
            "workout_intensity":  workout_intensity,
            "workout_confidence": workout_conf,
        }
        self.controller.finish_setup()