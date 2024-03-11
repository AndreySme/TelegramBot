from databases.database import update_quiz_index, get_quiz_index
from keyboards.keyboard import generate_options_keyboard
from data.questions import quiz_data


async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    user_name = f"{message.from_user.first_name} {message.from_user.last_name}"
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    number_correct_answers = 0
    await update_quiz_index(user_id, user_name, current_question_index, number_correct_answers)
    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)


async def get_question(message, user_id):
    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']

    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])

    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"✅ {quiz_data[current_question_index]['question']}", reply_markup=kb)
