import customtkinter as ctk
from datetime import datetime
from gui.styles import BG_MAIN, BG_CARD, ACCENT, TEXT_MAIN, TEXT_DIM
from gui.components.charts import MockupBMIGauge, MockupDonutChart

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_MAIN, corner_radius=0)
        self.controller = controller
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def on_show(self):
        # Refresh logic, clear and rebuild to keep it strictly aligned with mock data
        for w in self.winfo_children():
            w.destroy()
            
        data = self.controller.user_data
        
        # TOP BAR
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        top_bar.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        top_bar.grid_propagate(False)
        
        welcome_lbl = ctk.CTkLabel(top_bar, text=f"Welcome back, {data['name']}!", font=ctk.CTkFont(size=26, weight="bold"), text_color=TEXT_MAIN)
        welcome_lbl.pack(side="left")
        
        date_str = datetime.now().strftime("%d %B, %A")
        date_lbl = ctk.CTkLabel(top_bar, text=date_str, font=ctk.CTkFont(size=14), text_color=TEXT_DIM)
        date_lbl.pack(side="right")
        
        # DASHBOARD CONTENT CONTAINER
        dashboard_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        dashboard_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        dashboard_frame.grid_columnconfigure((0, 1), weight=1)
        
        # --- AI RECOMMENDATION CARD ---
        rec_card = ctk.CTkFrame(dashboard_frame, fg_color=BG_CARD, corner_radius=16)
        rec_card.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        rec_inner = ctk.CTkFrame(rec_card, fg_color="transparent")
        rec_inner.pack(fill="x", padx=24, pady=18)

        ctk.CTkLabel(rec_inner, text="AI RECOMMENDATIONS",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DIM).pack(anchor="w")

        pills = ctk.CTkFrame(rec_inner, fg_color="transparent")
        pills.pack(anchor="w", pady=(10, 0), fill="x")

        # Diet pill
        diet_pill = ctk.CTkFrame(pills, fg_color="#164e63", corner_radius=10)
        diet_pill.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(diet_pill, text="DIET",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#67e8f9").pack(side="left", padx=(12, 6), pady=10)
        diet_conf = data.get('diet_confidence', 0.0)
        ctk.CTkLabel(diet_pill,
                     text=f"{data['diet_rec'].replace('_', ' ')}  {diet_conf:.0%}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left", padx=(0, 12), pady=10)

        # Workout pill
        workout_intensity = data.get('workout_intensity', 'N/A')
        workout_conf      = data.get('workout_confidence', 0.0)
        INTENSITY_COLORS  = {"Light": "#16a34a", "Moderate": "#d97706", "Intense": "#dc2626"}
        w_bg  = {"Light": "#14532d", "Moderate": "#451a03", "Intense": "#450a0a"}.get(workout_intensity, "#1e293b")
        w_col = INTENSITY_COLORS.get(workout_intensity, ACCENT)

        workout_pill = ctk.CTkFrame(pills, fg_color=w_bg, corner_radius=10)
        workout_pill.pack(side="left")
        ctk.CTkLabel(workout_pill, text="WORKOUT",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=w_col).pack(side="left", padx=(12, 6), pady=10)
        ctk.CTkLabel(workout_pill,
                     text=f"{workout_intensity}  {workout_conf:.0%}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_MAIN).pack(side="left", padx=(0, 12), pady=10)

        # --- GAUGES ---
        bmi_card = ctk.CTkFrame(dashboard_frame, fg_color=BG_CARD, corner_radius=16)
        bmi_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(bmi_card, text="BODY MASS INDEX (BMI)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MAIN).pack(anchor="w", padx=20, pady=(20, 0))
        MockupBMIGauge(bmi_card, data['bmi'], height=260).pack(fill="both", expand=True, padx=20, pady=(0, 20))

        macro_card = ctk.CTkFrame(dashboard_frame, fg_color=BG_CARD, corner_radius=16)
        macro_card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(macro_card, text="MACRONUTRIENT BREAKDOWN", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MAIN).pack(anchor="w", padx=20, pady=(20, 0))
        MockupDonutChart(macro_card, data['macros'], height=260).pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # --- CALORIE BAR ---
        cal_card = ctk.CTkFrame(dashboard_frame, fg_color=BG_CARD, corner_radius=16)
        cal_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(10, 20))
        ctk.CTkLabel(cal_card, text="CALORIE TARGET", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(15, 0))
        
        goal = data['target_cals']
        bot = ctk.CTkFrame(cal_card, fg_color="transparent")
        bot.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(bot, text=f"GOAL: {goal:,} kcal", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        
        prog_frame = ctk.CTkFrame(bot, fg_color="transparent")
        prog_frame.pack(side="right", fill="x", expand=True, padx=(40, 0))
        
        cns_fr = ctk.CTkFrame(prog_frame, fg_color="transparent")
        cns_fr.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(cns_fr, text="0 Kcal Consumed", font=ctk.CTkFont(size=11), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(cns_fr, text="0%", font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(side="right")
        
        pbar = ctk.CTkProgressBar(prog_frame, height=6, progress_color=ACCENT, fg_color="#334155", corner_radius=3)
        pbar.pack(fill="x")
        pbar.set(0.0)

        # --- MEAL PLAN CARDS ---
        meal_header = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        meal_header.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(20, 5))
        ctk.CTkLabel(meal_header, text="MEAL PLAN", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MAIN).pack()

        meal_grid = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        meal_grid.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5)
        meal_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        menu_items = list(data['menu'].items())
        
        for i in range(4):
            mc = ctk.CTkFrame(meal_grid, fg_color=BG_CARD, corner_radius=16)
            mc.grid(row=0, column=i, sticky="nsew", padx=8, pady=10)
            
            img_ph = ctk.CTkFrame(mc, height=120, fg_color="#334155", corner_radius=12)
            img_ph.pack(fill="x", padx=10, pady=10)
            img_ph.pack_propagate(False)
            ctk.CTkLabel(img_ph, text="📷 Image", text_color="#64748b").place(relx=0.5, rely=0.5, anchor="center")
            
            title, details = menu_items[i]
            desc, kcal = details
            
            body = ctk.CTkFrame(mc, fg_color="transparent")
            body.pack(fill="both", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(body, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(body, text=desc, font=ctk.CTkFont(size=11), text_color=TEXT_DIM, wraplength=180, justify="left").pack(anchor="w", pady=(5, 10))
            
            spacer = ctk.CTkFrame(body, fg_color="transparent", height=10)
            spacer.pack(fill="both", expand=True)
            
            cbot = ctk.CTkFrame(body, fg_color="transparent")
            cbot.pack(fill="x")
            
            ctk.CTkLabel(cbot, text=kcal, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_DIM).pack(side="left", pady=(0, 5))
            act_btn = ctk.CTkButton(cbot, text="📋", width=30, height=30, fg_color=ACCENT, hover_color="#0891b2", text_color="#000", corner_radius=8)
            act_btn.pack(side="right", pady=(0, 5))
