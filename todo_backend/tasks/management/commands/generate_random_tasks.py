import requests
from django.core.management.base import BaseCommand
from tasks.models import Task  # Import from the 'tasks' app
import uuid
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generates random tasks using JsonPlaceholder API'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of random tasks to generate')

    def handle(self, *args, **options):
        count = options['count']
        url = 'https://jsonplaceholder.typicode.com/todos'

        try:
            response = requests.get(url)
            response.raise_for_status()
            todos = response.json()

            random_todos = random.sample(todos, min(count, len(todos)))

            for todo in random_todos:
                Task.objects.create(
                    id=uuid.uuid4(),
                    title=todo['title'],
                    completed=todo['completed'],
                    description=f"Task from user {todo['userId']}",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    due_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                    category="Random",
                    telegram_user_id=random.choice([1111, 2222]),  # Randomly choose 1111 or 2222
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully created {count} random tasks!'))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error fetching data: {e}'))