Documents:
postman document link :https://documenter.getpostman.com/view/37281446/2sAYdkGURm
system_overview_document.pdf : system architecure overview + userflow model + useCase model + information about directories.


instructions to run (in docker):
Configure .env file in my_todo_bot
docker-compose up --build

instructions to run without Docker:
telegram bot : my_todo_bot -> python main.py
Django : todo_backend -> 1 - python manage.py migrate  2 - python manage.py runserver

instructions to Generate Random data using JsonPlaceholder :
python manage.py generate_random_tasks --count 5