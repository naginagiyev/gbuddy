import os
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from workout import WorkoutData
warnings.filterwarnings("ignore")
from analyst import GymDataAnalyzer
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

CHOOSING_DAY, TRACKING_EXERCISE, SAVE_DATA = range(3)

CURRENT_DIR = os.getcwd()
EXERCISES_PATH = os.path.join(CURRENT_DIR, "exercises.json")

with open(EXERCISES_PATH, 'r') as file:
    exercises = json.load(file)

global workoutdata
workoutdata = None

analyst = GymDataAnalyzer()

def set_bot_commands(updater: Updater):
    updater.bot.set_my_commands([BotCommand("start", "Starts a new workout"),
                                 BotCommand("wstats", "Returns weight statistics"),
                                 BotCommand("last", "Returns last reps and weight"),
                                 BotCommand("spider", "Returns muscle development statistics"),
                                 BotCommand("stop", "Stops the current workout")])

def generate_day_keyboard():
    days = ["Push day", "Pull day", "Leg day"]
    keyboard = [[InlineKeyboardButton(day, callback_data=f"day:{day}")] for day in days]
    return InlineKeyboardMarkup(keyboard)

def generate_reps_keyboard(min_reps, max_reps):
    reps_keyboard = [[InlineKeyboardButton(f"{num}", callback_data=f"reps:{num}") for num in range(min_reps, max_reps + 1)]]
    return InlineKeyboardMarkup(reps_keyboard)

def generate_weight_keyboard():
    weights = np.arange(5, 100)
    weight_buttons = [InlineKeyboardButton(str(weight), callback_data=f"weight:{weight}") for weight in weights]
    weight_keyboard = [weight_buttons[i:i + 5] for i in range(0, len(weight_buttons), 5)]
    return InlineKeyboardMarkup(weight_keyboard)

def send_set_prompt(context):
    global workoutdata
    if workoutdata is None or workoutdata.current_exercise_data is None:
        return
    chat_id = context.job.context
    context.bot.send_message(chat_id=chat_id, text=f"🎯 _Set {workoutdata.current_set_number} \- {workoutdata.current_exercise} {workoutdata.current_exercise_data['min_reps']}/{workoutdata.current_exercise_data['max_reps']}_", parse_mode=ParseMode.MARKDOWN_V2)
    context.bot.send_message(chat_id=chat_id, text="🌀 Neçə təkrar etdin?", reply_markup=generate_reps_keyboard(workoutdata.current_exercise_data['min_reps'], workoutdata.current_exercise_data['max_reps']))
    context.bot.send_message(chat_id=chat_id, text="⚖️ Neçə kiloqramla işlədin?", reply_markup=generate_weight_keyboard())

