import os
import pandas as pd
from sqlalchemy import create_engine

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
        self.start_time = None
        self.pending_job = None
        self.engine = create_engine(os.getenv("CONNECTION_STRING"))
        self.data = pd.read_sql("SELECT * FROM gymdata", self.engine)
        self.data_of_today = pd.DataFrame(columns=["date", "day", "exercise", "set", "weight", "reps"])

    def reset(self):
        self.current_weight = None
        self.current_reps = None

    def cancel_pending_job(self):
        if self.pending_job is not None:
            try:
                self.pending_job.schedule_removal()
            except Exception:
                pass
            self.pending_job = None

    def save(self):
        self.data_of_today.to_sql("gymdata", self.engine, if_exists="append", index=False)