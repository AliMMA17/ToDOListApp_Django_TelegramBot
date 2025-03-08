# handlers/command_handlers.py
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from loader import dp  # import the central dispatcher

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks"),
            ],
            [
                InlineKeyboardButton(text="View Categories", callback_data="view_categories"),
                InlineKeyboardButton(text="View Completed Tasks", callback_data="view_completed_tasks"),
            ],
            [
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
    )
    
    await message.answer(
        "Main Menu Options:\n\n"
        "Choose one of the following actions:\n"
        "1. Add a Task\n"
        "2. View Tasks\n"
        "3. View Categories\n"
        "4. View Completed Tasks\n"
        "5. Clear All Tasks",
        reply_markup=keyboard
    )


