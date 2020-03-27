from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import data
import random
from datetime import datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import sqlite3
from sqlite3 import Error

#Подключение к боту
token = "e2edf221438fb1642ddfe5b8358559010e9c9be696c132946b9dd99a2df5a08de1c5c50d0234d63c37ffe"
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

#Функция создающая клавиатуры
def create_keyboard(response):
    keyboard = VkKeyboard(one_time=False)

    if response=="начать":

        keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Обманка', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)

    elif response == 'расписание':

        keyboard.add_button('Лекций', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Ивентов', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif response == 'назад':

        keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Обманка', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)

    elif response == 'викторина':
        select_users = "SELECT res FROM Qiuz WHERE id = '" + str(fullname) + " " + str(event.user_id) + "'" #Выберает номер пользователя по уникальному id
        test_res = execute_read_query(connection, select_users)
        test_res = str(test_res)
        if test_res == "[(-1,)]":
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Старт', color=VkKeyboardColor.POSITIVE)
        else:
            keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
            
    elif response == 'старт':
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('1', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('2', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('3', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('4', color=VkKeyboardColor.POSITIVE)

    keyboard = keyboard.get_keyboard()
    return keyboard

#Генерирует сообщения
def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',{id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})

#Функция подключающияся к бд. Или создает ее если ее нет.
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Подключение к базе данных SQLite прошло успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")

    return connection
#Записть в БД.
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Запрос выполнен успешно")
    except Error as e:
        print(f"Произошла ошибка '{e}'")
#Чтение из БД
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Произошла ошибка '{e}'")

def victorina():
    res = 0
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
                try:
                    #Вывод инфы в консоль
                    print(str(event.user_id))
                    print('Режим викторины. Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                    print('Ответ: ' + str(event.text))
                    print('-' * 60)
                    
                    #send_message(vk_session, 'user_id', event.user_id, message='Здраствуйте! \nПервый вопрос')
                                                        
                    response = event.text.lower()
                    keyboard = create_keyboard('старт')
                    print(res)                
                    if event.from_user and not (event.from_me):
                        if response == "старт":                            
                            send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 1.
                                                                                        1. Ответ 1
                                                                                        2. Ответ 2
                                                                                        3. Ответ 3
                                                                                        4. Ответ 4
                                                                                        ''',keyboard=keyboard)
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:
                                response = event.text.lower()
                                if event.from_user and not (event.from_me):
                                    if response == "1":
                                            keyboard = create_keyboard('старт')
                                            print('test1')
                                            res += 1
                                            print(res)
                                            send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 2.
                                                                                            1. Ответ 1
                                                                                            2. Ответ 2
                                                                                            3. Ответ 3
                                                                                            4. Ответ 4
                                                                                            ''')
                                    else:
                                        keyboard = create_keyboard('старт')
                                        print(res)
                                        send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 2.
                                                                                                1. Ответ 1
                                                                                                2. Ответ 2
                                                                                                3. Ответ 3
                                                                                                4. Ответ 4
                                                                                                ''')
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW:
                                            response = event.text.lower()
                                            if event.from_user and not (event.from_me):
                                                if response == "2":
                                                    keyboard = create_keyboard('старт')
                                                    print('test2')
                                                    res += 1
                                                    print(res)
                                                    keyboard = create_keyboard(response)
                                                    send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 3.
                                                                                                        1. Ответ 1
                                                                                                        2. Ответ 2
                                                                                                        3. Ответ 3
                                                                                                        4. Ответ 4
                                                                                                        ''')
                                                else:
                                                    keyboard = create_keyboard('старт')
                                                    print(res)
                                                    send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 3.
                                                                                                            1. Ответ 1
                                                                                                            2. Ответ 2
                                                                                                            3. Ответ 3
                                                                                                            4. Ответ 4
                                                                                                            ''')
                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW:
                                                        response = event.text.lower()
                                                        if event.from_user and not (event.from_me):
                                                            if response == "3":
                                                                keyboard = create_keyboard('старт')
                                                                print('test3')
                                                                res += 1
                                                                print(res)
                                                                send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 4.
                                                                                                                    1. Ответ 1
                                                                                                                    2. Ответ 2
                                                                                                                    3. Ответ 3
                                                                                                                    4. Ответ 4
                                                                                                                    ''')
                                                            else:
                                                                keyboard = create_keyboard('старт')
                                                                print(res)
                                                                send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 4.
                                                                                                                        1. Ответ 1
                                                                                                                        2. Ответ 2
                                                                                                                        3. Ответ 3
                                                                                                                        4. Ответ 4
                                                                                                                        ''')
                                                            for event in longpoll.listen():
                                                                if event.type == VkEventType.MESSAGE_NEW:
                                                                    response = event.text.lower()
                                                                    if event.from_user and not (event.from_me):
                                                                        if response == "4":
                                                                                print('test4')
                                                                                res += 1
                                                                                print(res)
                                                                                send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 5.
                                                                                                                                1. Ответ 1
                                                                                                                                2. Ответ 2
                                                                                                                                3. Ответ 3
                                                                                                                                4. Ответ 4
                                                                                                                                ''')
                                                                        else:
                                                                            print(res)
                                                                            send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 5.
                                                                                                                                    1. Ответ 1
                                                                                                                                    2. Ответ 2
                                                                                                                                    3. Ответ 3
                                                                                                                                    4. Ответ 4
                                                                                                                                    ''')
                                                                        for event in longpoll.listen():
                                                                            if event.type == VkEventType.MESSAGE_NEW:
                                                                                response = event.text.lower()
                                                                                if event.from_user and not (event.from_me):
                                                                                    if response == "1":
                                                                                            print('test5')
                                                                                            res += 1
                                                                                            print(res)
                                                                                            send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 6.
                                                                                                                                            1. Ответ 1
                                                                                                                                            2. Ответ 2
                                                                                                                                            3. Ответ 3
                                                                                                                                            4. Ответ 4
                                                                                                                                            ''')
                                                                                    else:
                                                                                        print(res)
                                                                                        send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 6.
                                                                                                                                                1. Ответ 1
                                                                                                                                                2. Ответ 2
                                                                                                                                                3. Ответ 3
                                                                                                                                                4. Ответ 4
                                                                                                                                                ''')
                                                                                    for event in longpoll.listen():
                                                                                        if event.type == VkEventType.MESSAGE_NEW:
                                                                                            response = event.text.lower()
                                                                                            if event.from_user and not (event.from_me):
                                                                                                if response == "2":
                                                                                                        print('test6')
                                                                                                        res += 1
                                                                                                        print(res)
                                                                                                        send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 7.
                                                                                                                                                        1. Ответ 1
                                                                                                                                                        2. Ответ 2
                                                                                                                                                        3. Ответ 3
                                                                                                                                                        4. Ответ 4
                                                                                                                                                        ''')
                                                                                                else:
                                                                                                    print(res)
                                                                                                    send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 7.
                                                                                                                                                            1. Ответ 1
                                                                                                                                                            2. Ответ 2
                                                                                                                                                            3. Ответ 3
                                                                                                                                                            4. Ответ 4
                                                                                                                                                            ''')
                                                                                                for event in longpoll.listen():
                                                                                                    if event.type == VkEventType.MESSAGE_NEW:
                                                                                                        response = event.text.lower()
                                                                                                        if event.from_user and not (event.from_me):
                                                                                                            if response == "3":
                                                                                                                    print('test7')
                                                                                                                    res += 1
                                                                                                                    print(res)
                                                                                                                    send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 8.
                                                                                                                                                                    1. Ответ 1
                                                                                                                                                                    2. Ответ 2
                                                                                                                                                                    3. Ответ 3
                                                                                                                                                                    4. Ответ 4
                                                                                                                                                                    ''')
                                                                                                            else:
                                                                                                                print(res)
                                                                                                                send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 8.
                                                                                                                                                                        1. Ответ 1
                                                                                                                                                                        2. Ответ 2
                                                                                                                                                                        3. Ответ 3
                                                                                                                                                                        4. Ответ 4
                                                                                                                                                                        ''')
                                                                                                            for event in longpoll.listen():
                                                                                                                if event.type == VkEventType.MESSAGE_NEW:
                                                                                                                    response = event.text.lower()
                                                                                                                    if event.from_user and not (event.from_me):
                                                                                                                        if response == "4":
                                                                                                                                print('test8')
                                                                                                                                res += 1
                                                                                                                                print(res)
                                                                                                                                send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 9.
                                                                                                                                                                                1. Ответ 1
                                                                                                                                                                                2. Ответ 2
                                                                                                                                                                                3. Ответ 3
                                                                                                                                                                                4. Ответ 4
                                                                                                                                                                                ''')
                                                                                                                        else:
                                                                                                                            print(res)
                                                                                                                            send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 9.
                                                                                                                                                                                    1. Ответ 1
                                                                                                                                                                                    2. Ответ 2
                                                                                                                                                                                    3. Ответ 3
                                                                                                                                                                                    4. Ответ 4
                                                                                                                                                                                    ''')
                                                                                                                        for event in longpoll.listen():
                                                                                                                            if event.type == VkEventType.MESSAGE_NEW:
                                                                                                                                response = event.text.lower()
                                                                                                                                if event.from_user and not (event.from_me):
                                                                                                                                    if response == "1":
                                                                                                                                            print('test9')
                                                                                                                                            res += 1
                                                                                                                                            print(res)
                                                                                                                                            send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 10.
                                                                                                                                                                                            1. Ответ 1
                                                                                                                                                                                            2. Ответ 2
                                                                                                                                                                                            3. Ответ 3
                                                                                                                                                                                            4. Ответ 4
                                                                                                                                                                                            ''')
                                                                                                                                    else:
                                                                                                                                        print(res)
                                                                                                                                        send_message(vk_session, 'user_id', event.user_id, message='''Вопрос 10.
                                                                                                                                                                                                1. Ответ 1
                                                                                                                                                                                                2. Ответ 2
                                                                                                                                                                                                3. Ответ 3
                                                                                                                                                                                                4. Ответ 4
                                                                                                                                                                                                ''')
                                                                                                                                    for event in longpoll.listen():
                                                                                                                                        if event.type == VkEventType.MESSAGE_NEW:
                                                                                                                                            response = event.text.lower()
                                                                                                                                            if event.from_user and not (event.from_me):
                                                                                                                                                if response == "2":
                                                                                                                                                    print('test10')
                                                                                                                                                    res += 1
                                                                                                                                                    print(res)
                                                                                                                                                    return res
                                                                                                                                                else:
                                                                                                                                                    return res
                                                                                                                                                
                except:
                    vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Ой, какаято ошибочка', 'random_id': 0})

        
