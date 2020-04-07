import bot_xs
import generationMessage



def answer_vic(result=None):
    # Сработает если пользователь ввел 1/2/3/4 и (проходит викторину)
    print("Следующий вопрос генерируется, после ответа " + str(result))

    if result is None:
        result = bot_xs.victorina(bot_xs.event.user_id, bot_xs.response)
        # Получает результат прохождения викторины, или None если не проел ее до конца

    if result is not None:  # Выполняется если польщователь прошел викторину
        keyboard = bot_xs.create_keyboard("назад")
        message_result = messageResult(result)
        bot_xs.send_message(bot_xs.vk_session, bot_xs.event.user_id, message=message_result, UserKeyBoard=keyboard)
        bot_xs.victorina_indicator.pop(bot_xs.event.user_id)
        bot_xs.t_flag = False
        print('Удалена запись в словаре с ключом ' + str(bot_xs.event.user_id))

        update_res = "UPDATE Qiuz SET res=('" + str(result) + "') WHERE id = ('" + str(
            bot_xs.event.user_id) + "');"
        # dbWork.execute_query(connection, update_res)


def messageResult(result):
    message = "Молодец! " + str(result)
    if result == 10:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 10 \n" \
                  "ЭТО ПРЕВОСХОДНЫЙ РЕЗУЛЬТАТ -- ВАШ приз Шоколадка!"
    if result == 9:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 9"
    if result == 8:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 8"
    if result == 7:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 7"
    if result == 6:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 6"
    if result == 5:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 5"
    if result == 4:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 4"
    if result == 3:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 3"
    if result == 2:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 2"
    if result == 1:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 1"
    if result == 0:
        message = "(НАДО ПРИДУМАТЬ УНИКАЛЬНЫЕ ОТВЕТ БОТА НА ВСЕ РЕЗУЛЬТАТЫ ВИКТОРИНЫ) результат: 0"
    return message
