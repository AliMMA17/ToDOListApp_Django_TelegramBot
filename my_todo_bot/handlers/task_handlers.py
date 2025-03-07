# handlers/task_handlers.py
from aiogram import Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter

from datetime import datetime
import aiohttp

from states import AddTaskStates
from utils import fetch_tasks, fetch_task_by_id, update_task_field,delete_task,delete_all_tasks,create_task,fetch_categories,fetch_completed_tasks
from config import API_URL

from loader import dp  # Import the central dispatcher


# Dictionary to store information about tasks being edited.
editing_task = {}

@dp.callback_query(lambda c: c.data == "add_task")
async def add_task_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Please send me the task title:")
    await state.set_state(AddTaskStates.waiting_for_title)
    user_id = callback.from_user.id
    await state.update_data(task_data={"completed": False, "telegram_user_id": user_id})

@dp.message(StateFilter(AddTaskStates.waiting_for_title))
async def process_title(message: Message, state: FSMContext):
    user_data = await state.get_data()
    task_data = user_data.get("task_data", {})
    task_data["title"] = message.text
    await state.update_data(task_data=task_data)
    
    await message.answer("Please send me the task description:")
    await state.set_state(AddTaskStates.waiting_for_description)

@dp.message(StateFilter(AddTaskStates.waiting_for_description))
async def process_description(message: Message, state: FSMContext):
    user_data = await state.get_data()
    task_data = user_data.get("task_data", {})
    task_data["description"] = message.text
    await state.update_data(task_data=task_data)
    
    await message.answer("Please send me the due date (format: YYYY-MM-DD HH:MM):")
    await state.set_state(AddTaskStates.waiting_for_due_date)

@dp.message(StateFilter(AddTaskStates.waiting_for_due_date))
async def process_due_date(message: Message, state: FSMContext):
    try:
        due_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        iso_due_date = due_date.strftime("%Y-%m-%dT%H:%M:00Z")
        user_data = await state.get_data()
        task_data = user_data.get("task_data", {})
        task_data["due_date"] = iso_due_date
        await state.update_data(task_data=task_data)
        
        await message.answer("Please send me the task category:")
        await state.set_state(AddTaskStates.waiting_for_category)
    except ValueError:
        await message.answer("Invalid date format! Please use YYYY-MM-DD HH:MM (e.g., 2025-03-05 17:00)")

@dp.message(StateFilter(AddTaskStates.waiting_for_category))
async def process_category(message: Message, state: FSMContext):
    user_data = await state.get_data()
    task_data = user_data.get("task_data", {})
    task_data["category"] = message.text
    
    # Use the create_task function from utils.py
    success = await create_task(task_data)
    
    if success:
        await message.answer("Task created successfully!")
    else:
        await message.answer("Failed to create task.")
    
    await state.clear()
    
    # Return to main menu
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Add a Task", callback_data="add_task")],
            [InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")],
            [InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")],
        ]
    )
    await message.answer("Back to main menu:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "view_tasks")
async def view_tasks_callback(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    tasks = await fetch_tasks(user_id)
    
    if tasks:
        for task in tasks:
            task_id = task['id']
            task_title = task['title']
            task_description = task['description'] if task.get('description') else "No description"
            task_due_date = (
                datetime.fromisoformat(task['due_date']).strftime("%B %d, %Y at %H:%M")
                if task.get('due_date') else "No due date"
            )
            task_created_at = (
                datetime.fromisoformat(task['created_at']).strftime("%B %d, %Y at %H:%M")
                if task.get('created_at') else "Unknown creation date"
            )
            task_category = task['category']
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Delete", callback_data=f"delete_{task_id}")],
                    [InlineKeyboardButton(text="Update", callback_data=f"update_{task_id}")]
                ]
            )
            await callback.message.answer(
                f"ID: {task_id}\nCreated At: {task_created_at}\n Title: {task_title}\n  Description: {task_description}\n Due Date: {task_due_date}\nCategory: {task_category}",
                reply_markup=keyboard
            )
    else:
        await callback.message.edit_text("You have no tasks at the moment!")

