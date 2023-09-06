import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

bot = telebot.TeleBot("6316438528:AAEWGZmtvCJmu86zypSiQCcUDUKjzPN9ozg")


@bot.message_handler(commands=['start'])
def start_message(message, page = 0, previous_message=None):
    if message.chat.id == 566266388:
        notes = requests.get("http://127.0.0.1:8080/notes").json()
        if len(notes) > 0:
            left = page - 1 if page != 0 else page
            right = page + 1 if page != len(notes) - 1 else page

            buttons      = types.InlineKeyboardMarkup()

            left_button  = types.InlineKeyboardButton("←",      callback_data="to " + str(left))
            page_button  = types.InlineKeyboardButton(str(page + 1) + "/" + str(len(notes)), callback_data="None") 
            right_button = types.InlineKeyboardButton("→",      callback_data="to " + str(right))

            problem_text   = types.InlineKeyboardButton("УСЛОВИЕ", url=notes[page].get("url"))
            update_button   = types.InlineKeyboardButton("ИЗМЕНИТЬ", callback_data="update " + str(notes[page].get("id")))
            delete_button   = types.InlineKeyboardButton("УДАЛИТЬ", callback_data="delete " + str(notes[page].get("id")))
            new_note   = types.InlineKeyboardButton("СОЗДАТЬ ЗАМЕТКУ", callback_data="new_note")

            buttons.add(left_button, page_button, right_button)
            buttons.add(problem_text)
            buttons.add(update_button)
            buttons.add(delete_button)
            buttons.add(new_note)


            text = notes[page].get("text")
            if text == "":
                text = "Заметки пока что нет!"
            msg = "Задача: " + notes[page].get("name") + "\n\n" + "Заметка: " + text

            bot.send_message(message.chat.id, msg, reply_markup=buttons)

            try: bot.delete_message(message.chat.id, previous_message.id)
            except: pass
        else:
            buttons = types.InlineKeyboardMarkup()
            new_note   = types.InlineKeyboardButton("СОЗДАТЬ ЗАМЕТКУ", callback_data="new_note")
            buttons.add(new_note)
            bot.send_message(message.chat.id, "Заметок пока что нет.", reply_markup=buttons)
    else:
        bot.send_message(message.chat.id, "У тебя нет доступа!")

@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    if 'to' in c.data: 
        page = int(c.data.split(' ')[1])
        start_message(c.message, page=page, previous_message=c.message)
    elif "delete" in c.data:
        id = c.data.split()[1]
        delRep = requests.delete("http://127.0.0.1:8080/delete/" + str(id))
        mess = bot.send_message(c.message.chat.id, "Заметка удалена!")

        start_message(c.message, page=0, previous_message=None)

    elif "update" in c.data:
        id = c.data.split()[1]
        mess = bot.send_message(c.message.chat.id, "Введите новый текст")
        bot.register_next_step_handler(mess, update_text, id)
    elif c.data == "new_note":
        mess = bot.send_message(c.message.chat.id, "Пришлите ссылку на задачу")
        bot.register_next_step_handler(mess, new_note)

def update_text(message, id):
    note = requests.get("http://127.0.0.1:8080/notes/" + str(id)).json()
    url = "http://127.0.0.1:8080/update/" + str(id)
    headers = {
        'Content-Type': 'application/json',
        'Accept' : '*/*', 
        'Accept-Encoding' : 'gzip, deflate, br', 
        'Connection' : 'keep-alive'
    }
    data = {
        "name": note.get("name"),
        "url": note.get("url"),
        "text": message.text,
    }
    response = requests.put(url, headers=headers, json=data) 
    bot.send_message(message.chat.id, "Заметка изменена!")
    start_message(message, page=0, previous_message=None)

def new_note(message):
    link = message.text + "?locale=ru"
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'lxml')
    name = soup.find("div", class_="title").text[3:]
    bot.send_message(message.chat.id, "Напишите свои мысли сюда")
    bot.register_next_step_handler(message, new_note_text, link, name)

def new_note_text(message, link, name):
    url = "http://127.0.0.1:8080/add"
    headers = {
        'Content-Type': 'application/json',
        'Accept' : '*/*', 
        'Accept-Encoding' : 'gzip, deflate, br', 
        'Connection' : 'keep-alive'
    }
    data = {
        "name": name,
        "url": link,
        "text": message.text,
    }
    response = requests.post(url, headers=headers, json=data) 
    bot.send_message(message.chat.id, "Заметка создана!")
    start_message(message, page=0, previous_message=None)


bot.infinity_polling()