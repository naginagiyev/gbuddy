# GBuddy

A personal Telegram bot for tracking gym workouts. GBuddy guides you through your workout session set by set, logs your reps and weight, and provides progress analytics with charts.

## Features 🏋️

- **Workout tracking** — Start a Push, Pull, or Leg day session and log each set interactively via inline keyboards
- **Rest timer** — Automatically waits between sets before prompting the next one
- **Last set recall** — Shows what weight and reps you did for the same exercise and set number in your most recent session
- **Weight progress chart** — Line chart of average weight over time for any exercise (`/wstats`)
- **Spider chart** — Radar chart showing your current muscle group development relative to target maximums (`/spider`)
- **Access control** — Only the configured user ID can interact with the bot

## Commands

| Command   | Description                              |
|-----------|------------------------------------------|
| `/start`  | Start a new workout session              |
| `/stop`   | End the current session and save or discard data |
| `/last`   | Show last logged reps/weight for current set |
| `/wstats` | Show weight progression chart for an exercise |
| `/spider` | Show muscle group development radar chart |

## Analytics 📊

### Weight Progress (`/wstats`)
![Weight Over Time](graphs/chart1.jpg)

### Muscle Development (`/spider`)
![Spider Chart](graphs/chart2.jpg)

## Project Structure

```
GBuddy/
├── main.py          # Telegram bot logic and conversation handlers
├── analyst.py       # Data analysis and chart generation
├── workout.py       # WorkoutData class for session state
├── exercises.json   # Exercise definitions per workout day
├── requirements.txt # Python dependencies
└── .env             # Environment variables
```

## Setup ⚙️

1. **Clone the repository and install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Create a `.env` file:**

```env
TELEGRAM_TOKEN=your_bot_token_here
ALLOWED_USER_ID=your_telegram_user_id_here
CONNECTION_STRING=postgresql://user:password@host:5432/dbname
```

3. **Create the database table.** Workout history is stored in a PostgreSQL table named `gymdata`:

```sql
CREATE TABLE gymdata (
    date TEXT,
    day TEXT,
    exercise TEXT,
    set INTEGER,
    weight DOUBLE PRECISION,
    reps INTEGER
);
```

4. **Run the bot:**

```bash
python main.py
```

## Customizing Exercises 📝

Workout days and exercises are defined in `exercises.json`. Each entry specifies the exercise name, rep range (`min_reps` / `max_reps`), number of sets, and rest time between sets in seconds (`rest_time`). You can add, remove, or rename days and exercises to match your own routine.