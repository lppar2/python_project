import json
import requests
import time
import urllib

from random import randint

from todohelp import DBHelper, PurchaseHelper


db = DBHelper()
pb = PurchaseHelper()

TOKEN = "5408578112:AAGOm3TXRAfV40XTt32hkT_NYiBA-dXMthI"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)
        purchases = pb.get_items(chat)

        if text == "/done":
            keyboard = build_keyboard(items)
            send_message("Выбери что нужно удалить", chat, keyboard)

        elif text == "/start":
            send_message(
                "Привет💚 Я помогу тебе запомнить все твои дела 🐹"
                "\n\nЧтобы добавить новую задачу, просто напиши мне любое сообщение"
                "\n\nЧтобы пополнить список покупок напиши '/buy <название>'"
                "\nНапример: /buy молоко"
                "\n\nВсе функции в меню или по команде /help", chat)

        elif text == "/get":
            message = "\n".join(items)
            if message == "":
                send_message("Кажется, тут пусто 🐾", chat)
            else:
                send_message("Список дел: ", chat)
                send_message(message, chat)

        elif text == "/help":
            send_message("Планы и задачи 📃:"
                         "\nЧтобы добавить задачу - просто напиши любое сообщение"
                         "\n/done - удалить сделанную задачу ✅"
                         "\n/get - посмотреть список задач ❓"
                         "\n/help - увидеть это сообщение 😊", chat)
            send_message("Список покупок ✏:"
                         "\n/buy <название> - добавить в список покупок 🍏"
                         "\n/bought - удалить из списка покупок 🍞"
                         "\n/show - посмотреть списко покупок 🧀", chat)

        elif "/buy " in text:
            purchase = text.replace("/buy ", "")
            pb.add_item(purchase, chat)
            send_message("Добавлено в список покупок 🛒", chat)

        elif text == "/bought":
            purchases = pb.get_items(chat)
            keyboard = build_keyboard(purchases)
            send_message("Выбери что нужно удалить", chat, keyboard)

        elif text == "/show":
            message = "\n".join(purchases)
            if message == "":
                send_message("Кажется, тут пусто 🐾", chat)
            else:
                send_message("Список покупок: ", chat)
                send_message(message, chat)

        elif text.startswith("/"):
            continue

        elif text in items:
            db.delete_item(text, chat)
            items = db.get_items(chat)
            keyboard = build_keyboard(items)
            send_message("Что еще уже сделано?", chat, keyboard)

        elif text in purchases:
            pb.delete_item(text, chat)
            purchases = pb.get_items(chat)
            keyboard = build_keyboard(purchases)
            send_message("Успешно удалено 🍏", chat, keyboard)

        else:
            db.add_item(text, chat)
            items = db.get_items(chat)
            send_message("Теперь в списке!", chat)
            question = randint(1, 9)
            if question == 1:
                send_message("Что ещё?", chat)
            if question == 2:
                send_message("И всё?", chat)
            if question == 3:
                send_message("Другие задания?", chat)
            if question == 4:
                send_message("Добавить еще что-нибудь?", chat)
            if question == 5:
                send_message("Больше заданий!", chat)
            if question == 6:
                send_message("Много дел...", chat)
            if question == 7:
                send_message("Задание? Добавим!", chat)
            if question == 8:
                send_message("Ещё что-то для меня?", chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)

    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    db.setup()
    pb.setup()

    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
