import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from gui.styles import BG_CARD, ACCENT, TEXT_MAIN, TEXT_DIM

class MockupBMIGauge(ctk.CTkFrame):
    def __init__(self, parent, bmi, **kwargs):
        super().__init__(parent, fg_color=BG_CARD, **kwargs)
        self.bmi = bmi
        self._create_plot()

    def _create_plot(self):
        # Increased figsize dramatically to make the gauge larger
        fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={"projection": "polar"})
        fig.patch.set_facecolor(BG_CARD)
        ax.set_facecolor(BG_CARD)

        theta_bg = np.linspace(np.radians(-30), np.radians(210), 100)
        ax.plot(theta_bg, np.ones_like(theta_bg), color="#334155", linewidth=24, solid_capstyle="butt")
        
        bmi_clamped = min(max(self.bmi, 15), 35)
        target_deg = 210 - ((bmi_clamped - 15) / 20) * 240
        theta_prog = np.linspace(np.radians(target_deg), np.radians(210), 100)
        
        ax.plot(theta_prog, np.ones_like(theta_prog), color=ACCENT, linewidth=24, solid_capstyle="butt")
        
        # Indicator circle marker
        ax.plot(np.radians(target_deg), 0.86, marker="o", color=ACCENT, markersize=10)

        # Reduced ylim slightly to zoom in the curve more, maximizing space
        ax.set_ylim(0, 1.35)
        ax.set_axis_off()
        # Tight margins to maximize use of the figure space
        fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)

        # Draw texts
        ax.text(np.pi/2, 0.15, f"{self.bmi:.1f}", ha="center", va="center", fontsize=36, fontweight="bold", color=TEXT_MAIN)
        
        status_text = "Healthy Weight" if 18.5 <= self.bmi < 25 else "Underweight" if self.bmi < 18.5 else "Overweight"
        ax.text(3 * np.pi / 2, 0.35, status_text, ha="center", va="center", fontsize=13, color=ACCENT)

        ax.text(np.radians(210), 1.25, "15", ha="right", va="center", fontsize=11, color=TEXT_DIM)
        ax.text(np.radians(-30), 1.25, "35", ha="left", va="center", fontsize=11, color=TEXT_DIM)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

class MockupDonutChart(ctk.CTkFrame):
    def __init__(self, parent, macros, **kwargs):
        super().__init__(parent, fg_color=BG_CARD, **kwargs)
        self.macros = macros
        self._create_plot()

    def _create_plot(self):
        fig, ax = plt.subplots(figsize=(4, 2.5))
        fig.patch.set_facecolor(BG_CARD)
        ax.set_facecolor(BG_CARD)

        values = [self.macros["Carbs"], self.macros["Protein"], self.macros["Fats"]]
        labels = ["Carbs", "Protein", "Fats"]
        colors = [ACCENT, "#38bdf8", "#0ea5e9"]
        total = sum(values)

        if total > 0:
            wedges, texts = ax.pie(
                values, 
                colors=colors,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.3, edgecolor=BG_CARD, linewidth=4)
            )
            
            # Manually position stacked text for alignment
            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1)/2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                
                r_text = 1.45
                tx = r_text * x
                ty = r_text * y
                pct = int(round(values[i] / total * 100))
                
                ax.text(tx, ty + 0.10, labels[i], ha="center", va="center", fontsize=11, color=TEXT_DIM)
                ax.text(tx, ty - 0.10, f"{pct}%", ha="center", va="center", fontsize=12, fontweight="bold", color=colors[i])

        ax.text(0, 0.1, "DAILY", ha="center", va="center", fontsize=11, fontweight="bold", color=TEXT_MAIN)
        ax.text(0, -0.15, "MACROS", ha="center", va="center", fontsize=11, fontweight="bold", color=TEXT_MAIN)

        fig.subplots_adjust(left=0.15, right=0.85, top=0.9, bottom=0.1)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