@dp.callback_query(lambda c: c.data.startswith("update_"))
async def update_task_callback(callback: CallbackQuery):
    task_id = callback.data.split("_")[1]
    user_id = callback.from_user.id  # Get user_id from callback

    # Fetch task for the specific user
    task = await fetch_task_by_id(user_id, task_id)

    # Save task ID for editing.
    editing_task[callback.from_user.id] = task_id

    await callback.answer()
    await callback.message.edit_text(
        f"Update Task\n\n"
        f"Title: {task['title']}\n"
        f"Due Date: {task['due_date']}\n"
        f"Category: {task['category']}\n\n"
        f"Click on a field to edit it.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Edit Title", callback_data=f"edit_title_{task_id}")],
                [InlineKeyboardButton(text="Edit Due Date", callback_data=f"edit_due_{task_id}")],
                [InlineKeyboardButton(text="Edit Category", callback_data=f"edit_category_{task_id}")],
                [InlineKeyboardButton(text="Cancel", callback_data=f"cancel_update_{task_id}")],
            ]
        )
    )
@dp.callback_query(lambda c: c.data.startswith("edit_"))
async def edit_task_field_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    field = parts[1]
    task_id = parts[2]

    user_id = callback.from_user.id  # Get user_id from callback

    # Fetch current task details for the user
    task = await fetch_task_by_id(user_id, task_id)

    if field == "title":
        await callback.message.answer("Please send the new title for the task:")
    elif field == "due":
        await callback.message.answer("Please send the new due date ,format: YYYY-MM-DD HH:MM:")
    elif field == "category":
        await callback.message.answer("Please send the new category:")

    # Save which field is being updated for this user.
    editing_task[callback.from_user.id] = {"task_id": task_id, "field": field}
    await callback.answer()


@dp.message(lambda message: message.from_user.id in editing_task and isinstance(editing_task[message.from_user.id], dict))
async def handle_task_update(message: Message):
    user_id = message.from_user.id  # Get user_id from the message
    task_info = editing_task[user_id]
    task_id = task_info['task_id']
    field = task_info['field']
    print("task_id: %s" % task_id)
    new_value = message.text
    if field == "title":
        await update_task_field(user_id, task_id, "title", new_value)
    elif field == "due":
        try:
            due_date = datetime.strptime(new_value, "%Y-%m-%d %H:%M")
            iso_due_date = due_date.strftime("%Y-%m-%dT%H:%M:00Z")
            await update_task_field(user_id, task_id, "due", iso_due_date)  # Use "due" as field
            await message.answer(f"The due date of the task has been updated to: {iso_due_date}")
        except ValueError:
            await message.answer("Invalid date format! Please use the format: YYYY-MM-DD HH:MM (e.g., 2025-03-05 17:00)")
            return
    elif field == "category":
        await update_task_field(user_id, task_id, "category", new_value)

    del editing_task[user_id]
    await message.answer(f"The {field} of the task has been updated to: {new_value}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
            ],
            [
                InlineKeyboardButton(text="Delete a Task", callback_data="delete_task"),
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
    )
    await message.answer(
        "Main Menu Options:\n\n"
        "Choose one of the following actions:\n"
        "1. Add a Task\n"
        "2. View Tasks\n"
        "3. Delete a Task\n"
        "4. Clear All Tasks",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("cancel_update_"))
async def cancel_update_callback(callback: CallbackQuery):
    user_id = callback.from_user.id  # Get user_id from callback
    if user_id in editing_task:
        del editing_task[user_id]
    await callback.answer("Update process canceled.")
    await callback.message.edit_text("Task update was canceled.")

@dp.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_specific_task_callback(callback: CallbackQuery):
    task_id = callback.data.split("_")[1]  # Extract task_id from callback data
    user_id = callback.from_user.id        # Get user_id from callback
    
    # Call the delete_task function from utils.py
    success = await delete_task(user_id, task_id)
    
    if success:
        await callback.messageanswer("Task deleted successfully!")
        await callback.message.answer(f"Task {task_id} has been deleted.")
    else:
        await callback.answer("Failed to delete task.")
        await callback.message.answer("Could not delete the task. Please try again.")
    
    # Show the main menu after deletion
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
            ],
            [
                InlineKeyboardButton(text="Delete a Task", callback_data="delete_task"),
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
    )
    
    await callback.message.answer(
        "Main Menu Options:\n\n"
        "Choose one of the following actions:\n"
        "1. Add a Task\n"
        "2. View Tasks\n"
        "3. Delete a Task\n"
        "4. Clear All Tasks",
        reply_markup=keyboard
    )






@dp.callback_query(lambda c: c.data == "clear_tasks")
async def clear_tasks_callback(callback: CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes, clear all tasks", callback_data="confirm_clear")],
            [InlineKeyboardButton(text="No, cancel", callback_data="cancel_clear")]
        ]
    )
    await callback.message.edit_text("Are you sure you want to clear all tasks?", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "confirm_clear")
