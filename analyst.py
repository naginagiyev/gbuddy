import os
import matplotlib
import numpy as np
import pandas as pd
matplotlib.use("Agg")
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

class GymDataAnalyzer:
    def __init__(self):
        self.data = None

    def _figToImageBuffer(self, fig):
        buffer = BytesIO()
        fig.savefig(buffer, format="jpeg", facecolor=fig.get_facecolor())
        plt.close(fig)
        buffer.seek(0)
        buffer.name = "chart.jpg"
        return buffer

    def load_data(self):
        engine = create_engine(os.getenv("CONNECTION_STRING"))
        self.data = pd.read_sql("SELECT * FROM gymdata", engine)
        self.data['date'] = pd.to_datetime(self.data['date'], format="%d/%m/%Y")

    def get_last(self, exercise_name, set_number, max_reps=None):
        fdata = self.data.loc[(self.data['set'] == int(set_number)) & (self.data['exercise'] == exercise_name)]

        if not fdata.empty:
            current_date = datetime.now()
            fdata = fdata.copy()
            fdata['date_diff'] = (fdata['date'] - current_date).abs()
            nearest_row = fdata.loc[fdata['date_diff'].idxmin()].drop('date_diff')
            weight = str(nearest_row['weight']).replace('.', '\\.')
            reps = str(nearest_row['reps']).replace('.', '\\.')
            if max_reps is not None:
                max_reps_str = str(max_reps).replace('.', '\\.')
                reps = f"{reps}/{max_reps_str}"
            return f"_🔍 *{weight}* kiloqramla *{reps}* təkrar etmişdin\\._"
        return "🗡️ Sonuncu yoxdur"

    def get_weight_stats(self, exercise_name):
        fdata = self.data[self.data['exercise'] == exercise_name]
        average_weight_per_date = fdata.groupby('date')['weight'].mean()
        average_weight_dict = {date.strftime('%d/%m/%Y'): round(avg_weight, 2) for date, avg_weight in average_weight_per_date.items()}

        date_labels = list(average_weight_dict.keys())
        weights = list(average_weight_dict.values())
        positions = list(range(len(date_labels)))

        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        ax.plot(positions, weights, linestyle='-', linewidth=3, color='#E19200',
                marker='o', markersize=10, markerfacecolor='#E19200',
                markeredgecolor='#E19200', markeredgewidth=2, label='Weight')

        ax.set_title('Weight Over Time', fontsize=24, pad=20)
        ax.set_xlabel('Date', fontsize=14)
        ax.set_ylabel('Weight', fontsize=14)
        ax.set_xticks(positions)
        ax.set_xticklabels(date_labels)
        plt.setp(ax.get_xticklabels(), rotation=-45, ha='left', fontsize=14)
        plt.setp(ax.get_yticklabels(), fontsize=14)
        ax.grid(True, color='LightGrey', linewidth=1)
        ax.legend(fontsize=14)

        fig.tight_layout()

        return self._figToImageBuffer(fig)

    def get_spider_chart(self):
        exercise_max = {
            "Incline Dumbbell Press": 35, "Dumbbell Bench Press": 35, "Peck Deck Machine": 75,
            "Lat Pulldown": 75, "Seated Row": 75, "Seated Machine Row": 80,
            "Seated Shoulder Press": 25, "Lateral Raises": 15, "Cable Rear Delt Fly": 15,
            "Cable Rope Hammer Curl": 40, "Cable Biceps Curl Both Biceps": 40, "Cable Biceps Curl One Bicep": 20,
            "Triceps Pushdowns": 50, "Cable Overhead Triceps Extension": 40,
            "Cable Wrist Curl": 50, "Reverse Biceps Curl": 40,
            "Leg Extension": 95, "Leg Curl": 60, "Calf Raises": 120,
            "Cable Crunches": 75,
        }
        categories_exercises = {
            "Chest": ["Incline Dumbbell Press", "Dumbbell Bench Press", "Peck Deck Machine"],
            "Back": ["Lat Pulldown", "Seated Row", "Seated Machine Row"],
            "Shoulders": ["Seated Shoulder Press", "Lateral Raises", "Cable Rear Delt Fly"],
            "Biceps": ["Cable Rope Hammer Curl", "Cable Biceps Curl Both Biceps", "Cable Biceps Curl One Bicep"],
            "Triceps": ["Triceps Pushdowns", "Cable Overhead Triceps Extension"],
            "Forearms": ["Cable Wrist Curl", "Reverse Biceps Curl"],
            "Legs": ["Leg Extension", "Leg Curl", "Calf Raises"],
            "Abs": ["Cable Crunches"],
        }

        current = {}
        for category, exercises in categories_exercises.items():
            scores = []
            for exercise in exercises:
                df = self.data[self.data['exercise'] == exercise]
                if df.empty:
                    continue
                latest_date = df['date'].max()
                weight = df[df['date'] == latest_date]['weight'].mean()
                scores.append(weight / exercise_max[exercise] * 100)
            current[category] = sum(scores) / len(scores) if scores else 0

        categories = list(categories_exercises.keys())
        scale = 100
        plot_current = [current[cat] for cat in categories]
        plot_max = [scale] * len(categories)

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        plot_current_closed = plot_current + [plot_current[0]]
        plot_max_closed = plot_max + [plot_max[0]]

        fig = plt.figure(figsize=(7, 7), dpi=100)
        fig.patch.set_facecolor('#141414')
        ax = fig.add_subplot(111, polar=True)
        ax.set_facecolor('#1e1e1e')

        ax.fill(angles, plot_current_closed, color=(45 / 255, 45 / 255, 45 / 255, 0.7))
        ax.plot(angles, plot_current_closed, color='#FFA500', linewidth=2)
        ax.plot(angles, plot_max_closed, color='#B4B4B4', linewidth=1, linestyle='dotted')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color='#DCDCDC', fontsize=14, fontfamily='sans-serif')
        ax.set_yticklabels([])
        ax.set_ylim(0, scale * 1.1)
        ax.grid(color=(100 / 255, 100 / 255, 100 / 255, 0.3))
        ax.spines['polar'].set_color((120 / 255, 120 / 255, 120 / 255))

        fig.tight_layout()

        return self._figToImageBuffer(fig)