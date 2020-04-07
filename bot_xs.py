import sys
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import dbWork
import traceback
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import generationMessage
import threading
import time
import helpFunc

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
thread_list = []
t_flag = True


def create_keyboard(UserResponse):
    UserKeyboard = VkKeyboard(one_time=False)

    if (UserResponse == "начать") or (UserResponse == 'назад'):
        if UserResponse == 'назад':
            dictionary_contest.pop(event.user_id, None)
        UserKeyboard = VkKeyboard(one_time=True)
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
        if (event.user_id == 83886028) or (event.user_id == 87404117) or (event.user_id == 88333266):
            UserKeyboard.add_button('Просмотр работ', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_line()
        UserKeyboard.add_button('Сдать работу', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'сдать работу':
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'розыгрыш':
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'викторина':
        SelectUsers = "SELECT res FROM Qiuz WHERE id = '" + \
                      str(event.user_id) + "'"  # Выберает номер пользователя по уникальному id
        test_res = dbWork.execute_read_query(connection, SelectUsers)[0][0]

        if test_res == -1:
            UserKeyboard = VkKeyboard(one_time=False, inline=True)
            UserKeyboard.add_button('1', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_button('2', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_button('3', color=VkKeyboardColor.POSITIVE)
            UserKeyboard.add_button('4', color=VkKeyboardColor.POSITIVE)

        else:
            UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    UserKeyboard = UserKeyboard.get_keyboard()
    return UserKeyboard


# Генерирует сообщения
def send_message(VkSession, VkUserId, message=None, attachment=None, UserKeyBoard=None):
    """
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
        'keyboard': UserKeyBoard
    })


# Функция записывающая пользователя в словарь
def vic_indicator(user_id):
    victorina_indicator[user_id] = 0
    print('Создалась запись в словаре с ключом ' + str(user_id))
    dictionary_res[user_id] = 0
    text_question = victorina_mass[0][1]
    send_message(vk_session, event.user_id,
                 message=text_question,
                 UserKeyBoard=keyboard)


# Функция викторины
def victorina(check_dict, ResponseUser):
    res = 0
    try:
        print('Викторина приняла значание ключа: ' + str(check_dict))
        num_question = victorina_indicator[check_dict]

        if ResponseUser == str(victorina_mass[num_question][2]):
            dictionary_res[check_dict] += 1
        elif ResponseUser == '0':
            helpFunc.answer_vic(result=dictionary_res[check_dict])
        else:
            return dictionary_res[check_dict]

        if num_question == 9:
            return dictionary_res[check_dict]

        if num_question < 10 and not (ResponseUser == '0'):
            victorina_indicator[check_dict] += 1

        if ResponseUser != '0':
            num_question = victorina_indicator[check_dict]
            text_question = str(victorina_mass[num_question][1])
            keyboard_question = create_keyboard('викторина')
            send_message(vk_session,
                         event.user_id,
                         message=text_question,
                         UserKeyBoard=keyboard_question)
            global t_flag
            t_flag = True
    except Exception:
        E_message_vic = "Ошибка:\n," + str(traceback.format_exc())
        send_message(vk_session, 83886028, message=E_message_vic)
        return res

# TODO разобратся с таймером, и с этими непонтно как работающими функциями helpFunc и generationMessage
def timer(n, time_user_id):
    time_indicator = victorina_indicator[int(time_user_id)]
    global t_flag
    print('Таймер для {} запущен\n'.format(time_user_id))
    t_flag = True
    time.sleep(n)
    print('Время у {} закончилось\n'.format(time_user_id))
    print(t_flag)
    print(time_indicator + 1)
    print(victorina_indicator[int(time_user_id)])
    tmp = (time_indicator == victorina_indicator[int(time_user_id)])
    print(t_flag)

    if t_flag and ((time_indicator + 1) == victorina_indicator[int(time_user_id)]):
        victorina(int(time_user_id), "0")



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
                print('Вложение: ' + str(event.user_id))
                print('-' * 60)

                select_users = "SELECT num FROM Qiuz WHERE id = '" + str(event.user_id) + "'"
                response = event.text.lower()
                keyboard = create_keyboard(response)
                photo = event.attachments

                timer_thread = threading.Thread(target=timer,
                                                name='thread_' + str(event.user_id),
                                                args=(5, str(event.user_id)))

                # Крч, тут можно добавиьт то чир аписано снизу, но шанс воспроизведения этой ошибки очень мал
                # А строк кода добавится много  (15) оно того не стоит
                # (добавить зашиту от запрсов к NULL к массивам и славарям, для JSON InformationMessage)
                if event.attachments and (event.user_id in dictionary_contest):
                    limit = 5
                    URL_file = InformationMessage['items'][0]['attachments'][0]

                    if event.attachments['attach1_type'] == 'photo':
                        URL_file = InformationMessage['items'][0]['attachments'][0]['photo']['sizes']
                        URL_file = URL_file[len(URL_file) - 1]['url']
                        keyboard = create_keyboard('назад')

                    if event.attachments['attach1_type'] == 'doc':
                        URL_file = InformationMessage['items'][0]['attachments'][0]['doc']['url']
                        keyboard = create_keyboard('назад')

                    if event.attachments['attach1_type'] == 'link':
                        URL_file = event.attachments['attach1_url']
                        keyboard = create_keyboard('назад')

                    test_contest = "SELECT URL FROM contest_design WHERE id = '" + str(event.user_id) + "'"
                    quantity_photo = dbWork.execute_read_query(connection, test_contest)
                    if len(quantity_photo) >= limit:
                        send_message(vk_session, event.user_id,
                                     message="Извените но на конкурс можно отправить не более " + str(
                                         limit) + " работ.",
                                     UserKeyBoard=keyboard)
                    else:
                        create_contest = "INSERT INTO contest_design (URL, id, fullname) VALUES ('" + str(
                            URL_file) + "', '" + str(
                            event.user_id) + "', '" + str(fullname) + "');"
                        dbWork.execute_query(connection, create_contest)

                        if event.from_user and not event.from_me:
                            send_message(vk_session, event.user_id,
                                         message="Спасибо, ваша работа принята",
                                         UserKeyBoard=keyboard)

                if event.from_user and not event.from_me:
                    if ((response == "1") or (response == "2") or (response == "3") or (response == "4")) and \
                            (event.user_id in victorina_indicator):
                        # Сработает если пользователь ввел 1/2/3/4 и (проходит викторину)

                        t_flag = False

                        thread_list.append(timer_thread)
                        timer_thread.start()

                        helpFunc.answer_vic(result=None)

                        '''# TODO: написать остановку потока и запус нового

                        result = victorina(event.user_id, response)
                        # Получает результат прохождения викторины, или None если не проел ее до конца

                        if result is not None:  # Выполняется если польщователь прошел викторину
                            keyboard = create_keyboard("назад")
                            message_result = generationMessage.messageResult(result)
                            send_message(vk_session, event.user_id, message=message_result, UserKeyBoard=keyboard)
                            victorina_indicator.pop(event.user_id)
                            print('Удалена запись в словаре с ключом ' + str(event.user_id))

                            update_res = "UPDATE Qiuz SET res=('" + str(result) + "') WHERE id = ('" + str(
                                event.user_id) + "');"
                            #dbWork.execute_query(connection, update_res)'''

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
                                                "\n\nПо нему будет осуществляться розыгрыш."

                                send_message(vk_session, event.user_id,
                                             message=message_start,
                                             UserKeyBoard=keyboard)

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

                        elif response == "просмотр работ" and ((event.user_id == 83886028) or
                                                               (event.user_id == 87404117) or
                                                               (event.user_id == 88333266)):
                            select_work = "SELECT URL, fullname FROM contest_design"
                            user_work = dbWork.execute_read_query(connection, select_work)
                            print(user_work)
                            for number in range(len(user_work)):
                                MessageWork = "Работа: " + str(user_work[number][0]) + "\n" \
                                                                                       "Выполнил: " + str(
                                    user_work[number][1]) + "\n" + "-" * 35
                                send_message(vk_session, event.user_id,
                                             message=MessageWork)

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
                                thread_list.append(timer_thread)
                                timer_thread.start()
                                print("поток запущен")

                            else:  # вывод результата прохождения викторины
                                keyboard_vic = create_keyboard('назад')
                                if res_victorina > 10:
                                    send_message(vk_session, event.user_id,
                                                 message='Молодец! Вы знаете про факультет ИКСС все!\n\n'
                                                         'Ваш результат: ' + str(res_victorina),
                                                 UserKeyBoard=keyboard_vic)
                                else:
                                    send_message(vk_session, event.user_id,
                                                 message='Ваш результат: ' + str(res_victorina) +
                                                         '\n\nВпечатляющий результат, но он не идеальный',
                                                 UserKeyBoard=keyboard_vic)
            except Exception as e:
                E_message = "Ошибка:\n," + str(traceback.format_exc())
                send_message(vk_session, 83886028,
                             message=E_message)
                print(E_message)
                sys.exit()
