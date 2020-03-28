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
        keyboard.add_button('Розыгрыш', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
    elif response == 'расписание':
        keyboard.add_button('Лекций', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Ивентов', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)
    elif response == 'назад':
        keyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Розыгрыш', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
    elif response == 'викторина':
        select_users = "SELECT res FROM Qiuz WHERE id = '" + str(fullname) + " " + str(event.user_id) + "'" #Выберает номер пользователя по уникальному id
        test_res = execute_read_query(connection, select_users)
        test_res = str(test_res)
        if test_res == "-1":
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        else:
            keyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)            
    elif response=="да":
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
        result = result[0]
        result = result[0]
        return result
    except Error as e:
        print(f"Произошла ошибка '{e}'")
#Функция викторины
def victorina():
    res = 0
    tmp = 0
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            try:
                response = event.text.lower()
                keyboard = create_keyboard(response)
                if response == "да":
                    for id in range(1, 11):
                        select_question = "SELECT question FROM victorina WHERE id = '" + str(id) + "'" #Выберает вопрос по уникальному id
                        select_answer = "SELECT answer FROM victorina WHERE id = '" + str(id) + "'" #Выберает ответ по уникальному id
                        question = execute_read_query(connection, select_question)
                        answer = execute_read_query(connection, select_answer)
                        send_message(vk_session, 'user_id', event.user_id, message=str(question),keyboard=keyboard)
                        res+=anser(answer)               
                    return res                
            except:
                vk_session.method('messages.send', {'user_id': event.user_id, 'message': f"Произошла ошибка в викторине:'{e}'", 'random_id': 0})
#Функция получает правельный ответ, и проверяет ответы введеные пользователем
def anser(answer):
    res = 0
    for event in longpoll.listen():            
        if event.type == VkEventType.MESSAGE_NEW:
                try:
                    user = vk_session.method("users.get", {"user_ids": event.user_id})
                    fullname = user[0]['first_name'] +  ' ' + user[0]['last_name']
                    print(str(fullname) + " " + str(event.user_id))
                    print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                    print('Текст сообщения: ' + str(event.text))
                    print('-' * 60)
                    response = event.text.lower()
                    keyboard = create_keyboard(response)
                                  
                    if event.from_user and not (event.from_me):
                        keyboard = create_keyboard(response)
                        print(response)
                        if (response=="1") or (response=="2") or (response=="3") or (response=="4"):
                            if int(response)==answer:
                                res = 1
                                return res
                            else:
                                return res
                except:
                    vk_session.method('messages.send', {'user_id': event.user_id, 'message': f"Произошла ошибка в генерации вопроса '{e}'", 'random_id': 0})
    
connection = create_connection("test1.sqlite")

#Создание таблицы в бд
create_users_table ='''
CREATE TABLE "victorina" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"question"	TEXT UNIQUE,
	"answer"	INTEGER NOT NULL DEFAULT 1
);
'''
#Оповещение о запуске бота
#send_message(vk_session, 'user_id', 223829105, message= 'БОТ УДАЧНО ЗАПУЩЕН. Скорее всего я подкручиваю результаты базы данных')
send_message(vk_session, 'user_id', 83886028, message= 'БОТ УДАЧНО ЗАПУЩЕН')

#execute_query(connection, create_users_table)
#execute_query(connection, create_users)

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
                    elif response == "розыгрыш":
                        message_start = "Все подкручено ты ничего не выиграешь, если ты не с иксс. Ваш номер в системе бота: " + str(users)
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
                        if test_res == "-1":
                            send_message(vk_session, 'user_id', event.user_id, message= 'Начнем?',keyboard=keyboard)
                            result = victorina()
                            result = str(result)
                            print(response)
                            create_acc = "UPDATE Qiuz SET res=('" + result + "') WHERE id = ('" + str(fullname) + " " + str(event.user_id) + "');"
                            execute_query(connection, create_acc)
                            keyboard = create_keyboard(response)
                            send_message(vk_session, 'user_id', event.user_id, message= 'Тест заверщен. \n\nКонечно можно было бы и лучше, но вы равно умнее половины ртсников. \n\nВаш результат: '+result,keyboard=keyboard)
                        else:
                            if test_res == "10":
                                test_res = test_res
                                create_keyboard('назад')
                                send_message(vk_session, 'user_id', event.user_id, message= 'Вы молодец, вы умнее 90% иситовцев. \n\nВаш результат: '+test_res)                                
                            else:
                                test_res = test_res
                                print(response)
                                keyboard = create_keyboard(response)
                                send_message(vk_session, 'user_id', event.user_id, message= 'Ваш результат: '+test_res+' \nЕсли вы с гф, то гордитесь этим до конца жизни, чудо что вы вообще тест прошли. ',keyboard=keyboard)                                
            except:
                vk_session.method('messages.send', {'user_id': event.user_id, 'message': "Произошла ошибка в основном коде:'{e}'", 'random_id': 0})






        





        
