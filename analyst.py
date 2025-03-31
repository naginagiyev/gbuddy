import os
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

class GymDataAnalyzer:
    def __init__(self):
        self.data = None

    def load_data(self):
        self.data = pd.read_pickle(os.path.join(os.getcwd(), "data.pkl"))
        self.data['date'] = pd.to_datetime(self.data['date'], format="%d/%m/%Y")

    def get_last(self, exercise_name, set_number):
        fdata = self.data.loc[(self.data['set'] == int(set_number)) & (self.data['exercise'] == exercise_name)]
        
        if not fdata.empty:
            current_date = datetime.now()
            fdata = fdata.copy()
            fdata['date_diff'] = (fdata['date'] - current_date).abs()
            nearest_row = fdata.loc[fdata['date_diff'].idxmin()].drop('date_diff')
            return f"🔍 Sonuncu dəfə, {exercise_name} hərəkitəndə, set {set_number}-də, {nearest_row['weight']} kiloqramla {nearest_row['reps']} təkrar etdin."
        return "🗡️ Sonuncu dəfə deyilən bir şey yoxdur"

    def get_weight_stats(self, exercise_name):
        fdata = self.data[self.data['exercise'] == exercise_name]
        average_weight_per_date = fdata.groupby('date')['weight'].mean()
        average_weight_dict = {date.strftime('%d/%m/%Y'): round(avg_weight, 2) for date, avg_weight in average_weight_per_date.items()}

        dates = [datetime.strptime(date, '%d/%m/%Y') for date in average_weight_dict.keys()]
        weights = list(average_weight_dict.values())

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers', name='Weight', line=dict(color='#FFD700', width=3),
                                marker=dict(size=10, symbol='circle', line=dict(color='#B8860B', width=2))))

        fig.update_layout(
            title={'text': 'Weight Over Time', 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': dict(size=24)},
            xaxis_title='Date', yaxis_title='Weight', xaxis_tickformat='%d/%m/%Y',
            plot_bgcolor='white', paper_bgcolor='white', font=dict(size=14), showlegend=True,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey', tickangle=-45),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
            margin=dict(l=80, r=80, t=100, b=80)
        )

        fig.write_image("chart.png")
        return os.path.join(os.getcwd(), "chart.png")
    
    def get_spider_chart(self):
        potential = {"Chest": 45, "Back": 75, "Shoulders": 20, "Biceps": 40, "Triceps": 50, "Forearms": 50, "Legs": 70, "Abs": 60}
        current = {"Chest": ["Incline Dumbell Press", "Bench Press", "Peck Deck Machine"],
                   "Back": ["Lat Pulldown", "Seated Row", "Seated Machine Row"],
                   "Shoulders": ["Seated Shoulder Press", "Lateral Raises", "Cable Rear Delt Flyes"],
                   "Biceps": ["Cable Rope Hammer Curl", "Cable Biceps Curl Both Biceps", "Cable Biceps Curl One Bicep"],
                   "Triceps": ["Triceps Pushdowns", "Cable Overhead Triceps Extension"],
                   "Forearms": ["Cable Wrist Curl", "Reverse Biceps Curl"], 
                   "Legs": ["Leg Extension", "Leg Curl", "Calf Raises"],
                   "Abs": ["Cable Crunches"]}
        
        for exercise in current.copy():
            df = self.data[self.data['exercise'].isin(current[exercise])]
            max_date = df['date'].max() 
            df = df[df['date'] == max_date]  
            current[exercise] = round(df['weight'].mean())
        
        categories = list(potential.keys())
        max_vals = list(potential.values())
        current_vals = [current[cat] for cat in categories]

        normalize = True
        scale = 100

        if normalize:
            normalized_current = [current_vals[i]/max_vals[i] * scale for i in range(len(categories))]
            normalized_max = [scale] * len(categories)
            
            plot_current = normalized_current
            plot_max = normalized_max
        else:
            plot_current = current_vals
            plot_max = max_vals

        categories_closed = categories + [categories[0]]
        plot_current_closed = plot_current + [plot_current[0]]
        plot_max_closed = plot_max + [plot_max[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(r=plot_current_closed, theta=categories_closed, fill='toself',
                                    fillcolor='rgba(45, 45, 45, 0.7)', line=dict(color='rgb(255, 165, 0)', width=2), name=''))
        fig.add_trace(go.Scatterpolar(r=plot_max_closed, theta=categories_closed, fill='none',
                                    line=dict(color='rgb(180, 180, 180)', width=1, dash='dot'), name=''))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, scale * 1.1], showticklabels=False, gridcolor='rgba(100, 100, 100, 0.3)', linecolor='rgb(120, 120, 120)',),
                                    angularaxis=dict(gridcolor='rgba(100, 100, 100, 0.3)', linecolor='rgb(120, 120, 120)',), bgcolor='rgb(30, 30, 30)',), showlegend=False,
                                    width=700, height=700, margin=dict(l=80, r=80, t=20, b=80), paper_bgcolor='rgb(20, 20, 20)', font=dict(family="Arial, sans-serif", size=14, color="rgb(220, 220, 220)"))

        fig.write_image("chart.png")
        return os.path.join(os.getcwd(), "chart.png")