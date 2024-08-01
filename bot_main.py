from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler, Updater, \
    Application, ContextTypes

# pip install python-telegram-bot
# pip install openai

from gpt import *
from util import *
import random

async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "avatar_bot2")
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "Меню бота 🌍",
        "gpt": "Задать вопрос ChatGPT?) 🧠",
        "date": "Переписка с персонажами 🔥",
        "message": "Предложит что написать в ответ 😈",
        "profile": "Сгенерирует профиль по описанию 😎",
        "opener": "Напишет сообщение для знакомства 🥰",
        "bye": "Пока?...🎀",
        "add": "Добавит вашу задачу на день 📊",
        "show": "Покажет ваши задачи 📩",
        "random": "Добавит рандомную задачу на сегодня 🤡"
    })


tasks = {}

RANDOM_TASKS = ["Солнечные ванны", "Скалолазание", "Бейсбол", "Катание на сноуборде", "Садоводство", "Крикет",
                "Катание на гидроцикле", "Наблюдение за звездами"]


def add_todo(date, task):
    if date in tasks:
        tasks[date].append(task)
    else:
        tasks[date] = []
        tasks[date].append(task)


async def add(update, context):
    command = update.message.text.split(maxsplit=2)
    date = command[1]
    task = command[2]
    add_todo(date, task)
    text = "Задача " + task + " добавлена на дату " + date
    await send_text(update, context, text)


async def show(update, context):
    command = update.message.text.split(maxsplit=1)
    date = command[1]
    text = ""
    if date in tasks:
        text = date + "\n"
        for task in tasks[date]:
            text = text + " ・ " + task + "\n"
    else:
        text = "Задачи на эту дату нет, отдыхайте 😎"
    await send_text(update, context, text)


async def random_add(update, context):
    date = "сегодня"
    task = random.choice(RANDOM_TASKS)
    add_todo(date, task)
    text = "Задача " + task + " добавлена на " + date
    await send_text(update, context, text)


async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)


async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_harry": "Гарри Поттер",
        "date_vader": "Дарт Вейдер",
        "date_hermione": "Гермиона",
        "date_jack": "Джек Воробей"
    })


async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "_набирает сообщение..._")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, "Отлично! Можете общаться)")
    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context,"gpt")
    await send_text_buttons(update, context, text, {
        "message_next": "Следующее сообщение",
        "message_date": "Пригласить на диалог"
    })
    dialog.list.clear()


async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update, context, "_ChatGPT 🧠 думает над ответом..._")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)
    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Ваше имя?")


async def profile_dialog(update, context):
    text = update.message.text
    dialog.count +=1
    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько вам лет?")
    if dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Кем работаете и какое хобби?")
    if dialog.count == 3:
        dialog.user["work"] = text
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)
        my_message = await send_text(update, context, "_ChatGPT 🧠 генерирует сообщение для вашего профиля..._")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = "opener"
    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)
    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Как зовут человека?")


async def opener_dialog(update, context):
    text = update.message.text
    dialog.count += 1
    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько ему лет?")
    if dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Кем работает и какое хобби?")
    if dialog.count == 3:
        dialog.user["work"] = text
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)
        my_message = await send_text(update, context, "_ChatGPT 🧠 думает над ответом..._")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def bye(update, context):
    text = ("Пока! Спасибо за использование бота!")
    txt = ("Еще увидемся! Твой Чарльз 🔥")
    await send_text(update, context, text)
    await send_photo(update, context, "avatar_bot")
    await send_text(update, context, txt)


async def common(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "*Привет!*")
        await send_text_buttons(update, context, "Как у вас дела?", {
            "emote_good": "Хорошо 😆",
            "emote_bad": "Плохо 😶‍🌫️"})


async def emote(update, context):
    query = update.callback_query.data
    if query == "emote_good":
        await send_text(update, context, "Ура! Я рад, отличного вам дня)")
        await send_photo(update, context, "happy")
    elif query == "emote_bad":
        await send_text(update, context, "Печально( Но главное помнить, что все лучшее впереди! Чем я могу помочь?")
        await send_photo(update, context, "sad")


dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}

chatgpt = ChatGptService(token="")

app = ApplicationBuilder().token("").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("show", show))
app.add_handler(CommandHandler("random", random_add))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))
app.add_handler(CommandHandler("bye", bye))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, common))

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(emote))

app.run_polling()
