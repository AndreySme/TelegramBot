import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message, KeyboardButton
from handlers.handler import new_quiz, get_question
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
from data.questions import quiz_data
from databases.database import (create_table, update_quiz_index, get_quiz_index,
                                get_number_correct_answers, get_results, get_user_name)
from config.config import API_TOKEN
import pandas as pd

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    print(callback.message.reply_markup)
    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Получаем количество правильных ответов
    number_correct_answers = await get_number_correct_answers(callback.from_user.id)
    # Отправляем в чат сообщение, что ответ верный
    for first_level in callback.message.reply_markup.inline_keyboard:
        if first_level[0].callback_data == 'right_answer':
            await callback.message.answer(f"Ваш ответ: {first_level[0].text} - правильный!👍")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    number_correct_answers += 1
    await update_quiz_index(callback.from_user.id, f"{callback.from_user.first_name} {callback.from_user.last_name}",
                            current_question_index, number_correct_answers)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        results = await get_results()
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        df = pd.DataFrame(results, columns=['--------', '']).set_index(keys='--------')
        await callback.message.answer(f"<u><b>Результаты</b></u>: <b>{df}</b>", parse_mode="HTML")


@dp.callback_query(F.data.split('/', maxsplit=1)[0] == "wrong_answer")
async def wrong_answer(callback: CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    callback_response = callback.data.split('/', maxsplit=1)[-1]
    for i in opts:
        if callback_response == i[-20:]:
            # Отправляем в чат сообщение об ошибке с указанием верного ответа
            await callback.message.answer(f"Ваш ответ: {i} - неправильный!😡\nПравильный ответ: "
                                          f"{quiz_data[current_question_index]['options'][correct_option]}")


    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    number_correct_answers = await get_number_correct_answers(callback.from_user.id)
    await update_quiz_index(callback.from_user.id, f"{callback.from_user.first_name} {callback.from_user.last_name}",
                            current_question_index, number_correct_answers)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        results = await get_results()
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        df = pd.DataFrame(results, columns=['--------', '']).set_index(keys='--------')
        await callback.message.answer(f"<u><b>Результаты</b></u>: <b>{df}</b>", parse_mode="HTML")


@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(KeyboardButton(text="Начать игру"))
    # Прикрепляем кнопки к сообщению
    await message.answer(f"Добро пожаловать, {message.from_user.first_name} {message.from_user.last_name}!",
                         reply_markup=builder.as_markup(resize_keyboard=True))


# Запуск процесса поллинга новых апдейтов
async def main():
    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
