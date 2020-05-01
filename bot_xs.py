from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import dbWork
import traceback
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import generationMessage
import time

print("Версия: 0.57")

# Обьявление всех словарей на случай если пропадет соединение и бот будет переподключатся
victorina_indicator = {}  # Словарь с данными о том на каком вопросе пользователь
dictionary_res = {}  # Словарь содержет в себе результаты ответов
dictionary_contest = {}  # Словарь для конкурса
dictionary_timer = {}  # Словарь хранящий время ответов на вопросы
dictionary_sql = {}  # Словарь для sql запросов
dictionary_quest = {}  # Словарь с квестами
dictionary_quest_indicator = {}  # словарь с вкладкой "Квест"
dictionary_vic_question = {}  # Словарь с вопросами и ответами

fullname = "ОШИБКА"  # ты ошибка, да, ты, тот кто это читает

# Ответы бота TODO: вынести их в отдельный файл
message_quest_0 = 'Добро пожаловать во вкладку квест. ' \
                  'Здесь мы познакомим тебя с нашими кафедрами и тем, чем они занимаются. ' \
                  'Что бы начать, тебе надо ответить, к чему ведет QR-код?🐶'
message_quest_1 = "Поздравляем,ты прошел первый этап нашего квеста! " \
                  "Это было давольно просто не так ли? Но это не конец! " \
                  "Теперь предлагаю познакомиться с кафедрой филс и ответить на вопрос."
message_quest_2 = "Ты зашёл так далеко! Но здесь ты не пройдешь. " \
                  "Попробуй пройти сквозь защиту кафедры ЗСС." \
                  "(http://u900653e.beget.tech/)"
message_quest_3 = "Поздравляю, ты прошел квест и стал ближе к нашему факультету! " \
                  "Теперь тебя ждёт небольшой бонус, ведь не каждый смог дойти до конца!"
message_quest_4 = "Молодец ты успешно прошел наш небольшой квест. " \
                  "Можешь рассказать о нем друзьям, и узнать такие же они догадливые."
message_vic_start = 'Вы можете пройти викторину только один раз.\n'\
                    'Викторина состоит из 10 вопросов.\n'\
                    'Переход к следующему вопросу возможен только при правильном ответе. '\
                    'На каждый вопрос дается одна минута, '\
                    'по истечению времени автоматически засчитывается неправильный ответ.\n'\
                    'За каждый вопрос даётся 1 балл.\n'\
                    'При наборе 4 баллов, ваш приз - стикер, при 7 - значок, при 10 - суперприз.\n'\
                    'Желаем удачи!'

#  TODO: Добваить глосование за работы на конкурс дизайна.
#  доработать немного косметически

