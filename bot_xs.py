import sys

from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import dbWork
import traceback
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random

connection = dbWork.create_connection("test1.sqlite")  # подключение к бд, или ее создание

# Подключение к боту
select_token = "SELECT group_token FROM token WHERE id = '1'"  # Выберает токен по уникальному id
token = dbWork.execute_read_query(connection, select_token)
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
LongPoll = VkLongPoll(vk_session)

# Выгрузка данных из бд для викторины
select_victorina = "SELECT * FROM victorina"
# Массив содержащий в себе вопросы и ответы для викторины
victorina_mass = dbWork.execute_read_query(connection, select_victorina)

victorina_indicator = {}  # Словарь с данными о том на каком вопросе пользователь
dictionary_res = {}  # Словарь содержет в себе результаты ответов
dictionary_contest = {}  # Словарь для конкурса


def create_keyboard(UserResponse):
    UserKeyboard = VkKeyboard(one_time=False)

    if UserResponse == "начать":
        UserKeyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Розыгрыш', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Конкурс', color=VkKeyboardColor.POSITIVE)

    elif UserResponse == 'расписание':
        UserKeyboard.add_button('Лекций', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Ивентов', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'конкурс':
        UserKeyboard.add_button('Сдать работу', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'сдать работу':
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'назад':

        dictionary_contest.pop(event.user_id, None)
        print(dictionary_contest)
        UserKeyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Розыгрыш', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Конкурс', color=VkKeyboardColor.POSITIVE)

    elif UserResponse == 'викторина':
        SelectUsers = "SELECT res FROM Qiuz WHERE id = '" + \
                      str(event.user_id) + "'"  # Выберает номер пользователя по уникальному id
        test_res = dbWork.execute_read_query(connection, SelectUsers)[0][0]

        if test_res == -1:
            UserKeyboard = VkKeyboard(one_time=False)
            UserKeyboard.add_button('1', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_button('2', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_button('3', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_button('4', color=VkKeyboardColor.POSITIVE)

        else:
            UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    UserKeyboard = UserKeyboard.get_keyboard()
    return UserKeyboard


# Генерирует сообщения
def send_message(VkSession, VkUserId, message=None, attachment=None, UserKeyBoard=None, payload=None):
    """
    :type payload: пока хз, потом напишу
    :type VkSession: сессия вк устававлимая через токен
    :type VkUserId: id пользователя
    :type message: сообщение для пользователя
    :type attachment: вложения для пользователя
    :type UserKeyBoard: клавиатура для поьлзователя
    """
    VkSession.method('messages.send', {
        'peer_id': VkUserId,
        'message': message,
        'random_id': random.randint(-2147483648, +2147483648),
        "attachment": attachment,
        'keyboard': UserKeyBoard,
        'payload': payload
    })


# Функция записывающая пользователя в словарь
def vic_indicator(user_id):
    victorina_indicator[user_id] = 0
    dictionary_res[user_id] = 0
    text_question = victorina_mass[0][1]
    send_message(vk_session, event.user_id,
                 message=text_question,
                 UserKeyBoard=keyboard)


# Функция викторины
def victorina(check_dict, ResponseUser):
    res = 0
    try:
        num_question = victorina_indicator[check_dict]

        if ResponseUser == str(victorina_mass[num_question][2]):
            dictionary_res[check_dict] += 1

        if num_question == 9:
            return dictionary_res[check_dict]

        if num_question < 10:
            victorina_indicator[check_dict] += 1
        num_question = victorina_indicator[check_dict]
        text_question = str(victorina_mass[num_question][1])
        send_message(vk_session, event.user_id, message=text_question)
    except Exception:
        E_message_vic = "Ошибка:\n," + str(traceback.format_exc())
        send_message(vk_session, 83886028, message=E_message_vic)
        return res


# Основная часть.
while True:
    print("Бот успешно запущен")
    for event in LongPoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            # noinspection PyBroadException
            try:
                user = vk_session.method("users.get", {"user_ids": event.user_id})
                InformationMessage = vk_session.method("messages.getById", {"message_ids": event.message_id})
                fullname = user[0]['first_name'] + ' ' + user[0]['last_name']

                # вывод данных в консоль, для мониторнка работы бота
                print(str(fullname) + " " + str(event.user_id))
                print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                print('Текст сообщения: ' + str(event.text))
                print('-' * 60)
                print(event.attachments)
                print('-' * 60)


                #TODO: крч, тут до некст отметки код, который принимает вложение фотку вытягивает url и отправляет обратно url ссылку
                if event.attachments['attach1_type']=='photo':
                    test = InformationMessage['items'][0]['attachments'][0]['photo']['sizes']
                    test1 = test[len(test)-1]['url']

                if event.attachments['attach1_type']=='photo' and event.from_user and not event.from_me:
                    send_message(vk_session, event.user_id,
                                 message="penis",
                                 attachment=test1)
                #TODO: вот до сюда. Этот код надо интегрировать в раздел "Сдать работу", так что бы эта ссылка на работу сохранялась в
                # бд вместе с id пользователя именем и фамилией
                # и по специальному запросу от админов высылала все url ссылки с именами и фамилиями людей



                select_users = "SELECT num FROM Qiuz WHERE id = '" + str(event.user_id) + "'"
                response = event.text.lower()
                keyboard = create_keyboard(response)
                photo = event.attachments

                if event.from_user and not event.from_me:
                    if ((response == "1") or (response == "2") or (response == "3") or (response == "4")) and \
                            (event.user_id in victorina_indicator):
                        # Сработает если пользователь ввел 1/2/3/4 и (проходит викторину)

                        result = victorina(event.user_id, response)
                        # Получает результат прохождения викторины, или None если не проел ее до конца

                        if result is not None:  # Выполняется если польщователь прошел викторину
                            keyboard = create_keyboard("назад")
                            send_message(vk_session, event.user_id,
                                         message='Тест заверщен. '
                                                 '\n\nКонечно можно было бы и лучше, но ты все равно молодец. '
                                                 '\n\nВаш результат: ' + str(result),
                                         UserKeyBoard=keyboard)
                            victorina_indicator.pop(event.user_id)
                            update_res = "UPDATE Qiuz SET res=('" + str(result) + "') WHERE id = ('" + str(
                                event.user_id) + "');"
                            dbWork.execute_query(connection, update_res)

                    elif not (event.user_id in victorina_indicator) and not (event.user_id in dictionary_contest):
                        # выполняется если пользователь не проходит викторину и бот не ждет от него работы на конкурс

                        if response == "начать":

                            create_acc = "INSERT INTO Qiuz (name, id) VALUES ('" + str(fullname) + "', '" + str(
                                event.user_id) + "');"
                            dbWork.execute_query(connection, create_acc)  # Создание записи о пользователе в бд

                            send_message(vk_session, event.user_id,
                                         message='Доброго времени суток ' + user[0]['first_name'] +
                                                 '!\nЖелаете узнать расписание, поучаствовать в розыгрыше или пройти виктарину?'
                                                 ' \n\nИли хотите сдать работу на конкурс',
                                         UserKeyBoard=keyboard)

                        elif response == "розыгрыш":

                            if dbWork.execute_read_query(connection, select_users)[0][0]:
                                users = dbWork.execute_read_query(connection, select_users)[0][
                                    0]  # получаем номер пользователя в бд

                                message_start = "Пусть удача прибудет с тобой, и ты выиграешь " \
                                                "\n\nВаш номер в системе бота: " + str(users) + \
                                                "\n\nПо нему будет осуществлятся розыгрыш."

                                send_message(vk_session, event.user_id,
                                             message=message_start)

                            else:
                                send_message(vk_session, event.user_id,
                                             message="Произошла ошибка, напишите 'Начать'")

                        elif response == "расписание":
                            send_message(vk_session, event.user_id,
                                         message='Расписание Лекций или Ивентов?',
                                         UserKeyBoard=keyboard)

                        elif response == "лекций":
                            send_message(vk_session, event.user_id,
                                         message='(расписание лекций)')

                        elif response == "ивентов":
                            send_message(vk_session, event.user_id,
                                         message='(расписание ивентов)')

                        elif response == "конкурс":
                            send_message(vk_session, event.user_id,
                                         message='Конкурс дизайна \n'
                                                 '(описание и условия конкурса)',
                                         attachment="photo427981641_457250888",
                                         UserKeyBoard=keyboard)

                        elif response == "сдать работу":
                            send_message(vk_session, event.user_id,
                                         message='Отправьте мне работу',
                                         UserKeyBoard=keyboard)
                            dictionary_contest[event.user_id] = 0

                        elif response == "назад":
                            send_message(vk_session, event.user_id,
                                         message='Желаете узнать расписание, поучаствовать в розыгрыше или пройти виктарину?\n\n'
                                                 'Или хотите сдать работу на конкурс',
                                         UserKeyBoard=keyboard)

                        elif response == "викторина":
                            select_users = "SELECT res FROM Qiuz WHERE id = '" + str(event.user_id) + "'"

                            if dbWork.execute_read_query(connection, select_users):
                                res_victorina: int = dbWork.execute_read_query(connection, select_users)[0][
                                    0]  # получаем результат викторины
                            else:
                                send_message(vk_session, event.user_id,
                                             message="Произошла ошибка, Напишите 'Начать'")

                            # noinspection PyUnboundLocalVariable
                            if res_victorina == -1:  # пользователь записывается в словарь, для прохождения викторины
                                vic_indicator(event.user_id)

                            else:  # вывод результата прохождения викторины
                                if res_victorina > 10:
                                    send_message(vk_session, event.user_id,
                                                 message='Молодец! Вы знаете про факультет ИКСС все!\n\n'
                                                         'Ваш результат: ' + str(res_victorina))
                                else:
                                    send_message(vk_session, event.user_id,
                                                 message='Ваш результат: ' + str(res_victorina) + '\n\n'
                                                                                                  'Впечатляющий результат, но он не идеальный')
            except Exception as e:
                E_message = "Ошибка:\n," + str(traceback.format_exc())
                send_message(vk_session, 83886028,
                             message=E_message)
                sys.exit()