def last(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == ALLOWED_USER_ID:
        global workoutdata
        analyst.load_data()
        try:
            max_reps = workoutdata.current_exercise_data['max_reps'] if workoutdata and workoutdata.current_exercise_data else None
            response = analyst.get_last(workoutdata.current_exercise, workoutdata.current_set_number, max_reps)
            update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2)
        except:
            update.message.reply_text(f'_🗡️ Sonuncu yoxdur_', parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('*Sən Nağı deyilsən axı! 🤔*', parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text('*Üzürlü say. Giriş qadağandır! 👊*', parse_mode=ParseMode.MARKDOWN)
    update.message.delete()

def wstats(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == ALLOWED_USER_ID:
        analyst.load_data()
        exercise_names = [exercise["exercise"] for day in dict(exercises).values() for exercise in day]
        buttons = [[InlineKeyboardButton(exercise, callback_data=f"exercise:{exercise}")] for exercise in exercise_names]
        update.message.reply_text("_📊 Hansı hərəkətin statistikalarını görmək istəyirsən ?_", parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        update.message.reply_text('*Sən Nağı deyilsən axı! 🤔*', parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text('*Üzürlü say. Giriş qadağandır! 👊*', parse_mode=ParseMode.MARKDOWN)
    update.message.delete()

def get_response(update, context):
    query = update.callback_query
    query.answer()
    exercise = query.data.split(':', 1)[1]
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=analyst.get_weight_stats(exercise), caption=exercise)
    query.delete_message()

def spider(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == ALLOWED_USER_ID:
        analyst.load_data()
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=analyst.get_spider_chart())
    else:
        update.message.reply_text('*Sən Nağı deyilsən axı! 🤔*', parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text('*Üzürlü say. Giriş qadağandır! 👊*', parse_mode=ParseMode.MARKDOWN)
    update.message.delete()

def start(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == ALLOWED_USER_ID:
        global workoutdata
        workoutdata = WorkoutData()
        workoutdata.start_time = datetime.now()
        update.message.reply_text('_☀️ Bu gün nə günüdür ?_', parse_mode=ParseMode.MARKDOWN, reply_markup=generate_day_keyboard())
    else:
        update.message.reply_text('*Sən Nağı deyilsən axı! 🤔*', parse_mode=ParseMode.MARKDOWN)
        update.message.reply_text('*Üzürlü say. Giriş qadağandır! 👊*', parse_mode=ParseMode.MARKDOWN)
    update.message.delete()
    return CHOOSING_DAY

def choose_day(update, context):
    global workoutdata
    query = update.callback_query
    query.answer()
    workoutdata.selected_day = query.data.split(':', 1)[1]
    workoutdata.date = datetime.now().strftime("%d/%m/%Y")
    workoutdata.selected_exercises = exercises[workoutdata.selected_day]
    query.edit_message_text(f"🚀 {workoutdata.selected_day} seçildi. Məşqə başlayırıq")
    return tracking_exercise(update, context)

def tracking_exercise(update, context):
    global workoutdata

    if workoutdata.current_index >= len(workoutdata.selected_exercises):
        return stop(update, context)

    workoutdata.current_exercise_data = workoutdata.selected_exercises[workoutdata.current_index]
    if workoutdata.current_set_number <= workoutdata.current_exercise_data["sets"]:
        workoutdata.current_exercise = workoutdata.current_exercise_data['exercise']
        analyst.load_data()
        context.bot.send_message(chat_id=update.effective_chat.id, text=analyst.get_last(workoutdata.current_exercise, workoutdata.current_set_number, workoutdata.current_exercise_data['max_reps']), parse_mode=ParseMode.MARKDOWN_V2)
        workoutdata.pending_job = context.job_queue.run_once(send_set_prompt, workoutdata.current_exercise_data['rest_time'], context=update.effective_chat.id)
        return SAVE_DATA
    else:
        workoutdata.current_index += 1
        workoutdata.current_set_number = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"_🏆{workoutdata.current_index}/{len(workoutdata.selected_exercises)} \- {workoutdata.current_exercise} bitdi\!_", parse_mode=ParseMode.MARKDOWN_V2)
        return tracking_exercise(update, context)

def save_data(update, context):
    global workoutdata
    query = update.callback_query
    query.answer()

    if query.data.startswith('confirm:'):
        choice = query.data.split(':', 1)[1]
        if choice == 'saxla':
            workoutdata.save()
            query.edit_message_text("📝 Məşq məlumatları saxlanıldı!")
        else:
            query.edit_message_text("🗑️ Məşq məlumatları silindi!")
        workoutdata = None
        return ConversationHandler.END

    if query.data.startswith('reps:'):
        workoutdata.current_reps = int(query.data.split(':', 1)[1])
        query.delete_message()
    elif query.data.startswith('weight:'):
        workoutdata.current_weight = float(query.data.split(':', 1)[1])
        query.delete_message()
    else:
        query.delete_message()
        return SAVE_DATA

    if workoutdata.current_reps is not None and workoutdata.current_weight is not None:
        row = [workoutdata.date, workoutdata.selected_day, workoutdata.current_exercise, workoutdata.current_set_number, workoutdata.current_weight, workoutdata.current_reps]
        workoutdata.data_of_today.loc[len(workoutdata.data_of_today)] = row
        workoutdata.current_set_number += 1
        workoutdata.reset()
        return tracking_exercise(update, context)

    return SAVE_DATA

def stop(update, context):
    global workoutdata
    if workoutdata is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="🤔 Hələ başlamamısan")
        if update.message:
            update.message.delete()
        return ConversationHandler.END

    workoutdata.cancel_pending_job()
    if workoutdata.start_time is not None:
        elapsed = datetime.now() - workoutdata.start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"_⏱️ {hours} saat {minutes} dəqiqədə tamamlandı!_", parse_mode=ParseMode.MARKDOWN)
    keyboard = [[InlineKeyboardButton("Saxla 🗂️", callback_data='confirm:saxla')], [InlineKeyboardButton("Sil 🗑️", callback_data='confirm:sil')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bu məşq günü saxlanılsın?", reply_markup=reply_markup)
    if update.message:
        update.message.delete()
    return SAVE_DATA

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_DAY: [CallbackQueryHandler(choose_day, pattern="^day:")],
            TRACKING_EXERCISE: [CallbackQueryHandler(tracking_exercise)],
            SAVE_DATA: [CallbackQueryHandler(save_data, pattern="^(confirm|reps|weight):")]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('last', last))
    dp.add_handler(CommandHandler('wstats', wstats))
    dp.add_handler(CommandHandler('spider', spider))
    dp.add_handler(CallbackQueryHandler(get_response, pattern="^exercise:"))

    set_bot_commands(updater)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("Running...")
    main()