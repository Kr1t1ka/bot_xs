import sys
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import dbWork
import traceback
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import generationMessage
import time


connection = dbWork.create_connection("test1.sqlite")  # подключение к бд, или ее создание
connection_sql = dbWork.create_connection("Chinook_Sqlite.sqlite")

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
dictionary_timer = {}  # Словарь хранящий время ответов на вопросы
dictionary_sql = {}  # Словарь для sql запросов


def create_keyboard(UserResponse):
    UserKeyboard = VkKeyboard(one_time=False)

    if (UserResponse == "начать") or (UserResponse == 'назад'):
        if UserResponse == 'назад':
            dictionary_contest.pop(event.user_id, None)
            dictionary_sql.pop(event.user_id, None)
        UserKeyboard = VkKeyboard(one_time=True)
        UserKeyboard.add_button('Расписание', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Розыгрыш', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Викторина', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Конкурс', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Квесты', color=VkKeyboardColor.POSITIVE)

    elif UserResponse == 'викторина':
        UserKeyboard = VkKeyboard(one_time=True)
        UserKeyboard.add_button('Приступить', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'квесты':
        UserKeyboard.add_button('SQL', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Еще часть квеста', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Еще часть квеста', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Еще часть квеста', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'расписание':
        UserKeyboard.add_button('Лекций', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_button('Интерактивов', color=VkKeyboardColor.POSITIVE)
        UserKeyboard.add_line()
        UserKeyboard.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

    elif UserResponse == 'sql':
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

    elif UserResponse == 'приступить':
        SelectUsers = "SELECT res FROM quiz WHERE id = '" + \
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
def send_message(VkSession, VkUserId, message=None, UserAttachment=None, UserKeyBoard=None):
    """
    :type VkSession: сессия вк устававлимая через токен
    :type VkUserId: id пользователя
    :type message: сообщение для пользователя
    :type UserAttachment: вложения для пользователя
    :type UserKeyBoard: клавиатура для поьлзователя
    """
    VkSession.method('messages.send', {
        'peer_id': VkUserId,
        'message': message,
        'random_id': random.randint(-2147483648, +2147483648),
        "attachment": UserAttachment,
        'keyboard': UserKeyBoard
    })


# Функция записывающая пользователя в словарь
def vic_indicator(user_id):
    victorina_indicator[user_id] = 0
    dictionary_res[user_id] = 0
    dictionary_timer[user_id] = time.time()
    text_question = victorina_mass[0][1]

    send_message(vk_session, event.user_id,
                 message=text_question,
                 UserKeyBoard=keyboard)


# Функция викторины
def victorina(check_dict, ResponseUser):
    res = 0
    try:
        num_question = victorina_indicator[check_dict]
        if time.time() - dictionary_timer[check_dict] > 60:
            keyboard_question = create_keyboard('назад')
            send_message(vk_session,
                         event.user_id,
                         message="К сожаления вы слишком долго отвечали на этот вопрос",
                         UserKeyBoard=keyboard_question)
            return dictionary_res[check_dict]
        if ResponseUser == str(victorina_mass[num_question][2]):
            dictionary_res[check_dict] += 1
        else:
            return dictionary_res[check_dict]

        if num_question == 9:
            return dictionary_res[check_dict]

        if num_question < 10:
            victorina_indicator[check_dict] += 1

        num_question = victorina_indicator[check_dict]
        text_question = str(victorina_mass[num_question][1])
        keyboard_question = create_keyboard('приступить')
        dictionary_timer[check_dict] = time.time()
        send_message(vk_session,
                     event.user_id,
                     message=text_question,
                     UserKeyBoard=keyboard_question)
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
                print('Вложение: ' + str(event.user_id))

                print('-' * 60)

                select_users = "SELECT res FROM quiz WHERE id = '" + str(event.user_id) + "'"
                response = event.text.lower()
                keyboard = create_keyboard(response)
                photo = event.attachments

                # Крч, тут можно добавиьт то чир аписано снизу, но шанс воспроизведения этой ошибки очень мал
                # А строк кода добавится много  (15) оно того не стоит
                # (добавить зашиту от запрсов к NULL к массивам и славарям, для JSON InformationMessage)
                if event.attachments and (event.user_id in dictionary_contest):
                    limit = 40
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

                        result = victorina(event.user_id, response)
                        # Получает результат прохождения викторины, или None если не проел ее до конца

                        if result is not None:  # Выполняется если польщователь прошел викторину
                            message_result = generationMessage.messageResult(result) + "А этот QR-код тебе пригодится."
                            keyboard = create_keyboard("назад")
                            attachment = "photo-192914903_457239030"
                            send_message(vk_session, event.user_id,
                                         message=message_result,
                                         UserAttachment=attachment,
                                         UserKeyBoard=keyboard)

                            victorina_indicator.pop(event.user_id)
                            update_res = "UPDATE quiz SET res=('" + str(result) + "') WHERE id = ('" + str(
                                event.user_id) + "');"
                            # dbWork.execute_query(connection, update_res)
                    elif (((response.find('select') == 0) or (response.find('from') == 0) or (
                            response.find('where') == 0)) and (event.user_id in dictionary_sql)):

                        # TODO: добавить более сложную базу данных, что бы надо было поискать.
                        if event.user_id == 83886028:
                            message_sql = dbWork.execute_read_query(connection, response)
                        else:
                            message_sql = dbWork.execute_read_query(connection_sql, response)
                        send_message(vk_session, event.user_id,
                                     message=str(message_sql))

                    elif not (event.user_id in victorina_indicator) and not (
                            event.user_id in dictionary_contest) and not (event.user_id in dictionary_sql):
                        # выполняется если пользователь не проходит викторину и бот не ждет от него работы на конкурс

                        if response == "начать":

                            create_acc = "INSERT INTO quiz (name, id) VALUES ('" + str(fullname) + "', '" + str(
                                event.user_id) + "');"
                            dbWork.execute_query(connection, create_acc)  # Создание записи о пользователе в бд

                            send_message(vk_session, event.user_id,
                                         message='Доброго времени суток, ' + user[0]['first_name'] +
                                                 '!\nЯ бот, созданный ко дню рождения факультета ИКСС, который будет помогать тебе!'
                                                 '\n\nНаше мероприятие пройдёт в формате лекций и интерактивов.'
                                                 '\nПодробнее с ними ты можешь ознакомиться, нажав на соответствующие кнопки.'
                                                 '\nТак же участвуй в нашей викторине! (она будет доступна только 22 мая)'
                                                 '\nА ещё, мы приготовили для тебя розыгрыш. Для участия в нем тебе надо пройти викторину'
                                                 '(неважно, сколько баллов ты там наберёшь).'
                                                 '\n\nМы будем рады, если ты проведёшь этот день с нами! Удачи!',
                                         UserKeyBoard=keyboard)

                        elif response == "розыгрыш":
                            select_raffle = "SELECT num FROM raffle WHERE id = '" + str(event.user_id) + "'"

                            try:
                                if dbWork.execute_read_query(connection, select_raffle)[0][0]:
                                    users = dbWork.execute_read_query(connection, select_raffle)[0][
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
                            except:
                                send_message(vk_session, event.user_id,
                                             message="Для участия в розыгрыше тебе надо пройти викторину\n"
                                                     "(неважно, сколько баллов ты там наберёшь)",
                                             UserKeyBoard=keyboard)

                        elif response == "расписание":
                            send_message(vk_session, event.user_id,
                                         message='Расписание Лекций или Интерактивов?',
                                         UserKeyBoard=keyboard)

                        elif response == "лекций":
                            send_message(vk_session, event.user_id,
                                         message='(расписание лекций)')

                        elif response == "интерактивов":
                            send_message(vk_session, event.user_id,
                                         message='(расписание интерактивов)')

                        elif response == "конкурс":
                            send_message(vk_session, event.user_id,
                                         message='Сюда ты можешь загрузить свою работу на конкурс дизайна!\n'
                                                 '(подробности смотри в официальной группе факультета ИКСС в вк)',
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
                        elif response == "викторина":
                            send_message(vk_session, event.user_id,
                                         message='Вы можете пройти викторину только один раз.\n'
                                                 'Викторина состоит из 10 вопросов.\n'
                                                 'Переход к следующему вопросу возможен только при правильном ответе. '
                                                 'На каждый вопрос дается одна минута, '
                                                 'по истечению времени автоматически засчитывается неправильный ответ.\n'
                                                 'За каждый вопрос даётся 1 балл.\n'
                                                 'При наборе 4 баллов, ваш приз - стикер, при 7 - значок, при 10 - суперприз.\n'
                                                 'Желаем удачи!', UserKeyBoard=keyboard)

                        elif response == "квесты":
                            send_message(vk_session, event.user_id,
                                         message='На нашем факультете есть различные кафедры, и чтобы познакомить тебя поближе с тем, чем они занимаются, мы подготовили квест!\n'
                                                 'Собирай qr-коды, разгадывай шифры и выигрывай призы!',
                                         UserKeyBoard=keyboard)

                        elif response == "sql":
                            dictionary_sql[event.user_id] = 1
                            send_message(vk_session, event.user_id,
                                         message='Вам надо извлеч информация из факультеа ИКСС, с кафедры ПИИВТ.\n'
                                                 'отправьте мне sql запрос, и я поищю то что вам нужно у себя',
                                         UserKeyBoard=keyboard)

                        elif response == "назад":
                            send_message(vk_session, event.user_id,
                                         message='Наше мероприятие проходит в формате лекций и интерактивов.'
                                                 '\nПодробнее с ними ты можешь ознакомиться, нажав на соответствующие кнопки.'
                                                 '\nТак же участвуй в нашей викторине! (она будет доступна только 22 мая)'
                                                 '\nА ещё, мы приготовили для тебя розыгрыш. Для участия в нем тебе надо пройти викторину '
                                                 '(неважно, сколько баллов ты там наберёшь).',
                                         UserKeyBoard=keyboard)

                        elif response == "приступить":

                            create_raffle = "INSERT INTO raffle (name, id) VALUES ('" + str(fullname) + "', '" + str(
                                event.user_id) + "');"
                            dbWork.execute_query(connection, create_raffle)  # Создание записи о пользователе в бд

                            if dbWork.execute_read_query(connection, select_users):
                                res_victorina: int = dbWork.execute_read_query(connection, select_users)[0][
                                    0]  # получаем результат викторины
                                print(res_victorina)
                            else:
                                send_message(vk_session, event.user_id,
                                             message="Произошла ошибка, Напишите 'Начать'")

                            # noinspection PyUnboundLocalVariable
                            if res_victorina == -1:  # пользователь записывается в словарь, для прохождения викторины

                                vic_indicator(event.user_id)

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
                #sys.exit()
