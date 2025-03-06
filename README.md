Documents:
postman document link :https://documenter.getpostman.com/view/37281446/2sAYdkGURm
system_overview_document.pdf : system architecure overview + userflow model + useCase model + information about directories.


instructions to run (in docker):
create and Configure .env file in my_todo_bot for "BOT_TOKEN" and "API_URL" (because we used  gitignore to not publish .env)

docker-compose up --build

instructions to run without Docker:
telegram bot : my_todo_bot -> python main.py
Django : todo_backend -> 1 - python manage.py migrate  2 - python manage.py runserver

instructions to Generate Random data using JsonPlaceholder :
(code location :todo_backend/tasks/management/commands/generate_random_tasks.py)
python manage.py generate_random_tasks --count 5