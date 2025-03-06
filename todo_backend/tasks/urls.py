from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import create_task,get_All_tasks_by_user,task_crud,search_tasks_by_category,delete_all_tasks_by_user,get_completed_tasks_by_user,get_incomplete_tasks_by_user,get_categories_by_user


urlpatterns = [
    path('tasks/create_task/', create_task, name='create_task'),
    path('tasks/getAllTask/<int:telegram_user_id>/', get_All_tasks_by_user, name='get_tasks_by_telegram_user'),
    path('tasks/<int:telegram_user_id>/<uuid:task_id>/', task_crud, name='task_crud'),
    path('tasks/searchByCategory/', search_tasks_by_category, name='search_tasks_by_category'),
    path('tasks/<int:telegram_user_id>/deleteAll/', delete_all_tasks_by_user, name='delete_all_tasks_by_user'),
    path('tasks/getCompletedTasks/<int:telegram_user_id>/', get_completed_tasks_by_user, name='getCompletedTasks'),
    path('tasks/getIncompleteTasks/<int:telegram_user_id>/', get_incomplete_tasks_by_user, name='getCompletedTasks'),
    path('tasks/getAllCategories/<int:telegram_user_id>/', get_categories_by_user, name='get_categories_by_user'),
]