from pytube import YouTube
import telebot
import yandex
import config
import pickle

import logging
logging.basicConfig(level=logging.DEBUG, filename='logs.txt')

try:
    with open('session_storage.pkl', 'rb') as f:
        sessionStorage = pickle.load(f)
except Exception as e:
    print(e)
    sessionStorage = {}

bot = telebot.TeleBot(config.TG_TOKEN)
print('Server started')
for cid in config.ADMIN_IDS:
    try:
        bot.send_message(cid, 'Server started')
    except telebot.apihelper.ApiException as e:
        logging.info(f'Error while sending message to {cid}:\n{str(e)}')


def get_video_url(chat_id, url):
    if url == sessionStorage[chat_id].get('last_url'):  # Second attempt - trying another player
        yt = YouTube(url).streams.first()
        sessionStorage[chat_id]['last_url'] = url
        return yt.url

    sessionStorage[chat_id]['last_url'] = url

    if "https://www.youtube" in url:
        url = url.split("&")[0]  # Removing arguments

    if "https://youtu.be" in url:
        url = "https://www.youtube.com/watch?v=" + url.split("/")[-1]

    # Page parsing and getting video_url here
    return url


def extract_url(text):
    return text  # TODO: getting url by entities info


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Привет, данный бот поможет вам отправить видео на вашу станцию")
    if chat_id not in sessionStorage:
        bot.send_message(chat_id, "Пришлите ваш логин и пароль от яндекса (нужно отключить вход по смс)")
    else:
        bot.send_message(chat_id, "Для выхода используйте команду /logout")


@bot.message_handler(commands=['logout'])
def handle_logout(message):
    chat_id = message.chat.id

    if chat_id not in sessionStorage:
        bot.send_message(chat_id, "Вы не авторизованы")
    else:
        del sessionStorage[chat_id]
        bot.send_message(chat_id, "Выход выполнен")


@bot.message_handler(content_types=['text'])
def handle_process_message(message):
    chat_id = message.chat.id

    if chat_id not in sessionStorage:
        bot.delete_message(chat_id, message.message_id)
        try:
            login, password = message.text.split()
            login, password = login.strip(), password.strip()
            req_session, x_csrf_token = yandex.get_session(login, password)
            sessionStorage[chat_id] = {
                'session': req_session,
                'x_csrf_token': x_csrf_token,
            }
            bot.send_message(chat_id, "Авторизация прошла успешно!")
            with open('session_storage.pkl', 'wb') as f:
                pickle.dump(sessionStorage, f)
            return
        except Exception as err:
            bot.send_message(chat_id, "Произошла ошибка")
            if chat_id in config.ADMIN_IDS:
                bot.send_message(chat_id, str(err))
            return

    url = extract_url(message.text)
    video_url = get_video_url(chat_id, url)
    try:
        result, device_name = yandex.send_to_screen(sessionStorage[chat_id]['session'], sessionStorage[chat_id]['x_csrf_token'], video_url)
    except Exception as err:
        bot.send_message(chat_id, "Произошла ошибка")
        if chat_id in config.ADMIN_IDS:
            bot.send_message(chat_id, str(err))
        return

    bot.send_message(chat_id, f'Видео отправлено на {device_name}\n{result + video_url}')


if __name__ == '__main__':
    bot.infinity_polling()