async def confirm_clear_callback(callback: CallbackQuery):
    user_id = callback.from_user.id  # Get user_id from callback
    
    # Call the delete_all_tasks function from utils.py
    success = await delete_all_tasks(user_id)
    
    if success:
        await callback.answer("All tasks cleared successfully!")
        await callback.message.edit_text("All tasks have been cleared!")
    else:
        await callback.answer("Failed to clear tasks.")
        await callback.message.edit_text("Could not clear all tasks. Please try again.")
    
    # Show the main menu after clearing
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
            ],
            [
                InlineKeyboardButton(text="Delete a Task", callback_data="delete_task"),
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
    )
    await callback.message.answer(
        "Main Menu Options:\n\n"
        "Choose one of the following actions:\n"
        "1. Add a Task\n"
        "2. View Tasks\n"
        "3. Delete a Task\n"
        "4. Clear All Tasks",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "cancel_clear")
async def cancel_clear_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Task clearing cancelled.")
    
    # Show the main menu after cancellation
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
            ],
            [
                InlineKeyboardButton(text="Delete a Task", callback_data="delete_task"),
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
    )
    await callback.message.answer(
        "Main Menu Options:\n\n"
        "Choose one of the following actions:\n"
        "1. Add a Task\n"
        "2. View Tasks\n"
        "3. Delete a Task\n"
        "4. Clear All Tasks",
        reply_markup=keyboard
    )



@dp.callback_query(lambda c: c.data == "view_categories")
async def process_view_categories(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    categories = await fetch_categories(user_id)
    
    if categories:
        categories_text = "\n".join(categories)
        response = f"Your categories:\n\n{categories_text}"
    else:
        response = "No categories found."
    
    await callback.message.answer(response)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
            ],
            [
                InlineKeyboardButton(text="View Categories", callback_data="view_categories"),
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
    )
    await callback.message.answer(
        "Main Menu Options:\n\n"
        "Choose one of the following actions:\n"
        "1. Add a Task\n"
        "2. View Tasks\n"
        "3. View Categories\n"
        "4. Clear All Tasks",
        reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data == "view_completed_tasks")
async def process_view_completed_tasks(callback: CallbackQuery) -> None:
    await callback.answer()  # Acknowledge the callback immediately
    user_id = callback.from_user.id
    tasks = await fetch_completed_tasks(user_id)
    keyboard_main = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Add a Task", callback_data="add_task"),
                InlineKeyboardButton(text="View Tasks", callback_data="view_tasks")
            ],
            [
                InlineKeyboardButton(text="View Categories", callback_data="view_categories"),
                InlineKeyboardButton(text="View Completed Tasks", callback_data="view_completed_tasks"),
                InlineKeyboardButton(text="Clear All Tasks", callback_data="clear_tasks")
            ]
        ]
        )
    
    if tasks:
        for task in tasks:
            task_id = task['id']
            task_title = task['title']
            task_description = task['description'] if task.get('description') else "No description"
            task_due_date = (
                datetime.fromisoformat(task['due_date']).strftime("%B %d, %Y at %H:%M")
                if task.get('due_date') else "No due date"
            )
            task_category = task['category']
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Delete", callback_data=f"delete_{task_id}")],
                    [InlineKeyboardButton(text="Update", callback_data=f"update_{task_id}")]
                ]
            )
            await callback.message.answer(
                f"ID: {task_id}\nTitle: {task_title}\n Description: {task_description}\n Due Date: {task_due_date}\nCategory: {task_category}",
                reply_markup=keyboard
            )
        
        
        await callback.message.answer(
            "Main Menu Options:\n\n"
            "Choose one of the following actions:\n"
            "1. Add a Task\n"
            "2. View Tasks\n"
            "3. View Categories\n"
            "4. View Completed Tasks\n"
            "5. Clear All Tasks",
            reply_markup=keyboard_main
        )
    else:
        await callback.message.answer("You have no completed tasks at the moment!")
        # Show main menu even if no tasks
        await callback.message.answer(
            "Main Menu Options:\n\n"
            "Choose one of the following actions:\n"
            "1. Add a Task\n"
            "2. View Tasks\n"
            "3. View Categories\n"
            "4. View Completed Tasks\n"
            "5. Clear All Tasks",
            reply_markup=keyboard_main
        )