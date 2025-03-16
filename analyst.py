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

        fig.write_image("weightprogress.png")
        return os.path.join(os.getcwd(), "weightprogress.png")