# utils.py
import aiohttp
from config import API_URL

async def fetch_tasks(user_id: int) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/getAllTask/{user_id}") as response:
            if response.status == 200:
                return await response.json()
            return []

async def fetch_task_by_id(user_id: int, task_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/{user_id}/{task_id}") as response:
            if response.status == 200:
                return await response.json()
            return None

async def update_task_field(user_id: int, task_id: str, field: str, new_value: str) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/{user_id}/{task_id}/"
        async with session.put(url, json={field: new_value}) as response:
            return response.status == 200
        
async def delete_task(user_id: int, task_id: str) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/{user_id}/{task_id}/"
        async with session.delete(url) as response:
            return response.status == 200

async def delete_all_tasks(user_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/{user_id}/deleteAll"
        async with session.delete(url) as response:
            return response.status == 200
        


async def create_task(task_data: dict) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/create_task/"
        print("CREATE URL:", url)
        async with session.post(url, json=task_data) as response:
            print(f"Create response status: {response.status}")
            return response.status == 201
        

async def fetch_categories(user_id: int) -> list:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/getAllCategories/{user_id}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("categories", [])
            return []
        
async def fetch_completed_tasks(user_id: int) -> list:
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/getCompletedTasks/{user_id}"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return []