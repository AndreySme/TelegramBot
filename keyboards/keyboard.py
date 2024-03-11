from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def generate_options_keyboard(answer_options, right_answer):

    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer" if option == right_answer else f"wrong_answer/{option[-20:]}"
            )
        )
    builder.adjust(1)
    return builder.as_markup()