connection = create_connection("test1.sqlite")


create_users_table ='''
CREATE TABLE "Qiuz" (
	"num"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"id"	TEXT UNIQUE,
	"res"	INTEGER NOT NULL DEFAULT -1
);
'''
#Оповещение о запуске бота
#send_message(vk_session, 'user_id', 223829105, message= 'БОТ УДАЧНО ЗАПУЩЕН. Скорее всего я подкручиваю результаты базы данных')
send_message(vk_session, 'user_id', 83886028, message= 'БОТ УДАЧНО ЗАПУЩЕН')

#execute_query(connection, create_users_table)
#execute_query(connection, create_users)

'''
#можно чисто по фану раскоментить и посмотреть что произойдет 
tmp = 0
while True:
    select_u = "SELECT * FROM Qiuz"
    us = execute_read_query(connection, select_u)
    send_message(vk_session, 'user_id', 223829105, message = str(us))
    print(tmp)
    tmp += 1
'''
#Основная часть.

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            try:
                user = vk_session.method("users.get", {"user_ids": event.user_id}) # вместо 1 подставляете айди нужного юзера
                fullname = user[0]['first_name'] +  ' ' + user[0]['last_name']
                print(str(fullname) + " " + str(event.user_id))
                print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                print('Текст сообщения: ' + str(event.text))
                print('-' * 60)
                
                select_users = "SELECT num FROM Qiuz WHERE id = '" + str(fullname) + " " + str(event.user_id) + "'" #Выберает номер пользователя по уникальному id
                users = execute_read_query(connection, select_users)
                                
                response = event.text.lower()
                keyboard = create_keyboard(response)
                                
                if event.from_user and not (event.from_me):
                    if response == "начать":
                        create_acc = "INSERT INTO Qiuz (id) VALUES ('" + str(fullname) + " " + str(event.user_id) + "');"
                        execute_query(connection, create_acc)
                        send_message(vk_session, 'user_id', event.user_id, message='Привет всем икссникам, остальным собалезную. \nЖелаете узнать расписание или пройти виктарину?',keyboard=keyboard)
                    elif response == "расписание":
                        send_message(vk_session, 'user_id', event.user_id, message='Расписание Лекций или Ивентов?',keyboard=keyboard)
                    elif response == "обманка":
                        user_id_naebka = str(users[0])
                        message_start = "Все подкручено ты ничего не выиграешь, если ты не с иксс. Ваш номер в системе бота: " + user_id_naebka[1:2]
                        print(message_start)
                        send_message(vk_session, 'user_id', event.user_id, message=message_start)
                    elif response == "лекций":
                        send_message(vk_session, 'user_id', event.user_id, message= '(расписание лекций)')
                    elif response == "ивентов":
                        send_message(vk_session, 'user_id', event.user_id, message= '(расписание ивентов)')
                    elif response == "назад":
                        send_message(vk_session, 'user_id', event.user_id, message= 'Желаете узнать расписание или пройти виктарину?',keyboard=keyboard)
                    elif response == "викторина":
                        select_users = "SELECT res FROM Qiuz WHERE id = '" + str(fullname) + " " + str(event.user_id) + "'" #Выберает номер пользователя по уникальному id
                        test_res = execute_read_query(connection, select_users)
                        test_res = str(test_res)
                        print(test_res)
                        if test_res == "[(-1,)]":
                            send_message(vk_session, 'user_id', event.user_id, message= 'Начнем?',keyboard=keyboard)
                            result = victorina()
                            result = str(result)
                            print(response)
                            create_acc = "UPDATE Qiuz SET res=('" + result + "') WHERE id = ('" + str(fullname) + " " + str(event.user_id) + "');"
                            execute_query(connection, create_acc)
                            keyboard = create_keyboard(response)
                            send_message(vk_session, 'user_id', event.user_id, message= 'Тест заверщен. \n\nКонечно можно было бы и лучше, но вы равно умнее половины ртсников. \n\nВаш результат: '+result,keyboard=keyboard)
                        else:
                            if test_res == "[(10,)]":
                                test_res = test_res[2:4]
                                create_keyboard('назад')
                                send_message(vk_session, 'user_id', event.user_id, message= 'Вы молодец, вы умнее 90% иситовцев. \n\nВаш результат: '+test_res)                                
                            else:
                                test_res = test_res[2:3]
                                print(response)
                                keyboard = create_keyboard(response)
                                send_message(vk_session, 'user_id', event.user_id, message= 'Ваш результат: '+test_res+' \nЕсли вы с гф, то гордитесь этим до конца жизни, чудо что вы вообще тест прошли. ',keyboard=keyboard)                                
            except:
                vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Ой, какаято ошибочка', 'random_id': 0})
        





        





        
