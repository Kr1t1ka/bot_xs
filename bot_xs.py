from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import random
from datetime import datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from sqlite3 import Error


# Функция подключающияся к бд. Или создает ее если ее нет.
def create_connection(path):
    try:
        connection = sqlite3.connect(path)
        print("Подключение к базе данных SQLite прошло успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")
    return connection


# Записть в БД.
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Запрос выполнен успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")


# Чтение из БД
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Произошла ошибка '{e}'")


connection = create_connection("test1.sqlite")  # подключение к бд, или ее создание

# Подключение к боту
select_token = "SELECT group_token FROM token WHERE id = '1'"  # Выберает токен по уникальному id
select_victorina = "SELECT * FROM victorina"

# Выгрузка данных из бд для викторины
victorina_mass = execute_read_query(connection,
                                    select_victorina)  # Массив содержащий в себе вопросы и ответы для викторины

victorina_indicator = {}  # Словарь с данными о том на каком вопросе пользователь
dictionary_res = {}


# Функция записывающая пользователя в словарь
def vic_indicator(user_id):
    victorina_indicator[user_id] = 0
    dictionary_res[user_id] = 0
    text_question = victorina_mass[0][1]
    send_message(vk_session, 'user_id', event.user_id,
                 message=text_question,
                 keyboard=keyboard)

# Функция блокирует выход из викторины и отбрасывает все неподходяшие сообшения при прохождении викторины
def vic_test(user_id):
    try:
        print("Пользователь " + fullname + " проходит викторину, сейчас на вопросе номер: " + str(victorina_indicator[user_id]))
        return 1
    except:
        print("Пользователь " + fullname + " не проходит викторину")
        return 0


token = execute_read_query(connection, select_token)
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


