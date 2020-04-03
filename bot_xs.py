from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import random
from datetime import datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import dbWork

connection = dbWork.create_connection("test1.sqlite")  # подключение к бд, или ее создание

# Подключение к боту
select_token = "SELECT group_token FROM token WHERE id = '1'"  # Выберает токен по уникальному id
select_victorina = "SELECT * FROM victorina"
token = dbWork.execute_read_query(connection, select_token)
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Выгрузка данных из бд для викторины
victorina_mass = dbWork.execute_read_query(connection,select_victorina)  # Массив содержащий в себе вопросы и ответы для викторины

victorina_indicator = {}  # Словарь с данными о том на каком вопросе пользователь
dictionary_res = {} # Словарь содержет в себе результаты ответов

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
        print("\nПользователь " + fullname + " проходит викторину, сейчас на вопросе номер: " + str(victorina_indicator[user_id]))
        return 1
    except:
        return 0

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
        select_users = "SELECT res FROM Qiuz WHERE id = '" + \
                        str(event.user_id) + "'"  # Выберает номер пользователя по уникальному id
        test_res = dbWork.execute_read_query(connection, select_users)[0][0]

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

# execute_query(connection, create_users_table)
# execute_query(connection, create_users)

# Основная часть.
while True:
    print("Бот успешно запущен")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            try:
                user = vk_session.method("users.get", {"user_ids": event.user_id})
                fullname = user[0]['first_name'] + ' ' + user[0]['last_name']

                # вывод данных в консоль, для мониторнка работы бота
                print(str(fullname) + " " + str(event.user_id))
                print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                print('Текст сообщения: ' + str(event.text))
                print('-' * 60)

                select_users = "SELECT num FROM Qiuz WHERE id = '" + str(event.user_id) + "'"

                response = event.text.lower()
                keyboard = create_keyboard(response)

                if event.from_user and not (event.from_me):
                    if ((response == "1") or (response == "2") or (response == "3") or (response == "4")) and (vic_test(event.user_id) == 1):

                        result = victorina(event.user_id, response) # Получает результат прохождения викторины, или None если не проел ее до конца

                        if result != None: # Выполняется если польщователь прошел викторину
                            keyboard = create_keyboard("назад")
                            send_message(vk_session, 'user_id', event.user_id,
                                            message='Тест заверщен. \n\nКонечно можно было бы и лучше, но вы равно умнее половины ртсников. '
                                                    '\n\nВаш результат: ' + str(result),
                                            keyboard=keyboard)
                            victorina_indicator.pop(event.user_id)
                            update_res = "UPDATE Qiuz SET res=('" + str(result) + "') WHERE id = ('" + str(event.user_id) + "');"
                            dbWork.execute_query(connection, update_res)

                    elif vic_test(event.user_id) == 0: # выполняется если пользователь не проходит викторину

                        if response == "начать":

                            create_acc = "INSERT INTO Qiuz (name, id) VALUES ('" + str(fullname) + "', '" + str(event.user_id) + "');"
                            dbWork.execute_query(connection, create_acc) # Создание записи о пользователе в бд

                            send_message(vk_session, 'user_id', event.user_id,
                                         message='Привет ' + user[0]['first_name'] +
                                                 '!\nЖелаете узнать расписание, поучаствовать в розыгрыше или пройти виктарину?'
                                                 ' \n\nИли хотите сдать работу на конкурс',
                                         keyboard=keyboard)

                        elif response == "розыгрыш":

                            users = dbWork.execute_read_query(connection, select_users)[0][0] # получаем номер пользователя в бд

                            message_start = "Пусть удача прибудет с тобой, и ты выиграешь " \
                                            "\n\nВаш номер в системе бота: " + str(users) + \
                                            "\n\nПо нему будет осуществлятся розыгрыш."

                            send_message(vk_session, 'user_id', event.user_id, message=message_start)

                        elif response == "расписание":
                            send_message(vk_session, 'user_id', event.user_id, message='Расписание Лекций или Ивентов?',keyboard=keyboard)

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
                            select_users = "SELECT res FROM Qiuz WHERE id = '" + str(event.user_id) + "'"
                            test_res = dbWork.execute_read_query(connection, select_users)[0][0] # получаем результат викторины

                            if test_res == -1:          # пользователь записывается в словарь, для прохождения викторины
                                vic_indicator(event.user_id)

                            else:                       # вывод результата прохождения викторины
                                if test_res == 10:
                                    send_message(vk_session, 'user_id', event.user_id,
                                                 message='Молодец! Вы знаете про факультет ИКСС все! '
                                                         '\n\nВаш результат: ' + str(test_res))
                                else:
                                    send_message(vk_session, 'user_id', event.user_id,
                                                 message='Ваш результат: ' + str(test_res) +
                                                         '\n\nВпечатляющий результат, но он не идеальный')
            except:
                print("Произошла ошибка в основном коде")
