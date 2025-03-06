import os
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime
from workout import WorkoutData
from analyst import GymDataAnalyzer
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler

warnings.filterwarnings("ignore")
TOKEN = "7151744103:AAGCb5liKMF6YZHY-vrxcmul4w1GWbZGHzE"

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
                                 BotCommand("wstats", "Returns weight statistics for a specific exercise"),
                                 BotCommand("last", "Returns last reps and weight for the current exercise"),
                                 BotCommand("stop", "Stops the current workout")])

def generate_day_keyboard():
    days = ["Push day", "Pull day", "Leg day"]
    keyboard = [[InlineKeyboardButton(day, callback_data=day)] for day in days]
    return InlineKeyboardMarkup(keyboard)

def generate_reps_keyboard(min_reps, max_reps):
    reps_keyboard = [[InlineKeyboardButton(f"{num}", callback_data=f"{num}") for num in range(min_reps, max_reps + 1)]]
    return InlineKeyboardMarkup(reps_keyboard)

def generate_weight_keyboard():
    weights = np.arange(5.0, 101.0, 2.5)
    weight_buttons = [InlineKeyboardButton(weight, callback_data=weight) for weight in weights]
    weight_keyboard = [weight_buttons[i:i + 5] for i in range(0, len(weight_buttons), 5)]
    return InlineKeyboardMarkup(weight_keyboard)

def last(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == "1955641675":
        global workoutdata
        analyst.load_data()
        try:
            response = analyst.get_last(workoutdata.current_exercise, workoutdata.current_set_number)
            update.message.reply_text(f'<i>{response}</i>', parse_mode=ParseMode.HTML)
        except:
            update.message.reply_text(f'<i>🗡️ Sonuncu dəfə deyilən bir şey yoxdur</i>', parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text('<b>Sən Nağı deyilsən axı! 🤔</b>', parse_mode=ParseMode.HTML)
        update.message.reply_text('<b>Üzürlü say. Giriş qadağandır! 👊</b>', parse_mode=ParseMode.HTML)

def wstats(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == "1955641675":
        analyst.load_data()
        exercise_names = [exercise["exercise"] for day in dict(exercises).values() for exercise in day]
        buttons = [[InlineKeyboardButton(exercise, callback_data=exercise)] for exercise in exercise_names]
        update.message.reply_text("<i>📊 Hansı hərəkətin statistikalarını görmək istəyirsən ?</i>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))

    else:
        update.message.reply_text('<b>Sən Nağı deyilsən axı! 🤔</b>', parse_mode=ParseMode.HTML)
        update.message.reply_text('<b>Üzürlü say. Giriş qadağandır! 👊</b>', parse_mode=ParseMode.HTML)

def get_response(update, context):
    query = update.callback_query
    query.answer()

    with open(analyst.get_weight_stats(query.data), "rb") as img:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=img, caption=f"Sənin zaman içində {query.data} inkişafın 💪")
    query.delete_message()
        
def start(update, context):
    user_id = update.message.from_user.id
    if str(user_id) == "1955641675":
        global workoutdata
        workoutdata = WorkoutData()
        update.message.reply_text('<b>🏋️‍♂️ Yeni bir məşqə xoş gəldin rəis 🏋️‍♂️</b>', parse_mode=ParseMode.HTML)
        update.message.reply_text('<i>Bu gün nə günüdür ?</i>', parse_mode=ParseMode.HTML, reply_markup=generate_day_keyboard())
        return CHOOSING_DAY
    else:
        update.message.reply_text('<b>Sən Nağı deyilsən axı! 🤔</b>', parse_mode=ParseMode.HTML)
        update.message.reply_text('<b>Üzürlü say. Giriş qadağandır! 👊</b>', parse_mode=ParseMode.HTML)

def choose_day(update, context):
    global workoutdata
    query = update.callback_query
    query.answer()
    workoutdata.selected_day = query.data
    workoutdata.date = datetime.now().strftime("%d/%m/%Y")
    workoutdata.selected_exercises = exercises[workoutdata.selected_day]
    query.edit_message_text(f"{workoutdata.selected_day} seçildi. Məşqə başlayırıq 💪")
    return tracking_exercise(update, context)

def tracking_exercise(update, context):
    global workoutdata
    
    if workoutdata.current_index >= len(workoutdata.selected_exercises):
        return stop(update, context)
        
    workoutdata.current_exercise_data = workoutdata.selected_exercises[workoutdata.current_index]
    if workoutdata.current_set_number <= workoutdata.current_exercise_data["sets"]:
        workoutdata.current_exercise = workoutdata.current_exercise_data['exercise']
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"🎯 _Set {workoutdata.current_set_number} \- {workoutdata.current_exercise} {workoutdata.current_exercise_data['min_reps']}/{workoutdata.current_exercise_data['max_reps']}_", parse_mode=ParseMode.MARKDOWN_V2)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Neçə təkrar etdin? 🔄", reply_markup=generate_reps_keyboard(workoutdata.current_exercise_data['min_reps'], workoutdata.current_exercise_data['max_reps']))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Neçə kiloqramla işlədin? 🏋️‍♂️", reply_markup=generate_weight_keyboard())
    else:
        workoutdata.current_index += 1
        workoutdata.current_set_number = 1
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"_🏆Zor\. {workoutdata.current_exercise} bitdi\!_", parse_mode=ParseMode.MARKDOWN_V2)
        return tracking_exercise(update, context)
    return SAVE_DATA

def save_data(update, context):
    global workoutdata
    query = update.callback_query
    query.answer()
    
    if query.data in ['saxla', 'sil']:
        if query.data == 'saxla':
            workoutdata.save()
            query.edit_message_text("Məşq məlumatları saxlanıldı! 📝")
        else:
            workoutdata.data_of_today = pd.DataFrame(columns=["date", "day", "exercise", "set", "weight", "reps"])
            query.edit_message_text("Məşq məlumatları silindi! 🗑️")
        return ConversationHandler.END
    
    try:
        user_input = int(query.data)
        workoutdata.current_reps = user_input
        query.delete_message()

    except ValueError:
        try:
            user_input = float(query.data)
            workoutdata.current_weight = user_input
            query.delete_message()
        except ValueError as e:
            with open(analyst.get_weight_stats(query.data), "rb") as img:
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=img, caption=f"Sənin zaman içində {query.data} inkişafın 💪")
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
    keyboard = [[InlineKeyboardButton("Saxla 🗂️", callback_data='saxla')], [InlineKeyboardButton("Sil 🗑️", callback_data='sil')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bu məşq günü saxlanılsın?", reply_markup=reply_markup)
    return SAVE_DATA

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_DAY: [CallbackQueryHandler(choose_day)],
            TRACKING_EXERCISE: [CallbackQueryHandler(tracking_exercise)],
            SAVE_DATA: [CallbackQueryHandler(save_data)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('last', last))
    dp.add_handler(CommandHandler('wstats', wstats))  
    dp.add_handler(CallbackQueryHandler(get_response))

    set_bot_commands(updater)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()