# Функция создающая клавиатуры
def create_keyboard(response):
    keyboard = VkKeyboard(one_time=False)
    if response == "начать":
        keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Розыгрыш', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Конкурс', color=VkKeyboardColor.POSITIVE)
    elif response == 'расписание':
        keyboard.add_button('Лекций', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Ивентов', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    elif response == 'назад':
        keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Розыгрыш', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Конкурс', color=VkKeyboardColor.POSITIVE)
    elif response == 'викторина':
        select_users = "SELECT res FROM Qiuz WHERE id = '" + str(
            event.user_id) + "'"  # Выберает номер пользователя по уникальному id
        test_res = execute_read_query(connection, select_users)
        test_res = test_res[0]
        test_res = test_res[0]
        if test_res == -1:
            keyboard = VkKeyboard(one_time=False)
            keyboard.add_button('1', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('2', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('3', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('4', color=VkKeyboardColor.POSITIVE)
        else:
            keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    keyboard = keyboard.get_keyboard()
    return keyboard


# Генерирует сообщения
def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',
                      {id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648),
                       "attachment": attachment, 'keyboard': keyboard})


# Функция викторины
def victorina(check_dict, response):
    res = 0
    try:
        num_question = victorina_indicator[check_dict]

        if response == str(victorina_mass[num_question][2]):
            dictionary_res[check_dict] += 1

        if num_question == 9:
            return dictionary_res[check_dict]

        if num_question < 10:
            victorina_indicator[check_dict] += 1
        num_question = victorina_indicator[check_dict]
        text_question = str(victorina_mass[num_question][1])
        send_message(vk_session, 'user_id', event.user_id, message=text_question)
    except:
        print("ошибка в викторине")
        return res


# Создание таблицы в бд
create_users_table = '''
CREATE TABLE "victorina" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"question"	TEXT UNIQUE,
	"answer"	INTEGER NOT NULL DEFAULT 1
);
'''

'''
#можно чисто по фану раскоментить и посмотреть что произойдет 
tmp = 0
while True:
    select_u = "SELECT * FROM Qiuz"
    us = execute_read_query(connection, select_u)
    send_message(vk_session, 'user_id', 100653823, message = "Ты хуй")
    print(tmp)
    tmp += 1
'''

# execute_query(connection, create_users_table)
# execute_query(connection, create_users)

# Основная часть.
while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            try:
                user = vk_session.method("users.get",
                                         {"user_ids": event.user_id})  # вместо 1 подставляете айди нужного юзера
                fullname = user[0]['first_name'] + ' ' + user[0]['last_name']
                print(str(fullname) + " " + str(event.user_id))
                print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                print('Текст сообщения: ' + str(event.text))
                print('-' * 60)

                select_users = "SELECT num FROM Qiuz WHERE id = '" + str(event.user_id) + "'"

                response = event.text.lower()
                keyboard = create_keyboard(response)

                if event.from_user and not (event.from_me):
                    if ((response == "1") or (response == "2") or (response == "3") or (response == "4")) and (vic_test(event.user_id) == 1):
                        result = victorina(event.user_id, response)

                        if result != None:
                            keyboard = create_keyboard("назад")
                            send_message(vk_session, 'user_id', event.user_id,
                                            message='Тест заверщен. \n\nКонечно можно было бы и лучше, но вы равно умнее половины ртсников. '
                                                    '\n\nВаш результат: ' + str(result),
                                            keyboard=keyboard)
                            victorina_indicator.pop(event.user_id)
                            update_res = "UPDATE Qiuz SET res=('" + str(result) + "') WHERE id = ('" + str(event.user_id) + "');"
                            execute_query(connection, update_res)
                    elif vic_test(event.user_id) == 0:
                        if response == "начать":
                            create_acc = "INSERT INTO Qiuz (name, id) VALUES ('" + str(fullname) + "', '" + str(
                                event.user_id) + "');"
                            execute_query(connection, create_acc)
                            send_message(vk_session, 'user_id', event.user_id,
                                         message='Привет ' + user[0]['first_name'] +
                                                 '!\nЖелаете узнать расписание, поучаствовать в розыгрыше или пройти виктарину?'
                                                 ' \n\nИли хотите сдать работу на конкурс',
                                         keyboard=keyboard)

                        elif response == "расписание":
                            send_message(vk_session, 'user_id', event.user_id, message='Расписание Лекций или Ивентов?',
                                         keyboard=keyboard)

                        elif response == "розыгрыш":
                            users = execute_read_query(connection, select_users)
                            users = users[0]
                            users = users[0]
                            message_start = "Все подкручено ты ничего не выиграешь. " \
                                            "\n\nВаш номер в системе бота: " + str(
                                users) + "\n\nПо нему будет осуществлятся розыгрыш."
                            send_message(vk_session, 'user_id', event.user_id, message=message_start)

                        elif response == "лекций":
                            send_message(vk_session, 'user_id', event.user_id, message='(расписание лекций)')

                        elif response == "ивентов":
                            send_message(vk_session, 'user_id', event.user_id, message='(расписание ивентов)')

                        elif response == "назад":
                            send_message(vk_session, 'user_id', event.user_id,
                                         message='Желаете узнать расписание, поучаствовать в розыгрыше или пройти виктарину?'
                                                 ' \n\nИли хотите сдать работу на конкурс',
                                         keyboard=keyboard)

                        elif response == "викторина":
                            select_users = "SELECT res FROM Qiuz WHERE id = '" + str(
                                event.user_id) + "'"  # Выберает номер пользователя по уникальному id
                            test_res = execute_read_query(connection, select_users)
                            test_res = test_res[0]
                            test_res = test_res[0]
                            if test_res == -1:
                                vic_indicator(event.user_id)
                            else:
                                if test_res == 10:
                                    test_res = test_res
                                    create_keyboard('назад')
                                    send_message(vk_session, 'user_id', event.user_id,
                                                 message='Молодец! Вы знаете про факультет ИКСС все! \n\nВаш результат: ' + str(test_res))
                                else:
                                    test_res = test_res
                                    keyboard = create_keyboard(response)
                                    send_message(vk_session, 'user_id', event.user_id,
                                                 message='Ваш результат: ' + str(test_res) + ' \n\n\nВпечатляющий результат, но он не идеальный')
            except:
                print("Произошла ошибка в основном коде")
