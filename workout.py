import os 
import pandas as pd 

class WorkoutData:
    def __init__(self):
        self.selected_day = None
        self.date = None
        self.selected_exercises = None
        self.current_index = 0
        self.current_exercise_data = None
        self.current_exercise = None
        self.current_set_number = 1
        self.current_weight = None
        self.current_reps = None
        self.data = pd.read_pickle(os.path.join(os.getcwd(), "data.pkl"))
        self.data_of_today = pd.DataFrame(columns=["date", "day", "exercise", "set", "weight", "reps"])
        
    def reset(self):
        self.current_weight = None
        self.current_reps = None
        
    def save(self):
        data = pd.concat([self.data, self.data_of_today], axis=0, ignore_index=True)
        data.to_pickle(os.path.join(os.getcwd(), "data.pkl"))