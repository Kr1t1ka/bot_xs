def messageResult(result):
    message = "Молодец!"
    if result == 10:
        message = "Поздравляем, ты один из немногих, кто прошёл викторину и набрал 10 баллов! Суперприз по праву твой!\n" \
                  "(напиши этому человеку [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 9:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Но, ты набрал ты 9 баллов и выиграл значок!\n" \
                  "(напиши этому человеку [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 8:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Но, ты набрал ты 8 баллов и выиграл значок!\n" \
                  "(напиши этому человеку [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 7:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Но, ты набрал ты 7 баллов и выиграл значок!\n" \
                  "(напиши этому человеку [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 6:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Но, ты набрал ты 6 баллов и выиграл стикер!\n" \
                  "(напиши этому человеку [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 5:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Но, ты набрал ты 5 баллов и выиграл стикер!\n" \
                  "(напиши этому человеку [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 4:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Но, ты набрал ты 4 балла и выиграл стикер!\n" \
                  "(напиши этому [id21818078|человеку] и узнай, как получить свой приз)\n"
    if result == 3:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Результат: 3\n"
    if result == 2:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Результат: 2\n"
    if result == 1:
        message = "К сожалению, ты дал неправильный ответ на предыдущий вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Результат: 1\n"
    if result == 0:
        message = "К сожалению, ты дал неправильный ответ на вопрос. Не расстраивайся!\n" \
                  "Сегодня ты можешь поближе познакомиться с нашим факультетом и в следующем году точно пройдешь всю викторину!\n" \
                  "Результат: 0\n"
    return message
