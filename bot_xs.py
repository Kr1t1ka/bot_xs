from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import data
import random
from datetime import datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor



token = "9b0d14d517db405de5c53463e1f0f782b59cc170cc8df6f0857ad0b5bb37f3bd40e64d98882f82fbf908a"

vk_session = vk_api.VkApi(token=token)

session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def create_keyboard(response):
    keyboard = VkKeyboard(one_time=False)

    if response == 'тест':

        keyboard.add_button('Белая кнопка', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)

        keyboard.add_line()  # Переход на вторую строку
        keyboard.add_button('Красная кнопка', color=VkKeyboardColor.NEGATIVE)

        keyboard.add_line()
        keyboard.add_button('Синяя кнопка', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Привет', color=VkKeyboardColor.PRIMARY)


    elif response == 'привет':
        keyboard.add_button('Тест', color=VkKeyboardColor.POSITIVE)

    elif response == 'котики':
        keyboard.add_button('Котики!', color=VkKeyboardColor.POSITIVE)

    elif response == 'закрыть':
        print('закрываем клаву')
        return keyboard.get_empty_keyboard()

    keyboard = keyboard.get_keyboard()
    return keyboard

def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',{id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})
    

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            #try:
                print('Сообщение пришло в: ' + str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                print('Текст сообщения: ' + str(event.text))
                print(event.user_id)
                print('-' * 30)
                response = event.text.lower()
                keyboard = create_keyboard(response)
                                
                if event.from_user and not (event.from_me):
                    if response == "привет": 
                        send_message(vk_session, 'user_id', event.user_id, message='Нажми на кнопку, чтобы получить список команд',keyboard=keyboard)
                    elif response == "":
                        vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Буквами пиши, выблядок', 'random_id': 0})
                    elif response == "?":
                        vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Извините не тужа \nНо оксимирон пиздаиый', 'random_id': 0})
                    elif response == "2":
                        vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'отправь мне гс, и иди нахуй', 'random_id': 0})
                    elif response == "тест":
                        send_message(vk_session, 'user_id', event.user_id, message= 'Тестовые команды',keyboard=keyboard)
                    else:
                        vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Введите  2 или ? или отправь мне стикер. или раскажи про свою любовь мне', 'random_id': 0})
            #except:
            #    vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'ошибка ввода', 'random_id': 0})
        






        





        
