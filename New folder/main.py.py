import telebot
import random
import json
from datetime import datetime

TOKEN = '7966345656:AAGrPgocoWcRgDoxaeUvizqicFz4A-5o74o'
bot = telebot.TeleBot(TOKEN)

user_scores = {}
user_games = {}  # Har bir foydalanuvchi o'yin holati

# Eski o'yinlar (qisqartirib)
YORDAM = ["💡 Bugun yangi narsa o'rganing!", "🌟 O'zingizga ishonch bildiring"]
LATIFA = ["👨‍🔬 Fizik latifasi...", "🍕 Pizza latifasi..."]

# YANGI O'YINLAR
def generate_number_game(user_id):
    """Raqam top o'yini"""
    son = random.randint(1, 100)
    user_games[user_id] = {'type': 'number', 'answer': son, 'tries': 0}
    return son

def snake_game(user_id):
    """Ilon o'yini holati"""
    user_games[user_id] = {'type': 'snake', 'grid': [[' ']*10 for _ in range(10)], 'snake': [(5,5)], 'food': (8,8), 'dir': 'right'}
    return draw_snake_grid(user_games[user_id])

def draw_snake_grid(game):
    """Ilon o'yinini chizish"""
    grid = game['grid']
    for x,y in game['snake']:
        grid[y][x] = '🐍'
    grid[game['food'][1]][game['food'][0]] = '🍎'
    return '\n'.join([' '.join(row) for row in grid])

def move_snake(game, direction):
    head = game['snake'][0]
    if direction == 'right': new_head = (head[0]+1, head[1])
    elif direction == 'left': new_head = (head[0]-1, head[1])
    elif direction == 'up': new_head = (head[0], head[1]-1)
    elif direction == 'down': new_head = (head[0], head[1]+1)
    
    game['snake'].insert(0, new_head)
    if new_head == game['food']:
        game['food'] = (random.randint(0,9), random.randint(0,9))
    else:
        game['snake'].pop()
    return draw_snake_grid(game)

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🎮 O'YINLAR")
    btn2 = telebot.types.KeyboardButton("📊 BALLARIM")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 
        "🧠 **MIYYA O\'YINLARI BOTI!**\n\n"
        "🎮 O\'YINLAR | 📊 Ballar tanlang!", 
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎮 O'YINLAR")
def show_games(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("❓ Yordam", callback_data="yordam")
    btn2 = telebot.types.InlineKeyboardButton("😂 Latifa", callback_data="latifa")
    btn3 = telebot.types.InlineKeyboardButton("🔢 Raqam Top", callback_data="number")
    btn4 = telebot.types.InlineKeyboardButton("🐍 Ilon", callback_data="snake")
    btn5 = telebot.types.InlineKeyboardButton("🎯 2048", callback_data="2048")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "🧠 **O\'YIN TANLANG:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    
    if call.data == "number":
        son = generate_number_game(user_id)
        bot.edit_message_text(
            f"🔢 **RAQAM TOP!**\n\n"
            f"1-100 orasida son o'yladim!\n"
            f"❓ Sizning taxminingizni yozing:\n\n"
            f"_/raqam_ deb yozing (masalan: /50)",
            user_id, call.message.message_id)
        
    elif call.data == "snake":
        grid = snake_game(user_id)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("⬅️ Chap", callback_data="snake_left"),
            telebot.types.InlineKeyboardButton("➡️ O'ng", callback_data="snake_right")
        )
        markup.add(
            telebot.types.InlineKeyboardButton("⬆️ Yuqori", callback_data="snake_up"),
            telebot.types.InlineKeyboardButton("⬇️ Past", callback_data="snake_down")
        )
        bot.edit_message_text(f"🐍 **ILON O\'YINI:**\n\n{grid}", 
                             user_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("snake_"):
        direction = call.data.split('_')[1]
        game = user_games[user_id]
        new_grid = move_snake(game, direction)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("⬅️", callback_data="snake_left"),
            telebot.types.InlineKeyboardButton("➡️", callback_data="snake_right")
        )
        markup.add(
            telebot.types.InlineKeyboardButton("⬆️", callback_data="snake_up"),
            telebot.types.InlineKeyboardButton("⬇️", callback_data="snake_down")
        )
        bot.edit_message_text(f"🐍 **ILON:**\n\n{new_grid}", 
                             user_id, call.message.message_id, reply_markup=markup)
        add_score(user_id, 5)
    
    elif call.data == "2048":
        bot.send_message(user_id, 
            "🎯 **2048 O\'YINI!**\n\n"
            "⬅️➡️⬆️⬇️ tugmalarini bosing!\n"
            "(To'liq versiya uchun HTML veb-sayt kerak)")
        add_score(user_id, 10)

# Raqam top javoblari
@bot.message_handler(commands=['raqam'])
def check_number(message):
    user_id = message.chat.id
    if user_id not in user_games or user_games[user_id]['type'] != 'number':
        bot.reply_to(message, "🔢 Avval 'Raqam Top' o\'yinini boshlang!")
        return
    
    game = user_games[user_id]
    try:
        taxmin = int(message.text.split()[1])
        game['tries'] += 1
        
        if taxmin == game['answer']:
            bot.reply_to(message, f"🎉 **TABRIK!** {game['tries']} urinishda topdingiz!\n+50 ball! 🔥")
            add_score(user_id, 50)
            del user_games[user_id]
        elif taxmin < game['answer']:
            bot.reply_to(message, f"📈 **Yuqoriroq!** ({game['tries']} urinish)")
        else:
            bot.reply_to(message, f"📉 **Pastroq!** ({game['tries']} urinish)")
    except:
        bot.reply_to(message, "❓ /raqam 50 formatida yozing!")

def add_score(user_id, ball):
    if user_id not in user_scores: user_scores[user_id] = 0
    user_scores[user_id] += ball

@bot.message_handler(func=lambda m: m.text == "📊 BALLARIM")
def show_score(message):
    score = user_scores.get(message.chat.id, 0)
    bot.reply_to(message, f"🏆 **SIZNING BALLAR:** {score}⭐\n🧠 Miya mushaklarini mustahkamlang!")

if __name__ == '__main__':
    print("🧠 MIYYA BOT ISHLADI! 🚀")
    bot.polling(none_stop=True)