while True:
    try:
        connection = dbWork.create_connection("test1.sqlite")  # подключение к бд, или ее создание
        connection_sql = dbWork.create_connection("event_sql.db")

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


        def create_keyboard(UserResponse):
            global test_res
            UserKeyboard = VkKeyboard(one_time=False)

            if (UserResponse == "начать") or (UserResponse == 'главное меню'):
                SelectUsers = "SELECT res FROM quiz WHERE id = '" + \
                              str(event.user_id) + "'"  # Выберает номер пользователя по уникальному id
                if UserResponse == 'начать':
                    test_res = -1

                if UserResponse == 'главное меню':
                    dictionary_contest.pop(event.user_id, None)
                    dictionary_sql.pop(event.user_id, None)
                    dictionary_quest_indicator.pop(event.user_id, None)
                    try:
                        test_res = dbWork.execute_read_query(connection, SelectUsers)[0][0]
                    except:
                        send_message(vk_session, event.user_id, message="Ой, ошибочка.")
                UserKeyboard = VkKeyboard(one_time=True)
                UserKeyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
                UserKeyboard.add_button('Розыгрыш', color=VkKeyboardColor.PRIMARY)
                UserKeyboard.add_line()
                UserKeyboard.add_button('Викторина', color=VkKeyboardColor.PRIMARY)
                UserKeyboard.add_button('Конкурс', color=VkKeyboardColor.PRIMARY)
                if test_res > -1:
                    UserKeyboard.add_button('Квест', color=VkKeyboardColor.POSITIVE)

            elif UserResponse == 'викторина':
                UserKeyboard = VkKeyboard(one_time=True)
                UserKeyboard.add_button('Приступить', color=VkKeyboardColor.POSITIVE)
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'квест':
                UserKeyboard.add_button('SQL', color=VkKeyboardColor.PRIMARY)
                UserKeyboard.add_button('Какой QR-код?', color=VkKeyboardColor.PRIMARY)
                UserKeyboard.add_line()
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'расписание':
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'sql':
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'конкурс':
                if (event.user_id == 83886028) or (event.user_id == 87404117) or (event.user_id == 88333266):
                    UserKeyboard.add_button('Просмотр работ(админка)', color=VkKeyboardColor.PRIMARY)
                    UserKeyboard.add_line()
                UserKeyboard.add_button('Сдать работу', color=VkKeyboardColor.POSITIVE)
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'сдать работу':
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'розыгрыш':
                UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

            elif UserResponse == 'приступить':
                SelectUsers = "SELECT res FROM quiz WHERE id = '" + \
                              str(event.user_id) + "'"  # Выберает номер пользователя по уникальному id
                try:
                    test_res = dbWork.execute_read_query(connection, SelectUsers)[0][0]
                except:
                    send_message(vk_session, event.user_id,
                                 message="Ой, ошибочка.\n"
                                         "Запрос вмещает в себя слишком много данных, "
                                         "попробуйте сузить параметры поиска.")

                if test_res == -1:
                    UserKeyboard = VkKeyboard(one_time=False, inline=True)
                    UserKeyboard.add_button('1', color=VkKeyboardColor.PRIMARY)
                    UserKeyboard.add_button('2', color=VkKeyboardColor.PRIMARY)
                    UserKeyboard.add_button('3', color=VkKeyboardColor.PRIMARY)
                    UserKeyboard.add_button('4', color=VkKeyboardColor.PRIMARY)

                else:
                    UserKeyboard.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

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
            dictionary_vic_question[user_id] = random.randint(1, 2)

            if dictionary_vic_question[user_id] == 1:
                text_question = victorina_mass[0][1]

            elif dictionary_vic_question[user_id] == 2:
                text_question = victorina_mass[0][3]

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

                if dictionary_vic_question[check_dict] == 1:
                    if ResponseUser == str(victorina_mass[num_question][2]):
                        dictionary_res[check_dict] += 1
                    else:
                        return dictionary_res[check_dict]
                else:
                    if ResponseUser == str(victorina_mass[num_question][4]):
                        dictionary_res[check_dict] += 1
                    else:
                        return dictionary_res[check_dict]

                if num_question == 9:
                    return dictionary_res[check_dict]
                if num_question < 10:
                    victorina_indicator[check_dict] += 1

                dictionary_vic_question[check_dict] = random.randint(1, 2)
                num_question = victorina_indicator[check_dict]
                if dictionary_vic_question[check_dict] == 1:
                    text_question = str(victorina_mass[num_question][1])
                else:
                    text_question = str(victorina_mass[num_question][3])

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
                        select_quest = "SELECT step FROM quest WHERE id = '" + str(event.user_id) + "'"

                        # вывод данных в консоль, для мониторнка работы бота
                        print(str(fullname) + " " + str(event.user_id))
                        print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                        print('Текст сообщения: ' + str(event.text))
                        print('Вложение: ' + str(event.user_id))
                        try:
                            dictionary_quest[event.user_id] = dbWork.execute_read_query(connection, select_quest)[0][0]
                            print("Пользователь проходит квест. "
                                  "Сейчас на шаге: " + str(dictionary_quest[event.user_id]))
                        except:
                            print("Пользователь не проходит квест.")
                            dictionary_quest[event.user_id] = -1
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
                                keyboard = create_keyboard('главное меню')

                            if event.attachments['attach1_type'] == 'doc':
                                URL_file = InformationMessage['items'][0]['attachments'][0]['doc']['url']
                                keyboard = create_keyboard('главное меню')

                            if event.attachments['attach1_type'] == 'link':
                                URL_file = event.attachments['attach1_url']
                                keyboard = create_keyboard('главное меню')

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
                                    message_result = generationMessage.messageResult(
                                        result) + "А этот QR-код тебе пригодится."
                                    keyboard = create_keyboard("расписание")
                                    attachment = "photo-192914903_457239052"
                                    create_acc_quest = "INSERT INTO quest (id, step) VALUES ('" + str(
                                        event.user_id) + "','1');"

                                    dbWork.execute_query(connection, create_acc_quest)  # запись пользователей в квест

                                    send_message(vk_session, event.user_id,
                                                 message=message_result,
                                                 UserAttachment=attachment,
                                                 UserKeyBoard=keyboard)

                                    victorina_indicator.pop(event.user_id)
                                    update_res = "UPDATE quiz SET res=('" + str(result) + "') WHERE id = ('" + str(
                                        event.user_id) + "');"
                                    dbWork.execute_query(connection, update_res)
                            elif (((response.find('select') == 0) or (response.find('from') == 0) or (
                                    response.find('where') == 0)) and (event.user_id in dictionary_sql)):

                                if event.user_id == 838860281:
                                    message_sql = dbWork.execute_read_query(connection, response)
                                else:
                                    message_sql = dbWork.execute_read_query(connection_sql, response)

                                try:
                                    send_message(vk_session, event.user_id,
                                                 message=str(message_sql))
                                except:
                                    send_message(vk_session, event.user_id,
                                                 message="Ой, ошибочка.\n"
                                                         "Запрос вмещает в себя слишком много данных, "
                                                         "попробуйте сузить параметры поиска.")

                            # обработка квеста
                            elif event.user_id in dictionary_quest_indicator:
                                if response == "sql":
                                    dictionary_sql[event.user_id] = 1
                                    attachment = "photo-192914903_457239036"
                                    send_message(vk_session, event.user_id,
                                                 message='Ты не любишь инстаграмм и сторис? \n'
                                                         'Тогда эта вкладка для тебя, здесь ты можешь получить QR-код, который является яастью большого квеста.\n'
                                                         'Таблица поможет тебе в составлении SQL-запросов.\n'
                                                         'Начани с этого: "SELECT emi FROM ceubi WHERE id=0"',
                                                 UserAttachment=attachment,
                                                 UserKeyBoard=keyboard)
                                elif response == "какой qr-код?":
                                    keyboard = create_keyboard('расписание')  # выводит клавиатуру "Главное меню"
                                    send_message(vk_session, event.user_id,
                                                 message='(подсказка про qr-код)',
                                                 UserKeyBoard=keyboard)

                                elif dictionary_quest[event.user_id] > 0:

                                    if dictionary_quest[event.user_id] == 1:
                                        if (response.find("хатико") > -1) or (response.find("собака") > -1) \
                                                or (response.find("акита-ину") > -1) or (response.find("сиба-ину") > -1) \
                                                or (response.find("сиба ину") > -1) or (
                                                response.find("акита ину") > -1):

                                            send_message(vk_session, event.user_id, message=message_quest_1,
                                                         UserAttachment="video-192914903_456239019")
                                            update_quest = "UPDATE quest SET step=('2') WHERE id = ('" + str(
                                                event.user_id) + "');"
                                            dbWork.execute_query(connection, update_quest)
                                        else:
                                            send_message(vk_session, event.user_id, message="間違った答え")
                                    elif dictionary_quest[event.user_id] == 2:
                                        if (response.find("10 15") > -1) or (response.find("10-15") > -1):

                                            send_message(vk_session, event.user_id, message=message_quest_2)
                                            update_quest = "UPDATE quest SET step=('3') WHERE id = ('" + str(
                                                event.user_id) + "');"
                                            dbWork.execute_query(connection, update_quest)
                                        else:
                                            send_message(vk_session, event.user_id, message='Ответ неверный, '
                                                                                            'посмотри отрывок фильма '
                                                                                            '"Операция «Колибри»", и попробуй ответить еще раз.')
                                    elif dictionary_quest[event.user_id] == 3:
                                        if response == "пароль":

                                            send_message(vk_session, event.user_id,
                                                         message=message_quest_3)
                                            update_quest = "UPDATE quest SET step=('4') WHERE id = ('" + str(
                                                event.user_id) + "');"
                                            dbWork.execute_query(connection, update_quest)
                                        else:
                                            send_message(vk_session, event.user_id,
                                                         message="ERROR404:\n THE_PASSWORD_IS_INCORRECT")

                            elif not (event.user_id in victorina_indicator) and not (
                                    event.user_id in dictionary_contest) and not (event.user_id in dictionary_sql) \
                                    and not (event.user_id in dictionary_quest_indicator):

                                # выполняется если пользователь не проходит викторину и бот не ждет от него работы на конкурс

                                if response == "начать":

                                    create_acc = "INSERT INTO quiz (name, id) VALUES ('" + str(fullname) + "', '" + str(
                                        event.user_id) + "');"
                                    dbWork.execute_query(connection, create_acc)  # Создание записи о пользователе в бд

                                    # TODO: исправить все текста

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

                                            message_vic = "Пусть удача прибудет с тобой, и ты выиграешь " \
                                                            "\n\nВаш номер в системе бота: " + str(users) + \
                                                            "\n\nПо нему будет осуществляться розыгрыш."

                                            send_message(vk_session, event.user_id,
                                                         message=message_vic,
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
                                                 message='(Расписание лекций)',
                                                 UserKeyBoard=keyboard)

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

                                elif response == "просмотр работ(админка)" and ((event.user_id == 83886028) or
                                                                                (event.user_id == 87404117) or
                                                                                (event.user_id == 88333266)):
                                    select_work = "SELECT URL, fullname FROM contest_design"
                                    user_work = dbWork.execute_read_query(connection, select_work)
                                    for number in range(len(user_work)):
                                        MessageWork = "Работа: " + str(user_work[number][0]) + "\n" \
                                                                                               "Выполнил: " + str(
                                            user_work[number][1]) + "\n" + "-" * 35
                                        send_message(vk_session, event.user_id,
                                                     message=MessageWork)

                                elif response == "викторина":
                                    send_message(vk_session, event.user_id,
                                                 message=message_vic_start, UserKeyBoard=keyboard)

                                elif response == "квест":
                                    dictionary_quest_indicator[event.user_id] = 1
                                    if dictionary_quest[event.user_id] == 1:
                                        send_message(vk_session, event.user_id, message=message_quest_0,
                                                     UserKeyBoard=keyboard)
                                    elif dictionary_quest[event.user_id] == 2:
                                        keyboard = create_keyboard('расписание')  # выводит клавиатуру "Главное меню"
                                        send_message(vk_session, event.user_id, message=message_quest_1,
                                                     UserAttachment="video-192914903_456239019", UserKeyBoard=keyboard)
                                    elif dictionary_quest[event.user_id] == 3:
                                        keyboard = create_keyboard('расписание')  # выводит клавиатуру "Главное меню"
                                        send_message(vk_session, event.user_id, message=message_quest_2,
                                                     UserKeyBoard=keyboard)
                                    elif dictionary_quest[event.user_id] == 4:
                                        keyboard = create_keyboard('расписание')  # выводит клавиатуру "Главное меню"
                                        send_message(vk_session, event.user_id, message=message_quest_4,
                                                     UserKeyBoard=keyboard)

                                elif response == "главное меню":
                                    send_message(vk_session, event.user_id,
                                                 message='Наше мероприятие проходит в формате лекций и интерактивов.'
                                                         '\nПодробнее с ними ты можешь ознакомиться, нажав на соответствующие кнопки.'
                                                         '\nТак же участвуй в нашей викторине! (она будет доступна только 22 мая)'
                                                         '\nА ещё, мы приготовили для тебя розыгрыш. Для участия в нем тебе надо пройти викторину '
                                                         '(неважно, сколько баллов ты там наберёшь).',
                                                 UserKeyBoard=keyboard)

                                elif response == "приступить":

                                    create_raffle = "INSERT INTO raffle (name, id) VALUES ('" + str(
                                        fullname) + "', '" + str(
                                        event.user_id) + "');"
                                    dbWork.execute_query(connection,
                                                         create_raffle)  # Создание записи о пользователе в бд

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
                                        keyboard_vic = create_keyboard('главное меню')
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
                        E_message = "Ошибка:\n," + str(traceback.format_exc()) + "\n" \
                                                                                 "Пользователь: " + str(
                            fullname) + " " + str(event.user_id) + '\n' \
                                                                   "Сообщение пришло в: " + str(
                            datetime.strftime(datetime.now(), "%H:%M:%S")) + "\n" \
                                                                             "Вложение: " + str(event.user_id) + "\n"
                        send_message(vk_session, 83886028,
                                     message=E_message)
                        print(E_message)
                        # sys.exit()
    except:
        E_message = "Ошибка:\n," + str(traceback.format_exc())
        print(E_message)
