from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User  # Add this import
from .models import Task
from .serializers import TaskSerializer


from rest_framework.decorators import throttle_classes
from rest_framework.throttling import UserRateThrottle

class CustomTaskThrottle(UserRateThrottle):
    rate = '15/minute'



@api_view(['POST'])
@throttle_classes([CustomTaskThrottle])
def create_task(request):
    data = request.data

    telegram_user_id = data.get('telegram_user_id')
    if not telegram_user_id:
        return Response({"error": "Telegram user ID is required"}, status=400)

    serializer = TaskSerializer(data=data)
    if serializer.is_valid():
        task = serializer.save()
        return Response({
            "message": "Task created successfully",
            "task": serializer.data
        }, status=201)
    
    return Response(serializer.errors, status=400)


@api_view(['GET', 'DELETE', 'PUT'])
@throttle_classes([CustomTaskThrottle])
def task_crud(request, telegram_user_id, task_id):
    """
    GET: Retrieve task by ID and Telegram user ID.
    DELETE: Delete the task if it belongs to the user.
    PUT: Update the task fields.
    """
    try:
        task = Task.objects.get(id=task_id, telegram_user_id=telegram_user_id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found or unauthorized access'}, status=404)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)

    elif request.method == 'DELETE':
        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=200)

    elif request.method == 'PUT':
        # Validate the incoming data using the serializer
        serializer = TaskSerializer(task, data=request.data, partial=True)

        if serializer.is_valid():
            # Save the updated task instance
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=404)

@api_view(['GET'])
@throttle_classes([CustomTaskThrottle])
def get_All_tasks_by_user(request, telegram_user_id):
    tasks = Task.objects.filter(telegram_user_id=telegram_user_id)
    
    if not tasks.exists():
        return Response({"message": "No tasks found for this Telegram user"}, status=404)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=200)



@api_view(['POST'])
@throttle_classes([CustomTaskThrottle])
def search_tasks_by_category(request):
    telegram_user_id = request.data.get('telegram_user_id')
    category = request.data.get('category')

    if not telegram_user_id:
        return Response({"error": "telegram_user_id is required"}, status=400)

    # Filtering tasks by telegram_user_id
    tasks = Task.objects.filter(telegram_user_id=telegram_user_id)

    # Case-insensitive, partial match for category
    if category:
        tasks = tasks.filter(category__icontains=category)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@throttle_classes([CustomTaskThrottle])
def delete_all_tasks_by_user(request, telegram_user_id):
    tasks = Task.objects.filter(telegram_user_id=telegram_user_id)

    if not tasks.exists():
        return Response({'error': 'No tasks found for this Telegram user'}, status=404)

    tasks.delete()
    return Response({'message': 'All tasks deleted successfully'}, status=200)




@api_view(['GET'])
@throttle_classes([CustomTaskThrottle])
def get_completed_tasks_by_user(request, telegram_user_id):
    tasks = Task.objects.filter(telegram_user_id=telegram_user_id, completed=True)
    if not tasks.exists():
        return Response({"message": "No completed tasks found for this Telegram user"}, status=404)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@throttle_classes([CustomTaskThrottle])
def get_incomplete_tasks_by_user(request, telegram_user_id):
    tasks = Task.objects.filter(telegram_user_id=telegram_user_id, completed=False)
    if not tasks.exists():
        return Response({"message": "No incomplete tasks found for this Telegram user"}, status=404)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@throttle_classes([CustomTaskThrottle])
def get_categories_by_user(request, telegram_user_id):
    categories = Task.objects.filter(telegram_user_id=telegram_user_id)\
                             .exclude(category__isnull=True)\
                             .exclude(category="")\
                             .values_list('category', flat=True)\
                             .distinct()
    if not categories:
        return Response({"message": "No categories found for this Telegram user"}, status=404)

    return Response({"categories": list(categories)}, status=200)